# logging 配一次
import logging

from tortoise import Tortoise, connections

from app.config import ConfigClass

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
for name in ("tortoise", "tortoise.db_client", "tortoise.backends", "tortoise.query"):
    logging.getLogger(name).setLevel(logging.DEBUG)


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    # 本地开发阶段自动补齐缺失表结构，降低首次启动门槛。
    if ConfigClass.env_mode == 'dev':
        await Tortoise.generate_schemas(safe=True)
    # 仅在调试时打开
    connections.get("default").log_queries = ConfigClass.env_mode == 'dev'


async def close_db():
    await Tortoise.close_connections()


# ✅ 供 Aerich 使用
TORTOISE_ORM = {
    "connections": {
        "default": ConfigClass.db.url  # 使用你的动态配置
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",  # ✅ Aerich 自带表结构必须添加
                "app.api.admin_compat.models",
            ],
            "default_connection": "default"
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}

# 是否启用逻辑删除
LOGIC_DELETE_ENABLED = True
