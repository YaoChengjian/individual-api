# 🚀 FastAPI 高性能服务框架部署模板

本项目基于 FastAPI + Tortoise ORM + Aerich + Docker 构建，适用于中大型项目的现代服务后端架构，使用 **Gunicorn + Uvicorn
workers** 高性能部署，并支持 **Nginx 反向代理、静态资源挂载、Docker Compose 自动更新**。

---

## 🧱 技术栈说明

| 技术组件            | 用途                       |
| ------------------- | -------------------------- |
| FastAPI             | 异步 Web 框架              |
| Tortoise ORM        | 异步 ORM 框架              |
| Aerich              | 数据库迁移工具             |
| Gunicorn            | Python 主进程管理器        |
| Uvicorn Worker      | 高性能 ASGI 工作进程       |
| MySQL               | 关系型数据库               |
| Nginx               | 反向代理 + 静态资源服务器  |
| Docker Compose      | 多容器服务编排             |
| Pydantic Settings   | 分层配置和环境变量管理     |
| Uvicorn + httptools | 极致高性能的 HTTP 服务底层 |

## 📁 项目结构

```plaintext
demo-api/
├── app/                        # 应用主目录
│   ├── api/                    # API 模块
│   ├── common/                 # 公共组件
│   │   ├── exceptions/         # 异常处理
│   │   ├── middleware/         # 中间件
│   │   ├── schema.py           # 公共数据模型
│   │   └── utils/              # 工具函数
│   ├── config/                 # 配置模块
│   │   ├── base.py             # 基础配置
│   │   ├── dev.py              # 开发环境配置
│   │   └── prod.py             # 生产环境配置
│   ├── core/                   # 核心组件
│   │   ├── celery.py           # Celery 配置
│   │   ├── db.py               # 数据库连接
│   │   ├── db_models.py        # 基础数据模型
│   │   ├── logger.py           # 日志配置
│   │   ├── openapi.py          # OpenAPI 配置
│   │   └── redis.py            # Redis 连接
│   ├── main.py                 # 应用入口
│   ├── routers.py              # 路由注册
│   ├── schedule.py             # 定时任务配置
│   └── tasks/                  # Celery 任务
├── deploy/                     # 部署相关配置
│   └── nginx/                  # Nginx 配置
├── migrations/                 # 数据库迁移文件
├── static/                     # 静态文件目录
├── .env.example                # 环境变量示例
├── .env.docker.example         # Docker 环境变量示例
├── dc_script.sh                # Docker 启动后端服务的脚本
├── Dockerfile                  # Docker 构建文件
├── docker-compose.yaml         # Docker Compose 配置
├── pyproject.toml              # 项目配置
├── requirements.txt            # 依赖列表
└── run.py                      # 启动脚本

```
## 🎯 项目特点

- 模块化设计 ：清晰的目录结构，便于扩展和维护
- 中间件支持 ：请求日志记录，便于调试和监控
- 标准化响应 ：统一的 API 响应格式
- 逻辑删除 ：支持数据的逻辑删除，提高数据安全性
- 异步支持 ：基于 FastAPI 和 Tortoise ORM 的全异步架构
- 容器化部署 ：完整的 Docker 和 Docker Compose 支持

## 📝 开发规范
- 使用 Tortoise ORM 进行数据库操作
- 使用 Pydantic 进行数据验证和序列化
- 遵循 RESTful API 设计原则
- 使用统一的响应格式

## 🚀 快速启动

### 🧪 本地开发

#### 1. 安装依赖：

```bash
pip install -r requirements.txt
 ```

#### 2. 配置环境变量
编辑 `.env` 文件，设置必要的环境变量。

#### 3. 运行服务：

```bash
python run.py
```
或

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

#### 4. 启动 Celery 任务 （可选）：

```bash
# 启动 Worker
celery -A app.core.celery:celery_app worker --loglevel=info

# Windows 本地开发启动
celery -A app.core.celery:celery_app worker --loglevel=info --pool=solo

# 启动定时任务
celery -A app.core.celery:celery_app beat --loglevel=info
```

### 🐳 Docker 部署

#### 1. 配置环境变量

```bash
cp .env.docker.example .env
```

#### 2. 启动服务

```bash
docker compose up -d
```
或
```bash
docker-compose up -d
```

## 📄 API 文档入口

- Swagger 文档：http://localhost/docs
- Redoc 文档：http://localhost/redoc
- 静态资源：http://localhost/static/

## 🔄 数据库迁移

项目使用 Aerich 进行数据库迁移管理：

### 1. 初始化迁移：

```bash
aerich init-db
 ```

### 2. 创建新的迁移：

```bash
aerich migrate
 ```

### 3. 更新数据库：

```bash
aerich upgrade
```

## ⚠️ 注意事项

1. 确保在开发环境中正确配置 .env 文件
2. 生产环境部署时建议使用 Docker Compose
3. 所有敏感信息应通过环境变量配置
4. 建议定期备份数据库

