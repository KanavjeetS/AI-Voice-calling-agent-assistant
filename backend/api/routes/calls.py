from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.schemas import CallRecord
from services.calls.manager import handle_customer_turn, initiate_outbound_call, list_call_records
from services.crm.store import crm_store

router = APIRouter(prefix="/api/v1/calls", tags=["calls"])


class InitiateCallRequest(BaseModel):
    phone_number: str
    lead_id: str | None = None
    agent_id: str = "vahan_loan_assistant"


class CustomerTurnRequest(BaseModel):
    text: str


@router.post("/initiate", response_model=CallRecord)
async def initiate_call(payload: InitiateCallRequest) -> CallRecord:
    return await initiate_outbound_call(payload.phone_number, payload.lead_id, payload.agent_id)


@router.get("", response_model=list[CallRecord])
async def list_calls() -> list[CallRecord]:
    return await list_call_records()


@router.get("/{call_sid}", response_model=CallRecord)
async def get_call(call_sid: str) -> CallRecord:
    call = await crm_store.get_call(call_sid)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.post("/{call_sid}/turn", response_model=CallRecord)
async def customer_turn(call_sid: str, payload: CustomerTurnRequest) -> CallRecord:
    try:
        return await handle_customer_turn(call_sid, payload.text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
