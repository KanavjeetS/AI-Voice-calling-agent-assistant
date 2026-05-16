import asyncio
import logging
from typing import List, Optional

from config.settings import settings

logger = logging.getLogger(__name__)

_model: Optional[object] = None


async def load_embedding_model() -> None:
    global _model
    if _model is not None:
        return
    from sentence_transformers import SentenceTransformer

    loop = asyncio.get_running_loop()
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    _model = await loop.run_in_executor(
        None,
        lambda: SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE,
            trust_remote_code=True,
        ),
    )
    logger.info("Embedding model loaded dims=%s", settings.EMBEDDING_DIMENSIONS)


async def embed_text(text: str) -> List[float]:
    if _model is None:
        await load_embedding_model()
    loop = asyncio.get_running_loop()
    vector = await loop.run_in_executor(
        None,
        lambda: _model.encode(
            [text],
            normalize_embeddings=True,
            prompt_name="search_document",
        )[0],
    )
    return vector.tolist()


async def embed_batch(texts: List[str]) -> List[List[float]]:
    if _model is None:
        await load_embedding_model()
    loop = asyncio.get_running_loop()
    vectors = await loop.run_in_executor(
        None,
        lambda: _model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            prompt_name="search_document",
        ),
    )
    return [vector.tolist() for vector in vectors]
