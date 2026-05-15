from fastapi import APIRouter

from app.api.admin_compat.routers.audit import router as audit_router
from app.api.admin_compat.routers.auth import public_router as auth_public_router
from app.api.admin_compat.routers.auth import protected_router as auth_protected_router
from app.api.admin_compat.routers.closed_loop import router as closed_loop_router
from app.api.admin_compat.routers.file import router as file_router
from app.api.admin_compat.routers.message import router as message_router
from app.api.admin_compat.routers.mobile import app_router, h5_router
from app.api.admin_compat.routers.patrol_mvp import router as patrol_mvp_router
from app.api.admin_compat.routers.system import router as system_router
from app.api.admin_compat.routers.task import router as task_router

router = APIRouter()
admin_router = APIRouter(prefix="/admin")
router.include_router(auth_public_router)
router.include_router(auth_protected_router)
router.include_router(system_router)
router.include_router(task_router)
router.include_router(closed_loop_router)
router.include_router(patrol_mvp_router)
router.include_router(audit_router)
router.include_router(file_router)
router.include_router(message_router)
router.include_router(h5_router)
router.include_router(app_router)

admin_router.include_router(auth_public_router)
admin_router.include_router(auth_protected_router)
admin_router.include_router(system_router)
admin_router.include_router(task_router)
admin_router.include_router(closed_loop_router)
admin_router.include_router(patrol_mvp_router)
admin_router.include_router(audit_router)
admin_router.include_router(file_router)
admin_router.include_router(message_router)
router.include_router(admin_router)
