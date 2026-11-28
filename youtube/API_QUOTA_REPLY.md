# YouTube API 할당량 재심사 답장 초안 (2026-11-23 · 새 계산표 반영)

출처: 할당량 계산기 https://developers.google.com/youtube/data/determine_quota_cost (최종 업데이트 2026-10-15)

## 바뀐 점 (핵심)
- **videos.insert(업로드)는 따로 계산**: 하루 기본 **100번**, 한 번에 1. (예전엔 1번에 1,600 단위라 하루 6편이 한계였음)
- 나머지 API는 지금처럼 하루 **10,000 단위**.
- 단가: 자막 insert 400 · 썸네일 set 50 · videos.update 50 · 댓글 commentThreads.insert 50 · 재생목록 playlistItems.insert 50 · list 류 1

## 우리 사용량 (코드 기준: tools/upload.py · upload_clips.py · publish_queue.py · link_shorts.py · clip_desc.py)
하루 최대 = 채널 2개(주식 · 지식) × (롱폼 1 + 쇼츠 9) = 영상 20편

| API | 하는 일 | 하루 호출 | 단가 | 하루 사용 |
|---|---|---|---|---|
| videos.insert | 비공개 업로드 | 20 | 업로드 전용 칸 (100번 중) | 20번 / 100번 |
| thumbnails.set | 썸네일 | 20 | 50 | 1,000 |
| captions.insert | 롱폼 자막 | 2 | 400 | 800 |
| playlistItems.insert | 롱폼 재생목록 | 2 | 50 | 100 |
| videos.update | 공개 전환 20 + 설명란 연결 20 | 40 | 50 | 2,000 |
| commentThreads.insert | 쇼츠 아래 롱폼 안내 댓글 | 18 | 50 | 900 |
| videos.list | 공개 · 연결 전 상태 확인 | 60 | 1 | 60 |
| channels.list | 채널 확인 | 10 | 1 | 10 |
| 합계 (업로드 제외) | | 152 | | **4,870 / 10,000** |

→ **새 방식으로는 기본 할당량 안에 다 들어감.** 업로드 20번(한도 100), 나머지 4,870단위(한도 10,000의 약 49%).
→ 그래서 답장은 "늘릴 필요가 없어졌다, 현재 기본 할당량으로 충분하니 심사를 마무리해 달라"로 보내는 걸 추천.

---

## 보낼 영문 답장

Hello YouTube API Services Team,

Thank you for letting us know about the updated quota calculation. We recalculated our usage with the updated quota calculator (last updated 2026-10-15). Under the new methodology, our needs fit within the default quota, so we no longer need an increase.

**1. API endpoints and expected daily usage (peak day)**

Our application is an internal publishing tool used only by the channel owner to upload and schedule videos on our own two YouTube channels. No third-party users access it. On a peak day we publish 2 long-form videos and 18 Shorts (1 long-form + 9 Shorts per channel).

| Endpoint | Purpose | Calls/day | Cost | Usage/day |
|---|---|---|---|---|
| videos.insert | Upload each video as private | 20 | separate bucket (1 per call) | 20 of 100 calls |
| thumbnails.set | Set custom thumbnail | 20 | 50 | 1,000 |
| captions.insert | Upload Korean captions (long-form) | 2 | 400 | 800 |
| playlistItems.insert | Add long-form videos to series playlists | 2 | 50 | 100 |
| videos.update | Switch to public at the scheduled time (20), add related-video links to descriptions (20) | 40 | 50 | 2,000 |
| commentThreads.insert | Post a comment linking to the full video under each Short | 18 | 50 | 900 |
| videos.list | Check status before publishing / linking | 60 | 1 | 60 |
| channels.list | Verify the authenticated channel | 10 | 1 | 10 |
| **Total (excluding videos.insert)** | | **152** | | **4,870 of 10,000 units** |

**2. Estimated API call volume**

About 172 calls per day at peak: 20 videos.insert calls (of the 100-call daily bucket) and 152 calls to other endpoints using about 4,870 units (of 10,000). On regular days usage is about half.

**3. Current and projected user traffic**

- Users of the application: 1 (the channel owner). The tool is not offered to the public.
- Channels managed: 2 (both owned by us).
- Current output: up to 2 long-form videos and 18 Shorts per day.
- Projected: the same two channels; we do not plan to add external users.

**4. Quota request**

With the updated methodology, the default quota (100 videos.insert calls and 10,000 units per day) covers our peak usage with about 50% headroom. We therefore withdraw our request for an increase and would like to complete the compliance review with the default quota. If our publishing volume grows in the future, we will submit a new request with updated figures.

We comply with the YouTube API Services Terms of Service and Developer Policies: all uploads are our own original content, videos with AI-generated narration are disclosed as altered or synthetic content, and we store only the video IDs needed for scheduling.

Thank you,
[이름 / 채널명]
