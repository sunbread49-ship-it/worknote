"""움직이는 배경 (2026-11-11 사용자 요청: 배경은 사진 대신 영상, 저작권 문제 없게).

쓰는 법 (에디토리얼 장면의 bg):
  bg: {kind: video, file: trading_floor, dark: 0.6, blur: 14}   # assets/video/<file>.mp4 (자유 이용 영상 · 출처는 <file>.json)
  bg: {kind: motion, style: bokeh|ticker|particles, tone: navy|gold|red, dark: 0.3}   # 코드로 만든 가공 영상 (저작권 없음)
  bg: {kind: parallax, file: <사진 이름>, dark: 0.6, blur: 10}  # 자유 이용 사진을 2.5D 카메라 이동 영상으로

영상은 640x360 · 15fps로 미리 풀어 메모리에 두고(흐리게 깔 거라 충분), 끝에 닿으면 거꾸로 되돌아가며 이어 재생(핑퐁).
"""
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from .style import ROOT, W, H

VDIR = ROOT / "assets" / "video"
VW, VH, VFPS = 640, 360, 15


@lru_cache(maxsize=6)
def _frames(name, secs=14):
    src = VDIR / f"{name}.mp4"
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(src), "-t", str(secs), "-vf",
                          f"fps={VFPS},scale={VW}:{VH}:force_original_aspect_ratio=increase,crop={VW}:{VH}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, VH, VW, 3)


def credit(name):
    p = VDIR / f"{name}.json"
    return json.loads(p.read_text()).get("credit", "") if p.exists() else ""


def _grade(im, dark, blur, sat=0.75):
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Color(im).enhance(sat)
    if dark:
        im = Image.blend(im, Image.new("RGB", im.size, (6, 8, 14)), dark)
    return im


def video_at(sp, t):
    fr = _frames(sp["file"])
    n = len(fr)
    k = int(t * VFPS * sp.get("speed", 1.0)) % (2 * n - 2) if n > 1 else 0
    k = k if k < n else 2 * n - 2 - k
    im = Image.fromarray(fr[k]).resize((W, H), Image.BILINEAR)
    return _grade(im, sp.get("dark", 0.6), sp.get("blur", 12), sp.get("sat", 0.75))


TONES = {"navy": ((70, 120, 220), (255, 196, 80)), "gold": ((255, 190, 80), (255, 236, 180)), "red": ((230, 70, 70), (255, 150, 120))}


@lru_cache(maxsize=4)
def _seeds(style, n=60):
    r = np.random.default_rng({"bokeh": 3, "ticker": 5, "particles": 7, "candles": 11}.get(style, 1))
    return r.random((n, 6))


def motion_at(sp, t):
    """코드로 만든 가공 배경 영상"""
    style = sp.get("style", "bokeh")
    c1, c2 = TONES.get(sp.get("tone", "navy"), TONES["navy"])
    base = Image.new("RGB", (W // 2, H // 2), (8, 10, 18))
    d = ImageDraw.Draw(base, "RGBA")
    w, h = W // 2, H // 2
    if style == "bokeh":
        for x, y, r, sp_, ph, hue in _seeds(style, 40):
            xx = (x * w + math.sin(t * 0.3 * (0.5 + sp_) + ph * 6) * 40) % w
            yy = (y * h - t * 12 * (0.3 + sp_)) % h
            rr = 14 + r * 46
            col = c1 if hue > 0.35 else c2
            a = int(40 + 50 * (0.5 + 0.5 * math.sin(t * (0.6 + sp_) + ph * 7)))
            d.ellipse((xx - rr, yy - rr, xx + rr, yy + rr), fill=col + (a,))
        im = base.filter(ImageFilter.GaussianBlur(10))
    elif style == "ticker":  # 흐르는 주가선 여러 줄 + 격자
        for gx in range(0, w, 40):
            d.line((gx, 0, gx, h), fill=(255, 255, 255, 10))
        for i, (a0, a1, a2, sp_, ph, hue) in enumerate(_seeds(style, 7)):
            y0 = h * (0.2 + 0.1 * i)
            pts = []
            for x in range(-20, w + 20, 6):
                xx = x + t * 30 * (0.5 + sp_)
                pts.append((x, y0 + 30 * math.sin(xx / 60 + ph * 9) + 18 * math.sin(xx / 23 + a0 * 9) - (xx % 400) * 0.05 * (a1 - 0.5)))
            d.line(pts, fill=(c1 if hue > 0.4 else c2) + (90,), width=2)
        im = base.filter(ImageFilter.GaussianBlur(1.5))
    elif style == "aurora":  # 11/28: 아주 느린 빛 띠 두 개 (깜빡임 없음)
        import numpy as _np
        yy, xx = _np.mgrid[0:h, 0:w]
        f1 = _np.exp(-((yy - h * (0.35 + 0.05 * math.sin(t * 0.08))) / (h * 0.22)) ** 2) * (0.6 + 0.4 * _np.sin(xx / w * 3.1 + t * 0.05))
        f2 = _np.exp(-((yy - h * (0.78 + 0.04 * math.cos(t * 0.06))) / (h * 0.18)) ** 2) * (0.5 + 0.5 * _np.cos(xx / w * 2.3 - t * 0.04))
        arr = _np.array(base, dtype=float)
        for k in range(3):
            arr[..., k] += f1 * c1[k] * 0.28 + f2 * c2[k] * 0.12
        im = Image.fromarray(arr.clip(0, 255).astype("uint8"))
    elif style == "grid":  # 11/28: 옅은 격자 + 천천히 움직이는 스포트라이트(비네트)
        for gx in range(0, w, 32):
            d.line((gx, 0, gx, h), fill=(255, 255, 255, 9))
        for gy in range(0, h, 32):
            d.line((0, gy, w, gy), fill=(255, 255, 255, 9))
        cx, cy = w * (0.5 + 0.18 * math.sin(t * 0.07)), h * (0.42 + 0.08 * math.cos(t * 0.05))
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((cx - w * 0.45, cy - h * 0.45, cx + w * 0.45, cy + h * 0.45), fill=c1 + (38,))
        base.paste(Image.alpha_composite(base.convert("RGBA"), g.filter(ImageFilter.GaussianBlur(90))).convert("RGB"))
        im = base
    elif style == "contour":  # 11/28: 지도 등고선처럼 가는 곡선들이 아주 천천히 흐름
        for i in range(14):
            pts = []
            for x in range(-10, w + 10, 8):
                y = h * (i / 13) + 18 * math.sin(x / 90 + i * 0.7 + t * 0.12) + 10 * math.sin(x / 37 - i + t * 0.07)
                pts.append((x, y))
            d.line(pts, fill=(c1 if i % 3 else c2) + (26 if i % 3 else 34,), width=1)
        im = base.filter(ImageFilter.GaussianBlur(0.6))
    elif style == "candles":  # 11/28: 아래쪽에 아주 옅은 캔들 차트가 천천히 지나감
        r_ = _seeds("candles", 60)
        cw_ = 14
        off = (t * 10) % (cw_ * 60)
        price = h * 0.7
        for i in range(60):
            o, c_, hi, lo, _, _ = r_[i]
            p0 = price; p1 = price + (c_ - 0.5) * 30
            x = (i * cw_ - off) % (cw_ * 60) - cw_
            up = p1 < p0
            col = (c2 if up else c1) + (34,)
            d.line((x + cw_ / 2, min(p0, p1) - hi * 14, x + cw_ / 2, max(p0, p1) + lo * 14), fill=col, width=1)
            d.rectangle((x + 2, min(p0, p1), x + cw_ - 2, max(p0, p1) + 1), fill=col)
            price = min(h * 0.9, max(h * 0.5, p1))
        im = base.filter(ImageFilter.GaussianBlur(0.5))
    else:  # particles: 위로 떠오르는 작은 점
        for x, y, r, sp_, ph, hue in _seeds(style, 120):
            yy = (y * h - t * 25 * (0.2 + sp_)) % h
            xx = x * w + math.sin(t + ph * 6) * 6
            rr = 1 + r * 2.5
            d.ellipse((xx - rr, yy - rr, xx + rr, yy + rr), fill=(c2 if hue > 0.5 else c1) + (int(90 + 120 * r),))
        im = base.filter(ImageFilter.GaussianBlur(0.8))
    im = im.resize((W, H), Image.BILINEAR)
    return _grade(im, sp.get("dark", 0.0), 0, 1.0)


def parallax_at(sp, t, dur=8.0):
    from . import depth as DP
    key = (sp["file"], json.dumps(sp.get("move", {}), sort_keys=True))
    clip = _px(key)
    k = (t / dur) % 2
    k = k if k < 1 else 2 - k
    return _grade(clip.at(k).convert("RGB"), sp.get("dark", 0.6), sp.get("blur", 10))


@lru_cache(maxsize=4)
def _px(key):
    from . import depth as DP
    name, mv = key
    return DP.Parallax(name, W, H, move=json.loads(mv) or {"zoom": 0.12, "dx": 0.03})


def at(sp, t):
    kind = sp.get("kind")
    if kind == "video":
        return video_at(sp, t)
    if kind == "motion":
        return motion_at(sp, t)
    return parallax_at(sp, t)
