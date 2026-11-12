# 이미지 · 영상 소스 설정 안내 (PC에서 하면 편해요)

API 키는 **절대 채팅에 붙여넣지 마세요.** 발급 후 "발급했어"라고만 알려 주면, Claude가 비밀값 입력 창을 띄웁니다(이 환경에만 저장, 화면에 안 보임).

---

## 1. Pexels (사진 + 무료 영상) — ⚠️ 2026-11-12 현재 새 API 키 발급 중단 → Pixabay로 대체

- 라이선스: 상업적 이용 · 수정 가능, 출처 표기 의무 없음 (우리는 그래도 설명란에 표기)
  https://www.pexels.com/license/
1. 가입: https://www.pexels.com/join/ (구글 계정으로 가입 가능)
2. API 페이지: https://www.pexels.com/api/ → **"Your API Key"** (또는 "Get Started")
3. 신청서 간단히 작성
   - Project name: 주식 악어새 영상 제작
   - Description(예시): Background photos and stock video for educational YouTube videos about investing and science.
   - URL: 유튜브 채널 주소
4. 발급된 키 확인 (페이지에 바로 표시)
5. Claude에게 "Pexels 키 발급했어" → 입력 창에 키 붙여넣기
   - Claude 쪽 설정: api.pexels.com 에 키를 헤더로 자동 첨부, images.pexels.com · videos.pexels.com 접속 허용

## 2. Pixabay ⭐ 지금 1순위 (사진 · 일러스트 · 무료 영상)

- 라이선스: https://pixabay.com/service/license-summary/ (상업적 이용 · 수정 가능)
1. 가입: https://pixabay.com/accounts/register/
2. 로그인 후 API 문서: https://pixabay.com/api/docs/ → 페이지 안 **"Your API key"** 부분에 키가 보임
3. 키 저장 (Pixabay는 키를 주소에 붙여 보내는 방식이라 '환경 변수'로 저장):
   - claude.ai/code 세션 화면 위쪽 제목 줄의 **클라우드 환경 메뉴(유튜브 영상제작) → Edit(편집)**
   - **환경 변수(Environment variables)** 에 한 줄 추가: `PIXABAY_API_KEY=발급받은키`
   - 저장 후 **새 세션**을 열면 Claude가 그 키를 씀 (지금 세션에는 바로 안 들어올 수 있음)
   - Claude 쪽 설정: pixabay.com(API) · cdn.pixabay.com(사진 · 영상) 접속 허용 요청

## 3. Unsplash (감성 고화질 사진, 선택)

- 라이선스: https://unsplash.com/license
1. 개발자 가입: https://unsplash.com/developers → "Register as a developer"
2. https://unsplash.com/oauth/applications → **New Application** → 약관 동의 → 이름 · 설명 입력
3. 앱 페이지의 **Access Key** 복사 (Secret Key는 필요 없음)
4. 위 Pixabay와 같은 곳(환경 편집 → 환경 변수)에 `UNSPLASH_ACCESS_KEY=키` 추가 → 새 세션에서 사용

---

## 이미 연결된 것 (키 필요 없음)
- 위키미디어 공용 (tools/commons.py) — 요청이 많으면 잠시 막힘(429), 천천히 재시도
- Openverse → 플리커 등 CC 사진 (tools/openverse.py) — 상업적 이용 · 수정 가능한 것만 검색
- NASA 이미지 (퍼블릭 도메인) — images-api.nasa.gov · images-assets.nasa.gov 허용됨

## 공통 원칙
- 상업적 이용 + 수정 가능 라이선스만 (NC · ND 제외)
- 사진 · 영상 출처는 화면 구석 + 설명란에 표기
- 로고 · 상표는 그 회사를 가리킬 때만, 변형 없이, 제휴처럼 보이지 않게

---

# 효과음 소스 (지금은 코드로 직접 만든 소리만 사용 중 → 더 다양하게 쓰려면 아래 중 선택)

## A. Freesound ⭐ 추천 (효과음 50만 개 이상, API 있음)
- 라이선스: 소리마다 다름 → **CC0 · CC BY만** 골라 씀 (CC BY는 설명란 표기, NC 제외)
1. 가입: https://freesound.org/home/register/
2. API 키 신청: https://freesound.org/apiv2/apply/ → 이름 · 설명 입력 → **Client secret/Api key** 확인
3. Claude에게 "Freesound 키 발급했어" → Claude가 비밀값 입력 창을 띄움(지금 세션에서 바로 사용 가능)
   - Claude 쪽 설정: freesound.org(API) · cdn.freesound.org(미리듣기 고음질 mp3) 접속 허용

## B. Mixkit (무료 효과음 · 키 필요 없음)
- 라이선스: https://mixkit.co/license/#sfxFree (영상에 무료 사용 가능, 효과음 파일 자체 재배포만 금지)
- 해야 할 일: Claude가 접속 허용 요청만 하면 됨 (assets.mixkit.co) — 승인 버튼만 누르면 끝

## C. 유튜브 오디오 보관함 (가장 안전 · 직접 다운로드)
- 유튜브 스튜디오 → 왼쪽 메뉴 '오디오 보관함' → '음향 효과' 탭
- 원하는 소리를 내려받아 채팅에 파일로 올려 주면 Claude가 효과음 목록에 넣음
- (API 없음 · 수동)

## 제외
- BBC Sound Effects 등 비상업 라이선스, 출처 불명 '무료 효과음 모음' 사이트
