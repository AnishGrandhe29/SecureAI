"""
Rate Limiting Middleware — slowapi (30 req/min on chat endpoint).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
