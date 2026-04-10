from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `cert_apply_record` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `cert_id` VARCHAR(64) NOT NULL COMMENT '认证主表ID',
    `review_no` VARCHAR(50) COMMENT '认证审核编号',
    `user_id` VARCHAR(64) COMMENT '提交人Web用户ID',
    `db_type` VARCHAR(50) COMMENT '数商类型(认证类型)。supplier：供方；demander；server：服务方，可多选，使用-连接',
    `business_license` VARCHAR(300) COMMENT '营业执照',
    `company_logo` VARCHAR(300) COMMENT '企业Logo URL/Key',
    `company_name` VARCHAR(200) NOT NULL COMMENT '企业名称',
    `cert_type` INT NOT NULL COMMENT '证件类型。0：其他；1：统一社会信用代码；2：商业登记证号码',
    `cert_no` VARCHAR(100) NOT NULL COMMENT '证件/统一社会信用代码',
    `company_type` INT NOT NULL COMMENT '企业类型。1：有限责任公司；2：股份有限公司；3：其他企业法人；4：事业单位法人；5：社会团体法人；6：捐助法人(基金会)；7：捐助法人(社会服务机构)；8：捐助法人(宗教活动场所)',
    `register_currency` INT NOT NULL COMMENT '注册资本币种。1：人民币',
    `register_amount` DECIMAL(18,2) COMMENT '注册资本金额',
    `biz_place` VARCHAR(100) COMMENT '营业场所',
    `establish_date` DATE COMMENT '成立日期',
    `biz_term_begin` DATE COMMENT '营业期限(起)',
    `biz_term_end` DATE COMMENT '营业期限(止)',
    `biz_scope` LONGTEXT COMMENT '经营范围',
    `reg_address` VARCHAR(300) COMMENT '注册地址',
    `company_intro` LONGTEXT COMMENT '公司简介',
    `contact_name` VARCHAR(50) COMMENT '联系人快照',
    `contact_phone` VARCHAR(30) COMMENT '联系电话快照',
    `status` INT NOT NULL COMMENT '审核状态。0：草稿；1：等待审核；2：认证通过；3：认证驳回；4：撤销认证' DEFAULT 1,
    `submit_time` DATETIME(6) NOT NULL COMMENT '提交时间' DEFAULT CURRENT_TIMESTAMP(6),
    `review_time` DATETIME(6) COMMENT '审核时间',
    `reviewer_user_id` VARCHAR(64) COMMENT '审核员用户ID',
    `review_note` LONGTEXT COMMENT '驳回原因/审核备注',
    `legal_person` JSON NOT NULL COMMENT '法人信息快照',
    `contact_person` JSON NOT NULL COMMENT '联系人信息快照',
    `file_list` JSON NOT NULL COMMENT '附件列表快照',
    KEY `idx_cert_apply__review__cadc41` (`review_no`)
) CHARACTER SET utf8mb4 COMMENT='认证申请记录快照表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `cert_apply_record`;"""
