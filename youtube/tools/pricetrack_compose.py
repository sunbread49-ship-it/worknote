"""주가 롤러코스터 프레임 + 2D 표시 (날짜 · 그날 주가 · 구간 알림) — 색 조합 08 → assets/media/<name>.mp4
  python3 tools/pricetrack_compose.py <frames_dir> <track.json> <name>
  track.json 의 "notes": [{"from": "2025-09-19", "to": "2025-10-10", "text": "6달 전 매수 · 3만 4,700원", "color": "green|red"}]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import draw as G, style as S  # noqa: E402

WHITE, GREEN, RED = (251, 251, 249), (1, 66, 43), (163, 22, 26)
src, D, name = Path(sys.argv[1]), json.load(open(sys.argv[2])), sys.argv[3]
frames = sorted(src.glob("f*.png"))
NF, hold = len(frames), 40
dates, prices = D["dates"], D["prices"]
out = S.ROOT / "assets" / "media" / f"{name}.mp4"
W, H = 1920, 1080
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                      "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
for fi, fp in enumerate(frames):
    u = min(1.0, fi / (NF - hold - 1))
    i = round(u * (len(dates) - 1))
    f = Image.open(fp).convert("RGB").resize((W, H), Image.BICUBIC).convert("RGBA")
    G.blit(f, G.pill(dates[i].replace("-", "."), "Black", 44, WHITE, GREEN, pad=(24, 10), radius=10), (W / 2, 40), 1, "mt")
    G.blit(f, G.text_img(f"{D.get('label', '')} {prices[i]:,.0f}원", "Black", 54, WHITE, stroke=6, stroke_fill=(0, 0, 0)), (W / 2, 128), 1, "mt")
    for nt in D.get("notes", []):
        if nt["from"] <= dates[i] <= nt["to"]:
            col = GREEN if nt["color"] == "green" else RED
            G.blit(f, G.pill(nt["text"], "Black", 50, WHITE, col, pad=(26, 12), radius=10), (W / 2, 220), 1, "mt")
    p.stdin.write(f.convert("RGB").tobytes())
p.stdin.close(); p.wait()
print("→", out)
