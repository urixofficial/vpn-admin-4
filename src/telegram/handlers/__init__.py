# src/telegram/handlers/__init__.py

from .user import router as user_router
from .admin import router as admin_router
from .user_control import router as user_control_router

__all__ = ["user_router", "admin_router", "user_control_router"]