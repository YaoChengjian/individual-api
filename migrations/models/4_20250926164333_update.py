from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_application` DROP COLUMN `certification_type`;
        ALTER TABLE `cert_application` MODIFY COLUMN `status` INT NOT NULL COMMENT '审核状态。0：草稿；1：等待审核；2：认证通过；3：认证驳回；4：撤销认证' DEFAULT 0;
        ALTER TABLE `cert_application` MODIFY COLUMN `db_type` VARCHAR(50) COMMENT '数商类型(认证类型)。supplier：供方；demander；server：服务方； 可以多选，使用-符号连接';
        ALTER TABLE `cert_application` MODIFY COLUMN `company_type` INT NOT NULL COMMENT '企业类型。1：有限责任公司；2：股份有限公司；3：其他企业法人；4：事业单位法人；5：社会团体法人；6：捐助法人（基金会）；7：捐助法人（社会服务机构）；8：捐助法人（宗教活动场所）';
        ALTER TABLE `cert_application` MODIFY COLUMN `company_type` INT NOT NULL COMMENT '企业类型。1：有限责任公司；2：股份有限公司；3：其他企业法人；4：事业单位法人；5：社会团体法人；6：捐助法人（基金会）；7：捐助法人（社会服务机构）；8：捐助法人（宗教活动场所）';
        ALTER TABLE `cert_application` MODIFY COLUMN `company_type` INT NOT NULL COMMENT '企业类型。1：有限责任公司；2：股份有限公司；3：其他企业法人；4：事业单位法人；5：社会团体法人；6：捐助法人（基金会）；7：捐助法人（社会服务机构）；8：捐助法人（宗教活动场所）';
        ALTER TABLE `cert_file` ADD `file_path` VARCHAR(500) NOT NULL COMMENT '文件路径';
        ALTER TABLE `cert_file` DROP COLUMN `file_url`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_file` ADD `file_url` VARCHAR(500) NOT NULL COMMENT '文件URL';
        ALTER TABLE `cert_file` DROP COLUMN `file_path`;
        ALTER TABLE `cert_application` ADD `certification_type` VARCHAR(50) COMMENT '认证类型';
        ALTER TABLE `cert_application` MODIFY COLUMN `status` INT NOT NULL COMMENT '审核状态。0：草稿；1：等待审核；2：认证通过；3：认证驳回' DEFAULT 0;
        ALTER TABLE `cert_application` MODIFY COLUMN `db_type` VARCHAR(50) COMMENT '数商类型。supplier：供方；demander；server：服务方； 可以多选，使用-符号连接';
        ALTER TABLE `cert_application` MODIFY COLUMN `company_type` VARCHAR(100) COMMENT '企业类型';
        ALTER TABLE `cert_application` MODIFY COLUMN `company_type` VARCHAR(100) COMMENT '企业类型';
        ALTER TABLE `cert_application` MODIFY COLUMN `company_type` VARCHAR(100) COMMENT '企业类型';"""
