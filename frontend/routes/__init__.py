from fastapi import APIRouter

from frontend.routes.admin import router as admin_router
from frontend.routes.agent import router as agent_router
from frontend.routes.auth import router as auth_router
from frontend.routes.public import router as public_router

router = APIRouter(tags=["frontend"])
router.include_router(public_router)
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(agent_router)

__all__ = ["router"]
