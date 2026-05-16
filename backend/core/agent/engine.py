import re
import time
from typing import Dict, Tuple

from config.settings import settings
from core.agent.prompts import AGENT_SYSTEM_PROMPT, BRANCH_GUIDANCE
from models.schemas import (
    AgentReply,
    ConversationBranch,
    FollowUpAction,
    LatencyBreakdown,
    Lead,
    LeadStatus,
)
from services.intent.detector import detect_intent_live
from services.llm.groq_client import llm_client


class LoanVoiceAgent:
    async def generate_reply(self, lead: Lead, transcript: str) -> AgentReply:
        started = time.perf_counter()
        branch = self._select_branch(transcript)
        heuristic_intent, sentiment = self._heuristic_intent(transcript, lead)

        intent_payload: Dict[str, object]
        try:
            intent_started = time.perf_counter()
            intent_payload = await detect_intent_live(transcript)
            llm_intent_ms = int((time.perf_counter() - intent_started) * 1000)
        except Exception:
            intent_payload = {
                "intent": heuristic_intent,
                "sentiment_score": sentiment,
                "confidence": 0.75,
                "action": self._action_for_intent(heuristic_intent),
            }
            llm_intent_ms = 0

        intent = str(intent_payload.get("intent") or heuristic_intent)
        sentiment_score = float(intent_payload.get("sentiment_score") or sentiment)
        action = self._map_action(str(intent_payload.get("action") or self._action_for_intent(intent)), intent)
        lead_status = self._lead_status_for_intent(intent, action)

        text_started = time.perf_counter()
        text = await self._compose_text(lead, transcript, branch, intent)
        llm_text_ms = int((time.perf_counter() - text_started) * 1000)

        latency = LatencyBreakdown(
            stt_ms=520 if settings.MODEL_TIER == "free" else 420,
            llm_ms=max(llm_intent_ms + llm_text_ms, 450),
            tts_ms=220 if settings.MODEL_TIER != "full" else 160,
        )
        elapsed = int((time.perf_counter() - started) * 1000)
        if latency.llm_ms < elapsed:
            latency.llm_ms = elapsed

        return AgentReply(
            text=text,
            branch=branch,
            intent_label=intent,
            sentiment_score=sentiment_score,
            follow_up_action=action,
            lead_status=lead_status,
            escalate=action == FollowUpAction.ESCALATE_AGENT,
            terminate=action == FollowUpAction.TERMINATE_CALL,
            callback_time=self._extract_callback(transcript),
            latency=latency,
        )

    async def _compose_text(
        self,
        lead: Lead,
        transcript: str,
        branch: ConversationBranch,
        intent: str,
    ) -> str:
        fallback = self._fallback_text(lead, transcript, branch, intent)
        if not settings.GROQ_API_KEY and settings.MODEL_TIER != "full":
            return fallback

        system_prompt = (
            f"{AGENT_SYSTEM_PROMPT}\nBranch guidance: {BRANCH_GUIDANCE[branch.value]}\n"
            "Reply in the customer's language. Keep under 32 words for voice latency."
        )
        try:
            response = await llm_client.complete(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Lead: {lead.model_dump_json()}\n"
                            f"Customer said: {transcript}\n"
                            f"Detected intent: {intent}"
                        ),
                    }
                ],
                system_prompt=system_prompt,
                max_tokens=90,
                temperature=0.35,
            )
            return response.strip() or fallback
        except Exception:
            return fallback

    def _select_branch(self, transcript: str) -> ConversationBranch:
        text = transcript.lower()
        if any(word in text for word in ["emi", "monthly", "installment", "किस्त"]):
            return ConversationBranch.EMI
        if any(word in text for word in ["document", "salary", "pan", "statement", "दस्तावेज"]):
            return ConversationBranch.DOCUMENT_REMINDER
        if any(word in text for word in ["later", "callback", "tomorrow", "कल", "बाद"]):
            return ConversationBranch.CALLBACK_BOOKING
        if any(word in text for word in ["rate", "interest", "expensive", "not interested", "नहीं"]):
            return ConversationBranch.OBJECTION_HANDLING
        if any(word in text for word in ["eligible", "qualification", "income", "salary", "योग्य"]):
            return ConversationBranch.ELIGIBILITY
        return ConversationBranch.GREETING

    def _heuristic_intent(self, transcript: str, lead: Lead) -> Tuple[str, float]:
        text = transcript.lower()
        if lead.loan_amount >= 1_500_000 or "large amount" in text or "20 lakh" in text:
            return "high_ticket", 0.7
        if any(word in text for word in ["yes", "interested", "send", "haan", "हाँ", "ok"]):
            return "interested", 0.7
        if any(word in text for word in ["confused", "explain", "samajh", "समझ"]):
            return "confused", 0.1
        if any(word in text for word in ["angry", "stop calling", "complaint", "गुस्सा"]):
            return "angry", -0.8
        if any(word in text for word in ["wrong number", "spam", "invalid"]):
            return "spam_invalid", -0.4
        if any(word in text for word in ["callback", "later", "tomorrow", "कल"]):
            return "callback", 0.3
        return "unknown", 0.0

    def _action_for_intent(self, intent: str) -> str:
        return {
            "interested": "continue",
            "confused": "continue",
            "angry": "escalate",
            "spam_invalid": "terminate",
            "high_ticket": "escalate",
            "callback": "schedule_callback",
        }.get(intent, "continue")

    def _map_action(self, action: str, intent: str) -> FollowUpAction:
        if action == "escalate" or intent in {"angry", "high_ticket"}:
            return FollowUpAction.ESCALATE_AGENT
        if action == "terminate" or intent == "spam_invalid":
            return FollowUpAction.TERMINATE_CALL
        if action == "schedule_callback" or intent == "callback":
            return FollowUpAction.BOOK_CALLBACK
        return FollowUpAction.CONTINUE_AI

    def _lead_status_for_intent(self, intent: str, action: FollowUpAction) -> LeadStatus:
        if action == FollowUpAction.ESCALATE_AGENT:
            return LeadStatus.ESCALATED
        if action == FollowUpAction.BOOK_CALLBACK:
            return LeadStatus.CALLBACK_BOOKED
        if action == FollowUpAction.TERMINATE_CALL:
            return LeadStatus.INVALID if intent == "spam_invalid" else LeadStatus.NOT_INTERESTED
        if intent == "interested":
            return LeadStatus.INTERESTED
        return LeadStatus.CONTACTED

    def _fallback_text(
        self,
        lead: Lead,
        transcript: str,
        branch: ConversationBranch,
        intent: str,
    ) -> str:
        hindi = bool(re.search(r"[\u0900-\u097F]", transcript)) or lead.language_hint == "hindi"
        if intent == "angry":
            return "Sorry, main aapki baat samajh gaya. Main abhi human agent ko connect karwa deta hoon." if hindi else "I understand. I am escalating this to a human agent right away."
        if intent == "spam_invalid":
            return "Sorry for the disturbance. I will mark this number as invalid and end the call." if not hindi else "Pareshani ke liye maaf kijiye. Main is number ko invalid mark kar raha hoon."
        if branch == ConversationBranch.EMI:
            return "A rough EMI depends on tenure and rate. For an exact quote, I can arrange a quick callback." if not hindi else "EMI tenure aur rate par depend karti hai. Exact quote ke liye callback book kar deta hoon?"
        if branch == ConversationBranch.DOCUMENT_REMINDER:
            missing = ", ".join(lead.missing_fields) or "pending documents"
            return f"Your application is almost ready. We only need {missing} to continue." if not hindi else f"Aapki application almost ready hai. Bas {missing} chahiye."
        if branch == ConversationBranch.CALLBACK_BOOKING:
            return "Sure, what time should our loan specialist call you back?" if not hindi else "Zaroor, loan specialist aapko kis time call kare?"
        if branch == ConversationBranch.OBJECTION_HANDLING:
            return "That is fair. I can explain the charges simply and you can decide after that." if not hindi else "Bilkul, main charges simple tareeke se explain kar deta hoon, phir aap decide kar sakte hain."
        return f"Hi {lead.name}, this is VahanAI calling about your loan application. Is this a good time?" if not hindi else f"Namaste {lead.name}, main VahanAI se loan application ke baare mein call kar raha hoon. Kya abhi baat kar sakte hain?"

    def _extract_callback(self, transcript: str) -> str | None:
        match = re.search(r"(\d{1,2}\s*(?:am|pm|AM|PM))", transcript)
        if match:
            return match.group(1)
        if "tomorrow" in transcript.lower() or "कल" in transcript:
            return "tomorrow"
        return None


loan_voice_agent = LoanVoiceAgent()
