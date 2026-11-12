"""Pixabay 사진 · 영상 받기 (Pixabay 콘텐츠 라이선스: 상업적 이용 · 수정 가능, 출처 표기 의무 없음 — 그래도 설명란에 표기)
키: 환경 변수 PIXABAY_API_KEY (클라우드 환경 → 편집 → 환경 변수, 새 세션부터 적용) — 키 값은 절대 출력하지 않는다

  python tools/pixabay.py search "stock market crash"            # 사진
  python tools/pixabay.py search "stock market crash" --video    # 영상
  python tools/pixabay.py get <id> <이름>            → assets/photos/<이름>.jpg + .json
  python tools/pixabay.py get <id> <이름> --video    → assets/video/<이름>.mp4 + .json (bgvideo 배경용)
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "JusikAkeosaeVideoTool/1.0 python-urllib"}


def _key():
    k = os.environ.get("PIXABAY_API_KEY")
    if not k:
        raise SystemExit("PIXABAY_API_KEY 환경 변수가 없습니다 (환경 편집 후 새 세션에서 실행)")
    return k


def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def search(q, video=False, n=12):
    base = "https://pixabay.com/api/videos/" if video else "https://pixabay.com/api/"
    d = json.loads(_get(base + "?" + urllib.parse.urlencode({"key": _key(), "q": q, "per_page": n, "safesearch": "true"})))
    rows = []
    for h in d.get("hits", []):
        if video:
            v = h["videos"].get("large") or h["videos"].get("medium")
            rows.append((h["id"], h.get("duration"), f"{v.get('width')}x{v.get('height')}", h.get("tags", "")[:60], h.get("user")))
        else:
            rows.append((h["id"], f"{h.get('imageWidth')}x{h.get('imageHeight')}", h.get("tags", "")[:60], h.get("user")))
    return rows


def get(pid, name, video=False):
    base = "https://pixabay.com/api/videos/" if video else "https://pixabay.com/api/"
    d = json.loads(_get(base + "?" + urllib.parse.urlencode({"key": _key(), "id": pid})))
    h = d["hits"][0]
    if video:
        v = h["videos"].get("large") or h["videos"].get("medium")
        out = ROOT / "assets" / "video" / f"{name}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(_get(v["url"]))
    else:
        out = ROOT / "assets" / "photos" / f"{name}.jpg"
        out.write_bytes(_get(h.get("largeImageURL") or h["webformatURL"]))
    meta = {"title": h.get("tags"), "page": h.get("pageURL"), "license": "Pixabay Content License", "artist": h.get("user"),
            "credit": f"{'영상' if video else '사진'}: {h.get('user')}, Pixabay", "file": out.name}
    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(out, "·", meta["credit"])


if __name__ == "__main__":
    vid = "--video" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--video"]
    if args[0] == "search":
        for r in search(args[1], vid):
            print(" | ".join(str(x) for x in r))
    else:
        get(args[1], args[2], vid)
