#!/usr/bin/env python3
"""Бункер за 25 000 $ — серия 3 (зрители выбрали СОСЕДА).

Поворот 1: вор — дядя Гена, но он спас героя от «серьёзных людей».
Поворот 2: Гена — бывший астроном: удар не через 255 дней, а через 60.
Финал: РАССКАЗАТЬ ВСЕМ или МОЛЧАТЬ + чёрная машина с номером на 66.

  python3 ep3.py --timings timings_ep3.json --audio audio/mix_ep3_norm.wav --out out/bunker_ep3.mp4
"""
import math, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import ep2
from ep2 import draw_bunker, draw_shed, draw_gena, bubble, draw_house, icon_neighbor, PX0, PX1, PD
from render import (W, H, GROUND, font, lerp, lc, clamp, ease_io, ease_out, back_out,
                    WHITE, GREY, YEL, RED, GREEN, BLUE)

EP2_SCENE = R.render_scene           # сцены серии 2 — для «В прошлой серии»
R.INIT = (290.0, 60.0, 600.0)
R.EP_LABEL = "СЕРИЯ 3"
R.END_LINES = ("РАССКАЗАТЬ или МОЛЧАТЬ?", "ПИШИ В КОММЕНТАРИЯХ")
R.CHOICE_CARDS = [("РАССКАЗАТЬ", "tell", YEL, 280, "ЛЮДИ УСПЕЮТ", "ТОЛПА У БУНКЕРА"),
                  ("МОЛЧАТЬ", "silent", BLUE, 800, "БУНКЕР НАШ", "40 СОСЕДЕЙ…")]

S_ = dict
R.SEGMENTS[:] = [
    S_(cap="В прошлой серии меня ограбили. Осталось !600 $!, а на камере — только *зелёный сапог*.",
       scene="prev_rob"),
    S_(cap="Вы выбрали *соседа*. Дядю Гену.", scene="votes"),
    S_(cap="Иду к нему. Он молча достаёт из-под матраса пачку денег.", scene="gena_money"),
    S_(cap="*10 000 $*. Наличными.", scene="gena_cash", budget=10600, delta=10000),
    S_(cap="Условие одно: место в бункере. И !код от двери! будет знать он тоже.", scene="gena_deal"),
    S_(cap="Договор пишем на *салфетке*.", scene="napkin"),
    S_(cap="Пункт четвёртый: *дверь*.", scene="door_tag", tag="4. ДВЕРЬ"),
    S_(cap="Гермодверь из стали, как на подводной лодке. Минус *3 500 $*.", scene="door", tag="4. ДВЕРЬ",
       budget=7100, delta=-3500, pct=70, days=280),
    S_(cap="Пункт пятый: *вентиляция*.", scene="vent_tag", tag="5. ВОЗДУХ"),
    S_(cap="Труба с фильтром — чтобы дышать, даже когда наверху !пепел!. Минус *2 500 $*.", scene="vent",
       tag="5. ВОЗДУХ", budget=4600, delta=-2500, pct=78, days=270),
    S_(cap="Пункт шестой: *еда*.", scene="food_tag", tag="6. ЕДА"),
    S_(cap="Консервы, вода, крупа — на двоих, на полгода. Минус *2 000 $*.", scene="food", tag="6. ЕДА",
       budget=2600, delta=-2000, pct=88, days=255),
    S_(cap="Дядя Гена работает лучше меня. Не устаёт, не жалуется.", scene="gena_work"),
    S_(cap="Но есть !странности!.", scene="weird"),
    S_(cap="Каждую ночь он ходит в бункер. !Один!.", scene="gena_night"),
    S_(cap="И приносит какие-то *коробки*.", scene="gena_boxes"),
    S_(cap="А однажды я замечаю: на нём снова !зелёные сапоги!.", scene="boots_again"),
    S_(cap="Ставлю новую камеру. *Внутри бункера*.", scene="cam_install"),
    S_(cap="Ночь. Запись.", scene="cam2"),
    S_(cap="Дядя Гена открывает дверь *своим кодом* и заносит внутрь !мешок!.", scene="cam2_bag"),
    S_(cap="Беру лопату и спускаюсь.", scene="descend"),
    S_(cap="— Дядя Гена! Что в мешке?", scene="confront"),
    S_(cap="Он молча высыпает его на пол.", scene="pour_bag"),
    S_(cap="Там мой *генератор*. Мои *инструменты*.", scene="reveal"),
    S_(cap="— Да. Это я тебя !ограбил!, — говорит он.", scene="confess"),
    S_(cap="— В ту ночь к тебе ехали те самые !серьёзные люди!. Я видел их машину.", scene="flash_car"),
    S_(cap="— Они забрали бы всё. А может, и тебя. Я успел *первым*.", scene="flash_first"),
    S_(cap="— А десять тысяч, что я тебе дал, — это твои же *7 900 $*. Плюс моя *пенсия*.", scene="math"),
    S_(cap="Я не знаю, что сказать. Но он ещё !не закончил!.", scene="not_done"),
    S_(cap="Он достаёт старое удостоверение. *Обсерватория*. Тридцать лет стажа.", scene="id_card"),
    S_(cap="— Я всю жизнь смотрел на небо. И этот астероид я *посчитал сам*.", scene="board"),
    S_(cap="— По радио !врут!, чтобы не было паники.", scene="board_lie"),
    S_(cap="— Он прилетит не через двести пятьдесят дней.", scene="board_250"),
    S_(cap="— А через !60!.", scene="sixty", days=60),
    S_(cap="Бункер готов на *88 %*. Еды — на двоих.", scene="status"),
    S_(cap="А в посёлке ещё !40 человек!, которые думают, что у них почти год.", scene="village"),
    S_(cap="И тут у забора останавливается !чёрная машина!.", scene="car_arrive"),
    S_(cap="Номер заканчивается на !66!.", scene="plate"),
    S_(cap="Два варианта. Оба !страшные!.", scene="choice", tag="ВЫБОР"),
    S_(cap="Первый: *рассказать всем*. Люди успеют подготовиться — но толпа может прийти за !нашим бункером!.",
       scene="choice_l", tag="ВЫБОР"),
    S_(cap="Второй: *молчать*. Закрыть дверь и спасти только себя и дядю Гену.", scene="choice_r", tag="ВЫБОР"),
    S_(cap="Но тогда сорок соседей не узнают, что у них !всего два месяца!.", scene="choice_r2", tag="ВЫБОР"),
    S_(cap="Пиши в комментариях: *рассказать* или *молчать*.", scene="choice_vote", tag="ВЫБОР"),
    S_(cap="А машина у забора всё ещё стоит. Следующая серия — !по вашему выбору!.", scene="choice_vote2",
       tag="ВЫБОР"),
]

STEEL = (120, 128, 140)


# ---------- объекты ----------

def draw_bunker_plus(d, door=True, vent=True, food=True, gen=False, light=True):
    draw_bunker(d, walls=1, roof=True)
    if door:   # стальной люк с штурвалом вместо простого
        d.rectangle([600, GROUND - 26, 700, GROUND], fill=STEEL)
        d.ellipse([628, GROUND - 46, 672, GROUND - 2], outline=(70, 74, 82), width=6)
        d.line([(650, GROUND - 44), (650, GROUND - 4)], fill=(70, 74, 82), width=5)
        d.line([(630, GROUND - 24), (670, GROUND - 24)], fill=(70, 74, 82), width=5)
    if vent:
        d.rectangle([410, GROUND - 120, 430, GROUND + 30], fill=(150, 150, 160))
        d.chord([385, GROUND - 150, 455, GROUND - 100], 180, 360, fill=(150, 150, 160))
    if food:
        for row in range(2):
            y = GROUND + 120 + row * 70
            d.rectangle([PX0 + 40, y, PX0 + 200, y + 6], fill=(150, 110, 70))
            for k in range(6):
                d.rectangle([PX0 + 46 + k * 25, y - 34, PX0 + 66 + k * 25, y], fill=[(200, 60, 50), (220, 180, 50),
                            (80, 140, 200)][(k + row) % 3])
        for k in range(3):
            d.rectangle([PX1 - 150 + k * 36, GROUND + 190, PX1 - 122 + k * 36, GROUND + 240], fill=(110, 170, 230))
    if gen:
        d.rounded_rectangle([PX1 - 170, GROUND + 160, PX1 - 50, GROUND + 240], radius=8, fill=(200, 60, 50))
    if light:
        d.line([(540, GROUND + 30), (540, GROUND + 60)], fill=(40, 40, 40), width=3)
        d.ellipse([528, GROUND + 58, 552, GROUND + 82], fill=(255, 230, 140))


def draw_car(d, x, t, lights=True):
    y = GROUND
    d.rounded_rectangle([x - 200, y - 110, x + 200, y - 30], radius=24, fill=(14, 14, 18))
    d.polygon([(x - 120, y - 110), (x - 70, y - 170), (x + 90, y - 170), (x + 140, y - 110)], fill=(14, 14, 18))
    d.polygon([(x - 100, y - 112), (x - 62, y - 158), (x + 4, y - 158), (x + 4, y - 112)], fill=(40, 50, 70))
    d.polygon([(x + 14, y - 112), (x + 14, y - 158), (x + 84, y - 158), (x + 122, y - 112)], fill=(40, 50, 70))
    for wx in (x - 120, x + 120):
        d.ellipse([wx - 40, y - 70, wx + 40, y + 6], fill=(10, 10, 12))
        d.ellipse([wx - 16, y - 46, wx + 16, y - 16], fill=(80, 80, 86))
    if lights:
        d.ellipse([x - 206, y - 96, x - 180, y - 70], fill=(255, 250, 210))


def icon_tell(d, cx, cy, s):
    d.polygon([(cx - 120 * s, cy - 30 * s), (cx - 40 * s, cy - 30 * s), (cx + 60 * s, cy - 90 * s),
               (cx + 60 * s, cy + 50 * s), (cx - 40 * s, cy - 10 * s), (cx - 120 * s, cy - 10 * s)], fill=YEL)
    d.rectangle([cx - 100 * s, cy - 10 * s, cx - 70 * s, cy + 50 * s], fill=YEL)
    for k in range(3):
        r = (40 + k * 30) * s
        d.arc([cx + 60 * s - r, cy - 20 * s - r, cx + 60 * s + r, cy - 20 * s + r], -40, 40, fill=WHITE,
              width=int(6 * s))
    for k in range(5):   # толпа
        hx = cx - 120 * s + k * 60 * s
        d.ellipse([hx - 16 * s, cy + 60 * s, hx + 16 * s, cy + 92 * s], fill=(140, 140, 150))


def icon_silent(d, cx, cy, s):
    d.rounded_rectangle([cx - 90 * s, cy - 110 * s, cx + 90 * s, cy + 90 * s], radius=int(12 * s), fill=STEEL)
    d.ellipse([cx - 50 * s, cy - 60 * s, cx + 50 * s, cy + 40 * s], outline=(70, 74, 82), width=int(10 * s))
    d.line([(cx, cy - 58 * s), (cx, cy + 38 * s)], fill=(70, 74, 82), width=int(8 * s))
    d.line([(cx - 48 * s, cy - 10 * s), (cx + 48 * s, cy - 10 * s)], fill=(70, 74, 82), width=int(8 * s))
    d.rounded_rectangle([cx + 40 * s, cy + 30 * s, cx + 120 * s, cy + 100 * s], radius=int(10 * s), fill=(220, 180, 50))
    d.arc([cx + 52 * s, cy - 10 * s, cx + 108 * s, cy + 50 * s], 180, 360, fill=(220, 180, 50), width=int(10 * s))


R.ICONS["tell"] = icon_tell
R.ICONS["silent"] = icon_silent


def interior(img, gt, lamp=1.0, gen=False, mess=False):
    """Крупный план бункера изнутри."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, R.SOIL_BOT], fill=(96, 98, 104))
    d.rectangle([60, 200, W - 60, R.SOIL_BOT - 60], fill=(60, 60, 66))
    d.rectangle([0, R.SOIL_BOT - 60, W, R.SOIL_BOT], fill=(80, 80, 86))
    # лестница из люка
    d.rectangle([780, 200, 880, 230], fill=STEEL)
    for k in range(9):
        d.line([(790, 250 + k * 95), (870, 250 + k * 95)], fill=(150, 150, 160), width=8)
    d.line([(790, 230), (790, R.SOIL_BOT - 60)], fill=(150, 150, 160), width=8)
    d.line([(870, 230), (870, R.SOIL_BOT - 60)], fill=(150, 150, 160), width=8)
    # полки с консервами
    for row in range(3):
        y = 520 + row * 150
        d.rectangle([110, y, 460, y + 12], fill=(150, 110, 70))
        for k in range(10):
            d.rectangle([118 + k * 34, y - 60, 146 + k * 34, y], fill=[(200, 60, 50), (220, 180, 50),
                        (80, 140, 200)][(k + row) % 3])
    # лампа
    lc_ = lc((60, 60, 50), (255, 230, 140), lamp)
    d.line([(560, 200), (560, 300)], fill=(30, 30, 30), width=4)
    d.ellipse([536, 296, 584, 344], fill=lc_)
    if gen or mess:
        d.rounded_rectangle([480, 1140, 680, 1280], radius=12, fill=(200, 60, 50))
        d.ellipse([520, 1170, 580, 1230], fill=(70, 70, 76))
        d.text((580, 1110), "ГЕНЕРАТОР", font=font(30), fill=WHITE, anchor="mm")
    if mess:
        for k, (x, y, a) in enumerate([(300, 1270, 0.3), (380, 1285, -0.5), (720, 1275, 0.8), (260, 1250, 1.2)]):
            d.line([(x - 40 * math.cos(a), y - 40 * math.sin(a)), (x + 40 * math.cos(a), y + 40 * math.sin(a))],
                   fill=(170, 175, 185), width=12)
        d.polygon([(640, 1300), (700, 1240), (780, 1300)], fill=(120, 100, 70))   # мешок
    return d


def night_overlay(img, a=150):
    ov = Image.new("RGBA", (W, H), (0, 0, 12, a)); img.paste(ov, (0, 0), ov)
    return ImageDraw.Draw(img)


def flashlight(img, x, y, dirx, a=70, spread=160, length=420):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(x, y), (x + dirx * length, y - spread), (x + dirx * length, y + spread)],
                               fill=(255, 240, 180, a))
    img.paste(ov, (0, 0), ov)


def field(img, gt, **kw):
    d = R.draw_sky(img, gt, kw.pop("red", 0.0))
    R.draw_landscape(d); R.draw_ground(d); R.draw_fence(d, 60, 250)
    draw_bunker_plus(d, **kw)
    return d


def outlined(d, xy, text, size, col, stroke=10):
    d.text(xy, text, font=font(size), fill=col, anchor="mm", stroke_width=stroke, stroke_fill=(16, 12, 16))


# ---------- сцены ----------

def render_scene(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    dur = seg["dur"]

    if sc == "prev_rob":
        EP2_SCENE(img, dict(seg, scene="stolen"), i, lt + 0.3, p, gt, st)
        ov = Image.new("RGBA", (W, H), (60, 40, 20, 70)); img.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(img)
        d.rectangle([20, 200, W - 20, R.SOIL_BOT - 10], outline=(240, 236, 226), width=6)
        if int(gt * 2) % 2 == 0:
            d.ellipse([50, 225, 80, 255], fill=RED)
        d.text((95, 240), "В ПРОШЛОЙ СЕРИИ", font=font(40), fill=WHITE, anchor="lm")
        if lt > 1.8:
            # врезка с сапогом
            d.rounded_rectangle([600, 300, 1000, 620], radius=18, fill=(30, 40, 34), outline=WHITE, width=5)
            d.rounded_rectangle([750, 400, 800, 560], radius=10, fill=(70, 160, 80))
            d.rounded_rectangle([750, 510, 850, 560], radius=14, fill=(70, 160, 80))
            d.text((800, 340), "CAM 1", font=font(30), fill=WHITE, anchor="mm")
        return
    if sc == "votes":
        d = field(img, gt, door=False, vent=False, food=False, light=False)
        k = ease_out(clamp((lt - 0.2) / 1.2))
        for j, (lab, val, col) in enumerate([("СОСЕД", 64, GREEN), ("ЗАЙМ", 36, RED)]):
            y = 470 + j * 190
            d.text((90, y - 60), lab, font=font(52), fill=col, anchor="lm")
            d.rounded_rectangle([90, y - 20, 990, y + 60], radius=20, fill=(30, 34, 52))
            wv = 900 * val / 100 * k
            if wv > 30:
                d.rounded_rectangle([90, y - 20, 90 + wv, y + 60], radius=20, fill=col)
            d.text((990, y - 60), f"{int(val * k)} %", font=font(52), fill=WHITE, anchor="rm")
        if lt > 1.3:
            R.draw_stamp(img, "ДЯДЯ ГЕНА", lt - 1.3, col=(40, 150, 70), cy=880)
        return
    if sc in ("gena_money", "gena_cash", "gena_deal", "napkin"):
        d = R.draw_sky(img, gt, 0.0)
        R.draw_landscape(d); R.draw_ground(d)
        draw_house(d, 420)
        draw_gena(d, 330, GROUND + 4, 1.4, gt, boots=False, face=1)
        R.draw_hero(d, 820, GROUND + 4, 1.4, gt, face=-1)
        if sc == "gena_money":
            s = back_out((lt - 0.8) / 0.5)
            if s > 0.02:
                d.rectangle([400 - 60 * s, 700 - 34 * s, 400 + 60 * s, 700 + 34 * s], fill=(90, 170, 100),
                            outline=(50, 110, 60), width=5)
                d.text((400, 700), "$", font=font(int(46 * s) + 1), fill=(30, 80, 40), anchor="mm")
        elif sc == "gena_cash":
            for k in range(6):
                ft = clamp((lt - k * 0.12) / 0.6)
                x = lerp(400, 560 + (k % 3) * 70, ease_out(ft)); y = lerp(700, 470 + (k // 3) * 70, ease_out(ft))
                d.rectangle([x - 50, y - 28, x + 50, y + 28], fill=(90, 170, 100), outline=(50, 110, 60), width=4)
            outlined(d, (540, 330), "+10 000 $", 110, GREEN)
        elif sc == "gena_deal":
            bubble(d, 330, 450, "МЕСТО В БУНКЕРЕ", 40, tail=-1)
            if lt > 1.3:
                bubble(d, 330, 570, "И КОД ОТ ДВЕРИ", 40, col=(250, 220, 60), tail=-1)
        else:
            s = back_out(lt / 0.4)
            cx, cy = 560, 520
            d.rectangle([cx - 230 * s, cy - 180 * s, cx + 230 * s, cy + 180 * s], fill=(250, 250, 246))
            for k in range(0, int(460 * s), 22):
                d.arc([cx - 230 * s + k, cy - 190 * s, cx - 230 * s + k + 22, cy - 170 * s], 0, 180, fill=(220, 220, 214), width=3)
            d.text((cx, cy - 120 * s), "ДОГОВОР", font=font(int(46 * s) + 1), fill=(30, 30, 40), anchor="mm")
            d.text((cx, cy - 40 * s), "10 000 $ = 1 МЕСТО", font=font(int(36 * s) + 1, True), fill=(30, 30, 40),
                   anchor="mm")
            d.text((cx, cy + 20 * s), "+ КОД ОТ ДВЕРИ", font=font(int(36 * s) + 1, True), fill=RED, anchor="mm")
            if lt > 0.8:
                d.line([(cx - 190, cy + 120), (cx - 140, cy + 90), (cx - 100, cy + 125), (cx - 50, cy + 95)],
                       fill=(40, 60, 160), width=5)
                d.line([(cx + 50, cy + 120), (cx + 90, cy + 85), (cx + 120, cy + 130), (cx + 190, cy + 100)],
                       fill=(40, 60, 160), width=5)
        return
    if sc in ("door_tag", "door", "vent_tag", "vent", "food_tag", "food", "gena_work"):
        door = sc not in ("door_tag",)
        vent = sc in ("vent", "food_tag", "food", "gena_work")
        food = sc in ("food", "gena_work")
        if sc == "door":
            door = lt > 0.6
        if sc == "vent":
            vent = lt > 0.6
        if sc == "food":
            food = lt > 0.6
        d = field(img, gt, door=door, vent=vent, food=food)
        draw_gena(d, 230, GROUND + 4, 1.25, gt, boots=False, face=1)
        R.draw_hero(d, 880, GROUND + 4, 1.25, gt, face=-1)
        if sc == "door" and lt > 0.6:
            s = back_out((lt - 0.6) / 0.4)
            d.ellipse([540 - 150 * s, 560 - 150 * s, 540 + 150 * s, 560 + 150 * s], fill=STEEL,
                      outline=(70, 74, 82), width=int(12 * s) + 1)
            a = gt * 2
            for k in range(3):
                aa = a + k * math.pi / 3
                d.line([(540 - math.cos(aa) * 110 * s, 560 - math.sin(aa) * 110 * s),
                        (540 + math.cos(aa) * 110 * s, 560 + math.sin(aa) * 110 * s)], fill=(70, 74, 82),
                       width=int(14 * s) + 1)
            d.ellipse([540 - 26 * s, 560 - 26 * s, 540 + 26 * s, 560 + 26 * s], fill=(70, 74, 82))
        if sc == "vent" and lt > 0.6:
            for k in range(6):   # пепел, который фильтр не пускает
                ft = (gt * 0.6 + k / 6) % 1
                d.ellipse([300 + k * 80, 300 + ft * 500, 312 + k * 80, 312 + ft * 500], fill=(150, 150, 150))
            outlined(d, (540, 470), "ФИЛЬТР", 90, (140, 210, 255))
        if sc == "food" and lt > 0.6:
            outlined(d, (540, 450), "НА 2 ЧЕЛ. × 6 МЕС.", 70, YEL)
        if sc == "gena_work":
            for k in range(3):
                ft = (lt * 0.8 + k / 3) % 1
                d.text((230, 560 - ft * 200), "+", font=font(70), fill=lc(GREEN, (30, 50, 40), ft), anchor="mm")
            outlined(d, (560, 430), "88 %", 140, GREEN)
        return
    if sc == "weird":
        d = field(img, gt)
        draw_gena(d, 300, GROUND + 4, 1.4, gt, boots=False, sus=True)
        R.draw_hero(d, 820, GROUND + 4, 1.4, gt, face=-1)
        outlined(d, (560, 470), "?", 280, YEL)
        return
    if sc in ("gena_night", "gena_boxes"):
        d = field(img, gt)
        R.draw_hero(d, 1000, GROUND + 4, 0.9, gt, face=-1)     # герой подглядывает издалека
        gx = lerp(120, 600, ease_io(lt / max(0.5, dur)))
        draw_gena(d, gx, GROUND + 4, 1.3, gt, boots=True, face=1)
        if sc == "gena_boxes":
            d.rectangle([gx + 30, GROUND - 200, gx + 130, GROUND - 120], fill=(170, 130, 80), outline=(120, 90, 50), width=4)
            d.line([(gx + 30, GROUND - 160), (gx + 130, GROUND - 160)], fill=(120, 90, 50), width=4)
        night_overlay(img)
        flashlight(img, gx + 50, GROUND - 160, 1)
        d = ImageDraw.Draw(img)
        if sc == "gena_night":
            outlined(d, (540, 430), "КАЖДУЮ НОЧЬ", 70, WHITE)
        return
    if sc == "boots_again":
        d = R.draw_sky(img, gt, 0.0)
        R.draw_landscape(d); R.draw_ground(d)
        # крупный план сапог
        z = 1 + 0.2 * ease_out(clamp(lt / 1.2))
        for bx in (380, 640):
            d.rounded_rectangle([bx - 70 * z, GROUND - 300 * z, bx + 40 * z, GROUND], radius=20, fill=(70, 170, 85))
            d.rounded_rectangle([bx - 70 * z, GROUND - 90 * z, bx + 120 * z, GROUND], radius=26, fill=(70, 170, 85))
            d.rectangle([bx - 80 * z, GROUND - 320 * z, bx + 50 * z, GROUND - 290 * z], fill=(70, 70, 80))
        if lt > 0.8:
            R.draw_stamp(img, "ОПЯТЬ ОНИ", lt - 0.8, col=(40, 140, 60), cy=420)
        return
    if sc == "cam_install":
        d = interior(img, gt)
        R.draw_hero(d, 640, R.SOIL_BOT - 56, 1.5, gt, face=-1)
        d.rounded_rectangle([140, 240, 230, 290], radius=8, fill=(40, 40, 46))
        d.ellipse([120, 248, 150, 282], fill=(20, 20, 24))
        if int(gt * 3) % 2 == 0:
            d.ellipse([206, 248, 220, 262], fill=RED)
        outlined(d, (480, 360), "КАМЕРА №2", 70, WHITE)
        return
    if sc in ("cam2", "cam2_bag"):
        img.paste((10, 14, 12), (0, 0, W, R.SOIL_BOT))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([60, 220, W - 60, 1000], radius=26, fill=(36, 36, 42))
        scr = Image.new("RGB", (W - 160, 680), (26, 34, 30))
        sd = ImageDraw.Draw(scr)
        sd.rectangle([0, 560, scr.width, 680], fill=(40, 52, 44))
        for k in range(7):
            sd.line([(640, 120 + k * 70), (720, 120 + k * 70)], fill=(70, 90, 76), width=6)
        sd.line([(640, 100), (640, 560)], fill=(70, 90, 76), width=6)
        sd.line([(720, 100), (720, 560)], fill=(70, 90, 76), width=6)
        if sc == "cam2":
            open_ = ease_out(clamp((lt - 0.5) / 0.8))
            sd.rectangle([600, 0, 760, 100 - 60 * open_], fill=(80, 96, 86))
            if open_ > 0.5:
                sd.polygon([(680, 100), (520, 560), (840, 560)], fill=(70, 86, 70))
        else:
            gy = lerp(120, 560, ease_out(clamp(lt / 1.4)))
            sd.rectangle([660, gy - 160, 710, gy], fill=(10, 12, 10))
            sd.ellipse([660, gy - 210, 710, gy - 160], fill=(10, 12, 10))
            sd.polygon([(710, gy - 120), (780, gy - 60), (720, gy - 20)], fill=(10, 12, 10))
            sd.rounded_rectangle([650, gy - 30, 676, gy + 2], radius=4, fill=(70, 160, 80))   # сапог
        for k in range(700):
            x = R.rnd.randrange(scr.width); y = R.rnd.randrange(scr.height)
            c = R.rnd.randrange(30, 110); sd.point((x, y), fill=(c, c + 10, c))
        sd.text((24, 30), "CAM 2 — БУНКЕР", font=font(36), fill=WHITE)
        sd.text((scr.width - 24, 30), "02:4" + str(min(9, int(lt * 2))), font=font(36), fill=WHITE, anchor="ra")
        if int(gt * 2) % 2 == 0:
            sd.ellipse([24, scr.height - 64, 54, scr.height - 34], fill=RED)
            sd.text((66, scr.height - 50), "REC", font=font(32), fill=WHITE, anchor="lm")
        img.paste(scr, (80, 240))
        if sc == "cam2_bag" and lt > 1.0:
            R.draw_stamp(img, "КОД ЗНАЕТ ТОЛЬКО ОН", lt - 1.0, cy=1120)
        return
    if sc in ("descend", "confront", "pour_bag", "reveal", "confess", "math", "not_done"):
        lamp = 0.35 if sc in ("descend", "confront") else 1.0
        gen = sc in ("reveal", "confess", "math", "not_done")
        d = interior(img, gt, lamp=lamp, mess=gen)
        hy = R.SOIL_BOT - 56
        if sc == "descend":
            hy_ = lerp(560, hy, ease_io(lt / max(0.5, dur)))
            R.draw_hero(d, 830, hy_, 1.4, gt, shovel=True, dig=0.2, face=-1)
            draw_gena(d, 300, hy, 1.4, gt, boots=True, face=1)
        else:
            R.draw_hero(d, 830, hy, 1.4, gt, shovel=True, dig=0.2, face=-1)
            draw_gena(d, 300, hy, 1.4, gt, boots=True, face=1, sus=sc == "confront")
        if sc in ("descend", "confront"):
            night_overlay(img, 90)
            flashlight(img, 260, hy - 160, 1, a=60)
            d = ImageDraw.Draw(img)
            if sc == "confront":
                bubble(d, 760, 420, "ЧТО В МЕШКЕ?!", 50, tail=1)
            else:
                d.polygon([(370, hy - 20), (420, hy - 140), (480, hy - 20)], fill=(120, 100, 70))
        if sc == "pour_bag":
            d.polygon([(370, hy - 20), (420, hy - 140), (480, hy - 20)], fill=(120, 100, 70))
            for k in range(5):
                ft = clamp((lt - k * 0.15) / 0.8)
                d.rectangle([420 + k * 40 - 12, hy - 120 + ft * 100, 420 + k * 40 + 12, hy - 96 + ft * 100],
                            fill=(170, 175, 185))
        if sc == "reveal" and lt > 0.5:
            R.draw_stamp(img, "МОЙ ГЕНЕРАТОР", lt - 0.5, cy=430)
        if sc == "confess":
            bubble(d, 330, 420, "ДА. ЭТО Я.", 60, tail=-1)
            if lt > 1.0:
                R.draw_stamp(img, "ВОР — ГЕНА", lt - 1.0, cy=620)
        if sc == "math":
            s = back_out(lt / 0.4)
            outlined(d, (540, 420), "7 900 $", int(90 * s) + 1, YEL)
            if lt > 1.0:
                outlined(d, (540, 540), "+ 2 100 $ ПЕНСИИ", int(64 * s) + 1, WHITE)
            if lt > 2.0:
                outlined(d, (540, 660), "= 10 000 $", int(90 * s) + 1, GREEN)
        if sc == "not_done":
            outlined(d, (540, 470), "…", 200, WHITE)
        return
    if sc in ("flash_car", "flash_first"):
        d = field(img, gt, door=False, vent=False, food=False)
        draw_shed(d, 880, broken=sc == "flash_first")
        night_overlay(img, 130)
        d = ImageDraw.Draw(img)
        cx = lerp(1400, 1000, ease_out(clamp(lt / 1.5))) if sc == "flash_car" else 1000
        draw_car(d, cx + 220, gt)
        flashlight(img, cx + 14, GROUND - 82, -1, a=80, spread=90, length=600)
        d = ImageDraw.Draw(img)
        if sc == "flash_first":
            draw_gena(d, 700, GROUND + 4, 1.2, gt, boots=True, face=-1)
            d.rectangle([600, GROUND - 160, 660, GROUND - 100], fill=(120, 100, 70))
        ov = Image.new("RGBA", (W, H), (120, 80, 40, 50)); img.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(img)
        d.text((60, 240), "ТА НОЧЬ", font=font(40), fill=WHITE, anchor="lm")
        return
    if sc == "id_card":
        d = interior(img, gt, mess=True)
        s = back_out(lt / 0.5)
        cx, cy = 540, 620
        d.rounded_rectangle([cx - 340 * s, cy - 220 * s, cx + 340 * s, cy + 220 * s], radius=int(20 * s) + 1,
                            fill=(150, 40, 40))
        d.rounded_rectangle([cx - 320 * s, cy - 200 * s, cx + 320 * s, cy + 200 * s], radius=int(16 * s) + 1,
                            fill=(246, 240, 226))
        if s > 0.3:
            icon_neighbor(d, cx - 190 * s, cy + 20 * s, 0.9 * s)
            d.text((cx + 90 * s, cy - 140 * s), "ОБСЕРВАТОРИЯ", font=font(int(40 * s) + 1), fill=(30, 30, 40), anchor="mm")
            d.text((cx + 90 * s, cy - 60 * s), "СТ. НАУЧНЫЙ", font=font(int(32 * s) + 1, True), fill=(30, 30, 40), anchor="mm")
            d.text((cx + 90 * s, cy - 20 * s), "СОТРУДНИК", font=font(int(32 * s) + 1, True), fill=(30, 30, 40), anchor="mm")
            d.text((cx + 90 * s, cy + 60 * s), "СТАЖ: 30 ЛЕТ", font=font(int(36 * s) + 1), fill=(150, 40, 40), anchor="mm")
            d.ellipse([cx + 160 * s, cy + 100 * s, cx + 280 * s, cy + 190 * s], outline=(60, 80, 170), width=4)
        return
    if sc in ("board", "board_lie", "board_250", "sixty"):
        d = interior(img, gt, mess=True)
        # доска с расчётами
        d.rectangle([90, 230, 990, 900], fill=(30, 56, 44), outline=(120, 90, 60), width=14)
        d.ellipse([200, 600, 300, 700], fill=(70, 140, 220))           # Земля
        d.text((250, 730), "ЗЕМЛЯ", font=font(30), fill=WHITE, anchor="mm")
        k = clamp(lt / 1.5)
        pts = [(900, 300), (750, 420), (560, 520), (380, 610)]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=(240, 240, 230), width=5)
        d.ellipse([880, 280, 930, 330], fill=(160, 140, 120))
        for n in range(6):
            d.text((520 + (n % 3) * 140, 290 + (n // 3) * 50), ["v=", "Δt", "∫", "r²", "π", "≈"][n] +
                   str(17 + n * 3), font=font(30, True), fill=(220, 220, 210))
        if sc == "board_lie":
            R.draw_stamp(img, "ПО РАДИО ВРУТ", lt - 0.3, cy=500)
        if sc == "board_250":
            outlined(d, (650, 760), "НЕ 250 ДНЕЙ", 70, WHITE)
        if sc == "sixty":
            pulse = 1 + 0.08 * math.sin(gt * 12)
            outlined(d, (600, 700), "60", int(280 * pulse), RED, 14)
            outlined(d, (600, 860), "ДНЕЙ", 80, RED)
            if int(gt * 6) % 2 == 0:
                ov = Image.new("RGBA", (W, H), (200, 0, 0, 40)); img.paste(ov, (0, 0), ov)
        return
    if sc == "status":
        d = field(img, gt)
        draw_gena(d, 250, GROUND + 4, 1.2, gt, boots=False)
        R.draw_hero(d, 880, GROUND + 4, 1.2, gt, face=-1)
        outlined(d, (560, 430), "88 %", 150, GREEN)
        outlined(d, (560, 580), "ЕДА НА ДВОИХ", 56, YEL)
        return
    if sc == "village":
        d = R.draw_sky(img, gt, 0.0)
        R.draw_landscape(d); R.draw_ground(d)
        rnd = R.random.Random(5)
        for k in range(9):
            x = 60 + k * 125; hh = 120 + rnd.randrange(60)
            d.rectangle([x - 50, GROUND - hh, x + 50, GROUND], fill=(130 + rnd.randrange(30), 90, 60))
            d.polygon([(x - 62, GROUND - hh), (x, GROUND - hh - 60), (x + 62, GROUND - hh)], fill=(100, 100, 110))
            if (k + int(gt * 2)) % 3:
                d.rectangle([x - 20, GROUND - hh + 30, x + 20, GROUND - hh + 64], fill=(250, 220, 140))
        outlined(d, (540, 460), "40 ЧЕЛОВЕК", 110, WHITE)
        outlined(d, (540, 590), "ДУМАЮТ, ЧТО ЕСТЬ ГОД", 50, YEL)
        return
    if sc in ("car_arrive", "plate"):
        d = field(img, gt)
        night_overlay(img, 140)
        d = ImageDraw.Draw(img)
        cx = lerp(1500, 420, ease_out(clamp(lt / 1.6))) if sc == "car_arrive" else 420
        draw_car(d, cx, gt)
        flashlight(img, cx - 194, GROUND - 82, -1, a=90, spread=80, length=500)
        d = ImageDraw.Draw(img)
        draw_gena(d, 820, GROUND + 4, 1.2, gt, boots=False, face=-1)
        R.draw_hero(d, 940, GROUND + 4, 1.2, gt, face=-1)
        if sc == "plate":
            s = back_out(lt / 0.4)
            d.rounded_rectangle([540 - 280 * s, 520 - 90 * s, 540 + 280 * s, 520 + 90 * s], radius=14,
                                fill=WHITE, outline=(20, 20, 20), width=8)
            d.text((540, 520), "А 666 АА 66", font=font(int(84 * s) + 1), fill=(20, 20, 20), anchor="mm")
        return
    if sc.startswith("choice"):
        foc = {"choice_l": 0, "choice_r": 1, "choice_r2": 1}.get(sc)
        d = field(img, gt)
        R.draw_choice(img, lt if sc == "choice" else 5.0, gt, focus=foc, vote=sc.startswith("choice_vote"))
        d = ImageDraw.Draw(img)
        if sc == "choice_r2":
            R.draw_stamp(img, "ВСЕГО 2 МЕСЯЦА", lt - 0.3, cy=960)
        if sc == "choice_vote2":
            draw_car(d, 160, gt)
            s = back_out(lt / 0.5)
            d.text((640, 960), "СЕРИЯ 4 — ВЫБИРАЕТЕ ВЫ", font=font(int(44 * s) + 1), fill=YEL, anchor="mm")
        return
    raise KeyError(sc)


R.render_scene = render_scene


def sfx_events(add, S, L, nxt, fx):
    add(S("prev_rob"), fx["whoosh"](0.8)); add(S("prev_rob") + 1.8, fx["pop"]())
    add(S("votes"), fx["whoosh"](1.2)); add(S("votes") + 1.3, fx["thud"]())
    add(S("gena_money") + 0.8, fx["pop"]()); add(S("gena_cash"), fx["cash"]()); add(S("gena_cash") + 0.3, fx["cash"]())
    add(S("gena_deal") + 1.3, fx["pop"]()); add(S("napkin") + 0.8, fx["whoosh"](0.4))
    for nm in ("door_tag", "vent_tag", "food_tag"): add(S(nm), fx["pop"]())
    add(S("door") + 0.6, fx["thud"]()); add(S("door"), fx["cash"]())
    add(S("vent") + 0.6, fx["whoosh"](1.5)); add(S("vent"), fx["cash"]())
    add(S("food") + 0.6, fx["pop"]()); add(S("food"), fx["cash"]())
    add(S("weird"), fx["boom"]() * 0.3)
    add(S("boots_again") + 0.8, fx["thud"]())
    add(S("cam_install"), fx["pop"]())
    add(S("cam2"), fx["rain"](L("cam2") + L("cam2_bag") + 1.0) * 0.4)
    add(S("cam2_bag") + 1.0, fx["thud"]())
    add(S("confront"), fx["thud"]()); add(S("pour_bag"), fx["whoosh"](0.8))
    add(S("reveal") + 0.5, fx["thud"]()); add(S("confess") + 1.0, fx["boom"]() * 0.5)
    add(S("flash_car"), fx["motor"](L("flash_car") + 0.4) * 0.8)
    add(S("math") + 1.0, fx["pop"]()); add(S("math") + 2.0, fx["cash"]())
    add(S("id_card"), fx["pop"]()); add(S("board_lie") + 0.3, fx["thud"]())
    add(S("sixty"), fx["boom"]())
    add(S("village"), fx["whoosh"](1.0))
    add(S("car_arrive"), fx["motor"](L("car_arrive") + 0.5))
    add(S("plate"), fx["thud"]())
    add(S("choice"), fx["whoosh"](0.5)); add(S("choice") + 0.15, fx["whoosh"](0.5)); add(S("choice") + 0.5, fx["pop"]())
    add(S("choice_l"), fx["pop"]()); add(S("choice_r"), fx["pop"]()); add(S("choice_r2") + 0.3, fx["thud"]())


if __name__ == "__main__":
    R.main()
