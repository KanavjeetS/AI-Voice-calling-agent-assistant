# VahanAI Studio

Production-oriented AI voice calling platform for loan follow-up and customer
support. The stack keeps Twilio for PSTN and replaces paid AI APIs with
open-source or free-tier providers:

- STT: Groq Whisper in `free`, faster-whisper in `balanced` and `full`
- LLM: Groq Llama in `free` and `balanced`, vLLM Mistral in `full`
- TTS: Kokoro-82M in `free` and `balanced`, Chatterbox-Turbo in `full`
- CRM/data: PostgreSQL + pgvector, with in-memory demo fallback
- Alerts: Slack incoming webhooks

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`  
Dashboard: `http://localhost:3000`

For local backend-only validation:

```bash
cd backend
set PYTHONPATH=%CD%
uvicorn main:app --reload --port 8000
```

## Required Demo Endpoints

- `GET /health`
- `POST /api/v1/calls/initiate`
- `GET /api/v1/debug/stt-test`
- `GET /api/v1/debug/llm-test`
- `GET /api/v1/debug/tts-test?text=hello+world`

## Deliverables

- Architecture diagram: `docs/ARCHITECTURE.md`
- API flow: `docs/API_FLOW.md`
- Latency profiling: `docs/LATENCY.md`
- Scalability roadmap: `docs/SCALABILITY.md`
- Demo script: `docs/DEMO_SCRIPT.md`
