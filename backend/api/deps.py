"""
FastAPI dependency injection helpers.
"""

from db.database import get_db
from api.middleware.auth import get_current_user, require_admin

__all__ = ["get_db", "get_current_user", "require_admin"]
