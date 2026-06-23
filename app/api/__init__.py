from fastapi import APIRouter

from app.api import admin, agent, client


api_router = APIRouter()
api_router.include_router(client.router)
api_router.include_router(agent.router)
api_router.include_router(admin.router)
