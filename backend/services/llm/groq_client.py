import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class GroqLLMClient:
    def __init__(self) -> None:
        self._client: Optional[object] = None

    async def warm_up(self) -> None:
        if not settings.GROQ_API_KEY:
            logger.warning("Groq API key not set; LLM calls will be unavailable")
            return
        from groq import AsyncGroq

        self._client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        try:
            models = await self._client.models.list()
            available = [model.id for model in models.data]
            if settings.GROQ_LLM_MODEL not in available:
                logger.warning(
                    "Configured Groq model %s not listed; first available=%s",
                    settings.GROQ_LLM_MODEL,
                    available[:1],
                )
            logger.info("Groq LLM client ready model=%s", settings.GROQ_LLM_MODEL)
        except Exception as exc:
            logger.warning("Groq LLM warm-up skipped: %s", exc)

    async def stream(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        if self._client is None:
            await self.warm_up()
        if self._client is None:
            return

        full_messages = [{"role": "system", "content": system_prompt}, *messages]
        retries = 0
        while retries <= 2:
            try:
                stream = await self._client.chat.completions.create(
                    model=settings.GROQ_LLM_MODEL,
                    messages=full_messages,
                    max_tokens=max_tokens or settings.GROQ_LLM_MAX_TOKENS,
                    temperature=temperature if temperature is not None else settings.GROQ_LLM_TEMPERATURE,
                    stream=True,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
                return
            except Exception as exc:
                if "rate_limit" in str(exc).lower():
                    retries += 1
                    await asyncio.sleep(2**retries)
                    continue
                logger.exception("Groq LLM stream failed: %s", exc)
                return

    async def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 200,
        temperature: float = 0.1,
        system_prompt: Optional[str] = None,
    ) -> str:
        if self._client is None:
            await self.warm_up()
        if self._client is None:
            raise RuntimeError("Groq client is not configured")

        full_messages = messages
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}, *messages]
        response = await self._client.chat.completions.create(
            model=settings.GROQ_LLM_MODEL,
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )
        return response.choices[0].message.content or ""

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()


class VLLMClient:
    def __init__(self) -> None:
        self._base_url = settings.VLLM_BASE_URL
        self._model = settings.VLLM_MODEL
        self._http_client: Optional[object] = None

    async def warm_up(self) -> None:
        import httpx

        self._http_client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(connect=3.0, read=15.0, write=5.0, pool=None),
        )
        try:
            response = await self._http_client.get("/models")
            response.raise_for_status()
            logger.info("vLLM client ready model=%s", self._model)
        except httpx.HTTPError as exc:
            logger.warning("vLLM warm-up failed: %s", exc)

    async def stream(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        import httpx

        payload = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "max_tokens": max_tokens or settings.GROQ_LLM_MAX_TOKENS,
            "temperature": temperature if temperature is not None else settings.GROQ_LLM_TEMPERATURE,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{self._base_url}/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line.removeprefix("data: ").strip()
                    if data == "[DONE]":
                        break
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    async def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 200,
        temperature: float = 0.1,
        system_prompt: Optional[str] = None,
    ) -> str:
        import httpx

        full_messages = messages
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}, *messages]
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                json={
                    "model": self._model,
                    "messages": full_messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"].get("content", "")

    async def close(self) -> None:
        if self._http_client is not None:
            await self._http_client.aclose()


def create_llm_client() -> GroqLLMClient | VLLMClient:
    if settings.MODEL_TIER == "full":
        return VLLMClient()
    return GroqLLMClient()


llm_client = create_llm_client()
