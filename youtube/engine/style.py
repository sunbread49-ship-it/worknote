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

ON_ACCENT = (16, 20, 32)   # 강조색 알약 위 글자색
THEME = __import__("os").environ.get("CH_THEME", "")
if THEME == "08":   # 2026-11-16 사용자 확정: 08 (흰 #FBFBF9 · 진초록 #01422B · 딥레드 #A3161A) — 요소에만, 바탕은 무채색 어둠
    WHITE08, GREEN08, RED08 = (251, 251, 249), (1, 66, 43), (163, 22, 26)
    GREEN_L, RED_L = (72, 176, 120), (232, 66, 62)   # 어두운 화면 위 글자 · 선용 밝은 톤
    BG_TOP, BG_BOT, PANEL = (22, 24, 24), (8, 9, 9), (32, 36, 35)
    FG, MUTED, FAINT, NEUTRAL = WHITE08, (150, 160, 156), (58, 64, 62), (160, 168, 165)
    GOLD, UP, DOWN = RED_L, GREEN_L, RED_L   # 빨강 = 손해 · 경고 · 핵심 / 초록 = 기준 · 정답 (사용자 11.16)
    ON_ACCENT = WHITE08

SAFE_X = 120          # 좌우 여백
SUB_Y = 1032          # 자막 기준선(하단)


@lru_cache(maxsize=None)
def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    """weight: Regular / Medium / SemiBold / Bold / ExtraBold / Black"""
    path = FONT_DIR / f"Pretendard-{weight}.otf"
    if not path.exists():
        raise SystemExit("폰트가 없습니다. 먼저 `python tools/fetch_assets.py` 를 실행하세요.")
    return ImageFont.truetype(str(path), size)
