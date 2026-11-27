# 이어받기 메모 (2026-11-27 저녁 · 새 세션은 이것부터)

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
