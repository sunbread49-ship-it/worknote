"""Unsplash 사진 받기 (Unsplash License: 상업적 이용 · 수정 가능 — API 규칙상 작가 · Unsplash 표기, 다운로드 시 download 엔드포인트 호출)
키: 환경 변수 UNSPLASH_ACCESS_KEY (클라우드 환경 → 편집 → 환경 변수, 새 세션부터 적용) — 키 값은 절대 출력하지 않는다

  python tools/unsplash.py search "stock market"
  python tools/unsplash.py get <id> <이름>      → assets/photos/<이름>.jpg + .json
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _req(url, raw=False):
    k = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not k:
        raise SystemExit("UNSPLASH_ACCESS_KEY 환경 변수가 없습니다 (환경 편집 후 새 세션에서 실행)")
    r = urllib.request.Request(url, headers={"Authorization": f"Client-ID {k}", "Accept-Version": "v1"})
    b = urllib.request.urlopen(r, timeout=60).read()
    return b if raw else json.loads(b)


def search(q, n=12):
    d = _req("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode({"query": q, "per_page": n}))
    return [(p["id"], f"{p['width']}x{p['height']}", (p.get("alt_description") or "")[:60], p["user"]["name"]) for p in d["results"]]


def get(pid, name):
    p = _req(f"https://api.unsplash.com/photos/{pid}")
    _req(p["links"]["download_location"])          # API 규칙: 다운로드 집계
    img = urllib.request.urlopen(p["urls"]["full"] + "&w=2400", timeout=120).read()
    out = ROOT / "assets" / "photos" / f"{name}.jpg"
    out.write_bytes(img)
    meta = {"title": p.get("alt_description"), "page": p["links"]["html"], "license": "Unsplash License",
            "artist": p["user"]["name"], "credit": f"사진: {p['user']['name']}, Unsplash", "file": out.name}
    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(out, "·", meta["credit"])


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for r in search(sys.argv[2]):
            print(" | ".join(str(x) for x in r))
    else:
        get(sys.argv[2], sys.argv[3])
