import string
import random


class StrUtils:

    @staticmethod
    def get_random_str(str_len, str_type='all') -> str:
        """获取随机字符:
        all : 数字+字母
        digits: 数字
        letters: 字母
        """

        content = ''
        if str_type == 'all':
            content = string.ascii_letters + string.digits
        elif str_type == 'digits':
            content = string.digits
        elif str_type == 'letters':
            content = string.ascii_letters

        return ''.join(random.choices(content, k=str_len))
