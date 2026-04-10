import base64
import io
import os
import random
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.common.constants import RedisKey
from app.common.utils.redis_utils import RedisUtil


class CaptchaService:
    # 登录框宽度固定，默认使用 4 位验证码来换取更大的单字显示面积。
    CODE_LEN = 4
    EXPIRE_SEC = 120  # 验证码有效期（秒）
    # 默认按登录页 `108 x 40` 的显示框输出，避免浏览器缩放后文字发虚。
    IMAGE_WIDTH = 108
    IMAGE_HEIGHT = 40
    FONT_SIZE = 40
    LINE_COUNT = 2
    NOISE_POINT_COUNT = 8
    CHAR_GAP = 0
    TEXT_MARGIN_X = 3
    # 去掉容易混淆的字符（0/O、1/I）
    ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

    @classmethod
    def build_code(cls, exclude: str | None = None) -> str:
        """
        生成验证码文本。

        `exclude` 用于避免连续两次刷新拿到完全相同的验证码内容，提升前端刷新时的感知。
        """
        code_len = cls._read_int_env('CAPTCHA_CODE_LEN', cls.CODE_LEN, 4, 6)
        code = ''
        for _ in range(8):
            code = ''.join(random.choice(cls.ALPHABET) for _ in range(code_len))
            if not exclude or code.lower() != exclude.lower():
                return code
        return code

    @classmethod
    async def generate(cls, code_type: str = 'web') -> dict:
        """
        生成验证码图片（Base64）并写入 Redis；返回 captcha_id + image(data URI) + expires_in
        """
        code = cls.build_code()
        captcha_id = uuid.uuid4().hex
        image_bytes = cls._build_image(code)

        key = ''
        if code_type == 'web':
            key = f'{RedisKey.web_captcha}{captcha_id}'
        elif code_type == 'sys':
            key = f'{RedisKey.sys_captcha}{captcha_id}'
        elif code_type == 'web-register':
            key = f'{RedisKey.web_register_captcha}{captcha_id}'

        await RedisUtil.set(key, code.lower(), expire=cls.EXPIRE_SEC)
        return {
            'captcha_id': captcha_id,
            'image': 'data:image/png;base64,' + base64.b64encode(image_bytes).decode(),
            'expires_in': cls.EXPIRE_SEC
        }

    @staticmethod
    def _load_font(size: int):
        """
        加载验证码字体（多环境兜底）：
        1. 优先读取环境变量 CAPTCHA_FONT_PATH；
        2. 依次尝试 Linux/Windows 常见字体路径；
        3. 再尝试按字体名加载系统已注册字体；
        4. 最后退回 Pillow 默认字体。
        """
        # 允许运维通过环境变量显式指定验证码字体文件路径。
        font_candidates = []
        env_font_path = os.getenv('CAPTCHA_FONT_PATH')
        if env_font_path:
            font_candidates.append(env_font_path)

        # 常见系统字体路径（覆盖 Linux 与 Windows）。
        font_candidates.extend([
            # macOS 常见粗体字体，当前开发机优先命中这里，避免退回 Pillow 默认小字体。
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            'C:/Windows/Fonts/arialbd.ttf',
            'C:/Windows/Fonts/msyhbd.ttc',
        ])

        # 兼容部分 Python/Pillow 安装目录中附带字体文件的场景。
        pil_dir = Path(ImageFont.__file__).resolve().parent
        font_candidates.extend([
            str(pil_dir / 'fonts' / 'DejaVuSans-Bold.ttf'),
            str(pil_dir / 'DejaVuSans-Bold.ttf'),
        ])

        for font_path in font_candidates:
            try:
                if font_path and Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue

        # 按字体名兜底尝试（依赖系统字体注册）。
        for font_name in ['Arial Bold.ttf', 'Hiragino Sans GB.ttc', 'STHeiti Medium.ttc', 'DejaVuSans-Bold.ttf', 'arialbd.ttf', 'msyhbd.ttc']:
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                continue

        return ImageFont.load_default()

    @staticmethod
    def _read_int_env(name: str, default: int, minimum: int, maximum: int) -> int:
        """
        从环境变量读取整数配置，并做边界保护。

        验证码是高频接口，这里统一做轻量解析，避免每个参数都重复写 try/except。
        """
        value = os.getenv(name)
        if not value:
            return default
        try:
            parsed = int(value)
        except Exception:
            return default
        return max(minimum, min(maximum, parsed))

    @staticmethod
    def _build_image(text: str) -> bytes:
        width = CaptchaService._read_int_env('CAPTCHA_WIDTH', CaptchaService.IMAGE_WIDTH, 96, 180)
        height = CaptchaService._read_int_env('CAPTCHA_HEIGHT', CaptchaService.IMAGE_HEIGHT, 36, 64)
        font_size = CaptchaService._read_int_env('CAPTCHA_FONT_SIZE', CaptchaService.FONT_SIZE, 24, 44)
        line_count = CaptchaService._read_int_env('CAPTCHA_LINE_COUNT', CaptchaService.LINE_COUNT, 0, 3)
        noise_points = CaptchaService._read_int_env(
            'CAPTCHA_NOISE_POINTS',
            CaptchaService.NOISE_POINT_COUNT,
            0,
            120,
        )
        char_gap = CaptchaService._read_int_env('CAPTCHA_CHAR_GAP', CaptchaService.CHAR_GAP, 0, 6)
        text_margin_x = CaptchaService._read_int_env('CAPTCHA_TEXT_MARGIN_X', CaptchaService.TEXT_MARGIN_X, 2, 12)

        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 使用跨平台字体加载策略，避免单一路径失效导致字体缩小。
        font = CaptchaService._load_font(font_size)

        # 先计算文本整体尺寸。
        char_sizes = []
        max_char_h = 0
        for ch in text:
            try:
                bbox = draw.textbbox((0, 0), ch, font=font, stroke_width=1)
                char_w = max(1, bbox[2] - bbox[0])
                char_h = max(1, bbox[3] - bbox[1])
            except Exception:
                # 极端兜底：若测量失败，按字号近似估算。
                char_w = max(1, int(font_size * 0.6))
                char_h = max(1, int(font_size))
            char_sizes.append((char_w, char_h))
            if char_h > max_char_h:
                max_char_h = char_h

        total_text_w = sum(w for w, _ in char_sizes) + char_gap * max(0, len(text) - 1)
        available_text_w = max(1, width - text_margin_x * 2)
        base_y = max(0, int((height - max_char_h) / 2) - 1)

        # 单独绘制一层文本；如果 5 位字符总宽超出画布，就只横向压缩文本层。
        text_layer = Image.new('RGBA', (max(total_text_w, 1), height), (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_layer)
        text_fill = (15, 23, 42, 255)

        x_cursor = 0
        for i, ch in enumerate(text):
            char_w, char_h = char_sizes[i]
            y = max(0, min(height - char_h, base_y))
            text_draw.text(
                (x_cursor, y),
                ch,
                font=font,
                fill=text_fill,
                stroke_width=1,
                stroke_fill=text_fill,
            )
            x_cursor += char_w + char_gap

        if total_text_w > available_text_w:
            resample = getattr(getattr(Image, 'Resampling', Image), 'LANCZOS')
            text_layer = text_layer.resize((available_text_w, height), resample)
            rendered_text_w = available_text_w
        else:
            rendered_text_w = total_text_w

        dest_x = max(text_margin_x, int((width - rendered_text_w) / 2))
        composed = img.convert('RGBA')
        composed.alpha_composite(text_layer, dest=(dest_x, 0))
        img = composed.convert('RGB')
        draw = ImageDraw.Draw(img)

        # 文本绘制完成后再叠加轻量干扰线，让视觉上明显是“带干扰线验证码”，同时不至于压住正文。
        for _ in range(line_count):
            draw.line(
                (
                    random.randint(0, max(0, width // 5)),
                    random.randint(0, height - 1),
                    random.randint(max(0, width * 3 // 5), width - 1),
                    random.randint(0, height - 1),
                ),
                fill=(
                    random.randint(150, 178),
                    random.randint(160, 186),
                    random.randint(175, 205),
                ),
                width=1,
            )

        # 噪点数量降低，颜色保持浅灰，避免压住正文。
        for _ in range(noise_points):
            draw.point((random.randint(0, width - 1), random.randint(0, height - 1)),
                       fill=(random.randint(205, 235),) * 3)

        bio = io.BytesIO()
        img.save(bio, format='PNG')
        return bio.getvalue()

    @classmethod
    async def verify_and_consume(cls, captcha_id: str, user_input: str, code_type: str = 'web') -> bool:
        """
        一次性校验：成功/失败后都会销毁该验证码，确保“只能用一次”
        如你的 Redis 支持 GETDEL，建议在 RedisUtil 中实现原子 getdel 以彻底避免并发复用。
        """
        if not captcha_id or not user_input:
            return False

        key = ''
        if code_type == 'web':
            key = f'{RedisKey.web_captcha}{captcha_id}'
        elif code_type == 'sys':
            key = f'{RedisKey.sys_captcha}{captcha_id}'
        elif code_type == 'web-register':
            key = f'{RedisKey.web_register_captcha}{captcha_id}'

        # 优先尝试原子 GETDEL
        code = None
        if hasattr(RedisUtil, 'getdel'):
            code = await RedisUtil.getdel(key)
        else:
            code = await RedisUtil.get(key)
            if code is not None:
                await RedisUtil.delete(key)

        if code is None:   # 已过期或已被使用
            return False

        return user_input.strip().lower() == str(code).strip().lower()
