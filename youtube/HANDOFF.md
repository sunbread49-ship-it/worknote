# 이어받기 메모 (2026-11-27 저녁 · 새 세션은 이것부터)

## 11/28 새 세션 (session_01XzgYRuMiqWnt41spL6daXw)
- 쇼츠 배치: 11/29 공개분까지 옛 배치 그대로 · **11/30 공개분부터 15:50 → 16:50~19:50(1시간) → 다음날 06:50~09:50** (STRATEGY.md)
- 다음 주식 편: **ep027 닷컴 시스코 결말** (AI 거품 × 2000년 '그때의 엔비디아' · 사용자 픽) — 트렌드 · 조회수(나스닥 결말 8.7천) 근거로 선정
  - **11/28 업로드 완료(비공개 · 롱폼 tAJeJzNHmtg) → 오늘 11/28 15:50 공개** · 쇼츠 9개: 15:50 · 18 · 20 · 22 · 11/29 07:30 · 09:30 · 12:00 · 13:30 · 15:00
  - 공개 작업: 옛 세션 트리거가 같은 시각 `due`로 함께 처리 + **이 세션(session_01XzgYRuMiqWnt41spL6daXw)에 3분 뒤 예비 트리거** → 이 세션도 11/29 15:03까지 보관 금지
  - 주식채널은 매일 15:50 공개(지식채널과 같은 날) — '다음 날'로 미루지 말 것 (11/28 사용자)
- **ep028 삼성 배당(보너스의 함정)**: 11/28 업로드(비공개 · yycMKaswBVc) → **11/29 15:50 공개** · 쇼츠 18 · 20 · 22 · 11/30 07:30 · 09:30 · 12:00 · 13:30 · 15:00 · 썸네일 E
  - 끝에 예고: '진짜 하락장, 배당의 힘'(KEEP K2) → 다음 주식 주제 후보
  - 엔진: 퀴즈 셋·둘·하나 = 실제 소리 난 마지막 3박에 자막 · 화면 숫자 · 틱 맞춤(timeline.cues · hfscene BT) · 장면별 다시 녹음 `tts_take: N`
- 블로그 자동화(tools/blog.py · BLOG.md): 사용자 결정 대기(발행 방식 · 시점 · 분량 · 지식채널)
  - 데이터: `assets/data/ep027_{csco,amzn,nvda,msft}_daily.csv` (달러 종가 · 배당 제외 · 11.25까지) · 숫자 근거는 episode.yaml 머리 주석
  - 확인할 것: 시스코 2000 회계연도 매출 189억 달러(10-K 원문) · clips 시각은 렌더 후 채우기
- 새 컨테이너 준비: `python3 tools/fetch_assets.py`(폰트) · `cd hf && npm ci`(HyperFrames) · 배경 영상 mp4 상당수 없음(market_crash_v · money_count_v · datacenter_v · clock_anxiety_v 등 → json만 있음, Pixabay 키 등록 후 다시 받기)
- 주제 고를 때: `uploads.json` 최근 롱폼과 겹치는지 먼저 · 구글 트렌드 한국 화면(playwright로 trends.google.com/trending?geo=KR) 상위권 + `tools/channel_stats.py` 조회수 참고

## 지금 상태
- 공개 대기열: `publish_queue.json` · 예약 작업(트리거)이 시간마다 `tools/publish_queue.py due` 실행
  - 11/27 삼성전자(ep026) · 지구 관통(sci05) 쇼츠 공개 중 → 19:51 마지막 회차에 link_shorts
  - 11/28 15:50 서울 동네 이름(sci06, 지식) 공개 · 쇼츠는 A/B 2주차 시간대 배치(18 · 20 · 22 · 다음날 07:30 · 09:30 · 12:00 · 13:30 · 15:00)
- 11/27 삼성전자(ep026) · 지구 관통(sci05) 전부 공개 완료 · 쇼츠 링크 연결 완료
- sci07 지구가 딱 1초 멈추면: 비공개 업로드 완료(G3I10LsEGyk) · 11/29 15:50 공개 · 쇼츠 11/29 18·20·22 · 11/30 07:30·09:30·12:00·13:30·15:00
- **예약 공개 작업(트리거)은 옛 세션(session_01XzgYRsYwxnJKVwoBmLGtiR)에 묶여 있음** → 그 세션은 11/30 15:01 마지막 회차까지 보관(archive) 금지. 새 세션에서 새로 업로드하는 편은 새 세션에서 트리거를 새로 만들 것
- link_shorts: 주식 = `python3 tools/link_shorts.py` · 지식 = `YT_CHANNEL=SCIENCE python3 tools/link_shorts.py` (지식 쇼츠는 uploads.json["science"]에 기록)
- 다음 주식 주제(11/28 할 일 · 주간 한도 78% → 새 장면 개발 없이 기존 틀로 가볍게): 후보 A 곱버스 결말(코스피 반토막 맞혔는데 -95%) · 사용자는 "주식은 트렌드 중요" → 당일 뉴스로 다시 고르기

## 오늘 정한 규칙 (TEMPLATES.md 에도 있음)
- 같은 장면 틀은 한 편에 1번만(퀴즈만 예외) · 상상실험 = 어두운 톤 통일 · 생활상식 = 밝은 톤
- 말만 하는 장면 금지 → 움직이는 도식 · 핵심 장면은 HyperFrames(`engine/hfscene.py`, `hfscene2.py`)
- 그림: 내가 도형으로 그린 사람/사물 금지 · 이모지(Fluent) 유치해서 탈락 · 유료 생성 금지
  → 무료 실물 사진을 rembg 로 오려서(배경 제거) 모션그래픽 재료로 · NASA 이미지 API(키 없음) · 위키미디어
  → 배경에 사진 통째로 깔기 금지(톤 무너짐)
- 퀴즈 카운트다운: `beat_line` 으로 셋·둘·하나 1초 간격 · '2번'은 say 로 '이 번'
- 저녁에 할 일: Pexels/Pixabay 무료 키 등록(request_credential) · Poly Haven 접속 허용(update_environment)
- 대본은 더 쉽게(SCRIPT_STYLE.md 11/27 절): 생활 비유 먼저 · 장면당 새 개념 1개 · 전문어 한 줄 풀이 · 숫자엔 비교 대상 · 「정리하면」
- 렌더는 Bash run_in_background + timeout 7200000 (기본 30분이면 중간에 끊김) · 녹음 후 재렌더는 TTS_CACHE_ONLY=1
