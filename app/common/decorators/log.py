from functools import wraps


def log_api(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    wrapper._log_api_enabled = True
    return wrapper
