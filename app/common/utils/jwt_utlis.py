from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import ConfigClass

SECRET_KEY = ConfigClass.secret_key
ALGORITHM = "HS256"


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """验证明文密码与加密密码是否匹配"""
    try:
        return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())
    except ValueError:
        return False


def get_password(password: str) -> str:
    """生成加密后的密码"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_token(data: dict, expires_delta: timedelta = timedelta(hours=12)) -> str:
    """生成 JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
