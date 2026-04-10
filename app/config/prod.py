from .base import BaseConfig


class ProdConfig(BaseConfig):
    name: str = "prod"
    debug: bool = False
    enable_file_log: bool = True
    docs_config: dict = {
        # 文档路径控制（生产环境下禁用）
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": None,
    }
