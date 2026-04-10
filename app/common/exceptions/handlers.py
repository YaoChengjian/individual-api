# app/core/exception_handlers.py
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.common.utils.response import JsonResponse, fail
from app.core.logger import error_logger as logger


def _format_loc(loc):
    return ".".join(str(x) for x in loc)


def _normalize_validation_errors(exc: RequestValidationError):
    normalized = []
    for err in exc.errors():
        loc = _format_loc(err.get("loc", [])).replace('body.', '')
        e_type = err.get("type", "")
        msg = err.get("msg", "")

        if e_type in {"missing", "value_error.missing"}:
            friendly = f"字段 {loc} 为必填项，缺失或未提供。"
            code = "required"

        elif e_type in {"none_is_not_allowed"}:
            friendly = f"字段 {loc} 不能为空（不能为 null）。"
            code = "not_null"

        elif e_type.endswith("_type"):
            expected = e_type.replace("_type", "")
            friendly = f"字段 {loc} 类型不正确，应为 {expected}。"
            code = "type_error"

        else:
            friendly = f"字段 {loc} 校验失败：{msg}"
            code = "validation_error"

        normalized.append({
            "field": loc,
            "code": code,
            "message": friendly,
        })
    return normalized


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"[VALIDATION] {request.method} {request.url}\n{exc}", exc_info=False)

    errs = _normalize_validation_errors(exc)

    result = fail(
        msg="参数校验失败，请检查输入。",
        data={"errors": errs}
    )
    return JsonResponse(result, status_code=HTTP_400_BAD_REQUEST)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"[HTTP] {request.method} {request.url} -> {exc.status_code} {exc.detail}")
    result = fail(msg=exc.detail or "请求失败。")
    return JsonResponse(result, status_code=exc.status_code)


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[EXCEPTION] {request.url} \n {exc.__class__.__name__}: {exc}", exc_info=True)
    result = fail(msg=str(exc), data={"detail": str(exc)})
    return JsonResponse(result, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
