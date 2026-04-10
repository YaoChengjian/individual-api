from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ConfigClass

from .request_mdw import RequestMiddleware


def register_middlewares(app: FastAPI):
    app.add_middleware(RequestMiddleware)

    # 管理台开发环境直接放开跨域，避免本地不同端口联调时被浏览器拦截。
    if ConfigClass.env_mode == "dev":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["Authorization"],
        )
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[ConfigClass.base_host.rstrip("/")],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Authorization"],
    )
