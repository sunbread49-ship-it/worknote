"""사진에 깊이감 입히기 (2.5D 패럴랙스) — 무료 · CPU만으로.

1) Depth Anything V2 (small, ONNX)로 사진의 깊이 지도 추정 → assets/photos/<이름>.depth.png 캐시
2) 카메라를 조금씩 움직이며(줌 · 좌우 · 위아래) 가까운 곳은 많이, 먼 곳은 적게 움직여 입체감
   모델: https://github.com/fabio-sim/Depth-Anything-ONNX (Apache-2.0, small 모델) → ~/.depth/da2_vits.onnx

사용:
  from engine import depth as DP
  clip = DP.Parallax("alex_library", 1920, 1080, move={"zoom": 0.08, "dx": 0.03, "dy": -0.01})
  frame = clip.at(k)   # k = 0~1 진행
"""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from .style import ROOT

PHOTOS = ROOT / "assets" / "photos"
MODEL = Path.home() / ".depth" / "da2_vits.onnx"
MODEL_URL = "https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/depth_anything_v2_vits.onnx"


def _ensure_model():
    if not MODEL.exists():
        import urllib.request
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    return MODEL


@lru_cache(maxsize=1)
def _session():
    import onnxruntime as ort
    return ort.InferenceSession(str(_ensure_model()), providers=["CPUExecutionProvider"])


def estimate(img: Image.Image) -> np.ndarray:
    """가까울수록 1, 멀수록 0 (float32, 이미지 크기)"""
    s = 518
    x = np.asarray(img.convert("RGB").resize((s, s), Image.BICUBIC), np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    d = _session().run(None, {_session().get_inputs()[0].name: x})[0][0]
    d = (d - d.min()) / (d.max() - d.min() + 1e-9)
    im = Image.fromarray((d * 255).astype(np.uint8), "L").resize(img.size, Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


def photo_path(name):
    m = json.loads((PHOTOS / f"{name}.json").read_text()) if (PHOTOS / f"{name}.json").exists() else {"file": name}
    return PHOTOS / m["file"]


def depth_of(name, img=None):
    cache = PHOTOS / f"{name}.depth.png"
    if cache.exists():
        return np.asarray(Image.open(cache), np.float32) / 255
    img = img or Image.open(photo_path(name)).convert("RGB")
    d = estimate(img)
    Image.fromarray((d * 255).astype(np.uint8), "L").save(cache)
    return d


class Parallax:
    """사진 한 장 → 카메라가 천천히 움직이는 입체 클립.
    move: zoom(앞으로 다가가기 비율), dx/dy(카메라 이동, 화면 비율), focus(크롭 중심), strength(입체 세기),
          ease(True면 부드럽게 가속·감속)"""

    def __init__(self, name, w, h, move=None, focus=(0.5, 0.5), grade=None, margin=1.12):
        import cv2  # noqa: F401  (없으면 pip install opencv-python-headless)
        self.w, self.h = w, h
        mv = {"zoom": 0.08, "dx": 0.025, "dy": 0.0, "strength": 1.0, "ease": True}
        mv.update(move or {})
        self.mv = mv
        src = Image.open(photo_path(name)).convert("RGB")
        dep = depth_of(name, src)
        # 여유 있게 크롭(움직일 공간) → 작업 해상도
        W, H = int(w * margin), int(h * margin)
        sc = max(W / src.width, H / src.height)
        sw, sh = int(src.width * sc) + 1, int(src.height * sc) + 1
        x0, y0 = int((sw - W) * focus[0]), int((sh - H) * focus[1])
        self._geo = (src.width, src.height, sc, x0, y0)
        img = src.resize((sw, sh), Image.LANCZOS).crop((x0, y0, x0 + W, y0 + H))
        if grade:
            img = grade(img)
        d = Image.fromarray((dep * 255).astype(np.uint8), "L").resize((sw, sh), Image.BICUBIC).crop((x0, y0, x0 + W, y0 + H))
        d = d.filter(ImageFilter.GaussianBlur(6))  # 경계가 찢어지지 않게 부드럽게
        self.img = np.asarray(img.convert("RGB"))
        self.dep = np.asarray(d, np.float32) / 255
        self.W, self.H = W, H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.xx, self.yy = xx, yy

    def project(self, fx, fy, k):
        """원본 사진의 비율 좌표(fx, fy) → 진행 k일 때 화면 좌표 (지시 표시용)"""
        sw0, sh0, sc, x0, y0 = self._geo
        x, y = fx * sw0 * sc - x0, fy * sh0 * sc - y0
        mv = self.mv
        k = float(np.clip(k, 0, 1))
        if mv.get("ease", True):
            k = k * k * (3 - 2 * k)
        st = mv.get("strength", 1.0)
        d = float(self.dep[int(np.clip(y, 0, self.H - 1)), int(np.clip(x, 0, self.W - 1))])
        z = 1 + mv["zoom"] * k
        dz = 1 + (z - 1) * (0.35 + 0.65 * d * st)
        sx = mv["dx"] * k * self.W * (0.25 + 0.75 * d * st)
        sy = mv["dy"] * k * self.H * (0.25 + 0.75 * d * st)
        cx, cy = self.W / 2, self.H / 2
        X, Y = (x + sx - cx) * dz + cx, (y + sy - cy) * dz + cy
        return X - (self.W - self.w) // 2, Y - (self.H - self.h) // 2

    def at(self, k):
        import cv2
        mv = self.mv
        k = float(np.clip(k, 0, 1))
        if mv.get("ease", True):
            k = k * k * (3 - 2 * k)
        st = mv.get("strength", 1.0)
        z = 1 + mv["zoom"] * k                    # 가까운 곳일수록 더 많이 확대
        cx, cy = self.W / 2, self.H / 2
        dz = 1 + (z - 1) * (0.35 + 0.65 * self.dep * st)
        sx = mv["dx"] * k * self.W * (0.25 + 0.75 * self.dep * st)
        sy = mv["dy"] * k * self.H * (0.25 + 0.75 * self.dep * st)
        mx = (self.xx - cx) / dz + cx - sx
        my = (self.yy - cy) / dz + cy - sy
        out = cv2.remap(self.img, mx, my, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # 가운데 w×h 잘라내기
        ox, oy = (self.W - self.w) // 2, (self.H - self.h) // 2
        return Image.fromarray(out[oy:oy + self.h, ox:ox + self.w]).convert("RGBA")
