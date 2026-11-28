# EP003 슬라이드 구성 생성 스크립트 (episode.yaml 의 scenes 를 다시 만든다). 직접 수정은 episode.yaml 에 해도 됨.
import os

import yaml

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'episode.yaml')
CH = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'channel.yaml'), encoding='utf-8'))
src = open(P, encoding='utf-8').read()
head = src[:src.index('scenes:')]


def K(lines, text, hl="", hc=None, sub=None, size=120, bg=None, bgc=None, ch=None, stamp=None, extra=None):
    """가운데 큰 글씨 슬라이드"""
    it = {'text': text, 'on': 1, 'size': size}
    if hl:
        it['highlight'] = hl
    if hc:
        it['hl_color'] = hc
    if sub:
        it['sub'] = sub
    d = {'type': 'kinetic', 'items': [it], 'narration': lines}
    if bg:
        d['bg_word'] = bg
    if bgc:
        d['bg_color'] = bgc
    if ch:
        d['chapter'] = ch
    if stamp:
        d['stamp'] = stamp
    if extra:
        d.update(extra)
    return d


def VS(lines, heading, L, R, hl="", ch=None, extra=None):
    d = {'type': 'versus', 'heading': heading, 'left': L, 'right': R, 'narration': lines}
    if hl:
        d['highlight'] = hl
    if ch:
        d['chapter'] = ch
    if extra:
        d.update(extra)
    return d


SRC = "자료: S&P500 지수 일간 종가 (배당 제외)"
S = []

# ── 인트로
S.append(K(["2026년 11월 3일, 미국 중간선거가 끝났습니다.", "근데요, 주식시장엔 오래된 얘기가 하나 있어요."],
           "미국 중간선거, 끝", hl="끝", sub="2026년 11월 3일", size=140, bg="2026", ch="인트로"))
S.append(K(["중간선거가 끝나면, 그다음 1년은 오른다."], "중간선거 다음 1년은\n오른다?", hl="오른다?", size=130, ch="인트로"))
S.append(K(["월가에선 수십 년째 도는 얘기고, | 요즘 국내 커뮤니티에도 자주 보이죠.",
            "근데 이거, 진짜일까요? | 그리고 이걸로 매매하면, 정말 돈을 벌 수 있을까요?"],
           "진짜일까?\n이걸로 매매하면?", hl="매매하면?", size=120, ch="인트로"))
S.append({'type': 'title', 'skyline': True, 'y': 250, 'kicker': CH.get('series_b', '매매법 해부'),
          'title': '중간선거 다음 1년\n정말 오를까?', 'highlight': '정말 오를까?',
          'subtitle': 'S&P500 76년 데이터로 대통령 임기 사이클을 백테스트했습니다',
          'narration': ["매매법 해부, 첫 번째 시간입니다.",
                        "오늘은 미국 대통령 임기 사이클, 그리고 중간선거 매매법을, | 1950년부터 76년 치 데이터로 뜯어보겠습니다."]})
S.append({'type': 'card', 'heading': 'S&P500 = 미국 대표 기업 500개', 'highlight': '500개', 'width': 1500, 'size': 50,
          'bullets': [{'text': '애플 · 마이크로소프트 · 엔비디아 · 아마존 …', 'on': 1}, {'text': '미국 증시 전체 흐름을 보는 기준', 'on': 2}],
          'narration': ["오늘 기준은 S&P500이에요. | 애플, 마이크로소프트, 엔비디아 같은 미국 대표 기업 500개를 모은 지수죠.",
                        "미국 증시가 전체적으로 어땠는지 볼 때, 가장 많이 쓰는 기준입니다."]})
S.append(K(["아, 참고로요. 지금 사라는 영상, 절대 아닙니다. | 과거엔 이랬다는 거고, 함정도 같이 볼 거예요."],
           "지금 사라는 영상 아닙니다", hl="아닙니다", hc='down', sub="과거 데이터와 그 함정을 같이 봅니다", size=110))

# ── 기초
S.append({'type': 'card', 'chapter': '기초', 'heading': '미국 대통령 임기 = 4년', 'highlight': '4년', 'width': 1500,
          'numbered': True, 'size': 50, 'gap': 34,
          'bullets': [{'text': '대선 다음 해', 'sub': '예: 2025년', 'on': 3},
                      {'text': '중간선거 해', 'sub': '예: 2026년, 지금', 'on': 3, 'offset': 0.6, 'highlight': '중간선거 해'},
                      {'text': '대선 전 해', 'sub': '예: 2027년', 'on': 3, 'offset': 1.2},
                      {'text': '대선 해', 'sub': '예: 2028년', 'on': 3, 'offset': 1.8}],
          'narration': ["자, 먼저 기초부터요.", "미국 대통령 임기는 4년이고, 그 한가운데에 중간선거가 있습니다.",
                        "그래서 4년을 이렇게 나눠요. | 대선 다음 해, 중간선거 해, 대선 전 해, 그리고 대선 해.",
                        "중간선거에선 하원 전체와 상원 3분의 1을 다시 뽑기 때문에, | 대통령 정책이 계속 힘을 받을지가 여기서 갈려요."]})
S.append(K(["지금은 2026년, 중간선거 해죠. | 그리고 2027년은, 대선 전 해가 됩니다."],
           "지금: 중간선거 해 → 대선 전 해", hl="대선 전 해", size=100, ch="기초"))
S.append({'type': 'chart', 'chapter': '기초', 'chart': {
    'series': 'spx', 'start': '2025-11-03', 'end': '2026-11-04', 'color': [240, 84, 84],
    'title': 'S&P500 · 최근 1년', 'draw': {'on': 1, 'dur': 2.2},
    'marks': [{'date': '2026-11-03', 'label': '중간선거', 'sub': '2026.11.3', 'on': 2, 'dy': -80, 'dx': -120, 'color': 'gold'}],
    'source': SRC},
    'narration': ["S&P500의 최근 1년은 이랬고요.", "중간선거 날, 7,568포인트로 마감했습니다."]})

# ── 임기 사이클
S.append({'type': 'bars', 'chapter': '임기 사이클', 'heading': '임기 4년, 해마다 연평균 수익률',
          'subheading': 'S&P500 · 1950~2025 · 배당 제외', 'subheading_on': 1,
          'bars': {'unit': '%', 'rect': [200, 330, 1520, 430], 'source': '자료: S&P500 연간 수익률',
                   'groups': [{'label': '대선 다음 해', 'on': 2, 'bars': [{'label': '', 'color': 'neutral', 'stat': {'kind': 'cycle_mean', 'k': 1}}], 'vmax': 21},
                              {'label': '중간선거 해', 'on': 2, 'bars': [{'label': '', 'color': 'down', 'delay': 0.6, 'stat': {'kind': 'cycle_mean', 'k': 2}}], 'vmax': 21},
                              {'label': '대선 전 해', 'on': 3, 'bars': [{'label': '', 'color': 'gold', 'stat': {'kind': 'cycle_mean', 'k': 3}}], 'vmax': 21},
                              {'label': '대선 해', 'on': 4, 'bars': [{'label': '', 'color': 'neutral', 'stat': {'kind': 'cycle_mean', 'k': 4}}], 'vmax': 21}]},
          'narration': ["그럼 해마다 성적은 어땠을까요? | 1950년부터 2025년까지, S&P500 연간 수익률을 임기 순서대로 나눠 봤어요.",
                        "대선 다음 해, 8.4%. 중간선거 해, 4.6%.", "그리고 대선 전 해. 무려, 17.2%.", "대선 해는 8.1%였습니다."]})
S.append({'type': 'bignum', 'chapter': '임기 사이클', 'label': '대선 전 해, 오른 횟수', 'from': 0, 'to': 17, 'fmt': '{:.0f}번',
          'final': '19번 중 17번', 'size': 170, 'on': 1, 'dur': 1.0, 'color': 'gold', 'sub': '1951 ~ 2023', 'sub_on': 1,
          'narration': ["오른 해만 세어 봐도, 대선 전 해는 19번 중 17번 올랐습니다."]})
S.append({'type': 'yearbars', 'chapter': '임기 사이클', 'which': 'cycle3', 'on': 1, 'step': 0.12,
          'heading': '대선 전 해, 해마다 S&P500 연간 수익률 (%)', 'sub': '1951 ~ 2023 · 19번',
          'mark': {2015: '2011·2015 사실상 0%'}, 'mark_on': 3, 'source': '자료: S&P500 연간 수익률 (배당 제외)',
          'narration': ["해마다 펼쳐 보면 이렇습니다.", "1975년 31.5%, 1995년 34.1%, 2019년 28.9%. | 큰 상승이 유독 이 해에 몰려 있어요.",
                        "떨어진 두 번도, 2011년 0%, 2015년 마이너스 0.7%. | 사실상 제자리였습니다."]})
S.append(K(["재밌는 건요. | 중간선거 해가 꼴찌고, 바로 그다음 해가 1등이라는 거예요."],
           "중간선거 해 꼴찌 → 다음 해 1등", hl="1등", size=100, ch="임기 사이클"))
S.append(VS(["중간선거 해엔 하락도 깊었어요. | 그 해 고점 대비 가장 많이 빠졌던 폭이, 평균 17.5%.",
             "대선 전 해는요? 11.2%였습니다."], "해마다 겪은 최대 하락폭 (평균)",
            {'title': '중간선거 해', 'value': '-17.5%', 'sub': '4년 중 가장 깊었다', 'color': 'down', 'on': 1},
            {'title': '대선 전 해', 'value': '-11.2%', 'sub': '4년 중 가장 얕았다', 'color': 'neutral', 'on': 2}, ch="임기 사이클"))
S.append({'type': 'card', 'chapter': '임기 사이클', 'heading': '왜 이런 패턴이?', 'highlight': '왜', 'width': 1500, 'size': 48,
          'bullets': [{'text': '중간선거 전: 정책 불확실성이 커진다', 'on': 1},
                      {'text': '선거 후: 불확실성 해소 + 다음 대선 앞두고 경기 부양', 'on': 2},
                      {'text': '단, 이건 해석일 뿐 정답은 아님', 'on': 3, 'highlight': '해석일 뿐', 'hl_color': 'down'}],
          'narration': ["이유로는 보통 이런 얘기를 해요. | 중간선거 전엔 의회가 어떻게 바뀔지 몰라서 불확실성이 커지고,",
                        "선거가 끝나면 그게 걷히면서, | 다음 대선을 앞두고 경기를 띄우려는 힘이 생긴다.",
                        "물론 이건 해석일 뿐이에요. 정답은 아닙니다."]})

# ── 중간선거 1년
S.append(K(["자, 그럼 본론이요. | 중간선거 날 사서, 딱 1년 들고 있었다면 어땠을까요?"],
           "중간선거 날 사서\n1년 들고 있었다면?", hl="1년", size=120, ch="중간선거 1년"))
S.append({'type': 'yearbars', 'chapter': '중간선거 1년', 'which': 'midterm', 'on': 2, 'step': 0.14,
          'heading': '중간선거일 종가 → 1년 뒤 수익률 (%)', 'sub': 'S&P500 · 1950 ~ 2022 중간선거 19번',
          'mark': {1986: '최저 +1.1%'}, 'mark_on': 4,
          'narration': ["1950년부터 2022년까지, 중간선거는 모두 19번 있었습니다.",
                        "선거 당일 종가에 사서, 1년 뒤에 팔았다고 쳐 볼게요.",
                        "보이시나요? 막대가 전부 위로 올라가 있죠.",
                        "가장 안 좋았던 1986년도, 플러스 1.1%였어요."]})
S.append({'type': 'bignum', 'chapter': '중간선거 1년', 'label': '중간선거 다음 1년, 상승 횟수', 'from': 0, 'to': 19, 'fmt': '{:.0f}번',
          'final': '19번 중 19번', 'size': 170, 'on': 1, 'dur': 1.0, 'color': 'up', 'sub': '평균 수익률 +14.8%', 'sub_on': 2,
          'sfx_end': 'cash',
          'narration': ["네. 19번 중, 19번 다 올랐습니다.", "평균 수익률은 14.8%."]})
S.append(VS(["비교해 볼게요. 대선 날 사서 1년 들고 있었다면? | 평균 8.5%, 오른 건 19번 중 12번.",
             "같은 선거인데, 결과가 꽤 다르죠."], "선거 날 사서 1년 뒤",
            {'title': '중간선거 날', 'value': '+14.8%', 'sub': '19번 중 19번 상승', 'color': 'up', 'on': 1},
            {'title': '대선 날', 'value': '+8.5%', 'sub': '19번 중 12번 상승', 'color': 'neutral', 'on': 1, 'offset': 1.0}, ch="중간선거 1년"))
S.append(VS(["그럼 그냥 아무 해나, 11월 초에 사서 1년 들고 있었다면요?", "평균 9.2%, 오른 확률 76%. | 중간선거 해가 확실히 한 단계 높았던 거죠."],
            "11월 초에 사서 1년 뒤 (1950~2024)",
            {'title': '중간선거 해만', 'value': '+14.8%', 'sub': '상승 확률 100%', 'color': 'up', 'on': 1, 'offset': 1.0},
            {'title': '아무 해나', 'value': '+9.2%', 'sub': '상승 확률 76%', 'color': 'neutral', 'on': 1}, ch="중간선거 1년"))
S.append({'type': 'chart', 'chapter': '중간선거 1년', 'chart': {
    'series': 'spx', 'start': '2022-01-01', 'end': '2023-12-31', 'color': [240, 84, 84],
    'title': '가장 최근 사례 · S&P500 2022~2023', 'draw': {'on': 2, 'dur': 2.2},
    'marks': [{'date': '2022-10-12', 'label': '바닥', 'sub': '2022.10', 'on': 2, 'offset': 1.6, 'dy': 50, 'dx': -110, 'color': 'down'},
              {'date': '2022-11-08', 'label': '중간선거', 'on': 3, 'dy': 70, 'dx': 90, 'color': 'gold'},
              {'date': '2023-11-08', 'label': '1년 뒤 +14.5%', 'on': 3, 'offset': 1.5, 'dy': -70, 'dx': -60, 'color': 'up'}],
    'source': SRC},
    'narration': ["가장 최근, 2022년을 보면요.", "그 해 S&P500은 연초부터 크게 빠졌고, 10월에 바닥을 찍었어요.",
                  "그리고 11월 중간선거 날 사서 1년 들고 있었다면, 14.5% 수익이었습니다."]})
S.append({'type': 'chart', 'chapter': '중간선거 1년', 'chart': {
    'series': 'spx', 'start': '1990-01-01', 'end': '1991-12-31', 'color': [240, 84, 84], 'title': '1990년 중간선거 · S&P500',
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '1990-10-11', 'label': '걸프전 공포 -20%', 'on': 1, 'offset': 1.4, 'dy': 50, 'dx': -110, 'color': 'down'},
              {'date': '1990-11-06', 'label': '중간선거', 'on': 2, 'dy': 70, 'dx': 100, 'color': 'gold'}],
    'source': SRC},
    'narration': ['다른 해도 볼까요. 1990년엔 걸프전 공포로, 여름부터 10월까지 20% 가까이 빠졌어요.', '그런데 중간선거 다음 1년은? 플러스 25.1%였습니다.']})
S.append({'type': 'chart', 'chapter': '중간선거 1년', 'chart': {
    'series': 'spx', 'start': '2002-01-01', 'end': '2003-12-31', 'color': [240, 84, 84], 'title': '2002년 중간선거 · S&P500',
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2002-10-09', 'label': '닷컴 붕괴 바닥', 'on': 1, 'offset': 1.4, 'dy': 50, 'dx': -110, 'color': 'down'},
              {'date': '2002-11-05', 'label': '중간선거', 'on': 2, 'dy': 70, 'dx': 100, 'color': 'gold'}],
    'source': SRC},
    'narration': ['2002년은 닷컴 버블이 무너지던 해였죠. | 3월부터 10월까지만 33% 넘게 빠졌습니다.', '그 해 중간선거 다음 1년은, 플러스 14.9%.']})
S.append({'type': 'chart', 'chapter': '중간선거 1년', 'chart': {
    'series': 'spx', 'start': '2018-07-01', 'end': '2019-12-31', 'color': [240, 84, 84], 'title': '2018년 중간선거 · S&P500',
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2018-11-06', 'label': '중간선거', 'on': 1, 'offset': 1.4, 'dy': -80, 'dx': -80, 'color': 'gold'},
              {'date': '2018-12-24', 'label': '-14.7%', 'sub': '선거 7주 뒤', 'on': 2, 'dy': 60, 'dx': 90, 'color': 'down', 'size': 36},
              {'date': '2019-11-06', 'label': '1년 뒤 +11.7%', 'on': 3, 'dy': -70, 'dx': -80, 'color': 'up'}],
    'source': SRC},
    'shake': [{'on': 2, 'offset': 0.2, 'dur': 0.4, 'amp': 12}],
    'narration': ["근데 2018년은 좀 달랐어요. 선거 날 샀다면,", "7주 뒤 크리스마스이브엔 14.7%나 빠져 있었습니다.",
                  "결국 1년 뒤엔 플러스 11.7%로 끝났지만, | 그 사이 공포를 버텨야 했던 거죠."]})
S.append(K(["그리고 중간선거 해의 가장 낮은 날에 샀다면, 1년 뒤 평균 31.8%.",
            "물론 바닥을 맞히는 건, 현실에선 거의 불가능하지만요."],
           "중간선거 해 바닥에서 샀다면\n1년 뒤 +31.8%", hl="+31.8%", hc='up', sub="바닥을 맞힐 수 있다면, 이지만요", size=96))

# ── 백테스트
S.append(K(["자, 이제 진짜 궁금한 거요. | 이걸 매매법으로 만들면, 어떻게 될까요?"],
           "이걸 매매법으로 만들면?", hl="매매법", size=120, ch="백테스트"))
S.append({'type': 'card', 'chapter': '백테스트', 'heading': '중간선거 매매법 규칙', 'highlight': '규칙', 'width': 1500, 'size': 50,
          'numbered': True, 'gap': 40,
          'bullets': [{'text': '중간선거 날 매수', 'sub': 'S&P500 지수 그대로', 'on': 1},
                      {'text': '2년 뒤 대선 날 매도', 'on': 1, 'offset': 1.4},
                      {'text': '다음 중간선거까지 2년은 현금', 'on': 2, 'highlight': '현금', 'hl_color': 'down'}],
          'narration': ["규칙은 간단합니다. 중간선거 날 사서, 2년 뒤 대선 날 판다.",
                        "그리고 대선부터 다음 중간선거까지 2년은, 현금으로 쉰다."]})
S.append({'type': 'chart', 'chapter': '백테스트', 'chart': {
    'lines': [{'series': 'strat_mid2pres', 'color': 'gold', 'label': '중간선거→대선만'},
              {'series': 'strat_pres2mid', 'color': 'down', 'label': '대선→중간선거만', 'fill': False}],
    'start': '1950-11-07', 'end': '2026-11-04', 'base': 1000, 'unit': 'won', 'log': True, 'end_labels': True,
    'rect': [210, 200, 1300, 620], 'title': '1950년부터 1,000만 원 (로그 스케일)', 'draw': {'on': 2, 'dur': 3.0},
    'source': '자료: S&P500 일간 종가 · 배당·세금·수수료 미반영'},
    'narration': ["1950년 중간선거부터 지금까지, 1,000만 원으로 돌려 봤어요.",
                  "중간선거부터 대선까지만 들고 있었다면, 약 76배.",
                  "반대로 대선부터 중간선거까지만 들고 있었다면, 5.2배."]})
S.append(VS(["2년 단위로 보면, 중간선거부터 대선까지는 평균 26.8%, | 19번 중 18번 올랐고,",
             "대선부터 중간선거까지는 평균 11.9%, 19번 중 14번이었습니다."], "같은 4년, 두 개의 2년",
            {'title': '중간선거 → 대선', 'value': '+26.8%', 'sub': '2년 평균 · 19번 중 18번 상승', 'color': 'gold', 'on': 1},
            {'title': '대선 → 중간선거', 'value': '+11.9%', 'sub': '2년 평균 · 19번 중 14번 상승', 'color': 'down', 'on': 2}, ch="백테스트"))
S.append(K(["결국 4년 중 절반에서, | 수익의 대부분이 나온 셈이죠."], "4년 중 절반이\n수익 대부분", hl="절반", size=120))
S.append(K(["근데요. 여기서 반전이 있습니다."], "반전", size=200, bg="BUT", extra={'sfx': [{'name': 'scratch', 'on': 1, 'offset': 0.3}]}))
S.append({'type': 'chart', 'chapter': '반전', 'chart': {
    'lines': [{'series': 'spx', 'color': 'up', 'label': '그냥 계속 보유'},
              {'series': 'strat_mid2pres', 'color': 'gold', 'label': '중간선거 매매법', 'fill': False}],
    'start': '1950-11-07', 'end': '2026-11-04', 'base': 1000, 'unit': 'won', 'log': True, 'end_labels': True,
    'rect': [210, 200, 1300, 620], 'title': '같은 1,000만 원, 그냥 계속 들고 있었다면', 'draw': {'on': 1, 'dur': 3.0},
    'source': '자료: S&P500 일간 종가 · 배당 제외'},
    'narration': ["그냥 아무것도 안 하고 계속 들고 있었다면요?", "393배. 1,000만 원이 39억이 됐습니다."]})
S.append(VS(["중간선거 매매법은 약 7억 6천. 그냥 들고 있기는 39억.",
             "쉬는 2년 동안에도 시장은 5배 넘게 올랐거든요. | 그걸 통째로 놓친 겁니다."], "1950 → 2026, 1,000만 원의 결과",
            {'title': '중간선거 매매법', 'value': '7.6억', 'sub': '약 76배 · 절반은 현금', 'color': 'gold', 'on': 1},
            {'title': '그냥 계속 보유', 'value': '39억', 'sub': '393배', 'color': 'up', 'on': 1, 'offset': 1.4}, ch="반전"))
S.append(K(["계산은 간단해요. 76배 곱하기 5.2배, 이게 393배입니다.", "두 구간을 다 가져가야, 393배가 되는 거죠."],
           "76 × 5.2 = 393", hl="393", hc='up', sub="두 구간을 모두 가져가야 393배", size=150, ch="반전"))
S.append(VS(["그럼 아까 그 19번 중 19번, 중간선거 다음 1년만 들고 있었다면요?",
             "1,000만 원이 약 1억 3천. 13배였습니다. | 확률 100%짜리 1년만 골라 담았는데도요."], "중간선거 다음 1년만 보유했다면",
            {'title': '1년만 보유 (19번)', 'value': '13배', 'sub': '1,000만 원 → 약 1.3억', 'color': 'gold', 'on': 1, 'offset': 1.0},
            {'title': '그냥 계속 보유', 'value': '393배', 'sub': '1,000만 원 → 39억', 'color': 'up', 'on': 2}, ch="반전"))
S.append(K(["확률은 높였지만, 수익은 놓쳤다. | 이게 이 매매법의 핵심 함정이에요."], "확률은 높였지만\n수익은 놓쳤다",
           hl="수익은 놓쳤다", hc='down', size=120, ch="반전"))

# ── 함정
S.append(K(["그리고 이 통계를 믿기 전에, | 꼭 알아야 할 것들이 있습니다."], "믿기 전에 알아야 할 것", hl="알아야 할 것", size=110, ch="함정"))
for txt, sub_, line in [
    ("표본이 19번뿐", "동전 19번 던진 결과로 결론 내리긴 이르다",
     "첫째. 표본이 19번뿐이에요. | 76년이지만, 중간선거는 겨우 19번이었습니다."),
    ("1950년 이전엔 예외가 있었다", "1930년 중간선거 다음 1년 -34.9%",
     "둘째. 1950년 이전으로 가면 예외가 있어요. | 대공황 때인 1930년엔, 중간선거 다음 1년 동안 34.9% 빠졌습니다."),
    ("2년 구간은 실패도 있었다", "2006 → 2008 금융위기 -27.3%",
     "셋째. 2년 구간으로 보면 실패도 있었어요. | 2006년 중간선거부터 2008년 대선까지, 금융위기로 27.3% 하락."),
    ("선거 때문인지는 모른다", "그 시기에 겹친 사건일 수도",
     "넷째. 선거 때문에 오른 건지, 그 시기에 우연히 겹친 사건들 때문인지는 | 이 데이터만으론 알 수 없습니다."),
    ("1년 뒤 결과만 보면 안 된다", "2018년 -14.7%, 1974년 -13.4%, 2002년 -12.5%를 먼저 겪었다",
     "다섯째. 1년 뒤 숫자만 보면 안 돼요. | 1974년, 2002년, 2018년엔 선거 뒤 12에서 15% 하락을 먼저 버텨야 했습니다."),
    ("사고팔면 세금이 붙는다", "해외주식 양도차익 22% (연 250만 원 공제)",
     "여섯째. 2년마다 사고팔면 세금이 붙어요. | 해외주식은 수익에서 연 250만 원을 빼고, 22%가 양도소득세입니다."),
]:
    S.append({'type': 'card', 'chapter': '함정', 'heading': txt, 'width': 1500, 'size': 52, 'icon': 'dash',
              'bullets': [{'text': sub_, 'on': 1}], 'narration': [line]})

# ── 그럼 어떻게 써먹나
S.append(K(["그럼 이 통계, 개인 투자자는 어떻게 받아들이면 좋을까요?", "매매 신호보다는, 이렇게 쓰는 게 낫다고 봐요."],
           "그럼 어떻게 써먹나?", hl="써먹나?", size=140, ch="활용"))
for txt, sub_, line in [
    ("하락장에서 버티는 근거로", "중간선거 해의 하락은 역사적으로 자주 있었다",
     "첫째. 하락장에서 버티는 근거로요. | 중간선거 해에 빠지는 건, 역사적으로 늘 있던 일이었거든요."),
    ("팔 이유가 아니라, 들고 갈 이유로", "쉬는 2년이 393배와 76배를 갈랐다",
     "둘째. 팔 이유가 아니라, 들고 갈 이유로요. | 오늘 봤듯이 쉬는 2년이, 393배와 76배를 갈랐습니다."),
    ("몰빵 근거로는 쓰지 않기", "표본 19번, 미래는 다를 수 있다",
     "셋째. 몰빵 근거로는 쓰지 않기. | 19번의 과거가, 20번째를 보장하진 않으니까요."),
]:
    S.append({'type': 'card', 'chapter': '활용', 'heading': txt, 'width': 1500, 'size': 52,
              'bullets': [{'text': sub_, 'on': 1}], 'narration': [line]})

# ── 결론
S.append(K(["자, 오늘 확인한 거 정리해 볼게요."], "오늘의 결론", size=140, ch="오늘의 결론", bg="CHECK"))
for txt, st, c, line in [
    ("중간선거 다음 1년", "19번 중 19번 상승", "up", "중간선거 다음 1년. 1950년 이후 19번 중 19번 올랐습니다. 사실이에요."),
    ("대통령 임기 사이클", "대선 전 해가 가장 강했다", "gold", "임기 사이클로 보면, 대선 전 해가 평균 17%로 가장 강했고요."),
    ("이걸로 매매하면?", "그냥 보유보다 못했다", "down", "근데 이걸로 매매하면, 그냥 들고 있는 것보다 결과가 훨씬 못했습니다."),
    ("2027년도 오를까?", "아무도 모른다", "neutral", "그리고 2027년도 오를까? | 이건, 아무도 모릅니다."),
]:
    S.append(K([line], txt, size=110, ch="오늘의 결론",
               stamp={'text': st, 'color': c, 'on': 1, 'offset': 0.6, 'pos': [960, 700], 'rot': -5, 'size': 72}))
S.append(K(["그래서 하나 약속할게요. | 2027년 11월, 1년 뒤에 이 숫자로 다시 확인해 보겠습니다.",
            "이번 중간선거 날 S&P500 종가는 7,568포인트. 기억해 두세요."], "1년 뒤 확인: 7,568",
           hl="7,568", sub="2026년 중간선거 날 S&P500 종가", size=130, ch="오늘의 결론"))
S.append(K(["계절성은요, 확률이 조금 기울어진 동전이지, | 답이 정해진 시험지가 아닙니다."],
           "계절성 = 기울어진 동전", hl="기울어진 동전", sub="답이 정해진 시험지가 아니다", size=110, ch="오늘의 결론"))
S.append({'type': 'outro', 'heading': '확률이 높다고\n정답은 아니다', 'highlight': '정답은 아니다',
          'sub': '궁금한 주제 · 종목 · 매매법, 댓글로 남겨주세요',
          'disclaimer': '본 영상은 투자 교육 목적이며, 특정 종목·ETF의 매수·매도 추천이 아닙니다.\n과거 데이터는 미래 수익을 보장하지 않으며, 투자 판단과 책임은 본인에게 있습니다.',
          'subscribe_on': 3, 'signature': CH['signature'], 'signature_on': 4,
          'narration': ["확률이 높다고, 그게 정답은 아닙니다.",
                        "여러분은 이 통계, 어떻게 보세요? | 궁금했던 주제, 종목, 매매법, 뭐든 댓글로 남겨 주세요. 다음 영상에서 데이터로 끝까지 파헤쳐 드리겠습니다.",
                        CH['outro_fixed'], CH['signature']]})

body = yaml.safe_dump({'scenes': S}, allow_unicode=True, sort_keys=False, width=200, default_flow_style=None)
body = body.replace("'on':", "on:")
open(P, 'w', encoding='utf-8').write(head + body)
print(len(S), 'slides; kinetic', sum(1 for x in S if x['type'] == 'kinetic'))
