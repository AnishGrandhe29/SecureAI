"""
PDF parsing, chunking (400-token windows / 50-token overlap), and embedding
using sentence-transformers/all-MiniLM-L6-v2 (CPU-compatible, ~80MB).
"""

from pathlib import Path
from pydantic import BaseModel
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 400   # tokens (approximated as words for simplicity)
CHUNK_OVERLAP = 50

PDF_DIR = Path(__file__).parent.parent / "data" / "pdfs"

# Lazy-loaded model singleton
_model = None

DOC_TYPE_MAP = {
    "quarterly_executive_report_q1_2025.pdf": "quarterly_report",
    "campaign_performance_summary.pdf": "campaign",
    "content_roadmap_2025.pdf": "roadmap",
    "platform_policy_guidelines.pdf": "policy",
    "audience_behavior_report.pdf": "audience",
}


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


class Chunk(BaseModel):
    content: str
    embedding: list[float]
    metadata: dict


def _extract_text(path: Path) -> list[tuple[int, str]]:
    """Extract text from PDF, returning list of (page_number, text)."""
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append((i + 1, text.strip()))
    return pages


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks based on word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def embed_pdf(path: Path) -> list[Chunk]:
    """Parse a single PDF → chunk → embed → return list of Chunk."""
    model = _get_model()
    filename = path.name
    doc_type = DOC_TYPE_MAP.get(filename, "unknown")
    pages = _extract_text(path)

    all_chunks = []
    chunk_index = 0

    for page_num, page_text in pages:
        text_chunks = _chunk_text(page_text)
        for chunk_text in text_chunks:
            embedding = model.encode(chunk_text).tolist()
            all_chunks.append(Chunk(
                content=chunk_text,
                embedding=embedding,
                metadata={
                    "source_file": filename,
                    "page_number": page_num,
                    "chunk_index": chunk_index,
                    "doc_type": doc_type,
                },
            ))
            chunk_index += 1

    return all_chunks


def embed_all_pdfs() -> list[Chunk]:
    """Embed all PDFs in the data/pdfs directory."""
    all_chunks = []
    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        chunks = embed_pdf(pdf_path)
        print(f"  [EMBED] {pdf_path.name}: {len(chunks)} chunks")
        all_chunks.extend(chunks)
    return all_chunks
