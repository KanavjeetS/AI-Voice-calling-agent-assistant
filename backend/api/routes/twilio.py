from fastapi import APIRouter, Query, Request, Response

from services.calls.twilio import build_voice_twiml
from services.crm.store import crm_store

router = APIRouter(prefix="/api/v1/twilio", tags=["twilio"])


@router.post("/voice")
@router.get("/voice")
async def voice_webhook(
    lead_id: str = Query(default="unknown"),
    agent_id: str = Query(default="vahan_loan_assistant"),
) -> Response:
    twiml = await build_voice_twiml(lead_id=lead_id, agent_id=agent_id)
    return Response(content=twiml, media_type="application/xml")


@router.post("/status")
async def status_callback(request: Request) -> dict[str, str]:
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
