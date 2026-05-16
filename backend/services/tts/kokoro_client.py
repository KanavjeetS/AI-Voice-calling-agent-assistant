import asyncio
import logging
from typing import AsyncGenerator, Optional

import numpy as np

from config.settings import settings
from core.call_session import Language

logger = logging.getLogger(__name__)


class KokoroTTSClient:
    def __init__(self) -> None:
        self._pipeline: Optional[object] = None

    async def warm_up(self) -> None:
        from kokoro_onnx import Kokoro

        loop = asyncio.get_running_loop()
        self._pipeline = await loop.run_in_executor(
            None,
            lambda: Kokoro("kokoro-v1_0.onnx", "voices-v1_0.bin"),
        )
        logger.info("Kokoro TTS ready voice=%s", settings.KOKORO_VOICE)

    async def synthesize_stream(
        self,
        text: str,
        language: Language = Language.HINGLISH,
        voice_settings: Optional[dict] = None,
        **kwargs: object,
    ) -> AsyncGenerator[bytes, None]:
        if not text.strip():
            return
        if self._pipeline is None:
            await self.warm_up()

        voice = self._select_voice(language)
        lang = self._select_lang(language)
        loop = asyncio.get_running_loop()
        try:
            samples, sample_rate = await loop.run_in_executor(
                None,
                lambda: self._pipeline.create(
                    text,
                    voice=voice,
                    speed=settings.KOKORO_SPEED,
                    lang=lang,
                ),
            )
            mulaw_bytes = self._convert_to_twilio(samples, int(sample_rate))
            for index in range(0, len(mulaw_bytes), 160):
                chunk = mulaw_bytes[index : index + 160]
                if chunk:
                    yield chunk
                    await asyncio.sleep(0)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Kokoro synthesis failed: %s", exc)

    def _convert_to_twilio(self, samples: np.ndarray, src_rate: int) -> bytes:
        import audioop

        mono = np.asarray(samples, dtype=np.float32).reshape(-1)
        if src_rate != settings.KOKORO_SAMPLE_RATE:
            mono = self._resample(mono, src_rate, settings.KOKORO_SAMPLE_RATE)
        mono = np.clip(mono, -1.0, 1.0)
        pcm16 = (mono * 32767).astype(np.int16).tobytes()
        return audioop.lin2ulaw(pcm16, 2)

    def _resample(self, samples: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
        if len(samples) == 0:
            return samples
        ratio = dst_rate / src_rate
        n_samples = max(1, int(len(samples) * ratio))
        indices = np.linspace(0, len(samples) - 1, n_samples)
        return np.interp(indices, np.arange(len(samples)), samples)

    def _select_voice(self, language: Language) -> str:
        if language == Language.HINDI:
            return "hf_alpha"
        return settings.KOKORO_VOICE

    def _select_lang(self, language: Language) -> str:
        if language == Language.HINDI:
            return "hi"
        return settings.KOKORO_LANG

    async def synthesize_complete(
        self,
        text: str,
        language: Language = Language.HINGLISH,
    ) -> Optional[bytes]:
        chunks: list[bytes] = []
        async for chunk in self.synthesize_stream(text, language):
            chunks.append(chunk)
        return b"".join(chunks) if chunks else None

    async def close(self) -> None:
        logger.info("Kokoro TTS client closed")


class ChatterboxTTSClient:
    def __init__(self) -> None:
        self._model: Optional[object] = None

    async def warm_up(self) -> None:
        from chatterbox.tts import ChatterboxTTS

        loop = asyncio.get_running_loop()
        self._model = await loop.run_in_executor(
            None,
            lambda: ChatterboxTTS.from_pretrained(device=settings.CHATTERBOX_DEVICE),
        )
        logger.info("Chatterbox TTS ready device=%s", settings.CHATTERBOX_DEVICE)

    async def synthesize_stream(
        self,
        text: str,
        language: Language = Language.HINGLISH,
        **kwargs: object,
    ) -> AsyncGenerator[bytes, None]:
        if self._model is None:
            await self.warm_up()

        loop = asyncio.get_running_loop()
        try:
            wav_tensor = await loop.run_in_executor(
                None,
                lambda: self._model.generate(
                    text,
                    exaggeration=settings.CHATTERBOX_EXAGGERATION,
                    cfg_weight=settings.CHATTERBOX_CFG_WEIGHT,
                ),
            )
            samples = wav_tensor.squeeze().detach().cpu().numpy()
            mulaw = KokoroTTSClient()._convert_to_twilio(samples, 24000)
            for index in range(0, len(mulaw), 160):
                chunk = mulaw[index : index + 160]
                if chunk:
                    yield chunk
                    await asyncio.sleep(0)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Chatterbox synthesis failed: %s", exc)

    async def synthesize_complete(
        self,
        text: str,
        language: Language = Language.HINGLISH,
    ) -> Optional[bytes]:
        chunks: list[bytes] = []
        async for chunk in self.synthesize_stream(text, language):
            chunks.append(chunk)
        return b"".join(chunks) if chunks else None

    async def close(self) -> None:
        logger.info("Chatterbox TTS client closed")


def create_tts_client() -> KokoroTTSClient | ChatterboxTTSClient:
    if settings.MODEL_TIER == "full":
        return ChatterboxTTSClient()
    return KokoroTTSClient()


tts_client = create_tts_client()
