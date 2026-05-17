from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from app.common.exceptions.handlers import global_exception_handler, request_validation_exception_handler, \
    http_exception_handler
from app.common.middleware import register_middlewares
from app.config import ConfigClass
from app.core import logger  # ✅ 初始化日志系统
from app.core.db import init_db, close_db
from app.core.init_data import init_data
from app.core.redis import init_redis, close_redis
from app.core.root_router import router as public_router
from app.routers import api_router  # ✅ 导入全局路由聚合器


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    # 初始化数据
    await init_data()
    logger.init_logger.info(f"FastAPI 启动成功, 运行环境：{ConfigClass.env_mode}")
    yield
    await close_db()
    await close_redis()


# 实例化 FastAPI
app = FastAPI(**ConfigClass.docs_config, lifespan=lifespan)

# 本地开发环境提供静态文件服务
if ConfigClass.static_server_enable:
    # 挂载本地 swagger 静态文件路径
    app.mount("/static", StaticFiles(directory="static"), name="static")
    # H5 通过 Vite 的 /api 代理访问后端静态文件，避免移动端拿到 127.0.0.1 地址。
    app.mount("/api/static", StaticFiles(directory="static"), name="api-static")


# ✅ 注册统一无前缀的 API 路由
app.include_router(public_router)
# ✅ 注册统一前缀的 API 路由
app.include_router(api_router)  # 📌 建议放在中间件和异常后，生命周期之前

# ✅ 日志中间件
register_middlewares(app)

# ✅ 统一异常处理
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# ✅ 全局异常处理兜底
app.add_exception_handler(Exception, global_exception_handler)
