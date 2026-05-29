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

SEED_ROLES = [
    {
        "role_code": "admin",
        "role_name": "超级管理员",
        "is_system_role": 1,
        "comments": "系统默认超级管理员角色",
    },
    {
        "role_code": "operator",
        "role_name": "业务管理员",
        "is_system_role": 1,
        "comments": "业务模块管理角色",
    },
    {
        "role_code": "viewer",
        "role_name": "只读用户",
        "is_system_role": 1,
        "comments": "基础只读角色",
    },
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
    {
        "dict_code": "patrol_task_type",
        "dict_name": "巡查任务类型",
        "sort_number": 30,
        "comments": "巡查任务分类",
        "items": [
            {
                "dict_data_code": "fire_safety",
                "dict_data_name": "消防安全",
                "color": "#1f6feb",
                "ripple": 0,
                "sort_number": 10,
            },
            {
                "dict_data_code": "environment",
                "dict_data_name": "环境巡查",
                "color": "#20b56b",
                "ripple": 0,
                "sort_number": 20,
            },
            {
                "dict_data_code": "governance",
                "dict_data_name": "综合治理",
                "color": "#f59e0b",
                "ripple": 0,
                "sort_number": 30,
            },
        ],
    },
    {
        "dict_code": "patrol_task_status",
        "dict_name": "巡查任务状态",
        "sort_number": 40,
        "comments": "巡查任务流转状态",
        "items": [
            {
                "dict_data_code": "running",
                "dict_data_name": "执行中",
                "color": "#20b56b",
                "ripple": 1,
                "sort_number": 20,
            },
            {
                "dict_data_code": "waiting",
                "dict_data_name": "待执行",
                "color": "#7c3aed",
                "ripple": 1,
                "sort_number": 10,
            },
            {
                "dict_data_code": "finished",
                "dict_data_name": "已完成",
                "color": "#1f6feb",
                "ripple": 0,
                "sort_number": 30,
            },
            {
                "dict_data_code": "overdue",
                "dict_data_name": "已逾期",
                "color": "#f04438",
                "ripple": 1,
                "sort_number": 40,
            },
        ],
    },
    {
        "dict_code": "patrol_task_priority",
        "dict_name": "巡查任务优先级",
        "sort_number": 50,
        "comments": "巡查任务优先级",
        "items": [
            {
                "dict_data_code": "low",
                "dict_data_name": "低",
                "color": "#22c55e",
                "ripple": 0,
                "sort_number": 10,
            },
            {
                "dict_data_code": "medium",
                "dict_data_name": "中",
                "color": "#f59e0b",
                "ripple": 0,
                "sort_number": 20,
            },
            {
                "dict_data_code": "high",
                "dict_data_name": "高",
                "color": "#f97316",
                "ripple": 1,
                "sort_number": 30,
            },
            {
                "dict_data_code": "urgent",
                "dict_data_name": "紧急",
                "color": "#f04438",
                "ripple": 1,
                "sort_number": 40,
            },
        ],
    },
    {
        "dict_code": "patrol_task_repeat_rule",
        "dict_name": "巡查任务重复规则",
        "sort_number": 60,
        "comments": "巡查任务重复规则",
        "items": [
            {
                "dict_data_code": "none",
                "dict_data_name": "不重复",
                "color": "#1f6feb",
                "ripple": 0,
                "sort_number": 10,
            },
            {
                "dict_data_code": "repeat",
                "dict_data_name": "重复",
                "color": "#20b56b",
                "ripple": 0,
                "sort_number": 20,
            },
        ],
    },
]

SEED_PATROL_AREAS = [
    {
        "area_code": "AREA_BYDDN",
        "area_name": "广州白云国际会议中心",
        "center_lat": 23.188677,
        "center_lng": 113.279451,
        "sort_number": 10,
        "comments": "广州白云国际会议中心演示巡查面",
        "boundary": [
            {"lat": 23.19010, "lng": 113.27862},
            {"lat": 23.19002, "lng": 113.28020},
            {"lat": 23.18942, "lng": 113.28108},
            {"lat": 23.18855, "lng": 113.28092},
            {"lat": 23.18772, "lng": 113.27982},
            {"lat": 23.18784, "lng": 113.27855},
            {"lat": 23.18866, "lng": 113.27810},
        ],
    },
    {
        "area_code": "AREA_FY_COMMUNITY",
        "area_name": "逢源社区",
        "center_lat": 23.12455,
        "center_lng": 113.24562,
        "sort_number": 20,
        "comments": "广州市荔湾区逢源社区演示巡查面",
        "boundary": [
            {"lat": 23.13004, "lng": 113.24002},
            {"lat": 23.13018, "lng": 113.25236},
            {"lat": 23.12524, "lng": 113.25318},
            {"lat": 23.11872, "lng": 113.24922},
            {"lat": 23.11838, "lng": 113.24072},
            {"lat": 23.12442, "lng": 113.23892},
        ],
    },
]

SEED_PATROL_POINTS = [
    {"area_code": "AREA_BYDDN", "point_code": "DEMO-01", "point_name": "巡查点01", "point_type": "key_point", "lat": 23.189511, "lng": 113.280523, "sort_number": 10},
    {"area_code": "AREA_BYDDN", "point_code": "DEMO-02", "point_name": "巡查点02", "point_type": "key_point", "lat": 23.188306, "lng": 113.279493, "sort_number": 20},
    {"area_code": "AREA_BYDDN", "point_code": "DEMO-03", "point_name": "巡查点03", "point_type": "key_point", "lat": 23.188677, "lng": 113.279451, "sort_number": 30},
    {"area_code": "AREA_FY_COMMUNITY", "point_code": "FY-01", "point_name": "逢源社区巡查点01", "point_type": "key_point", "lat": 23.12862, "lng": 113.24462, "sort_number": 40},
    {"area_code": "AREA_FY_COMMUNITY", "point_code": "FY-02", "point_name": "逢源社区巡查点02", "point_type": "key_point", "lat": 23.12392, "lng": 113.24728, "sort_number": 50},
    {"area_code": "AREA_FY_COMMUNITY", "point_code": "FY-03", "point_name": "逢源社区巡查点03", "point_type": "key_point", "lat": 23.12046, "lng": 113.24316, "sort_number": 60},
]

SEED_PATROL_USER_DEVICES = [
    {"username": "admin", "user_name": "张三", "employee_no": "GW2025052001", "device_type": "smart_glasses", "device_name": "智能眼镜", "device_sn": "GY2025050001", "online_status": "online", "bind_status": "bound"},
    {"username": "admin", "user_name": "张三", "employee_no": "GW2025052001", "device_type": "headset", "device_name": "耳机", "device_sn": "EJ2025050001", "online_status": "online", "bind_status": "bound"},
    {"username": "admin", "user_name": "张三", "employee_no": "GW2025052001", "device_type": "badge", "device_name": "工牌", "device_sn": "GP2025050001", "online_status": "online", "bind_status": "bound"},
    {"username": "admin", "user_name": "张三", "employee_no": "GW2025052001", "device_type": "handheld", "device_name": "手持终端", "device_sn": "SC2025050001", "online_status": "online", "bind_status": "bound"},
    {"username": "admin", "user_name": "张三", "employee_no": "GW2025052001", "device_type": "printer", "device_name": "便携打印机", "device_sn": "DY2025050001", "online_status": "online", "bind_status": "bound"},
]

SEED_PATROL_TASKS = [
    {
        "task_code": "RWD20260515141720",
        "task_title": "广州白云国际会议中心演示巡查任务",
        "task_type": "fire_safety",
        "priority": "high",
        "description": "围绕广州白云国际会议中心演示区域开展闭环巡查。",
        "ai_focus": 1,
        "patrol_location": "广州白云国际会议中心",
        "area_codes": ["AREA_BYDDN"],
        "point_codes": ["DEMO-01", "DEMO-02", "DEMO-03"],
        "area_ids": [],
        "point_ids": [],
        "plan_time": "2026-05-20 08:30",
        "start_time": "2026-05-20 08:00",
        "end_time": "2026-05-20 12:00",
        "duration_hours": 4,
        "repeat_rule": "none",
        "task_status": "waiting",
        "progress": 0,
        "exception_count": 1,
    },
]


SEED_INSPECTION_EVENTS = [
    {
        "event_code": "EVT20260520084542",
        "event_title": "幸福里小区3号楼消防通道堵塞",
        "event_type": "fire_lane_blocked",
        "risk_level": "high",
        "source": "AI识别",
        "status": "pending_confirm",
        "task_code": "RWD20260515141720",
        "area_code": "AREA_XFL",
        "point_code": "XFL-3",
        "inspector_name": "张三",
        "confidence": 96.8,
        "description": "智能眼镜识别到楼道转角堆放杂物，消防通道宽度不足。",
        "image_url": "/static/document/patrol/fire-lane-before.png",
        "detected_time": "2026-05-20 08:45:42",
    },
    {
        "event_code": "EVT20260520090218",
        "event_title": "阳光花园社区垃圾满溢",
        "event_type": "garbage_overflow",
        "risk_level": "medium",
        "source": "人工上报",
        "status": "work_order_created",
        "area_code": "AREA_YHG",
        "point_code": "YHG-2",
        "inspector_name": "李雨晴",
        "confidence": 88.5,
        "description": "生活垃圾桶满溢并外散，影响小区公共环境。",
        "image_url": "/static/document/patrol/garbage-overflow.png",
        "detected_time": "2026-05-20 09:02:18",
    },
    {
        "event_code": "EVT20260520101536",
        "event_title": "平安社区东门岗亭设备异常",
        "event_type": "device_exception",
        "risk_level": "low",
        "source": "AI识别",
        "status": "handled",
        "area_code": "AREA_PA",
        "point_code": "PA-DM",
        "inspector_name": "赵敏",
        "confidence": 91.2,
        "description": "门岗摄像头离线，现场已联系物业处理。",
        "image_url": "/static/document/patrol/device-exception.png",
        "detected_time": "2026-05-20 10:15:36",
    },
]

SEED_WORK_ORDERS = [
    {
        "work_order_code": "XFS202605200001",
        "title": "幸福里小区3号楼消防通道严重堵塞",
        "risk_level": "high",
        "source": "AI识别",
        "reporter_name": "张三",
        "area_code": "AREA_XFL",
        "point_name": "幸福里小区3号楼",
        "event_code": "EVT20260520084542",
        "task_code": "RWD20260515141720",
        "status": "pending_report",
        "platform_code": "",
        "deadline_time": "2026-05-20 10:45:42",
        "remaining_minutes": 95,
        "responsible_department": "街道安监办",
        "handler_name": "",
        "description": "消防通道被纸箱和杂物占用，存在高风险隐患。",
        "suggestion": "立即通知物业清理，并完成复核拍照归档。",
        "timeline": [
            {"time": "05-20 08:45", "title": "AI识别", "desc": "智能眼镜识别消防通道堵塞", "status": "已完成", "color": "#18A058"},
            {"time": "05-20 08:46", "title": "生成工单", "desc": "事件自动生成待上报工单", "status": "待上报", "color": "#FAAD14"},
            {"time": "05-20 08:48", "title": "管理端确认", "desc": "等待管理员一键上报治理平台", "status": "处理中", "color": "#1677FF"},
        ],
    },
    {
        "work_order_code": "XFS202605200002",
        "title": "阳光花园社区垃圾满溢处置",
        "risk_level": "medium",
        "source": "人工上报",
        "reporter_name": "李雨晴",
        "area_code": "AREA_YHG",
        "point_name": "阳光花园社区2号楼",
        "event_code": "EVT20260520090218",
        "status": "processing",
        "platform_code": "GZPT202605200128",
        "deadline_time": "2026-05-20 13:02:18",
        "remaining_minutes": 162,
        "responsible_department": "环卫保洁队",
        "handler_name": "王工",
        "description": "垃圾桶满溢，周边散落垃圾较多。",
        "suggestion": "安排保洁清运，补拍整改后照片。",
        "timeline": [
            {"time": "05-20 09:02", "title": "事件上报", "desc": "巡查员现场拍照取证", "status": "已完成", "color": "#18A058"},
            {"time": "05-20 09:10", "title": "一键上报", "desc": "同步治理平台成功", "status": "已完成", "color": "#18A058"},
            {"time": "05-20 09:18", "title": "部门接单", "desc": "环卫保洁队已受理", "status": "处理中", "color": "#1677FF"},
        ],
    },
    {
        "work_order_code": "XFS202605200003",
        "title": "平安社区东门岗亭设备异常复核",
        "risk_level": "low",
        "source": "AI识别",
        "reporter_name": "赵敏",
        "area_code": "AREA_PA",
        "point_name": "平安社区东门岗亭",
        "event_code": "EVT20260520101536",
        "status": "finished",
        "platform_code": "GZPT202605200203",
        "deadline_time": "2026-05-21 10:15:36",
        "remaining_minutes": 0,
        "responsible_department": "物业服务中心",
        "handler_name": "陈工",
        "description": "岗亭设备离线，物业已重启恢复。",
        "suggestion": "纳入本周设备巡检报告。",
        "timeline": [
            {"time": "05-20 10:15", "title": "发现异常", "desc": "设备离线告警", "status": "已完成", "color": "#18A058"},
            {"time": "05-20 10:31", "title": "现场处置", "desc": "物业完成设备重启", "status": "已完成", "color": "#18A058"},
            {"time": "05-20 10:50", "title": "复核通过", "desc": "管理员复核完成", "status": "已完成", "color": "#18A058"},
        ],
    },
]

SEED_INSPECTION_REPORTS = [
    {
        "report_code": "BG202605200001",
        "report_title": "幸福里小区消防安全巡查闭环报告",
        "task_code": "RWD20260515141720",
        "work_order_code": "XFS202605200001",
        "report_status": "generated",
        "closure_rate": 71.9,
        "point_count": 6,
        "ai_detect_count": 12,
        "work_order_count": 1,
        "timeout_count": 0,
        "summary": "本次巡查覆盖幸福里小区重点楼栋和消防通道，发现高风险隐患1处，工单已进入上报流程。",
        "generated_time": "2026-05-20 11:20:00",
        "archive_time": None,
    },
    {
        "report_code": "BG202605200002",
        "report_title": "阳光花园社区环境巡查处置报告",
        "work_order_code": "XFS202605200002",
        "report_status": "generating",
        "closure_rate": 58.5,
        "point_count": 4,
        "ai_detect_count": 4,
        "work_order_count": 1,
        "timeout_count": 0,
        "summary": "阳光花园环境巡查发现垃圾满溢，责任队伍已受理并处置中。",
        "generated_time": "2026-05-20 11:40:00",
        "archive_time": None,
    },
]

SEED_LAW_DOCUMENTS = [
    {
        "document_code": "WS202605200001",
        "document_title": "责令立即整改通知书",
        "document_type": "责令立即整改通知书",
        "work_order_code": "XFS202605200001",
        "checked_unit": "幸福里小区物业服务中心",
        "check_location": "幸福里小区3号楼1-2层转角平台",
        "print_status": "pending_print",
        "inspector_name": "张三",
        "content": "经现场巡查，发现消防通道存在杂物堵塞，请立即整改并反馈整改照片。",
        "qr_code": "QR-WS202605200001",
    },
    {
        "document_code": "WS202605200002",
        "document_title": "现场检查记录",
        "document_type": "现场检查记录",
        "work_order_code": "XFS202605200002",
        "checked_unit": "阳光花园社区物业服务中心",
        "check_location": "阳光花园社区2号楼垃圾投放点",
        "print_status": "printed",
        "inspector_name": "李雨晴",
        "content": "现场发现垃圾满溢，已通知环卫保洁队清运并要求复核。",
        "qr_code": "QR-WS202605200002",
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
