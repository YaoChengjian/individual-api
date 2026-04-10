from fastapi import APIRouter

from app.api.admin_compat.routers.auth import public_router as auth_public_router
from app.api.admin_compat.routers.auth import protected_router as auth_protected_router
from app.api.admin_compat.routers.file import router as file_router
from app.api.admin_compat.routers.message import router as message_router
from app.api.admin_compat.routers.system import router as system_router

router = APIRouter()
router.include_router(auth_public_router)
router.include_router(auth_protected_router)
router.include_router(system_router)
router.include_router(file_router)
router.include_router(message_router)
