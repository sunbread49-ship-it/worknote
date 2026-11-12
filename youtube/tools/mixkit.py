"""Mixkit 무료 효과음 (키 필요 없음) — 라이선스: https://mixkit.co/license/#sfxFree (영상에 무료 사용, 효과음 파일 자체 재배포만 금지)

  python tools/mixkit.py list whoosh              # https://mixkit.co/free-sound-effects/whoosh/ 목록 (id · 제목)
  python tools/mixkit.py get 1489 [1492 ...]      → assets/sfx/mx_1489.mp3 + mx_1489.json
장면 yaml/코드에서는 효과음 이름을 "mx:1489" 처럼 쓴다 (engine/sfx.py 가 파일을 읽음).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sfx"
UA = {"User-Agent": "Mozilla/5.0 (JusikAkeosaeVideoTool)"}


def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def listing(cat):
    s = _get(f"https://mixkit.co/free-sound-effects/{cat}/").decode("utf-8", "ignore")
    rows, seen = [], set()
    for m in re.finditer(r'item-grid-card__title[^>]*>\s*([^<]+)<', s):
        tail = s[m.end(): m.end() + 6000]
        u = re.search(r'sfx/(\d+)/\1-preview\.mp3', tail)
        if u and u.group(1) not in seen:
            seen.add(u.group(1))
            rows.append((u.group(1), m.group(1).strip()))
    return rows


def get(i, title=""):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"mx_{i}.mp3").write_bytes(_get(f"https://assets.mixkit.co/active_storage/sfx/{i}/{i}-preview.mp3"))
    meta = {"id": i, "title": title, "source": "Mixkit", "license": "Mixkit Sound Effects Free License",
            "page": "https://mixkit.co/free-sound-effects/", "credit": "효과음: Mixkit"}
    (OUT / f"mx_{i}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(OUT / f"mx_{i}.mp3", title)


if __name__ == "__main__":
    if sys.argv[1] == "list":
        for i, t in listing(sys.argv[2]):
            print(i, "|", t)
    else:
        for i in sys.argv[2:]:
            get(i)
