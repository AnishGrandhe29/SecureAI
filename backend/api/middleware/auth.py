"""
JWT Authentication & RBAC Middleware.
Provides get_current_user dependency and token generation.
Demo users: analyst/analyst123, admin/admin123.
"""

from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from config import settings

security = HTTPBearer()

# ─── Demo Users (hardcoded for demo — production uses a proper user store) ───

DEMO_USERS = {
    "analyst": {"password": "analyst123", "role": "analyst"},
    "admin": {"password": "admin123", "role": "admin"},
}


class User(BaseModel):
    username: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in: int


def create_access_token(username: str, role: str) -> str:
    """Create a JWT token with username, role, and expiry."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> User:
    """Decode and validate a JWT token. Returns a User or raises HTTPException."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return User(username=username, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """FastAPI dependency — extracts and validates JWT from Authorization header."""
    return verify_token(credentials.credentials)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency — ensures the user has the admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def authenticate_user(username: str, password: str) -> User | None:
    """Validate demo credentials. Returns User or None."""
    user_data = DEMO_USERS.get(username)
    if user_data and user_data["password"] == password:
        return User(username=username, role=user_data["role"])
    return None
