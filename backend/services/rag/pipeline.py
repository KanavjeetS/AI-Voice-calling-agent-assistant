from typing import List

from services.rag.embeddings import embed_text


async def embed_query(query_text: str) -> List[float]:
    return await embed_text(query_text)


KNOWLEDGE_CHUNKS_DDL = """
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);
"""
