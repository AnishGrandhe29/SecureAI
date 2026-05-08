"""
RAG Tool — ChromaDB hybrid retrieval with PII scrubbing.
All retrieved text is scrubbed through Presidio before returning.
"""

from vector.retriever import Retriever, RetrievedChunk
from services.pii_service import scrub

_retriever = None


def _get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


async def search_documents(
    query: str,
    doc_type: str | None = None,
) -> dict:
    """
    Retrieve relevant passages from PDF documents.
    All returned text is PII-scrubbed via Presidio.
    """
    retriever = _get_retriever()

    where_filter = None
    if doc_type:
        where_filter = {"doc_type": doc_type}

    chunks = retriever.query(text=query, n_results=5, where_filter=where_filter)

    # PII-scrub all retrieved content
    scrubbed_chunks = []
    for chunk in chunks:
        scrubbed_chunks.append({
            "content": scrub(chunk.content),
            "source": chunk.source,
            "score": chunk.score,
            "metadata": chunk.metadata,
        })

    return {
        "chunks": scrubbed_chunks,
        "source": "pdf_documents",
    }
