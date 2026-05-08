"""
ChromaDB persistent client — collection operations for the insights_docs collection.
Supports upsert and hybrid retrieval with optional metadata filtering.
"""

import chromadb
from pydantic import BaseModel
from config import settings
from vector.embedder import Chunk, _get_model


class RetrievedChunk(BaseModel):
    content: str
    source: str
    score: float
    metadata: dict


COLLECTION_NAME = "insights_docs"


class Retriever:
    """Manages ChromaDB collection for document retrieval."""

    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[Chunk]) -> None:
        """Upsert a list of embedded chunks into the collection."""
        if not chunks:
            return

        ids = [f"{c.metadata['source_file']}_{c.metadata['chunk_index']}" for c in chunks]
        documents = [c.content for c in chunks]
        embeddings = [c.embedding for c in chunks]
        metadatas = [c.metadata for c in chunks]

        # ChromaDB has a batch limit — upsert in batches of 500
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            end = i + batch_size
            self._collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
            )

    def query(
        self,
        text: str,
        n_results: int = 5,
        where_filter: dict | None = None,
    ) -> list[RetrievedChunk]:
        """Query the collection by text similarity, with optional metadata filter."""
        model = _get_model()
        query_embedding = model.encode(text).tolist()

        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if where_filter:
            query_params["where"] = where_filter

        results = self._collection.query(**query_params)

        retrieved = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0.0
                score = 1.0 - distance  # cosine distance → similarity
                retrieved.append(RetrievedChunk(
                    content=doc,
                    source=meta.get("source_file", "unknown"),
                    score=round(score, 4),
                    metadata=meta,
                ))
        return retrieved

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self._collection.count()
