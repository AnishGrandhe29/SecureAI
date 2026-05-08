# Secure AI Insights Assistant

> **AI-powered analytics assistant with multi-source reasoning** — built with Python/FastAPI, Next.js 14, GPT-4o (function calling), ChromaDB, SQLite, and Redis.

![Stack](https://img.shields.io/badge/Python-3.11-blue) ![Stack](https://img.shields.io/badge/Next.js-14-black) ![Stack](https://img.shields.io/badge/GPT--4o-OpenAI-green) ![Stack](https://img.shields.io/badge/Docker-Compose-blue)

---

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/your-username/secure-insights
cd secure-insights
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY and a random SECRET_KEY

# 2. Start the full stack
docker compose up --build

# 3. Open the app
open http://localhost:3000
```

## Demo Credentials

| Username | Password | Role | Access |
|---|---|---|---|
| `analyst` | `analyst123` | Analyst | Chat, Insights, Analytics |
| `admin` | `admin123` | Admin | All above + data ingestion |

## Example Questions to Try

1. *Which titles performed best in 2025?*
2. *Why is Stellar Run trending recently?*
3. *Compare Dark Orbit vs Last Kingdom.*
4. *Which city had the strongest engagement last month?*
5. *What explains weak comedy performance?*
6. *What recommendations would you give for leadership?*

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│  Next.js 14  │───▶│  FastAPI API  │───▶│   GPT-4o Orchestrator   │
│  (Frontend)  │    │  (Gateway)   │    │  (Function Calling)     │
└─────────────┘    └──────────────┘    └────────┬────────────────┘
                                                │
                         ┌──────────────────────┼───────────────────┐
                         ▼                      ▼                   ▼
                  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
                  │  SQL Tool    │    │  RAG Tool     │    │  CSV Tool    │
                  │  (SQLite)    │    │  (ChromaDB)   │    │  (Pandas)    │
                  └─────────────┘    └──────────────┘    └─────────────┘
```

## Architecture Decisions & Tradeoffs

| Decision | Rationale |
|---|---|
| Named SQL templates instead of LLM-generated SQL | **Security**: prevents SQL injection; the LLM picks a template, never writes SQL |
| ChromaDB local persistence | Simplicity: no extra container; production would swap for Qdrant or Weaviate |
| `all-MiniLM-L6-v2` for embeddings | CPU-compatible; no GPU required; ~80MB download |
| Pandas DataFrames in memory | CSVs are small and static; avoids duplicate DB load |
| JWT over sessions | Stateless; works across replicas without shared session store |
| Presidio PII scrubbing | Production-grade; avoids sending viewer PII to the LLM |
| Redis TTL caching | Analytics queries are expensive; 5-minute TTL keeps UI responsive |
| Tool-based architecture | LLM never touches raw data; every data access is mediated and auditable |

## Security Controls

| Control | Implementation |
|---|---|
| SQL injection prevention | All SQL runs through named template catalogue — LLM never generates raw SQL |
| Authentication | JWT HS256, 8-hour expiry, verified on every protected endpoint |
| Authorization | RBAC middleware: `analyst` vs `admin` roles enforced via FastAPI dependency |
| CORS | Restricted to `ALLOWED_ORIGINS` env var; default `localhost:3000` only |
| PII scrubbing | Microsoft Presidio runs on all retrieved text before it is returned to the LLM or client |
| Secrets management | All secrets via `.env` / environment variables; `.env.example` provided with no secret defaults |
| Rate limiting | `30 req/min` per IP on the chat endpoint via `slowapi` |
| Audit logging | Every request and tool call logged with structlog (JSON). Raw results never logged |
| Input validation | All request bodies validated via Pydantic models with explicit field constraints |
| Admin endpoint protection | Ingest routes require `role == "admin"` checked in dependency |

## Assumptions

- **SQLite** used for development portability. `DATABASE_URL` env var switches to PostgreSQL for production with zero code changes.
- **ChromaDB** runs in-process using local file persistence. Production would use Qdrant or Weaviate for horizontal scaling.
- **`all-MiniLM-L6-v2`** chosen for embedding — requires no GPU, downloads ~80MB on first run.
- **Synthetic data** seeded with `random.seed(42)` — results are deterministic and reproducible.
- **Demo users are hard-coded** — no user management UI. Production would use a proper user store with hashed passwords.
- **PDF chunking** uses fixed 400-token windows with 50-token overlap. Production would use semantic chunking.
- **Tool templates are a fixed allowlist** — deliberate security decision. The LLM cannot construct arbitrary queries.
- **No streaming** on chat — full response returned as single JSON. SSE streaming is a straightforward upgrade.
- **HTTPS** not configured at application level — assumed handled by reverse proxy in production.
- **Data volumes** — ~5,000 rows per table, ~500 ChromaDB vectors. Fits on any machine with 4GB RAM.

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/token` | None | Get JWT token |
| POST | `/api/chat` | Bearer | Multi-turn AI chat |
| GET | `/api/analytics/top-titles` | Bearer | Top titles by revenue |
| GET | `/api/analytics/genre-trends` | Bearer | Genre performance over time |
| GET | `/api/analytics/city-engagement` | Bearer | City engagement rankings |
| GET | `/api/analytics/marketing-roi` | Bearer | Marketing ROI by title |
| POST | `/api/ingest/csv` | Admin | Re-seed database |
| POST | `/api/ingest/pdfs` | Admin | Re-embed PDFs |
| GET | `/api/ingest/status` | Admin | Data status |
| GET | `/api/health` | None | Health check |

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python 3.11) |
| AI Model | GPT-4o (OpenAI function calling) |
| SQL Database | SQLite (dev) / PostgreSQL (prod) |
| Vector Store | ChromaDB |
| Embedding | `all-MiniLM-L6-v2` |
| Cache | Redis 7 |
| PII Scrubbing | Microsoft Presidio |
| Frontend | Next.js 14 (App Router) |
| Charts | Recharts |
| Auth | JWT (python-jose) + RBAC |
| Logging | Structlog (JSON) |
| Container | Docker Compose |
