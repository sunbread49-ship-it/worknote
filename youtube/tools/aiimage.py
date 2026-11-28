"""AI 일러스트 만들기 (Gemini 이미지 · 2026-11-14 사용자 벤치마킹: '다채롭지만 한 장면에 한 그림' 펠트 · 점토 미니어처 디오라마)

  python tools/aiimage.py <이름> "<장면 설명(영어 권장)>" [--aspect 16:9]
     → assets/photos/<이름>.png + <이름>.json (출처: AI 생성 이미지)
  같은 이름이 있으면 다시 만들지 않음 (--force 로 다시)

키: 환경 Network secrets — generativelanguage.googleapis.com / x-goog-api-key (Gemini TTS와 같은 키)
스타일은 STYLE로 고정해 영상 전체가 한 톤으로 보이게. 글자는 넣지 않는다(모델이 엉터리 글자를 그림).
"""
import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "photos"
MODEL = "gemini-2.5-flash-image"
STYLE = ("A cozy handmade felt-and-clay miniature diorama, tiny clay figures, soft warm studio lighting, shallow depth of field, "
         "tilt-shift look, rich but harmonious colors, cinematic composition. "
         "Absolutely no text, no letters, no numbers, no writing, no logos, no signs anywhere in the image. Scene: ")


def generate(name, scene, aspect="16:9", force=False):
    out = OUT / f"{name}.png"
    if out.exists() and not force:
        return out
    body = {"contents": [{"parts": [{"text": STYLE + scene}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    for k in range(5):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            res = json.loads(urllib.request.urlopen(req, timeout=180).read())
            for p in res["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    out.write_bytes(base64.b64decode(p["inlineData"]["data"]))
                    meta = {"title": scene[:120], "license": "AI 생성 이미지 (Gemini)", "artist": "AI 생성",
                            "credit": "그림: AI 생성 (Gemini)", "file": out.name}
                    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
                    print(out)
                    return out
            raise RuntimeError("이미지 없음")
        except Exception as e:
            print("  재시도", k + 1, str(e)[:100])
            time.sleep(10 + 10 * k)
    raise SystemExit(f"실패: {name}")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    asp = sys.argv[sys.argv.index("--aspect") + 1] if "--aspect" in sys.argv else "16:9"
    if asp in a:
        a.remove(asp)
    generate(a[0], a[1], asp, "--force" in sys.argv)
