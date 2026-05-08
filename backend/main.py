"""
FastAPI Application Entry Point.
Assembles routes, middleware, CORS, and startup events.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from api.middleware.rate_limit import limiter
from api.middleware.audit import AuditMiddleware
from api.middleware.auth import authenticate_user, create_access_token, TokenResponse
from api.routes import health, chat, analytics, ingest
from db.database import init_db
from pydantic import BaseModel

# ─── Structured Logging Setup ────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


# ─── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("startup", environment=settings.ENVIRONMENT)
    await init_db()
    yield
    logger.info("shutdown")


# ─── App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Secure AI Insights API",
    description="AI-powered analytics assistant with multi-source reasoning",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit logging
app.add_middleware(AuditMiddleware)

# ─── Routes ──────────────────────────────────────────────────────────

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(ingest.router, prefix="/api", tags=["Ingest"])


# ─── Auth Token Route ────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/auth/token", response_model=TokenResponse, tags=["Auth"])
async def login(body: LoginRequest):
    """Authenticate with demo credentials and receive a JWT token."""
    user = authenticate_user(body.username, body.password)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user.username, user.role)
    return TokenResponse(
        access_token=token,
        role=user.role,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )
