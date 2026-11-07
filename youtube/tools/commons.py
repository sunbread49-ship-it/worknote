"""위키미디어 공용(자유 라이선스)에서 사진 · 로고 받아오기 + 출처 자동 기록

  python tools/commons.py search "Denny's restaurant"            # 후보 목록 (라이선스 · 작가 · 크기)
  python tools/commons.py get "File:Denny's (1822 S Las Vegas Blvd).jpg" dennys
      → assets/photos/dennys.jpg + assets/photos/dennys.json (credit 문자열 포함)

영상 장면에서는 bg: {kind: photo, file: dennys} 로 쓰고, 화면 오른쪽 위 출처에 credit 이 자동으로 붙는다.
허용 라이선스: Public domain · CC0 · CC BY · CC BY-SA (NC/ND 는 받지 않음)
로고: 상표이므로 '그 회사를 가리킬 때'만, 변형 없이, 제휴·추천처럼 보이지 않게 사용
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "photos"
UA = {"User-Agent": "JusikAkeosaeVideoTool/1.0 (https://github.com/sunbread49-ship-it/worknote) python-urllib"}
OK = ("public domain", "cc0", "cc by ", "cc by-sa", "cc-by", "pd", "cc by 2", "cc by 3", "cc by 4")


def _get(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and k < tries - 1:
                time.sleep(4 * (k + 1))
                continue
            raise


def api(**p):
    return json.loads(_get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**p, "format": "json"})))


def _clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def info(title, width=1920):
    r = api(action="query", titles=title, prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth=width)
    p = next(iter(r["query"]["pages"].values()))
    ii = p["imageinfo"][0]
    m = ii.get("extmetadata", {})
    lic = _clean(m.get("LicenseShortName", {}).get("value"))
    artist = _clean(m.get("Artist", {}).get("value")) or "Wikimedia Commons"
    url = (ii.get("thumburl") or ii["url"]).split("?")[0].replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/")
    return {"title": title, "url": url, "license": lic, "artist": artist[:60],
            "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
            "credit": f"사진: {artist[:40]}, {lic} (Wikimedia Commons)"}


def search(term, n=8):
    r = api(action="query", generator="search", gsrsearch="filetype:bitmap " + term, gsrnamespace=6, gsrlimit=n,
            prop="imageinfo", iiprop="extmetadata|size")
    out = []
    for p in (r.get("query", {}).get("pages", {}) or {}).values():
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        out.append((p["title"], _clean(m.get("LicenseShortName", {}).get("value")), _clean(m.get("Artist", {}).get("value"))[:40],
                    ii["width"], ii["height"]))
    return out


def get(title, name, width=1920):
    OUT.mkdir(parents=True, exist_ok=True)
    meta = info(title, width)
    if not any(k in meta["license"].lower() for k in OK) or "nc" in meta["license"].lower().split("-"):
        raise SystemExit(f"허용되지 않는 라이선스: {meta['license']}")
    ext = Path(urllib.parse.urlparse(meta["url"]).path).suffix.lower() or ".jpg"
    dst = OUT / f"{name}{ext}"
    dst.write_bytes(_get(meta["url"]))
    (OUT / f"{name}.json").write_text(json.dumps({**meta, "file": dst.name}, ensure_ascii=False, indent=2))
    return dst, meta


def load(name):
    """name → (PIL 이미지 경로, credit)"""
    meta = json.loads((OUT / f"{name}.json").read_text())
    return OUT / meta["file"], meta["credit"]


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for row in search(sys.argv[2]):
            print(" | ".join(map(str, row)))
    elif sys.argv[1] == "get":
        p, m = get(sys.argv[2], sys.argv[3])
        print(p, "·", m["credit"])
