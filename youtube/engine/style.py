"""채널 공통 디자인 토큰. 색·폰트·크기를 여기서만 바꾸면 전 영상에 반영된다."""
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"

W, H = 1920, 1080
FPS = 30

# 다크 네이비 + 골드 포인트. 한국 관례대로 상승=빨강, 하락=파랑.
BG_TOP = (16, 22, 40)
BG_BOT = (7, 10, 20)
PANEL = (24, 32, 56)
FG = (238, 241, 248)
MUTED = (138, 150, 176)
FAINT = (52, 62, 90)
GOLD = (255, 194, 70)
UP = (240, 84, 84)
DOWN = (74, 144, 255)
NEUTRAL = (150, 160, 182)

SAFE_X = 120          # 좌우 여백
SUB_Y = 1032          # 자막 기준선(하단)


@lru_cache(maxsize=None)
def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    """weight: Regular / Medium / SemiBold / Bold / ExtraBold / Black"""
    path = FONT_DIR / f"Pretendard-{weight}.otf"
    if not path.exists():
        raise SystemExit("폰트가 없습니다. 먼저 `python tools/fetch_assets.py` 를 실행하세요.")
    return ImageFont.truetype(str(path), size)
