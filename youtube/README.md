# 유튜브 주식 채널 · 영상 자동 제작

주식 지식·인사이트(대가 투자법, 매매법) 롱폼 영상을 **코드로 렌더링**한다.
사람이 하는 일은 **대본 검토 → 녹음 1회 → 최종 검수 후 공개**뿐.

```
episode.yaml (대본+장면)  ─┬─▶ script.md (녹음용 대본)
                           │
audio/full.wav (내 녹음)  ─┼─▶ render.py ─▶ video.mp4  (차트·카드·일러스트·자막·BGM)
                           │              captions.srt (유튜브 자막 파일)
실제 시세 데이터          ─┘              thumbnail.png · youtube.json(제목·설명·태그)
```

## 처음 한 번

```bash
pip install -r requirements.txt     # ffmpeg 필요
python tools/fetch_assets.py        # 폰트(Pretendard) + 시세 데이터 내려받기
```

## 에피소드 만들기

```bash
# 1) 녹음용 대본 뽑기
python render.py episodes/ep001_buffett_fear --script

# 2) 화면만 빠르게 확인 (장면별 스틸 이미지, 몇 초)
python render.py episodes/ep001_buffett_fear --stills

# 3) 녹음 파일을 episodes/ep001_buffett_fear/audio/full.wav 로 넣고 렌더
python render.py episodes/ep001_buffett_fear

#    일부 장면만 미리보기
python render.py episodes/ep001_buffett_fear --scenes 5-7
```

결과물은 `out/<에피소드>/` 에 생긴다.

### 녹음 규칙 (자동 싱크용)

- 폰 음성녹음 앱으로 대본을 읽고, 파일을 `episodes/<ep>/audio/` 에 넣기 (m4a·mp3·wav 모두 가능)
- **파일이 여러 개여도 OK** → 파일 이름 순서대로 자동으로 이어 붙임
  (버벅이면 그 부분 잘라내고, 끊긴 문장부터 새 파일로 이어서 녹음)
- 문장 사이: 자연스럽게 0.3초 이상 쉬기 → 자막이 문장 단위로 맞음
- **장면 사이(대본의 ─── 표시): 2초 쉬기** → 무음 구간을 찾아 장면을 자동으로 나눔
- 녹음이 없으면 **가이드 모드**: 글자 수로 길이를 추정해 BGM만 깔린 영상을 만든다(화면 검수용)
- 렌더 시 장면별 실제 길이와 예상 길이를 비교해, 크게 어긋나면 `← 확인 필요`로 알려준다

내레이션은 `highpass → 컴프레서 → 라우드니스 -16 LUFS`로 정리되고,
BGM은 목소리가 나올 때 자동으로 작아진다(사이드체인 더킹).

## 폴더 구조

```
channel.yaml              채널명·코너 문구 (전 영상 공통)
episodes/<ep>/episode.yaml 대본 + 장면 정의 (이것만 쓰면 영상이 나옴)
episodes/<ep>/script.md   녹음용 대본 (자동 생성)
engine/
  style.py   색·폰트 디자인 토큰 (상승=빨강, 하락=파랑)
  data.py    실제 시세 로더 + 대본 숫자 검증 통계
  charts.py  애니메이션 선 차트(로그/낙폭/기준선/마커/구간) · 막대 차트
  illust.py  코드로 그린 일러스트 (공포-탐욕 게이지, 신문, 경고 등)
  scenes.py  장면 타입: title · quote · card · chart · bars · versus · bignum · reddit · outro
             + 공통 재미 요소: stickers(3D 이모지 팝업) · mascot(개미 + 말풍선) · stamp(판정 도장)
               · shake(화면 흔들림) · sfx(효과음)
  timeline.py 녹음 무음 감지 → 장면·문장 타이밍, 자막(SRT)
  bgm.py     코드로 합성한 배경음 (저작권 문제 없음)
  sfx.py     코드로 합성한 효과음 (뽁·슉·띵·쿵·빠밤빠·끼익 등 12종)
tools/fetch_assets.py     폰트·데이터 다운로드
```

## episode.yaml 작성법 (요약)

```yaml
scenes:
  - type: chart              # title | quote | card | chart | bars | outro
    chapter: "검증 ②"         # 오른쪽 위 챕터 표시
    chart:
      series: vix            # sp500 | sp500_drawdown | vix
      start: "1990-01-01"
      draw: {on: 1, dur: 4}  # 내레이션 1번 줄에서 4초간 그려짐
      hlines: [{y: 40, label: "VIX 40"}]
      marks:  [{date: "2020-03-16", label: "2020", on: 2}]
    callouts:                # 숫자 강조 박스
      - {on: 3, pos: [1370, 200], value: "+23.0%", label: "...", sub: "..."}
    narration:               # 한 줄 = 녹음 한 문장. ' | ' 로 자막 끊을 위치 지정 가능
      - "이번엔 공포지수로 확인해 보겠습니다."
```

`on: N` = 내레이션 N번째 문장이 시작될 때 등장. 녹음 길이가 바뀌어도 자동으로 따라간다.

`bars` 장면의 값과 `checks:` 항목은 **렌더할 때마다 실제 데이터로 다시 계산**해
`out/<ep>/numbers.txt` 에 출력된다 → 대본 숫자와 대조.

## 원칙

- 특정 종목 매수·매도 추천 금지. 교육·해설 톤. 영상 끝·설명란에 면책 문구.
- 숫자는 모두 실제 데이터에서 계산하고, 데이터 기준(월평균·배당 제외 등)을 화면에 표기.
- 폰트(Pretendard, OFL)·BGM(자체 합성)·일러스트(코드 생성) 모두 상업적 사용 가능.

## 데이터 출처

| 시리즈 | 내용 | 출처 |
|---|---|---|
| `sp500` | S&P500 월평균 지수 1871~ (1957 이전은 전신 지수) | Robert Shiller, [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500) |
| `vix` | VIX 일간 종가 1990~ | CBOE, [datasets/finance-vix](https://github.com/datasets/finance-vix) |
| `tqqq` `sqqq` `qqq` | ETF 일간 수정주가 (배당·분할 반영) | Yahoo Finance 일간 시세 공개 미러 (2개 저장소 대조, 오차 <0.001%) |
| `ndx` | 나스닥100 일간 1985~ | 〃 |
| `sim3x_ndx` | 나스닥100 x3 - 연 0.95% (가상 TQQQ, 차입비용 미반영) | 위 데이터로 계산 |

이미지: [Microsoft Fluent UI Emoji 3D](https://github.com/microsoft/fluentui-emoji) (MIT, 상업적 사용 가능)

> 현재 작업 환경에서는 Yahoo/FRED/KRX 등이 막혀 있어 GitHub 공개 데이터셋을 쓴다.
> 2단계에서 개별 지수·국내 시장 데이터가 필요하면 집 PC/서버에서 `yfinance`·`pykrx` 로더를 추가.

## 로드맵

- [x] **1단계**: 첫 주제 대본 + 샘플 영상 (EP001 버핏 '공포에 사라' 검증)
- [x] EP002 레딧 썰 팩트체크 ① TQQQ/SQQQ (8분+, 스티커·마스코트·효과음 연출)
- [ ] **2단계**: 전체 자동화
  - 주제 목록 → 대본 초안 자동 생성(LLM) → 내가 검토
  - 녹음 업로드 감지 → 자동 렌더
  - Whisper로 단어 단위 자막 싱크 (현재는 문장 단위)
  - 롱폼 → 쇼츠(9:16) 자동 잘라내기
  - YouTube Data API 비공개 업로드 (`youtube.json` + `captions.srt` + 썸네일 + 챕터)
