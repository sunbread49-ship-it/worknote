# EP004 슬라이드 구성 생성 스크립트 (episode.yaml 의 scenes 를 다시 만든다). 직접 수정은 episode.yaml 에 해도 됨.
import os

import yaml

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'episode.yaml')
CH = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'channel.yaml'), encoding='utf-8'))
src = open(P, encoding='utf-8').read()
head_yaml = src[:src.index('scenes:')]


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
LEV = "3배 = TQQQ 수정주가 (2010.2 이전은 나스닥100 x3 - 연 0.95% 가상 계산)"
S = []

# ── 인트로
S.append(K(["모두가 공포에 질려서 팔 때, | 거꾸로 돈을 빌려서까지 주식을 산 사람이 있습니다."],
           "모두가 팔 때\n돈을 빌려서 샀다", hl="돈을 빌려서", size=120, ch="인트로"))
S.append(K(["1939년, 존 템플턴이라는 사람이었죠."], "1939년, 존 템플턴", hl="존 템플턴", size=140, bg="1939", ch="인트로"))
S.append(K(["그리고 요즘 커뮤니티에도 비슷한 말이 돌아요. | 공포지수 40 넘으면, TQQQ 풀매수."],
           "VIX 40 넘으면\nTQQQ 풀매수?", hl="TQQQ 풀매수?", hc='up', size=120, ch="인트로"))
S.append({'type': 'title', 'skyline': True, 'y': 250, 'kicker': CH.get('series_b', '매매법 해부'),
          'title': '하락장에 세게 들어가면\n정말 돈이 될까?', 'highlight': '정말 돈이 될까?',
          'subtitle': '템플턴의 역발상 + VIX 40 TQQQ 매매법을 백테스트했습니다',
          'narration': ["매매법 해부, 두 번째 시간입니다.",
                        "오늘은 하락장에 세게 들어가는 공격적인 매매법 두 가지를, | 1929년부터 실제 데이터로 뜯어보겠습니다."]})
S.append(K(["아, 참고로요. 사라는 영상, 절대 아닙니다. | 특히 레버리지는 원금 대부분을 잃을 수 있어요."],
           "사라는 영상 아닙니다", hl="아닙니다", hc='down', sub="레버리지는 원금 대부분을 잃을 수 있습니다", size=110))

# ── 템플턴
S.append({'type': 'card', 'chapter': '템플턴', 'heading': '존 템플턴은 누구?', 'highlight': '존 템플턴', 'width': 1500, 'size': 50,
          'bullets': [{'text': '월가의 전설적인 역발상 투자자', 'on': 1}, {'text': '해외 주식 투자를 개척한 펀드매니저', 'on': 2},
                      {'text': '"비관이 극에 달했을 때가 최고의 매수 시점"', 'on': 3, 'highlight': '비관이 극에 달했을 때'}],
          'narration': ["존 템플턴은 월가에서 가장 유명한 역발상 투자자 중 한 명이에요.",
                        "미국 투자자들이 해외 주식을 거의 안 보던 시절, 그걸 개척한 펀드매니저이기도 하고요.",
                        "그의 원칙은 딱 하나였습니다. 비관이 극에 달했을 때가, 최고의 매수 시점이다."]})
S.append({'type': 'chart', 'chapter': '템플턴', 'chart': {
    'series': 'spx', 'start': '1937-01-01', 'end': '1940-06-30', 'color': [74, 144, 255], 'title': 'S&P500 · 1937 ~ 1940',
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '1939-09-01', 'label': '2차대전 발발', 'sub': '1939.9', 'on': 2, 'dy': -90, 'dx': -60, 'color': 'gold'}],
    'source': SRC},
    'narration': ["1939년은 대공황의 상처가 아직 남아 있던 때였어요.", "그리고 9월, 유럽에서 2차 세계대전이 터집니다. | 시장은 공포 그 자체였죠."]})
S.append({'type': 'card', 'chapter': '템플턴', 'heading': '템플턴이 한 일', 'highlight': '한 일', 'width': 1500, 'size': 50,
          'numbered': True, 'gap': 36,
          'bullets': [{'text': '1만 달러를 빌렸다', 'on': 1},
                      {'text': '1달러 이하로 떨어진 주식 104개를 샀다', 'sub': '그중 34개는 파산 상태였다', 'on': 2},
                      {'text': '그리고 4년을 기다렸다', 'on': 3}],
          'narration': ["그때 템플턴은, 1만 달러를 빌립니다.", "그리고 주가가 1달러 아래로 떨어진 회사 104개를, | 100주씩 전부 삽니다. 그중 34개는 이미 파산 상태였어요.",
                        "그리고 4년을 기다렸죠."]})
S.append(VS(["결과는요? 4년 뒤, 약 4배.", "같은 기간 S&P500은요? 겨우 4.8% 올랐습니다."], "4년 뒤 결과 (1939 → 1943)",
            {'title': '템플턴', 'value': '약 4배', 'sub': '104개 중 휴지가 된 건 4개뿐', 'color': 'up', 'on': 1},
            {'title': 'S&P500', 'value': '+4.8%', 'sub': '1939.9 → 1943.9', 'color': 'neutral', 'on': 2}, ch="템플턴",
            extra={'note': '템플턴 투자는 널리 알려진 일화 기준'}))
S.append({'type': 'chart', 'chapter': '템플턴', 'chart': {
    'series': 'spx', 'start': '1939-06-01', 'end': '1946-06-30', 'color': [240, 84, 84], 'title': 'S&P500 · 1939 ~ 1946',
    'draw': {'on': 1, 'dur': 2.2},
    'marks': [{'date': '1939-09-01', 'label': '템플턴 매수', 'on': 1, 'dy': -80, 'dx': 60, 'color': 'gold'},
              {'date': '1942-04-28', 'label': '-34%', 'sub': '2년 반 뒤', 'on': 2, 'dy': 50, 'dx': 90, 'color': 'down', 'size': 36},
              {'date': '1946-05-29', 'label': '+158%', 'on': 3, 'dy': -70, 'dx': -80, 'color': 'up', 'size': 36}],
    'source': SRC},
    'narration': ["근데 재밌는 건요. 템플턴이 산 뒤에도, 시장은 바로 안 올랐어요.",
                  "2년 반 동안 34%가 더 빠졌거든요.", "그 바닥에서부터 4년 동안은, 158%가 올랐습니다."]})
S.append({'type': 'quote', 'chapter': '템플턴',
          'original': 'Bull markets are born on pessimism, grow on skepticism, mature on optimism, and die on euphoria.',
          'text': '강세장은 비관 속에서 태어나, 회의 속에서 자라고, 낙관 속에서 무르익어, 환희 속에서 죽는다.',
          'highlight': '비관 속에서 태어나', 'source': '존 템플턴',
          'narration': ["템플턴이 남긴 유명한 말이 있어요.", "강세장은 비관 속에서 태어나, 회의 속에서 자라고, | 낙관 속에서 무르익어, 환희 속에서 죽는다."]})

# ── 백테스트 ① 하락장 매수
S.append(K(["자, 이걸 규칙으로 만들어 볼게요."], "템플턴을 규칙으로", hl="규칙", size=140, ch="백테스트 ①"))
S.append({'type': 'card', 'chapter': '백테스트 ①', 'heading': '하락장 매수 규칙', 'highlight': '규칙', 'width': 1500, 'size': 50,
          'numbered': True, 'gap': 38,
          'bullets': [{'text': 'S&P500이 고점 대비 -30% 빠진 첫날 매수', 'on': 1, 'highlight': '-30%', 'hl_color': 'down'},
                      {'text': '5년 들고 있기', 'on': 2},
                      {'text': '하락장마다 한 번만 (고점 회복 후 다시)', 'on': 2, 'offset': 1.2}],
          'narration': ["S&P500이 직전 고점보다 30% 빠진 첫날에 사서,", "5년 들고 있는다. 하락장 한 번에 한 번만이요."]})
S.append({'type': 'yearbars', 'chapter': '백테스트 ①', 'which': 'dd', 'th': -0.3, 'years': 5, 'on': 2, 'step': 0.3,
          'heading': '-30% 빠진 날 사서 5년 뒤 수익률 (%)', 'sub': 'S&P500 · 1929 ~ 2020 · 하락장 7번',
          'mark': {1929: '대공황'}, 'mark_on': 3, 'source': '자료: S&P500 일간 종가 (배당 제외)',
          'narration': ["1929년부터 지금까지, S&P500이 30% 넘게 빠진 하락장은 모두 7번이었어요.",
                        "1970년, 1974년, 1987년, 2001년, 2008년, 2020년.",
                        "근데 하나만 파란색이죠. 1929년 대공황입니다."]})
S.append({'type': 'bignum', 'chapter': '백테스트 ①', 'label': '-30%에 사서 5년 뒤 플러스', 'from': 0, 'to': 6, 'fmt': '{:.0f}번',
          'final': '7번 중 6번', 'size': 170, 'on': 1, 'dur': 1.0, 'color': 'up', 'sub': '평균 +43.3% · 1929년을 빼면 평균 +60%', 'sub_on': 2,
          'narration': ["7번 중 6번은, 5년 뒤 플러스였어요.", "평균 43.3%. 1929년을 빼면 평균 60%입니다."]})
S.append(VS(["1년 뒤로 보면 차이가 더 확실해요. | -30% 날 샀다면 평균 16.0%,", "아무 날에나 샀다면 평균 8.2%. 거의 두 배죠."], "1년 뒤 평균 수익률",
            {'title': '-30% 빠진 날 매수', 'value': '+16.0%', 'sub': '1929~ · 7번', 'color': 'up', 'on': 1},
            {'title': '아무 날에나 매수', 'value': '+8.2%', 'sub': '1928~ 모든 날', 'color': 'neutral', 'on': 2}, ch="백테스트 ①"))
S.append(VS(["근데 5년으로 늘리면요? | -30% 매수는 평균 43.3%, 아무 날 매수는 45.6%.", "오히려 비슷하거나, 살짝 낮아요. 왜일까요?"], "5년 뒤 평균 수익률",
            {'title': '-30% 빠진 날 매수', 'value': '+43.3%', 'sub': '7번 평균', 'color': 'gold', 'on': 1},
            {'title': '아무 날에나 매수', 'value': '+45.6%', 'sub': '모든 날 평균', 'color': 'neutral', 'on': 1, 'offset': 1.5}, ch="백테스트 ①"))
S.append(K(["범인은, 1929년 하나예요."], "범인은 1929년", hl="1929년", hc='down', size=150, bg="1929", bgc='down'))
S.append({'type': 'chart', 'chapter': '백테스트 ①', 'chart': {
    'series': 'spx', 'start': '1929-06-01', 'end': '1934-12-31', 'color': [74, 144, 255], 'title': 'S&P500 · 1929 ~ 1934',
    'draw': {'on': 1, 'dur': 2.2},
    'marks': [{'date': '1929-10-29', 'label': '-30%에 매수', 'on': 1, 'offset': 0.8, 'dy': -70, 'dx': 90, 'color': 'gold'},
              {'date': '1932-06-01', 'label': '거기서 -78%', 'on': 2, 'dy': -90, 'dx': 70, 'color': 'down', 'size': 36}],
    'source': SRC},
    'shake': [{'on': 2, 'offset': 0.3, 'dur': 0.5, 'amp': 14, 'sfx': 'boom'}],
    'narration': ["1929년 10월, 30% 빠졌을 때 샀다면요.", "거기서 또 78%가 빠졌습니다. | 1억이 2,200만 원이 되는 거죠."]})
S.append(VS(["그래서 이 숫자가 제일 중요해요. 산 다음에, 얼마나 더 빠졌나.", "평균 26.6%. 최악은 78.5%였습니다."],
            "-30%에 산 뒤, 5년 안에 더 빠진 폭",
            {'title': '평균', 'value': '-26.6%', 'sub': '7번 평균', 'color': 'down', 'on': 1, 'offset': 1.2},
            {'title': '최악 (1929)', 'value': '-78.5%', 'sub': '1억 → 2,150만 원', 'color': 'down', 'on': 2}, ch="백테스트 ①"))
S.append(K(["다시 말해서요. -30%에 사도, 바닥이 아니라 | 대부분 한가운데에서 사게 된다는 거예요."], "바닥이 아니라\n한가운데서 산다",
           hl="한가운데", hc='down', size=120))
S.append({'type': 'bars', 'chapter': '백테스트 ①', 'heading': '얼마나 빠졌을 때 사는 게 나았을까', 'subheading': 'S&P500 · 1929 ~ · 하락장마다 첫 도달일 매수',
          'subheading_on': 1,
          'bars': {'unit': '%', 'rect': [200, 330, 1520, 430], 'source': '자료: S&P500 일간 종가 (배당 제외)',
                   'groups': [{'label': '-20%에 매수 (11번)', 'on': 2, 'vmax': 55, 'bars': [
                                  {'label': '1년 뒤', 'color': 'neutral', 'stat': {'kind': 'dd_mean1', 'th': -0.2}},
                                  {'label': '5년 뒤', 'color': 'up', 'stat': {'kind': 'dd_meanY', 'th': -0.2}}]},
                              {'label': '-30%에 매수 (7번)', 'on': 2, 'vmax': 55, 'bars': [
                                  {'label': '1년 뒤', 'color': 'neutral', 'delay': 0.6, 'stat': {'kind': 'dd_mean1', 'th': -0.3}},
                                  {'label': '5년 뒤', 'color': 'up', 'delay': 0.6, 'stat': {'kind': 'dd_meanY', 'th': -0.3}}]},
                              {'label': '-40%에 매수 (4번)', 'on': 3, 'vmax': 55, 'bars': [
                                  {'label': '1년 뒤', 'color': 'neutral', 'stat': {'kind': 'dd_mean1', 'th': -0.4}},
                                  {'label': '5년 뒤', 'color': 'up', 'stat': {'kind': 'dd_meanY', 'th': -0.4}}]}]},
          'narration': ["그럼 더 깊이 빠질 때까지 기다리면 나을까요?", "-20%에 사도, -30%에 사도, 5년 뒤 평균은 43% 안팎으로 비슷했고,",
                        "-40%까지 기다리면 오히려 39%로 낮아졌어요. | 기회도 100년에 4번뿐이었고요."]})
S.append({'type': 'chart', 'chapter': '백테스트 ①', 'chart': {
    'series': 'spx', 'start': '2021-10-01', 'end': '2024-03-31', 'color': [240, 84, 84], 'title': 'S&P500 · 2022년 하락장',
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2022-10-12', 'label': '-25%에서 멈춤', 'on': 1, 'offset': 1.0, 'dy': 50, 'dx': 100, 'color': 'down'}],
    'source': SRC},
    'narration': ["2022년이 딱 그랬죠. 고점 대비 25%에서 바닥을 찍고 올라갔어요.",
                  "-30%를 기다린 사람은, 한 주도 못 사고 상승장을 구경만 했습니다."]})

# ── VIX + TQQQ
S.append(K(["자, 이제 공격 모드입니다. | 이걸 3배 레버리지로 하면 어떻게 될까요?"], "이걸 3배로 하면?", hl="3배", hc='up', size=150, bg="3X", ch="VIX + TQQQ"))
S.append({'type': 'card', 'chapter': 'VIX + TQQQ', 'heading': '공포지수 VIX', 'highlight': 'VIX', 'width': 1500, 'size': 50,
          'bullets': [{'text': '앞으로 30일, 시장이 얼마나 흔들릴지 예상한 값', 'on': 1},
                      {'text': '평소 15~20 · 40을 넘으면 극도의 공포', 'on': 2, 'highlight': '40', 'hl_color': 'down'}],
          'narration': ["VIX는 공포지수라고 불려요. 앞으로 한 달 동안 시장이 얼마나 출렁일지 예상한 값이에요.",
                        "평소엔 15에서 20 정도인데, 40을 넘으면 말 그대로 극도의 공포 상태입니다."]})
S.append({'type': 'chart', 'chapter': 'VIX + TQQQ', 'chart': {
    'series': 'vix', 'start': '1990-01-01', 'end': '2026-11-04', 'color': [240, 84, 84], 'title': 'VIX 공포지수 · 1990 ~ 2026',
    'draw': {'on': 1, 'dur': 2.4}, 'hlines': [{'y': 40, 'label': 'VIX 40', 'color': 'gold'}], 'source': '자료: CBOE VIX 일간 종가'},
    'narration': ["1990년부터 보면, VIX가 40을 넘은 건 손에 꼽을 정도예요.", "9·11, 금융위기, 코로나, 그리고 작년 관세 충격 때."]})
S.append({'type': 'card', 'chapter': 'VIX + TQQQ', 'heading': 'VIX 40 TQQQ 매매법', 'highlight': 'TQQQ', 'width': 1500, 'size': 50,
          'numbered': True, 'gap': 38,
          'bullets': [{'text': 'VIX가 40을 처음 넘은 날 TQQQ 매수', 'on': 1, 'highlight': 'TQQQ', 'hl_color': 'up'},
                      {'text': '1년 들고 있기', 'on': 1, 'offset': 1.4},
                      {'text': '2010년 이전은 가상 TQQQ로 계산', 'sub': '나스닥100 하루 수익률 × 3', 'on': 2}],
          'narration': ["규칙은 이래요. VIX가 40을 처음 넘은 날, TQQQ를 사서 1년 들고 있는다.",
                        "TQQQ가 없던 2010년 이전은, 나스닥100 하루 수익률의 3배로 가상 계산했어요."]})
S.append({'type': 'yearbars', 'chapter': 'VIX + TQQQ', 'which': 'vix', 'on': 2, 'step': 0.3, 'vmax': 200,
          'heading': 'VIX 40 첫 돌파일에 3배 레버리지 → 1년 뒤 (%)', 'sub': '1998 ~ 2025 · 11번',
          'mark': {'01.09': '9·11', '08.09': '금융위기'}, 'mark_on': 4, 'source': LEV,
          'narration': ["1998년부터 지금까지, 이런 날은 모두 11번 있었습니다.", "1년 뒤 결과를 보시면요.",
                        "대부분 100% 안팎으로 올랐어요. 1998년엔 무려 514%.",
                        "근데 파란 막대 두 개가 보이죠. 9·11 직후랑, 금융위기 때입니다."]})
S.append({'type': 'bignum', 'chapter': 'VIX + TQQQ', 'label': 'VIX 40 + 3배 레버리지, 1년 뒤 평균', 'from': 0, 'to': 117.2,
          'fmt': '+{:.0f}%', 'final': '+117%', 'size': 210, 'on': 1, 'dur': 1.2, 'color': 'up', 'sub': '11번 중 9번 플러스', 'sub_on': 2,
          'sfx_end': 'cash',
          'narration': ["평균은, 117%.", "11번 중 9번 플러스였어요."]})
S.append(VS(["같은 날 레버리지 없이 나스닥100을 샀다면, 평균 35.4%.", "3배로 들어가니까, 수익도 3배 넘게 커진 거죠."], "VIX 40 넘은 날 사서 1년 뒤",
            {'title': '나스닥100 (1배)', 'value': '+35.4%', 'sub': '11번 평균', 'color': 'neutral', 'on': 1},
            {'title': '3배 레버리지', 'value': '+117%', 'sub': '11번 평균', 'color': 'up', 'on': 2}, ch="VIX + TQQQ"))
S.append(K(["근데요. 평균 뒤에 숨은 두 번을, 꼭 보셔야 합니다."], "평균 뒤에 숨은 두 번", hl="두 번", hc='down', size=130))
S.append({'type': 'chart', 'chapter': 'VIX + TQQQ', 'chart': {
    'series': 'sim3x_ndx', 'start': '2001-07-01', 'end': '2002-10-31', 'color': [74, 144, 255], 'title': '가상 TQQQ · 2001 ~ 2002', 'ymin': 0,
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2001-09-17', 'label': 'VIX 41.8 매수', 'sub': '9·11 직후', 'on': 1, 'offset': 0.8, 'dy': -80, 'dx': 80, 'color': 'gold'},
              {'date': '2002-09-17', 'label': '1년 뒤 -80%', 'on': 2, 'dy': -70, 'dx': -60, 'color': 'down', 'size': 36}],
    'source': LEV},
    'shake': [{'on': 2, 'offset': 0.3, 'dur': 0.5, 'amp': 14, 'sfx': 'boom'}],
    'narration': ["2001년 9·11 직후, VIX가 41.8을 찍은 날 샀다면요.", "1년 뒤, 마이너스 80%. 1억이 2천만 원이 됩니다."]})
S.append({'type': 'chart', 'chapter': 'VIX + TQQQ', 'chart': {
    'series': 'sim3x_ndx', 'start': '2008-08-01', 'end': '2009-10-31', 'color': [74, 144, 255], 'title': '가상 TQQQ · 2008 ~ 2009', 'ymin': 0,
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2008-09-29', 'label': 'VIX 46.7 매수', 'on': 1, 'offset': 0.8, 'dy': -80, 'dx': 80, 'color': 'gold'},
              {'date': '2009-03-09', 'label': '5개월 뒤 -78%', 'on': 2, 'dy': -90, 'dx': 60, 'color': 'down', 'size': 36}],
    'source': LEV},
    'narration': ["2008년 금융위기 때는 9월 말에 VIX 40을 넘었는데,", "진짜 바닥은 5개월 뒤였어요. 그 사이 78%가 빠졌습니다."]})
S.append(VS(["11번 전체로 보면, 산 뒤 1년 안에 겪은 최대 하락이 평균 28.8%.", "최악은 80.8%였어요."], "VIX 40에 3배로 산 뒤, 1년 안에 겪은 하락",
            {'title': '평균', 'value': '-28.8%', 'sub': '11번 평균', 'color': 'down', 'on': 1},
            {'title': '최악', 'value': '-80.8%', 'sub': '2001년 9·11 직후', 'color': 'down', 'on': 2}, ch="VIX + TQQQ"))
S.append(K(["솔직히 물어볼게요. | 1억이 2천만 원이 되는 걸, 1년 동안 버틸 수 있으세요?"], "1억 → 2천만 원\n버틸 수 있나요?",
           hl="버틸 수 있나요?", hc='down', size=120))
S.append({'type': 'chart', 'chapter': '최근 사례', 'chart': {
    'series': 'tqqq', 'start': '2020-01-01', 'end': '2021-03-31', 'color': [240, 84, 84], 'title': 'TQQQ · 2020 코로나', 'ymin': 0,
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2020-02-28', 'label': 'VIX 40.1 매수', 'on': 1, 'offset': 0.6, 'dy': -80, 'dx': -40, 'color': 'gold'},
              {'date': '2020-03-20', 'label': '3주 뒤 -54%', 'on': 2, 'dy': 50, 'dx': 100, 'color': 'down'},
              {'date': '2021-02-26', 'label': '1년 뒤 +132%', 'on': 3, 'dy': -70, 'dx': -80, 'color': 'up'}],
    'source': '자료: TQQQ 수정주가'},
    'narration': ["최근엔 결과가 좋았어요. 2020년 2월 말, VIX 40을 넘은 날 샀다면,", "3주 만에 54%가 빠졌다가,", "1년 뒤엔 132%로 끝났습니다."]})
S.append({'type': 'chart', 'chapter': '최근 사례', 'chart': {
    'series': 'tqqq', 'start': '2025-01-01', 'end': '2026-04-30', 'color': [240, 84, 84], 'title': 'TQQQ · 2025 관세 충격', 'ymin': 0,
    'draw': {'on': 1, 'dur': 2.0},
    'marks': [{'date': '2025-04-04', 'label': 'VIX 45.3 매수', 'on': 1, 'offset': 0.6, 'dy': 60, 'dx': -100, 'color': 'gold'},
              {'date': '2026-04-02', 'label': '1년 뒤 +112%', 'on': 2, 'dy': -70, 'dx': -80, 'color': 'up'}],
    'source': '자료: TQQQ 수정주가'},
    'narration': ["작년 4월 관세 충격 때도, VIX 45를 넘은 날 샀다면", "1년 뒤 112%였죠. 최근 두 번은 대박이었던 겁니다."]})
S.append(K(["근데 그게 함정이에요. | 최근 성공만 보고 들어가면, 9·11이나 금융위기 같은 날을 만났을 때 버티질 못하거든요."],
           "최근 성공이 함정", hl="함정", hc='down', size=140))

# ── 함정
S.append(K(["그래서 이 매매법을 믿기 전에, | 꼭 알아야 할 것들이 있습니다."], "믿기 전에 알아야 할 것", hl="알아야 할 것", size=110, ch="함정"))
for txt, sub_, line in [
    ("표본이 너무 적다", "-30% 하락장 7번 · VIX 40 돌파 11번 (2020년엔 3번이 몰림)",
     "첫째. 표본이 너무 적어요. | -30% 하락장은 100년에 7번, VIX 40은 11번뿐이고, 2020년엔 3번이 몰려 있었습니다."),
    ("첫 신호는 바닥이 아니다", "2008년: VIX 40 첫 돌파 → 진짜 바닥은 5개월 뒤",
     "둘째. 첫 신호는 바닥이 아니에요. | 2008년처럼 신호가 뜨고도 몇 달을 더 빠질 수 있습니다."),
    ("레버리지는 회복이 훨씬 어렵다", "-80%를 메우려면 +400%가 필요",
     "셋째. 레버리지는 회복이 훨씬 어려워요. | 80% 빠지면, 본전까지 400%가 올라야 합니다."),
    ("2010년 이전은 가상 계산", "실제 TQQQ보다 유리하게 계산됨 (차입비용 미반영)",
     "넷째. 2010년 이전은 가상 계산이에요. | 실제보다 유리하게 잡혀 있어서, 현실은 더 나빴을 수 있습니다."),
    ("세금과 환율", "해외주식 양도차익 22% (연 250만 원 공제) · 환율 변동",
     "다섯째. 세금과 환율. | 해외주식은 수익에서 연 250만 원을 빼고 22%가 양도소득세고, 환율도 같이 움직여요."),
]:
    S.append({'type': 'card', 'chapter': '함정', 'heading': txt, 'width': 1500, 'size': 52, 'icon': 'dash',
              'bullets': [{'text': sub_, 'on': 1}], 'narration': [line]})

# ── 템플턴과의 차이
S.append(K(["그리고 가장 중요한 거요. | 템플턴이 한 거랑, VIX 40 TQQQ 매매법은 완전히 달라요."], "템플턴과 결정적 차이", hl="결정적 차이", size=120, ch="템플턴과의 차이"))
S.append(VS(["템플턴은 104개 회사에 나눠서 샀고, 4년을 기다렸어요.", "VIX 매매법은 하나의 3배 상품에, 1년 승부죠."], "같은 역발상, 다른 방식",
            {'title': '템플턴 (1939)', 'value': '104개 분산', 'sub': '4년 보유 · 가치를 보고 샀다', 'color': 'gold', 'on': 1},
            {'title': 'VIX 40 TQQQ', 'value': '1개 × 3배', 'sub': '1년 승부 · 공포 숫자만 보고 산다', 'color': 'down', 'on': 2}, ch="템플턴과의 차이"))
S.append({'type': 'card', 'chapter': '활용', 'heading': '개인 투자자는 이렇게', 'highlight': '이렇게', 'width': 1500, 'size': 50,
          'numbered': True, 'gap': 38,
          'bullets': [{'text': '공포가 오기 전에, 살 현금을 미리', 'on': 1},
                      {'text': '한 번에 말고, 나눠서 들어가기', 'on': 2},
                      {'text': '레버리지는 -80%를 버틸 만큼만', 'on': 3, 'highlight': '-80%', 'hl_color': 'down'}],
          'narration': ["그럼 개인 투자자는 어떻게 쓰면 좋을까요? | 첫째, 공포가 오기 전에 살 현금을 미리 준비해 두기.",
                        "둘째, 한 번에 다 넣지 말고, 나눠서 들어가기. | 바닥은 아무도 모르니까요.",
                        "셋째, 레버리지를 쓴다면, 마이너스 80%를 맞아도 버틸 수 있는 만큼만."]})

# ── 결론
S.append(K(["자, 오늘 확인한 거 정리해 볼게요."], "오늘의 결론", size=140, ch="오늘의 결론", bg="CHECK"))
for txt, st, c, line in [
    ("-30%에 샀다면 5년 뒤", "7번 중 6번 상승", "up", "S&P500이 30% 빠졌을 때 샀다면, 5년 뒤엔 7번 중 6번 플러스였어요."),
    ("산 다음 더 빠진 폭", "평균 -27%, 최악 -79%", "down", "단, 산 다음에도 평균 27%는 더 빠졌습니다."),
    ("VIX 40에 3배 레버리지", "평균 +117%", "up", "VIX 40에 3배로 들어가면, 1년 뒤 평균 117%."),
    ("그 뒤에 숨은 것", "최악 -80%", "down", "그 뒤엔 마이너스 80%가 숨어 있었고요."),
]:
    S.append(K([line], txt, size=110, ch="오늘의 결론",
               stamp={'text': st, 'color': c, 'on': 1, 'offset': 0.6, 'pos': [960, 700], 'rot': -5, 'size': 72}))
S.append(K(["공포에 사는 건 용기가 아니라, 준비예요. | 버틸 수 있는 사람만, 그 수익을 가져갔습니다."],
           "공포에 사는 건\n용기가 아니라 준비", hl="준비", size=120, ch="오늘의 결론"))
S.append({'type': 'outro', 'heading': '공포에 사는 건\n버틸 수 있는 사람의 몫', 'highlight': '버틸 수 있는 사람',
          'sub': '궁금한 주제 · 종목 · 매매법, 댓글로 남겨주세요',
          'disclaimer': '본 영상은 투자 교육 목적이며, 특정 종목·ETF의 매수·매도 추천이 아닙니다.\n레버리지 ETF는 원금 대부분을 잃을 수 있으며, 과거 데이터는 미래 수익을 보장하지 않습니다.',
          'subscribe_on': 3, 'signature': CH['signature'], 'signature_on': 4,
          'narration': ["공포에 사는 건, 결국 버틸 수 있는 사람의 몫입니다.",
                        "여러분은 하락장에 들어갈 수 있으세요? | 궁금했던 주제, 종목, 매매법, 뭐든 댓글로 남겨 주세요. 다음 영상에서 데이터로 끝까지 파헤쳐 드리겠습니다.",
                        CH['outro_fixed'], CH['signature']]})

body = yaml.safe_dump({'scenes': S}, allow_unicode=True, sort_keys=False, width=200, default_flow_style=None)
body = body.replace("'on':", "on:")
open(P, 'w', encoding='utf-8').write(head_yaml + body)
print(len(S), 'slides; kinetic', sum(1 for x in S if x['type'] == 'kinetic'))
