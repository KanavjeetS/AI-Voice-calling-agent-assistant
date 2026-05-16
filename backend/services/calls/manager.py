import time
from typing import List

from core.agent.engine import loan_voice_agent
from models.schemas import CallRecord, Lead, TranscriptTurn
from services.alerts.dispatcher import dispatch_hot_lead_alert
from services.calls.twilio import create_twilio_call, is_twilio_ready
from services.crm.persistence import save_call_record
from services.crm.store import crm_store
from services.settings.agents import AGENTS


async def initiate_demo_call(
    phone_number: str,
    lead_id: str | None = None,
    agent_id: str = "vahan_loan_assistant",
) -> CallRecord:
    await crm_store.seed()
    lead = await _resolve_lead(phone_number, lead_id)
    call_sid = f"SIM-{int(time.time() * 1000)}"
    agent = next((item for item in AGENTS if item.id == agent_id), AGENTS[0])
    record = CallRecord(
        call_sid=call_sid,
        lead_id=lead.id,
        customer_phone=lead.phone_number,
        agent_id=agent.id,
        agent_name=agent.name,
        call_mode="simulation",
        status="queued",
        transcript=[],
    )
    return await save_call_record(record)


async def initiate_outbound_call(
    phone_number: str,
    lead_id: str | None = None,
    agent_id: str = "vahan_loan_assistant",
) -> CallRecord:
    record = await initiate_demo_call(phone_number, lead_id, agent_id)
    if not is_twilio_ready():
        record.status = "simulation_ready_missing_public_webhook"
        return await save_call_record(record)

    provider_sid = await create_twilio_call(
        to_number=record.customer_phone,
        lead_id=record.lead_id,
        agent_id=record.agent_id,
    )
    record.provider_call_sid = provider_sid
    record.call_sid = provider_sid
    record.call_mode = "twilio"
    record.status = "initiated"
    return await save_call_record(record)


async def handle_customer_turn(call_sid: str, text: str) -> CallRecord:
    call = await crm_store.get_call(call_sid)
    if call is None:
        raise KeyError(f"Call not found: {call_sid}")
    lead = await crm_store.get_lead(call.lead_id)
    if lead is None:
        raise KeyError(f"Lead not found: {call.lead_id}")

    reply = await loan_voice_agent.generate_reply(lead, text)
    call.transcript.append(TranscriptTurn(speaker="customer", text=text, intent=reply.intent_label))
    call.transcript.append(
        TranscriptTurn(
            speaker="agent",
            text=reply.text,
            latency_ms=reply.latency.total_ms,
            intent=reply.intent_label,
        )
    )
    call.intent_label = reply.intent_label
    call.sentiment_score = reply.sentiment_score
    call.follow_up_action = reply.follow_up_action
    call.updated_lead_status = reply.lead_status
    call.latency = reply.latency
    saved = await save_call_record(call)

    if reply.escalate or reply.intent_label in {"interested", "high_ticket"}:
        await dispatch_hot_lead_alert(
            {
                "call_sid": call_sid,
                "lead_id": lead.id,
                "name": lead.name,
                "intent": reply.intent_label,
                "action": reply.follow_up_action.value,
            }
        )
    return saved


async def list_call_records() -> List[CallRecord]:
    return await crm_store.list_calls()


async def _resolve_lead(phone_number: str, lead_id: str | None) -> Lead:
    if lead_id:
        lead = await crm_store.get_lead(lead_id)
        if lead:
            return lead
    for lead in await crm_store.list_leads():
        if lead.phone_number == phone_number:
            return lead
    lead = Lead(id=f"lead_{abs(hash(phone_number)) % 100000}", name="Demo Customer", phone_number=phone_number)
    return await crm_store.upsert_lead(lead)
