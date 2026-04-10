import logging

from app.api.admin_compat.seed import ensure_seed_data

logger = logging.getLogger(__name__)

async def init_data():
    """
    兼容层后端启动时补齐当前管理台所需的基础数据和导航数据。
    """

    try:
        await ensure_seed_data()
    except Exception as exc:
        logger.exception("兼容层初始化失败：%s", exc)
        raise
