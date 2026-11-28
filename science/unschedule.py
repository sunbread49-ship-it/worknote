"""지식창고 예약 영상 하나를 예약 해제(비공개 유지)하기: python3 science/unschedule.py VIDEO_ID"""
import sys
from pathlib import Path
import os
os.environ["YT_CHANNEL"] = "SCIENCE"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "youtube" / "tools"))
import upload as U  # noqa: E402

vid = sys.argv[1]
t = U.access_token()
U.call("PUT", U.API + "/youtube/v3/videos?part=status", t,
       {"id": vid, "status": {"privacyStatus": "private", "publishAt": None, "selfDeclaredMadeForKids": False}})
s = U.call("GET", U.API + "/youtube/v3/videos?part=status&id=" + vid, t)["items"][0]["status"]
print(vid, s["privacyStatus"], s.get("publishAt"))
