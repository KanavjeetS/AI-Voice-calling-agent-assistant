from fastapi import APIRouter, Query, Request, Response, Depends, HTTPException

from services.calls.twilio import build_voice_twiml
from services.crm.store import crm_store
from config.settings import settings
from twilio.request_validator import RequestValidator

router = APIRouter(prefix="/api/v1/twilio", tags=["twilio"])


async def validate_twilio_signature(request: Request):
    # Skip signature check if TWILIO_AUTH_TOKEN is empty or standard placeholder
    if (
        not settings.TWILIO_AUTH_TOKEN
        or settings.TWILIO_AUTH_TOKEN == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ):
        return

    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=403, detail="X-Twilio-Signature header missing")

    # Reconstruct the original request URL using the public base URL
    base_url = settings.TWILIO_WEBHOOK_BASE_URL or str(request.base_url)
    path_with_query = request.url.path
    if request.url.query:
        path_with_query += f"?{request.url.query}"
    url = base_url.rstrip("/") + path_with_query

    params = {}
    if request.method == "POST":
        form_data = await request.form()
        params = {k: v for k, v in form_data.items()}

    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    if not validator.validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")


@router.post("/voice")
@router.get("/voice")
async def voice_webhook(
    lead_id: str = Query(default="unknown"),
    agent_id: str = Query(default="vahan_loan_assistant"),
    _signature: None = Depends(validate_twilio_signature),
) -> Response:
    twiml = await build_voice_twiml(lead_id=lead_id, agent_id=agent_id)
    return Response(content=twiml, media_type="application/xml")


@router.post("/status")
async def status_callback(
    request: Request,
    _signature: None = Depends(validate_twilio_signature),
) -> dict[str, str]:
    form = await request.form()
    call_sid = str(form.get("CallSid", ""))
    call_status = str(form.get("CallStatus", ""))
    duration_raw = str(form.get("CallDuration", "0"))
    call_duration = int(duration_raw) if duration_raw.isdigit() else 0
    call = await crm_store.get_call(call_sid)
    if call:
        call.status = call_status or call.status
        call.duration_seconds = call_duration or call.duration_seconds
        await crm_store.save_call(call)
    return {"status": "ok"}
