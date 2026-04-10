import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import ConfigClass

log_dir = ConfigClass.log_path
os.makedirs(log_dir, exist_ok=True)

log_format = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)

# === 全局根日志器 ===
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 控制台输出
if ConfigClass.debug:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

# app.log 输出
if ConfigClass.enable_file_log:
    app_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    app_handler.setFormatter(log_format)
    root_logger.addHandler(app_handler)

# === 初始化日志 ===
init_logger = logging.getLogger("init")
init_logger.setLevel(logging.INFO)
init_logger.propagate = False  # 不向上传播到 root
init_handler = logging.StreamHandler()
init_handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
init_logger.addHandler(init_handler)

# === 请求日志器 ===
request_logger = logging.getLogger("request")
request_logger.setLevel(logging.INFO)
if ConfigClass.enable_file_log:
    request_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "request.log"),
        maxBytes=3 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8"
    )
    request_handler.setFormatter(log_format)
    request_logger.addHandler(request_handler)

# === 错误日志器 ===
error_logger = logging.getLogger("error")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False  # 不向上传播到 root 这样不会输出到控制台

if ConfigClass.enable_file_log:
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "error.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8"
    )
    error_handler.setFormatter(log_format)
    error_logger.addHandler(error_handler)

# 导出相关的日志器 (使得使用 import * 时，不会导入无关的变量)
__all__ = ['root_logger', 'init_logger', 'error_logger', 'request_logger']
