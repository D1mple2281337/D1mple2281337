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
R.END_LINES = ("ЗАЙМ или СОСЕД? И КТО ВОР?", "ПИШИ В КОММЕНТАРИЯХ")
ORIG_SCENE = R.render_scene          # сцены серии 1 — для «В прошлой серии»
EP1_CARDS = list(R.CHOICE_CARDS)
R.CHOICE_CARDS = [("ЗАЙМ", "loan", RED, 280, "10 000 $ СРАЗУ", "ВЕРНУТЬ ЗА 3 МЕС."),
                  ("ДЯДЯ ГЕНА", "neighbor", GREEN, 800, "10 000 $", "МЕСТО В БУНКЕРЕ")]

R.SEGMENTS[:] = [
    dict(cap="В прошлой серии я взял кредит на *25 000 $*, потому что через год — !конец света!.",
         scene="prev_loan"),
    dict(cap="Купил поле, выкопал котлован и спросил вас: *бетон* или *контейнер*?", scene="prev_choice"),
    dict(cap="Вы выбрали *бетон*. С большим отрывом.", scene="votes"),
    dict(cap="Значит, строю надёжно. Пункт третий: *стены*.", scene="recap", tag="3. СТЕНЫ"),
    dict(cap="Сначала арматура и опалубка. Минус *3 000 $*.", scene="rebar", tag="3. СТЕНЫ",
         budget=14000, delta=-3000, days=327),
    dict(cap="На второй день через забор заглядывает *сосед*. Дядя Гена.", scene="gena_fence"),
    dict(cap="Приносит чай, помогает вязать арматуру.", scene="gena_help"),
    dict(cap="И очень интересуется: сколько стоит бункер и !где я храню деньги!.", scene="gena_ask"),
    dict(cap="На участок заезжают *6 бетономешалок*.", scene="mixers", tag="3. СТЕНЫ"),
    dict(cap="Заливаю стены и потолок. Минус *5 500 $*.", scene="pour", tag="3. СТЕНЫ",
         budget=8500, delta=-5500, pct=50, days=322),
    dict(cap="Бетону нужно *28 дней*, чтобы набрать прочность.", scene="cure", tag="3. СТЕНЫ", days=294),
    dict(cap="Пока жду — включаю *радио*.", scene="radio"),
    dict(cap="Учёные пересчитали траекторию астероида. Вероятность удара — !97 %!.", scene="radio97"),
    dict(cap="Девяносто семь. Значит, есть *3 %*, что всё это зря.", scene="three"),
    dict(cap="И в тот же день приходит письмо из банка: первый платёж — !через месяц!.", scene="letter"),
    dict(cap="Платить я не собираюсь. *Строю дальше*.", scene="tear"),
    dict(cap="Проверка: загоняю на крышу *экскаватор*.", scene="test", tag="ПРОВЕРКА"),
    dict(cap="Держит. Ни одной *трещины*.", scene="test_ok", tag="ПРОВЕРКА", pct=60),
    dict(cap="Бункер готов на *60 %*. Впервые за месяц я сплю спокойно.", scene="calm"),
    dict(cap="Деньги я храню в *бытовке*, прямо на участке. И ставлю *камеру*.", scene="shed"),
    dict(cap="Ночью слышу !шум!.", scene="night"),
    dict(cap="Утром дверь бытовки !выбита!.", scene="broken", days=290),
    dict(cap="Украли генератор, инструменты и !почти все деньги!.", scene="stolen",
         budget=600, delta=-7900),
    dict(cap="Осталось !600 $!.", scene="left"),
    dict(cap="Смотрю запись с *камеры*.", scene="cam"),
    dict(cap="Запись обрывается на !третьей секунде!. Вор первым украл генератор.", scene="cam_cut"),
    dict(cap="Но в кадре видно одно: *зелёный резиновый сапог*.", scene="boot"),
    dict(cap="Звоню в *полицию*.", scene="phone"),
    dict(cap="Говорят: до конца света !9 месяцев!, кому сейчас нужна твоя бытовка.", scene="police"),
    dict(cap="Иду к *дяде Гене*. Он сидит на крыльце.", scene="porch"),
    dict(cap="В обычных *тапочках*. Сапог нигде нет.", scene="slippers"),
    dict(cap="Но у крыльца стоят сапоги. !Зелёные!. И слишком чистые — будто их только что вымыли.",
         scene="boots_clean"),
    dict(cap="А впереди ещё дверь, вентиляция и запас еды.", scene="todo"),
    dict(cap="Без этого бункер — просто !бетонная коробка! в земле.", scene="box"),
    dict(cap="Вечером звонит !незнакомый номер!.", scene="call2"),
    dict(cap="«Слышал, у тебя проблемы с деньгами. *Могу помочь*».", scene="call2b"),
    dict(cap="Денег взять негде. Осталось два варианта, и оба !плохие!.", scene="choice", tag="ВЫБОР"),
    dict(cap="Первый: *займ* у серьёзных людей. *10 000 $* сразу, но вернуть через !3 месяца!.",
         scene="choice_l", tag="ВЫБОР"),
    dict(cap="А если конец света не наступит, они придут за мной !раньше астероида!.",
         scene="choice_l2", tag="ВЫБОР"),
    dict(cap="Второй: *дядя Гена*. Он предлагает *10 000 $*, но хочет !место в бункере!.",
         scene="choice_r", tag="ВЫБОР"),
    dict(cap="Откуда у пенсионера *10 000 $* — через день после !ограбления!?", scene="choice_r2", tag="ВЫБОР"),
    dict(cap="Пиши в комментариях: *займ* или *сосед*.", scene="choice_vote", tag="ВЫБОР"),
    dict(cap="А кто, по-твоему, !вор!? Тоже пиши.", scene="who", tag="ВЫБОР"),
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
    d.chord([cx - 84 * s, cy - 110 * s, cx + 84 * s, cy + 10 * s], 180, 360, fill=(190, 190, 196))
    ex = 18 * s if sus else 0
    for side in (-1, 1):
        x = cx + side * 34 * s
        d.ellipse([x - 18 * s, cy - 36 * s, x + 18 * s, cy - 8 * s], fill=WHITE)
        d.ellipse([x - 8 * s + ex, cy - 30 * s, x + 8 * s + ex, cy - 14 * s], fill=(30, 30, 30))
        if sus:
            d.line([(x - 22 * s, cy - 44 * s), (x + 22 * s, cy - 36 * s)], fill=(60, 40, 30), width=int(6 * s))
    d.arc([cx - 36 * s, cy - 6 * s, cx + 36 * s, cy + 34 * s], 20, 160, fill=(120, 50, 40), width=int(6 * s))
    d.chord([cx - 44 * s, cy - 4 * s, cx + 44 * s, cy + 24 * s], 180, 360, fill=(190, 190, 196))
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
            R.draw_stamp(img, "ОТКУДА ДЕНЬГИ?", lt - 0.4, col=(200, 120, 20), cy=960)
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



# ======== расширенная версия серии: новые сцены ========
BOOT = (60, 150, 70)


def draw_gena(d, x, y, s=1.0, t=0.0, boots=True, cup=False, face=1, sus=False):
    """Сосед дядя Гена: седой, с усами, в зелёных резиновых сапогах (или тапочках)."""
    by = y - 70 * s
    d.line([(x - 10 * s, by), (x - 12 * s, y - 6 * s)], fill=(70, 70, 80), width=int(16 * s))
    d.line([(x + 10 * s, by), (x + 12 * s, y - 6 * s)], fill=(70, 70, 80), width=int(16 * s))
    if boots:
        for sx in (-1, 1):
            d.rounded_rectangle([x + sx * 12 * s - 13 * s, y - 40 * s, x + sx * 12 * s + 13 * s + (8 * s if sx > 0 else 0),
                                 y + 4 * s], radius=int(5 * s), fill=BOOT)
    else:
        for sx in (-1, 1):
            d.ellipse([x + sx * 14 * s - 16 * s, y - 6 * s, x + sx * 14 * s + 18 * s, y + 6 * s], fill=(90, 120, 200))
    d.rounded_rectangle([x - 34 * s, by - 92 * s, x + 34 * s, by + 4 * s], radius=int(16 * s), fill=(110, 70, 60))
    d.line([(x - 32 * s, by - 80 * s), (x - 40 * s, by - 20 * s)], fill=(110, 70, 60), width=int(14 * s))
    d.line([(x + 32 * s, by - 80 * s), (x + 42 * s * face, by - 30 * s)], fill=(110, 70, 60), width=int(14 * s))
    if cup:
        cx = x + 46 * s * face
        d.rectangle([cx - 12 * s, by - 46 * s, cx + 12 * s, by - 18 * s], fill=WHITE)
        for k in range(3):
            d.line([(cx - 6 * s + k * 6 * s, by - 56 * s - k * 4), (cx - 6 * s + k * 6 * s, by - 70 * s - k * 4)],
                   fill=(200, 200, 210), width=3)
    hy = by - 122 * s
    d.ellipse([x - 27 * s, hy - 28 * s, x + 27 * s, hy + 28 * s], fill=(236, 190, 152))
    d.chord([x - 29 * s, hy - 32 * s, x + 29 * s, hy + 6 * s], 180, 360, fill=(196, 196, 202))
    ex = x + 8 * s * face + (6 * s if sus else 0)
    d.ellipse([ex - 4 * s, hy + 0 * s, ex + 4 * s, hy + 8 * s], fill=(30, 30, 30))
    d.ellipse([ex + 12 * s * face - 4 * s, hy, ex + 12 * s * face + 4 * s, hy + 8 * s], fill=(30, 30, 30))
    d.chord([x - 10 * s + 8 * s * face, hy + 10 * s, x + 22 * s + 8 * s * face, hy + 24 * s], 180, 360,
            fill=(196, 196, 202))


def bubble(d, x, y, text, size=40, col=(246, 244, 236), tcol=(30, 30, 40), tail=-1):
    f = font(size)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([x - tw / 2 - 24, y - size * 0.9, x + tw / 2 + 24, y + size * 0.9], radius=18, fill=col)
    d.polygon([(x + tail * 30, y + size * 0.8), (x + tail * 70, y + size * 1.8), (x + tail * 70 - tail * 40,
               y + size * 0.8)], fill=col)
    d.text((x, y), text, font=f, fill=tcol, anchor="mm")


def bg(img, gt, stage):
    d = R.draw_sky(img, gt, 0.0)
    R.draw_landscape(d); R.draw_ground(d); R.draw_fence(d, 60, 250)
    if stage == "rebar":
        draw_bunker(d, walls=0, rebar=True, forms=True)
    elif stage == "built":
        draw_bunker(d, walls=1, roof=True)
    return d


def draw_radio(d, x, y, t, on=True):
    d.rounded_rectangle([x - 110, y - 120, x + 110, y], radius=18, fill=(150, 90, 50))
    d.ellipse([x - 90, y - 100, x - 10, y - 20], fill=(60, 40, 30))
    for k in range(4):
        d.line([(x + 20, y - 95 + k * 18), (x + 90, y - 95 + k * 18)], fill=(230, 210, 160), width=5)
    d.line([(x + 70, y - 120), (x + 130, y - 240)], fill=(160, 160, 170), width=5)
    if on:
        for k in range(3):
            r = 40 + k * 40 + (t * 80) % 40
            d.arc([x - 130 - r, y - 160 - r, x - 130 + r, y - 160 + r], 200, 280, fill=(220, 220, 240), width=5)


def draw_house(d, x):
    y = GROUND
    d.rectangle([x - 200, y - 260, x + 200, y], fill=(150, 100, 60))
    for k in range(y - 250, y, 28):
        d.line([(x - 200, k), (x + 200, k)], fill=(130, 84, 50), width=3)
    d.polygon([(x - 230, y - 260), (x, y - 400), (x + 230, y - 260)], fill=(110, 110, 120))
    d.rectangle([x + 60, y - 200, x + 160, y - 110], fill=(250, 220, 140))
    d.line([(x + 110, y - 200), (x + 110, y - 110)], fill=(150, 100, 60), width=6)
    d.rectangle([x - 150, y - 190, x - 60, y], fill=(90, 60, 40))
    d.rectangle([x - 220, y - 40, x + 20, y], fill=(120, 80, 50))   # крыльцо


def scene_ext(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    dur = seg["dur"]
    if sc in ("prev_loan", "prev_choice"):
        fake = dict(seg, scene="loan" if sc == "prev_loan" else "choice_vote")
        cards = R.CHOICE_CARDS
        R.CHOICE_CARDS = EP1_CARDS
        ORIG_SCENE(img, fake, i, lt + (2 if sc == "prev_loan" else 0), p, gt, st)
        R.CHOICE_CARDS = cards
        # «плёнка»: тонировка, рамка, РАНЕЕ
        ov = Image.new("RGBA", (W, H), (60, 40, 20, 70))
        img.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(img)
        d.rectangle([20, 200, W - 20, R.SOIL_BOT - 10], outline=(240, 236, 226), width=6)
        if int(gt * 2) % 2 == 0:
            d.ellipse([50, 225, 80, 255], fill=RED)
        d.text((95, 240), "В ПРОШЛОЙ СЕРИИ", font=font(40), fill=WHITE, anchor="lm")
        return True
    if sc == "calm":
        d = bg(img, gt, "built")
        R.draw_hero(d, 760, GROUND + 4, 1.3, gt, face=-1)
        for k in range(3):
            ft = (lt * 0.6 + k / 3) % 1
            d.text((820 + ft * 120, 640 - ft * 260), "Z", font=font(int(50 + ft * 40)),
                   fill=lc((40, 40, 60), WHITE, 1 - ft), anchor="mm")
        d.text((450, 470), "60 %", font=font(150), fill=GREEN, anchor="mm", stroke_width=10,
               stroke_fill=(20, 16, 20))
        return True
    if sc == "boots_clean":
        d = R.draw_sky(img, gt, 0.0)
        R.draw_landscape(d); R.draw_ground(d)
        draw_house(d, 420)
        draw_gena(d, 300, GROUND + 4, 1.4, gt, boots=False, face=1, sus=True)
        R.draw_hero(d, 960, GROUND + 4, 1.2, gt, face=-1)
        # сапоги у крыльца + блеск
        for bx in (640, 700):
            d.rounded_rectangle([bx - 22, GROUND - 90, bx + 14, GROUND], radius=8, fill=(80, 190, 95))
            d.rounded_rectangle([bx - 22, GROUND - 30, bx + 34, GROUND], radius=10, fill=(80, 190, 95))
        for k in range(4):
            a = gt * 4 + k * 1.6
            x, y = 670 + math.cos(a) * 70, GROUND - 120 + math.sin(a) * 40
            r = 10 + 6 * math.sin(gt * 8 + k)
            d.polygon([(x, y - r * 2), (x + r * 0.5, y), (x, y + r * 2), (x - r * 0.5, y)], fill=WHITE)
            d.polygon([(x - r * 2, y), (x, y - r * 0.5), (x + r * 2, y), (x, y + r * 0.5)], fill=WHITE)
        if lt > 1.4:
            R.draw_stamp(img, "СЛИШКОМ ЧИСТЫЕ", lt - 1.4, col=(40, 140, 60), cy=520)
        return True
    if sc in ("call2", "call2b"):
        d = bg(img, gt, "built")
        draw_shed(d, 880, broken=True)
        ov = Image.new("RGBA", (W, H), (10, 0, 30, 90)); img.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(img)
        R.draw_hero(d, 560, GROUND + 4, 1.4, gt)
        d.rounded_rectangle([590, GROUND - 330, 616, GROUND - 280], radius=6, fill=(30, 30, 34))
        if sc == "call2":
            s_ = back_out(lt / 0.4)
            d.rounded_rectangle([540 - 200 * s_, 420 - 220 * s_, 540 + 200 * s_, 420 + 220 * s_], radius=30,
                                fill=(20, 20, 26), outline=(90, 90, 100), width=6)
            d.text((540, 340), "НЕИЗВЕСТНЫЙ", font=font(int(44 * s_) + 1), fill=WHITE, anchor="mm")
            d.text((540, 400), "НОМЕР", font=font(int(44 * s_) + 1), fill=WHITE, anchor="mm")
            d.text((540, 480), "+7 *** *** ** 66", font=font(int(34 * s_) + 1, True), fill=GREY, anchor="mm")
            if int(gt * 4) % 2 == 0:
                d.ellipse([500, 540, 580, 620], fill=(40, 180, 80))
        else:
            bubble(d, 540, 430, "МОГУ ПОМОЧЬ…", 54, col=(20, 20, 26), tcol=RED, tail=1)
        return True
    if sc == "votes":
        d = bg(img, gt, None)
        draw_bunker(d, walls=0)
        k = ease_out(clamp((lt - 0.2) / 1.4))
        for j, (lab, val, col) in enumerate([("БЕТОН", 81, BLUE), ("КОНТЕЙНЕР", 19, YEL)]):
            y = 470 + j * 190
            d.text((90, y - 60), lab, font=font(52), fill=col, anchor="lm")
            d.rounded_rectangle([90, y - 20, 990, y + 60], radius=20, fill=(30, 34, 52))
            wv = 900 * val / 100 * k
            if wv > 30:
                d.rounded_rectangle([90, y - 20, 90 + wv, y + 60], radius=20, fill=col)
            d.text((990, y - 60), f"{int(val * k)} %", font=font(52), fill=WHITE, anchor="rm")
        if lt > 1.5:
            R.draw_stamp(img, "БЕТОН", lt - 1.5, col=(40, 120, 220), cy=900)
        return True
    if sc in ("gena_fence", "gena_help", "gena_ask"):
        d = bg(img, gt, "rebar")
        if sc == "gena_fence":
            gy = lerp(GROUND + 200, GROUND + 4, ease_out(clamp(lt / 0.8)))
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_gena(ImageDraw.Draw(tmp), 160, gy, 1.3, gt)
            tmp.crop((0, 0, W, GROUND - 60)).load()
            img.paste(tmp.crop((0, 0, W, GROUND - 50)), (0, 0), tmp.crop((0, 0, W, GROUND - 50)))
            d = ImageDraw.Draw(img)
            R.draw_fence(d, 60, 250)
            R.draw_hero(d, 860, GROUND + 4, 1.3, gt, face=-1)
            if lt > 0.9:
                bubble(d, 300, 520, "ЗДОРОВО, СОСЕД!", 40, tail=-1)
        else:
            draw_gena(d, 260, GROUND + 4, 1.3, gt, cup=(sc == "gena_help"), sus=(sc == "gena_ask"))
            R.draw_hero(d, 860, GROUND + 4, 1.3, gt, face=-1)
            if sc == "gena_help":
                d.text((540, 450), "+1 ПОМОЩНИК", font=font(60), fill=GREEN, anchor="mm", stroke_width=6,
                       stroke_fill=(20, 16, 20))
            else:
                bubble(d, 330, 470, "А ДЕНЬГИ ГДЕ ХРАНИШЬ?", 38, tail=-1)
                if lt > 1.2:
                    d.text((330, 610), "?", font=font(90), fill=YEL, anchor="mm")
        return True
    if sc in ("radio", "radio97", "three"):
        d = bg(img, gt, "built")
        draw_radio(d, 300, GROUND, gt, on=True)
        R.draw_hero(d, 860, GROUND + 4, 1.3, gt, face=-1)
        if sc == "radio97":
            pulse = 1 + 0.05 * math.sin(gt * 9)
            d.text((620, 520), "97 %", font=font(int(190 * pulse)), fill=RED, anchor="mm", stroke_width=12,
                   stroke_fill=(20, 16, 20))
            d.text((620, 660), "ВЕРОЯТНОСТЬ УДАРА", font=font(44), fill=WHITE, anchor="mm")
        if sc == "three":
            d.text((620, 520), "3 %", font=font(220), fill=YEL, anchor="mm", stroke_width=12,
                   stroke_fill=(20, 16, 20))
            d.text((620, 670), "ЧТО ВСЁ ЗРЯ", font=font(52), fill=WHITE, anchor="mm")
        return True
    if sc in ("letter", "tear"):
        d = bg(img, gt, "built")
        R.draw_hero(d, 860, GROUND + 4, 1.3, gt, face=-1)
        cx, cy = 480, 560
        if sc == "letter":
            s = back_out(lt / 0.5)
            d.rectangle([cx - 260 * s, cy - 170 * s, cx + 260 * s, cy + 170 * s], fill=(246, 244, 236))
            d.polygon([(cx - 260 * s, cy - 170 * s), (cx, cy), (cx + 260 * s, cy - 170 * s)], fill=(226, 222, 212))
            d.text((cx, cy + 40 * s), "БАНК", font=font(int(50 * s) + 1), fill=(40, 40, 60), anchor="mm")
            d.text((cx, cy + 110 * s), "ПЛАТЁЖ ЧЕРЕЗ 30 ДНЕЙ", font=font(int(34 * s) + 1, True), fill=RED, anchor="mm")
        else:
            for k in range(8):
                ft = clamp(lt / 1.5)
                ang = k * 0.8
                x = cx + math.cos(ang) * 300 * ft; y = cy + math.sin(ang) * 120 * ft + 400 * ft * ft
                d.polygon([(x - 40, y - 30), (x + 50, y - 20), (x + 30, y + 40), (x - 30, y + 30)], fill=(246, 244, 236))
            R.draw_stamp(img, "НЕ ПЛАЧУ", lt - 0.3, cy=480)
        return True
    if sc == "shed":
        render_scene(img, seg, i, lt, p, gt, st)
        d = ImageDraw.Draw(img)
        if lt > 1.5:
            d.rectangle([1046, GROUND - 330, 1056, GROUND], fill=(80, 80, 86))
            d.rounded_rectangle([990, GROUND - 360, 1060, GROUND - 320], radius=8, fill=(40, 40, 46))
            d.ellipse([975, GROUND - 352, 1000, GROUND - 328], fill=(20, 20, 24))
            if int(gt * 3) % 2 == 0:
                d.ellipse([1040, GROUND - 354, 1052, GROUND - 342], fill=RED)
        return True
    if sc in ("cam", "cam_cut", "boot"):
        img.paste((10, 14, 12), (0, 0, W, R.SOIL_BOT))
        d = ImageDraw.Draw(img)
        # монитор
        d.rounded_rectangle([60, 220, W - 60, 1000], radius=26, fill=(36, 36, 42))
        scr = Image.new("RGB", (W - 160, 680), (30, 40, 34))
        sd = ImageDraw.Draw(scr)
        sd.rectangle([0, 470, W, 680], fill=(40, 56, 42))
        sd.rectangle([520, 220, 800, 470], fill=(60, 80, 70))       # бытовка в ч/б-зелёном
        sd.rectangle([560, 300, 640, 470], fill=(40, 52, 46))
        cut = sc != "cam" and lt > 0.6 if sc == "cam_cut" else sc == "boot"
        if sc == "cam" or (sc == "cam_cut" and not cut):
            tx = 900 - lt * 120
            sd.rectangle([tx - 30, 300, tx + 30, 470], fill=(12, 16, 14))
            sd.ellipse([tx - 26, 250, tx + 26, 302], fill=(12, 16, 14))
        if sc == "boot":
            z = 1 + 0.15 * ease_out(clamp(lt / 1.0))
            bx, by = 440, 480
            sd.rounded_rectangle([bx - 60 * z, by - 150 * z, bx + 20 * z, by], radius=12, fill=(70, 160, 80))
            sd.rounded_rectangle([bx - 60 * z, by - 50 * z, bx + 80 * z, by], radius=16, fill=(70, 160, 80))
            sd.ellipse([bx - 140 * z, by - 230 * z, bx + 160 * z, by + 60 * z], outline=RED, width=8)
        # шум
        for k in range(900):
            x = R.rnd.randrange(scr.width); y = R.rnd.randrange(scr.height)
            c = R.rnd.randrange(30, 120)
            sd.point((x, y), fill=(c, c + 10, c))
        if cut and sc == "cam_cut":
            scr = Image.effect_noise((W - 160, 680), 90).convert("RGB")
            sd = ImageDraw.Draw(scr)
            sd.rectangle([180, 290, scr.width - 180, 390], fill=(10, 10, 10))
            sd.text((scr.width / 2, 340), "НЕТ СИГНАЛА", font=font(60), fill=WHITE, anchor="mm")
        sd.text((24, 30), "CAM 1", font=font(36), fill=WHITE)
        sec = 3 if sc != "cam" else min(3, int(lt * 1.5))
        sd.text((scr.width - 24, 30), f"03:12:0{sec}", font=font(36), fill=WHITE, anchor="ra")
        if int(gt * 2) % 2 == 0:
            sd.ellipse([24, scr.height - 64, 54, scr.height - 34], fill=RED)
            sd.text((66, scr.height - 50), "REC", font=font(32), fill=WHITE, anchor="lm")
        img.paste(scr, (80, 240))
        if sc == "boot" and lt > 0.8:
            R.draw_stamp(img, "ЗЕЛЁНЫЙ САПОГ", lt - 0.8, col=(40, 140, 60), cy=1120)
        return True
    if sc in ("phone", "police"):
        d = bg(img, gt, "built")
        draw_shed(d, 880, broken=True)
        R.draw_hero(d, 560, GROUND + 4, 1.4, gt)
        # телефон у уха
        d.rounded_rectangle([590, GROUND - 330, 616, GROUND - 280], radius=6, fill=(30, 30, 34))
        if sc == "phone":
            if int(gt * 4) % 2 == 0:
                d.text((700, GROUND - 400), "ДЗЫНЬ", font=font(50), fill=YEL, anchor="mm")
        else:
            bubble(d, 540, 420, "КОМУ НУЖНА", 46, col=(40, 70, 160), tcol=WHITE, tail=1)
            bubble(d, 540, 540, "ТВОЯ БЫТОВКА?", 46, col=(40, 70, 160), tcol=WHITE, tail=1)
            R.draw_stamp(img, "ДЕЛО ЗАКРЫТО", lt - 1.4, cy=700)
        return True
    if sc in ("porch", "slippers"):
        d = R.draw_sky(img, gt, 0.0)
        R.draw_landscape(d); R.draw_ground(d)
        draw_house(d, 420)
        draw_gena(d, 300, GROUND + 4, 1.4, gt, boots=False, face=1)
        if sc == "porch":
            wt = clamp(lt / 1.6)
            R.draw_hero(d, lerp(1150, 820, ease_out(wt)), GROUND + 4, 1.3, gt, walk=wt < 1, face=-1)
            if lt > 1.4:
                bubble(d, 300, 470, "ЧЕГО ТЕБЕ?", 42, tail=-1)
        else:
            R.draw_hero(d, 820, GROUND + 4, 1.3, gt, face=-1)
            # лупа на тапочках
            d.ellipse([170, GROUND - 120, 430, GROUND + 140], outline=YEL, width=10)
            d.line([(410, GROUND + 110), (520, GROUND + 220)], fill=YEL, width=18)
            d.text((300, 380), "ТАПОЧКИ", font=font(70), fill=YEL, anchor="mm", stroke_width=8,
                   stroke_fill=(20, 16, 20))
            d.text((300, 470), "А САПОГИ ГДЕ?", font=font(44), fill=WHITE, anchor="mm")
        return True
    if sc == "who":
        SUS["on"] = True
        R.draw_choice(img, 5.0, gt, focus=None, vote=True)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([290, 880, 790, 1000], radius=20, fill=(40, 140, 60))
        d.text((540, 940), "КТО ВОР?  🥾", font=font(56), fill=WHITE, anchor="mm")
        return False   # фон уже нарисован в draw_choice? — нет, нарисуем ниже
    return None


_base_scene = render_scene


def render_scene2(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    if sc == "who":
        _base_scene(img, dict(seg, scene="choice_vote"), i, lt, p, gt, st)
        d = ImageDraw.Draw(img)
        s = back_out(lt / 0.5)
        d.rounded_rectangle([540 - 260 * s, 950 - 60 * s, 540 + 260 * s, 950 + 60 * s], radius=20,
                            fill=(40, 140, 60))
        d.text((540, 950), "КТО ВОР?", font=font(int(60 * s) + 1), fill=WHITE, anchor="mm")
        return
    if sc in ("choice_r2", "choice_vote2", "choice_vote"):
        SUS["on"] = sc != "choice_vote"
    if scene_ext(img, seg, i, lt, p, gt, st) is None:
        _base_scene(img, seg, i, lt, p, gt, st)


R.render_scene = render_scene2


def sfx_events(add, S, L, nxt, fx):
    add(S("prev_loan"), fx["whoosh"](0.8)); add(S("prev_loan") + 0.4, fx["thud"]())
    add(S("prev_choice"), fx["whoosh"](0.6))
    add(S("votes"), fx["whoosh"](1.2)); add(S("votes") + 1.5, fx["thud"]())
    add(S("recap"), fx["pop"]())
    add(S("rebar"), fx["cash"]()); add(S("rebar") + 1.3, fx["thud"]())
    add(S("gena_fence"), fx["pop"]()); add(S("gena_ask") + 1.2, fx["pop"]())
    add(S("mixers"), fx["motor"](L("mixers") + 0.4))
    add(S("pour"), fx["motor"](L("pour")) * 0.7); add(S("pour"), fx["cash"]())
    add(S("cure"), fx["whoosh"](1.5))
    add(S("radio"), fx["rain"](L("radio") + 0.4) * 0.6)
    add(S("radio97"), fx["boom"]() * 0.4); add(S("three"), fx["pop"]())
    add(S("letter"), fx["pop"]()); add(S("tear"), fx["whoosh"](0.8)); add(S("tear") + 0.3, fx["thud"]())
    add(S("test"), fx["pop"]()); add(S("test") + 0.8, fx["thud"]()); add(S("test"), fx["motor"](L("test")) * 0.6)
    add(S("test_ok") + 0.2, fx["thud"]())
    add(S("shed"), fx["pop"]()); add(S("shed") + 1.5, fx["pop"]())
    add(S("night") + 0.3, fx["thud"]() * 0.6); add(S("night") + 0.9, fx["thud"]() * 0.8)
    add(S("broken") + 0.6, fx["thud"]())
    add(S("stolen") + 0.2, fx["thud"]()); add(S("stolen") + 0.6, fx["whoosh"](1.2))
    add(S("left"), fx["boom"]() * 0.5)
    add(S("cam"), fx["rain"](L("cam") + 0.4) * 0.4)
    add(S("cam_cut") + 0.6, fx["rain"](1.5) * 1.5)
    add(S("boot") + 0.8, fx["thud"]())
    add(S("phone"), fx["cash"]()); add(S("phone") + 0.5, fx["cash"]())
    add(S("police") + 1.4, fx["thud"]())
    add(S("slippers"), fx["pop"]())
    add(S("todo"), fx["pop"]()); add(S("box") + 0.5, fx["thud"]())
    add(S("choice"), fx["whoosh"](0.5)); add(S("choice") + 0.15, fx["whoosh"](0.5)); add(S("choice") + 0.5, fx["pop"]())
    add(S("choice_l"), fx["pop"]()); add(S("choice_l2") + 0.3, fx["thud"]())
    add(S("choice_r"), fx["pop"]()); add(S("choice_r2") + 0.4, fx["thud"]())
    add(S("who"), fx["pop"]())
    add(S("calm"), fx["whoosh"](1.0)); add(S("boots_clean") + 1.4, fx["thud"]())
    add(S("call2"), fx["cash"]()); add(S("call2") + 0.6, fx["cash"]()); add(S("call2b"), fx["boom"]() * 0.3)


if __name__ == "__main__":
    R.main()
