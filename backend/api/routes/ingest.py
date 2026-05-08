"""
Ingest endpoints — admin only.
POST /api/ingest/csv   → re-seed database from CSVs
POST /api/ingest/pdfs  → re-embed PDFs into ChromaDB
GET  /api/ingest/status → row counts + vector doc count
"""

import structlog
from fastapi import APIRouter, Depends
from api.middleware.auth import require_admin, User

logger = structlog.get_logger()
router = APIRouter()


@router.post("/ingest/csv")
async def ingest_csv(admin: User = Depends(require_admin)):
    """Re-run CSV → database seed pipeline."""
    from db.seed import seed_database
    await seed_database()
    logger.info("ingest_csv", user_id=admin.username)
    return {"status": "success", "message": "Database re-seeded from CSVs"}


@router.post("/ingest/pdfs")
async def ingest_pdfs(admin: User = Depends(require_admin)):
    """Re-run PDF → ChromaDB embed pipeline."""
    from vector.embedder import embed_all_pdfs
    from vector.retriever import Retriever

    chunks = embed_all_pdfs()
    retriever = Retriever()
    retriever.upsert_chunks(chunks)
    logger.info("ingest_pdfs", user_id=admin.username, chunk_count=len(chunks))
    return {"status": "success", "chunks_embedded": len(chunks)}


@router.get("/ingest/status")
async def ingest_status(admin: User = Depends(require_admin)):
    """Return row counts per table and vector document count."""
    from sqlalchemy import text
    from db.database import AsyncSessionLocal
    from vector.retriever import Retriever

    tables = ["movies", "viewers", "watch_activity", "reviews", "marketing_spend", "regional_performance"]
    counts = {}

    async with AsyncSessionLocal() as session:
        for table in tables:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            counts[table] = result.scalar()

    retriever = Retriever()
    counts["vector_documents"] = retriever.count()

    return {"status": "success", "counts": counts}
