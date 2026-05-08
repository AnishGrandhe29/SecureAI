"""
Chat endpoint — POST /api/chat
Authenticated, rate-limited, dispatches to the AI orchestrator.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from api.middleware.auth import get_current_user, User
from api.middleware.rate_limit import limiter
from services.orchestrator import run_conversation

logger = structlog.get_logger()
router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class Filters(BaseModel):
    year: int | None = None
    genre: str | None = None
    city: str | None = None
    month: str | None = None


class ChatRequest(BaseModel):
    messages: list[Message]
    filters: Filters = Field(default_factory=Filters)


class ToolCall(BaseModel):
    tool: str
    input: dict
    row_count: int = 0
    source: str | None = None


class ChartSpecResponse(BaseModel):
    chart_type: str
    data: list[dict]
    x_key: str
    y_key: str
    title: str
    color: str = "#6366f1"


class ChatResponse(BaseModel):
    answer: str
    tool_trace: list[dict]
    chart_spec: dict | None = None
    sources: list[str]


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Multi-turn chat endpoint with AI orchestration."""
    try:
        # Convert messages to plain dicts for the orchestrator
        messages = [m.model_dump() for m in body.messages]
        filters = body.filters.model_dump(exclude_none=True)

        result = await run_conversation(
            messages=messages,
            filters=filters,
            user_role=current_user.role,
        )
        return ChatResponse(
            answer=result.answer,
            tool_trace=result.tool_trace,
            chart_spec=result.chart_spec,
            sources=result.sources,
        )
    except Exception as e:
        logger.error("chat_error", error=str(e), user_id=current_user.username)
        raise HTTPException(status_code=500, detail="Internal error processing chat request")
