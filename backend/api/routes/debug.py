from fastapi import APIRouter, HTTPException, Query, Response

from config.settings import settings
from services.llm.groq_client import llm_client
from services.tts.kokoro_client import tts_client

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/stt-test")
async def stt_test() -> dict[str, object]:
    return {
        "tier": settings.MODEL_TIER,
        "groq_model": settings.GROQ_STT_MODEL,
        "whisper_model": settings.WHISPER_MODEL_SIZE,
        "device": settings.WHISPER_DEVICE,
        "compute_type": settings.WHISPER_COMPUTE_TYPE,
        "endpointing_ms": settings.WHISPER_ENDPOINTING_MS,
        "configured": bool(settings.GROQ_API_KEY) if settings.MODEL_TIER == "free" else True,
    }


@router.get("/llm-test")
async def llm_test() -> dict[str, str]:
    try:
        response = await llm_client.complete(
            messages=[{"role": "user", "content": "say hello in one word"}],
            max_tokens=8,
            temperature=0.0,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "model": settings.GROQ_LLM_MODEL if settings.MODEL_TIER != "full" else settings.VLLM_MODEL,
        "response": response,
    }


@router.get("/tts-test")
async def tts_test(text: str = Query(default="hello world", min_length=1)) -> Response:
    try:
        audio = await tts_client.synthesize_complete(text)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not audio:
        raise HTTPException(status_code=503, detail="TTS produced no audio")
    return Response(content=audio, media_type="audio/basic")
