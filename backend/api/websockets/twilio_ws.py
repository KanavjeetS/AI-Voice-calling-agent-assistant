import base64
import json

from fastapi import WebSocket, WebSocketDisconnect

from core.session_registry import session_registry
from services.llm.groq_client import llm_client
from services.stt.whisper_client import stt_client
from services.tts.kokoro_client import tts_client


async def twilio_media_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    session = await session_registry.create(call_sid="pending")

    async def on_final(transcript: str) -> None:
        session.last_transcript = transcript

    async def on_speech_started() -> None:
        await session.mark_interrupted()

    async def on_speech_ended() -> None:
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
            elif event.get("event") == "media":
                payload = event["media"].get("payload", "")
                await stream.send_audio(base64.b64decode(payload))
            elif event.get("event") == "stop":
                break
    except WebSocketDisconnect:
        pass
    finally:
        await stream.close()
        await session_registry.remove(session.call_sid)
