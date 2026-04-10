from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `cert_application` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `user_id` VARCHAR(64) COMMENT '提交人Web用户ID',
    `db_type` VARCHAR(50) COMMENT '数商类型。supplier：供方；demander；server：服务方； 可以多选，使用-符号连接',
    `business_license` VARCHAR(300) COMMENT '营业执照',
    `company_logo` VARCHAR(300) COMMENT '企业Logo URL/Key',
    `company_name` VARCHAR(200) NOT NULL COMMENT '企业名称',
    `cert_type` INT NOT NULL COMMENT '证件类型。0：其他；1：统一社会信用代码；2：商业登记证号码；',
    `cert_no` VARCHAR(100) NOT NULL COMMENT '证件/统一社会信用代码',
    `company_type` VARCHAR(100) COMMENT '企业类型',
    `register_currency` INT NOT NULL COMMENT '注册资本币种。1：人民币',
    `register_amount` DECIMAL(18,2) COMMENT '注册资本金额',
    `biz_place` VARCHAR(100) COMMENT '营业场所',
    `establish_date` DATE COMMENT '成立日期',
    `biz_term_begin` DATE COMMENT '营业期限(起)',
    `biz_term_end` DATE COMMENT '营业期限(止)',
    `biz_scope` LONGTEXT COMMENT '经营范围',
    `reg_address` VARCHAR(300) COMMENT '注册地址',
    `reg_address_detail` VARCHAR(300) COMMENT '详细地址',
    `company_intro` LONGTEXT COMMENT '公司简介',
    `certification_type` VARCHAR(50) COMMENT '认证类型',
    `email` VARCHAR(120) COMMENT '邮箱',
    `status` INT NOT NULL COMMENT '审核状态。0：草稿；1：等待审核；2：认证通过；3：认证驳回' DEFAULT 0,
    `submit_time` DATETIME(6) NOT NULL COMMENT '提交时间' DEFAULT CURRENT_TIMESTAMP(6),
    `review_time` DATETIME(6) COMMENT '审核时间',
    `reviewer_user_id` VARCHAR(64) COMMENT '审核员用户ID',
    `review_note` LONGTEXT COMMENT '驳回原因/审核备注'
) CHARACTER SET utf8mb4 COMMENT='认证申请表';
CREATE TABLE IF NOT EXISTS `cert_file` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `cert_id` VARCHAR(64) NOT NULL COMMENT '认证申请ID',
    `file_url` VARCHAR(500) NOT NULL COMMENT '文件URL',
    `file_name` VARCHAR(255) COMMENT '原始文件名'
) CHARACTER SET utf8mb4 COMMENT='认证申请-附件表';
CREATE TABLE IF NOT EXISTS `cert_contact_person` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `cert_id` VARCHAR(64) NOT NULL COMMENT '认证申请ID',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `position` VARCHAR(50) COMMENT '职务',
    `phone` VARCHAR(30) COMMENT '联系电话',
    `email` VARCHAR(120) COMMENT '邮箱',
    `id_number` VARCHAR(64) COMMENT '（可选）证件号',
    `id_front_url` VARCHAR(300) COMMENT '身份证正面URL',
    `id_back_url` VARCHAR(300) COMMENT '身份证反面URL'
) CHARACTER SET utf8mb4 COMMENT='认证申请-联系人信息表';
CREATE TABLE IF NOT EXISTS `cert_legal_person` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `cert_id` VARCHAR(64) NOT NULL COMMENT '认证申请ID',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `id_type` INT NOT NULL COMMENT '证件类型。1：身份证',
    `id_number` VARCHAR(64) NOT NULL COMMENT '证件号',
    `id_front_url` VARCHAR(300) COMMENT '身份证正面URL',
    `id_back_url` VARCHAR(300) COMMENT '身份证反面URL'
) CHARACTER SET utf8mb4 COMMENT='认证申请-法人信息表';
CREATE TABLE IF NOT EXISTS `sys_log` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键ID',
    `user_id` VARCHAR(64) COMMENT '用户ID',
    `user_name` VARCHAR(64) COMMENT '用户名称',
    `path` VARCHAR(255) NOT NULL COMMENT '请求路径（不含域名）',
    `method` VARCHAR(16) NOT NULL COMMENT 'HTTP方法',
    `ip` VARCHAR(64) COMMENT '客户端IP地址',
    `summary` VARCHAR(255) COMMENT '接口摘要信息',
    `req_headers` JSON COMMENT '请求头',
    `req_body` JSON COMMENT '请求体',
    `resp_code` INT,
    `resp_msg` VARCHAR(255) COMMENT '响应信息',
    `resp_body` JSON COMMENT '响应体（JSON存储，建议采样或截断，防止大文件占用空间）',
    `latency_ms` INT NOT NULL COMMENT '接口耗时（毫秒）',
    `create_time` DATETIME(6) NOT NULL COMMENT '日志记录时间' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='操作日志表（记录用户请求与响应信息）';
CREATE TABLE IF NOT EXISTS `sys_permission` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `name` VARCHAR(100) NOT NULL COMMENT '权限名称',
    `mark` VARCHAR(100) NOT NULL COMMENT '权限标识',
    `parent_mark` VARCHAR(100) COMMENT '父级权限标识',
    `description` LONGTEXT COMMENT '权限描述'
) CHARACTER SET utf8mb4 COMMENT='权限表';
CREATE TABLE IF NOT EXISTS `sys_role` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `description` LONGTEXT COMMENT '角色描述',
    `status` BOOL NOT NULL COMMENT '状态。0：停用；1：正常' DEFAULT 1,
    `create_user_id` VARCHAR(32) COMMENT '创建者ID'
) CHARACTER SET utf8mb4 COMMENT='角色表';
CREATE TABLE IF NOT EXISTS `sys_role_permission` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `role_id` VARCHAR(32) NOT NULL COMMENT '角色ID',
    `perm_mark` VARCHAR(50) NOT NULL COMMENT '权限标识',
    KEY `idx_sys_role_pe_role_id_f464e0` (`role_id`),
    KEY `idx_sys_role_pe_perm_ma_a666d4` (`perm_mark`)
) CHARACTER SET utf8mb4 COMMENT='角色-权限 关联表';
CREATE TABLE IF NOT EXISTS `sys_user` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL COMMENT '加密后的密码',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `phone` VARCHAR(20) COMMENT '手机号',
    `status` INT NOT NULL COMMENT '状态。0：停用；1：正常' DEFAULT 1,
    `description` LONGTEXT COMMENT '说明',
    `is_superuser` BOOL NOT NULL COMMENT '是否超级管理员' DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='用户表';
CREATE TABLE IF NOT EXISTS `sys_user_role` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
    `role_id` VARCHAR(32) NOT NULL COMMENT '角色ID',
    KEY `idx_sys_user_ro_user_id_f77cd0` (`user_id`),
    KEY `idx_sys_user_ro_role_id_2aa7a8` (`role_id`)
) CHARACTER SET utf8mb4 COMMENT='用户-角色 关联表';
CREATE TABLE IF NOT EXISTS `web_user` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL COMMENT '加密后的密码',
    `name` VARCHAR(50) COMMENT '姓名',
    `phone` VARCHAR(20) COMMENT '手机号',
    `status` INT NOT NULL COMMENT '状态。0：停用；1：正常' DEFAULT 1
) CHARACTER SET utf8mb4 COMMENT='Web用户表';
CREATE TABLE IF NOT EXISTS `pro_demand` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `user_id` VARCHAR(64) NOT NULL COMMENT 'Web用户ID',
    `title` VARCHAR(50) NOT NULL COMMENT '需求标题',
    `desc` LONGTEXT COMMENT '需求说明',
    `qualification_require` LONGTEXT COMMENT '资格要求',
    `limit_date` DATE COMMENT '截止日期',
    `contact_name` VARCHAR(50) COMMENT '联系人',
    `contact_phone` VARCHAR(30) COMMENT '联系电话',
    `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；'
) CHARACTER SET utf8mb4 COMMENT='需求表';
CREATE TABLE IF NOT EXISTS `pro_demand_ecology_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `demand_id` VARCHAR(64) NOT NULL COMMENT '需求ID',
    `ecology_id` VARCHAR(64) NOT NULL COMMENT '产品形态ID'
) CHARACTER SET utf8mb4 COMMENT='产品形态关系表';
CREATE TABLE IF NOT EXISTS `pro_demand_scene_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `demand_id` VARCHAR(64) NOT NULL COMMENT '需求ID',
    `scene_id` VARCHAR(64) NOT NULL COMMENT '应用场景ID'
) CHARACTER SET utf8mb4 COMMENT='产品应用场景关系表';
CREATE TABLE IF NOT EXISTS `pro_demand_tag` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `demand_id` VARCHAR(64) NOT NULL COMMENT '需求ID',
    `name` VARCHAR(50) NOT NULL COMMENT '标签名称'
) CHARACTER SET utf8mb4 COMMENT='产品标签表';
CREATE TABLE IF NOT EXISTS `pro_ecology` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名',
    `parent_id` VARCHAR(64) COMMENT '父级分类ID'
) CHARACTER SET utf8mb4 COMMENT='产品形态表';
CREATE TABLE IF NOT EXISTS `pro_product` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `user_id` VARCHAR(64) NOT NULL COMMENT 'Web用户ID',
    `publisher_name` VARCHAR(50) COMMENT '发布者名称',
    `reg_cert_url` VARCHAR(300) COMMENT '广东省数据资产登记凭证-URL',
    `reg_cert_code` VARCHAR(50) COMMENT '广东省数据资产登记凭证-编码',
    `reg_cert_date` VARCHAR(50) COMMENT '广东省数据资产登记凭证-核发日期',
    `desc` LONGTEXT COMMENT '产品说明',
    `data_type` INT NOT NULL COMMENT '数据类型。1：公共数据；2：非公共数据',
    `pay_mode` INT NOT NULL COMMENT '收费模式。1：一次支付；2：定期支付；3：免费；4：面议',
    `ban_range` LONGTEXT COMMENT '禁止使用范围',
    `target_customers` LONGTEXT COMMENT '目标客户群体',
    `product_detail` LONGTEXT COMMENT '产品详情',
    `product_scene` LONGTEXT COMMENT '产品应用场景',
    `delivery_desc` LONGTEXT COMMENT '产品交付说明',
    `settle_requirement` LONGTEXT COMMENT '结算要求',
    `limit_date` DATE COMMENT '截止日期',
    `contact_name` VARCHAR(50) COMMENT '联系人',
    `contact_phone` VARCHAR(30) COMMENT '联系电话',
    `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；'
) CHARACTER SET utf8mb4 COMMENT='产品表';
CREATE TABLE IF NOT EXISTS `pro_product_ecology_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `product_id` VARCHAR(64) NOT NULL COMMENT '产品ID',
    `ecology_id` VARCHAR(64) NOT NULL COMMENT '产品形态ID'
) CHARACTER SET utf8mb4 COMMENT='产品形态关系表';
CREATE TABLE IF NOT EXISTS `pro_product_scene_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `product_id` VARCHAR(64) NOT NULL COMMENT '产品ID',
    `scene_id` VARCHAR(64) NOT NULL COMMENT '应用场景ID'
) CHARACTER SET utf8mb4 COMMENT='产品应用场景关系表';
CREATE TABLE IF NOT EXISTS `pro_product_tag` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `product_id` VARCHAR(64) NOT NULL COMMENT '产品ID',
    `name` VARCHAR(50) NOT NULL COMMENT '标签名称'
) CHARACTER SET utf8mb4 COMMENT='产品标签表';
CREATE TABLE IF NOT EXISTS `pro_scene` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `name` VARCHAR(50) NOT NULL COMMENT '场景名称',
    `parent_id` VARCHAR(64) COMMENT '父级分类ID'
) CHARACTER SET utf8mb4 COMMENT='应用场景表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
