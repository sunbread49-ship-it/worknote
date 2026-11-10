"""쇼츠 → 롱폼 연결: 쇼츠 설명란 맨 위에 롱폼 링크 + 채널 댓글(링크) 달기.

  python tools/link_shorts.py            # 전체 (이미 연결된 건 건너뜀)
  python tools/link_shorts.py --dry-run

고정(핀)은 API로 안 되므로 스튜디오에서 직접. 비공개 · 예약 영상은 댓글이 안 달려서 설명란만 바꾸고, 공개 후 다시 실행하면 댓글을 단다.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upload as U  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# 롱폼 id → 쇼츠 id (EP001은 롱폼 없음, EP009는 비공개 보류라 제외)
MAP = {
    "Gb3quRi94Tc": ["ScyZvTcxg2A", "74Zd8APD9jI", "V1aVIvMesNA"],   # EP002 TQQQ
    "KBMQw7_aHFk": ["BHt-_2LdqbE", "9cw0VRKGHh0", "Z9jhGkgl2YQ"],   # EP003 중간선거
    "fOkegCj4T9Q": ["8xlWHAl2JuQ", "2X5Yy77lqls", "mZBPHJhOurM"],   # EP004 템플턴 · VIX
    "edqx5gJGJ48": ["i9jl-UgNUO0", "niOCAbWHzMk", "3IlCFb5nhRA"],   # EP005 나스닥 폭락
}
for ep, v in json.loads((ROOT / "uploads.json").read_text()).items():
    if not isinstance(v, dict) or not v.get("long", {}).get("id") or ep.startswith("ep009"):
        continue
    shorts = [v[k]["id"] for k in sorted(v) if k.startswith("short") and v[k].get("id")]
    if shorts:
        MAP[v["long"]["id"]] = shorts

MARK = "▶ 전체 영상"
LOG = ROOT / "link_shorts.json"  # git에 커밋 (댓글 중복 방지)


def main(dry=False):
    t = U.access_token()
    done = json.loads(LOG.read_text()) if LOG.exists() else {}
    longs = U.call("GET", U.API + "/youtube/v3/videos?part=snippet,contentDetails&id=" + ",".join(MAP), t)["items"]
    meta = {i["id"]: i for i in longs}
    for lid, sids in MAP.items():
        lt = meta[lid]["snippet"]["title"]
        dur = meta[lid]["contentDetails"]["duration"].replace("PT", "").split("M")[0]
        line = f"{MARK}({dur}분): {lt}\nhttps://youtu.be/{lid}"
        items = U.call("GET", U.API + "/youtube/v3/videos?part=snippet,status&id=" + ",".join(sids), t)["items"]
        for it in items:
            sid, sn, st = it["id"], it["snippet"], it["status"]["privacyStatus"]
            rec = done.setdefault(sid, {})
            if MARK not in sn.get("description", ""):
                body = {"id": sid, "snippet": {"title": sn["title"], "description": line + "\n\n" + sn.get("description", ""),
                                               "categoryId": sn["categoryId"], "tags": sn.get("tags", []),
                                               "defaultLanguage": sn.get("defaultLanguage", "ko"),
                                               "defaultAudioLanguage": sn.get("defaultAudioLanguage", "ko")}}
                if not dry:
                    U.call("PUT", U.API + "/youtube/v3/videos?part=snippet", t, body)
                rec["desc"] = True
                print(f"설명란 ✔ {sid} → {lid}")
            if not rec.get("comment"):
                if st != "public":
                    print(f"댓글 보류(공개 전) {sid}")
                    continue
                c = {"snippet": {"videoId": sid, "topLevelComment": {"snippet": {"textOriginal": line}}}}
                if not dry:
                    try:
                        r = U.call("POST", U.API + "/youtube/v3/commentThreads?part=snippet", t, c)
                        rec["comment"] = r["id"]
                        print(f"댓글 ✔ {sid}")
                    except Exception as e:  # noqa: BLE001
                        print(f"댓글 실패 {sid}: {str(e)[:160]}")
    if not dry:
        LOG.parent.mkdir(exist_ok=True)
        LOG.write_text(json.dumps(done, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
