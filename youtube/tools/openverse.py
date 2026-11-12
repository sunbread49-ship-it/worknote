"""Openverse(플리커 · 위키미디어 등 CC 이미지 모음)에서 자유 이용 사진 받기 + 출처 자동 기록

  python tools/openverse.py search "battery fire"            # 상업적 이용 · 수정 가능한 라이선스만
  python tools/openverse.py get <openverse_id> <이름>        → assets/photos/<이름>.jpg + .json (credit)
허용: CC0 · PDM · CC BY · CC BY-SA (NC/ND 제외) — 썸네일은 '수정'이 들어가므로 modification 허용만
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "photos"
UA = {"User-Agent": "JusikAkeosaeVideoTool/1.0 (https://github.com/sunbread49-ship-it/worknote) python-urllib"}
API = "https://api.openverse.org/v1/images/"


CACHE = ROOT / "out" / "openverse_cache.json"  # 검색 결과 기억 (상세 API가 자주 시간 초과라 검색 결과로 받음)


def _get(url, tries=4):
    import time
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception:  # noqa: BLE001
            if k == tries - 1:
                raise
            time.sleep(5 * (k + 1))


def search(q, n=12):
    u = API + "?" + urllib.parse.urlencode({"q": q, "license_type": "commercial,modification", "page_size": n})
    d = json.loads(_get(u))
    c = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    c.update({r["id"]: r for r in d["results"]})
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(c, ensure_ascii=False))
    return [(r["id"], r["source"], r["license"], r.get("width"), r.get("height"), (r.get("title") or "")[:50]) for r in d["results"]]


def get(oid, name):
    c = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    r = c.get(oid) or json.loads(_get(API + oid + "/"))
    lic = r["license"].lower()
    if lic in ("by-nc", "by-nd", "by-nc-sa", "by-nc-nd", "nc-sampling+"):
        raise SystemExit(f"라이선스 불가: {lic}")
    OUT.mkdir(parents=True, exist_ok=True)
    ext = ".jpg"
    (OUT / f"{name}{ext}").write_bytes(_get(r["url"]))
    lic_name = {"pdm": "Public domain", "cc0": "CC0"}.get(lic, f"CC {lic.upper()} {r.get('license_version', '')}".strip())
    creator = r.get("creator") or "작자 미상"
    meta = {"title": r.get("title"), "url": r["url"], "license": lic_name, "artist": creator, "page": r.get("foreign_landing_url"),
            "source": r.get("source"), "credit": f"사진: {creator}, {lic_name} ({r.get('source', '').capitalize()})", "file": f"{name}{ext}"}
    (OUT / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(OUT / f"{name}{ext}", "·", meta["credit"])


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for row in search(sys.argv[2]):
            print(" | ".join(str(x) for x in row))
    else:
        get(sys.argv[2], sys.argv[3])
