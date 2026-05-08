"""
One-shot pipeline: generate synthetic data → seed database → embed PDFs into ChromaDB.
Run during Docker build or manually for local development.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    print("=" * 60)
    print("SecureAI Insights — Data Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Generate synthetic data
    print("\n[1/3] Generating synthetic data...")
    from scripts.generate_data import main as generate_main
    generate_main()

    # Step 2: Seed database
    print("\n[2/3] Seeding database...")
    from db.seed import seed_database
    await seed_database()

    # Step 3: Embed PDFs into ChromaDB
    print("\n[3/3] Embedding PDF documents into ChromaDB...")
    from vector.embedder import embed_all_pdfs
    from vector.retriever import Retriever

    chunks = embed_all_pdfs()
    retriever = Retriever()
    retriever.upsert_chunks(chunks)
    print(f"  [OK] {len(chunks)} chunks embedded into ChromaDB")

    print("\n" + "=" * 60)
    print("✓ Ingestion pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
