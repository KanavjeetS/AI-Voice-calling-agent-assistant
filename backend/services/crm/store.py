from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import asyncpg

from config.settings import settings
from models.schemas import CallRecord, Lead, LeadStatus, FollowUpAction, TranscriptTurn, LatencyBreakdown

logger = logging.getLogger(__name__)


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


class PostgresCRMStore:
    def __init__(self) -> None:
        self._pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            logger.info("Initializing PostgreSQL Connection Pool...")
            self._pool = await asyncpg.create_pool(settings.DATABASE_URL)
            async with self._pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS leads (
                        id VARCHAR(100) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        phone_number VARCHAR(100) NOT NULL,
                        loan_amount INT DEFAULT 0,
                        city VARCHAR(255) DEFAULT 'Unknown',
                        status VARCHAR(100) DEFAULT 'new',
                        language_hint VARCHAR(100) DEFAULT 'hinglish',
                        missing_fields JSONB DEFAULT '[]'::jsonb,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS call_records (
                        call_sid VARCHAR(100) PRIMARY KEY,
                        customer_phone VARCHAR(100) NOT NULL,
                        agent_id VARCHAR(100) DEFAULT 'vahan_loan_assistant',
                        agent_name VARCHAR(255) DEFAULT 'Vahan Loan Assistant',
                        call_mode VARCHAR(100) DEFAULT 'simulation',
                        provider_call_sid VARCHAR(255),
                        status VARCHAR(100) DEFAULT 'queued',
                        duration_seconds INT DEFAULT 0,
                        transcript JSONB DEFAULT '[]'::jsonb,
                        intent_label VARCHAR(100) DEFAULT 'unknown',
                        sentiment_score NUMERIC(5, 2) DEFAULT 0.0,
                        follow_up_action VARCHAR(100) DEFAULT 'continue_ai',
                        updated_lead_status VARCHAR(100) DEFAULT 'contacted',
                        recording_url VARCHAR(512),
                        latency JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        lead_id VARCHAR(100) REFERENCES leads(id) ON DELETE SET NULL
                    );
                """)
                count = await conn.fetchval("SELECT COUNT(*) FROM leads")
                if count == 0:
                    logger.info("Seeding initial leads into PostgreSQL...")
                    sample_leads = [
                        ("lead_1001", "Priya Sharma", "+919876543210", 650000, "Delhi", "new", "hinglish", json.dumps(["salary_slip", "pan_card"])),
                        ("lead_1002", "Rahul Mehta", "+919812340987", 1800000, "Mumbai", "new", "hindi", json.dumps(["bank_statement"])),
                        ("lead_1003", "Aisha Khan", "+919700111222", 420000, "Bengaluru", "contacted", "hinglish", json.dumps([]))
                    ]
                    await conn.executemany("""
                        INSERT INTO leads (id, name, phone_number, loan_amount, city, status, language_hint, missing_fields)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                    """, sample_leads)
        return self._pool

    async def upsert_lead(self, lead: Lead) -> Lead:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO leads (id, name, phone_number, loan_amount, city, status, language_hint, missing_fields, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    phone_number = EXCLUDED.phone_number,
                    loan_amount = EXCLUDED.loan_amount,
                    city = EXCLUDED.city,
                    status = EXCLUDED.status,
                    language_hint = EXCLUDED.language_hint,
                    missing_fields = EXCLUDED.missing_fields,
                    created_at = EXCLUDED.created_at
            """, lead.id, lead.name, lead.phone_number, lead.loan_amount, lead.city, lead.status.value, lead.language_hint, json.dumps(lead.missing_fields), lead.created_at)
        return lead

    async def list_leads(self) -> List[Lead]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM leads")
            return [
                Lead(
                    id=row["id"],
                    name=row["name"],
                    phone_number=row["phone_number"],
                    loan_amount=row["loan_amount"],
                    city=row["city"],
                    status=LeadStatus(row["status"]),
                    language_hint=row["language_hint"],
                    missing_fields=json.loads(row["missing_fields"]) if isinstance(row["missing_fields"], str) else (row["missing_fields"] or []),
                    created_at=row["created_at"]
                ) for row in rows
            ]

    async def get_lead(self, lead_id: str) -> Optional[Lead]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM leads WHERE id = $1", lead_id)
            if not row:
                return None
            return Lead(
                id=row["id"],
                name=row["name"],
                phone_number=row["phone_number"],
                loan_amount=row["loan_amount"],
                city=row["city"],
                status=LeadStatus(row["status"]),
                language_hint=row["language_hint"],
                missing_fields=json.loads(row["missing_fields"]) if isinstance(row["missing_fields"], str) else (row["missing_fields"] or []),
                created_at=row["created_at"]
            )

    async def update_lead_status(self, lead_id: str, status: LeadStatus) -> None:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("UPDATE leads SET status = $1 WHERE id = $2", status.value, lead_id)

    async def save_call(self, call: CallRecord) -> CallRecord:
        pool = await self.get_pool()
        transcript_json = json.dumps([turn.dict() for turn in call.transcript])
        latency_json = json.dumps(call.latency.dict())
        
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO call_records (
                    call_sid, lead_id, customer_phone, agent_id, agent_name, call_mode,
                    provider_call_sid, status, duration_seconds, transcript, intent_label,
                    sentiment_score, follow_up_action, updated_lead_status, recording_url,
                    latency, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                ON CONFLICT (call_sid) DO UPDATE SET
                    lead_id = EXCLUDED.lead_id,
                    customer_phone = EXCLUDED.customer_phone,
                    agent_id = EXCLUDED.agent_id,
                    agent_name = EXCLUDED.agent_name,
                    call_mode = EXCLUDED.call_mode,
                    provider_call_sid = EXCLUDED.provider_call_sid,
                    status = EXCLUDED.status,
                    duration_seconds = EXCLUDED.duration_seconds,
                    transcript = EXCLUDED.transcript,
                    intent_label = EXCLUDED.intent_label,
                    sentiment_score = EXCLUDED.sentiment_score,
                    follow_up_action = EXCLUDED.follow_up_action,
                    updated_lead_status = EXCLUDED.updated_lead_status,
                    recording_url = EXCLUDED.recording_url,
                    latency = EXCLUDED.latency,
                    created_at = EXCLUDED.created_at
            """,
                call.call_sid, call.lead_id, call.customer_phone, call.agent_id, call.agent_name,
                call.call_mode, call.provider_call_sid, call.status, call.duration_seconds,
                transcript_json, call.intent_label, call.sentiment_score, call.follow_up_action.value,
                call.updated_lead_status.value, call.recording_url, latency_json, call.created_at
            )
        await self.update_lead_status(call.lead_id, call.updated_lead_status)
        return call

    async def list_calls(self) -> List[CallRecord]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM call_records ORDER BY created_at DESC")
            calls = []
            for row in rows:
                t_list = json.loads(row["transcript"])
                transcript = [TranscriptTurn(**turn) for turn in t_list]
                
                lat_dict = json.loads(row["latency"]) if row["latency"] else {}
                latency = LatencyBreakdown(**lat_dict) if lat_dict else LatencyBreakdown()
                
                calls.append(CallRecord(
                    call_sid=row["call_sid"],
                    lead_id=row["lead_id"],
                    customer_phone=row["customer_phone"],
                    agent_id=row["agent_id"],
                    agent_name=row["agent_name"],
                    call_mode=row["call_mode"],
                    provider_call_sid=row["provider_call_sid"],
                    status=row["status"],
                    duration_seconds=row["duration_seconds"],
                    transcript=transcript,
                    intent_label=row["intent_label"],
                    sentiment_score=float(row["sentiment_score"]),
                    follow_up_action=FollowUpAction(row["follow_up_action"]),
                    updated_lead_status=LeadStatus(row["updated_lead_status"]),
                    recording_url=row["recording_url"],
                    latency=latency,
                    created_at=row["created_at"]
                ))
            return calls

    async def get_call(self, call_sid: str) -> Optional[CallRecord]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM call_records WHERE call_sid = $1", call_sid)
            if not row:
                return None
            t_list = json.loads(row["transcript"])
            transcript = [TranscriptTurn(**turn) for turn in t_list]
            
            lat_dict = json.loads(row["latency"]) if row["latency"] else {}
            latency = LatencyBreakdown(**lat_dict) if lat_dict else LatencyBreakdown()
            
            return CallRecord(
                call_sid=row["call_sid"],
                lead_id=row["lead_id"],
                customer_phone=row["customer_phone"],
                agent_id=row["agent_id"],
                agent_name=row["agent_name"],
                call_mode=row["call_mode"],
                provider_call_sid=row["provider_call_sid"],
                status=row["status"],
                duration_seconds=row["duration_seconds"],
                transcript=transcript,
                intent_label=row["intent_label"],
                sentiment_score=float(row["sentiment_score"]),
                follow_up_action=FollowUpAction(row["follow_up_action"]),
                updated_lead_status=LeadStatus(row["updated_lead_status"]),
                recording_url=row["recording_url"],
                latency=latency,
                created_at=row["created_at"]
            )


class UnifiedCRMStore:
    def __init__(self) -> None:
        self._in_memory = InMemoryCRMStore()
        self._db = PostgresCRMStore()

    @property
    def active_store(self) -> InMemoryCRMStore | PostgresCRMStore:
        if settings.USE_DATABASE:
            return self._db
        return self._in_memory

    async def upsert_lead(self, lead: Lead) -> Lead:
        return await self.active_store.upsert_lead(lead)

    async def list_leads(self) -> List[Lead]:
        return await self.active_store.list_leads()

    async def get_lead(self, lead_id: str) -> Optional[Lead]:
        return await self.active_store.get_lead(lead_id)

    async def update_lead_status(self, lead_id: str, status: LeadStatus) -> None:
        await self.active_store.update_lead_status(lead_id, status)

    async def save_call(self, call: CallRecord) -> CallRecord:
        return await self.active_store.save_call(call)

    async def list_calls(self) -> List[CallRecord]:
        return await self.active_store.list_calls()

    async def get_call(self, call_sid: str) -> Optional[CallRecord]:
        return await self.active_store.get_call(call_sid)

    async def seed(self) -> None:
        if settings.USE_DATABASE:
            await self._db.get_pool()
        else:
            await self._in_memory.seed()


crm_store = UnifiedCRMStore()
