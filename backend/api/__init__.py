from fastapi import APIRouter

from backend.api.api import admin_router, agent_router, auth_router, client_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(client_router)
api_router.include_router(agent_router)
api_router.include_router(admin_router)
