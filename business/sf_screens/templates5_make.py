from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
D = os.path.dirname(os.path.abspath(__file__)) + "/"
FD = "/home/user/shorts-factory/server/fonts/"
W, H = 1080, 1920
SRC = Image.open(D + "src_50.jpg").convert("RGB")
HEAD = ["만원 속 혼천의", "세종대왕 것 아니다?"]
HL = "아니다?"
SUB = [("별 ", 0), ("1,400개", 1), (" 새긴 지도", 0)]


def F(s, w="Black"):
    return ImageFont.truetype(FD + f"Pretendard-{w}.otf", s)


def video(width, zoom=1.2):
    vw = int(width * zoom)
    vh = int(vw * 9 / 16)
    v = SRC.resize((vw, vh), Image.LANCZOS)
    x = (vw - width) // 2
    return v.crop((x, 0, x + width, vh))


def cover_burned(v, color=(0, 0, 0), a=235):
    # 원본 자막(아래쪽) 가리는 띠
    o = Image.new("RGBA", v.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    y = int(v.size[1] * 0.83)
    d.rectangle((0, y, v.size[0], int(v.size[1] * 0.985)), fill=color + (a,))
    return Image.alpha_composite(v.convert("RGBA"), o).convert("RGB")


def text_w(parts, f):
    return sum(f.getlength(t) for t, _ in parts)


def draw_parts(d, x, y, parts, f, fg, hl, stroke=0, sc=(0, 0, 0)):
    for t, h in parts:
        d.text((x, y), t, font=f, fill=hl if h else fg, stroke_width=stroke, stroke_fill=sc)
        x += f.getlength(t)


def head_lines(d, cy, f, fg, ac, stroke=0, sc=(0, 0, 0), lh=1.22):
    fs = f.size
    y = cy - len(HEAD) * fs * lh / 2
    for ln in HEAD:
        parts = [(ln[:ln.index(HL)], 0), (HL, 1)] if HL in ln else [(ln, 0)]
        x = (W - text_w(parts, f)) / 2
        draw_parts(d, x, y, parts, f, fg, ac, stroke, sc)
        y += fs * lh


def label(im, n, name):
    d = ImageDraw.Draw(im)
    f = F(40, "Bold")
    t = f"{n:02d}  {name}"
    w = f.getlength(t)
    d.rounded_rectangle((30, H - 100, 30 + w + 50, H - 30), 20, fill=(20, 20, 24))
    d.text((55, H - 92), t, font=f, fill=(255, 255, 255))


# 01 심플 화이트 (첨부 이미지 느낌)
def t1():
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    f = F(112)
    head_lines(d, 300, f, (255, 214, 0), (255, 214, 0), stroke=12, sc=(0, 0, 0))
    v = cover_burned(video(W, 1.35), (255, 255, 255), 0)  # 띠 없이, 자막 박스가 덮음
    vy = 540
    im.paste(v, (0, vy))
    f2 = F(92, "Bold")
    tw = text_w(SUB, f2)
    by = vy + int(v.size[1] * 0.83)
    bw = max(tw, 900)
    d.rectangle(((W - bw) / 2 - 34, by - 10, (W + bw) / 2 + 34, by + 120), fill=(0, 0, 0))
    draw_parts(d, (W - tw) / 2, by, SUB, f2, (255, 255, 255), (255, 255, 255))
    label(im, 1, "심플 화이트")
    return im


# 02 네온 다크 (지금 기본값)
def t2():
    im = Image.new("RGB", (W, H), (6, 8, 14))
    d = ImageDraw.Draw(im)
    head_lines(d, 230, F(104), (255, 255, 255), (34, 229, 255))
    d.rectangle((0, 422, W, 430), fill=(34, 229, 255))
    v = cover_burned(video(W, 1.35))
    vy = 500
    im.paste(v, (0, vy))
    f2 = F(120)
    tw = text_w(SUB, f2)
    draw_parts(d, (W - tw) / 2, vy + v.size[1] - 150, SUB, f2, (255, 255, 255), (255, 225, 40), 8)
    label(im, 2, "네온 다크 (현재 기본)")
    return im


# 03 이슈 속보형
def t3():
    im = Image.new("RGB", (W, H), (14, 22, 48))
    d = ImageDraw.Draw(im)
    f = F(44, "ExtraBold")
    d.rounded_rectangle((W / 2 - 150, 90, W / 2 + 150, 160), 14, fill=(232, 40, 40))
    t = "충격 사실"
    d.text((W / 2 - f.getlength(t) / 2, 97), t, font=f, fill=(255, 255, 255))
    head_lines(d, 300, F(100), (255, 255, 255), (255, 214, 0))
    v = cover_burned(video(W))
    vy = 500
    im.paste(v, (0, vy))
    d.rectangle((0, vy - 10, W, vy), fill=(232, 40, 40))
    d.rectangle((0, vy + v.size[1], W, vy + v.size[1] + 10), fill=(232, 40, 40))
    f2 = F(104)
    tw = text_w(SUB, f2)
    by = vy + v.size[1] - 160
    d.rectangle(((W - tw) / 2 - 30, by - 8, (W + tw) / 2 + 30, by + 128), fill=(255, 214, 0))
    draw_parts(d, (W - tw) / 2, by, SUB, f2, (10, 10, 10), (220, 30, 30))
    # 하단 티커
    ty = vy + v.size[1] + 60
    d.rectangle((0, ty, W, ty + 90), fill=(232, 40, 40))
    d.text((40, ty + 16), "LIVE  ·  만원 지폐 속 숨은 이야기", font=F(48, "Bold"), fill=(255, 255, 255))
    label(im, 3, "이슈 속보형")
    return im


# 04 블러 배경 몰입형
def t4():
    bg = SRC.resize((int(H * 16 / 9), H), Image.LANCZOS)
    x = (bg.size[0] - W) // 2
    bg = bg.crop((x, 0, x + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    im = bg
    d = ImageDraw.Draw(im)
    head_lines(d, 330, F(108), (255, 255, 255), (255, 214, 0), stroke=8)
    v = cover_burned(video(W, 1.3), (0, 0, 0), 200)
    vy = 600
    im.paste(v, (0, vy))
    f2 = F(120)
    tw = text_w(SUB, f2)
    draw_parts(d, (W - tw) / 2, vy + int(v.size[1] * 0.83) - 6, SUB, f2, (255, 255, 255), (255, 214, 0), 10)
    label(im, 4, "블러 배경 몰입형")
    return im


# 05 아이보리 노트형
def t5():
    im = Image.new("RGB", (W, H), (247, 241, 228))
    d = ImageDraw.Draw(im)
    for gx in range(0, W, 60):
        d.line((gx, 0, gx, H), fill=(234, 226, 208))
    for gy in range(0, H, 60):
        d.line((0, gy, W, gy), fill=(234, 226, 208))
    f = F(100)
    # 형광펜 밑줄
    ln = HEAD[1]
    y2 = 290
    x0 = (W - f.getlength(ln)) / 2
    d.rectangle((x0 + f.getlength(ln[:ln.index(HL)]) - 6, y2 + 70, x0 + f.getlength(ln) + 6, y2 + 118), fill=(255, 220, 80))
    head_lines(d, 290, f, (38, 40, 52), (226, 92, 64))
    v = cover_burned(video(W - 80, 1.25), (247, 241, 228), 0)
    vy = 540
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40 + 8, vy + 16, 40 + v.size[0] + 8, vy + v.size[1] + 16), 36, fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im = Image.alpha_composite(im.convert("RGBA"), sh).convert("RGB")
    m = Image.new("L", v.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, v.size[0], v.size[1]), 32, fill=255)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((28, vy - 12, 52 + v.size[0], vy + v.size[1] + 12), 42, fill=(255, 255, 255))
    im.paste(v, (40, vy), m)
    f2 = F(104)
    tw = text_w(SUB, f2)
    by = vy + v.size[1] - 170
    d.rounded_rectangle(((W - tw) / 2 - 44, by - 14, (W + tw) / 2 + 44, by + 124), 70, fill=(255, 255, 255))
    draw_parts(d, (W - tw) / 2, by, SUB, f2, (38, 40, 52), (226, 92, 64))
    label(im, 5, "아이보리 노트형")
    return im



def crop_box(w, h, fx=0.5, keep=0.82):
    # 원본 위쪽 82%만 사용(아래 원본 자막은 잘라냄) → 세로로 긴 칸에 꽉 채움
    sh = int(SRC.size[1] * keep)
    sw = int(sh * w / h)
    x = int(max(0, min(SRC.size[0] - sw, SRC.size[0] * fx - sw / 2)))
    return SRC.crop((x, 0, x + sw, sh)).resize((w, h), Image.LANCZOS)


# 03 빅 블랙 (본영상 꽉 차게)
def tb1():
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f = F(96)
    d.text(((W - f.getlength(HEAD[0])) / 2, 40), HEAD[0], font=f, fill=(255, 214, 0))
    parts = [(HEAD[1][:HEAD[1].index(HL)], 0), (HL, 1)]
    draw_parts(d, (W - text_w(parts, f)) / 2, 160, parts, f, (255, 255, 255), (240, 50, 40))
    vy, vh = 300, 1180
    im.paste(crop_box(W, vh, 0.7), (0, vy))
    f2 = F(118)
    tw = text_w(SUB, f2)
    draw_parts(d, (W - tw) / 2, vy + vh + 40, SUB, f2, (255, 255, 255), (255, 214, 0), 8)
    label(im, 3, "빅 블랙 (꽉 찬 화면)")
    return im


# 04 빅 풀스크린 (화면 전체 + 위아래 그라데이션)
def tb2():
    im = crop_box(W, H, 0.7).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for y in range(520):
        gd.line((0, y, W, y), fill=(0, 0, 0, int(215 * (1 - y / 520))))
    for y in range(1300, H):
        gd.line((0, y, W, y), fill=(0, 0, 0, int(215 * (y - 1300) / (H - 1300))))
    im = Image.alpha_composite(im, g).convert("RGB")
    d = ImageDraw.Draw(im)
    head_lines(d, 250, F(106), (255, 255, 255), (255, 214, 0), stroke=9)
    f2 = F(118)
    tw = text_w(SUB, f2)
    by = 1400
    d.rounded_rectangle(((W - tw) / 2 - 36, by - 10, (W + tw) / 2 + 36, by + 140), 24, fill=(255, 214, 0))
    draw_parts(d, (W - tw) / 2, by, SUB, f2, (10, 10, 10), (220, 30, 30))
    label(im, 4, "빅 풀스크린")
    return im


ims = [t() for t in (t1, t2, tb1, tb2, t5)]
for i, im in enumerate(ims, 1):
    im.save(D + f"tpl{i}.jpg", quality=90)
sw = 540
sheet = Image.new("RGB", (sw * 5 + 40 * 6, 960 + 80), (30, 30, 34))
for i, im in enumerate(ims):
    sheet.paste(im.resize((sw, 960), Image.LANCZOS), (40 + i * (sw + 40), 40))
sheet.save(D + "templates5.jpg", quality=90)
print("ok")
