from pathlib import Path
from typing import ClassVar
from typing import Literal
from urllib.parse import quote
from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings


class DBConfig(BaseModel):
    engine: Literal["mysql", "postgres", "sqlite"]
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def url(self) -> str:

        # 对密码进行 URL 编码（防止特殊字符破坏连接字符串）
        safe_password = quote(self.password)

        if self.engine == "mysql":
            return f"mysql://{self.user}:{safe_password}@{self.host}:{self.port}/{self.name}"
        elif self.engine == "postgres":
            return f"postgres://{self.user}:{safe_password}@{self.host}:{self.port}/{self.name}"
        elif self.engine == "sqlite":
            return f"sqlite://{self.name}"
        else:
            raise ValueError(f"Unsupported DB engine: {self.engine}")


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int = 0
    password: str = ""


class BaseConfig(BaseSettings):
    secret_key: str
    system_clear_redis_token: str = ""

    db: DBConfig
    redis: RedisConfig

    log_path: str

    # 静态文件路径前缀
    static_root_path: str
    # 静态文件保存目录
    static_dir: str

    env_mode: str
    base_host: str

    # 是否开启静态文件服务
    static_server_enable: bool = False

    @computed_field  # ✅ 会参与序列化、导出等
    @property
    def static_path(self) -> str:
        """自动拼接静态文件完整路径"""
        path_str = f"{self.static_root_path}{self.static_dir}"
        if '//' in path_str:
            path_str = path_str.replace('//', '/')
        return path_str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",  # ✅ 告诉 Pydantic 如何解析嵌套字段
        "extra": "allow",  # ✅ 添加这个项，允许.env额外无关紧要的字段
    }

    # 获取当前 config/base.py 文件的路径
    CURRENT_FILE: ClassVar[Path] = Path(__file__).resolve()

    # 项目根目录，假设 config 在 app 目录下
    BASE_DIR: str = str(CURRENT_FILE.parent.parent.parent)
