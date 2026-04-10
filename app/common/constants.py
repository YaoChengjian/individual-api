class ErrorConstants:

    Authentication = {
        1000: '新用户注册',
        1001: '认证失败，用户名或密码错误',
        1002: 'Token无效或已过期',
        1003: '无权访问',
        1004: '账户不存在',
        1005: '账号已停用!',
        1006: '验证过期',
        1007: '验证码错误或已过期，请重新获取',
        1008: 'H5用户未初始化信息',
    }

    # 数据验证类
    DataVerify = {
        2001: '参数错误'
    }


class RedisKey:

    login_token = 'login-token-'
    web_login_token = 'web-login-token-'

    web_captcha = 'web:captcha:'                  # 新增：一次性验证码
    web_login_fail_count = 'web:login:fail:'      # 新增：失败次数计数
    web_login_lock = 'web:login:lock:'            # 新增：账号锁定

    sys_captcha = 'sys:captcha:'                  # 新增：一次性验证码
    sys_login_fail_count = 'sys:login:fail:'      # 新增：失败次数计数
    sys_login_lock = 'sys:login:lock:'            # 新增：账号锁定

    web_register_captcha = 'register:captcha'


class ProductShelfStatus:
    """
    产品上架状态常量。
    说明：
    1. 该类用于统一维护产品“上架/下架/禁用”的状态值；
    2. 前后台涉及产品可见性判断时，统一引用本类，避免魔法值散落在业务代码中。
    """
    ON = 1
    OFF = 2
    DISABLED = 3
    # 兼容历史命名：旧代码中 FORCE_OFF 的语义已迁移为“禁用”。
    FORCE_OFF = DISABLED


class ProductApplyType:
    """
    产品申请类型常量。
    说明：
    1. FIRST：同一 product_id 的首次申请；
    2. CHANGE：同一 product_id 的第二次及以上申请（变更申请）。
    """
    FIRST = 1
    CHANGE = 2


class BusinessZoneStatus:
    """
    数商专区状态常量。
    说明：
    1. DRAFT：草稿，尚未提交审核；
    2. PENDING：待审核，已提交发布申请；
    3. APPROVED：审核通过；
    4. REJECTED：审核驳回；
    5. REVOKED：撤销申请。
    """
    DRAFT = 0
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    REVOKED = 4


class BusinessZoneShelfStatus:
    """
    数商专区上架状态常量。
    说明：
    1. ON：上架；
    2. OFF：下架；
    3. DISABLED：禁用。
    """
    ON = 1
    OFF = 2
    DISABLED = 3


class BusinessZoneApplyType:
    """
    数商专区申请类型常量。
    说明：
    1. FIRST：首次申请；
    2. CHANGE：变更申请。
    """
    FIRST = 1
    CHANGE = 2


class CertApplyType:
    """
    认证申请类型常量。
    说明：
    1. FIRST：同一 cert_id 的首次申请；
    2. CHANGE：同一 cert_id 的第二次及以上申请（变更申请）。
    """
    FIRST = 1
    CHANGE = 2


class CertDisableResourceType:
    """
    数商禁用影响到的资源类型常量。
    说明：
    1. 该常量用于记录“禁用后被强制下架”的资源；
    2. 启用时根据该类型准确恢复对应资源状态；
    3. 后续若新增其他需要随数商禁用联动的资源，也可继续扩展这里。
    """
    PRODUCT = 'product'
    DEMAND = 'demand'
    BUSINESS_ZONE = 'business_zone'


class PortalRankingType:
    """
    门户排行榜类型常量。
    说明：
    1. PRODUCT：产品排行榜；
    2. BUSINESS_ZONE：数商专区排行榜。
    """
    PRODUCT = 'product'
    BUSINESS_ZONE = 'business_zone'


class DemandApplyType:
    """
    需求申请类型常量。
    说明：
    1. FIRST：同一 demand_id 的首次申请；
    2. CHANGE：同一 demand_id 的第二次及以上申请（变更申请）。
    """
    FIRST = 1
    CHANGE = 2
