"""
Chart Tool — Generates Recharts-compatible JSON specs.
The frontend renders the chart — no server-side image generation.
"""

from typing import Literal
from pydantic import BaseModel


class ChartSpec(BaseModel):
    chart_type: str
    data: list[dict]
    x_key: str
    y_key: str
    title: str
    color: str = "#6366f1"


async def generate_chart(
    chart_type: Literal["bar", "line", "scatter", "pie"],
    data: list[dict],
    x_key: str,
    y_key: str,
    title: str,
) -> dict:
    """
    Generate a Recharts-compatible chart specification from data.
    Returns a JSON-serializable dict that the frontend renders directly.
    """
    spec = ChartSpec(
        chart_type=chart_type,
        data=data,
        x_key=x_key,
        y_key=y_key,
        title=title,
    )
    return spec.model_dump()
