# YouTube API 할당량 재심사 답장 초안 (2026-11-23)

요청: 새 계산표(https://developers.google.com/youtube/v3/determine_quota_cost)로 다시 계산해서
① 쓰는 API와 예상 사용량 ② 호출 수 ③ 현재·예상 트래픽 ④ 늘리는 이유 를 7영업일 안에 회신.

⚠ 보내기 전에: 계산표 페이지에서 아래 **단가(units)** 가 맞는지 확인하고, 다르면 표의 단가만 바꾸면 합계가 바뀜.
(작업 환경에서 그 페이지를 직접 열지 못해서, 현재 알고 있는 단가로 채움: insert 1,600 · update/set/insert류 50 · captions.insert 400 · list 1)

## 실제 쓰는 API (코드 기준: tools/upload.py · upload_clips.py · publish_queue.py · link_shorts.py · clip_desc.py)
| 작업 | API | 롱폼 1편 | 쇼츠 1편 |
|---|---|---|---|
| 영상 올리기 (비공개) | videos.insert | 1 | 1 |
| 썸네일 | thumbnails.set | 1 | 1 |
| 자막 | captions.insert | 1 | 0 |
| 재생목록 넣기 | playlistItems.insert | 1 | 0 |
| 예약 시각에 공개 전환 | videos.list + videos.update(status) | 1 + 1 | 1 + 1 |
| 롱폼 ↔ 쇼츠 설명란 연결 | videos.update(snippet) | 1 | 1 |
| 쇼츠에 롱폼 안내 댓글 | commentThreads.insert | 0 | 1 |
| 채널 확인 · 상태 확인 | channels.list · videos.list | 약 5 | 약 2 |

하루 최대: 채널 2개(주식 · 지식) × (롱폼 1 + 쇼츠 9) = 영상 20편

---

## 보낼 영문 답장

Hello YouTube API Services Team,

Thank you for the follow-up. Below is our recalculated quota breakdown using the updated quota calculator.

**1. API endpoints and expected daily usage**

Our application is an internal publishing tool used only by the channel owner to upload and schedule videos on our own two YouTube channels. No third-party users access it. On a peak day we publish 2 long-form videos and 18 Shorts (1 long-form + 9 Shorts per channel).

| Endpoint | Purpose | Calls/day | Unit cost | Units/day |
|---|---|---|---|---|
| videos.insert | Upload each video as private | 20 | 1,600 | 32,000 |
| thumbnails.set | Set custom thumbnail | 20 | 50 | 1,000 |
| captions.insert | Upload Korean captions (long-form) | 2 | 400 | 800 |
| playlistItems.insert | Add long-form videos to series playlists | 2 | 50 | 100 |
| videos.update | Switch to public at scheduled time (20), add related-video links to descriptions (20) | 40 | 50 | 2,000 |
| commentThreads.insert | Post a comment linking to the full video under each Short | 18 | 50 | 900 |
| videos.list | Check status before publishing / linking | 60 | 1 | 60 |
| channels.list | Verify the authenticated channel | 10 | 1 | 10 |
| **Total** | | **172** | | **36,870** |

**2. Estimated API call volume**

About 172 calls per day at peak (36,870 units). On regular days (one channel publishing) usage is roughly half (about 18,500 units).

**3. Current and projected user traffic**

- Users of the application: 1 (the channel owner). The tool is not offered to the public.
- Channels managed: 2 (both owned by us).
- Current output: up to 2 long-form videos and 18 Shorts per day.
- Projected: the same two channels; we do not plan to add external users.

**4. Reason for the quota increase**

The default 10,000 units/day allows only about 5 uploads per day, which is not enough for our daily schedule of 20 videos across two channels. We request **50,000 units per day**, which covers the peak of 36,870 units plus about 35% headroom for re-uploads after failed uploads and corrections to metadata.

We comply with the YouTube API Services Terms and Developer Policies: all uploads are our own original content, every video is labeled as containing AI-generated narration where applicable, and no YouTube data is stored beyond video IDs needed for scheduling.

Thank you,
[이름 / 채널명]
