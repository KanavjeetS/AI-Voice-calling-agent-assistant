"""
Open-source STT client: faster-whisper plus Groq fallback.

Tier routing:
  free      -> Groq Whisper API
  balanced  -> faster-whisper CPU
  full      -> faster-whisper GPU

faster-whisper does not expose true incremental streaming, so calls use a
sliding-window VAD buffer and transcribe on utterance end.
"""

import asyncio
import io
import logging
import time
from typing import Awaitable, Callable, Optional

import numpy as np

from config.settings import settings
from core.call_session import CallSession, Language

logger = logging.getLogger(__name__)

SILENCE_FRAMES_THRESHOLD = 15
AUDIO_SAMPLE_RATE = 8000
CHUNK_DURATION_MS = 20
CHUNK_BYTES = int(AUDIO_SAMPLE_RATE * CHUNK_DURATION_MS / 1000) * 2

Callback = Callable[..., Awaitable[None]]


class WhisperSTTStream:
    def __init__(
        self,
        session: CallSession,
        model: object,
        on_final: Callable[[str], Awaitable[None]],
        on_speech_started: Callback,
        on_speech_ended: Callback,
    ) -> None:
        self.session = session
        self.model = model
        self.on_final = on_final
        self.on_speech_started = on_speech_started
        self.on_speech_ended = on_speech_ended
        self._audio_buffer: list[bytes] = []
        self._silence_frames = 0
        self._is_speaking = False
        self._closed = False
        self._energy_threshold = 300

    async def send_audio(self, mulaw_bytes: bytes) -> None:
        if self._closed:
            return

        pcm_bytes = self._mulaw_to_pcm16(mulaw_bytes)
        energy = self._rms_energy(pcm_bytes)

        if energy > self._energy_threshold:
            if not self._is_speaking:
                self._is_speaking = True
                self._silence_frames = 0
                asyncio.create_task(self.on_speech_started())
            self._audio_buffer.append(pcm_bytes)
            self._silence_frames = 0
            return

        if self._is_speaking:
            self._silence_frames += 1
            self._audio_buffer.append(pcm_bytes)
            if self._silence_frames >= SILENCE_FRAMES_THRESHOLD:
                self._is_speaking = False
                asyncio.create_task(self.on_speech_ended())
                audio_data = b"".join(self._audio_buffer)
                self._audio_buffer = []
                self._silence_frames = 0
                asyncio.create_task(self._transcribe(audio_data))

    async def _transcribe(self, pcm_bytes: bytes) -> None:
        t0 = time.perf_counter()
        try:
            audio_np = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            lang = self._get_whisper_lang()
            loop = asyncio.get_running_loop()
            segments, info = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio_np,
                    language=lang,
                    beam_size=settings.WHISPER_BEAM_SIZE,
                    vad_filter=settings.WHISPER_VAD_FILTER,
                    vad_parameters={
                        "min_silence_duration_ms": 300,
                        "speech_pad_ms": 100,
                    },
                    word_timestamps=False,
                ),
            )
            transcript = " ".join(segment.text.strip() for segment in segments).strip()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            if transcript:
                detected = getattr(info, "language", None)
                if detected:
                    self._update_language(detected)
                logger.debug(
                    "[%s] Whisper transcript=%r latency_ms=%.0f language=%s",
                    self.session.call_sid,
                    transcript,
                    elapsed_ms,
                    detected,
                )
                await self.on_final(transcript)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("[%s] Whisper transcription failed: %s", self.session.call_sid, exc)

    def _mulaw_to_pcm16(self, mulaw_bytes: bytes) -> bytes:
        import audioop

        return audioop.ulaw2lin(mulaw_bytes, 2)

    def _rms_energy(self, pcm_bytes: bytes) -> float:
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        if samples.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(samples**2)))

    def _get_whisper_lang(self) -> Optional[str]:
        lang_map = {
            Language.HINDI: "hi",
            Language.ENGLISH: "en",
            Language.HINGLISH: None,
        }
        return lang_map.get(self.session.detected_language)

    def _update_language(self, detected: str) -> None:
        if detected == "hi":
            self.session.detected_language = Language.HINDI
        elif detected == "en":
            self.session.detected_language = Language.ENGLISH

    async def close(self) -> None:
        self._closed = True
        self._audio_buffer = []


class WhisperSTTClientGroq:
    def __init__(self) -> None:
        self._groq = None

    async def warm_up(self) -> None:
        if not settings.GROQ_API_KEY:
            logger.warning("Groq STT key not set; debug status will report not configured")
            return
        from groq import AsyncGroq

        self._groq = AsyncGroq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq STT client ready")

    async def transcribe(self, pcm_bytes: bytes, language: Optional[str] = None) -> tuple[str, Optional[str]]:
        if self._groq is None:
            return "", None
        import soundfile as sf

        buf = io.BytesIO()
        with sf.SoundFile(
            buf,
            mode="w",
            samplerate=AUDIO_SAMPLE_RATE,
            channels=1,
            format="WAV",
            subtype="PCM_16",
        ) as wav_file:
            wav_file.write(np.frombuffer(pcm_bytes, dtype=np.int16))
        buf.seek(0)

        try:
            response = await self._groq.audio.transcriptions.create(
                file=("audio.wav", buf, "audio/wav"),
                model=settings.GROQ_STT_MODEL,
                language=language or None,
                response_format="verbose_json",
            )
            # Access verbose_json fields
            if hasattr(response, "text"):
                transcript = response.text.strip()
                detected_lang = getattr(response, "language", None)
            else:
                # Fallback if dictionary returned
                res_dict = dict(response)
                transcript = res_dict.get("text", "").strip()
                detected_lang = res_dict.get("language", None)
            return transcript, detected_lang
        except Exception as exc:
            logger.exception("Groq STT failed: %s", exc)
            return "", None

    async def close(self) -> None:
        if self._groq is not None:
            await self._groq.close()


class GroqSTTStream:
    def __init__(
        self,
        session: CallSession,
        groq_client: WhisperSTTClientGroq,
        on_final: Callable[[str], Awaitable[None]],
        on_speech_started: Callback,
        on_speech_ended: Callback,
    ) -> None:
        self.session = session
        self._groq = groq_client
        self.on_final = on_final
        self.on_speech_started = on_speech_started
        self.on_speech_ended = on_speech_ended
        self._audio_buffer: list[bytes] = []
        self._silence_frames = 0
        self._is_speaking = False
        self._closed = False
        self._energy_threshold = 300

    async def send_audio(self, mulaw_bytes: bytes) -> None:
        if self._closed:
            return
        import audioop

        pcm_bytes = audioop.ulaw2lin(mulaw_bytes, 2)
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        energy = float(np.sqrt(np.mean(samples**2))) if samples.size else 0.0

        if energy > self._energy_threshold:
            if not self._is_speaking:
                self._is_speaking = True
                self._silence_frames = 0
                asyncio.create_task(self.on_speech_started())
            self._audio_buffer.append(pcm_bytes)
            self._silence_frames = 0
            return

        if self._is_speaking:
            self._silence_frames += 1
            self._audio_buffer.append(pcm_bytes)
            if self._silence_frames >= SILENCE_FRAMES_THRESHOLD:
                self._is_speaking = False
                asyncio.create_task(self.on_speech_ended())
                audio_data = b"".join(self._audio_buffer)
                self._audio_buffer = []
                self._silence_frames = 0
                
                lang = None
                if self.session.detected_language == Language.HINDI:
                    lang = "hi"
                elif self.session.detected_language == Language.ENGLISH:
                    lang = "en"
                asyncio.create_task(self._send_to_groq(audio_data, lang))

    async def _send_to_groq(self, pcm_bytes: bytes, language: Optional[str]) -> None:
        t0 = time.perf_counter()
        transcript, detected = await self._groq.transcribe(pcm_bytes, language)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if transcript:
            if detected:
                self._update_language(detected)
            logger.debug(
                "[%s] Groq STT transcript=%r latency_ms=%.0f language=%s",
                self.session.call_sid,
                transcript,
                elapsed_ms,
                detected,
            )
            await self.on_final(transcript)

    def _update_language(self, detected: str) -> None:
        detected = detected.lower()
        if detected == "hi" or detected == "hindi":
            self.session.detected_language = Language.HINDI
        elif detected == "en" or detected == "english":
            self.session.detected_language = Language.ENGLISH

    async def close(self) -> None:
        self._closed = True


class WhisperSTTClient:
    def __init__(self) -> None:
        self._model: Optional[object] = None
        self._groq_client: Optional[WhisperSTTClientGroq] = None

    async def warm_up(self) -> None:
        if settings.MODEL_TIER in ("balanced", "full"):
            from faster_whisper import WhisperModel

            loop = asyncio.get_running_loop()
            self._model = await loop.run_in_executor(
                None,
                lambda: WhisperModel(
                    settings.WHISPER_MODEL_SIZE,
                    device=settings.WHISPER_DEVICE,
                    compute_type=settings.WHISPER_COMPUTE_TYPE,
                    num_workers=2,
                ),
            )
            logger.info("faster-whisper ready")

        if settings.MODEL_TIER == "free":
            self._groq_client = WhisperSTTClientGroq()
            await self._groq_client.warm_up()

        logger.info("STT client ready tier=%s", settings.MODEL_TIER)

    async def create_stream(
        self,
        session: CallSession,
        on_final: Callable[[str], Awaitable[None]],
        on_speech_started: Callback,
        on_speech_ended: Callback,
        on_interim: Optional[Callback] = None,
    ) -> WhisperSTTStream | GroqSTTStream:
        if settings.MODEL_TIER == "free":
            if self._groq_client is None:
                self._groq_client = WhisperSTTClientGroq()
                await self._groq_client.warm_up()
            return GroqSTTStream(
                session=session,
                groq_client=self._groq_client,
                on_final=on_final,
                on_speech_started=on_speech_started,
                on_speech_ended=on_speech_ended,
            )
        if self._model is None:
            await self.warm_up()
        return WhisperSTTStream(
            session=session,
            model=self._model,
            on_final=on_final,
            on_speech_started=on_speech_started,
            on_speech_ended=on_speech_ended,
        )

    async def close(self) -> None:
        if self._groq_client is not None:
            await self._groq_client.close()


stt_client = WhisperSTTClient()
