#!/bin/sh
set -e

# Ensure data directory exists and is writable before anything touches SQLite
mkdir -p /app/data/csv /app/data/pdf

# Run data ingestion only if the database hasn't been seeded yet
if [ ! -f /app/data/.seeded ]; then
  echo "==> Running data ingestion pipeline..."
  python scripts/ingest_all.py
  touch /app/data/.seeded
  echo "==> Ingestion complete."
else
  echo "==> Data already seeded, skipping ingestion."
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
