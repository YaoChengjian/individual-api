import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

key = b'0khfB10q0nUK9FqcoB1SB4FGOUgJ8FRN'  # 需要与前端保持一致
iv = b'JXmQ0OWCb1JId6Fo'


def un_pad(s):
    """移除填充字符"""
    # 获取填充的字符数
    pad_len = s[-1]
    # 移除填充的字符并返回结果
    return s[:-pad_len]


# 解密函数
def decrypt(encrypted_data: str) -> str:
    # 使用AES解密
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_data))
    return un_pad(decrypted).decode('utf-8')


# 加密函数
def encrypt(data: str) -> str:

    # 使用AES加密
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))

    # 返回Base64编码的加密数据
    return base64.b64encode(encrypted).decode('utf-8')


if __name__ == '__main__':
    # 测试
    import time, json
    data = {
        "username": "admin",
        "password": "admin@123",
        "timestamp": int(time.time()),
        'captcha_id': '54d799757ce146d9a60a99d16c15bb6e',
        'captcha_code': 'ukz4z'
    }

    # data = {
    #     "timestamp": int(time.time()),
    # }

    param_str = json.dumps(data)
    print(encrypt(param_str))
