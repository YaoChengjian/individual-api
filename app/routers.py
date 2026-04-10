from fastapi import APIRouter

from app.api.admin_compat.routers import router as admin_compat_router

# 全局路由 前缀
api_router = APIRouter(prefix="/api")

# 当前项目后端只保留管理台兼容层接口。
api_router.include_router(admin_compat_router)
