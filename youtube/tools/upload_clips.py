"""구간 쇼츠 업로드 (롱폼 1편 = 쇼츠 9개)
  python3 tools/upload_clips.py <에피소드> <쇼츠번호들 예: 1,2,3> --channel science --start "2026-11-21T20:20" --every 20
  · 공개 시각 = start + (k × every분) · 이미 지났으면 지금 + 5분부터 다시 계산 · 표지(cN_cover.jpg)를 썸네일로 · uploads.json 기록
설명 · 제목은 out/<ep>/clips/cN.txt (첫 줄 = 제목, 나머지 = 설명)
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import upload as U  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
ap = argparse.ArgumentParser()
ap.add_argument("ep"); ap.add_argument("nums"); ap.add_argument("--channel", default="")
ap.add_argument("--start"); ap.add_argument("--every", type=int, default=30)
a = ap.parse_args()
U.CHANNEL = a.channel.upper()
od = ROOT / "out" / a.ep / "clips"
t0 = dt.datetime.fromisoformat(a.start).replace(tzinfo=KST)
now = dt.datetime.now(KST)
if t0 < now + dt.timedelta(minutes=4):
    t0 = (now + dt.timedelta(minutes=6)).replace(second=0, microsecond=0)
tok = U.access_token()
log = json.loads((ROOT / "uploads.json").read_text())
rec = log.setdefault(("science" if a.channel == "science" else a.ep) if a.channel == "science" else a.ep, {})
for k, n in enumerate(int(x) for x in a.nums.split(",")):
    lines = (od / f"c{n}.txt").read_text(encoding="utf-8").split("\n", 1)
    when = t0 + dt.timedelta(minutes=a.every * k)
    vid, pv = U.upload_video(tok, od / f"c{n}.mp4", lines[0].strip(), lines[1].strip(), [], when)
    try:
        U.set_thumbnail(tok, vid, od / f"c{n}_cover.jpg")
    except Exception as e:
        print("  표지 실패:", str(e)[:80])
    key = f"{a.ep}_clip{n}" if a.channel == "science" else f"clip{n}"
    rec[key] = {"id": vid, "title": lines[0].strip(), "publish_at": when.isoformat()}
    (ROOT / "uploads.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))
    print(f"  ✔ 쇼츠 {n} → https://youtu.be/{vid} · 공개 {when.strftime('%H:%M')}")
