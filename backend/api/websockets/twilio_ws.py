import asyncio
import base64
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from core.session_registry import session_registry
from services.stt.whisper_client import stt_client
from services.tts.kokoro_client import tts_client
from services.crm.store import crm_store
from services.calls.manager import handle_customer_turn
from models.schemas import TranscriptTurn

logger = logging.getLogger(__name__)


async def twilio_media_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    session = await session_registry.create(call_sid="pending")

    async def speak_text(text: str, language_hint: str) -> None:
        if not session.stream_sid:
            return
        session.is_ai_speaking = True
        session.is_interrupted = False
        try:
            async for chunk in tts_client.synthesize_stream(text, language=language_hint):
                if session.is_interrupted:
                    logger.info(f"[{session.call_sid}] TTS playback interrupted by customer speech")
                    break
                media_event = {
                    "event": "media",
                    "streamSid": session.stream_sid,
                    "media": {
                        "payload": base64.b64encode(chunk).decode("utf-8")
                    }
                }
                await websocket.send_text(json.dumps(media_event))
        except Exception as exc:
            logger.exception(f"[{session.call_sid}] Error streaming TTS audio chunk: {exc}")
        finally:
            session.is_ai_speaking = False

    async def on_final(transcript: str) -> None:
        if not transcript.strip():
            return
        logger.info(f"[{session.call_sid}] Customer final transcript: {transcript}")
        session.last_transcript = transcript

        try:
            # Retrieve Call and Lead info
            call_record = await crm_store.get_call(session.call_sid)
            if not call_record:
                logger.warning(f"[{session.call_sid}] Call record not found in crm_store")
                return
            
            # Execute turn through manager to update CRM and generate AI response
            updated_call = await handle_customer_turn(session.call_sid, transcript)
            
            # Extract generated agent reply from the last transcript turn
            if updated_call.transcript and updated_call.transcript[-1].speaker == "agent":
                agent_reply = updated_call.transcript[-1].text
                logger.info(f"[{session.call_sid}] AI Response: {agent_reply}")
                
                # Speak response back to customer
                asyncio.create_task(speak_text(agent_reply, session.detected_language))
        except Exception as exc:
            logger.exception(f"[{session.call_sid}] Error in on_final: {exc}")

    async def on_speech_started() -> None:
        logger.info(f"[{session.call_sid}] Speech started - customer is interrupting AI")
        await session.mark_interrupted()
        if session.stream_sid:
            # Send "clear" event to Twilio to stop playing audio currently in buffer
            clear_event = {
                "event": "clear",
                "streamSid": session.stream_sid
            }
            await websocket.send_text(json.dumps(clear_event))

    async def on_speech_ended() -> None:
        logger.info(f"[{session.call_sid}] Speech ended")
        return None

    stream = await stt_client.create_stream(
        session=session,
        on_final=on_final,
        on_speech_started=on_speech_started,
        on_speech_ended=on_speech_ended,
    )
    
    try:
        while True:
            raw = await websocket.receive_text()
            event = json.loads(raw)
            if event.get("event") == "start":
                session.call_sid = event["start"].get("callSid", session.call_sid)
                session.stream_sid = event["start"].get("streamSid")
                logger.info(f"[{session.call_sid}] Twilio Stream started. Stream SID: {session.stream_sid}")
                
                # Trigger initial greeting
                call_record = await crm_store.get_call(session.call_sid)
                if call_record:
                    lead = await crm_store.get_lead(call_record.lead_id)
                    if lead:
                        hindi = lead.language_hint == "hindi"
                        greeting = (
                            f"Hi {lead.name}, this is VahanAI calling about your loan application. Is this a good time?"
                            if not hindi
                            else f"Namaste {lead.name}, main VahanAI se loan application ke baare mein call kar raha hoon. Kya abhi baat kar sakte hain?"
                        )
                        # Register the initial agent turn
                        call_record.transcript.append(
                            TranscriptTurn(speaker="agent", text=greeting, intent="unknown")
                        )
                        await crm_store.save_call(call_record)
                        
                        # Stream out the greeting
                        asyncio.create_task(speak_text(greeting, session.detected_language))
            elif event.get("event") == "media":
                payload = event["media"].get("payload", "")
                await stream.send_audio(base64.b64decode(payload))
            elif event.get("event") == "stop":
                logger.info(f"[{session.call_sid}] Twilio Stream stopped event received.")
                break
    except WebSocketDisconnect:
        logger.info(f"[{session.call_sid}] Twilio WebSocket disconnected.")
    finally:
        await stream.close()
        await session_registry.remove(session.call_sid)
