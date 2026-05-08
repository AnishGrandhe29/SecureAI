"""
CSV → database bulk loader. Idempotent: truncates tables before insert.
Reads all 6 CSVs and bulk-inserts via SQLAlchemy in chunked batches of 500.
"""

import asyncio
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from db.database import engine, AsyncSessionLocal, init_db
from db.models import Movie, Viewer, WatchActivity, Review, MarketingSpend, RegionalPerformance

DATA_DIR = Path(__file__).parent.parent / "data" / "csv"

TABLE_MAP = {
    "movies.csv": ("movies", Movie),
    "viewers.csv": ("viewers", Viewer),
    "watch_activity.csv": ("watch_activity", WatchActivity),
    "reviews.csv": ("reviews", Review),
    "marketing_spend.csv": ("marketing_spend", MarketingSpend),
    "regional_performance.csv": ("regional_performance", RegionalPerformance),
}

BATCH_SIZE = 500


async def seed_database():
    """Load all CSVs into the database. Truncates existing data first."""
    await init_db()

    async with AsyncSessionLocal() as session:
        for csv_file, (table_name, _model_cls) in TABLE_MAP.items():
            csv_path = DATA_DIR / csv_file
            if not csv_path.exists():
                print(f"  [SKIP] {csv_file} not found")
                continue

            # Truncate table for idempotency
            await session.execute(text(f"DELETE FROM {table_name}"))
            await session.commit()

            df = pd.read_csv(csv_path)
            # Strip whitespace from column names
            df.columns = [c.strip() for c in df.columns]
            rows = df.to_dict(orient="records")

            # Bulk insert in batches
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                await session.execute(
                    text(
                        f"INSERT INTO {table_name} ({', '.join(batch[0].keys())}) "
                        f"VALUES ({', '.join(':' + k for k in batch[0].keys())})"
                    ),
                    batch,
                )
                await session.commit()

            print(f"  [OK] {table_name}: {len(rows)} rows inserted")


if __name__ == "__main__":
    asyncio.run(seed_database())
