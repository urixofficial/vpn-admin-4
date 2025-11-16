# src/telegram/handlers/__init__.py

from .user_panel import router as user_router
from .admin_panel import router as admin_router

__all__ = ["user_router", "admin_router"]