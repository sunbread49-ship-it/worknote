"""Blender 동전 탑 경주 프레임 + 2D 라벨 (색 조합 08: 흰 종이 이름표 · 진초록 날짜 · 딥레드 강조) → assets/media/<name>.mp4
  python3 tools/towers_compose.py <frames_dir> <towers.json> <name> x1 x2 x3   (x = 화면 가로 비율)
  towers.json 에 "labels": ["반도체 1배", "SOXL 몰빵", "반만 담기"] · "colors": ["ink", "red", "green"]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import draw as G, style as S  # noqa: E402

WHITE, GREEN, RED, INK = (251, 251, 249), (1, 66, 43), (163, 22, 26), (24, 28, 26)
src, D, name = Path(sys.argv[1]), json.load(open(sys.argv[2])), sys.argv[3]
xs = [float(x) for x in sys.argv[4:7]]
rows, labels = D["rows"], D["labels"]
cols = [{"ink": INK, "red": RED, "green": GREEN}[c] for c in D["colors"]]
frames = sorted(src.glob("f*.png"))
NF, hold = len(frames), 25
out = S.ROOT / "assets" / "media" / f"{name}.mp4"
W, H = 1920, 1080
SC, OY = 0.74, 40
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                      "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
T = lambda txt, sz, c, w="Black": G.text_img(txt, w, sz, c)


def tag(lab, val, c):
    t = Image.new("RGBA", (300, 100), WHITE + (255,))
    d = ImageDraw.Draw(t)
    d.rectangle((0, 0, 299, 99), outline=GREEN + (255,), width=4)
    d.rectangle((8, 8, 291, 91), outline=GREEN + (255,), width=1)
    l_, v_ = T(lab, 26, INK, "Bold"), T(f"{val:,.0f}만", 46, c)
    t.alpha_composite(l_, ((300 - l_.width) // 2, 10)); t.alpha_composite(v_, ((300 - v_.width) // 2, 40))
    sh = Image.new("RGBA", (310, 110), (0, 0, 0, 0))
    sh.alpha_composite(Image.new("RGBA", (300, 100), GREEN + (255,)), (10, 10)); sh.alpha_composite(t, (0, 0))
    return sh


for fi, fp in enumerate(frames):
    u = min(1.0, fi / (NF - hold))
    pos = u * (len(rows) - 1)
    i0 = int(pos); fr = pos - i0
    r0, r1 = rows[i0], rows[min(i0 + 1, len(rows) - 1)]
    v = [a + (b - a) * fr for a, b in zip(r0["v"], r1["v"])]
    raw = Image.open(fp).convert("RGB")
    f = raw.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(18)).convert("RGBA")   # 뒤: 흐린 확대본
    sm = raw.resize((int(W * SC), int(H * SC)), Image.BICUBIC)   # 앞: 작게 줄여 위 · 아래에 라벨 · 자막 자리
    mk = Image.new("L", sm.size, 255)
    from PIL import ImageDraw as _D
    mk = Image.new("L", sm.size, 0); _D.Draw(mk).rectangle((40, 40, sm.width - 40, sm.height - 40), fill=255)
    mk = mk.filter(ImageFilter.GaussianBlur(30))
    f.paste(sm, (int((W - sm.width) / 2), OY), mk)
    G.blit(f, G.pill(rows[min(round(pos), len(rows) - 1)]["date"].replace("-", "."), "Black", 44, WHITE, GREEN, pad=(24, 10), radius=10), (W / 2, 40), 1, "mt")
    G.blit(f, T("" + D.get("note", "1,000만 원씩 · 동전 1개 = 50만 원") + "", 30, (210, 214, 212), "Bold"), (W / 2, 122), 1, "mt")
    for x, lab, val, c in zip(xs, labels, v, cols):
        G.blit(f, tag(lab, val, c), (W * x, 740), 1, "mt")
    if fi >= NF - hold and D.get("summary"):
        k = min(1.0, (fi - (NF - hold)) / 8)
        G.blit(f, G.pill(D["summary"], "Black", 46, WHITE, RED, pad=(26, 12), radius=10), (W / 2, 176), k, "mt")
    p.stdin.write(f.convert("RGB").tobytes())
p.stdin.close(); p.wait()
print("→", out)
