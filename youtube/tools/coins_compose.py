"""Blender 동전 탑 프레임 + 2D 라벨(월 · 금액 세기) → assets/media/<name>.mp4 (EP017)
  python3 tools/coins_compose.py /tmp/coins_frames /tmp/coins.json coins_ep017 [xl xr xd]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import draw as G, style as S  # noqa: E402

src, data, name = Path(sys.argv[1]), json.load(open(sys.argv[2])), sys.argv[3]
xs = [float(x) for x in sys.argv[4:7]] if len(sys.argv) > 6 else [0.30, 0.58, 0.75]
frames = sorted(src.glob("f*.png"))
NF, hold = len(frames), 25
out = S.ROOT / "assets" / "media" / f"{name}.mp4"
out.parent.mkdir(exist_ok=True)
W, H = 1920, 1080
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                      "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
T = lambda txt, sz, c=(255, 255, 255), w="Black": G.text_img(txt, w, sz, c)
for fi, fp in enumerate(frames):
    u = min(1.0, fi / (NF - hold))
    pos = u * (len(data) - 1)
    i0 = int(pos); fr = pos - i0
    r0, r1 = data[i0], data[min(i0 + 1, len(data) - 1)]
    v = {k: r0[k] + (r1[k] - r0[k]) * fr for k in ("idx", "cc", "div")}
    f = Image.open(fp).convert("RGB").resize((W, H), Image.BICUBIC).convert("RGBA")
    G.blit(f, G.pill(data[min(round(pos), len(data) - 1)]["date"].replace("-", "."), "Black", 44, (14, 16, 24), S.GOLD, pad=(22, 10), radius=14), (W / 2, 40), 1, "mt")
    G.blit(f, T("1,000만 원 · 동전 1개 = 50만 원", 30, (200, 206, 220), "Bold"), (W / 2, 120), 1, "mt")
    for x, lab, val, c in ((xs[0], "그냥 나스닥100", v["idx"], (230, 232, 240)), (xs[1], "커버드콜 원금", v["cc"], (230, 232, 240)),
                           (xs[2], "분배금(세후)", v["div"], S.GOLD)):
        tag = Image.new("RGBA", (300, 118), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(tag).rounded_rectangle((0, 0, 299, 117), 18, fill=(10, 12, 20, 200))
        l_, v_ = T(lab, 32, c, "Bold"), T(f"{val:,.0f}만", 54, c)
        tag.alpha_composite(l_, ((300 - l_.width) // 2, 8)); tag.alpha_composite(v_, ((300 - v_.width) // 2, 46))
        G.blit(f, tag, (W * x, H - 330), 1, "mt")
    if fi >= NF - hold:
        k = min(1.0, (fi - (NF - hold)) / 8)
        G.blit(f, G.pill(f"커버드콜 합계 {v['cc'] + v['div']:,.0f}만  vs  나스닥 {v['idx']:,.0f}만", "Black", 46, (14, 16, 24), (255, 255, 255), pad=(26, 12), radius=16), (W / 2, 180), k, "mt")
    p.stdin.write(f.convert("RGB").tobytes())
p.stdin.close(); p.wait()
print("→", out)
