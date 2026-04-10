from celery.schedules import crontab

beat_schedule = {
    # "say-hello": {
    #     "task": "app.tasks.demo.say_hello",
    #     # "schedule": crontab(hour=1, minute=0),  # 每天凌晨 1 点执行
    #     "schedule": 10.0,
    #     "args": [],
    # },
}
