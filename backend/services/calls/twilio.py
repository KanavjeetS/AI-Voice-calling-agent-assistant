import asyncio
from urllib.parse import urlencode

from config.settings import settings


def _public_base_url() -> str:
    return settings.TWILIO_WEBHOOK_BASE_URL.rstrip("/")


def is_twilio_ready() -> bool:
    return bool(
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_PHONE_NUMBER
        and settings.TWILIO_WEBHOOK_BASE_URL
    )


async def create_twilio_call(
    to_number: str,
    lead_id: str,
    agent_id: str,
) -> str:
    if not is_twilio_ready():
        raise RuntimeError("Twilio is missing credentials or TWILIO_WEBHOOK_BASE_URL")

    from twilio.rest import Client

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    query = urlencode({"lead_id": lead_id, "agent_id": agent_id})
    voice_url = f"{_public_base_url()}/api/v1/twilio/voice?{query}"
    status_callback = f"{_public_base_url()}{settings.TWILIO_STATUS_CALLBACK_PATH}"

    loop = asyncio.get_running_loop()
    call = await loop.run_in_executor(
        None,
        lambda: client.calls.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=voice_url,
            status_callback=status_callback,
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            status_callback_method="POST",
        ),
    )
    return str(call.sid)


async def build_voice_twiml(lead_id: str, agent_id: str) -> str:
    from twilio.twiml.voice_response import Connect, Say, Stream, VoiceResponse

    base = _public_base_url()
    ws_base = base.replace("https://", "wss://").replace("http://", "ws://")
    stream_url = f"{ws_base}/api/v1/ws/twilio?{urlencode({'lead_id': lead_id, 'agent_id': agent_id})}"

    response = VoiceResponse()
    response.say(
        "Connecting you to the Vahan AI loan assistant.",
        voice="alice",
        language="en-IN",
    )
    connect = Connect()
    connect.append(Stream(url=stream_url))
    response.append(connect)
    return str(response)
