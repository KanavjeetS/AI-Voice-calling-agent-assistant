from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    HINDI = "hindi"
    ENGLISH = "english"
    HINGLISH = "hinglish"


class IntentLabel(str, Enum):
    INTERESTED = "interested"
    CONFUSED = "confused"
    ANGRY = "angry"
    SPAM_INVALID = "spam_invalid"
    HIGH_TICKET = "high_ticket"
    CALLBACK = "callback"
    UNKNOWN = "unknown"


class CallSession(BaseModel):
    call_sid: str
    stream_sid: Optional[str] = None
    customer_phone: Optional[str] = None
    detected_language: Language = Language.HINGLISH
    current_intent: IntentLabel = IntentLabel.UNKNOWN
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_transcript: str = ""
    is_ai_speaking: bool = False
    is_interrupted: bool = False

    async def mark_ai_speaking(self, speaking: bool) -> None:
        self.is_ai_speaking = speaking

    async def mark_interrupted(self) -> None:
        self.is_interrupted = True
