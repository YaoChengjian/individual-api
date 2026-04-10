#!/bin/sh
set -eu

# ---- 1) 加载 .env（更稳妥）-----------------------------------------------
# 说明：用 set -a + source 的方式，支持引号/空格等常见写法
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

# ---- 2) 读取环境变量并做兜底 ---------------------------------------------
LOG_PATH="${LOG_PATH:-/var/log}"
CELERY_ENABLE="${CELERY_ENABLE:-false}"
ENV_MODE="${ENV_MODE:-dev}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-}"

# 确保日志目录存在
mkdir -p "$LOG_PATH"

# ---- 3) 数据库迁移 -------------------------------------------------------
# aerich 不存在可升级项时会输出 "No upgrade items found" —— 正常
aerich upgrade || true

# ---- 4) Celery：worker & beat（修复 pidfile 冲突 + 启动前清理僵尸 pid）---
if [ "$CELERY_ENABLE" = "true" ]; then
  echo "启动 celery worker..."
  nohup celery -A app.core.celery:celery_app worker \
        -c 10 --loglevel=INFO \
        --logfile="$LOG_PATH/celery.log" \
        >/dev/null 2>&1 &

  echo "启动 celery beat..."
  # 使用主机名做区分，避免跨重启 / 多实例的 pidfile 冲突
  HOSTNAME_TAG="${HOSTNAME:-beat}"
  CELERY_PIDFILE="/tmp/celery-beat-${HOSTNAME_TAG}.pid"
  CELERY_SCHEDULE="/tmp/celery-schedule-${HOSTNAME_TAG}.db"

  # 若 pidfile 存在但进程已不在，启动前自动清理
  if [ -f "$CELERY_PIDFILE" ]; then
    OLD_PID="$(cat "$CELERY_PIDFILE" 2>/dev/null || true)"
    if [ -n "${OLD_PID:-}" ] && ! kill -0 "$OLD_PID" 2>/dev/null; then
      echo "检测到陈旧 pidfile，清理：$CELERY_PIDFILE (was $OLD_PID)"
      rm -f "$CELERY_PIDFILE"
    fi
  fi

  nohup celery -A app.core.celery:celery_app beat \
        --loglevel=INFO \
        --pidfile="$CELERY_PIDFILE" \
        --schedule="$CELERY_SCHEDULE" \
        --logfile="$LOG_PATH/beat.log" \
        >/dev/null 2>&1 &
fi

# ---- 5) 计算 Gunicorn worker 数量 ----------------------------------------
if [ "$ENV_MODE" = "dev" ]; then
  GUNICORN_WORKERS="${GUNICORN_WORKERS:-2}"
else
  GUNICORN_WORKERS="${GUNICORN_WORKERS:-4}"
fi

echo "ENV_MODE=$ENV_MODE，Gunicorn workers=$GUNICORN_WORKERS"

# ---- 6) 以前台主进程方式运行 gunicorn（exec 交接为 PID1）-------------------
# 说明：容器的主进程以 gunicorn 运行，便于优雅停机；celery 由后台进程运行。
# 如果你希望三个进程都被同一进程管理，建议改用 supervisord 或拆分为三个服务。
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers "$GUNICORN_WORKERS" \
  --worker-connections 1000 \
  --timeout 120
