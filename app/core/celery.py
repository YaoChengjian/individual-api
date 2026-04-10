from celery import Celery

from app.config import ConfigClass
from app.schedule import beat_schedule

redis_url = (
    f'redis://:{ConfigClass.redis.password}@{ConfigClass.redis.host}:{ConfigClass.redis.port}'
    if ConfigClass.redis.password
    else f'redis://{ConfigClass.redis.host}:{ConfigClass.redis.port}')

celery_app = Celery(
    "fastapi_app",
    broker=f"{redis_url}/1",
    backend=f"{redis_url}/2"
)

celery_app.conf.update(
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule=beat_schedule,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)

# ✅ 自动扫描任务模块: 注意 tasks中的__init__.py 中添加对应模块
celery_app.autodiscover_tasks(packages=["app.tasks"], force=True)

# 启动命令：celery -A app.core.celery:celery_app worker --loglevel=info
# window 中本地开发启动： celery -A app.core.celery:celery_app worker --loglevel=info --pool=solo

# 定时任务启动命令：celery -A app.core.celery:celery_app beat --loglevel=info
