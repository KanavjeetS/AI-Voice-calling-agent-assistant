from models.schemas import AgentConfig, ConversationBranch


AGENTS = [
    AgentConfig(
        id="vahan_loan_assistant",
        name="Vahan Loan Assistant",
        language="Hindi + English",
        voice="Kokoro af_sarah / hf_alpha",
        description="Default bilingual loan follow-up agent for eligibility, EMI, documents, objections, and callbacks.",
        branches=[
            ConversationBranch.GREETING,
            ConversationBranch.ELIGIBILITY,
            ConversationBranch.EMI,
            ConversationBranch.DOCUMENT_REMINDER,
            ConversationBranch.OBJECTION_HANDLING,
            ConversationBranch.CALLBACK_BOOKING,
        ],
    ),
    AgentConfig(
        id="hot_lead_closer",
        name="Hot Lead Closer",
        language="English first, Hindi fallback",
        voice="Kokoro af_bella",
        description="More assertive handoff agent for high-ticket and strongly interested customers.",
        branches=[
            ConversationBranch.GREETING,
            ConversationBranch.EMI,
            ConversationBranch.OBJECTION_HANDLING,
            ConversationBranch.CALLBACK_BOOKING,
        ],
    ),
    AgentConfig(
        id="document_reminder_agent",
        name="Document Reminder Agent",
        language="Hindi + Hinglish",
        voice="Kokoro hf_alpha",
        description="Short reminder agent focused on missing PAN, salary slip, and bank statement collection.",
        branches=[
            ConversationBranch.GREETING,
            ConversationBranch.DOCUMENT_REMINDER,
            ConversationBranch.CALLBACK_BOOKING,
        ],
    ),
]


async def list_agents() -> list[AgentConfig]:
    return AGENTS
