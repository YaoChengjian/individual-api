import json
import logging
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.api.admin_compat.models import AdminCompatOperationRecord

logger = logging.getLogger("request")


class RequestMiddleware(BaseHTTPMiddleware):
    IGNORE_PATHS_FIX = ["/docs", "/openapi.json", "/redoc"]

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):

        if "/" + str(request.url.path).split("/")[1] in self.IGNORE_PATHS_FIX:
            return await call_next(request)

        start_time = datetime.now()

        # 记录请求基本信息
        method, url, req_var, req_name = request.method, request.url, {}, 'Body'
        req_content_type = request.headers.get("content-type", "")

        if method == 'POST':
            # 常规 json 请求
            if req_content_type == "application/json":
                body_bytes = await request.body()
                req_var = body_bytes.decode("utf-8")
            elif req_content_type == "multipart/form-data":
                form = await request.form()
                req_var, req_name = dict(form), 'Form'

        elif method == 'GET':
            req_var, req_name = json.dumps(dict(request.query_params)), 'Query'

        # 调用下一个中间件或处理程序处理请求
        response: Response = await call_next(request)

        # 这里直接拿 route（无需循环）
        route = request.scope.get("route")
        summary = getattr(route, "summary", None)
        endpoint = getattr(route, "endpoint", None) if route else None

        if response.headers.get("content-type", "") == "application/json":
            try:
                content = b""
                async for chunk in response.body_iterator:
                    content += chunk

                async def body_iterator():
                    yield content

                response.body_iterator = body_iterator()

                # 解析返回数据
                response_body = content.decode("utf-8")
            except (ValueError, AttributeError, UnicodeDecodeError):
                response_body = "Invalid JSON or empty content"
        else:
            response_body = "Not a JSON response"

        # 日志输出
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            f"\n[{method}] {url} Time Elapsed: {latency_ms} \n"
            f"[{req_name}]: {req_var} \n"
            f"[Response]: {response_body}"
        )

        # 打标记的接口才需要记录
        if getattr(endpoint, "_log_api_enabled", False):
            req_dict = json.loads(response_body)
            # print(req_dict.get("code", None))
            log_item = {
                "user_id": getattr(getattr(request.state, "cur_user", None), "id", None),
                "user_name": getattr(getattr(request.state, "cur_user", None), "name", None),
                "path": request.url.path,
                "method": method,
                "ip": request.client.host if request.client else None,
                "summary": summary,
                "req_headers": dict(request.headers),
                "req_body": req_var,  # 同上
                "resp_code": req_dict.get("code", None),
                "resp_msg": req_dict.get("message", None),
                "resp_body": response_body,  # 建议采样或截断
                "latency_ms": latency_ms,
            }
            try:
                await AdminCompatOperationRecord.create(**log_item)
            except Exception as exc:
                logger.warning("操作日志写入失败：%s", exc)

        return response
