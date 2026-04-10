import base64
import json
import mimetypes
from datetime import datetime
from types import SimpleNamespace
from typing import Any, Callable, Iterable

from app.config import ConfigClass


def build_page_payload(items: list[dict[str, Any]], count: int) -> dict[str, Any]:
    """
    统一返回前端所需的分页结构。
    """

    return {"list": items, "count": count}


def dump_models(items: Iterable[Any]) -> list[dict[str, Any]]:
    result = []
    for item in items:
        if hasattr(item, "model_dump"):
            result.append(item.model_dump(mode="json"))
        else:
            result.append(item)
    return result


async def paginate_queryset(queryset, page: int, limit: int):
    total = await queryset.count()
    data = await queryset.offset((page - 1) * limit).limit(limit)
    return total, data


def resolve_order_field(sort: str, order: str, mapping: dict[str, str], default: str) -> str:
    """
    把前端 sort/order 转成 Tortoise 的 order_by 参数。
    """

    db_field = mapping.get(sort, default.lstrip("-")) if sort else default.lstrip("-")
    if not db_field:
        return default
    return f"-{db_field}" if order == "desc" else db_field


def format_datetime(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def json_dumps(value: Any) -> str:
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def build_file_url(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    base_host = ConfigClass.base_host.rstrip("/")
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{base_host}{normalized}"


def is_image_file(path: str | None, content_type: str | None = None) -> bool:
    if content_type and content_type.startswith("image/"):
        return True
    if not path:
        return False
    return path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"))


def decode_base64_payload(payload: str) -> tuple[bytes, str | None]:
    """
    兼容 data URI 和纯 base64 两种格式。
    """

    if not payload:
        raise ValueError("base64 数据不能为空")

    content_type = None
    raw = payload
    if "," in payload and payload.startswith("data:"):
        header, raw = payload.split(",", 1)
        if ";base64" in header:
            content_type = header[5:].replace(";base64", "")
    return base64.b64decode(raw), content_type


def guess_content_type(file_name: str | None, content_type: str | None = None) -> str | None:
    if content_type:
        return content_type
    if not file_name:
        return None
    guessed, _ = mimetypes.guess_type(file_name)
    return guessed


def get_request_ip(request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


def parse_user_agent(user_agent: str | None) -> dict[str, str]:
    """
    轻量解析 User-Agent。

    这里不引入额外三方库，保持依赖简单；识别结果只用于日志展示，不追求极致准确。
    """

    ua = (user_agent or "").lower()

    if "windows" in ua:
        os_name = "Windows"
    elif "mac os" in ua or "macintosh" in ua:
        os_name = "macOS"
    elif "iphone" in ua or "ipad" in ua or "ios" in ua:
        os_name = "iOS"
    elif "android" in ua:
        os_name = "Android"
    elif "linux" in ua:
        os_name = "Linux"
    else:
        os_name = "Unknown"

    if "edg/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "safari/" in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome/" not in ua:
        browser = "Safari"
    else:
        browser = "Unknown"

    if "mobile" in ua or "iphone" in ua or "android" in ua:
        device = "Mobile"
    elif "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    elif ua:
        device = "Desktop"
    else:
        device = "Unknown"

    return {"os": os_name, "browser": browser, "device": device}


def make_log_user_context(user_id: int, username: str, nickname: str):
    """
    兼容项目现有请求日志中间件使用的 request.state.cur_user 结构。
    """

    return SimpleNamespace(id=user_id, username=username, name=nickname)

