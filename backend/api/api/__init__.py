from backend.api.api.admins import router as admin_router
from backend.api.api.agents import router as agent_router
from backend.api.api.auth import router as auth_router
from backend.api.api.clients import router as client_router

__all__ = ["admin_router", "agent_router", "auth_router", "client_router"]
