"""
SQL Tool — Read-only parameterised SQL templates.
The LLM never executes raw SQL. It selects from a fixed catalogue of named
query templates and provides only parameter values. This makes SQL injection
structurally impossible.
"""

from pydantic import BaseModel
from sqlalchemy import text
from db.database import AsyncSessionLocal


class SQLResult(BaseModel):
    rows: list[dict]
    query_name: str
    row_count: int
    source: str = "sql_database"


# ─── Named Query Template Catalogue ─────────────────────────────────

QUERY_TEMPLATES = {
    "top_titles_by_revenue": (
        "SELECT m.title, m.genre, m.release_year, m.revenue_usd "
        "FROM movies m "
        "WHERE (:year IS NULL OR m.release_year = :year) "
        "ORDER BY m.revenue_usd DESC "
        "LIMIT :limit"
    ),
    "top_titles_by_views": (
        "SELECT m.title, m.genre, COUNT(wa.activity_id) as total_views "
        "FROM movies m "
        "JOIN watch_activity wa ON m.movie_id = wa.movie_id "
        "WHERE (:year IS NULL OR m.release_year = :year) "
        "GROUP BY m.title, m.genre "
        "ORDER BY total_views DESC "
        "LIMIT :limit"
    ),
    "genre_performance_over_time": (
        "SELECT m.genre, m.release_year, "
        "COUNT(wa.activity_id) as total_views, "
        "ROUND(AVG(wa.completion_pct), 1) as avg_completion "
        "FROM movies m "
        "JOIN watch_activity wa ON m.movie_id = wa.movie_id "
        "GROUP BY m.genre, m.release_year "
        "ORDER BY m.genre, m.release_year"
    ),
    "city_engagement_ranking": (
        "SELECT rp.city, "
        "ROUND(AVG(rp.engagement_score), 2) as avg_engagement, "
        "SUM(rp.views) as total_views, "
        "SUM(rp.revenue_usd) as total_revenue "
        "FROM regional_performance rp "
        "WHERE (:month IS NULL OR rp.month = :month) "
        "GROUP BY rp.city "
        "ORDER BY avg_engagement DESC "
        "LIMIT :limit"
    ),
    "compare_two_titles": (
        "SELECT m.title, m.genre, m.rating, m.revenue_usd, m.budget_usd, "
        "COUNT(wa.activity_id) as total_views, "
        "ROUND(AVG(wa.completion_pct), 1) as avg_completion "
        "FROM movies m "
        "LEFT JOIN watch_activity wa ON m.movie_id = wa.movie_id "
        "WHERE m.title IN (:title1, :title2) "
        "GROUP BY m.title, m.genre, m.rating, m.revenue_usd, m.budget_usd"
    ),
    "weak_genre_analysis": (
        "SELECT m.genre, "
        "COUNT(DISTINCT m.movie_id) as title_count, "
        "ROUND(AVG(m.rating), 2) as avg_rating, "
        "SUM(m.revenue_usd) as total_revenue, "
        "ROUND(AVG(wa.completion_pct), 1) as avg_completion "
        "FROM movies m "
        "JOIN watch_activity wa ON m.movie_id = wa.movie_id "
        "GROUP BY m.genre "
        "ORDER BY avg_completion ASC"
    ),
    "marketing_roi_per_title": (
        "SELECT m.title, "
        "SUM(ms.spend_usd) as total_spend, "
        "SUM(ms.conversions) as total_conversions, "
        "ROUND(SUM(m.revenue_usd) / NULLIF(SUM(ms.spend_usd), 0), 2) as roi "
        "FROM movies m "
        "JOIN marketing_spend ms ON m.movie_id = ms.movie_id "
        "GROUP BY m.title "
        "ORDER BY roi DESC "
        "LIMIT :limit"
    ),
    "audience_segments_by_genre": (
        "SELECT m.genre, v.age_group, v.subscription_tier, "
        "COUNT(wa.activity_id) as watch_count "
        "FROM movies m "
        "JOIN watch_activity wa ON m.movie_id = wa.movie_id "
        "JOIN viewers v ON wa.viewer_id = v.viewer_id "
        "WHERE (:genre IS NULL OR m.genre = :genre) "
        "GROUP BY m.genre, v.age_group, v.subscription_tier "
        "ORDER BY watch_count DESC "
        "LIMIT :limit"
    ),
    "trending_titles_recent": (
        "SELECT m.title, m.genre, "
        "COUNT(wa.activity_id) as recent_views, "
        "ROUND(AVG(r.rating), 1) as avg_review_rating "
        "FROM movies m "
        "JOIN watch_activity wa ON m.movie_id = wa.movie_id "
        "LEFT JOIN reviews r ON m.movie_id = r.movie_id "
        "GROUP BY m.title, m.genre "
        "ORDER BY recent_views DESC "
        "LIMIT :limit"
    ),
    "review_sentiment_by_title": (
        "SELECT m.title, r.sentiment, COUNT(*) as count "
        "FROM movies m "
        "JOIN reviews r ON m.movie_id = r.movie_id "
        "WHERE (:title IS NULL OR m.title = :title) "
        "GROUP BY m.title, r.sentiment "
        "ORDER BY m.title, count DESC"
    ),
    "device_usage_stats": (
        "SELECT wa.device, "
        "COUNT(*) as session_count, "
        "ROUND(AVG(wa.watch_duration_min), 1) as avg_duration, "
        "ROUND(AVG(wa.completion_pct), 1) as avg_completion "
        "FROM watch_activity wa "
        "GROUP BY wa.device "
        "ORDER BY session_count DESC"
    ),
    "subscription_tier_analysis": (
        "SELECT v.subscription_tier, "
        "COUNT(DISTINCT v.viewer_id) as viewer_count, "
        "COUNT(wa.activity_id) as total_watches, "
        "ROUND(AVG(wa.completion_pct), 1) as avg_completion "
        "FROM viewers v "
        "JOIN watch_activity wa ON v.viewer_id = wa.viewer_id "
        "GROUP BY v.subscription_tier "
        "ORDER BY total_watches DESC"
    ),
    "monthly_revenue_trend": (
        "SELECT rp.month, "
        "SUM(rp.revenue_usd) as total_revenue, "
        "SUM(rp.views) as total_views "
        "FROM regional_performance rp "
        "GROUP BY rp.month "
        "ORDER BY rp.month"
    ),
    "campaign_channel_performance": (
        "SELECT ms.channel, "
        "SUM(ms.spend_usd) as total_spend, "
        "SUM(ms.impressions) as total_impressions, "
        "SUM(ms.clicks) as total_clicks, "
        "SUM(ms.conversions) as total_conversions, "
        "ROUND(SUM(ms.clicks) * 1.0 / NULLIF(SUM(ms.impressions), 0) * 100, 2) as ctr_pct "
        "FROM marketing_spend ms "
        "GROUP BY ms.channel "
        "ORDER BY total_conversions DESC"
    ),
    "title_details": (
        "SELECT m.* FROM movies m "
        "WHERE m.title = :title "
        "LIMIT 1"
    ),
}

# Default parameter values to avoid missing params
DEFAULT_PARAMS = {
    "year": None,
    "limit": 10,
    "month": None,
    "title": None,
    "title1": None,
    "title2": None,
    "genre": None,
}


async def query_sql(query_name: str, params: dict | None = None) -> dict:
    """
    Execute a named SQL template with the given parameters.
    Returns a dict matching the SQLResult schema.
    """
    if query_name not in QUERY_TEMPLATES:
        return {
            "rows": [],
            "query_name": query_name,
            "row_count": 0,
            "source": "sql_database",
            "error": f"Unknown query template: {query_name}",
        }

    template = QUERY_TEMPLATES[query_name]
    merged_params = {**DEFAULT_PARAMS, **(params or {})}

    async with AsyncSessionLocal() as session:
        result = await session.execute(text(template), merged_params)
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

    return {
        "rows": rows,
        "query_name": query_name,
        "row_count": len(rows),
        "source": "sql_database",
    }
