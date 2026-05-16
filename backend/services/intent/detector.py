import json
from typing import Dict

from core.call_session import IntentLabel
from services.llm.groq_client import llm_client


INTENT_SYSTEM_PROMPT = """Classify live loan follow-up customer intent.
Return only JSON with keys intent, sentiment_score, confidence, action.
Allowed intent values: interested, confused, angry, spam_invalid, high_ticket, callback, unknown.
Allowed action values: escalate, continue, terminate, schedule_callback."""


async def detect_intent_live(transcript: str) -> Dict[str, object]:
    response = await llm_client.complete(
        messages=[{"role": "user", "content": transcript}],
        system_prompt=INTENT_SYSTEM_PROMPT,
        max_tokens=120,
        temperature=0.0,
    )
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        data = {
            "intent": IntentLabel.UNKNOWN.value,
            "sentiment_score": 0.0,
            "confidence": 0.0,
            "action": "continue",
        }
    return data
