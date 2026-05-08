"""
Analytics endpoints — pre-canned queries for the Insights Panel.
All cached in Redis with 5-minute TTL.
"""

import json
import structlog
from fastapi import APIRouter, Depends, Query, Request
from api.middleware.auth import get_current_user, User
from api.middleware.rate_limit import limiter
from services.sql_tool import query_sql

logger = structlog.get_logger()
router = APIRouter()

# Simple in-memory cache fallback (Redis integration below)
_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 300  # 5 minutes

try:
    import redis.asyncio as aioredis
    from config import settings
    _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    _redis_client = None


async def _get_cached(key: str) -> dict | None:
    """Try Redis first, fall back to in-memory cache."""
    if _redis_client:
        try:
            data = await _redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
    # In-memory fallback
    import time
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
    return None


async def _set_cached(key: str, data: dict):
    """Set in both Redis and in-memory cache."""
    if _redis_client:
        try:
            await _redis_client.setex(key, CACHE_TTL, json.dumps(data, default=str))
        except Exception:
            pass
    import time
    _cache[key] = (time.time(), data)


@router.get("/analytics/top-titles")
@limiter.limit("60/minute")
async def top_titles(
    request: Request,
    year: int | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    cache_key = f"analytics:top-titles:{year}:{limit}"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    result = await query_sql("top_titles_by_revenue", {"year": year, "limit": limit})
    await _set_cached(cache_key, result)
    return result


@router.get("/analytics/genre-trends")
@limiter.limit("60/minute")
async def genre_trends(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    cache_key = "analytics:genre-trends"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    result = await query_sql("genre_performance_over_time", {})
    await _set_cached(cache_key, result)
    return result


@router.get("/analytics/city-engagement")
@limiter.limit("60/minute")
async def city_engagement(
    request: Request,
    limit: int = Query(5, ge=1, le=20),
    month: str | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    cache_key = f"analytics:city-engagement:{limit}:{month}"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    result = await query_sql("city_engagement_ranking", {"limit": limit, "month": month})
    await _set_cached(cache_key, result)
    return result


@router.get("/analytics/marketing-roi")
@limiter.limit("60/minute")
async def marketing_roi(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    cache_key = "analytics:marketing-roi"
    cached = await _get_cached(cache_key)
    if cached:
        return cached

    result = await query_sql("marketing_roi_per_title", {"limit": 10})
    await _set_cached(cache_key, result)
    return result
