"""
CSV Tool — Pandas aggregation engine over static reference data.
All 6 CSVs are loaded into in-memory DataFrames at import time.
Supports metric + group_by + optional filters for trend analysis.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "csv"

# Supported metrics and dimensions
METRICS = ["total_views", "avg_rating", "revenue_usd", "engagement_score", "marketing_roi"]
DIMENSIONS = ["genre", "city", "month", "device", "subscription_tier"]

# Lazy-loaded DataFrames
_dfs: dict[str, pd.DataFrame] | None = None


def _load_dataframes() -> dict[str, pd.DataFrame]:
    global _dfs
    if _dfs is None:
        _dfs = {}
        for csv_file in DATA_DIR.glob("*.csv"):
            name = csv_file.stem
            df = pd.read_csv(csv_file)
            df.columns = [c.strip() for c in df.columns]
            _dfs[name] = df
    return _dfs


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply optional filters to a DataFrame."""
    if not filters:
        return df
    for key, value in filters.items():
        if value is not None and key in df.columns:
            df = df[df[key] == value]
        elif key == "year" and "release_year" in df.columns and value is not None:
            df = df[df["release_year"] == value]
    return df


async def analyze_csv(
    metric: str,
    group_by: str,
    filters: dict | None = None,
) -> dict:
    """
    Run aggregation queries over CSV business data.
    Returns grouped/aggregated data based on the requested metric and dimension.
    """
    dfs = _load_dataframes()
    filters = filters or {}

    result_data = []

    if metric == "total_views":
        if "watch_activity" in dfs and "movies" in dfs:
            merged = dfs["watch_activity"].merge(dfs["movies"], on="movie_id", how="left")
            if group_by == "device":
                merged = _apply_filters(merged, filters)
                result_data = merged.groupby("device").size().reset_index(name="total_views")
            elif group_by == "genre":
                merged = _apply_filters(merged, filters)
                result_data = merged.groupby("genre").size().reset_index(name="total_views")
            elif group_by == "city" and "viewers" in dfs:
                merged = merged.merge(dfs["viewers"][["viewer_id", "city"]], on="viewer_id", how="left")
                merged = _apply_filters(merged, filters)
                result_data = merged.groupby("city").size().reset_index(name="total_views")
            elif group_by == "month":
                merged["month"] = pd.to_datetime(merged["watch_date"]).dt.to_period("M").astype(str)
                merged = _apply_filters(merged, filters)
                result_data = merged.groupby("month").size().reset_index(name="total_views")
            elif group_by == "subscription_tier" and "viewers" in dfs:
                merged = merged.merge(dfs["viewers"][["viewer_id", "subscription_tier"]], on="viewer_id", how="left")
                merged = _apply_filters(merged, filters)
                result_data = merged.groupby("subscription_tier").size().reset_index(name="total_views")

    elif metric == "avg_rating":
        if "reviews" in dfs and "movies" in dfs:
            merged = dfs["reviews"].merge(dfs["movies"], on="movie_id", how="left")
            merged = _apply_filters(merged, filters)
            if group_by in merged.columns:
                result_data = merged.groupby(group_by)["rating"].mean().round(2).reset_index()
                result_data.columns = [group_by, "avg_rating"]

    elif metric == "revenue_usd":
        if "regional_performance" in dfs:
            df = dfs["regional_performance"].copy()
            df = _apply_filters(df, filters)
            if group_by in df.columns:
                result_data = df.groupby(group_by)["revenue_usd"].sum().round(2).reset_index()

    elif metric == "engagement_score":
        if "regional_performance" in dfs:
            df = dfs["regional_performance"].copy()
            df = _apply_filters(df, filters)
            if group_by in df.columns:
                result_data = df.groupby(group_by)["engagement_score"].mean().round(2).reset_index()

    elif metric == "marketing_roi":
        if "marketing_spend" in dfs and "movies" in dfs:
            merged = dfs["marketing_spend"].merge(dfs["movies"], on="movie_id", how="left")
            merged = _apply_filters(merged, filters)
            if group_by == "channel":
                gb = merged.groupby("channel").agg(
                    total_spend=("spend_usd", "sum"),
                    total_conversions=("conversions", "sum"),
                ).reset_index()
                gb["marketing_roi"] = (gb["total_conversions"] / gb["total_spend"] * 1000).round(2)
                result_data = gb

    # Convert to list of dicts
    if isinstance(result_data, pd.DataFrame) and not result_data.empty:
        data = result_data.to_dict(orient="records")
    else:
        data = []

    return {
        "data": data,
        "metric": metric,
        "group_by": group_by,
        "source": "csv_files",
    }
