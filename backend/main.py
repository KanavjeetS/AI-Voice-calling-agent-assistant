from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.routes import calls, crm, dashboard, debug, settings as settings_routes, simulator, twilio
from config.logging_config import configure_logging
from config.settings import settings
from services.llm.groq_client import llm_client
from services.rag.embeddings import load_embedding_model
from services.stt.whisper_client import stt_client
from services.tts.kokoro_client import tts_client
from api.websockets.monitor_ws import monitor_stream
from api.websockets.twilio_ws import twilio_media_stream
from services.crm.store import crm_store

configure_logging()


class CallInitiateRequest(BaseModel):
    phone_number: str
    lead_id: str | None = None


class CallInitiateResponse(BaseModel):
    call_sid: str
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await crm_store.seed()
    if settings.STARTUP_WARM_MODELS:
        await stt_client.warm_up()
        await llm_client.warm_up()
        await tts_client.warm_up()
        await load_embedding_model()
    yield
    await stt_client.close()
    await llm_client.close()
    await tts_client.close()


app = FastAPI(
    title="VahanAI Studio Voice Platform",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.websocket("/api/v1/ws/twilio")(twilio_media_stream)
app.websocket("/api/v1/ws/monitor")(monitor_stream)
app.include_router(calls.router)
app.include_router(crm.router)
app.include_router(dashboard.router)
app.include_router(debug.router)
app.include_router(settings_routes.router)
app.include_router(simulator.router)
app.include_router(twilio.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "tier": settings.MODEL_TIER}


@app.post("/api/v1/legacy/calls/initiate", response_model=CallInitiateResponse)
async def initiate_call(payload: CallInitiateRequest) -> CallInitiateResponse:
    call_sid = f"SIM-{payload.lead_id or payload.phone_number[-4:]}"
    return CallInitiateResponse(call_sid=call_sid, status="queued")


@app.get("/api/v1/legacy/debug/stt-test")
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


@app.get("/api/v1/legacy/debug/llm-test")
async def llm_test() -> dict[str, str]:
    try:
        response = await llm_client.complete(
            messages=[{"role": "user", "content": "say hello in one word"}],
            max_tokens=8,
            temperature=0.0,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"model": settings.GROQ_LLM_MODEL if settings.MODEL_TIER != "full" else settings.VLLM_MODEL, "response": response}


@app.get("/api/v1/legacy/debug/tts-test")
async def tts_test(text: str = Query(default="hello world", min_length=1)) -> Response:
    try:
        audio = await tts_client.synthesize_complete(text)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not audio:
        raise HTTPException(status_code=503, detail="TTS produced no audio")
    return Response(content=audio, media_type="audio/basic")


@app.get("/api/v1/legacy/dashboard/stats")
async def dashboard_stats() -> dict[str, object]:
    calls_today = 0
    groq_tokens_used = 0
    groq_daily_limit = 500_000
    return {
        "total_calls": calls_today,
        "live_calls": 0,
        "conversion_rate": 0.0,
        "false_positive_rate": 0.0,
        "cost_estimate": {
            "tier": settings.MODEL_TIER,
            "calls_today": calls_today,
            "groq_tokens_used": groq_tokens_used,
            "groq_daily_limit": groq_daily_limit,
            "groq_pct_used": 0.0,
            "estimated_cost_usd": 0.00,
            "message": "Running on free tier - $0 spent today"
            if settings.MODEL_TIER == "free"
            else f"Running on {settings.MODEL_TIER} tier",
        },
    }
