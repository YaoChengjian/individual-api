from .base import BaseConfig


class DevConfig(BaseConfig):
    name: str = "dev"
    debug: bool = True
    enable_file_log: bool = True

    # 文档页面配置
    docs_config: dict = {
        # 项目信息
        "title": "YanMeng Docs 管理后台 API",
        "summary": "admin 前端联调接口文档",
        "description": (
            "面向 `admin` 前端整理的后台接口文档，覆盖登录认证、菜单权限、"
            "系统管理、文件上传、消息中心与个人中心等能力。"
        ),
        "version": "1.1.0",
        "openapi_tags": [
            {
                "name": "管理台兼容层-认证",
                "description": "登录、退出、验证码、当前用户信息与密码资料维护。",
            },
            {
                "name": "管理台兼容层-系统管理",
                "description": "用户、角色、菜单、机构、字典、日志与用户文件管理。",
            },
            {
                "name": "管理台兼容层-文件",
                "description": "公共文件上传、上传记录查询与删除。",
            },
            {
                "name": "管理台兼容层-消息",
                "description": "消息中心未读消息、消息列表、状态更新与删除。",
            },
        ],

        # 文档路径禁用，使得使用本地的swagger文件
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": "/openapi.json",

        # Swagger UI 自定义参数
        "swagger_ui_parameters": {
            "defaultModelsExpandDepth": -1,  # 默认收起 Models 面板
            "displayRequestDuration": True,  # 显示每个请求的耗时
            # "docExpansion": "none"  # 默认收起 tag 分组
        }
    }
