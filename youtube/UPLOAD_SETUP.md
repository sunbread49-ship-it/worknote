# 유튜브 자동 업로드 설정 (최초 1회, PC에서 약 20~30분)

업로드 도구: `tools/upload.py` (롱폼 + 썸네일 + 자막 + 쇼츠 + 예약 공개)

## 1. YouTube Data API 켜기
- TTS 때 만든 구글 클라우드 프로젝트를 그대로 써도 됩니다.
- https://console.cloud.google.com/apis/library/youtube.googleapis.com → **사용**

## 2. OAuth 동의 화면 만들기
- https://console.cloud.google.com/auth/overview → **시작하기**
  - 앱 이름: `개미의 계산기 업로더` / 사용자 지원 이메일: 본인 Gmail
  - 대상(사용자 유형): **외부**
  - 연락처 이메일: 본인 Gmail → 완료
- **데이터 액세스(범위)** → 범위 추가 → 아래 2개 체크 → 저장
  - `https://www.googleapis.com/auth/youtube.upload` (영상 업로드)
  - `https://www.googleapis.com/auth/youtube.force-ssl` (자막·썸네일·재생목록)
- **대상(Audience)** → **앱 게시(프로덕션으로 푸시)**
  - ⚠️ '테스트' 상태로 두면 7일마다 토큰이 만료되어 자동 업로드가 멈춥니다. 반드시 '프로덕션'으로.
  - 구글 검증(verification)은 안 받아도 됩니다. 본인 계정만 쓰므로 '확인되지 않은 앱' 경고만 뜹니다.

## 3. OAuth 클라이언트 만들기
- https://console.cloud.google.com/auth/clients → **클라이언트 만들기**
  - 애플리케이션 유형: **웹 애플리케이션**
  - 승인된 리디렉션 URI: `https://developers.google.com/oauthplayground`
- 만들어진 **클라이언트 ID**와 **클라이언트 보안 비밀번호**를 메모장에 복사 (채팅에 붙여넣지 말 것)

## 4. 리프레시 토큰 받기 (OAuth Playground)
1. https://developers.google.com/oauthplayground 접속
2. 오른쪽 위 **톱니바퀴** → **Use your own OAuth credentials** 체크 → 3단계의 ID·비밀번호 붙여넣기 → Close
3. 왼쪽 **Step 1** 아래 입력칸에 아래를 붙여넣고 **Authorize APIs**
   ```
   https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.force-ssl
   ```
4. 구글 로그인 → **채널 선택 화면에서 '개미의 계산기' 채널**을 고르기 (본인 이름 채널 말고)
5. '확인되지 않은 앱' 경고 → **고급** → **(안전하지 않음)으로 이동** → 허용
6. **Step 2** → **Exchange authorization code for tokens** → 나온 **Refresh token** 복사

## 5. Claude 환경에 넣기 (채팅에 붙여넣지 말 것)
- Claude 앱 오른쪽 **환경 → '유튜브 영상제작' 톱니바퀴** → **환경 변수** 칸에 3줄 추가
  ```
  YT_CLIENT_ID=3단계 클라이언트 ID
  YT_CLIENT_SECRET=3단계 클라이언트 보안 비밀번호
  YT_REFRESH_TOKEN=4단계 리프레시 토큰
  ```
- 저장 후 **새 세션**에서부터 적용 → "업로드 연결 확인해줘"라고 하면 `python tools/upload.py --check` 로 확인

## 6. 공개 업로드 허가 받기 (YouTube API 감사)
- 개인이 새로 만든 API 프로젝트로 올린 영상은 감사 통과 전까지 **비공개로 잠깁니다** (예약 공개도 안 됨).
- 신청: https://support.google.com/youtube/contact/yt_api_form → "YouTube API Services - Audit and Quota Extension"
  - 용도: 본인 채널에 직접 제작한 교육 영상을 업로드 · 예약 공개하는 내부 도구
- 통과 전: 자동 업로드(비공개) → 스튜디오 앱에서 '공개'만 누르기
- 통과 후: 예약 공개까지 완전 자동

## 업로드 명령 (참고)
```bash
python tools/upload.py episodes/ep004_templeton_vix --long --shorts 1,2,3 --dry-run               # 미리 보기
python tools/upload.py episodes/ep004_templeton_vix --long --shorts 1,2,3 \
       --publish-at 2026-11-10T18:00 --shorts-every 1d                                             # 롱폼 18시, 쇼츠 하루 1개
```
- 대표 썸네일: `out/<ep>/thumbnail_pick.png` 가 있으면 그걸, 없으면 `thumbnail.png`
- 올린 기록: `out/<ep>/uploaded.json` (중복 업로드 방지)
- 하루 할당량(10,000): 업로드 1건 1,600 → 하루 롱폼 1 + 쇼츠 3 정도가 안전
