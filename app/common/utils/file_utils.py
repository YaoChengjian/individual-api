import hashlib
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import UploadFile

from app.common.exceptions.exception import TipsError
from app.config import ConfigClass

logger = logging.getLogger(__name__)


class FileUtils:
    upload_dir = '/upload'

    @staticmethod
    async def init_dir():

        dir_list = [
            # 上传文件的目录
            f"{ConfigClass.static_path}{FileUtils.upload_dir}",
        ]
        for path in dir_list:
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def get_md5(file_path: str) -> str:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                md5.update(chunk)
        return md5.hexdigest()

    @staticmethod
    def force_delete(path: str):
        """
        强制删除指定文件：忽略文件不存在、权限等异常
        """
        try:
            os.remove(path)
            logger.info(f"[删除成功] {path}")
        except FileNotFoundError:
            logger.warning(f"[忽略] 文件不存在：{path}")
        except PermissionError:
            logger.warning(f"[异常] 无权限删除：{path}")
        except Exception as e:
            logger.warning(f"[异常] 删除失败：{path} -> {e}")

    @staticmethod
    async def upload_file(
            file: UploadFile,
            use_origin_name: bool = False,
            save_dir: Optional[str] = None,
            limit_type: Optional[List[str]] = None,
            limit_mb: Optional[int] = None,
            md5_str: Optional[str] = None):
        """
        上传文件并保存至指定目录，可配置文件名、类型、大小限制及 MD5 校验。

        参数说明：
        ----------
        file : UploadFile
            待上传的文件对象。
        use_origin_name : bool
            是否保留原始文件名；若为 False，则使用 UUID 重命名（默认 False）。
        save_dir : Optional[str]
            文件保存的目录，相对于静态资源根路径；默认保存到 ConfigClass.static_path + FileUtils.upload_dir。
        limit_type : Optional[List[str]]
            限制允许的文件后缀类型列表（如 ['.jpg', '.png']），不传则不限制。
        limit_mb : Optional[int]
            限制文件最大体积（单位：MB），不传则不限制。
        md5_str : Optional[str]
            客户端传入的 MD5 值，用于完整性校验；若为空则不校验。

        返回值：
        ----------
        dict
            包含原始文件名 `file_name` 和可供前端访问的相对路径 `file_path`。
        """
        await FileUtils.init_dir()

        # 源文件名称
        file_name = file.filename

        # 文件后缀
        suffix = Path(file_name).suffix
        if limit_type and suffix not in limit_type:
            raise TipsError("不支持该文件类型")

        # 文件大小
        if limit_mb:
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)
            if size > limit_mb * 1024 * 1024:
                raise TipsError(f"文件不能大于{limit_mb}MB")

        # 保存的文件名称
        save_file_name = file_name if use_origin_name else f"{uuid.uuid4().hex}{suffix}"
        # 保存的文件路径 （这两路径的作用就是为了不暴露服务器的具体位置，以及方便文件迁移，只需要注意必须是 某个目录的 static文件夹作为总文件夹）
        opt_save_file_dir = f"{ConfigClass.static_root_path}{save_dir}" if save_dir else f"{ConfigClass.static_path}{FileUtils.upload_dir}"  # 操作保存时 完整的目录
        db_save_file_dir = save_dir if save_dir else f"{ConfigClass.static_dir}{FileUtils.upload_dir}"  # 保存与数据，以及返回给前端的 目录

        # 保存文件
        opt_save_file_path = f"{opt_save_file_dir}/{save_file_name}"
        db_save_file_path = f"{db_save_file_dir}/{save_file_name}"

        with open(opt_save_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # md5 完整性验证
        if md5_str and md5_str != FileUtils.get_md5(opt_save_file_path):
            # 删除文件
            FileUtils.force_delete(opt_save_file_path)
            raise TipsError(f"MD5检验失败，文件上传失败")

        return {'file_name': file_name, 'file_path': db_save_file_path}

    @staticmethod
    async def get_save_filepath(save_dir: str, suffix: str) -> dict[str, str]:
        """
            save_dir: 文件保存的目录
            suffix: 文件后缀
        """
        # 完整的服务器路径
        abs_dir = f"{ConfigClass.static_path}{save_dir}"
        # 确保目录存在
        os.makedirs(abs_dir, exist_ok=True)

        # 生成保存的完整路径
        save_file_name = f"{uuid.uuid4().hex}{suffix}"

        # 保存的文件路径
        opt_save_file_dir = abs_dir
        db_save_file_dir = f"{ConfigClass.static_dir}{save_dir}"

        # 保存文件
        opt_save_file_path = f"{opt_save_file_dir}/{save_file_name}"
        db_save_file_path = f"{db_save_file_dir}/{save_file_name}"

        return {'save_path': opt_save_file_path, 'db_path': db_save_file_path}
