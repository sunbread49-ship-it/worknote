"""YouTube 자동 업로드 (YouTube Data API v3, 표준 라이브러리만 사용).

  python tools/upload.py episodes/ep004_templeton_vix --dry-run                 # 무엇을 올릴지 미리 보기
  python tools/upload.py episodes/ep004_templeton_vix --long                    # 롱폼만 (비공개)
  python tools/upload.py episodes/ep004_templeton_vix --shorts 1,2,3            # 쇼츠만
  python tools/upload.py episodes/ep004_templeton_vix --long --shorts 1,2,3 \\
        --publish-at 2026-11-10T18:00 --shorts-every 1d                         # 예약 공개 (롱폼 18시, 쇼츠는 다음 날부터 하루 1개)
  python tools/upload.py --check                                                # 인증·채널 확인

필요한 환경 변수 (클라우드 환경 설정 → 환경 변수):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

업로드 내용
  롱폼: out/<ep>/video.mp4 + 제목·설명(설명란.txt 기준, 챕터 포함) + 태그 + 대표 썸네일 + 한국어 자막(captions.srt)
  쇼츠: out/<ep>/shorts/shortN.mp4 + episode.yaml shorts[N].yt_title / yt_desc
  결과는 youtube/uploads.json 에 기록(커밋할 것) → 같은 파일을 두 번 올리지 않음
  --publish-at next → 다음 빈 화·금·토 18:00 KST 롱폼, 쇼츠는 다음 날부터 하루 1개

주의
  - API 프로젝트가 YouTube 감사(audit)를 통과하기 전에는 업로드 영상이 '비공개'로 잠긴다.
    그 전에는 예약 공개(publishAt)도 적용되지 않으므로, 스튜디오에서 공개로 바꿔야 한다.
  - 하루 기본 할당량 10,000: 업로드 1건 1,600 · 썸네일 50 · 자막 400 → 하루 롱폼 1 + 쇼츠 3 정도가 안전
"""
import argparse
import datetime as dt
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
KST = dt.timezone(dt.timedelta(hours=9))
API = "https://www.googleapis.com"


# ── 인증 ─────────────────────────────────────────────────────────
CHANNEL = os.environ.get("YT_CHANNEL", "")  # "" = 주식 악어새, "SCIENCE" = 악어새 지식창고 (--channel science)


def access_token():
    rt = "YT_REFRESH_TOKEN" + (f"_{CHANNEL}" if CHANNEL else "")
    need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", rt]
    miss = [k for k in need if not os.environ.get(k)]
    if miss:
        raise SystemExit(f"환경 변수가 없습니다: {', '.join(miss)} (youtube/UPLOAD_SETUP.md 참고)")
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ[rt], "grant_type": "refresh_token"}).encode()
    try:
        with urllib.request.urlopen("https://oauth2.googleapis.com/token", body, timeout=30) as r:
            return json.loads(r.read())["access_token"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"토큰 발급 실패 {e.code}: {e.read().decode()[:300]}\n"
                         "→ 리프레시 토큰이 만료됐을 수 있습니다(동의 화면이 '테스트' 상태면 7일 만료). UPLOAD_SETUP.md 4단계 참고")


def call(method, url, token, data=None, headers=None, raw=False):
    h = {"Authorization": f"Bearer {token}"}
    if headers:
        h.update(headers)
    if data is not None and not isinstance(data, (bytes, bytearray)):
        data = json.dumps(data).encode()
        h.setdefault("Content-Type", "application/json; charset=UTF-8")
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r if raw else (json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:600]
        if "quotaExceeded" in msg or "uploadLimitExceeded" in msg:
            raise SystemExit("오늘 업로드 한도를 넘었습니다. 내일 다시 실행하세요.\n" + msg)
        raise RuntimeError(f"{method} {url.split('?')[0]} → {e.code}: {msg}")


# ── 업로드 동작 ───────────────────────────────────────────────────
def upload_video(token, path, title, desc, tags, publish_at=None, category="27"):
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}
    if publish_at:
        status["publishAt"] = publish_at.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    meta = {"snippet": {"title": title[:100], "description": desc[:5000], "tags": tags[:30], "categoryId": category,
                        "defaultLanguage": "ko", "defaultAudioLanguage": "ko"}, "status": status}
    size = Path(path).stat().st_size
    r = call("POST", f"{API}/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", token, meta,
             {"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}, raw=True)
    loc = r.headers["Location"]
    with open(path, "rb") as fp:
        res = call("PUT", loc, token, fp.read(), {"Content-Type": "video/mp4"})
    return res["id"], res.get("status", {}).get("privacyStatus")


def set_thumbnail(token, vid, img):
    data = Path(img).read_bytes()
    call("POST", f"{API}/upload/youtube/v3/thumbnails/set?videoId={vid}", token, data,
         {"Content-Type": mimetypes.guess_type(str(img))[0] or "image/png"})


def add_captions(token, vid, srt, name="한국어"):
    b = uuid.uuid4().hex
    meta = json.dumps({"snippet": {"videoId": vid, "language": "ko", "name": name, "isDraft": False}}).encode()
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n").encode() + meta + \
           (f"\r\n--{b}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + Path(srt).read_bytes() + \
           f"\r\n--{b}--".encode()
    call("POST", f"{API}/upload/youtube/v3/captions?uploadType=multipart&part=snippet", token, body,
         {"Content-Type": f"multipart/related; boundary={b}"})


def add_to_playlist(token, vid, playlist_id):
    call("POST", f"{API}/youtube/v3/playlistItems?part=snippet", token,
         {"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": vid}}})


# ── 에피소드 → 업로드 목록 ─────────────────────────────────────────
def plan(ep_dir, want_long, want_shorts, publish_at, shorts_every):
    import render
    ep, channel = render.load(ep_dir)
    out = ROOT / "out" / ep_dir.name
    yt = ep.get("youtube", {})
    items = []
    if want_long:
        desc_file = out / "설명란.txt"
        if desc_file.exists():  # 첫 줄은 제목, 나머지가 설명(챕터 포함)
            title, _, desc = desc_file.read_text(encoding="utf-8").partition("\n")
            desc = desc.strip()
        else:
            title, desc = yt.get("title", ep.get("title", "")), yt.get("description", "")
        thumb = out / "thumbnail_pick.png"
        if not thumb.exists():
            thumb = out / "thumbnail.png"
        items.append({"key": "long", "file": out / "video.mp4", "title": title.strip(), "desc": desc,
                      "tags": yt.get("tags", []), "thumb": thumb, "srt": out / "captions.srt",
                      "publish_at": publish_at, "playlist": yt.get("playlist")})
    for n in want_shorts:
        sh = ep["shorts"][n - 1]
        when = None
        if publish_at:
            when = publish_at + shorts_every * len([i for i in items if i["key"].startswith("short")]) + \
                (shorts_every if want_long else dt.timedelta(0))
        desc = sh.get("yt_desc", "")
        lid = load_log().get(ep_dir.name, {}).get("long", {}).get("id")
        if lid and "▶ 전체 영상" not in desc:  # 쇼츠 → 롱폼 연결 (설명란 첫 줄)
            desc = f"▶ 전체 영상: https://youtu.be/{lid}\n\n" + desc
        items.append({"key": f"short{n}", "file": out / "shorts" / f"short{n}.mp4", "title": sh.get("yt_title", sh["title"]),
                      "desc": desc, "tags": yt.get("tags", [])[:10], "thumb": None, "srt": None,
                      "publish_at": when, "playlist": None})
    return items, out


SLOT_DAYS = (0, 1, 2, 3, 4, 5, 6)   # 2026-11-16~11-29 매일 롱폼 2주 시험 (이전: 화·금·토 (1, 4, 5))
SLOT_HOUR = 18       # 18:00 KST
LOG_PATH = ROOT / "uploads.json"  # git에 커밋되는 업로드 기록 (out/ 은 git 제외라 세션이 바뀌면 사라짐)


def load_log():
    return json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else {}


def next_slot(log, now=None):
    """이미 예약된 롱폼과 겹치지 않는 다음 화·금·토 18:00 (최소 3시간 여유)."""
    now = now or dt.datetime.now(KST)
    taken = {v.get("publish_at", "")[:16] for ep in log.values() for k, v in ep.items() if k == "long" and v.get("publish_at")}
    d = now + dt.timedelta(hours=3)
    cand = d.replace(hour=SLOT_HOUR, minute=0, second=0, microsecond=0)
    if cand < d:
        cand += dt.timedelta(days=1)
    while cand.weekday() not in SLOT_DAYS or cand.isoformat()[:16] in taken:
        cand += dt.timedelta(days=1)
    return cand


def parse_every(s):
    s = s.strip().lower()
    n, unit = int(s[:-1]), s[-1]
    return dt.timedelta(days=n) if unit == "d" else dt.timedelta(hours=n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", nargs="?")
    ap.add_argument("--long", action="store_true")
    ap.add_argument("--shorts", default="", help="예: 1,2,3")
    ap.add_argument("--publish-at", help="한국 시간 예약 공개. 예: 2026-11-10T18:00 · 'next' = 다음 빈 화·금·토 18:00")
    ap.add_argument("--shorts-every", default="1d", help="쇼츠 예약 간격 (1d=하루, 6h=6시간)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="이미 올린 것도 다시 올리기")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--channel", default="", help="science = 악어새 지식창고 (환경 변수 YT_REFRESH_TOKEN_SCIENCE)")
    ap.add_argument("--file", help="단일 영상 업로드(지식창고 쇼츠 등)")
    ap.add_argument("--title")
    ap.add_argument("--desc-file")
    a = ap.parse_args()
    global CHANNEL
    CHANNEL = a.channel.upper()
    if a.file:
        when = dt.datetime.fromisoformat(a.publish_at).replace(tzinfo=KST) if a.publish_at else None
        desc = Path(a.desc_file).read_text(encoding="utf-8") if a.desc_file else ""
        tok = access_token()
        vid, privacy = upload_video(tok, a.file, a.title, desc, [], when)
        print(f"  ✔ 업로드 → https://youtu.be/{vid} ({privacy})")
        return

    if a.check:
        tok = access_token()
        me = call("GET", f"{API}/youtube/v3/channels?part=snippet,statistics,status&mine=true", tok)
        for c in me.get("items", []):
            print("채널:", c["snippet"]["title"], c["snippet"].get("customUrl", ""), "· 구독자", c["statistics"].get("subscriberCount"))
        print("인증 OK")
        return

    ep_dir = Path(a.episode).resolve()
    shorts = [int(x) for x in a.shorts.split(",") if x.strip()]
    all_log = load_log()
    if a.publish_at == "next":
        when = next_slot(all_log)
    else:
        when = dt.datetime.fromisoformat(a.publish_at).replace(tzinfo=KST) if a.publish_at else None
    items, out = plan(ep_dir, a.long, shorts, when, parse_every(a.shorts_every))
    log = all_log.setdefault(ep_dir.name, {})
    for it in items:
        mark = " (이미 올림)" if it["key"] in log and not a.force else ""
        print(f"[{it['key']}] {it['title']}{mark}")
        print(f"    파일 {it['file'].name} · 공개 {it['publish_at'].strftime('%m/%d %H:%M KST') if it['publish_at'] else '비공개(수동 공개)'}"
              f"{' · 썸네일 ' + it['thumb'].name if it['thumb'] else ''}{' · 자막' if it['srt'] else ''}")
    if a.dry_run:
        return
    tok = access_token()
    for it in items:
        if it["key"] in log and not a.force:
            continue
        vid, privacy = upload_video(tok, it["file"], it["title"], it["desc"], it["tags"], it["publish_at"])
        print(f"  ✔ {it['key']} 업로드 → https://youtu.be/{vid} ({privacy})")
        if it["thumb"] and it["thumb"].exists():
            try:
                set_thumbnail(tok, vid, it["thumb"])
                print("    썸네일 OK")
            except RuntimeError as e:
                print("    썸네일 실패:", e)
        if it["srt"] and it["srt"].exists():
            try:
                add_captions(tok, vid, it["srt"])
                print("    자막 OK")
            except RuntimeError as e:
                print("    자막 실패:", e)
        if it.get("playlist"):
            add_to_playlist(tok, vid, it["playlist"])
        log[it["key"]] = {"id": vid, "title": it["title"], "at": dt.datetime.now(KST).isoformat(),
                          "publish_at": it["publish_at"].isoformat() if it["publish_at"] else None}
        LOG_PATH.write_text(json.dumps(all_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
