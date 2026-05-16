# Latency Profile

This Phase 0 profile documents honest open-source latency expectations for the
Twilio -> STT -> LLM -> TTS -> Twilio loop. Measure production values with real
PSTN traffic because network RTT, utterance length, and model warm state have a
large effect on tail latency.

| Tier | Twilio ingress | STT | LLM | TTS | Twilio egress | Expected perceived total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| free | 80-150 ms | 500-800 ms Groq Whisper | 600-900 ms Groq Llama | 150-300 ms Kokoro CPU | 80-150 ms | 1.8-2.3 s |
| balanced | 80-150 ms | 400-700 ms faster-whisper CPU | 600-900 ms Groq Llama | 150-300 ms Kokoro CPU | 80-150 ms | 1.7-2.2 s |
| full | 80-150 ms | 150-300 ms faster-whisper GPU | 500-800 ms vLLM Mistral | 100-200 ms Chatterbox GPU | 80-150 ms | 1.0-1.6 s |

## Budget

The runtime budget is configured in `backend/config/settings.py`:

| Stage | Budget |
| --- | ---: |
| STT | 600 ms |
| LLM | 1400 ms |
| TTS | 500 ms |
| Total | 2500 ms |

## Phase 0 Implementation Notes

faster-whisper and Kokoro are blocking model calls, so the backend wraps them in
`run_in_executor` to keep WebSocket media handling responsive. Groq STT also uses
local VAD and buffered utterance transcription because Whisper APIs are not true
streaming STT connections.
