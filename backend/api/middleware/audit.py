"""
Structured Audit Logging — structlog JSON logger.
Logs every request and tool call. Never logs raw tool output (may contain PII).
"""

import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request with user, endpoint, method, status, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()

        # Extract user from JWT if present (best-effort)
        user_id = "anonymous"
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from api.middleware.auth import verify_token
                user = verify_token(auth_header.split(" ")[1])
                user_id = user.username
            except Exception:
                pass

        response = await call_next(request)

        duration_ms = round((time.monotonic() - start) * 1000)
        logger.info(
            "request",
            user_id=user_id,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response
