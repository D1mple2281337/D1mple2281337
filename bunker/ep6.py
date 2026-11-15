#!/usr/bin/env python3
"""Бункер за 25 000 $ — серия 6 (зрители выбрали ПРЕДУПРЕДИТЬ).

Герой бросает пост и предупреждает посёлок. Три пункта: завал у входа, табличка «Газ»,
фильтр — банкиров выкуривает пеплом из бункера. В 6:00 колонна у школы; Аркадий ведёт
военных к входу — это его школа. Поворот: первой поднимается Маша, Аркадий врёт «тут погреб».
Осколок — колонна уходит. Гена впускает сына. Банкиры просят места: свободно 2, их 7.
Крючок: радио «траектория изменилась, новая дата удара…» — обрыв.
Финал: ВПУСТИТЬ ВСЕХ или НИКОГО.

  python3 ep6.py --timings timings_ep6.json --audio audio/mix_ep6_norm.wav --out out/bunker_ep6.mp4
"""
import math, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import ep5
from ep2 import draw_gena, bubble, draw_radio
from ep3 import draw_bunker_plus, draw_car, night_overlay, flashlight, field, outlined, STEEL
from ep4 import draw_suit, draw_soldier, draw_kid, draw_valya, draw_truck, meteor, shake, tinted_prev
from ep5 import (draw_arkady, draw_booth, draw_dog, draw_school, draw_paper, draw_vent_pipe, booth_scene,
                 MASHA)
from render import (W, H, GROUND, font, lerp, lc, clamp, ease_io, ease_out, back_out,
                    WHITE, GREY, YEL, RED, GREEN, BLUE)

EP5_SCENE = R.render_scene
R.INIT = (42.0, 0.0, 400.0)
R.EP_LABEL = "СЕРИЯ 6"
R.END_LINES = ("ВПУСТИТЬ или НИКОГО?", "ПИШИ В КОММЕНТАРИЯХ")
R.CHOICE_CARDS = [("ВПУСТИТЬ ВСЕХ", "let_in", YEL, 280, "НИКТО НАВЕРХУ", "ЕДЫ МЕНЬШЕ ВСЕМ"),
                  ("НИКОГО", "nobody", BLUE, 800, "ЕДЫ ХВАТИТ", "7 ЧЕЛ. НАВЕРХУ")]

S_ = dict
R.SEGMENTS[:] = [
    S_(cap="В прошлой серии я услышал через вентиляцию: утром военные заберут !убежище под школой!.",
       scene="prev_vent"),
    S_(cap="А на обороте рисунка Маши Гена написал: *фильтр открывается снаружи*.", scene="prev_note"),
    S_(cap="Вы выбрали — *предупредить*.", scene="votes"),
    S_(cap="Я снимаю форму охранника и бросаю её в будку.", scene="leave_post"),
    S_(cap="И бегу. Через поле, через пепел — *к школе*.", scene="run"),
    S_(cap="Четыре часа ночи. До колонны — !два часа!.", scene="clock4", days=41),
    S_(cap="Стучу в подвал. Открывает *тётя Валя*.", scene="door"),
    S_(cap="— Опять погреб пришёл показывать? — говорит она !холодно!.", scene="valya_cold"),
    S_(cap="Я рассказываю всё. Про банк. Про военных. Про то, что !соврал ей!.", scene="confess"),
    S_(cap="Вокруг собираются люди. Кто-то кричит, что я !шпион банка!.", scene="crowd"),
    S_(cap="И тут вперёд выходит Маша: — Он хороший. *Я его нарисовала*.", scene="masha_def"),
    S_(cap="Дядя Гена кладёт руку мне на плечо: — Два часа. *Работаем*.", scene="gena_go"),
    S_(cap="План из *трёх пунктов*.", scene="plan", tag="ПЛАН"),
    S_(cap="Первый: спрятать вход. Засыпаем его кирпичами, мусором и *старыми партами*.", scene="plan1",
       tag="1. ВХОД"),
    S_(cap="Второй: табличка. «Опасно. !Утечка газа!». Пусть военные подумают дважды.", scene="plan2",
       tag="2. ТАБЛИЧКА"),
    S_(cap="Третий пункт — мой. *Фильтр*.", scene="plan3", tag="3. ФИЛЬТР"),
    S_(cap="Я бегу обратно к бункеру. Банкиры !спят!.", scene="back", tag="3. ФИЛЬТР"),
    S_(cap="Откручиваю крышку фильтра. Снаружи — !пепел и дым! после ночных осколков.", scene="filter",
       tag="3. ФИЛЬТР"),
    S_(cap="Через минуту снизу раздаётся !кашель!.", scene="cough", tag="3. ФИЛЬТР"),
    S_(cap="Люк распахивается. Банкиры вылезают один за другим. *В пижамах*. С собакой.", scene="out",
       tag="3. ФИЛЬТР"),
    S_(cap="Директор кашляет и орёт: — Охрана! !Где охрана!?", scene="director", tag="3. ФИЛЬТР"),
    S_(cap="А охрана сидит в кустах. И впервые за месяц *смеётся*.", scene="bushes", tag="3. ФИЛЬТР"),
    S_(cap="!Шесть утра!.", scene="clock6"),
    S_(cap="Колонна въезжает в посёлок.", scene="column"),
    S_(cap="Военные у школы. Перед ними — гора мусора и табличка *«Газ»*.", scene="at_school"),
    S_(cap="Командир морщится: — Это и есть убежище? Тут же *свалка*.", scene="commander"),
    S_(cap="Кажется, *сработало*.", scene="works"),
    S_(cap="И тут подъезжает ещё одна машина. Выходит !Аркадий!.", scene="ark_car"),
    S_(cap="Он идёт прямо к куче мусора. Как будто !знает дорогу!.", scene="ark_walk"),
    S_(cap="Потому что знает. Это *его школа*. Он здесь учился.", scene="his_school"),
    S_(cap="— Здесь, — говорит он. Солдаты !разбирают завал!.", scene="clear"),
    S_(cap="Люк поднимается. Внизу — !триста пар глаз!.", scene="hatch"),
    S_(cap="— Выходим по одному! — командует офицер.", scene="order"),
    S_(cap="Первой по лестнице поднимается *Маша*.", scene="masha_up"),
    S_(cap="Аркадий видит её лицо. И !замирает!.", scene="freeze"),
    S_(cap="Секунда. Две. Три.", scene="seconds"),
    S_(cap="— Я ошибся, — говорит Аркадий. — Это *старый погреб*. Мест тут нет.", scene="ark_lie"),
    S_(cap="Командир смотрит на него. Потом на людей. !Не верит!.", scene="doubt"),
    S_(cap="И в этот момент в небе вспыхивает осколок. !Взрыв! — за рекой.", scene="blast"),
    S_(cap="— По машинам! — кричит командир. Колонна *уходит*.", scene="retreat"),
    S_(cap="Аркадий остаётся. Без машины. Без банка. !Без бункера!.", scene="ark_alone"),
    S_(cap="Маша подходит и молча *даёт ему руку*.", scene="hand"),
    S_(cap="Дядя Гена смотрит на сына. И впервые за восемь лет говорит: — *Заходи*.", scene="come_in",
       pct=100),
    S_(cap="А через час к школе приходят банкиры. В пепле. !С собакой!.", scene="bankers"),
    S_(cap="Их бункер полон пепла. Фильтр забит. Жить там !нельзя!.", scene="ruined"),
    S_(cap="Директор просит: — Пустите. Мы заплатим. *Сколько угодно*.", scene="beg"),
    S_(cap="Гена считает места. *Триста*. Нас — двести девяносто восемь.", scene="count"),
    S_(cap="Свободно — !два места!. А банкиров — !семь!.", scene="two"),
    S_(cap="И тут из старого приёмника в подвале — *сигнал*.", scene="radio"),
    S_(cap="«Внимание. Траектория астероида !изменилась!. Новая дата удара…»", scene="radio2"),
    S_(cap="!Связь обрывается!.", scene="cut"),
    S_(cap="А нам надо решить: кого пустить.", scene="choice", tag="ВЫБОР"),
    S_(cap="Первый: *впустить всех*. Будет тесно, а еды станет !меньше — для каждого!.", scene="choice_l",
       tag="ВЫБОР"),
    S_(cap="Второй: *никого*. Пусть чистят свой бункер сами. Те, кто !выгнал нас!.", scene="choice_r",
       tag="ВЫБОР"),
    S_(cap="Пиши в комментариях: *впустить* или *никого*.", scene="choice_vote", tag="ВЫБОР"),
    S_(cap="А новую дату удара мы узнаем !в следующей серии!.", scene="choice_vote2", tag="ВЫБОР"),
]


# ---------- объекты ----------

def draw_crowd(d, x0, x1, y, n, seed=1, s=1.0):
    rnd = R.random.Random(seed)
    cols = [(150, 70, 110), (60, 120, 160), (200, 80, 40), (120, 128, 66), (110, 70, 60), (90, 90, 96),
            (180, 150, 60)]
    for k in range(n):
        x = lerp(x0, x1, (k + 0.5) / n) + rnd.uniform(-10, 10)
        yy = y - rnd.randrange(0, 18)
        sc = s * rnd.uniform(0.85, 1.1)
        d.rounded_rectangle([x - 20 * sc, yy - 110 * sc, x + 20 * sc, yy - 30 * sc], radius=int(8 * sc),
                            fill=cols[k % len(cols)])
        d.ellipse([x - 18 * sc, yy - 148 * sc, x + 18 * sc, yy - 112 * sc], fill=(236, 194, 160))
        d.line([(x - 8 * sc, yy - 30 * sc), (x - 8 * sc, yy)], fill=(50, 50, 60), width=int(10 * sc))
        d.line([(x + 8 * sc, yy - 30 * sc), (x + 8 * sc, yy)], fill=(50, 50, 60), width=int(10 * sc))


def shelter(img, gt, crowd=True):
    """Советское убежище под школой изнутри."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, R.SOIL_BOT], fill=(80, 84, 78))
    d.pieslice([40, 120, W - 40, 900], 180, 360, fill=(104, 110, 100))
    d.rectangle([40, 510, W - 40, R.SOIL_BOT - 60], fill=(104, 110, 100))
    d.rectangle([0, R.SOIL_BOT - 60, W, R.SOIL_BOT], fill=(70, 70, 66))
    d.rounded_rectangle([360, 260, 720, 360], radius=10, fill=(240, 230, 200), outline=(170, 40, 40), width=6)
    d.text((540, 310), "УБЕЖИЩЕ №1", font=font(46), fill=(170, 40, 40), anchor="mm")
    for k in range(3):
        x = 220 + k * 320
        d.line([(x, 200), (x, 400)], fill=(30, 30, 30), width=3)
        d.ellipse([x - 18, 400, x + 18, 436], fill=(255, 230, 140) if int(gt * 3 + k) % 7 else (200, 180, 110))
    if crowd:
        draw_crowd(d, 60, W - 60, R.SOIL_BOT - 56, 14, seed=3, s=1.1)
    return d


def rubble(d, x, h=1.0):
    rnd = R.random.Random(9)
    for k in range(int(40 * h)):
        bx = x + rnd.randrange(-220, 220) * (1 - k / (40 * h + 1) * 0.5)
        by = GROUND - rnd.randrange(0, int(200 * h) + 1) * (1 - abs(bx - x) / 260)
        w_ = rnd.randrange(30, 70); h_ = rnd.randrange(16, 30)
        col = [(160, 80, 60), (120, 110, 100), (140, 100, 60), (90, 70, 50)][k % 4]
        d.rectangle([bx - w_ / 2, by - h_, bx + w_ / 2, by], fill=col)
    # парта
    if h > 0.5:
        d.rectangle([x - 90, GROUND - 210 * h, x + 90, GROUND - 190 * h], fill=(120, 150, 90))
        d.line([(x - 70, GROUND - 190 * h), (x - 80, GROUND - 120 * h)], fill=(80, 80, 86), width=8)
        d.line([(x + 70, GROUND - 190 * h), (x + 80, GROUND - 120 * h)], fill=(80, 80, 86), width=8)


def gas_sign(d, x, y, s=1.0):
    d.line([(x, y), (x, GROUND)], fill=(110, 110, 116), width=int(10 * s))
    d.polygon([(x, y - 170 * s), (x - 130 * s, y + 50 * s), (x + 130 * s, y + 50 * s)], fill=YEL,
              outline=(30, 30, 30))
    d.text((x, y - 10 * s), "!", font=font(int(80 * s) + 1), fill=(30, 30, 30), anchor="mm")
    d.rectangle([x - 150 * s, y + 70 * s, x + 150 * s, y + 160 * s], fill=WHITE, outline=(30, 30, 30), width=4)
    d.text((x, y + 98 * s), "ОПАСНО", font=font(int(34 * s) + 1), fill=RED, anchor="mm")
    d.text((x, y + 136 * s), "УТЕЧКА ГАЗА", font=font(int(28 * s) + 1, True), fill=(30, 30, 30), anchor="mm")


def pajama(d, x, y, s=1.0, col=(120, 160, 220), t=0.0, cough=False):
    d.line([(x - 10 * s, y - 70 * s), (x - 12 * s, y)], fill=col, width=int(16 * s))
    d.line([(x + 10 * s, y - 70 * s), (x + 12 * s, y)], fill=col, width=int(16 * s))
    by = y - 70 * s - (abs(math.sin(t * 12)) * 8 * s if cough else 0)
    d.rounded_rectangle([x - 30 * s, by - 94 * s, x + 30 * s, by + 4 * s], radius=int(12 * s), fill=col)
    for k in range(3):
        d.line([(x - 30 * s, by - 80 * s + k * 30 * s), (x + 30 * s, by - 80 * s + k * 30 * s)], fill=WHITE, width=3)
    hy = by - 122 * s
    d.ellipse([x - 25 * s, hy - 27 * s, x + 25 * s, hy + 27 * s], fill=(210, 200, 190))   # в пепле
    d.chord([x - 26 * s, hy - 29 * s, x + 26 * s, hy], 180, 360, fill=(60, 56, 54))
    d.ellipse([x - 8 * s, hy + 8 * s, x + 8 * s, hy + 20 * s], fill=(70, 40, 40))


def smoke(d, x, y, t, n=8, spread=1.0):
    for k in range(n):
        ft = (t * 0.5 + k / n) % 1
        r = 30 + ft * 70
        d.ellipse([x - r + math.sin(t + k) * 30 * spread, y - ft * 300 - r, x + r + math.sin(t + k) * 30 * spread,
                   y - ft * 300 + r], fill=lc((150, 150, 156), (70, 70, 80), ft))


def draw_clock(d, cx, cy, hour, minute):
    d.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(246, 244, 236), outline=(40, 40, 50), width=12)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line([(cx + math.sin(a) * 170, cy - math.cos(a) * 170), (cx + math.sin(a) * 186, cy - math.cos(a) * 186)],
               fill=(40, 40, 50), width=6)
    ha = (hour % 12 + minute / 60) / 12 * 2 * math.pi
    ma = minute / 60 * 2 * math.pi
    d.line([(cx, cy), (cx + math.sin(ha) * 100, cy - math.cos(ha) * 100)], fill=(30, 30, 30), width=14)
    d.line([(cx, cy), (cx + math.sin(ma) * 160, cy - math.cos(ma) * 160)], fill=RED, width=8)


def icon_let_in(d, cx, cy, s):
    d.rectangle([cx - 80 * s, cy - 100 * s, cx + 80 * s, cy + 90 * s], fill=(60, 64, 60))
    d.polygon([(cx - 80 * s, cy - 100 * s), (cx - 20 * s, cy - 80 * s), (cx - 20 * s, cy + 110 * s), (cx - 80 * s, cy + 90 * s)],
              fill=(120, 128, 136))
    for k in range(4):
        x = cx - 10 * s + k * 40 * s
        d.ellipse([x - 14 * s, cy - 20 * s, x + 14 * s, cy + 8 * s], fill=(236, 194, 160))
        d.rectangle([x - 14 * s, cy + 8 * s, x + 14 * s, cy + 70 * s], fill=[(34, 36, 44), (120, 90, 70), (34, 36, 44),
                    (240, 236, 230)][k])


def icon_nobody(d, cx, cy, s):
    d.rectangle([cx - 100 * s, cy - 100 * s, cx + 100 * s, cy + 90 * s], fill=STEEL)
    d.ellipse([cx - 50 * s, cy - 60 * s, cx + 50 * s, cy + 40 * s], outline=(70, 74, 82), width=int(10 * s))
    d.ellipse([cx - 110 * s, cy - 110 * s, cx + 110 * s, cy + 100 * s], outline=RED, width=int(14 * s))
    d.line([(cx - 76 * s, cy + 66 * s), (cx + 76 * s, cy - 76 * s)], fill=RED, width=int(14 * s))


R.ICONS["let_in"] = icon_let_in
R.ICONS["nobody"] = icon_nobody


def school_yard(img, gt, red=0.4, night=False, rub=0.0, sign=False):
    d = R.draw_sky(img, gt, red)
    R.draw_landscape(d); R.draw_ground(d)
    draw_school(d, 540, glow=night, t=gt)
    if rub > 0:
        rubble(d, 540, rub)
    if sign:
        gas_sign(d, 820, GROUND - 330, 0.9)
    if night:
        night_overlay(img, 110)
    return ImageDraw.Draw(img)


# ---------- сцены ----------

def render_scene(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    dur = seg["dur"]

    if sc in ("prev_vent", "prev_note"):
        EP5_SCENE(img, dict(seg, scene="vent2" if sc == "prev_vent" else "note"), i, lt + 1.6, p, gt, st)
        tinted_prev(img, gt)
        return
    if sc == "votes":
        d = booth_scene(img, gt, red=0.5, night=False)
        k = ease_out(clamp((lt - 0.1) / 0.9))
        for j, (lab, val, col) in enumerate([("ПРЕДУПРЕДИТЬ", 71, GREEN), ("ПРОВЕСТИ", 29, RED)]):
            y = 470 + j * 190
            d.text((90, y - 60), lab, font=font(52), fill=col, anchor="lm")
            d.rounded_rectangle([90, y - 20, 990, y + 60], radius=20, fill=(30, 34, 52))
            wv = 900 * val / 100 * k
            if wv > 30: d.rounded_rectangle([90, y - 20, 90 + wv, y + 60], radius=20, fill=col)
            d.text((990, y - 60), f"{int(val * k)} %", font=font(52), fill=WHITE, anchor="rm")
        return
    if sc in ("leave_post", "run"):
        if sc == "leave_post":
            d = booth_scene(img, gt, red=0.4)
            R.draw_hero(d, 760, GROUND + 4, 1.3, gt, face=1)
            k = clamp(lt / 1.0)
            x = lerp(800, 880, k); y = GROUND - 200 + 200 * k * k - 150 * math.sin(k * math.pi)
            d.rectangle([x - 40, y - 30, x + 40, y + 30], fill=(40, 50, 90))
            R.draw_stamp(img, "УВОЛЬНЯЮСЬ", lt - 1.0, cy=450)
        else:
            d = R.draw_sky(img, gt, 0.6)
            R.draw_landscape(d); R.draw_ground(d)
            for k in range(60):
                x = (k * 97 - gt * 120) % W; y = (k * 53 + gt * 80 * (1 + k % 3)) % GROUND
                d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(170, 170, 176))
            draw_school(d, 980 - lt * 60, t=gt)
            R.draw_hero(d, 360, GROUND + 4, 1.4, gt * 1.6, walk=True)
            night_overlay(img, 110)
        return
    if sc in ("clock4", "clock6"):
        img.paste((16, 16, 24), (0, 0, W, R.SOIL_BOT))
        d = ImageDraw.Draw(img)
        if sc == "clock4":
            draw_clock(d, 540, 560, 4, int(lt * 6) % 60)
            outlined(d, (540, 880), "ДО КОЛОННЫ 2 ЧАСА", 60, RED)
        else:
            draw_clock(d, 540, 560, 6, 0)
            outlined(d, (540, 880), "06:00", 110, RED)
        return

    # --- в школе ночью ---
    if sc in ("door", "valya_cold", "confess", "crowd", "masha_def", "gena_go"):
        d = school_yard(img, gt, night=True)
        d = ImageDraw.Draw(img)
        R.draw_hero(d, 700, GROUND + 4, 1.3, gt, face=-1)
        draw_valya(d, 500, GROUND + 4, 1.25)
        if sc in ("crowd", "masha_def", "gena_go"):
            draw_crowd(d, 60, 420, GROUND + 4, 6, seed=4)
            draw_crowd(d, 820, 1060, GROUND + 4, 3, seed=5)
        if sc in ("masha_def", "gena_go"):
            draw_kid(d, 600, GROUND + 4, 1.1, **MASHA)
        if sc == "gena_go":
            draw_gena(d, 840, GROUND + 4, 1.3, gt, boots=False, face=-1)
        if sc == "valya_cold":
            bubble(d, 480, 430, "ОПЯТЬ ПОГРЕБ?", 50, tail=1)
        if sc == "confess":
            for k, w in enumerate(["БАНК", "ВОЕННЫЕ", "Я СОВРАЛ"]):
                if lt > k * 0.9:
                    outlined(d, (540, 380 + k * 110), w, 80, [WHITE, WHITE, RED][k])
        if sc == "crowd":
            bubble(d, 260, 430, "ШПИОН БАНКА!", 50, col=(200, 60, 50), tcol=WHITE, tail=-1)
        if sc == "masha_def":
            bubble(d, 600, 450, "ОН ХОРОШИЙ!", 50, col=(255, 230, 120), tail=-1)
        if sc == "gena_go":
            outlined(d, (540, 450), "2 ЧАСА", 140, YEL)
        return
    if sc in ("plan", "plan1", "plan2", "plan3"):
        d = school_yard(img, gt, night=True,
                        rub={"plan": 0, "plan1": ease_io(lt / max(0.5, dur)), "plan2": 1, "plan3": 1}[sc],
                        sign=sc in ("plan2", "plan3") and (sc == "plan3" or lt > 0.8))
        d = ImageDraw.Draw(img)
        if sc == "plan":
            s = back_out(lt / 0.4)
            d.rectangle([540 - 240 * s, 520 - 200 * s, 540 + 240 * s, 520 + 200 * s], fill=(246, 244, 236))
            for k, w in enumerate(["1. ВХОД", "2. ТАБЛИЧКА", "3. ФИЛЬТР"]):
                d.text((360, 400 + k * 110), w, font=font(int(50 * s) + 1), fill=(30, 30, 40), anchor="lm")
        if sc == "plan1":
            draw_crowd(d, 80, 300, GROUND + 4, 4, seed=7)
            draw_crowd(d, 800, 1040, GROUND + 4, 4, seed=8)
        if sc == "plan3":
            outlined(d, (400, 470), "ФИЛЬТР", 110, (140, 210, 255))
        return
    if sc in ("back", "filter", "cough", "out", "director", "bushes"):
        d = field(img, gt, red=0.5)
        draw_booth(d, 900)
        draw_vent_pipe(d, 420, gt, talk=False)
        if sc in ("filter", "cough", "out", "director", "bushes"):
            # крышка снята, внутрь затягивает пепел
            d.ellipse([370, GROUND - 170, 470, GROUND - 130], fill=(150, 150, 160))
            for k in range(10):
                ft = (gt * 0.8 + k / 10) % 1
                x = lerp(420 + math.sin(k) * 260, 420, ft); y = lerp(GROUND - 500, GROUND - 120, ft)
                d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(140, 140, 146))
        if sc in ("cough", "out", "director"):
            smoke(d, 650, GROUND - 20, gt, n=7)
        if sc in ("back", "filter"):
            R.draw_hero(d, 500 if sc == "filter" else lerp(1150, 520, ease_out(clamp(lt / 1.6))), GROUND + 4, 1.25,
                        gt, walk=sc == "back" and lt < 1.6, face=-1)
            if sc == "back":
                for k in range(3):
                    ft = (gt * 0.5 + k / 3) % 1
                    d.text((650 + ft * 60, GROUND - 60 - ft * 200), "Z", font=font(int(40 + ft * 30)),
                           fill=lc((40, 40, 60), WHITE, 1 - ft), anchor="mm")
        if sc == "cough":
            outlined(d, (650, 450), "КХЕ! КХЕ!", 110, WHITE)
        if sc in ("out", "director", "bushes"):
            n = 6 if sc != "out" else 1 + int(5 * clamp(lt / max(0.5, dur - 0.3)))
            for k in range(n):
                pajama(d, 560 + k * 75, GROUND + 4, 1.0, col=[(120, 160, 220), (220, 140, 170), (140, 200, 140)][k % 3],
                       t=gt + k, cough=True)
            draw_dog(d, 1010, GROUND + 4, 0.9)
        if sc == "director":
            bubble(d, 600, 420, "ГДЕ ОХРАНА?!", 56, col=(20, 20, 26), tcol=WHITE, tail=-1)
        if sc == "bushes":
            for k in range(5):   # куст
                d.ellipse([60 + k * 50, GROUND - 160 + (k % 2) * 30, 200 + k * 50, GROUND + 10], fill=(40, 90, 50))
            d.ellipse([170, GROUND - 120, 210, GROUND - 80], fill=(240, 196, 160))
            d.chord([166, GROUND - 130, 214, GROUND - 98], 180, 360, fill=(200, 80, 40))
            outlined(d, (220, 440), "ХА-ХА", 100, YEL)
        night_overlay(img, 60)
        return

    # --- утро, колонна у школы ---
    if sc in ("column", "at_school", "commander", "works", "ark_car", "ark_walk", "his_school", "clear"):
        rub = 1.0 if sc not in ("clear",) else 1 - ease_io(lt / max(0.5, dur))
        d = school_yard(img, gt, red=0.5, rub=rub, sign=True)
        k = ease_out(clamp(lt / 1.8)) if sc == "column" else 1
        for j in range(3):
            draw_truck(d, lerp(-500 - j * 340, 120 - j * 330, k) if j == 0 else lerp(-800 - j * 340, -160 - (j - 1) * 330, k),
                       army=True)
        if sc != "column":
            draw_soldier(d, 300, GROUND + 4, 1.25, gt)
            draw_soldier(d, 390, GROUND + 4, 1.25, gt)
        if sc == "commander":
            bubble(d, 300, 430, "ТУТ ЖЕ СВАЛКА", 48, col=(40, 70, 40), tcol=WHITE, tail=-1)
        if sc == "works":
            R.draw_stamp(img, "СРАБОТАЛО?", lt - 0.2, col=(40, 150, 70), cy=450)
        if sc in ("ark_car", "ark_walk", "his_school", "clear"):
            ax = 470
            if sc == "ark_car":
                draw_car(d, lerp(1500, 940, ease_out(clamp(lt / 1.4))), gt)
                ax = 900
            elif sc == "ark_walk":
                draw_car(d, 940, gt)
                ax = lerp(880, 640, ease_io(clamp(lt / max(0.5, dur))))
            else:
                draw_car(d, 940, gt)
                ax = 640
            draw_arkady(d, ax, GROUND + 4, 1.25, gt, face=-1, walk=sc == "ark_walk")
        if sc == "his_school":
            # фото выпускника
            s = back_out(lt / 0.4)
            d.rectangle([540 - 220 * s, 440 - 170 * s, 540 + 220 * s, 440 + 170 * s], fill=(230, 220, 190),
                        outline=(120, 90, 60), width=8)
            draw_kid(d, 540, 440 + 120 * s, 1.4 * s, col=(40, 50, 90), hair=(30, 26, 24))
            d.text((540, 440 - 130 * s), "ВЫПУСК 1998", font=font(int(36 * s) + 1), fill=(90, 60, 40), anchor="mm")
        if sc == "clear":
            draw_soldier(d, 520, GROUND + 4, 1.2, gt)
            bubble(d, 640, 430, "ЗДЕСЬ.", 60, col=(20, 20, 26), tcol=WHITE, tail=1)
        return
    if sc in ("hatch", "order", "masha_up", "freeze", "seconds", "ark_lie", "doubt", "blast", "retreat",
              "ark_alone", "hand", "come_in"):
        d = school_yard(img, gt, red=0.5 if sc not in ("blast",) else 0.9, rub=0.0, sign=True)
        # открытый люк у школы
        d.rectangle([480, GROUND - 14, 600, GROUND + 4], fill=(20, 20, 24))
        d.polygon([(480, GROUND - 14), (440, GROUND - 120), (560, GROUND - 120), (600, GROUND - 14)], fill=STEEL)
        trucks = sc not in ("retreat", "ark_alone", "hand", "come_in")
        if sc == "retreat":
            k = ease_io(clamp(lt / max(0.5, dur)))
            for j in range(3):
                draw_truck(d, lerp(120 - j * 330, -900 - j * 330, k), army=True)
        elif trucks:
            for j in range(2):
                draw_truck(d, 120 - j * 330, army=True)
            draw_soldier(d, 330, GROUND + 4, 1.2, gt, face=1)
            draw_soldier(d, 410, GROUND + 4, 1.2, gt, face=1)
        ax = 720
        draw_arkady(d, ax, GROUND + 4, 1.3, gt, face=-1, pale=sc in ("freeze", "seconds"))
        if sc in ("masha_up", "freeze", "seconds", "ark_lie", "doubt", "blast", "ark_alone", "hand", "come_in", "retreat"):
            my = lerp(GROUND + 150, GROUND + 4, ease_out(clamp(lt / 1.2))) if sc == "masha_up" else GROUND + 4
            mx = 560 if sc not in ("hand", "come_in") else 640
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_kid(ImageDraw.Draw(tmp), mx, my, 1.15, face=1, **MASHA)
            clip = tmp.crop((0, 0, W, GROUND + 6)); img.paste(clip, (0, 0), clip)
            d = ImageDraw.Draw(img)
        if sc == "hatch":
            outlined(d, (540, 450), "300 ПАР ГЛАЗ", 100, WHITE)
            for k in range(8):
                ex = 500 + (k % 4) * 26; ey = GROUND - 4 + (k // 4) * 8
                if int(gt * 3 + k) % 5:
                    d.ellipse([ex - 4, ey - 3, ex + 4, ey + 3], fill=WHITE)
        if sc == "order":
            bubble(d, 360, 430, "ПО ОДНОМУ!", 56, col=(40, 70, 40), tcol=WHITE, tail=-1)
        if sc == "freeze":
            d.line([(700, 640), (590, 690)], fill=YEL, width=8)
        if sc == "seconds":
            n = min(3, 1 + int(lt / max(0.4, dur / 3)))
            outlined(d, (540, 450), "…".join(str(k) for k in range(1, n + 1)), 160, WHITE)
        if sc == "ark_lie":
            bubble(d, 760, 430, "ЭТО ПОГРЕБ.", 56, col=(20, 20, 26), tcol=WHITE, tail=1)
            bubble(d, 760, 540, "Я ОШИБСЯ.", 48, col=(20, 20, 26), tcol=WHITE, tail=1)
        if sc == "doubt":
            outlined(d, (400, 470), "?", 200, YEL)
        if sc == "blast":
            k = clamp(lt / 0.6)
            meteor(d, lerp(1000, 900, k), lerp(150, 700, k), 30, gt)
            if lt > 0.6:
                kk = clamp((lt - 0.6) / 0.8)
                d.ellipse([900 - 500 * kk, 700 - 300 * kk, 900 + 500 * kk, 700 + 300 * kk], fill=(255, 220, 140))
                shake(img, 12 * (1 - kk), gt)
                d = ImageDraw.Draw(img)
            outlined(d, (360, 450), "ЗА РЕКОЙ!", 90, RED)
        if sc == "ark_alone":
            outlined(d, (540, 420), "БЕЗ БАНКА", 90, WHITE)
            outlined(d, (540, 530), "БЕЗ БУНКЕРА", 90, RED)
        if sc == "hand":
            d.line([(680, GROUND - 90), (700, GROUND - 120)], fill=(240, 200, 170), width=10)
            outlined(d, (540, 470), "♥", 160, RED)
        if sc == "come_in":
            draw_gena(d, 380, GROUND + 4, 1.3, gt, boots=False, face=1)
            bubble(d, 380, 440, "ЗАХОДИ.", 64, tail=-1)
        return
    if sc in ("bankers", "ruined", "beg", "count", "two"):
        d = school_yard(img, gt, red=0.6, sign=True)
        d.rectangle([480, GROUND - 14, 600, GROUND + 4], fill=(20, 20, 24))
        draw_gena(d, 560, GROUND + 4, 1.25, gt, boots=False, face=1)
        R.draw_hero(d, 450, GROUND + 4, 1.2, gt)
        for k in range(6):
            pajama(d, 690 + k * 60, GROUND + 4, 0.95, col=[(120, 160, 220), (220, 140, 170), (140, 200, 140)][k % 3],
                   t=gt + k, cough=sc == "bankers")
        draw_dog(d, 1050, GROUND + 4, 0.8)
        if sc == "ruined":
            s = back_out(lt / 0.4)
            d.rectangle([540 - 260 * s, 470 - 170 * s, 540 + 260 * s, 470 + 170 * s], fill=(60, 60, 66),
                        outline=WHITE, width=5)
            d.rectangle([380, 380, 700, 560], fill=(130, 130, 136)) if s > 0.8 else None
            if s > 0.8:
                d.text((540, 470), "ПЕПЕЛ", font=font(70), fill=(60, 60, 66), anchor="mm")
        if sc == "beg":
            bubble(d, 760, 430, "МЫ ЗАПЛАТИМ!", 56, col=(20, 20, 26), tcol=WHITE, tail=-1)
            for k in range(6):
                ft = (gt * 0.8 + k / 6) % 1
                d.rectangle([860 + k * 20 - 30, 560 + ft * 300 - 16, 860 + k * 20 + 30, 560 + ft * 300 + 16], fill=(90, 170, 100))
        if sc == "count":
            n = int(lerp(200, 298, ease_out(clamp(lt / max(0.5, dur - 0.3)))))
            outlined(d, (540, 400), "МЕСТ: 300", 90, WHITE)
            outlined(d, (540, 520), f"НАС: {n}", 90, YEL)
        if sc == "two":
            outlined(d, (540, 400), "СВОБОДНО: 2", 90, GREEN)
            outlined(d, (540, 520), "БАНКИРОВ: 7", 90, RED)
        return
    if sc in ("radio", "radio2", "cut"):
        d = shelter(img, gt)
        draw_radio(d, 540, 760, gt, on=sc != "cut")
        if sc == "radio2":
            bubble(d, 540, 470, "ТРАЕКТОРИЯ ИЗМЕНИЛАСЬ", 42, col=(20, 20, 26), tcol=YEL, tail=-1)
            bubble(d, 540, 570, "НОВАЯ ДАТА УДАРА…", 42, col=(20, 20, 26), tcol=RED, tail=-1)
        if sc == "cut":
            for k in range(500):
                x = R.rnd.randrange(W); y = R.rnd.randrange(R.SOIL_BOT)
                c = R.rnd.randrange(40, 200)
                d.rectangle([x, y, x + 6, y + 3], fill=(c, c, c))
            outlined(d, (540, 470), "ШШШШ…", 130, WHITE)
        return
    if sc.startswith("choice"):
        foc = {"choice_l": 0, "choice_r": 1}.get(sc)
        shelter(img, gt)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 90)); img.paste(ov, (0, 0), ov)
        R.draw_choice(img, lt if sc == "choice" else 5.0, gt, focus=foc, vote=sc.startswith("choice_vote"))
        d = ImageDraw.Draw(img)
        if sc == "choice_vote2":
            s = back_out(lt / 0.5)
            d.text((540, 960), "СЕРИЯ 7 — ДАТА УДАРА", font=font(int(46 * s) + 1), fill=RED, anchor="mm")
        return
    raise KeyError(sc)


R.render_scene = render_scene


def sfx_events(add, S, L, nxt, fx):
    th, pp, ca, wh, bo, ra, mo = (fx[k] for k in ("thud", "pop", "cash", "whoosh", "boom", "rain", "motor"))
    add(S("prev_vent"), wh(0.8)); add(S("prev_note"), wh(0.6)); add(S("votes"), wh(1.0))
    add(S("leave_post") + 1.0, th()); add(S("run"), wh(1.6))
    add(S("clock4"), th()); add(S("door"), th() * 0.7); add(S("door") + 0.3, th() * 0.7)
    add(S("crowd"), wh(1.0)); add(S("masha_def"), pp()); add(S("gena_go"), pp())
    for nm in ("plan", "plan1", "plan2", "plan3"): add(S(nm), pp())
    add(S("plan1"), ra(L("plan1")) * 0.6); add(S("plan2") + 0.8, th())
    add(S("filter"), wh(1.5)); add(S("cough"), th() * 0.5); add(S("cough") + 0.5, th() * 0.5)
    add(S("out"), wh(1.0)); add(S("director"), th()); add(S("bushes"), pp())
    add(S("clock6"), bo() * 0.5)
    add(S("column"), mo(L("column") + 0.5)); add(S("works") + 0.2, th())
    add(S("ark_car"), mo(1.4)); add(S("his_school"), pp())
    add(S("clear"), ra(L("clear")) * 0.6); add(S("hatch"), th())
    add(S("order"), pp()); add(S("freeze"), bo() * 0.3)
    for k in range(3): add(S("seconds") + k * 0.7, th() * 0.5)
    add(S("blast") + 0.6, bo()); add(S("retreat"), mo(L("retreat") + 0.4))
    add(S("hand"), pp()); add(S("come_in"), pp())
    add(S("bankers"), wh(0.8)); add(S("beg"), ca()); add(S("two"), th())
    add(S("radio"), ra(L("radio") + L("radio2")) * 0.5); add(S("radio2"), bo() * 0.3)
    add(S("cut"), ra(1.5) * 2.0)
    add(S("choice"), wh(0.5)); add(S("choice") + 0.15, wh(0.5)); add(S("choice") + 0.5, pp())
    add(S("choice_l"), pp()); add(S("choice_r"), pp())


if __name__ == "__main__":
    R.main()
