from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    MODEL_TIER: Literal["free", "balanced", "full"] = Field(
        default="free", env="MODEL_TIER"
    )

    TWILIO_ACCOUNT_SID: str = Field(default="", env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = Field(default="", env="TWILIO_PHONE_NUMBER")
    TWILIO_WEBHOOK_BASE_URL: str = Field(default="", env="TWILIO_WEBHOOK_BASE_URL")
    TWILIO_STATUS_CALLBACK_PATH: str = Field(
        default="/api/v1/twilio/status", env="TWILIO_STATUS_CALLBACK_PATH"
    )

    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")
    GROQ_LLM_MODEL: str = Field(
        default="meta-llama/llama-4-scout-17b-16e-instruct", env="GROQ_LLM_MODEL"
    )
    GROQ_STT_MODEL: str = Field(default="whisper-large-v3", env="GROQ_STT_MODEL")
    GROQ_STT_LANGUAGE: str = Field(default="hi", env="GROQ_STT_LANGUAGE")
    GROQ_LLM_MAX_TOKENS: int = Field(default=300, env="GROQ_LLM_MAX_TOKENS")
    GROQ_LLM_TEMPERATURE: float = Field(default=0.7, env="GROQ_LLM_TEMPERATURE")

    WHISPER_MODEL_SIZE: str = Field(default="large-v3-turbo", env="WHISPER_MODEL_SIZE")
    WHISPER_DEVICE: Literal["cpu", "cuda"] = Field(default="cpu", env="WHISPER_DEVICE")
    WHISPER_COMPUTE_TYPE: str = Field(default="int8", env="WHISPER_COMPUTE_TYPE")
    WHISPER_LANGUAGE: str = Field(default="hi", env="WHISPER_LANGUAGE")
    WHISPER_BEAM_SIZE: int = Field(default=5, env="WHISPER_BEAM_SIZE")
    WHISPER_VAD_FILTER: bool = Field(default=True, env="WHISPER_VAD_FILTER")
    WHISPER_ENDPOINTING_MS: int = Field(default=400, env="WHISPER_ENDPOINTING_MS")

    VLLM_BASE_URL: str = Field(default="http://localhost:8001/v1", env="VLLM_BASE_URL")
    VLLM_MODEL: str = Field(
        default="mistralai/Mistral-Small-3.1-24B-Instruct-2503", env="VLLM_MODEL"
    )

    KOKORO_VOICE: str = Field(default="af_sarah", env="KOKORO_VOICE")
    KOKORO_SPEED: float = Field(default=1.1, env="KOKORO_SPEED")
    KOKORO_LANG: str = Field(default="en-us", env="KOKORO_LANG")
    KOKORO_SAMPLE_RATE: int = Field(default=8000, env="KOKORO_SAMPLE_RATE")

    CHATTERBOX_DEVICE: str = Field(default="cuda", env="CHATTERBOX_DEVICE")
    CHATTERBOX_EXAGGERATION: float = Field(default=0.4, env="CHATTERBOX_EXAGGERATION")
    CHATTERBOX_CFG_WEIGHT: float = Field(default=0.5, env="CHATTERBOX_CFG_WEIGHT")

    EMBEDDING_MODEL: str = Field(
        default="nomic-ai/nomic-embed-text-v1.5", env="EMBEDDING_MODEL"
    )
    EMBEDDING_DEVICE: str = Field(default="cpu", env="EMBEDDING_DEVICE")
    EMBEDDING_DIMENSIONS: int = Field(default=768, env="EMBEDDING_DIMENSIONS")
    RAG_TOP_K: int = Field(default=3, env="RAG_TOP_K")
    RAG_SIMILARITY_THRESHOLD: float = Field(
        default=0.70, env="RAG_SIMILARITY_THRESHOLD"
    )

    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    SLACK_HOT_LEAD_CHANNEL: str = Field(default="#hot-leads", env="SLACK_HOT_LEAD_CHANNEL")

    DATABASE_URL: str = Field(
        default="postgresql://vahanai:password@localhost:5432/vahanai_voice",
        env="DATABASE_URL",
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    SUPABASE_URL: str = Field(default="", env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(default="", env="SUPABASE_ANON_KEY")
    USE_DATABASE: bool = Field(default=False, env="USE_DATABASE")

    STT_MAX_LATENCY_MS: int = Field(default=600, env="STT_MAX_LATENCY_MS")
    LLM_MAX_LATENCY_MS: int = Field(default=1400, env="LLM_MAX_LATENCY_MS")
    TTS_MAX_LATENCY_MS: int = Field(default=500, env="TTS_MAX_LATENCY_MS")
    TOTAL_MAX_LATENCY_MS: int = Field(default=2500, env="TOTAL_MAX_LATENCY_MS")

    STARTUP_WARM_MODELS: bool = Field(default=False, env="STARTUP_WARM_MODELS")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
