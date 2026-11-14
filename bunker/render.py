#!/usr/bin/env python3
"""Бункер за 25 000 $ — серия 1. Процедурная 2D-анимация (1080x1920, 30 fps).

Использование:
  python3 render.py --timings timings.json --audio voice.mp3 --out ep1.mp4
Без --timings длительности сегментов оцениваются по длине текста.
"""
import argparse, json, math, random, subprocess, re
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
GROUND = 1010          # верх травы
SOIL_TOP = GROUND + 26
SOIL_BOT = 1360
CAP_Y = 1470

FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
_fc = {}
def font(size, bold=False):
    k = (size, bold)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONT_B if bold else FONT, size)
    return _fc[k]

# ---------- палитра ----------
SKY_TOP = (18, 24, 48); SKY_BOT = (44, 58, 92)
RED_TOP = (60, 10, 16); RED_BOT = (170, 60, 30)
MOUNT = (30, 40, 66); TREE = (22, 52, 46); TREE2 = (28, 64, 54)
GRASS = (62, 130, 70); SOIL = (78, 54, 38); SOIL2 = (64, 44, 30); SOIL3 = (92, 66, 46)
BOTTOM = (22, 18, 20)
WHITE = (245, 245, 240); GREY = (120, 120, 128); YEL = (255, 204, 40); RED = (235, 58, 52)
GREEN = (70, 210, 110); BLUE = (70, 150, 255); WATER = (60, 120, 200)

def lerp(a, b, t): return a + (b - a) * t
def lc(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_io(t): t = clamp(t); return t * t * (3 - 2 * t)
def pop(t):  # масштаб «выпрыгивания» 0..1 с перелётом
    t = clamp(t / 0.35)
    return 1 + 0.25 * math.sin(t * math.pi) * (1 - t) if t < 1 else 1.0 if t >= 1 else t

def back_out(t):
    t = clamp(t); c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

# ---------- сценарий ----------
# *текст* — жёлтый, !текст! — красный
SEGMENTS = [
    dict(cap="Вчера по всем каналам объявили: через *год* — !конец света!.", scene="tv"),
    dict(cap="К Земле летит !астероид!. Выжить можно только *под землёй*.", scene="asteroid"),
    dict(cap="Денег у меня нет. Поэтому я иду в *банк*.", scene="bank"),
    dict(cap="Беру кредит — *25 000 $*. Возвращать всё равно будет !некому!.", scene="loan",
         budget=25000, delta=25000),
    dict(cap="Но что, если конец света !не наступит!?", scene="doubt"),
    dict(cap="Тогда у меня будет бункер и огромный !долг!. Но рисковать не буду — *строю*.", scene="doubt2"),
    dict(cap="Что нужно бункеру? Участок. Котлован. Стены. Воздух.", scene="list"),
    dict(cap="Пункт первый: *участок*.", scene="city", tag="1. УЧАСТОК"),
    dict(cap="В городе земля стоит как !самолёт!.", scene="city_price", tag="1. УЧАСТОК"),
    dict(cap="Нахожу заброшенное поле за 100 км. *4 000 $*.", scene="field", tag="1. УЧАСТОК",
         budget=21000, days=352, pct=10, delta=-4000),
    dict(cap="Пункт второй: *котлован*.", scene="field2", tag="2. КОТЛОВАН"),
    dict(cap="Копать лопатой — !3 месяца!.", scene="shovel", tag="2. КОТЛОВАН"),
    dict(cap="Арендую *экскаватор*. Два дня — и яма *6 метров*.", scene="excav", tag="2. КОТЛОВАН",
         days=340),
    dict(cap="Минус *2 500 $*.", scene="pit", tag="2. КОТЛОВАН", budget=18500, pct=25, delta=-2500),
    dict(cap="Проверка. Ночью !ливень!.", scene="rain", tag="ПРОВЕРКА"),
    dict(cap="Утром в яме — !бассейн!.", scene="flood", tag="ПРОВЕРКА", days=338),
    dict(cap="Грунтовые воды. Ставлю *дренаж* и *насос*.", scene="pump", tag="ПРОВЕРКА"),
    dict(cap="Минус *1 500 $*. Яма сухая.", scene="dry", tag="ПРОВЕРКА", budget=17000, days=330,
         pct=30, delta=-1500),
    dict(cap="Осталось *17 000 $*.", scene="list2"),
    dict(cap="Пункт третий: *стены*. И тут два пути.", scene="choice", tag="3. СТЕНЫ"),
    dict(cap="*Бетон* — надёжно, но съест !половину бюджета!.", scene="choice_l", tag="3. СТЕНЫ"),
    dict(cap="Или *морской контейнер* — дёшево, но земля может его !раздавить!.", scene="choice_r",
         tag="3. СТЕНЫ"),
    dict(cap="Пиши в комментариях: *бетон* или *контейнер*.", scene="choice_vote", tag="3. СТЕНЫ"),
    dict(cap="В следующей серии строю то, что выберете вы.", scene="choice_vote2", tag="3. СТЕНЫ"),
]
END_CARD = 2.6
# настройки серии (серии 2+ переопределяют их в epN.py)
INIT = (365.0, 0.0, 0.0)          # дни, % бункера, бюджет на старте
EP_LABEL = "СЕРИЯ 1"
END_LINES = ("БЕТОН или КОНТЕЙНЕР?", "ПИШИ В КОММЕНТАРИЯХ")
CHECK_ITEMS = ["1. УЧАСТОК", "2. КОТЛОВАН", "3. СТЕНЫ", "4. ВОЗДУХ"]
CHECK_TITLE = "ЧТО НУЖНО БУНКЕРУ"
CHOICE_CARDS = [("БЕТОН", "concrete", (70, 150, 255), 280, "НАДЁЖНО", "ПОЛ-БЮДЖЕТА"),
                ("КОНТЕЙНЕР", "container", (255, 204, 40), 800, "ДЁШЕВО", "МОЖЕТ СМЯТЬ")]
ICONS = {}                        # kind -> fn(d, cx, cy, s) для своих иконок

# ---------- статичные слои ----------
rnd = random.Random(7)
STARS = [(rnd.randrange(W), rnd.randrange(60, 700), rnd.choice([2, 2, 3, 4]), rnd.random() * 6.28)
         for _ in range(90)]
SOIL_DOTS = [(rnd.randrange(W), rnd.randrange(SOIL_TOP + 10, SOIL_BOT), rnd.choice([4, 6, 8]))
             for _ in range(160)]
RAIN = [(rnd.randrange(W + 300), rnd.randrange(H), rnd.uniform(0.8, 1.3)) for _ in range(260)]


def make_sky(top, bot):
    im = Image.new("RGB", (W, GROUND))
    d = ImageDraw.Draw(im)
    for y in range(GROUND):
        d.line([(0, y), (W, y)], fill=lc(top, bot, y / GROUND))
    return im

SKY_N = make_sky(SKY_TOP, SKY_BOT)
SKY_R = make_sky(RED_TOP, RED_BOT)


def draw_landscape(d, trees=True):
    # горы
    d.polygon([(0, 800), (140, 690), (300, 780), (470, 660), (640, 770), (800, 680), (960, 760),
               (1080, 700), (1080, GROUND), (0, GROUND)], fill=MOUNT)
    if trees:
        for i, x in enumerate(range(-20, W + 40, 46)):
            h = 90 + (i * 37) % 60
            col = TREE if i % 2 else TREE2
            d.polygon([(x, GROUND - h), (x - 30, GROUND), (x + 30, GROUND)], fill=col)


def draw_ground(d, pit_w=0, pit_d=0, water=0.0, cx=540, wet=0.0):
    d.rectangle([0, GROUND, W, SOIL_TOP], fill=GRASS)
    d.rectangle([0, SOIL_TOP, W, SOIL_BOT], fill=SOIL)
    for i in range(3):  # слои грунта
        y = SOIL_TOP + 70 + i * 90
        d.rectangle([0, y, W, y + 6], fill=SOIL2)
    for x, y, r in SOIL_DOTS:
        d.ellipse([x - r, y - r, x + r, y + r], fill=SOIL3)
    # грунтовая вода внизу
    gw = lc((50, 80, 120), WATER, wet)
    d.rectangle([0, SOIL_BOT - 34, W, SOIL_BOT], fill=gw)
    if pit_w > 0 and pit_d > 0:
        x0, x1 = cx - pit_w / 2, cx + pit_w / 2
        d.rectangle([x0, GROUND, x1, GROUND + pit_d], fill=(40, 28, 22))
        d.rectangle([x0, GROUND + pit_d - 8, x1, GROUND + pit_d], fill=SOIL2)
        if water > 0:
            wy = GROUND + pit_d - pit_d * water
            d.rectangle([x0, wy, x1, GROUND + pit_d], fill=WATER)
            d.rectangle([x0, wy, x1, wy + 6], fill=(120, 180, 240))


def draw_sky(img, t, red=0.0):
    if red <= 0:
        img.paste(SKY_N, (0, 0))
    elif red >= 1:
        img.paste(SKY_R, (0, 0))
    else:
        img.paste(Image.blend(SKY_N, SKY_R, red), (0, 0))
    d = ImageDraw.Draw(img)
    for x, y, r, ph in STARS:
        a = 0.5 + 0.5 * math.sin(t * 2 + ph)
        if red < 0.5:
            c = lc((60, 70, 110), (230, 230, 255), a)
            d.ellipse([x - r / 2, y - r / 2, x + r / 2, y + r / 2], fill=c)
    # луна
    if red < 0.5:
        d.ellipse([90, 330, 180, 420], fill=(240, 236, 210))
        d.ellipse([117, 320, 207, 410], fill=lc(SKY_TOP, SKY_BOT, 0.2))
    return d

# ---------- персонажи и объекты ----------

def draw_hero(d, x, y, s=1.0, t=0.0, walk=False, shovel=False, dig=0.0, face=1):
    """x,y — точка у ног."""
    bob = abs(math.sin(t * 9)) * 6 * s if walk else 0
    leg = math.sin(t * 9) * 14 * s if walk else 0
    # ноги
    d.line([(x - 10 * s, y - 70 * s - bob), (x - 12 * s + leg, y)], fill=(48, 60, 90), width=int(16 * s))
    d.line([(x + 10 * s, y - 70 * s - bob), (x + 12 * s - leg, y)], fill=(48, 60, 90), width=int(16 * s))
    d.ellipse([x - 24 * s + leg, y - 8 * s, x - 2 * s + leg, y + 6 * s], fill=(30, 30, 34))
    d.ellipse([x + 2 * s - leg, y - 8 * s, x + 24 * s - leg, y + 6 * s], fill=(30, 30, 34))
    # туловище (куртка хаки)
    by = y - 70 * s - bob
    d.rounded_rectangle([x - 30 * s, by - 90 * s, x + 30 * s, by + 4 * s], radius=int(14 * s),
                        fill=(120, 128, 66))
    d.rectangle([x - 4 * s, by - 88 * s, x + 4 * s, by], fill=(96, 102, 52))
    # рука/лопата
    if shovel:
        ang = -0.6 + math.sin(dig * math.pi * 2) * 0.5
        hx, hy = x + 26 * s * face, by - 60 * s
        ex, ey = hx + math.cos(ang) * 70 * s * face, hy - math.sin(ang) * 70 * s
        d.line([(hx, hy), (ex, ey)], fill=(120, 128, 66), width=int(14 * s))
        sx, sy = ex + 40 * s * face, ey + 90 * s
        d.line([(ex - 30 * s * face, ey - 50 * s), (sx, sy)], fill=(140, 100, 60), width=int(8 * s))
        d.polygon([(sx - 14 * s, sy), (sx + 14 * s, sy), (sx + 8 * s, sy + 30 * s), (sx - 8 * s, sy + 30 * s)],
                  fill=(170, 175, 185))
    else:
        d.line([(x + 28 * s * face, by - 80 * s), (x + 36 * s * face, by - 20 * s)], fill=(120, 128, 66),
               width=int(14 * s))
    d.line([(x - 28 * s * face, by - 80 * s), (x - 36 * s * face, by - 20 * s)], fill=(120, 128, 66),
           width=int(14 * s))
    # голова
    hy = by - 120 * s
    d.ellipse([x - 26 * s, hy - 28 * s, x + 26 * s, hy + 28 * s], fill=(240, 196, 160))
    # кепка
    d.chord([x - 28 * s, hy - 34 * s, x + 28 * s, hy + 14 * s], 180, 360, fill=(200, 80, 40))
    d.rectangle([x + (0 if face > 0 else -44) * s, hy - 12 * s, x + (44 if face > 0 else 0) * s, hy - 4 * s],
                fill=(200, 80, 40))
    # глаза
    ex = x + 8 * s * face
    d.ellipse([ex - 4 * s, hy + 2 * s, ex + 4 * s, hy + 10 * s], fill=(30, 30, 30))
    d.ellipse([ex + 12 * s * face - 4 * s, hy + 2 * s, ex + 12 * s * face + 4 * s, hy + 10 * s], fill=(30, 30, 30))


def draw_excavator(d, x, arm, t):
    y = GROUND
    # гусеница
    d.rounded_rectangle([x - 120, y - 40, x + 120, y], radius=20, fill=(50, 50, 56))
    for i in range(6):
        cx = x - 95 + i * 38
        d.ellipse([cx - 14, y - 34, cx + 14, y - 6], fill=(90, 90, 96))
    # корпус
    d.rectangle([x - 100, y - 110, x + 90, y - 40], fill=(240, 180, 30))
    d.rectangle([x - 90, y - 190, x - 10, y - 110], fill=(240, 180, 30))
    d.rectangle([x - 80, y - 180, x - 20, y - 125], fill=(150, 200, 230))
    d.rectangle([x + 40, y - 150, x + 56, y - 110], fill=(60, 60, 60))
    # стрела
    bx, by = x + 60, y - 110
    a1 = -0.5 + arm * 1.1
    jx, jy = bx + math.cos(a1) * 200, by - math.sin(-a1) * 200 * -1
    jx, jy = bx + math.cos(a1) * 200, by + math.sin(a1) * 200 - 200 * (1 - arm) * 0.6
    d.line([(bx, by), (jx, jy)], fill=(230, 165, 20), width=26)
    a2 = 1.2 + arm * 0.5
    kx, ky = jx + math.cos(a2) * 150, jy + math.sin(a2) * 150
    d.line([(jx, jy), (kx, ky)], fill=(230, 165, 20), width=20)
    d.polygon([(kx - 30, ky - 10), (kx + 34, ky - 10), (kx + 20, ky + 40), (kx - 20, ky + 34)], fill=(70, 70, 76))
    return kx, ky


def draw_city(d, off=0):
    rnd2 = random.Random(3)
    x = int(-40 + off)
    while x < W + 80:
        w = rnd2.randrange(90, 160); h = rnd2.randrange(260, 620)
        d.rectangle([x, GROUND - h, x + w, GROUND], fill=(36, 44, 74))
        for wy in range(GROUND - h + 24, GROUND - 30, 44):
            for wx in range(x + 16, x + w - 24, 32):
                if rnd2.random() < 0.45:
                    d.rectangle([wx, wy, wx + 16, wy + 22], fill=(250, 210, 110))
        x += w + rnd2.randrange(8, 24)


def draw_fence(d, x0, x1):
    for x in range(int(x0), int(x1), 60):
        d.rectangle([x, GROUND - 90, x + 12, GROUND], fill=(130, 96, 62))
    d.rectangle([x0, GROUND - 74, x1, GROUND - 64], fill=(110, 80, 50))
    d.rectangle([x0, GROUND - 34, x1, GROUND - 24], fill=(110, 80, 50))


def draw_sign(d, x, text, s=1.0):
    d.rectangle([x - 6, GROUND - 200 * s, x + 6, GROUND], fill=(120, 88, 56))
    f = font(int(34 * s))
    tw = d.textlength(text, font=f)
    d.rectangle([x - tw / 2 - 20, GROUND - 270 * s, x + tw / 2 + 20, GROUND - 190 * s], fill=(236, 226, 200),
                outline=(120, 88, 56), width=6)
    d.text((x, GROUND - 230 * s), text, font=f, fill=(40, 30, 30), anchor="mm")


def draw_pump(d, x, t, on=True):
    y = GROUND
    d.rounded_rectangle([x - 60, y - 90, x + 60, y], radius=12, fill=(200, 60, 50))
    d.rectangle([x - 40, y - 110, x + 40, y - 90], fill=(60, 60, 66))
    d.ellipse([x - 26, y - 70, x + 26, y - 18], fill=(70, 70, 76))
    if on:
        a = t * 14
        d.line([(x, y - 44), (x + math.cos(a) * 22, y - 44 + math.sin(a) * 22)], fill=(220, 220, 220), width=6)


def draw_drop(d, x, y, r, col=WATER):
    d.polygon([(x, y - r * 1.8), (x - r * 0.9, y - r * 0.2), (x + r * 0.9, y - r * 0.2)], fill=col)
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)

# ---------- UI ----------

def text_w(d, s, f): return d.textlength(s, font=f)


def draw_tag(img, text, lt, col=None):
    d = ImageDraw.Draw(img)
    s = back_out(lt / 0.4)
    if s <= 0.01: return
    blue = text.startswith("ПРОВЕРКА")
    f = font(max(1, int(40 * s)))
    if text[0].isdigit() and not blue:
        num, rest = text.split(" ", 1)
        tw = text_w(d, num + " ", f) + text_w(d, rest, f)
        x0 = 540 - tw / 2
        d.rounded_rectangle([x0 - 22, 262 - 34 * s, x0 + tw + 22, 262 + 34 * s], radius=10, fill=(240, 236, 226))
        d.text((x0, 262), num + " ", font=f, fill=RED, anchor="lm")
        d.text((x0 + text_w(d, num + " ", f), 262), rest, font=f, fill=(30, 30, 40), anchor="lm")
    else:
        tw = text_w(d, text, f)
        d.rounded_rectangle([540 - tw / 2 - 22, 262 - 34 * s, 540 + tw / 2 + 22, 262 + 34 * s], radius=10,
                            fill=(20, 40, 90), outline=BLUE, width=5)
        d.text((540, 262), text, font=f, fill=(150, 200, 255), anchor="mm")


def fmt(n): return f"{int(n):,}".replace(",", " ")


def draw_hud(img, days, pct, budget, delta, delta_t):
    d = ImageDraw.Draw(img)
    boxes = [("ДО АПОКАЛИПСИСА", f"{int(days)} ДНЕЙ", RED, 30, 370),
             ("БУНКЕР", f"{int(pct)}%", GREEN, 395, 650),
             ("БЮДЖЕТ, $", fmt(budget), YEL, 675, 1050)]
    for lab, val, col, x0, x1 in boxes:
        d.rounded_rectangle([x0, 70, x1, 168], radius=14, fill=(26, 22, 28), outline=col, width=5)
        d.text(((x0 + x1) / 2, 96), lab, font=font(22, True), fill=lc(col, WHITE, 0.3), anchor="mm")
        d.text(((x0 + x1) / 2, 136), val, font=font(46), fill=WHITE, anchor="mm")
    if delta and 0 <= delta_t < 2.0:
        a = clamp(1 - (delta_t - 1.2) / 0.8)
        y = 196 + delta_t * 14
        if delta > 0:
            d.text((862, y), f"+{fmt(delta)} $", font=font(44), fill=lc((20, 40, 20), GREEN, a), anchor="mm")
        else:
            d.text((862, y), f"−{fmt(-delta)} $", font=font(44), fill=lc((40, 20, 20), RED, a), anchor="mm")


def parse_cap(cap):
    """-> list of (word, color)"""
    out = []
    for m in re.finditer(r"\*([^*]+)\*|!([^!]+)!|([^*!]+)", cap):
        if m.group(1): col, txt = YEL, m.group(1)
        elif m.group(2): col, txt = RED, m.group(2)
        else: col, txt = WHITE, m.group(3)
        for i, w in enumerate(re.split(r"(\s+)", txt)):
            if not w or w.isspace():
                continue
            # пунктуация, прилипшая к цветному слову
            if out and re.fullmatch(r"[.,:;?!]+", w):
                out[-1] = (out[-1][0] + w, out[-1][1], out[-1][2])
                continue
            out.append((w, col, txt.startswith(w) and False))
    return [(w, c) for w, c, _ in out]


def chunk_words(words, maxc=20):
    chunks, cur, n = [], [], 0
    for w in words:
        if cur and n + len(w[0]) > maxc:
            chunks.append(cur); cur, n = [], 0
        cur.append(w); n += len(w[0]) + 1
        if w[0][-1] in ".?:" and n > 8:
            chunks.append(cur); cur, n = [], 0
    if cur: chunks.append(cur)
    return chunks


def draw_caption(img, cap, p):
    d = ImageDraw.Draw(img)
    words = parse_cap(cap)
    chunks = chunk_words(words)
    total = sum(len(w) for c in chunks for w, _ in c)
    pos = p * total * 1.08
    acc = 0
    for ci, c in enumerate(chunks):
        clen = sum(len(w) for w, _ in c)
        if pos < acc + clen or ci == len(chunks) - 1:
            break
        acc += clen
    local = pos - acc
    f = font(64)
    parts = [(w.upper(), col) for w, col in c]
    sp = text_w(d, " ", f)
    tw = sum(text_w(d, w, f) for w, _ in parts) + sp * (len(parts) - 1)
    lines = [parts]
    if tw > 960:
        half = len(parts) // 2
        lines = [parts[:half], parts[half:]]
    y = CAP_Y - (len(lines) - 1) * 40
    seen = 0
    for ln in lines:
        lw = sum(text_w(d, w, f) for w, _ in ln) + sp * (len(ln) - 1)
        x = 540 - lw / 2
        for w, col in ln:
            spoken = local >= seen
            fill = col if spoken else lc(col, (40, 36, 40), 0.65)
            d.text((x + 4, y + 5), w, font=f, fill=(0, 0, 0), anchor="lm")
            d.text((x, y), w, font=f, fill=fill, anchor="lm")
            x += text_w(d, w, f) + sp
            seen += len(w)
        y += 80


def draw_stamp(img, text, lt, col=RED, cy=560):
    if lt < 0: return
    s = 1 + 1.5 * (1 - ease_out(lt / 0.25))
    f = font(int(76))
    tw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f)
    TW = int(tw + 120)
    tmp = Image.new("RGBA", (TW, 200), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rounded_rectangle([TW / 2 - tw / 2 - 30, 30, TW / 2 + tw / 2 + 30, 170], radius=14, fill=col + (235,),
                         outline=(255, 230, 230, 255), width=7)
    td.text((TW / 2, 100), text, font=f, fill=WHITE, anchor="mm")
    tmp = tmp.rotate(6 if TW < 1000 else 3, resample=Image.BICUBIC, expand=True)
    tmp = tmp.resize((int(tmp.width * s), int(tmp.height * s)), Image.BICUBIC)
    img.paste(tmp, (int(540 - tmp.width / 2), int(cy - tmp.height / 2)), tmp)


def draw_checklist(img, lt, checks=0, reveal=4.0, highlight=None, y0=330):
    d = ImageDraw.Draw(img)
    s = back_out(lt / 0.4)
    if s < 0.02: return
    items = CHECK_ITEMS
    x0, x1 = 300, 780
    tmp = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rounded_rectangle([10, 10, 510, 510], radius=10, fill=(246, 244, 236, 255))
    for i in range(7):
        td.line([(30, 120 + i * 56), (490, 120 + i * 56)], fill=(190, 205, 230, 255), width=2)
    td.text((260, 64), CHECK_TITLE, font=font(32), fill=(40, 40, 50, 255), anchor="mm")
    for i, it in enumerate(items):
        if i < reveal:
            yy = 150 + i * 80
            td.text((50, yy), it, font=font(44, True), fill=(30, 30, 40, 255), anchor="lm")
            if i < checks:
                td.line([(400, yy), (425, yy + 24), (470, yy - 28)], fill=(40, 190, 90, 255), width=10)
            if highlight == i:
                td.ellipse([30, yy - 40, 330, yy + 40], outline=(230, 50, 50, 255), width=6)
    tmp = tmp.rotate(-3, resample=Image.BICUBIC, expand=True)
    tmp = tmp.resize((int(tmp.width * s), int(tmp.height * s)), Image.BICUBIC)
    img.paste(tmp, (int(540 - tmp.width / 2), int(y0 + 260 - tmp.height / 2)), tmp)


def draw_bunker_icon(d, cx, cy, kind, s=1.0):
    if kind in ICONS:
        ICONS[kind](d, cx, cy, s)
    elif kind == "concrete":
        d.rectangle([cx - 150 * s, cy - 90 * s, cx + 150 * s, cy + 90 * s], fill=(150, 150, 150))
        d.rectangle([cx - 120 * s, cy - 60 * s, cx + 120 * s, cy + 60 * s], fill=(70, 70, 76))
        for i in range(-2, 3):
            d.line([(cx + i * 55 * s, cy - 90 * s), (cx + i * 55 * s, cy - 60 * s)], fill=(110, 110, 110),
                   width=int(4 * s))
        d.rectangle([cx - 30 * s, cy - 20 * s, cx + 30 * s, cy + 60 * s], fill=(100, 110, 120))
        d.ellipse([cx + 12 * s, cy + 14 * s, cx + 22 * s, cy + 24 * s], fill=(220, 200, 60))
    else:
        d.rectangle([cx - 160 * s, cy - 80 * s, cx + 160 * s, cy + 80 * s], fill=(40, 120, 160))
        for i in range(-7, 8):
            d.line([(cx + i * 20 * s, cy - 74 * s), (cx + i * 20 * s, cy + 74 * s)], fill=(30, 96, 130),
                   width=int(6 * s))
        d.rectangle([cx - 160 * s, cy - 80 * s, cx + 160 * s, cy + 80 * s], outline=(25, 80, 110),
                    width=int(8 * s))
        for rx, ry in [(-110, -40), (60, 30), (120, -50), (-40, 50)]:
            d.ellipse([cx + rx * s - 14 * s, cy + ry * s - 10 * s, cx + rx * s + 14 * s, cy + ry * s + 10 * s],
                      fill=(160, 90, 40))


def draw_choice(img, lt, gt, focus=None, vote=False):
    d = ImageDraw.Draw(img)
    cards = CHOICE_CARDS
    for i, (name, kind, col, cx, plus, minus) in enumerate(cards):
        s = back_out((lt - i * 0.15) / 0.45)
        if s < 0.02: continue
        foc = 1.0
        if focus is not None:
            foc = 1.08 if focus == i else 0.86
        if vote:
            foc = 1 + 0.04 * math.sin(gt * 6 + i * math.pi)
        s *= foc
        dim = focus is not None and focus != i
        cy = 640
        d.rounded_rectangle([cx - 230 * s, cy - 250 * s, cx + 230 * s, cy + 250 * s], radius=int(22 * s),
                            fill=(30, 34, 52) if not dim else (24, 26, 38), outline=col if not dim else GREY,
                            width=int(7 * s))
        draw_bunker_icon(d, cx, cy - 70 * s, kind, s * 0.95)
        fs_ = int(54 * s)
        while fs_ > 10 and d.textlength(name, font=font(fs_)) > 420 * s:
            fs_ -= 2
        d.text((cx, cy + 90 * s), name, font=font(fs_), fill=col if not dim else GREY, anchor="mm")
        d.text((cx, cy + 160 * s), "+ " + plus, font=font(int(32 * s), True), fill=GREEN if not dim else GREY,
               anchor="mm")
        d.text((cx, cy + 205 * s), "− " + minus, font=font(int(32 * s), True), fill=RED if not dim else GREY,
               anchor="mm")
    if lt > 0.5:
        s = back_out((lt - 0.5) / 0.4)
        d.ellipse([540 - 56 * s, 640 - 56 * s, 540 + 56 * s, 640 + 56 * s], fill=(240, 236, 226))
        d.text((540, 640), "ИЛИ", font=font(int(34 * s)), fill=(30, 30, 40), anchor="mm")


# ---------- сцены ----------

def render_scene(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    red = 0.0
    if sc == "asteroid":
        red = ease_io(lt / 0.8)
    elif sc == "bank":
        red = 1 - ease_io(lt / 0.8)
    elif sc == "apoc":
        red = ease_io(lt / 0.6)
    d = draw_sky(img, gt, red)
    city = sc in ("city", "city_price", "bank", "loan")
    if not city:
        draw_landscape(d)
    else:
        draw_landscape(d, trees=False)
        draw_city(d, off=-lt * 30)
    pit_w, pit_d, water, wet = 0, 0, 0.0, 0.0
    if sc == "excav":
        pit_w, pit_d = 360, 40 + 230 * ease_io((lt - 0.4) / max(0.1, seg["dur"] - 0.8))
    elif sc in ("pit", "rain", "flood", "pump", "dry", "choice", "choice_l", "choice_r",
                "choice_vote", "choice_vote2", "list2"):
        pit_w, pit_d = 360, 270
    if sc == "rain":
        water = 0.35 * ease_io(lt / seg["dur"]); wet = water
    elif sc == "flood":
        water = 0.35 + 0.5 * ease_io(lt / 0.8); wet = 1
    elif sc == "pump":
        water = 0.85 - 0.6 * ease_io((lt - 0.8) / max(0.1, seg["dur"] - 0.8)); wet = 1
    elif sc == "dry":
        water = 0.25 * (1 - ease_io(lt / 0.8)); wet = 0.6
    if sc == "shovel":
        pit_w, pit_d = 90, 12 + 10 * p
    draw_ground(d, pit_w, pit_d, water, cx=540, wet=wet)

    if sc == "tv":
        # телевизор с экстренным выпуском
        s_ = back_out(lt / 0.4)
        cx, cy, tw_, th_ = 445, 600, 680 * s_, 450 * s_
        if s_ > 0.02:
            d.rounded_rectangle([cx - tw_ / 2 - 24, cy - th_ / 2 - 24, cx + tw_ / 2 + 24, cy + th_ / 2 + 24],
                                radius=26, fill=(36, 36, 42))
            blink = int(gt * 3) % 2 == 0
            d.rectangle([cx - tw_ / 2, cy - th_ / 2, cx + tw_ / 2, cy + th_ / 2],
                        fill=(150, 20, 24) if blink else (120, 14, 20))
            d.line([(cx - 60, cy + th_ / 2 + 24), (cx - 110, cy + th_ / 2 + 80)], fill=(36, 36, 42), width=14)
            d.line([(cx + 60, cy + th_ / 2 + 24), (cx + 110, cy + th_ / 2 + 80)], fill=(36, 36, 42), width=14)
            d.text((cx, cy - th_ / 2 + 60 * s_), "СРОЧНО!", font=font(int(80 * s_) + 1), fill=WHITE, anchor="mm")
            # астероид на экране
            ax, ay = cx, cy + 10 * s_
            d.ellipse([ax - 70 * s_, ay - 60 * s_, ax + 70 * s_, ay + 60 * s_], fill=(110, 96, 84))
            d.ellipse([ax - 30 * s_, ay - 30 * s_, ax - 4 * s_, ay - 6 * s_], fill=(80, 70, 62))
            d.ellipse([ax + 14 * s_, ay + 6 * s_, ax + 44 * s_, ay + 32 * s_], fill=(80, 70, 62))
            # бегущая строка
            d.rectangle([cx - tw_ / 2, cy + th_ / 2 - 80 * s_, cx + tw_ / 2, cy + th_ / 2], fill=(250, 220, 40))
            tick = "КОНЕЦ СВЕТА ЧЕРЕЗ 365 ДНЕЙ  •  "
            f_ = font(int(40 * s_) + 1)
            bw, bh = int(tw_), int(80 * s_)
            band = Image.new("RGB", (max(1, bw), max(1, bh)), (250, 220, 40))
            bd = ImageDraw.Draw(band)
            twt = bd.textlength(tick, font=f_)
            x = -((lt * 260) % twt)
            while x < bw:
                bd.text((x, bh / 2), tick, font=f_, fill=(30, 20, 20), anchor="lm")
                x += twt
            img.paste(band, (int(cx - tw_ / 2), int(cy + th_ / 2 - bh)))
        draw_hero(d, 935, GROUND + 4, 1.4, gt, face=-1)
        if lt > 1.2:  # «!» над головой
            d.text((935, GROUND - 330), "!", font=font(110), fill=YEL, anchor="mm")
    elif sc == "asteroid":
        # огромный астероид в небе медленно растёт
        k_ = 0.6 + 0.4 * ease_io(lt / max(1, seg["dur"]))
        ax, ay, r = 700, 380, 150 * k_
        for q in range(10):
            tx, ty, rr = ax + (q + 1) * 26 * k_, ay - (q + 1) * 30 * k_, r * (1 - q * 0.08)
            d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=lc((255, 180, 80), (160, 40, 20), q / 10))
        d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=(120, 100, 86))
        for ox, oy, rr in [(-50, -40, 34), (40, 30, 44), (60, -60, 22), (-40, 60, 26)]:
            d.ellipse([ax + ox * k_ - rr * k_, ay + oy * k_ - rr * k_, ax + ox * k_ + rr * k_, ay + oy * k_ + rr * k_],
                      fill=(88, 74, 64))
        draw_hero(d, 300, GROUND + 4, 1.5, gt)
        if lt > 0.9:
            # стрелка «под землю»
            d.polygon([(540, GROUND + 60), (500, GROUND + 60), (500, GROUND + 160), (460, GROUND + 160),
                       (520, GROUND + 250), (580, GROUND + 160), (540, GROUND + 160)], fill=YEL)
            d.text((620, GROUND + 160), "ПОД ЗЕМЛЮ", font=font(52), fill=YEL, anchor="lm")
    elif sc in ("bank", "loan"):
        # здание банка поверх города
        bx = 540
        d.polygon([(bx - 330, GROUND - 470), (bx, GROUND - 600), (bx + 330, GROUND - 470)], fill=(210, 206, 196))
        d.rectangle([bx - 310, GROUND - 470, bx + 310, GROUND - 420], fill=(196, 190, 180))
        for c_ in range(6):
            x = bx - 270 + c_ * 108
            d.rectangle([x - 22, GROUND - 420, x + 22, GROUND - 40], fill=(226, 222, 212))
        d.rectangle([bx - 330, GROUND - 40, bx + 330, GROUND], fill=(180, 174, 164))
        d.text((bx, GROUND - 510), "БАНК", font=font(64), fill=(40, 40, 50), anchor="mm")
        d.rectangle([bx - 60, GROUND - 200, bx + 60, GROUND - 40], fill=(60, 50, 44))
        if sc == "bank":
            wt = clamp(lt / 1.8)
            draw_hero(d, lerp(-60, 420, ease_out(wt)), GROUND + 4, 1.4, gt, walk=wt < 1)
        else:
            draw_hero(d, 420, GROUND + 4, 1.4, gt)
            # договор
            s_ = back_out(lt / 0.4)
            if s_ > 0.02:
                cx, cy = 720, 560
                d.rectangle([cx - 150 * s_, cy - 190 * s_, cx + 150 * s_, cy + 190 * s_], fill=(246, 244, 236))
                d.text((cx, cy - 140 * s_), "КРЕДИТ", font=font(int(46 * s_) + 1), fill=(30, 30, 40), anchor="mm")
                d.text((cx, cy - 70 * s_), "25 000 $", font=font(int(52 * s_) + 1), fill=(200, 140, 10), anchor="mm")
                for q in range(4):
                    yy = cy - 10 * s_ + q * 40 * s_
                    d.line([(cx - 110 * s_, yy), (cx + 110 * s_, yy)], fill=(180, 180, 190), width=5)
                d.text((cx, cy + 165 * s_), "мелкий шрифт...", font=font(int(22 * s_) + 1, True),
                       fill=(150, 150, 160), anchor="mm")
            draw_stamp(img, "ОДОБРЕНО", lt - 0.8, col=(40, 160, 80), cy=640)
            # дождь из монет
            for k in range(9):
                ct = (lt * 1.4 + k * 0.37) % 1.0
                cx_ = 120 + k * 105; cy_ = 300 + ct * 650
                d.ellipse([cx_ - 22, cy_ - 22, cx_ + 22, cy_ + 22], fill=(255, 200, 40), outline=(200, 140, 20),
                          width=5)
                d.text((cx_, cy_), "$", font=font(26), fill=(170, 110, 10), anchor="mm")
    elif sc in ("doubt", "doubt2"):
        draw_hero(d, 540, GROUND + 4, 1.7, gt, shovel=(sc == "doubt2"), dig=lt)
        if sc == "doubt":
            s_ = back_out(lt / 0.5)
            wob = math.sin(gt * 5) * 6
            d.text((540 + wob, 520), "?", font=font(int(300 * s_) + 1), fill=YEL, anchor="mm",
                   stroke_width=10, stroke_fill=(20, 16, 20))
        else:
            draw_stamp(img, "ДОЛГ 25 000 $", lt - 0.2, cy=430)
            if lt > 1.6:
                draw_stamp(img, "СТРОЮ!", lt - 1.6, col=(40, 160, 80), cy=620)
    elif sc == "intro":
        draw_hero(d, 540, GROUND + 4, 1.6, gt)
        f = font(int(96 * back_out(lt / 0.5)) + 1)
        d.text((540, 430), "БУНКЕР", font=f, fill=WHITE, anchor="mm")
        d.text((540, 540), "ЗА 25 000 $", font=f, fill=YEL, anchor="mm")
        # монеты
        for k in range(5):
            ct = (lt * 1.2 + k * 0.2) % 1.2
            cx = 380 + k * 80; cy = 700 - math.sin(ct / 1.2 * math.pi) * 80
            d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 200, 40), outline=(200, 140, 20), width=5)
            d.text((cx, cy), "$", font=font(26), fill=(170, 110, 10), anchor="mm")
    elif sc == "apoc":
        # падающий метеор и вспышка
        mt = clamp(lt / 1.3)
        mx, my = lerp(1100, 700, mt), lerp(60, 640, mt)
        for k in range(14):
            tx, ty = mx + k * 22, my - k * 32
            r = 34 - k * 2
            d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=lc((255, 220, 120), (200, 60, 30), k / 14))
        d.ellipse([mx - 40, my - 40, mx + 40, my + 40], fill=(255, 240, 200))
        draw_hero(d, 330, GROUND + 4, 1.5, gt, face=1)
        draw_stamp(img, "АПОКАЛИПСИС", lt - 0.4, cy=430)
    elif sc == "task":
        draw_hero(d, 330, GROUND + 4, 1.5, gt)
        # чертёж бункера
        s = back_out(lt / 0.5)
        if s > 0.02:
            cx, cy = 690, 600
            d.rounded_rectangle([cx - 230 * s, cy - 170 * s, cx + 230 * s, cy + 170 * s], radius=12,
                                fill=(30, 80, 150), outline=(200, 230, 255), width=5)
            for k in range(-4, 5):
                d.line([(cx + k * 50 * s, cy - 160 * s), (cx + k * 50 * s, cy + 160 * s)], fill=(60, 110, 180),
                       width=2)
            d.rectangle([cx - 160 * s, cy - 40 * s, cx + 160 * s, cy + 110 * s], outline=WHITE, width=6)
            d.line([(cx - 160 * s, cy - 40 * s), (cx - 60 * s, cy - 120 * s), (cx - 60 * s, cy - 40 * s)],
                   fill=WHITE, width=6)
            d.line([(cx, cy - 40 * s), (cx, cy + 110 * s)], fill=WHITE, width=4)
            d.text((cx, cy - 135 * s), "БУНКЕР", font=font(int(40 * s)), fill=WHITE, anchor="mm")
    elif sc == "list":
        draw_hero(d, 150, GROUND + 4, 1.3, gt)
        reveal = 0 if p < 0.3 else 1 + (p - 0.3) / 0.7 * 4
        draw_checklist(img, lt, reveal=reveal)
    elif city:
        draw_hero(d, 540, GROUND + 4, 1.4, gt)
        if sc == "city_price":
            draw_stamp(img, "$ 500 000 / СОТКА", lt - 0.3, col=(200, 40, 40), cy=520)
            # самолётик
            px = lerp(-200, 1300, (lt / max(1, seg["dur"])))
            py = 380 + math.sin(lt * 3) * 10
            d.polygon([(px, py), (px - 150, py - 18), (px - 150, py + 18)], fill=(230, 230, 236))
            d.polygon([(px - 70, py), (px - 110, py - 70), (px - 130, py - 70), (px - 105, py)], fill=(200, 200, 210))
            d.polygon([(px - 70, py), (px - 110, py + 70), (px - 130, py + 70), (px - 105, py)], fill=(200, 200, 210))
    elif sc == "field":
        walk_t = clamp(lt / 1.6)
        draw_fence(d, 60, 1020)
        draw_sign(d, 820, "ПРОДАЁТСЯ")
        draw_hero(d, lerp(-60, 420, ease_out(walk_t)), GROUND + 4, 1.4, gt, walk=walk_t < 1)
        if lt > 1.0:
            draw_stamp(img, "КУПЛЕНО", lt - 1.0, col=(40, 160, 80), cy=520)
        d.text((540, 380), "100 КМ ОТ ГОРОДА", font=font(46), fill=WHITE, anchor="mm")
    elif sc == "field2":
        draw_fence(d, 60, 1020)
        draw_sign(d, 860, "МОЁ", 0.9)
        draw_hero(d, 300, GROUND + 4, 1.4, gt)
        # контур будущего котлована
        for x in range(360, 720, 40):
            d.line([(x, GROUND + 2), (x + 20, GROUND + 2)], fill=YEL, width=8)
    elif sc == "shovel":
        draw_fence(d, 60, 1020)
        draw_hero(d, 470, GROUND + 4, 1.4, gt, shovel=True, dig=lt * 1.5)
        draw_stamp(img, "3 МЕСЯЦА", lt - 0.5, cy=500)
    elif sc == "excav":
        draw_fence(d, 60, 240)
        arm = 0.5 + 0.5 * math.sin(lt * 3.2)
        draw_excavator(d, 230, arm, gt)
        draw_hero(d, 960, GROUND + 4, 1.2, gt)
        # отметка глубины
        if pit_d > 60:
            mx = 760
            d.line([(mx, GROUND), (mx, GROUND + pit_d)], fill=YEL, width=5)
            d.line([(mx - 14, GROUND + pit_d), (mx + 14, GROUND + pit_d)], fill=YEL, width=5)
            m = int(round(pit_d / 270 * 6))
            d.text((mx + 24, GROUND + pit_d / 2 + 10), f"{m} М", font=font(48), fill=YEL, anchor="lm")
        d.text((540, 400), f"ДЕНЬ {1 if lt < seg['dur'] / 2 else 2}", font=font(56), fill=WHITE, anchor="mm")
    elif sc == "pit":
        draw_fence(d, 60, 240)
        draw_hero(d, 860, GROUND + 4, 1.3, gt)
        mx = 760
        d.line([(mx, GROUND), (mx, GROUND + 270)], fill=YEL, width=5)
        d.text((mx + 24, GROUND + 145), "6 М", font=font(48), fill=YEL, anchor="lm")
        draw_stamp(img, "−2 500 $", lt - 0.2, cy=500)
    elif sc in ("rain", "flood", "pump", "dry"):
        draw_fence(d, 60, 240)
        if sc in ("pump", "dry"):
            draw_pump(d, 860, gt, on=(sc == "pump"))
            # шланг из ямы к насосу
            d.line([(560, GROUND + 230), (560, GROUND - 20), (800, GROUND - 20), (800, GROUND - 40)],
                   fill=(40, 40, 44), width=14)
            if sc == "pump":
                d.line([(920, GROUND - 60), (1080, GROUND - 60)], fill=(40, 40, 44), width=14)
                for k in range(6):
                    ft = (gt * 2 + k / 6) % 1
                    draw_drop(d, 1040 + ft * 40, GROUND - 60 + ft * 70, 9)
                # дренажная труба вдоль дна
                d.line([(360, GROUND + 266), (720, GROUND + 266)], fill=(220, 120, 40), width=10)
            draw_hero(d, 230 if sc == "pump" else 300, GROUND + 4, 1.2, gt)
        else:
            draw_hero(d, 860, GROUND + 4, 1.2, gt)
        if sc == "flood":
            # плавающая уточка
            wy = GROUND + 270 - 270 * water
            bx = 540 + math.sin(gt * 2) * 60
            d.ellipse([bx - 30, wy - 30, bx + 30, wy + 6], fill=(250, 210, 40))
            d.ellipse([bx + 4, wy - 56, bx + 40, wy - 20], fill=(250, 210, 40))
            d.polygon([(bx + 38, wy - 40), (bx + 58, wy - 36), (bx + 38, wy - 30)], fill=(240, 120, 30))
            draw_stamp(img, "БАССЕЙН", lt - 0.5, cy=500)
        if sc == "dry":
            draw_stamp(img, "СУХО", lt - 0.8, col=(40, 160, 80), cy=500)
    elif sc == "list2":
        draw_fence(d, 60, 240)
        draw_checklist(img, lt, checks=2 if lt > 0.5 else 1, reveal=4, highlight=2 if lt > 1.0 else None)
    elif sc.startswith("choice"):
        foc = {"choice_l": 0, "choice_r": 1}.get(sc)
        ctl = lt if sc == "choice" else 5.0
        draw_choice(img, ctl, gt, focus=foc, vote=sc.startswith("choice_vote"))
        if sc == "choice_vote2":
            s = back_out(lt / 0.5)
            d.text((540, 960), "СЕРИЯ 2 — ВЫБИРАЕТЕ ВЫ", font=font(int(46 * s) + 1), fill=YEL, anchor="mm")

    # рамка «вспышки» для апокалипсиса
    if sc == "apoc" and 1.2 < lt < 1.5:
        flash = Image.new("RGB", (W, H), (255, 230, 200))
        img.paste(Image.blend(img, flash, 0.6 * (1 - (lt - 1.2) / 0.3)))

    # дождь
    if sc == "rain" or (sc == "flood" and lt < 1.0):
        a = 1.0 if sc == "rain" else 1 - lt
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle([0, 0, W, SOIL_BOT], fill=(140, 150, 170, int(70 * a)))
        for x, y, sp in RAIN:
            yy = (y + gt * 1800 * sp) % (SOIL_BOT + 60)
            xx = (x - gt * 500 * sp) % (W + 300) - 150
            od.line([(xx, yy), (xx - 14, yy + 40)], fill=(200, 210, 230, int(170 * a)), width=3)
        img.paste(ov, (0, 0), ov)


def render_endcard(img, lt):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(14, 14, 20))
    s = back_out(lt / 0.5)
    d.text((540, 760), "БУНКЕР ЗА 25 000 $", font=font(int(70 * s) + 1), fill=WHITE, anchor="mm")
    d.text((540, 860), EP_LABEL, font=font(int(54 * s) + 1), fill=YEL, anchor="mm")
    d.text((540, 1040), END_LINES[0], font=font(int(52 * s) + 1), fill=WHITE, anchor="mm")
    d.text((540, 1120), END_LINES[1], font=font(int(40 * s) + 1, True), fill=GREY, anchor="mm")


# ---------- главный цикл ----------

def build_timeline(timings):
    t = timings.get("lead", 0.2) if timings else 0.2
    tl = []
    for i, seg in enumerate(SEGMENTS):
        if timings:
            st, en = timings["segments"][i]
            dur = en - t if i == 0 else None
        tl.append(seg)
    # длительности
    if timings:
        segs = timings["segments"]
        for i, seg in enumerate(SEGMENTS):
            start = segs[i][0] if i else 0.0
            end = segs[i + 1][0] if i + 1 < len(segs) else segs[i][1] + 0.6
            seg["start"], seg["dur"] = start, end - start
            seg["sp0"], seg["sp1"] = segs[i]  # интервал речи
    else:
        t = 0.0
        for seg in SEGMENTS:
            words = len(re.sub(r"[*!]", "", seg["cap"]))
            seg["dur"] = 0.5 + words * 0.068
            seg["start"] = t
            seg["sp0"], seg["sp1"] = t + 0.1, t + seg["dur"] - 0.3
            t += seg["dur"]
    return SEGMENTS[-1]["start"] + SEGMENTS[-1]["dur"]


def state_at(t):
    days, pct, budget = INIT
    delta, delta_t = None, -1
    for seg in SEGMENTS:
        if t < seg["start"]: break
        lt = t - seg["start"]
        k = ease_io(lt / 1.2)
        if "days" in seg:
            seg.setdefault("_d0", days)
            days = lerp(seg["_d0"], seg["days"], ease_io(lt / max(0.5, seg["dur"])))
        if "pct" in seg:
            seg.setdefault("_p0", pct)
            pct = lerp(seg["_p0"], seg["pct"], k)
        if "budget" in seg:
            seg.setdefault("_b0", budget)
            budget = lerp(seg["_b0"], seg["budget"], k)
            delta, delta_t = seg.get("delta"), lt
    return days, pct, budget, delta, delta_t


def prime_state():
    days, pct, budget = INIT
    for seg in SEGMENTS:
        if "days" in seg: seg["_d0"] = days; days = seg["days"]
        if "pct" in seg: seg["_p0"] = pct; pct = seg["pct"]
        if "budget" in seg: seg["_b0"] = budget; budget = seg["budget"]


def frame(t, total):
    img = Image.new("RGB", (W, H), BOTTOM)
    if t >= total:
        render_endcard(img, t - total)
        return img
    i = max(k for k, s in enumerate(SEGMENTS) if s["start"] <= t)
    seg = SEGMENTS[i]
    lt = t - seg["start"]
    # прогресс речи внутри сегмента для субтитров
    p = clamp((t - seg["sp0"]) / max(0.2, seg["sp1"] - seg["sp0"]))
    render_scene(img, seg, i, lt, p, t, None)
    d = ImageDraw.Draw(img)
    # нижняя подложка под субтитры
    d.rectangle([0, SOIL_BOT, W, H], fill=BOTTOM)
    if "tag" in seg:
        prev = SEGMENTS[i - 1].get("tag") if i else None
        tag_lt = lt if prev != seg["tag"] else 5
        if prev and prev != seg["tag"]:
            pass
        # находим начало блока с этим тегом
        j = i
        while j > 0 and SEGMENTS[j - 1].get("tag") == seg["tag"]:
            j -= 1
        draw_tag(img, seg["tag"], t - SEGMENTS[j]["start"])
    days, pct, budget, delta, delta_t = state_at(t)
    draw_hud(img, days, pct, budget, delta, delta_t)
    draw_caption(img, seg["cap"], p)
    # водяной знак серии
    d.text((W - 40, H - 120), EP_LABEL, font=font(30, True), fill=(90, 86, 96), anchor="rm")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timings")
    ap.add_argument("--audio")
    ap.add_argument("--music")
    ap.add_argument("--out", default="ep1.mp4")
    ap.add_argument("--preview", type=float, nargs="*")
    a = ap.parse_args()
    timings = json.load(open(a.timings)) if a.timings else None
    total = build_timeline(timings)
    prime_state()
    if a.preview is not None:
        for k, tt in enumerate(a.preview):
            frame(tt, total).save(f"preview_{k:02d}.jpg", quality=85)
        return
    dur = total + END_CARD
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if a.audio:
        cmd += ["-i", a.audio]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p"]
    if a.audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-t", f"{dur:.2f}", a.out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(dur * FPS)
    for f in range(n):
        pr.stdin.write(frame(f / FPS, total).tobytes())
    pr.stdin.close(); pr.wait()
    print("total", round(dur, 2), "s ->", a.out)


if __name__ == "__main__":
    main()
