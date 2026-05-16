from fastapi import APIRouter, HTTPException

from config.settings import settings
from models.schemas import AgentConfig, TierUpdateRequest, TierUpdateResponse
from services.calls.twilio import is_twilio_ready
from services.settings.agents import list_agents

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("/providers")
async def provider_status() -> dict[str, object]:
    return {
        "tier": settings.MODEL_TIER,
        "providers": {
            "groq_api_key": "Connected" if settings.GROQ_API_KEY else "Not Set",
            "whisper_model": f"Configured ({settings.WHISPER_MODEL_SIZE})",
            "kokoro_tts": "Configured",
            "vllm_server": "Configured" if settings.MODEL_TIER == "full" else "Hidden",
            "twilio": "Ready" if is_twilio_ready() else "Needs Public Webhook",
            "supabase": "Configured" if settings.SUPABASE_URL and settings.DATABASE_URL else "Not Set",
            "redis": "Configured" if settings.REDIS_URL else "Not Set",
        },
        "models": {
            "llm": settings.VLLM_MODEL if settings.MODEL_TIER == "full" else settings.GROQ_LLM_MODEL,
            "stt": settings.GROQ_STT_MODEL if settings.MODEL_TIER == "free" else settings.WHISPER_MODEL_SIZE,
            "tts": "Chatterbox-Turbo" if settings.MODEL_TIER == "full" else "Kokoro-82M",
            "embedding": settings.EMBEDDING_MODEL,
        },
    }


@router.get("/agents", response_model=list[AgentConfig])
async def agents() -> list[AgentConfig]:
    return await list_agents()


@router.put("/tier", response_model=TierUpdateResponse)
async def update_tier(payload: TierUpdateRequest) -> TierUpdateResponse:
    if payload.tier not in {"free", "balanced", "full"}:
        raise HTTPException(status_code=400, detail="tier must be free, balanced, or full")
    return TierUpdateResponse(
        tier=payload.tier,
        restart_required=True,
        message="Set MODEL_TIER in the environment and restart the API container to apply this tier.",
    )
