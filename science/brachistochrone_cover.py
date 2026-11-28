"""쇼츠 커버 (1080x1920): 경주 장면 + 큰 질문"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brachistochrone as B
from engine import draw as G
from PIL import Image

f = B.BG.copy()
B.race_frame(f, 0.62)
G.blit(f, B.T("공 3개 경주", 44, B.MINT, "ExtraBold"), (B.W / 2, 200), 1, "mt")
G.blit(f, B.T("직선이\n꼴찌라고?", 150, B.CREAM, "Black", highlight="꼴찌라고?", hl_fill=B.CORAL, align="center", line_gap=1.08, stroke=6, stroke_fill=(0, 0, 0)), (B.W / 2, 260), 1, "mt")
G.blit(f, B.T("가장 짧은 길 ≠ 가장 빠른 길", 50, B.CREAM, "ExtraBold"), (B.W / 2, 1330), 1, "mt")
f.convert("RGB").save(B.OUT / "cover.png")
print("커버 →", B.OUT / "cover.png")
