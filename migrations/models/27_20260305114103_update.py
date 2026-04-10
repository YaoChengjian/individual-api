from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `pro_product_apply_record` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `product_id` VARCHAR(32) NOT NULL COMMENT '原始产品ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT 'Web用户ID',
    `reg_cert_url` VARCHAR(300) COMMENT '广东省数据资产登记凭证URL',
    `reg_cert_code` VARCHAR(50) COMMENT '广东省数据资产登记凭证编码',
    `reg_cert_date` DATE COMMENT '广东省数据资产登记凭证核发日期',
    `product_no` VARCHAR(50) COMMENT '产品编号',
    `listing_cert_url` VARCHAR(300) COMMENT '广东省数据资产交易标的挂牌证书URL',
    `listing_cert_date` DATE COMMENT '广东省数据资产交易标的挂牌证书核发日期',
    `data_origin` VARCHAR(200) COMMENT '数据来源',
    `update_frequency` VARCHAR(50) COMMENT '更新频率',
    `data_volume` VARCHAR(50) COMMENT '数据量',
    `data_version` VARCHAR(50) COMMENT '数据版本',
    `update_date` DATE COMMENT '数据最后更新日期',
    `authorization_type` VARCHAR(100) COMMENT '授权类型',
    `email` VARCHAR(100) COMMENT '邮箱',
    `title` VARCHAR(100) COMMENT '产品标题',
    `product_intro` LONGTEXT COMMENT '产品简介',
    `amount` DECIMAL(15,2) NOT NULL COMMENT '金额' DEFAULT 0,
    `desc` LONGTEXT COMMENT '产品说明',
    `data_type` INT NOT NULL COMMENT '数据类型。1：公共数据；2：非公共数据',
    `pay_mode` INT NOT NULL COMMENT '收费模式。1：一次支付；2：定期支付；3：免费；4：面议',
    `ban_range` LONGTEXT COMMENT '禁止使用范围',
    `target_customers` LONGTEXT COMMENT '目标客户群体',
    `delivery_desc` LONGTEXT COMMENT '产品交付说明',
    `contact_name` VARCHAR(50) COMMENT '联系人',
    `contact_phone` VARCHAR(30) COMMENT '联系电话',
    `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；4：撤销申请' DEFAULT 1,
    `reason` LONGTEXT COMMENT '驳回理由',
    `origin_type` VARCHAR(50) NOT NULL COMMENT '创建来源。web:web用户创建；admin:后台用户创建' DEFAULT 'web',
    `label_id_list` JSON NOT NULL COMMENT '申请时的标签ID列表',
    `label_name_list` JSON NOT NULL COMMENT '申请时的标签名称列表',
    `scene_ids` JSON NOT NULL COMMENT '申请时的应用场景ID列表',
    `scene_name_list` JSON NOT NULL COMMENT '申请时的应用场景名称列表',
    `ecology_ids` JSON NOT NULL COMMENT '申请时的产品形态ID列表',
    `ecology_name_list` JSON NOT NULL COMMENT '申请时的产品形态名称列表'
) CHARACTER SET utf8mb4 COMMENT='产品申请记录快照表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `pro_product_apply_record`;"""
