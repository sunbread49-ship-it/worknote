"""위키미디어 공용에서 자유 이용 영상 받아 배경용 클립으로 만들기 (요청 제한 429에 강하게: 천천히 재시도).

  python tools/commons_video.py search "stock exchange"
  python tools/commons_video.py get "File:XXX.webm" trading_floor [시작초] [길이초]
      → assets/video/trading_floor.mp4 (1280x720, 소리 없음) + .json(출처)
허용 라이선스: Public domain · CC0 · CC BY · CC BY-SA
"""
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "video"
UA = {"User-Agent": "JusikAkeosaeVideoTool/1.0 (https://github.com/sunbread49-ship-it/worknote) python-urllib"}


def api(**kw):
    kw["format"] = "json"
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(kw)
    for k in range(8):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(20 * (k + 1))
    raise SystemExit("429 계속 — 나중에 다시")


def search(q, n=10):
    r = api(action="query", generator="search", gsrsearch="filetype:video " + q, gsrnamespace=6, gsrlimit=n,
            prop="imageinfo", iiprop="url|size|extmetadata", iiextmetadatafilter="LicenseShortName|Artist")
    rows = []
    for p in (r.get("query", {}).get("pages", {}) or {}).values():
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        rows.append((p["title"], m.get("LicenseShortName", {}).get("value", ""), ii.get("width"), ii.get("height"),
                     round(ii.get("duration", 0) or 0)))
    return rows


def get(title, name, ss=0, dur=14):
    import re
    r = api(action="query", titles=title, prop="imageinfo", iiprop="url|extmetadata", iiextmetadatafilter="LicenseShortName|Artist")
    p = next(iter(r["query"]["pages"].values()))
    ii = p["imageinfo"][0]
    lic = ii["extmetadata"].get("LicenseShortName", {}).get("value", "")
    if not any(k in lic.lower() for k in ("public domain", "cc0", "cc by", "pd")) or "nc" in lic.lower() or "nd" in lic.lower():
        raise SystemExit(f"라이선스 불가: {lic}")
    artist = re.sub(r"<[^>]+>", "", ii["extmetadata"].get("Artist", {}).get("value", "")).strip()
    OUT.mkdir(parents=True, exist_ok=True)
    src = OUT / f"{name}.src"
    req = urllib.request.Request(ii["url"], headers=UA)
    src.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", str(src), "-an",
                    "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", "-c:v", "libx264",
                    "-crf", "22", "-pix_fmt", "yuv420p", str(OUT / f"{name}.mp4")], check=True)
    src.unlink()
    meta = {"title": title, "license": lic, "artist": artist, "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title),
            "credit": f"영상: {artist}, {lic} (Wikimedia Commons)"}
    (OUT / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(OUT / f"{name}.mp4", "·", meta["credit"])


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for row in search(sys.argv[2]):
            print(" | ".join(str(x) for x in row))
    else:
        get(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 0, float(sys.argv[5]) if len(sys.argv) > 5 else 14)
