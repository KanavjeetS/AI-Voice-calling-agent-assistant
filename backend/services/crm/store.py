from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.schemas import CallRecord, Lead, LeadStatus


@dataclass
class InMemoryCRMStore:
    leads: Dict[str, Lead] = field(default_factory=dict)
    calls: Dict[str, CallRecord] = field(default_factory=dict)

    async def seed(self) -> None:
        if self.leads:
            return
        sample_leads = [
            Lead(
                id="lead_1001",
                name="Priya Sharma",
                phone_number="+919876543210",
                loan_amount=650000,
                city="Delhi",
                missing_fields=["salary_slip", "pan_card"],
            ),
            Lead(
                id="lead_1002",
                name="Rahul Mehta",
                phone_number="+919812340987",
                loan_amount=1800000,
                city="Mumbai",
                language_hint="hindi",
                missing_fields=["bank_statement"],
            ),
            Lead(
                id="lead_1003",
                name="Aisha Khan",
                phone_number="+919700111222",
                loan_amount=420000,
                city="Bengaluru",
                status=LeadStatus.CONTACTED,
            ),
        ]
        self.leads.update({lead.id: lead for lead in sample_leads})

    async def upsert_lead(self, lead: Lead) -> Lead:
        self.leads[lead.id] = lead
        return lead

    async def list_leads(self) -> List[Lead]:
        await self.seed()
        return list(self.leads.values())

    async def get_lead(self, lead_id: str) -> Optional[Lead]:
        await self.seed()
        return self.leads.get(lead_id)

    async def update_lead_status(self, lead_id: str, status: LeadStatus) -> None:
        lead = await self.get_lead(lead_id)
        if lead:
            lead.status = status
            self.leads[lead_id] = lead

    async def save_call(self, call: CallRecord) -> CallRecord:
        self.calls[call.call_sid] = call
        await self.update_lead_status(call.lead_id, call.updated_lead_status)
        return call

    async def list_calls(self) -> List[CallRecord]:
        return sorted(self.calls.values(), key=lambda call: call.created_at, reverse=True)

    async def get_call(self, call_sid: str) -> Optional[CallRecord]:
        return self.calls.get(call_sid)


crm_store = InMemoryCRMStore()
