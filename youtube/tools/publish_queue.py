"""비공개로 올려 둔 영상을 정해진 시각에 '공개'로 전환 (예약 업로드 대신 · 사용자 11/22)
  python3 tools/publish_queue.py add <channel(stock|science)> <video_id> "2026-11-23T15:50" [메모]
  python3 tools/publish_queue.py list
  python3 tools/publish_queue.py due        # 시각이 지난 항목을 공개로 전환 (예약 작업이 30분마다 실행)
기록: publish_queue.json · 공개 전환은 videos.update(part=status) 50유닛
"""
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import upload as U  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
Q = ROOT / "publish_queue.json"


def load():
    return json.loads(Q.read_text()) if Q.exists() else []


def save(q):
    Q.write_text(json.dumps(q, ensure_ascii=False, indent=1) + "\n")


def add(channel, vid, at, note=""):
    q = load()
    if any(x["id"] == vid for x in q):
        return
    q.append({"channel": channel, "id": vid, "at": at, "note": note, "done": None})
    q.sort(key=lambda x: x["at"])
    save(q)


def publish(tok, vid):
    it = U.call("GET", f"{U.API}/youtube/v3/videos?part=status&id={vid}", tok)["items"][0]["status"]
    if it.get("privacyStatus") == "public":
        return "already"
    st = {k: it[k] for k in ("selfDeclaredMadeForKids", "containsSyntheticMedia", "license", "embeddable", "publicStatsViewable") if k in it}
    st["privacyStatus"] = "public"
    U.call("PUT", f"{U.API}/youtube/v3/videos?part=status", tok, {"id": vid, "status": st})
    return "public"


def due():
    q = load()
    now = dt.datetime.now(KST)
    todo = [x for x in q if not x["done"] and dt.datetime.fromisoformat(x["at"]).replace(tzinfo=KST) <= now + dt.timedelta(minutes=2)]
    for ch in sorted({x["channel"] for x in todo}):
        U.CHANNEL = "SCIENCE" if ch == "science" else ""
        tok = U.access_token()
        for x in [y for y in todo if y["channel"] == ch]:
            try:
                r = publish(tok, x["id"])
                x["done"] = now.isoformat(timespec="minutes")
                print(f"✔ {ch} {x['id']} {x['note']} → {r}")
            except Exception as e:
                print(f"✘ {ch} {x['id']} {x['note']} → {str(e)[:160]}")
    save(q)
    left = [x for x in q if not x["done"]]
    print(f"남은 공개 대기 {len(left)}개" + (f" · 다음 {left[0]['at']} {left[0]['note']}" if left else ""))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "add":
        add(sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
    elif cmd == "list":
        for x in load():
            print(("✔ " if x["done"] else "· ") + f"{x['at']} {x['channel']} {x['id']} {x['note']}")
    elif cmd == "due":
        due()
