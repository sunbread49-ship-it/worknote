"""죽은 영상 살리기 (2026-11-14 사용자 공유 영상 '5가지' 중 API로 되는 3가지)

  python tools/seo_boost.py [--dry-run] [--only chapters|playlists|comments]

① 챕터 이름에 핵심 키워드 — 구글 검색 '주요 순간'에 챕터 이름이 그대로 노출됨 (시간은 그대로, 이름만 교체)
② 재생목록 + 설명 — 인기 영상과 묻힌 영상을 같은 재생목록에 (설명에도 키워드)
④ 키워드 질문 댓글 — 영상 핵심 키워드로 질문을 유도 (고정은 API가 안 돼서 스튜디오/앱에서 직접 '고정')
③ 엔딩 화면은 API가 없음 → 스튜디오에서 직접 · ⑤ 오프닝 잘라내기는 보류(사용자)
기록: youtube/seo_boost.json (git 커밋 · 중복 방지)
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upload as U  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "seo_boost.json"

# 영상 id → 새 챕터 이름 (기존 챕터 개수 · 순서와 같아야 함, 시간은 그대로)
CHAPTERS = {
    "edqx5gJGJ48": ["나스닥 하루 -6% 폭락", "나스닥 -6% 폭락 36번 백테스트", "역대 나스닥 폭락 사례", "닷컴 버블 vs 보통 폭락",
                    "폭락 다음 날 수익률", "대응법 ① 공포에 팔지 않기", "대응법 ② 분할 매수", "대응법 ③ 폭락장 레버리지 주의",
                    "대응법 ④ 폭락을 기회로 만든 사람들", "결론: 나스닥 폭락 때 할 일"],
    "Gb3quRi94Tc": ["TQQQ 2년 30배 성공담", "TQQQ · SQQQ 기초", "TQQQ 16년 백테스트 (302배)", "TQQQ 2년 30배 팩트체크",
                    "TQQQ 고점 이후 폭락", "레버리지 ETF 음의 복리 원리", "TQQQ 만약에 시나리오", "인버스 SQQQ 장기 보유 결과",
                    "인버스 ETF가 불리한 이유 3가지", "2025 관세 충격 TQQQ -58%", "결론: TQQQ 레버리지 투자"],
    "KBMQw7_aHFk": ["중간선거 후 주가 상승설", "미국 대통령 임기 4년 사이클", "임기별 S&P500 연간 수익률", "중간선거 후 1년 수익률",
                    "중간선거 매매법 백테스트", "반전: 그냥 보유하면 393배", "대통령 사이클 통계의 함정", "개인 투자자 활용법",
                    "결론: 중간선거와 주식"],
    "fOkegCj4T9Q": ["공포에 빚내서 산 존 템플턴", "존 템플턴 역발상 투자", "VIX 40 매수 백테스트", "VIX 40 + TQQQ 3배 레버리지",
                    "2020 코로나 VIX 매수 사례", "VIX 매매법의 함정", "템플턴 vs VIX TQQQ 차이", "공포지수 VIX 활용법",
                    "결론: 공포에 사는 법"],
    "aNpRLkol8LQ": ["중간선거 여소야대 결과", "정부 조합 5가지별 주가", "여소야대 주가 숫자 뒤 이유", "역대 레임덕 5번 주가",
                    "2028 대선 해 주가", "셧다운과 주가", "버핏: 정치와 투자", "결론: 레임덕 · 여소야대와 주식"],
    "tcQvg1c15F0": ["셀 인 메이 (Sell in May)", "S&P500 월별 수익률 12달", "핼러윈 매매법 규칙", "핼러윈 매매법 76년 백테스트",
                    "최근 10년 셀 인 메이", "나스닥100 월별 수익률", "11월 첫 주 하락 이후", "추수감사절 주가", "버핏: 영원한 보유",
                    "결론: 핼러윈 매매법"],
    "2erL2xkbvFk": ["목돈 1,200만 원 투자법", "거치식 vs 적립식 규칙", "거치식 vs 적립식 승률", "사상 최고치에 목돈 넣으면",
                    "최악의 타이밍 거치식 투자", "발상 전환: 분할 매수", "월급 적립식 투자 현실", "거치식 vs 분할 매수 정리",
                    "결론: 목돈 투자 방법"],
    "gGp7apOKjUo": ["코스피 일주일 -11.7%", "미국장 → 한국장 시차 규칙", "코스피 · 나스닥 상관계수", "나스닥 -5% 다음 날 코스피",
                    "코스피는 내릴 땐 더, 오를 땐 덜", "코스피가 미국과 따로 간 때", "코스피 주간 -10% 폭락 이후",
                    "코스피 고점 대비 -40% 5번", "정리: 코스피와 미국 증시"],
    "Blomyp9dPeE": ["인텔 -28.6% 반도체 급락", "불안 ① 인텔 실적 전망", "불안 ② 머스크 네오클라우드 발언",
                    "불안 ③ 외국인 삼성전자 · 하이닉스 매도", "반도체 ETF -7% 이후 1년", "메모리 반도체 사이클", "반도체 CEO들의 말",
                    "반도체 지켜볼 신호 3가지", "정리: SK하이닉스 -60% 반도체 전망"],
    "_qCrPvN0RLw": ["2차전지 레버리지 하루 -12.2%", "2023 에코프로 광풍과 추락", "전기차 캐즘 · 2차전지의 겨울",
                    "2차전지 레버리지 ETF의 함정", "2차전지 레버리지 버티면 회복?", "반전: AI 데이터센터와 ESS",
                    "2차전지 산업 vs 레버리지 상품", "2차전지 지켜볼 신호 (ESS 수주)", "정리: 2차전지 레버리지 -96%"],
    "E9iyOeVENB8": ["김장훈 국민연금 예상 수령액", "김장훈과 연예인 노후", "직장인 국민연금 보험료", "국민연금 보험료 주식 백테스트",
                    "반전: 국민연금 수령액 계산", "노후 소득의 구멍", "연금저축펀드 · IRP로 구멍 메우기", "지금 할 일: 예상 연금 조회",
                    "정리: 국민연금 vs 주식"],
    "TInoIij0V8Y": ["한화오션 10개월 -67%", "조선주 슈퍼사이클 15배 광풍", "한화오션 · 삼성중공업 추락", "2007 조선 사이클의 기억",
                    "반전: 신조선가지수", "조선 슈퍼사이클 이번엔 다를까", "고점 -20% 매도 규칙 백테스트", "조선주 지켜볼 신호 3가지",
                    "정리: 조선주 지금 사도 될까"],
}

# 재생목록: 인기 영상을 앞에, 묻힌 영상을 뒤에 (인기 영상 시청자가 이어서 보도록)
PLAYLISTS = [
    ("폭락장 생존 가이드 | 나스닥 · 코스피 · 반도체 · 조선주 급락 데이터",
     "주식이 폭락할 때 팔아야 할까, 사야 할까? 나스닥 -6% 폭락, 코스피 주간 -10%, 반도체 급락, 2차전지 · 조선주 고점 대비 하락까지 "
     "수십 년 데이터로 폭락 이후 1년 수익률과 대응법을 확인합니다. 폭락장 · 급락장 대응, 분할 매수, 공포지수 VIX.",
     ["_qCrPvN0RLw", "edqx5gJGJ48", "Blomyp9dPeE", "gGp7apOKjUo", "TInoIij0V8Y", "fOkegCj4T9Q"]),
    ("레버리지 ETF 백테스트 | TQQQ · SQQQ · 2차전지 레버리지",
     "TQQQ 3배 레버리지, 인버스 SQQQ, 2차전지 레버리지 ETF를 실제 데이터로 백테스트했습니다. 레버리지 ETF 장기 보유하면 왜 녹는지, "
     "음의 복리와 변동성 끌림, 공포지수 VIX와 함께 쓰는 법까지.",
     ["Gb3quRi94Tc", "_qCrPvN0RLw", "fOkegCj4T9Q"]),
    ("주식 달력 백테스트 | 중간선거 · 레임덕 · 셀 인 메이 · 핼러윈 매매법",
     "중간선거 다음 해엔 주가가 오른다? 5월엔 팔아라? 미국 대통령 임기 사이클, 여소야대 · 레임덕, 월별 수익률, 핼러윈 매매법을 "
     "S&P500 76년 데이터로 검증합니다.",
     ["KBMQw7_aHFk", "tcQvg1c15F0", "aNpRLkol8LQ"]),
    ("내 돈 굴리는 법 | 목돈 vs 적립식 · 국민연금 · 노후 준비",
     "목돈은 한 번에 넣을까 나눠 넣을까? 국민연금 보험료를 주식에 넣었다면? 거치식 vs 적립식 승률, 국민연금 예상 수령액, "
     "연금저축펀드 · IRP 지수 투자로 노후 준비하는 법을 데이터로 정리합니다.",
     ["2erL2xkbvFk", "E9iyOeVENB8"]),
]

# 키워드 질문 댓글 (채널 계정으로 작성 → 스튜디오/앱에서 '고정')
COMMENTS = {
    "edqx5gJGJ48": "나스닥 폭락 때 여러분은 팔았나요, 버텼나요, 더 샀나요? 나스닥 폭락이나 분할 매수에 대해 더 궁금한 점을 댓글로 남겨 주시면 하나씩 답해 드릴게요.",
    "Gb3quRi94Tc": "TQQQ나 SQQQ 들고 계신가요? TQQQ 장기 보유, 레버리지 ETF 음의 복리에 대해 궁금한 점을 댓글로 남겨 주시면 데이터로 답해 드릴게요.",
    "KBMQw7_aHFk": "중간선거 다음 해 주가, 여러분은 어떻게 보세요? 미국 대통령 임기 사이클이나 중간선거 매매법에 대해 궁금한 점을 댓글로 남겨 주세요.",
    "fOkegCj4T9Q": "공포지수 VIX가 40을 넘으면 여러분은 사시나요? 존 템플턴 역발상 투자나 VIX 매매법에 대해 궁금한 점을 댓글로 남겨 주시면 답해 드릴게요.",
    "aNpRLkol8LQ": "여소야대 · 레임덕, 주식에 영향이 있을까요? 레임덕이나 셧다운과 주가에 대해 궁금한 점을 댓글로 남겨 주세요.",
    "tcQvg1c15F0": "셀 인 메이, 올해도 통할까요? 핼러윈 매매법이나 월별 수익률에 대해 궁금한 점을 댓글로 남겨 주시면 데이터로 확인해 드릴게요.",
    "2erL2xkbvFk": "목돈이 생기면 한 번에 넣으시나요, 나눠서 넣으시나요? 거치식 · 적립식 투자에 대해 궁금한 점을 댓글로 남겨 주세요.",
    "gGp7apOKjUo": "미국 증시가 빠지면 코스피도 꼭 따라 빠질까요? 코스피와 나스닥 관계에 대해 궁금한 점을 댓글로 남겨 주시면 답해 드릴게요.",
    "Blomyp9dPeE": "SK하이닉스 · 삼성전자, 지금 사시나요 기다리시나요? 반도체 사이클이나 메모리 반도체에 대해 궁금한 점을 댓글로 남겨 주세요.",
    "_qCrPvN0RLw": "2차전지 레버리지, 버티고 계신가요? 2차전지 · 에코프로 · ESS에 대해 궁금한 점을 댓글로 남겨 주시면 데이터로 답해 드릴게요.",
    "E9iyOeVENB8": "국민연금 예상 수령액, 직접 조회해 보셨나요? 국민연금이나 연금저축펀드 · IRP에 대해 궁금한 점을 댓글로 남겨 주시면 하나씩 답해 드릴게요.",
    "aIgNBazE-y4": "젠슨 황 없는 엔비디아, 1985년 애플일까요 2011년 애플일까요? 엔비디아 주가나 CEO 교체에 대해 궁금한 점을 댓글로 남겨 주시면 데이터로 답해 드릴게요.",
    "TInoIij0V8Y": "한화오션 · 삼성중공업, 조선주 지금은 어떻게 보세요? 조선 슈퍼사이클이나 신조선가에 대해 궁금한 점을 댓글로 남겨 주세요.",
}

CH_RE = re.compile(r"^(\s*\d{1,2}:\d{2}(?::\d{2})?\s+)(.+)$", re.M)


def put_snippet(t, it, desc, dry):
    sn = it["snippet"]
    body = {"id": it["id"], "snippet": {"title": sn["title"], "description": desc, "categoryId": sn["categoryId"],
                                        "tags": sn.get("tags", []), "defaultLanguage": sn.get("defaultLanguage", "ko"),
                                        "defaultAudioLanguage": sn.get("defaultAudioLanguage", "ko")}}
    if not dry:
        U.call("PUT", U.API + "/youtube/v3/videos?part=snippet", t, body)


def chapters(t, log, dry):
    items = U.call("GET", U.API + "/youtube/v3/videos?part=snippet&id=" + ",".join(CHAPTERS), t)["items"]
    for it in items:
        vid, desc = it["id"], it["snippet"]["description"]
        names = CHAPTERS[vid]
        found = CH_RE.findall(desc)
        if [b for _, b in found] == names:
            print(f"챕터 이미 됨 {vid}")
            continue
        if len(found) != len(names):
            print(f"챕터 개수 다름 {vid}: {len(found)} vs {len(names)} → 건너뜀")
            continue
        it_names = iter(names)
        new = CH_RE.sub(lambda m: m.group(1) + next(it_names), desc)
        put_snippet(t, it, new, dry)
        log.setdefault("chapters", {})[vid] = names
        print(f"챕터 ✔ {vid}  {names[0]} … {names[-1]}")


def playlists(t, log, dry):
    have = {p["snippet"]["title"]: p["id"] for p in
            U.call("GET", U.API + "/youtube/v3/playlists?part=snippet&mine=true&maxResults=50", t).get("items", [])}
    done = log.setdefault("playlists", {})
    for title, desc, vids in PLAYLISTS:
        pid = have.get(title) or done.get(title, {}).get("id")
        if not pid:
            body = {"snippet": {"title": title, "description": desc, "defaultLanguage": "ko"}, "status": {"privacyStatus": "public"}}
            if dry:
                print(f"재생목록 만들기(미리보기) {title}")
                continue
            pid = U.call("POST", U.API + "/youtube/v3/playlists?part=snippet,status", t, body)["id"]
            print(f"재생목록 ✔ {title} → {pid}")
        rec = done.setdefault(title, {"id": pid, "videos": []})
        rec["id"] = pid
        for v in vids:
            if v in rec["videos"]:
                continue
            if not dry:
                for k in range(4):   # 연속 추가 시 409 ABORTED가 가끔 남 → 잠깐 쉬고 다시
                    try:
                        U.add_to_playlist(t, v, pid)
                        break
                    except RuntimeError as e:
                        if "409" not in str(e) or k == 3:
                            raise
                        time.sleep(3 + 3 * k)
            rec["videos"].append(v)
            print(f"  + {v}")


def comments(t, log, dry):
    done = log.setdefault("comments", {})
    st = {i["id"]: i["status"]["privacyStatus"] for i in
          U.call("GET", U.API + "/youtube/v3/videos?part=status&id=" + ",".join(COMMENTS), t)["items"]}
    for vid, text in COMMENTS.items():
        if done.get(vid):
            continue
        if st.get(vid) != "public":
            print(f"댓글 보류(공개 전) {vid}")
            continue
        if dry:
            print(f"댓글(미리보기) {vid}: {text[:40]}…")
            continue
        try:
            r = U.call("POST", U.API + "/youtube/v3/commentThreads?part=snippet", t,
                       {"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}})
            done[vid] = r["id"]
            print(f"댓글 ✔ {vid}")
        except Exception as e:  # noqa: BLE001
            print(f"댓글 실패 {vid}: {str(e)[:160]}")


def main():
    dry = "--dry-run" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    t = U.access_token()
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    try:
        for name, fn in (("chapters", chapters), ("playlists", playlists), ("comments", comments)):
            if only in (None, name):
                fn(t, log, dry)
    finally:
        if not dry:
            LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
