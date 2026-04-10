from datetime import datetime

from celery import shared_task

from app.core.celery import celery_app


# ===  定时任务  ===
@shared_task
def say_hello():
    print(f"[say_hello] {datetime.now()} - 👋 Hello from Celery task!")


# === 异步任务 ===
@celery_app.task
def async_say_hello():
    """

    # delay: 适合快速发
    # add.delay(2, 3)

    # apply_async: 可以加上更多参数控制
    # add.apply_async((2, 3), countdown=10)   # 10秒后执行
    # add.apply_async((2, 3), expires=30)     # 30秒后过期不执行
    # add.apply_async((2, 3), priority=5)     # 设置优先级

    """
    print(f"[async_say_hello] {datetime.now()} - 👋 Hello from Celery async task!")
