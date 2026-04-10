FROM python:3.12-slim-bookworm

COPY ./deploy/sources.list /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libgl1 \
    # 验证码字体依赖：避免容器中字体缺失回退为默认小字体
    fonts-dejavu-core \
    fonts-liberation2 \
    fontconfig \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app /log

ARG APP_DIR=/app/fishery-api
COPY . ${APP_DIR}
WORKDIR ${APP_DIR}

ENV PYTHONPATH=${APP_DIR}

RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ \
 && pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

EXPOSE 8000
