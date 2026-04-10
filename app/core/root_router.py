from fastapi import APIRouter, Request, HTTPException
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)
from starlette.responses import RedirectResponse
from app.config import ConfigClass

router = APIRouter(include_in_schema=False)  # 无前缀


# @router.get("/", include_in_schema=False)
# async def root():
#     FRONTEND_URL = f"{ConfigClass.base_host}/portal"
#     return RedirectResponse(FRONTEND_URL, status_code=308)


# 本地 swagger
@router.get("/docs", include_in_schema=False)
@router.get("/docs/", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):

    # ✅ 判断环境：假设 ConfigClass.env_mode = "prod" 表示生产
    if ConfigClass.env_mode == "prod":
        raise HTTPException(status_code=404, detail="Not Found")

    return get_swagger_ui_html(
        openapi_url=request.app.openapi_url,  # ✅ 从 request.app 取
        title=request.app.title + " - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url="/static/swagger/favicon.png",
    )


@router.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    # ✅ 判断环境：假设 ConfigClass.env_mode = "prod" 表示生产
    if ConfigClass.env_mode == "prod":
        raise HTTPException(status_code=404, detail="Not Found")
    return get_swagger_ui_oauth2_redirect_html()


@router.get("/redoc", include_in_schema=False)
@router.get("/redoc/", include_in_schema=False)
async def redoc_html(request: Request):
    # ✅ 判断环境：假设 ConfigClass.env_mode = "prod" 表示生产
    if ConfigClass.env_mode == "prod":
        raise HTTPException(status_code=404, detail="Not Found")
    return get_redoc_html(
        openapi_url=request.app.openapi_url,
        title=request.app.title + " - ReDoc",
        redoc_js_url="/static/swagger/redoc.standalone.js",
    )
