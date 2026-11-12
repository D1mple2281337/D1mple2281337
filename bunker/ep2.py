#!/usr/bin/env python3
"""Бункер за 25 000 $ — серия 2 (зрители выбрали БЕТОН).

  python3 ep2.py --timings timings_ep2.json --audio audio/mix_ep2_norm.wav --out out/bunker_ep2.mp4
"""
import math, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from render import (W, H, GROUND, SOIL_TOP, font, lerp, lc, clamp, ease_io, ease_out, back_out,
                    WHITE, GREY, YEL, RED, GREEN, BLUE)

R.INIT = (330.0, 30.0, 17000.0)
R.EP_LABEL = "СЕРИЯ 2"
R.END_LINES = ("ЗАЙМ или СОСЕД?", "ПИШИ В КОММЕНТАРИЯХ")
R.CHOICE_CARDS = [("ЗАЙМ", "loan", RED, 280, "10 000 $ СРАЗУ", "ВЕРНУТЬ ЗА 3 МЕС."),
                  ("СОСЕД", "neighbor", GREEN, 800, "10 000 $", "МЕСТО В БУНКЕРЕ")]

R.SEGMENTS[:] = [
    dict(cap="Вы выбрали *бетон*. Значит, строю надёжно.", scene="recap"),
    dict(cap="Пункт третий: *стены*.", scene="walls", tag="3. СТЕНЫ"),
    dict(cap="Сначала арматура и опалубка. Минус *3 000 $*.", scene="rebar", tag="3. СТЕНЫ",
         budget=14000, delta=-3000),
    dict(cap="На участок заезжают *6 бетономешалок*.", scene="mixers", tag="3. СТЕНЫ"),
    dict(cap="Заливаю стены и потолок. Минус *5 500 $*.", scene="pour", tag="3. СТЕНЫ",
         budget=8500, delta=-5500, pct=50),
    dict(cap="Бетону нужно *28 дней*, чтобы набрать прочность.", scene="cure", tag="3. СТЕНЫ", days=300),
    dict(cap="Проверка: загоняю на крышу *экскаватор*.", scene="test", tag="ПРОВЕРКА"),
    dict(cap="Держит. Ни одной *трещины*.", scene="test_ok", tag="ПРОВЕРКА", pct=60),
    dict(cap="Деньги я храню в *бытовке*, прямо на участке.", scene="shed"),
    dict(cap="Ночью слышу !шум!.", scene="night"),
    dict(cap="Утром дверь бытовки !выбита!.", scene="broken", days=296),
    dict(cap="Украли генератор, инструменты и !почти все деньги!.", scene="stolen",
         budget=600, delta=-7900),
    dict(cap="Осталось !600 $!.", scene="left"),
    dict(cap="А впереди ещё дверь, вентиляция и запас еды.", scene="todo"),
    dict(cap="Без этого бункер — просто !бетонная коробка! в земле.", scene="box"),
    dict(cap="Денег взять негде. Осталось два варианта, и оба !плохие!.", scene="choice", tag="ВЫБОР"),
    dict(cap="Первый: *займ* у серьёзных людей. *10 000 $* сразу, но вернуть через !3 месяца!.",
         scene="choice_l", tag="ВЫБОР"),
    dict(cap="А если конец света не наступит, они придут за мной !раньше астероида!.",
         scene="choice_l2", tag="ВЫБОР"),
    dict(cap="Второй: *сосед*. Он даст *10 000 $*, но хочет !место в бункере!.",
         scene="choice_r", tag="ВЫБОР"),
    dict(cap="Только вот он слишком часто спрашивал, !где я храню деньги!.", scene="choice_r2", tag="ВЫБОР"),
    dict(cap="Пиши в комментариях: *займ* или *сосед*.", scene="choice_vote", tag="ВЫБОР"),
    dict(cap="Что будет дальше — решаете *вы*.", scene="choice_vote2", tag="ВЫБОР"),
]

CONCRETE = (150, 152, 156)
CONCRETE_D = (120, 122, 128)
INSIDE = (34, 30, 34)
PX0, PX1, PD = 360, 720, 270          # котлован/бункер


# ---------- объекты ----------

def draw_bunker(d, walls=1.0, roof=False, rebar=False, forms=False, cracks=False):
    """Разрез бункера в котловане. walls — доля залитых стен (0..1)."""
    d.rectangle([PX0, GROUND, PX1, GROUND + PD], fill=(40, 28, 22))
    th = 30
    hw = PD * walls
    if walls > 0:
        d.rectangle([PX0, GROUND + PD - hw, PX0 + th, GROUND + PD], fill=CONCRETE)
        d.rectangle([PX1 - th, GROUND + PD - hw, PX1, GROUND + PD], fill=CONCRETE)
        d.rectangle([PX0, GROUND + PD - th, PX1, GROUND + PD], fill=CONCRETE)
    if walls >= 1:
        d.rectangle([PX0 + th, GROUND + th if roof else GROUND, PX1 - th, GROUND + PD - th], fill=INSIDE)
    if roof:
        d.rectangle([PX0 - 10, GROUND, PX1 + 10, GROUND + th], fill=CONCRETE_D)
        d.rectangle([620, GROUND - 22, 680, GROUND], fill=(90, 96, 104))       # люк
    if forms:
        for x in (PX0 + th, PX1 - th - 10):
            d.rectangle([x, GROUND, x + 10, GROUND + PD], fill=(170, 120, 70))
    if rebar:
        for x in range(PX0 + 10, PX1, 28):
            d.line([(x, GROUND + PD - 10), (x, GROUND + PD - 26)], fill=(180, 90, 50), width=4)
        for y in range(GROUND + 20, GROUND + PD, 34):
            d.line([(PX0 + 14, y), (PX0 + 14, y + 20)], fill=(180, 90, 50), width=4)
            d.line([(PX1 - 14, y), (PX1 - 14, y + 20)], fill=(180, 90, 50), width=4)
        d.line([(PX0 + 14, GROUND + 10), (PX0 + 14, GROUND + PD - 10)], fill=(200, 110, 60), width=5)
        d.line([(PX1 - 14, GROUND + 10), (PX1 - 14, GROUND + PD - 10)], fill=(200, 110, 60), width=5)
        d.line([(PX0 + 14, GROUND + PD - 16), (PX1 - 14, GROUND + PD - 16)], fill=(200, 110, 60), width=5)
    if cracks:
        d.line([(500, GROUND + 5), (520, GROUND + 18), (510, GROUND + 28)], fill=(60, 60, 60), width=3)


def draw_mixer(d, x, t, drum_rot=0.0):
    y = GROUND
    for wx in (x - 110, x - 30, x + 90):
        d.ellipse([wx - 28, y - 56, wx + 28, y], fill=(30, 30, 34))
        d.ellipse([wx - 12, y - 40, wx + 12, y - 16], fill=(120, 120, 126))
    d.rectangle([x - 150, y - 70, x + 140, y - 50], fill=(60, 60, 66))
    d.rounded_rectangle([x + 70, y - 170, x + 150, y - 60], radius=12, fill=(230, 70, 50))
    d.rectangle([x + 90, y - 155, x + 140, y - 115], fill=(150, 200, 230))
    # барабан
    d.ellipse([x - 160, y - 200, x + 60, y - 70], fill=(220, 220, 214))
    for k in range(3):
        a = drum_rot + k * 2.1
        d.line([(x - 50 + math.cos(a) * 90, y - 135 + math.sin(a) * 50),
                (x - 50 + math.cos(a + 0.9) * 90, y - 135 + math.sin(a + 0.9) * 50)], fill=(230, 70, 50), width=12)


def draw_shed(d, x, broken=False, open_t=0.0):
    y = GROUND
    d.rectangle([x - 130, y - 210, x + 130, y], fill=(70, 120, 150))
    for k in range(-120, 130, 24):
        d.line([(x + k, y - 210), (x + k, y)], fill=(56, 100, 128), width=4)
    d.rectangle([x - 145, y - 230, x + 145, y - 205], fill=(60, 60, 66))
    d.rectangle([x + 40, y - 150, x + 110, y - 100], fill=(150, 200, 230))
    # дверь
    if broken:
        d.rectangle([x - 100, y - 170, x - 20, y], fill=(20, 18, 22))
        d.polygon([(x - 100, y - 170), (x - 170, y - 150), (x - 170, y + 10), (x - 100, y)], fill=(130, 90, 60))
        d.line([(x - 150, y - 120), (x - 120, y - 90), (x - 140, y - 60)], fill=(60, 40, 30), width=5)
    else:
        d.rectangle([x - 100, y - 170, x - 20, y], fill=(130, 90, 60))
        d.ellipse([x - 38, y - 94, x - 26, y - 82], fill=(230, 200, 60))
        d.text((x + 75, y - 125), "$", font=font(40), fill=(40, 140, 60), anchor="mm")


def draw_thief(d, x, t):
    y = GROUND + 4
    bob = abs(math.sin(t * 8)) * 5
    d.line([(x - 10, y - 70 - bob), (x - 14 + math.sin(t * 8) * 12, y)], fill=(14, 14, 18), width=18)
    d.line([(x + 10, y - 70 - bob), (x + 14 - math.sin(t * 8) * 12, y)], fill=(14, 14, 18), width=18)
    d.rounded_rectangle([x - 32, y - 170 - bob, x + 32, y - 66 - bob], radius=14, fill=(14, 14, 18))
    d.ellipse([x - 28, y - 230 - bob, x + 28, y - 174 - bob], fill=(14, 14, 18))
    d.rectangle([x - 22, y - 210 - bob, x + 22, y - 198 - bob], fill=(220, 220, 220))   # прорезь маски
    d.ellipse([x - 14, y - 208 - bob, x - 6, y - 200 - bob], fill=(14, 14, 18))
    d.ellipse([x + 6, y - 208 - bob, x + 14, y - 200 - bob], fill=(14, 14, 18))


def icon_loan(d, cx, cy, s):
    # чемодан денег и тёмный силуэт в шляпе
    d.rounded_rectangle([cx - 150 * s, cy - 40 * s, cx + 30 * s, cy + 80 * s], radius=int(10 * s), fill=(60, 44, 34))
    d.rectangle([cx - 90 * s, cy - 62 * s, cx - 30 * s, cy - 40 * s], outline=(60, 44, 34), width=int(8 * s))
    d.text((cx - 60 * s, cy + 22 * s), "$$$", font=font(int(44 * s) + 1), fill=(90, 200, 100), anchor="mm")
    hx = cx + 100 * s
    d.ellipse([hx - 36 * s, cy - 76 * s, hx + 36 * s, cy - 4 * s], fill=(20, 20, 24))
    d.rectangle([hx - 60 * s, cy - 70 * s, hx + 60 * s, cy - 60 * s], fill=(20, 20, 24))
    d.rectangle([hx - 34 * s, cy - 110 * s, hx + 34 * s, cy - 66 * s], fill=(20, 20, 24))
    d.rounded_rectangle([hx - 50 * s, cy - 4 * s, hx + 50 * s, cy + 90 * s], radius=int(12 * s), fill=(20, 20, 24))
    d.rectangle([hx - 26 * s, cy - 44 * s, hx + 26 * s, cy - 34 * s], fill=(200, 40, 40))   # «очки»


def icon_neighbor(d, cx, cy, s, sus=False):
    d.ellipse([cx - 80 * s, cy - 100 * s, cx + 80 * s, cy + 60 * s], fill=(232, 190, 150))
    d.chord([cx - 84 * s, cy - 110 * s, cx + 84 * s, cy + 10 * s], 180, 360, fill=(90, 60, 40))
    ex = 18 * s if sus else 0
    for side in (-1, 1):
        x = cx + side * 34 * s
        d.ellipse([x - 18 * s, cy - 36 * s, x + 18 * s, cy - 8 * s], fill=WHITE)
        d.ellipse([x - 8 * s + ex, cy - 30 * s, x + 8 * s + ex, cy - 14 * s], fill=(30, 30, 30))
        if sus:
            d.line([(x - 22 * s, cy - 44 * s), (x + 22 * s, cy - 36 * s)], fill=(60, 40, 30), width=int(6 * s))
    d.arc([cx - 36 * s, cy - 6 * s, cx + 36 * s, cy + 34 * s], 20, 160, fill=(120, 50, 40), width=int(6 * s))
    d.rectangle([cx - 90 * s, cy + 60 * s, cx + 90 * s, cy + 100 * s], fill=(60, 120, 90))


SUS = {"on": False}
R.ICONS["loan"] = icon_loan
R.ICONS["neighbor"] = lambda d, cx, cy, s: icon_neighbor(d, cx, cy, s, SUS["on"])


# ---------- сцены ----------

def render_scene(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    d = R.draw_sky(img, gt, 0.0)
    R.draw_landscape(d)
    R.draw_ground(d)
    R.draw_fence(d, 60, 250)

    built = sc not in ("recap", "walls", "rebar", "mixers", "pour")
    if sc in ("recap", "walls"):
        draw_bunker(d, walls=0)
    elif sc == "rebar":
        draw_bunker(d, walls=0, rebar=lt > 0.2, forms=lt > 1.0)
    elif sc == "mixers":
        draw_bunker(d, walls=0, rebar=True, forms=True)
    elif sc == "pour":
        k = ease_io((lt - 0.2) / max(0.5, seg["dur"] - 0.6))
        draw_bunker(d, walls=min(1, k * 1.15), roof=k > 0.95, rebar=k < 0.4, forms=True)
    elif built:
        draw_bunker(d, walls=1, roof=True)

    if sc == "recap":
        s = back_out(lt / 0.5)
        cx, cy = 540, 560
        d.rounded_rectangle([cx - 250 * s, cy - 220 * s, cx + 250 * s, cy + 220 * s], radius=int(22 * s),
                            fill=(30, 34, 52), outline=BLUE, width=int(7 * s))
        R.draw_bunker_icon(d, cx, cy - 40 * s, "concrete", s * 1.05)
        d.text((cx, cy + 140 * s), "БЕТОН", font=font(int(70 * s) + 1), fill=BLUE, anchor="mm")
        R.draw_hero(d, 900, GROUND + 4, 1.3, gt)
        R.draw_stamp(img, "ВЫБОР ЗРИТЕЛЕЙ", lt - 0.7, col=(40, 160, 80), cy=870)
    elif sc in ("walls", "rebar"):
        R.draw_hero(d, 860, GROUND + 4, 1.3, gt)
        if sc == "rebar":
            R.draw_stamp(img, "−3 000 $", lt - 1.3, cy=520)
    elif sc == "mixers":
        for k in range(3):
            x = lerp(-400 - k * 360, 300 + 0 * k, ease_out(clamp((lt - k * 0.35) / 1.6))) if k == 0 else \
                lerp(-400 - k * 360, -60 - (k - 1) * 330, ease_out(clamp((lt - k * 0.35) / 1.6)))
            draw_mixer(d, x if k else min(x, 200), gt, gt * 3)
        d.text((540, 420), "× 6", font=font(110), fill=YEL, anchor="mm", stroke_width=8, stroke_fill=(20, 16, 20))
        R.draw_hero(d, 900, GROUND + 4, 1.3, gt)
    elif sc == "pour":
        draw_mixer(d, 200, gt, gt * 4)
        # жёлоб
        d.line([(250, GROUND - 120), (400, GROUND - 20)], fill=(90, 90, 96), width=16)
        if lt < seg["dur"] - 0.4:
            d.line([(400, GROUND - 20), (420, GROUND + 60)], fill=CONCRETE, width=22)
        R.draw_hero(d, 880, GROUND + 4, 1.3, gt)
    elif sc == "cure":
        # смена дня и ночи: солнце/луна по дуге
        cyc = (lt * 2.2) % 1.0
        ang = math.pi * (1 - cyc)
        sx, sy = 540 + math.cos(ang) * 420, 760 - math.sin(ang) * 420
        sun = int(lt * 2.2) % 2 == 0
        d.ellipse([sx - 50, sy - 50, sx + 50, sy + 50], fill=(255, 210, 70) if sun else (240, 236, 210))
        day = 1 + int(27 * ease_io(lt / max(0.5, seg["dur"])))
        d.text((540, 430), f"ДЕНЬ {day} / 28", font=font(84), fill=WHITE, anchor="mm",
               stroke_width=8, stroke_fill=(20, 16, 20))
        R.draw_hero(d, 880, GROUND + 4, 1.3, gt)
    elif sc in ("test", "test_ok"):
        arm = 0.5 + 0.5 * math.sin(gt * 3)
        drop = 0 if sc == "test_ok" else -60 * (1 - ease_out(clamp(lt / 0.8)))
        R.draw_excavator(d, 540, arm, gt) if drop == 0 else None
        if drop != 0:
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            R.draw_excavator(ImageDraw.Draw(tmp), 540, arm, gt)
            img.paste(tmp, (0, int(drop)), tmp)
        R.draw_hero(d, 900, GROUND + 4, 1.2, gt)
        if sc == "test_ok":
            R.draw_stamp(img, "ДЕРЖИТ", lt - 0.2, col=(40, 160, 80), cy=480)
    elif sc in ("shed", "night", "broken", "stolen", "left"):
        draw_shed(d, 880, broken=sc != "shed" and sc != "night")
        if sc == "shed":
            R.draw_hero(d, 640 - 0, GROUND + 4, 1.2, gt)
            # «$» над бытовкой
            s = back_out(lt / 0.5)
            d.ellipse([880 - 60 * s, 600 - 60 * s, 880 + 60 * s, 600 + 60 * s], fill=(255, 200, 40),
                      outline=(200, 140, 20), width=6)
            d.text((880, 600), "$", font=font(int(70 * s) + 1), fill=(160, 100, 10), anchor="mm")
        if sc == "night":
            tx = lerp(1140, 720, ease_io(lt / max(0.5, seg["dur"])))
            draw_thief(d, tx, gt)
        if sc == "broken":
            R.draw_hero(d, 560, GROUND + 4, 1.3, gt, face=1)
            if lt > 0.6:
                d.text((560, GROUND - 330), "!", font=font(110), fill=RED, anchor="mm")
            # следы
            for k in range(6):
                fx = 1060 - k * 60
                d.ellipse([fx - 14, GROUND + 6, fx + 14, GROUND + 16], fill=(40, 70, 44))
        if sc == "stolen":
            R.draw_hero(d, 560, GROUND + 4, 1.3, gt)
            R.draw_stamp(img, "УКРАДЕНО", lt - 0.2, cy=500)
            # улетающие вещи
            for k, (lab, col) in enumerate([("ГЕНЕРАТОР", (200, 60, 50)), ("ИНСТРУМЕНТЫ", (90, 90, 96)),
                                            ("$ 7 900", (40, 140, 60))]):
                ft = clamp((lt - 0.6 - k * 0.3) / 1.2)
                if ft > 0:
                    x = lerp(760, 1180, ease_io(ft)); y = 680 + k * 80 - ft * 120
                    tw = d.textlength(lab, font=font(36))
                    d.rounded_rectangle([x - tw / 2 - 16, y - 30, x + tw / 2 + 16, y + 30], radius=10, fill=col)
                    d.text((x, y), lab, font=font(36), fill=WHITE, anchor="mm")
        if sc == "left":
            R.draw_hero(d, 560, GROUND + 4, 1.3, gt)
            pulse = 1 + 0.06 * math.sin(gt * 10)
            d.text((540, 560), "600 $", font=font(int(200 * pulse)), fill=RED, anchor="mm",
                   stroke_width=12, stroke_fill=(20, 16, 20))
    elif sc == "todo":
        R.CHECK_ITEMS = ["4. ДВЕРЬ", "5. ВЕНТИЛЯЦИЯ", "6. ЕДА"]
        R.CHECK_TITLE = "ЕЩЁ НУЖНО"
        R.draw_checklist(img, lt, reveal=1 + p * 3, highlight=None)
        d.text((540, 940), "БЕЗ ДЕНЕГ", font=font(48), fill=RED, anchor="mm")
        R.draw_hero(d, 150, GROUND + 4, 1.2, gt)
    elif sc == "box":
        R.draw_hero(d, 880, GROUND + 4, 1.3, gt)
        R.draw_stamp(img, "ПРОСТО КОРОБКА", lt - 0.5, cy=520)
        # перекати-поле
        bx = lerp(-100, 1200, (lt / max(1, seg["dur"])))
        by = GROUND - 40 - abs(math.sin(lt * 6)) * 50
        for k in range(5):
            a = lt * 8 + k
            d.arc([bx - 40 + math.cos(a) * 6, by - 40, bx + 40, by + 40 + math.sin(a) * 6], 0, 360,
                  fill=(170, 140, 80), width=5)
    elif sc.startswith("choice"):
        foc = {"choice_l": 0, "choice_l2": 0, "choice_r": 1, "choice_r2": 1}.get(sc)
        SUS["on"] = sc == "choice_r2"
        ctl = lt if sc == "choice" else 5.0
        R.draw_choice(img, ctl, gt, focus=foc, vote=sc.startswith("choice_vote"))
        if sc == "choice_l2":
            R.draw_stamp(img, "ДОЛГ × 2", lt - 0.3, cy=960)
        if sc == "choice_r2":
            R.draw_stamp(img, "ЭТО ОН УКРАЛ?", lt - 0.4, col=(200, 120, 20), cy=960)
        if sc == "choice_vote2":
            s = back_out(lt / 0.5)
            d.text((540, 960), "СЕРИЯ 3 — ВЫБИРАЕТЕ ВЫ", font=font(int(46 * s) + 1), fill=YEL, anchor="mm")

    # ночь: затемнение + фонарик вора
    if sc == "night":
        ov = Image.new("RGBA", (W, H), (0, 0, 10, 150))
        od = ImageDraw.Draw(ov)
        tx = lerp(1140, 720, ease_io(lt / max(0.5, seg["dur"])))
        a = math.sin(gt * 3) * 0.3
        od.polygon([(tx - 20, GROUND - 120), (tx - 380, GROUND - 260 + a * 200), (tx - 380, GROUND + 40 + a * 200)],
                   fill=(255, 240, 180, 60))
        img.paste(ov, (0, 0), ov)
        d2 = ImageDraw.Draw(img)
        if int(gt * 2.5) % 2 == 0:
            d2.text((540, 480), "ХРУСТЬ…", font=font(80), fill=(220, 220, 230), anchor="mm")


R.render_scene = render_scene


def sfx_events(add, S, L, nxt, fx):
    add(S("recap"), fx["pop"]()); add(S("recap") + 0.7, fx["thud"]())
    add(S("walls"), fx["pop"]())
    add(S("rebar"), fx["cash"]()); add(S("rebar") + 1.3, fx["thud"]())
    add(S("mixers"), fx["motor"](L("mixers") + 0.4))
    add(S("pour"), fx["motor"](L("pour")) * 0.7); add(S("pour"), fx["cash"]())
    add(S("cure"), fx["whoosh"](1.5))
    add(S("test"), fx["pop"]()); add(S("test") + 0.8, fx["thud"]()); add(S("test"), fx["motor"](L("test")) * 0.6)
    add(S("test_ok") + 0.2, fx["thud"]())
    add(S("shed"), fx["pop"]())
    add(S("night") + 0.3, fx["thud"]() * 0.6); add(S("night") + 0.9, fx["thud"]() * 0.8)
    add(S("broken") + 0.6, fx["thud"]())
    add(S("stolen") + 0.2, fx["thud"]()); add(S("stolen") + 0.6, fx["whoosh"](1.2))
    add(S("left"), fx["boom"]() * 0.5)
    add(S("todo"), fx["pop"]())
    add(S("box") + 0.5, fx["thud"]())
    add(S("choice"), fx["whoosh"](0.5)); add(S("choice") + 0.15, fx["whoosh"](0.5)); add(S("choice") + 0.5, fx["pop"]())
    add(S("choice_l"), fx["pop"]()); add(S("choice_l2") + 0.3, fx["thud"]())
    add(S("choice_r"), fx["pop"]()); add(S("choice_r2") + 0.4, fx["thud"]())


if __name__ == "__main__":
    R.main()
