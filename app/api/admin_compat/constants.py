"""
admin 前端兼容层使用的常量定义。
"""

from .menu_seed import SEED_MENUS

TOKEN_EXPIRE_SECONDS = 60 * 60 * 12
CAPTCHA_EXPIRE_SECONDS = 120
LOGIN_FAIL_EXPIRE_SECONDS = 24 * 60 * 60

LOGIN_TOKEN_PREFIX = "admin-compat:login-token:"
LOGIN_FAIL_PREFIX = "admin-compat:login-fail:"
LOGIN_LOCK_PREFIX = "admin-compat:login-lock:"

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"
DEFAULT_ADMIN_NICKNAME = "超级管理员"

# 前端上传组件默认限制 100MB，这里和前端保持一致。
MAX_UPLOAD_MB = 100

# 仅做基础限制，避免上传明显不合法的文件类型。
UPLOAD_SUFFIXES = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
    ".zip",
    ".rar",
    ".7z",
]

SEED_ORGANIZATIONS = [
    {
        "organization_name": "平台总部",
        "organization_full_name": "平台总部",
        "organization_code": "HQ",
        "organization_type": "headquarters",
        "sort_number": 10,
        "comments": "系统初始化机构",
    }
]

SEED_DICTIONARIES = [
    {
        "dict_code": "sex",
        "dict_name": "性别",
        "sort_number": 10,
        "comments": "用户性别字典",
        "items": [
            {"dict_data_code": "1", "dict_data_name": "男", "sort_number": 10},
            {"dict_data_code": "2", "dict_data_name": "女", "sort_number": 20},
        ],
    },
    {
        "dict_code": "organization_type",
        "dict_name": "机构类型",
        "sort_number": 20,
        "comments": "组织机构分类",
        "items": [
            {
                "dict_data_code": "headquarters",
                "dict_data_name": "总部",
                "sort_number": 10,
            },
            {"dict_data_code": "branch", "dict_data_name": "分部", "sort_number": 20},
            {"dict_data_code": "team", "dict_data_name": "团队", "sort_number": 30},
        ],
    },
]

SEED_MESSAGES = [
    {
        "message_type": "notice",
        "title": "欢迎使用后台管理系统",
        "content": "系统已完成初始化，你现在可以开始联调前后端功能。",
        "status": 0,
        "icon": "report",
        "color": "#409eff",
    },
    {
        "message_type": "letter",
        "title": "产品同学",
        "content": "管理台基础能力已经准备好，辛苦开始验收。",
        "status": 0,
        "avatar": "https://cdn.eleadmin.com/20200610/avatar.jpg",
    },
    {
        "message_type": "todo",
        "title": "检查用户与角色权限",
        "content": "建议先确认用户、角色、菜单三块联调结果。",
        "status": 0,
    },
]
