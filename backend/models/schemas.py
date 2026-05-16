from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    CALLBACK_BOOKED = "callback_booked"
    ESCALATED = "escalated"
    NOT_INTERESTED = "not_interested"
    INVALID = "invalid"


class FollowUpAction(str, Enum):
    CONTINUE_AI = "continue_ai"
    ESCALATE_AGENT = "escalate_agent"
    TERMINATE_CALL = "terminate_call"
    BOOK_CALLBACK = "book_callback"
    SEND_DOCUMENT_REMINDER = "send_document_reminder"


class ConversationBranch(str, Enum):
    GREETING = "greeting"
    ELIGIBILITY = "eligibility"
    EMI = "emi"
    DOCUMENT_REMINDER = "document_reminder"
    OBJECTION_HANDLING = "objection_handling"
    CALLBACK_BOOKING = "callback_booking"


class Lead(BaseModel):
    id: str
    name: str
    phone_number: str
    loan_amount: int = 0
    city: str = "Unknown"
    status: LeadStatus = LeadStatus.NEW
    language_hint: str = "hinglish"
    missing_fields: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TranscriptTurn(BaseModel):
    speaker: str
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: Optional[int] = None
    intent: Optional[str] = None


class LatencyBreakdown(BaseModel):
    twilio_ingress_ms: int = 100
    stt_ms: int = 0
    llm_ms: int = 0
    tts_ms: int = 0
    twilio_egress_ms: int = 100

    @property
    def total_ms(self) -> int:
        return (
            self.twilio_ingress_ms
            + self.stt_ms
            + self.llm_ms
            + self.tts_ms
            + self.twilio_egress_ms
        )


class CallRecord(BaseModel):
    call_sid: str
    lead_id: str
    customer_phone: str
    agent_id: str = "vahan_loan_assistant"
    agent_name: str = "Vahan Loan Assistant"
    call_mode: str = "simulation"
    provider_call_sid: Optional[str] = None
    status: str = "queued"
    duration_seconds: int = 0
    transcript: List[TranscriptTurn] = Field(default_factory=list)
    intent_label: str = "unknown"
    sentiment_score: float = 0.0
    follow_up_action: FollowUpAction = FollowUpAction.CONTINUE_AI
    updated_lead_status: LeadStatus = LeadStatus.CONTACTED
    recording_url: Optional[str] = None
    latency: LatencyBreakdown = Field(default_factory=LatencyBreakdown)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentReply(BaseModel):
    text: str
    branch: ConversationBranch
    intent_label: str
    sentiment_score: float
    follow_up_action: FollowUpAction
    lead_status: LeadStatus
    escalate: bool = False
    terminate: bool = False
    callback_time: Optional[str] = None
    latency: LatencyBreakdown


class DashboardStats(BaseModel):
    total_calls: int
    live_calls: int
    conversions: int
    conversion_rate: float
    average_latency_ms: int
    average_sentiment: float
    false_positive_rate: float
    intent_counts: Dict[str, int]
    cost_estimate: Dict[str, object]


class SimulatorRequest(BaseModel):
    scenario: str = "interested"
    language: str = "english"
    turns: int = Field(default=6, ge=2, le=12)


class SimulatorTurn(BaseModel):
    customer: str
    agent: AgentReply


class SimulatorResponse(BaseModel):
    scenario: str
    language: str
    turns: List[SimulatorTurn]
    final_status: LeadStatus


class TierUpdateRequest(BaseModel):
    tier: str


class TierUpdateResponse(BaseModel):
    tier: str
    restart_required: bool = True
    message: str


class AgentConfig(BaseModel):
    id: str
    name: str
    language: str
    voice: str
    description: str
    branches: List[ConversationBranch]
    active: bool = True
