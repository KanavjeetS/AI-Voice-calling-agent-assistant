<div align="center">

# 🎙️ VahanAI Studio: Next-Gen Voice AI Calling Platform

<img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge&logo=rocket" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" />
<img src="https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=Twilio&logoColor=white" />
<img src="https://img.shields.io/badge/Groq-FF4F00?style=for-the-badge&logo=groq&logoColor=white" />

<p align="center">
  <b>A state-of-the-art, ultra-low latency conversational AI platform designed for seamless loan follow-ups and high-ticket customer support.</b>
</p>

</div>

---

## ✨ Majestic Capabilities & Glorious Features

Welcome to **VahanAI Studio** — where traditional PSTN telephony meets the absolute cutting edge of open-source Generative AI. We bypass expensive managed AI endpoints and deploy a custom, hyper-optimized LLM + TTS + STT pipeline capable of natural, bi-directional, interruptible human conversations.

- **🚀 Ultra-Low Latency Streaming:** Engineered for `< 500ms` endpoint-to-endpoint response times utilizing WebSockets.
- **🧠 Advanced Conversational Memory:** Context-aware LLM orchestration ensuring leads feel heard and understood.
- **⚡ Open-Source AI Stack:** Powered by **Groq Llama** (LLM), **faster-whisper** (STT), and **Kokoro-82M / Chatterbox** (TTS).
- **🌐 Enterprise Telephony Integration:** Seamless integration with **Twilio Media Streams** for real, live, inbound and outbound calling.
- **📊 Majestic Dashboard:** A glorious, dark-mode Next.js command center to monitor live calls, analytics, and CRM metrics in real-time.

---

## 🏗️ Glorious Architecture Stack

Our stack is meticulously crafted to balance extreme performance with cost efficiency, replacing paid APIs with hyper-optimized open-source models:

| Component | Technology / Model Stack | Purpose |
| --- | --- | --- |
| **Backend Core** | `FastAPI` + `WebSockets` | Asynchronous high-throughput request handling |
| **STT (Speech-to-Text)** | `Groq Whisper` / `faster-whisper` | Real-time audio transcription |
| **LLM Orchestration** | `Groq Llama` / `vLLM Mistral` | Cognitive processing & contextual responses |
| **TTS (Text-to-Speech)** | `Kokoro-82M` / `Chatterbox-Turbo` | Human-like voice synthesis (streaming) |
| **Telephony** | `Twilio` | Global PSTN inbound & outbound connectivity |
| **Frontend** | `Next.js 14` + `React` | Real-time operational dashboard & monitoring |
| **Data Layer** | `PostgreSQL` + `pgvector` | CRM persistence & vector embeddings for RAG |

---

## 🚀 Quick Start Guide

Transform your local machine into an enterprise-grade AI telephony hub.

### 1. ⚙️ Environment Setup
```bash
cp .env.example .env
# Fill in your Twilio Account SID, Auth Token, and Groq API Key
```

### 2. 🐳 Launch via Docker Compose (Recommended)
Launch the entire majestic stack in one command:
```bash
docker compose up --build
```
- **API Engine:** `http://localhost:8000`
- **Dashboard Command Center:** `http://localhost:3000`

### 3. 🖥️ Local Backend Validation (Developer Mode)
For ultra-fast iteration and local debugging:
```bash
cd backend
set PYTHONPATH=%CD%
uvicorn main:app --reload --port 8000
```

---

## 🎯 Verification & Demo Endpoints

To guarantee a flawless deployment, verify the platform health using our built-in diagnostic suite:

- 🟢 `GET /health` — General cluster status
- 📞 `POST /api/v1/calls/initiate` — Trigger an outbound Twilio lead call
- 🎙️ `GET /api/v1/debug/stt-test` — STT Pipeline validation
- 🧠 `GET /api/v1/debug/llm-test` — Cognitive Engine validation
- 🗣️ `GET /api/v1/debug/tts-test?text=hello+world` — Audio synthesis validation

---

## 📚 Comprehensive Documentation

Explore the depth of VahanAI Studio's engineering:

- 🏗️ [Architecture Overview](docs/ARCHITECTURE.md)
- 🔄 [API Request Flow](docs/API_FLOW.md)
- ⚡ [Latency Profiling & Optimizations](docs/LATENCY.md)
- 📈 [Scalability & Infrastructure Roadmap](docs/SCALABILITY.md)
- 📜 [Official Demo Script](docs/DEMO_SCRIPT.md)

---

<div align="center">
<i>Built with absolute precision for high-performance enterprise customer engagement.</i>
</div>
