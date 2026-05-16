# Scalability Roadmap: 500 Concurrent Calls

## Current Phase

Phase 0-6 code keeps the realtime path async and wraps blocking model calls in
`run_in_executor`. The API surface is ready for horizontal scaling, while the
demo store can be swapped for PostgreSQL using the included schema.

## 500-Call Target

| Layer | Plan |
| --- | --- |
| Twilio ingress | Use regional Twilio media streams and distribute calls by webhook URL |
| API WebSockets | Run 8-12 FastAPI workers across multiple containers; sticky routing by call SID |
| STT | Use Groq for burst free-tier demos; for production use faster-whisper GPU workers behind an internal queue |
| LLM | Use Groq for free/balanced tiers; full tier deploys vLLM with batching and autoscaling |
| TTS | Pool Kokoro CPU workers; full tier uses GPU Chatterbox workers |
| State | Redis for session registry, interruption flags, and live transcript fanout |
| CRM | PostgreSQL primary with read replicas for dashboard traffic |
| Observability | Per-stage latency histograms, p95 alarms, and per-provider failure rates |

## Capacity Math

At 500 concurrent calls, assume one customer utterance every 8 seconds:

- About 62 realtime turns per second
- STT workers sized for p95 under 700ms
- LLM budget p95 under 1400ms
- TTS budget p95 under 500ms

Use provider circuit breakers. If Groq rate limits, route to self-hosted vLLM or
short deterministic fallback prompts for safety-critical call handling.
