"""채널 영상 성적 한눈에 (YouTube Data API · 조회수 · 좋아요 · 댓글 · 길이) — 광고 후보 고르기용
  python3 tools/channel_stats.py [--channel science] → 표 출력 + out/channel_stats_<채널>.tsv
시청 지속률 · 클릭률은 이 API로 안 나옴 (YouTube Studio 분석 캡처로 보완)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upload as U  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def dur(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    h, mi, se = (int(x or 0) for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + se


def main():
    ch = "science" if "--channel" in sys.argv and sys.argv[sys.argv.index("--channel") + 1] == "science" else "stock"
    U.CHANNEL = "SCIENCE" if ch == "science" else ""
    tok = U.access_token()
    me = U.call("GET", f"{U.API}/youtube/v3/channels?part=contentDetails,statistics,snippet&mine=true", tok)["items"][0]
    up = me["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], ""
    while True:
        r = U.call("GET", f"{U.API}/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={up}" + (f"&pageToken={page}" if page else ""), tok)
        ids += [x["contentDetails"]["videoId"] for x in r["items"]]
        page = r.get("nextPageToken")
        if not page:
            break
    rows = []
    for i in range(0, len(ids), 50):
        r = U.call("GET", f"{U.API}/youtube/v3/videos?part=snippet,statistics,contentDetails,status&id=" + ",".join(ids[i:i + 50]), tok)
        for v in r["items"]:
            st = v["statistics"]
            rows.append({"id": v["id"], "date": v["snippet"]["publishedAt"][:10], "sec": dur(v["contentDetails"]["duration"]),
                         "status": v["status"]["privacyStatus"], "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)),
                         "comments": int(st.get("commentCount", 0)), "title": v["snippet"]["title"]})
    print(f"채널 {me['snippet']['title']} · 구독자 {me['statistics'].get('subscriberCount')} · 총 조회 {me['statistics'].get('viewCount')} · 영상 {len(rows)}개")
    out = ROOT / "out" / f"channel_stats_{ch}.tsv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", encoding="utf-8") as fp:
        fp.write("date\tkind\tsec\tstatus\tviews\tlikes\tcomments\tid\ttitle\n")
        for x in sorted(rows, key=lambda x: x["date"]):
            kind = "쇼츠" if x["sec"] <= 180 else "롱폼"
            fp.write(f"{x['date']}\t{kind}\t{x['sec']}\t{x['status']}\t{x['views']}\t{x['likes']}\t{x['comments']}\t{x['id']}\t{x['title']}\n")
    for x in sorted([r for r in rows if r["sec"] > 180 and r["status"] == "public"], key=lambda x: -x["views"]):
        print(f"{x['date']} 롱폼 {x['sec'] // 60}:{x['sec'] % 60:02d} 조회 {x['views']:>6} 좋아요 {x['likes']:>4} 댓글 {x['comments']:>3} · {x['title'][:40]}")
    sh = [r for r in rows if r["sec"] <= 180 and r["status"] == "public"]
    print(f"쇼츠 공개 {len(sh)}개 · 조회 합계 {sum(r['views'] for r in sh)} · 상위 5:")
    for x in sorted(sh, key=lambda x: -x["views"])[:5]:
        print(f"  {x['date']} 조회 {x['views']:>6} · {x['title'][:40]}")


if __name__ == "__main__":
    main()
