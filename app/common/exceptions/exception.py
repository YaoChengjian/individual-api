class TipsError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return f'{self.msg}'


class WeChatAPIError(Exception):
    """企业微信接口统一异常封装"""

    def __init__(self, errcode: int, errmsg: str):
        super().__init__(f"WeChat API Error {errcode}: {errmsg}")
        self.errcode = errcode
        self.errmsg = errmsg
