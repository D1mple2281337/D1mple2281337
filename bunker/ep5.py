#!/usr/bin/env python3
"""Бункер за 25 000 $ — серия 5 (зрители выбрали БАНК).

Банк вскрывает дверь. Поворот: банкир Аркадий — сын дяди Гены, Маша — его дочь.
В бункер на двоих заселяются 7 банкиров с пианино; «место» героя — будка охраны снаружи.
Маша приносит чай: под школой советское убежище на 300 человек. Через вентиляцию герой
слышит: военные завтра заберут школу, охранника выкинут. Аркадий даёт карту: «проведёшь —
получишь место». На обороте рисунка Маши — записка Гены: «фильтр открывается снаружи».
Финал: ПРОВЕСТИ или ПРЕДУПРЕДИТЬ + колонна уже едет, до 6 утра 7 часов.

  python3 ep5.py --timings timings_ep5.json --audio audio/mix_ep5_norm.wav --out out/bunker_ep5.mp4
"""
import math, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import ep4
from ep2 import draw_gena, bubble, draw_house, PX0, PX1, PD
from ep3 import draw_bunker_plus, draw_car, interior, night_overlay, flashlight, field, outlined, STEEL
from ep4 import (draw_suit, draw_soldier, draw_kid, draw_valya, draw_truck, draw_keypad, meteor, shake,
                 tinted_prev, SUIT)
from render import (W, H, GROUND, font, lerp, lc, clamp, ease_io, ease_out, back_out,
                    WHITE, GREY, YEL, RED, GREEN, BLUE)

EP4_SCENE = R.render_scene
R.INIT = (50.0, 0.0, 400.0)
R.EP_LABEL = "СЕРИЯ 5"
R.END_LINES = ("ПРОВЕСТИ или ПРЕДУПРЕДИТЬ?", "ПИШИ В КОММЕНТАРИЯХ")
R.CHOICE_CARDS = [("ПРОВЕСТИ", "lead", RED, 280, "МЕСТО ВНИЗУ?", "300 ЧЕЛ. НАВЕРХУ"),
                  ("ПРЕДУПРЕДИТЬ", "warn", GREEN, 800, "ШКОЛА СПАСЕНА?", "ВОЙНА С БАНКОМ")]
MASHA = dict(col=(230, 200, 60), hair=(200, 120, 50))

S_ = dict
R.SEGMENTS[:] = [
    S_(cap="В прошлой серии дядя Гена !запер меня снаружи!. С ним — внучка Маша.", scene="prev_lock"),
    S_(cap="А банкир предложил сделку: дверь вскроют, но бункер — !банку!.", scene="prev_deal"),
    S_(cap="Вы выбрали *банк*.", scene="votes"),
    S_(cap="Я подписываю договор прямо на капоте. В свете фар.", scene="sign"),
    S_(cap="Мелкий шрифт я не читаю. !Зря!.", scene="fine"),
    S_(cap="Через час приезжают люди банка. С *плазменным резаком*.", scene="team"),
    S_(cap="Сталь, как на подводной лодке, режут за !двадцать минут!.", scene="cut"),
    S_(cap="Дверь !падает!.", scene="door_fall"),
    S_(cap="Из бункера поднимается дядя Гена. За руку он держит *Машу*.", scene="gena_out"),
    S_(cap="Он смотрит не на меня. Он смотрит !на банкира!.", scene="gena_look"),
    S_(cap="— Здравствуй, *Аркаша*.", scene="hello"),
    S_(cap="Банкир бледнеет. — !Папа!?", scene="papa"),
    S_(cap="Банкир — !сын дяди Гены!.", scene="son"),
    S_(cap="Тот, кто восемь лет не звонил. Вот откуда Гена знал про !схему банка!.", scene="son2"),
    S_(cap="— Маша остаётся, — говорит банкир. — Она !моя дочь!.", scene="mine"),
    S_(cap="Маша прячется за дедушку: — Я тебя !не знаю!.", scene="masha_no"),
    S_(cap="Дядя Гена берёт её на руки и уходит в темноту. !Не оглядываясь!.", scene="go_away"),
    S_(cap="Только на секунду останавливается возле меня: — Ты сделал выбор. *Я когда-то тоже*.", scene="gena_words"),
    S_(cap="А потом подъезжает колонна. *Три чёрных джипа*.", scene="convoy"),
    S_(cap="Директор банка. Его жена. Охрана. *Собака*.", scene="who"),
    S_(cap="И — я не шучу — !пианино!.", scene="piano"),
    S_(cap="Семь человек. В бункер !на двоих!.", scene="seven"),
    S_(cap="Наши консервы летят на траву. — Мы такое !не едим!.", scene="cans"),
    S_(cap="— А где *моё место*? — спрашиваю я.", scene="where"),
    S_(cap="Аркадий молча показывает пункт двенадцать. !Мелким шрифтом!.", scene="print"),
    S_(cap="Моё место — !будка охранника!. Снаружи. У двери.", scene="booth"),
    S_(cap="Мне выдают фонарик, форму и *код от двери* — чтобы открывать хозяевам.", scene="code"),
    S_(cap="Зарплата — банка тушёнки в день. Из тех, что они !выкинули!.", scene="salary"),
    S_(cap="Дни идут.", scene="montage", days=42),
    S_(cap="С неба сыплется !пепел!. Каждую ночь падают осколки.", scene="ash"),
    S_(cap="Земля дрожит. А внизу играют на !пианино!.", scene="rumble"),
    S_(cap="На восьмую ночь у забора !кто-то стоит!.", scene="night_m"),
    S_(cap="Это *Маша*. С термосом.", scene="masha_fence"),
    S_(cap="— Это от тёти Вали. Дедушка сказал, ты *замёрзнешь*.", scene="masha_tea"),
    S_(cap="Она шепчет: под школой дедушка нашёл старое убежище. Советское. На !300 человек!.", scene="school"),
    S_(cap="Весь посёлок его откапывает. По ночам. *Тайком*.", scene="dig"),
    S_(cap="Маша суёт мне рисунок и убегает.", scene="drawing"),
    S_(cap="На рисунке — бункер. И много человечков. Один из них — *в моей кепке*.", scene="drawing2"),
    S_(cap="Ночью я слышу голоса. Из вентиляционной трубы. Той самой, что *я строил*.", scene="vent"),
    S_(cap="— Военные завтра забирают убежище под школой. Для !руководства области!.", scene="vent1"),
    S_(cap="— А людей? — !Наружу!. Список согласован.", scene="vent2"),
    S_(cap="— А охранник? — Охранник нам больше !не нужен!. Пусть идёт со всеми.", scene="vent3"),
    S_(cap="Через минуту люк открывается. Выходит *Аркадий*.", scene="hatch"),
    S_(cap="— Завтра в !шесть утра! проведёшь военных ко входу в школу. Ты знаешь, где он.", scene="map"),
    S_(cap="— Сделаешь — получишь место внутри. Настоящее. *Слово банка*.", scene="promise"),
    S_(cap="Пять минут назад я слышал, !чего стоит слово банка!.", scene="worth"),
    S_(cap="В одной руке — *карта*. В другой — *рисунок Маши*.", scene="hands"),
    S_(cap="Я переворачиваю рисунок. На обороте — !почерк дяди Гены!.", scene="flip"),
    S_(cap="«Вентиляцию строил ты. !Фильтр открывается снаружи!. Ты знаешь, что делать.»", scene="note"),
    S_(cap="Два пути. И на раздумья — !одна ночь!.", scene="choice", tag="ВЫБОР"),
    S_(cap="Первый: *провести военных*. Может, банкир не врёт — и я выживу внизу.", scene="choice_l", tag="ВЫБОР"),
    S_(cap="Но !300 человек! окажутся наверху. Среди них — Маша.", scene="choice_l2", tag="ВЫБОР"),
    S_(cap="Второй: *предупредить школу*. И пойти против банка, военных и Аркадия.", scene="choice_r",
       tag="ВЫБОР"),
    S_(cap="А что будет, если !открыть фильтр снаружи!, — знаю только я.", scene="choice_r2", tag="ВЫБОР"),
    S_(cap="Пиши в комментариях: *провести* или *предупредить*.", scene="choice_vote", tag="ВЫБОР"),
    S_(cap="А пока я думаю… к посёлку уже едет !колонна!.", scene="sting"),
    S_(cap="До шести утра — !семь часов!.", scene="clock"),
    S_(cap="Следующая серия — *по вашему выбору*.", scene="choice_vote2", tag="ВЫБОР"),
]


# ---------- объекты ----------

def draw_arkady(d, x, y, s=1.0, t=0.0, face=1, pale=False, walk=False):
    draw_suit(d, x, y, s, t, face=face, smile=not pale, walk=walk, glasses=False)
    hy = y - 70 * s - 124 * s
    if pale:
        d.ellipse([x - 26 * s, hy - 28 * s, x + 26 * s, hy + 28 * s], fill=(238, 226, 212))
        d.chord([x - 27 * s, hy - 30 * s, x + 27 * s, hy], 180, 360, fill=(30, 26, 24))
        d.ellipse([x + 8 * s * face - 5 * s, hy - 1 * s, x + 8 * s * face + 5 * s, hy + 9 * s], fill=WHITE,
                  outline=(30, 30, 30), width=2)
        d.ellipse([x + 8 * s * face - 2 * s, hy + 2 * s, x + 8 * s * face + 2 * s, hy + 6 * s], fill=(30, 30, 30))
        d.ellipse([x + 4 * s * face - 5 * s, hy + 14 * s, x + 4 * s * face + 5 * s, hy + 22 * s], fill=(90, 40, 40))
    else:
        d.ellipse([x + 8 * s * face - 4 * s, hy, x + 8 * s * face + 4 * s, hy + 8 * s], fill=(30, 30, 30))
    # отцовские усы — намёк на родство
    d.chord([x - 8 * s + 8 * s * face, hy + 10 * s, x + 20 * s + 8 * s * face, hy + 22 * s], 180, 360, fill=(30, 26, 24))


def draw_booth(d, x, light=True):
    y = GROUND
    d.rectangle([x - 90, y - 240, x + 90, y], fill=(200, 196, 186))
    d.rectangle([x - 104, y - 262, x + 104, y - 236], fill=(90, 96, 104))
    d.rectangle([x - 60, y - 200, x + 60, y - 120], fill=(250, 220, 140) if light else (60, 70, 90))
    d.text((x, y - 60), "ОХРАНА", font=font(30), fill=(40, 40, 50), anchor="mm")


def draw_piano(d, x, y, s=1.0):
    d.rectangle([x - 110 * s, y - 160 * s, x + 110 * s, y], fill=(20, 18, 20))
    d.rectangle([x - 100 * s, y - 100 * s, x + 100 * s, y - 70 * s], fill=WHITE)
    for k in range(9):
        d.rectangle([x - 92 * s + k * 22 * s, y - 100 * s, x - 84 * s + k * 22 * s, y - 84 * s], fill=(20, 18, 20))
    d.rectangle([x - 100 * s, y - 20 * s, x - 86 * s, y], fill=(40, 36, 40))
    d.rectangle([x + 86 * s, y - 20 * s, x + 100 * s, y], fill=(40, 36, 40))


def draw_dog(d, x, y, s=1.0):
    d.ellipse([x - 40 * s, y - 50 * s, x + 30 * s, y - 14 * s], fill=(240, 236, 230))
    d.ellipse([x + 16 * s, y - 74 * s, x + 54 * s, y - 40 * s], fill=(240, 236, 230))
    d.ellipse([x + 40 * s, y - 62 * s, x + 48 * s, y - 54 * s], fill=(20, 20, 20))
    for lx in (x - 30 * s, x + 16 * s):
        d.line([(lx, y - 20 * s), (lx, y)], fill=(240, 236, 230), width=int(8 * s))
    d.ellipse([x + 14 * s, y - 80 * s, x + 30 * s, y - 60 * s], fill=(230, 120, 160))   # бантик


def draw_school(d, x, glow=True, t=0.0):
    y = GROUND
    d.rectangle([x - 320, y - 300, x + 320, y], fill=(176, 120, 90))
    d.rectangle([x - 330, y - 320, x + 330, y - 296], fill=(100, 100, 110))
    d.text((x, y - 260), "ШКОЛА", font=font(40), fill=WHITE, anchor="mm")
    for r_ in range(2):
        for c_ in range(6):
            wx = x - 270 + c_ * 108; wy = y - 220 + r_ * 100
            on = glow and ((c_ + r_ + int(t * 2)) % 3 != 0)
            d.rectangle([wx - 26, wy - 30, wx + 26, wy + 30], fill=(250, 220, 140) if on else (50, 56, 70))
    d.rectangle([x - 40, y - 120, x + 40, y], fill=(70, 50, 40))


def draw_paper(d, cx, cy, s, back=False, t=0.0):
    d.rectangle([cx - 300 * s, cy - 220 * s, cx + 300 * s, cy + 220 * s], fill=(250, 248, 240))
    if not back:
        # детский рисунок: бункер и человечки
        d.rectangle([cx - 220 * s, cy + 20 * s, cx + 220 * s, cy + 170 * s], outline=(80, 80, 90), width=int(6 * s) + 1)
        d.line([(cx - 260 * s, cy + 20 * s), (cx + 260 * s, cy + 20 * s)], fill=(60, 160, 70), width=int(8 * s) + 1)
        d.ellipse([cx + 180 * s, cy - 200 * s, cx + 260 * s, cy - 120 * s], fill=(250, 200, 50))
        cols = [(230, 90, 110), (80, 150, 220), (200, 120, 50), (120, 128, 66), (150, 70, 110), (90, 90, 90)]
        for k in range(6):
            x = cx - 180 * s + k * 72 * s; y = cy + 150 * s
            d.ellipse([x - 14 * s, y - 100 * s, x + 14 * s, y - 72 * s], outline=cols[k], width=int(5 * s) + 1)
            d.line([(x, y - 72 * s), (x, y - 30 * s)], fill=cols[k], width=int(5 * s) + 1)
            d.line([(x, y - 30 * s), (x - 14 * s, y)], fill=cols[k], width=int(5 * s) + 1)
            d.line([(x, y - 30 * s), (x + 14 * s, y)], fill=cols[k], width=int(5 * s) + 1)
            d.line([(x - 20 * s, y - 60 * s), (x + 20 * s, y - 60 * s)], fill=cols[k], width=int(5 * s) + 1)
            if k == 3:   # кепка героя
                d.chord([x - 18 * s, y - 112 * s, x + 18 * s, y - 84 * s], 180, 360, fill=(200, 80, 40))
                d.rectangle([x, y - 94 * s, x + 26 * s, y - 88 * s], fill=(200, 80, 40))
        d.text((cx - 120 * s, cy - 150 * s), "БУНКЕР ДЛЯ ВСЕХ", font=font(int(34 * s) + 1), fill=(60, 80, 200), anchor="mm")
    else:
        lines = ["Вентиляцию строил ты.", "Фильтр открывается", "СНАРУЖИ.", "Ты знаешь, что делать.", "— Г."]
        for k, ln in enumerate(lines):
            d.text((cx - 260 * s, cy - 160 * s + k * 78 * s), ln, font=font(int(42 * s) + 1, True),
                   fill=(40, 50, 140) if k != 2 else (190, 40, 40), anchor="lm")


def draw_vent_pipe(d, x, t, talk=True):
    d.rectangle([x - 14, GROUND - 120, x + 14, GROUND + 30], fill=(150, 150, 160))
    d.chord([x - 40, GROUND - 150, x + 40, GROUND - 96], 180, 360, fill=(150, 150, 160))
    if talk:
        for k in range(3):
            r = 30 + k * 34 + (t * 70) % 34
            d.arc([x - r, GROUND - 150 - r, x + r, GROUND - 150 + r], 200, 340, fill=(220, 220, 240), width=5)


def icon_lead(d, cx, cy, s):
    d.chord([cx - 90 * s, cy - 110 * s, cx + 30 * s, cy - 10 * s], 180, 360, fill=(70, 90, 50))
    d.ellipse([cx - 70 * s, cy - 60 * s, cx + 10 * s, cy + 20 * s], fill=(226, 186, 150))
    d.rectangle([cx - 80 * s, cy + 20 * s, cx + 20 * s, cy + 90 * s], fill=(70, 90, 50))
    d.polygon([(cx + 40 * s, cy - 10 * s), (cx + 110 * s, cy - 10 * s), (cx + 110 * s, cy - 40 * s), (cx + 160 * s, cy + 10 * s),
               (cx + 110 * s, cy + 60 * s), (cx + 110 * s, cy + 30 * s), (cx + 40 * s, cy + 30 * s)], fill=RED)


def icon_warn(d, cx, cy, s):
    d.rectangle([cx - 140 * s, cy - 40 * s, cx + 140 * s, cy + 90 * s], fill=(176, 120, 90))
    d.polygon([(cx - 150 * s, cy - 40 * s), (cx, cy - 110 * s), (cx + 150 * s, cy - 40 * s)], fill=(100, 100, 110))
    for k in range(4):
        d.rectangle([cx - 110 * s + k * 62 * s, cy - 10 * s, cx - 76 * s + k * 62 * s, cy + 30 * s], fill=(250, 220, 140))
    d.ellipse([cx + 70 * s, cy - 150 * s, cx + 170 * s, cy - 50 * s], fill=YEL)
    d.text((cx + 120 * s, cy - 100 * s), "!", font=font(int(70 * s) + 1), fill=(30, 20, 20), anchor="mm")


R.ICONS["lead"] = icon_lead
R.ICONS["warn"] = icon_warn


def booth_scene(img, gt, red=0.4, night=True, ash=False):
    d = field(img, gt, red=red)
    draw_booth(d, 900)
    if ash:
        for k in range(60):
            x = (k * 97 + gt * 30) % W; y = (k * 53 + gt * 60 * (1 + k % 3)) % GROUND
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(170, 170, 176))
    if night:
        night_overlay(img, 120)
    return ImageDraw.Draw(img)


def door_area(img, gt, red=0.2):
    d = field(img, gt, red=red)
    night_overlay(img, 110)
    d = ImageDraw.Draw(img)
    draw_car(d, 120, gt)
    return d


# ---------- сцены ----------

def render_scene(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    dur = seg["dur"]

    if sc in ("prev_lock", "prev_deal"):
        EP4_SCENE(img, dict(seg, scene="masha" if sc == "prev_lock" else "deal"), i, lt + 0.5, p, gt, st)
        tinted_prev(img, gt)
        return
    if sc == "votes":
        d = field(img, gt, red=0.5)
        k = ease_out(clamp((lt - 0.1) / 0.9))
        for j, (lab, val, col) in enumerate([("БАНК", 54, RED), ("СОСЕДИ", 46, GREEN)]):
            y = 470 + j * 190
            d.text((90, y - 60), lab, font=font(52), fill=col, anchor="lm")
            d.rounded_rectangle([90, y - 20, 990, y + 60], radius=20, fill=(30, 34, 52))
            wv = 900 * val / 100 * k
            if wv > 30: d.rounded_rectangle([90, y - 20, 90 + wv, y + 60], radius=20, fill=col)
            d.text((990, y - 60), f"{int(val * k)} %", font=font(52), fill=WHITE, anchor="rm")
        if lt > 0.9:
            R.draw_stamp(img, "СДЕЛКА", lt - 0.9, cy=880)
        return

    # --- договор и вскрытие ---
    if sc in ("sign", "fine"):
        d = door_area(img, gt, red=0.6)
        flashlight(img, 120 + 14 - 200 + 200, GROUND - 82, 1, a=80, spread=80, length=700)
        d = ImageDraw.Draw(img)
        draw_arkady(d, 380, GROUND + 4, 1.25, gt, face=1)
        R.draw_hero(d, 620, GROUND + 4, 1.25, gt, face=-1)
        s = back_out(lt / 0.4)
        cx, cy = 540, 520
        d.rectangle([cx - 260 * s, cy - 230 * s, cx + 260 * s, cy + 230 * s], fill=(246, 244, 236))
        d.text((cx, cy - 180 * s), "ДОГОВОР", font=font(int(50 * s) + 1), fill=(30, 30, 40), anchor="mm")
        for k in range(6):
            yy = cy - 110 * s + k * 34 * s
            d.line([(cx - 210 * s, yy), (cx + 210 * s, yy)], fill=(170, 170, 180), width=5)
        for k in range(5):
            yy = cy + 100 * s + k * 14 * s
            d.line([(cx - 210 * s, yy), (cx + 120 * s, yy)], fill=(200, 200, 206), width=2)
        if sc == "sign" and lt > 1.0:
            d.line([(cx + 40, cy + 190), (cx + 90, cy + 160), (cx + 130, cy + 200), (cx + 200, cy + 165)],
                   fill=(40, 60, 160), width=6)
        if sc == "fine":
            d.line([(cx + 40, cy + 190), (cx + 90, cy + 160), (cx + 130, cy + 200), (cx + 200, cy + 165)],
                   fill=(40, 60, 160), width=6)
            d.ellipse([cx - 260, cy + 40, cx - 20, cy + 280], outline=YEL, width=10)
            d.line([(cx - 50, cy + 250), (cx + 30, cy + 330)], fill=YEL, width=18)
            d.text((cx - 140, cy + 160), "п.12 …", font=font(36, True), fill=(90, 90, 100), anchor="mm")
            R.draw_stamp(img, "НЕ ЧИТАЛ", lt - 0.8, cy=300)
        return
    if sc in ("team", "cut", "door_fall"):
        d = door_area(img, gt, red=0.3)
        draw_truck(d, -60)
        draw_suit(d, 560, GROUND + 4, 1.2, gt, smile=False)
        draw_suit(d, 760, GROUND + 4, 1.2, gt, face=-1, smile=False)
        R.draw_hero(d, 960, GROUND + 4, 1.2, gt, face=-1)
        if sc in ("cut", "team") and (sc == "cut" or lt > 1.2):
            prog = clamp(lt / max(0.5, dur)) if sc == "cut" else 0
            a0 = 0
            for k in range(int(36 * prog)):
                a = k / 36 * 2 * math.pi
                d.ellipse([650 + math.cos(a) * 40 - 5, GROUND - 13 + math.sin(a) * 10 - 5,
                           650 + math.cos(a) * 40 + 5, GROUND - 13 + math.sin(a) * 10 + 5], fill=(255, 140, 40))
            for k in range(16):
                a = gt * 10 + k
                x = 650 + math.cos(a) * (20 + (k * 13) % 70); y = GROUND - 30 - abs(math.sin(a)) * (30 + (k * 17) % 90)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 220, 80))
            if sc == "cut":
                outlined(d, (540, 450), f"{int(20 * prog)} МИН", 120, YEL)
        if sc == "door_fall":
            k = ease_io(clamp(lt / 0.5))
            d.ellipse([600 + 140 * k, GROUND - 26 - 10 * k, 700 + 140 * k, GROUND + 10 * k], fill=STEEL)
            outlined(d, (540, 450), "БАМ!", 150, WHITE)
            shake(img, 10 * (1 - clamp(lt / 0.6)), gt)
        return

    # --- Гена, Маша, Аркадий ---
    if sc in ("gena_out", "gena_look", "hello", "papa", "son", "son2", "mine", "masha_no", "go_away",
              "gena_words"):
        d = door_area(img, gt, red=0.3)
        gy = GROUND + 4
        gx, mx = 640, 720
        if sc == "gena_out":
            gy = lerp(GROUND + 220, GROUND + 4, ease_out(clamp(lt / 1.3)))
        if sc == "go_away":
            k = ease_io(clamp((lt - 0.3) / 2.2))
            gx = lerp(640, 1250, k); mx = gx + 40
        if sc == "gena_words":
            gx, mx = 860, 900
        pale = sc in ("papa", "son", "son2")
        draw_arkady(d, 330, GROUND + 4, 1.3, gt, face=1, pale=pale)
        R.draw_hero(d, 960 if sc != "gena_words" else 760, GROUND + 4, 1.2, gt, face=-1)
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        draw_gena(td, gx, gy, 1.3, gt, boots=False, face=-1)
        if sc not in ("go_away", "gena_words"):
            draw_kid(td, mx, gy, 1.0, face=-1, **MASHA)
        else:
            draw_kid(td, gx + 20, gy - 110, 0.85, face=-1, **MASHA)   # на руках
        clip = tmp.crop((0, 0, W, GROUND + 6))
        img.paste(clip, (0, 0), clip)
        d = ImageDraw.Draw(img)
        if sc == "gena_look":
            d.line([(600, 640), (420, 700)], fill=YEL, width=8)
            d.polygon([(420, 680), (390, 708), (432, 718)], fill=YEL)
        if sc == "hello":
            bubble(d, 640, 430, "ЗДРАВСТВУЙ, АРКАША.", 46, tail=1)
        if sc == "papa":
            bubble(d, 330, 430, "ПАПА?!", 70, col=(20, 20, 26), tcol=WHITE, tail=-1)
        if sc == "son":
            R.draw_stamp(img, "БАНКИР — СЫН ГЕНЫ", lt - 0.3, cy=450)
        if sc == "son2":
            outlined(d, (540, 430), "8 ЛЕТ", 150, RED)
            outlined(d, (540, 560), "НИ ОДНОГО ЗВОНКА", 56, WHITE)
        if sc == "mine":
            bubble(d, 330, 430, "ОНА МОЯ ДОЧЬ", 52, col=(20, 20, 26), tcol=WHITE, tail=-1)
        if sc == "masha_no":
            bubble(d, 720, 450, "Я ТЕБЯ НЕ ЗНАЮ", 46, col=(255, 230, 120), tail=1)
        if sc == "gena_words":
            bubble(d, 800, 420, "ТЫ СДЕЛАЛ ВЫБОР.", 42, tail=1)
            bubble(d, 800, 530, "Я КОГДА-ТО ТОЖЕ.", 42, tail=1)
        return

    # --- банкиры заселяются ---
    if sc in ("convoy", "who", "piano", "seven", "cans", "where", "print", "booth", "code", "salary"):
        d = field(img, gt, red=0.3)
        night_overlay(img, 90)
        d = ImageDraw.Draw(img)
        k = ease_out(clamp(lt / 1.8)) if sc == "convoy" else 1
        for j in range(3):
            draw_car(d, lerp(-600 - j * 450, 150 - j * 0, k) if j == 0 else lerp(-1000 - j * 450, -330 - (j - 1) * 470, k), gt)
        if sc in ("booth", "code", "salary"):
            draw_booth(d, 900)
        if sc not in ("convoy",):
            cast = [(470, "suit"), (560, "wife"), (650, "guard"), (740, "guard")]
            for x, kind in cast:
                if kind == "wife":
                    draw_valya(d, x, GROUND + 4, 1.1)   # силуэт в шубе — перекрашен ниже
                    d.polygon([(x - 44, GROUND + 4), (x + 44, GROUND + 4), (x + 30, GROUND - 140), (x - 30, GROUND - 140)],
                              fill=(120, 90, 70))
                else:
                    draw_suit(d, x, GROUND + 4, 1.1, gt, smile=kind == "suit")
            draw_dog(d, 830, GROUND + 4, 1.0)
        if sc in ("piano", "seven", "cans"):
            draw_piano(d, 340, GROUND + 4, 1.0)
        if sc == "piano":
            outlined(d, (540, 430), "ПИАНИНО", 120, YEL)
        if sc == "seven":
            outlined(d, (540, 400), "7 ЧЕЛОВЕК", 110, RED)
            outlined(d, (540, 520), "МЕСТ: 2", 80, WHITE)
        if sc == "cans":
            for j in range(8):
                ft = clamp((lt - j * 0.15) / 0.8)
                x = lerp(650, 120 + j * 60, ease_out(ft)); y = GROUND - 80 - math.sin(ft * math.pi) * 260
                d.rectangle([x - 16, y - 22, x + 16, y + 22], fill=[(200, 60, 50), (220, 180, 50), (80, 140, 200)][j % 3])
            bubble(d, 470, 420, "МЫ ТАКОЕ НЕ ЕДИМ", 42, col=(20, 20, 26), tcol=WHITE, tail=-1)
        if sc in ("where", "print", "booth", "code", "salary"):
            R.draw_hero(d, 1000 if sc not in ("booth", "code", "salary") else 900, GROUND + 4, 1.15, gt, face=-1)
        if sc == "where":
            bubble(d, 900, 440, "А ГДЕ МОЁ МЕСТО?", 42, tail=1)
        if sc == "print":
            s = back_out(lt / 0.4)
            d.rectangle([540 - 330 * s, 500 - 150 * s, 540 + 330 * s, 500 + 150 * s], fill=(246, 244, 236))
            d.text((540, 430), "п. 12", font=font(int(40 * s) + 1), fill=(90, 90, 100), anchor="mm")
            d.text((540, 500), "МЕСТО: ПОСТ ОХРАНЫ", font=font(int(46 * s) + 1), fill=(30, 30, 40), anchor="mm")
            d.text((540, 565), "(СНАРУЖИ)", font=font(int(54 * s) + 1), fill=RED, anchor="mm")
        if sc == "booth":
            R.draw_stamp(img, "СНАРУЖИ", lt - 0.5, cy=450)
        if sc == "code":
            draw_keypad(d, 540, 560, 0.8, status="ok", digits=6)
        if sc == "salary":
            d.rectangle([480, 380, 600, 540], fill=(200, 60, 50))
            d.rectangle([480, 420, 600, 500], fill=(240, 236, 226))
            d.text((540, 460), "ТУШЁНКА", font=font(24), fill=(60, 30, 30), anchor="mm")
            outlined(d, (540, 620), "1 БАНКА / ДЕНЬ", 60, YEL)
        return
    if sc in ("montage", "ash", "rumble"):
        d = booth_scene(img, gt, red=0.7, night=sc != "montage", ash=True)
        R.draw_hero(d, 900, GROUND + 4, 1.15, gt, face=-1)
        if sc == "montage":
            day = int(lerp(50, 42, ease_io(lt / max(0.5, dur))))
            outlined(d, (540, 450), f"ДЕНЬ {50 - day + 1}", 120, WHITE)
        if sc == "ash":
            for k in range(4):
                ft = (gt * 0.6 + k * 0.29) % 1.0
                meteor(d, 1100 - ft * 900, 120 + ft * 500, 12 + k * 4, gt)
        if sc == "rumble":
            shake(img, 5, gt)
            d = ImageDraw.Draw(img)
            for k in range(3):   # ноты из трубы
                ft = (gt * 0.7 + k / 3) % 1
                d.text((420 + ft * 60, GROUND - 160 - ft * 250), "♪", font=font(70), fill=lc(WHITE, (40, 40, 60), ft),
                       anchor="mm")
            draw_vent_pipe(d, 420, gt, talk=False)
        return
    if sc in ("night_m", "masha_fence", "masha_tea", "school", "dig", "drawing"):
        if sc in ("school", "dig"):
            d = R.draw_sky(img, gt, 0.6)
            R.draw_landscape(d); R.draw_ground(d)
            draw_school(d, 540, t=gt)
            if sc == "dig":
                for k in range(6):
                    x = 120 + k * 170
                    R.draw_hero(d, x, GROUND + 4, 0.8, gt + k, shovel=True, dig=gt * 1.5 + k * 0.3) if k == 2 else \
                        draw_kid(d, x, GROUND + 4, 1.2, col=[(150, 70, 110), (60, 120, 160), (200, 80, 40),
                                                              (120, 128, 66), (110, 70, 60), (90, 90, 96)][k])
                outlined(d, (540, 520), "ТАЙКОМ", 110, YEL)
            else:
                outlined(d, (540, 520), "300 МЕСТ", 120, GREEN)
                outlined(d, (540, 640), "СССР, 1987", 56, WHITE)
            night_overlay(img, 90)
            return
        d = booth_scene(img, gt, red=0.4)
        R.draw_hero(d, 760, GROUND + 4, 1.2, gt, face=-1)
        mx = 300 if sc != "night_m" else 200
        if sc == "drawing":
            mx = lerp(300, -100, ease_io(clamp((lt - 0.8) / 1.2)))
        draw_kid(d, mx, GROUND + 4, 1.15, face=1, **MASHA)
        if sc == "night_m":
            # только силуэт
            d.rectangle([150, GROUND - 170, 250, GROUND], fill=(14, 14, 18))
            outlined(d, (540, 450), "?", 200, WHITE)
        if sc in ("masha_fence", "masha_tea"):
            d.rounded_rectangle([mx + 20, GROUND - 120, mx + 50, GROUND - 50], radius=8, fill=(200, 60, 50))
            for k in range(3):
                d.line([(mx + 30 + k * 6, GROUND - 130 - k * 4), (mx + 30 + k * 6, GROUND - 150 - k * 4)], fill=(220, 220, 230), width=3)
        if sc == "masha_tea":
            bubble(d, 330, 450, "ДЕДУШКА СКАЗАЛ:", 38, col=(255, 230, 120), tail=-1)
            bubble(d, 330, 550, "ТЫ ЗАМЁРЗНЕШЬ", 38, col=(255, 230, 120), tail=-1)
        if sc == "drawing" and lt < 1.0:
            d.rectangle([mx + 30, GROUND - 130, mx + 90, GROUND - 90], fill=(250, 248, 240))
        return
    if sc in ("drawing2", "flip", "note", "hands"):
        d = booth_scene(img, gt, red=0.4)
        if sc == "hands":
            s = back_out(lt / 0.4)
            d.rectangle([250 - 180 * s, 560 - 150 * s, 250 + 180 * s, 560 + 150 * s], fill=(220, 210, 170))
            d.line([(150, 520), (250, 600), (350, 540)], fill=RED, width=6)
            d.text((250, 460), "КАРТА", font=font(int(40 * s) + 1), fill=(60, 50, 40), anchor="mm")
            draw_paper(d, 800, 560, 0.55 * s + 0.01)
            outlined(d, (540, 820), "ИЛИ", 80, WHITE)
            return
        if sc == "drawing2":
            draw_paper(d, 540, 560, back_out(lt / 0.4) + 0.01)
        elif sc == "flip":
            k = clamp(lt / 0.8)
            sx = abs(math.cos(k * math.pi))
            tmp = Image.new("RGB", (620, 460), (0, 0, 0))
            draw_paper(ImageDraw.Draw(tmp), 310, 230, 1.0, back=k > 0.5)
            tmp = tmp.resize((max(2, int(620 * sx)), 460))
            img.paste(tmp, (int(540 - tmp.width / 2), 330))
        else:
            draw_paper(d, 540, 560, 1.0, back=True)
            if lt > 1.5:
                R.draw_stamp(img, "ФИЛЬТР — СНАРУЖИ", lt - 1.5, cy=880)
        return
    if sc in ("vent", "vent1", "vent2", "vent3", "hatch", "map", "promise", "worth"):
        d = booth_scene(img, gt, red=0.4)
        draw_vent_pipe(d, 420, gt, talk=sc.startswith("vent"))
        R.draw_hero(d, 560 if sc.startswith("vent") else 820, GROUND + 4, 1.2, gt, face=-1)
        if sc == "vent1":
            bubble(d, 420, 430, "ШКОЛУ ЗАБИРАЮТ", 44, col=(20, 20, 26), tcol=WHITE, tail=-1)
            bubble(d, 420, 540, "ДЛЯ РУКОВОДСТВА", 44, col=(20, 20, 26), tcol=WHITE, tail=-1)
        if sc == "vent2":
            bubble(d, 420, 430, "А ЛЮДЕЙ?", 44, col=(20, 20, 26), tcol=WHITE, tail=-1)
            bubble(d, 420, 540, "НАРУЖУ.", 60, col=(20, 20, 26), tcol=RED, tail=-1)
        if sc == "vent3":
            bubble(d, 420, 430, "ОХРАННИК?", 44, col=(20, 20, 26), tcol=WHITE, tail=-1)
            bubble(d, 420, 540, "НЕ НУЖЕН.", 60, col=(20, 20, 26), tcol=RED, tail=-1)
        if sc in ("hatch", "map", "promise", "worth"):
            ay = lerp(GROUND + 200, GROUND + 4, ease_out(clamp(lt / 1.2))) if sc == "hatch" else GROUND + 4
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_arkady(ImageDraw.Draw(tmp), 650, ay, 1.25, gt, face=1)
            clip = tmp.crop((0, 0, W, GROUND + 6)); img.paste(clip, (0, 0), clip)
            d = ImageDraw.Draw(img)
        if sc == "map":
            s = back_out(lt / 0.4)
            d.rectangle([540 - 280 * s, 470 - 180 * s, 540 + 280 * s, 470 + 180 * s], fill=(220, 210, 170))
            d.line([(300, 560), (420, 470), (560, 520), (700, 400)], fill=RED, width=7)
            d.ellipse([680, 380, 720, 420], outline=RED, width=7)
            d.text((700, 350), "ШКОЛА", font=font(int(34 * s) + 1), fill=(60, 50, 40), anchor="mm")
            outlined(d, (540, 720), "06:00", 110, YEL)
        if sc == "promise":
            bubble(d, 650, 440, "СЛОВО БАНКА", 50, col=(20, 20, 26), tcol=WHITE, tail=1)
        if sc == "worth":
            R.draw_stamp(img, "ВРЁТ", lt - 0.3, cy=450)
        return
    if sc in ("sting", "clock"):
        d = R.draw_sky(img, gt, 0.6)
        R.draw_landscape(d); R.draw_ground(d)
        draw_school(d, 760, t=gt)
        night_overlay(img, 110)
        d = ImageDraw.Draw(img)
        if sc == "sting":
            k = ease_out(clamp(lt / max(0.5, dur)))
            for j in range(4):
                x = lerp(-300 - j * 330, 320 - j * 330, k)
                draw_truck(d, x, army=True)
                flashlight(img, x + 170, GROUND - 100, 1, a=70, spread=60, length=400)
                d = ImageDraw.Draw(img)
        else:
            cx, cy = 540, 520
            d.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(246, 244, 236), outline=(40, 40, 50), width=12)
            for k in range(12):
                a = k / 12 * 2 * math.pi
                d.line([(cx + math.sin(a) * 170, cy - math.cos(a) * 170), (cx + math.sin(a) * 186, cy - math.cos(a) * 186)],
                       fill=(40, 40, 50), width=6)
            ha = 11 / 12 * 2 * math.pi
            ma = (lt * 0.5) % 1 * 2 * math.pi
            d.line([(cx, cy), (cx + math.sin(ha) * 100, cy - math.cos(ha) * 100)], fill=(30, 30, 30), width=14)
            d.line([(cx, cy), (cx + math.sin(ma) * 160, cy - math.cos(ma) * 160)], fill=RED, width=8)
            outlined(d, (540, 820), "7 ЧАСОВ", 100, RED)
        return
    if sc.startswith("choice"):
        foc = {"choice_l": 0, "choice_l2": 0, "choice_r": 1, "choice_r2": 1}.get(sc)
        booth_scene(img, gt, red=0.5, night=False)
        R.draw_choice(img, lt if sc == "choice" else 5.0, gt, focus=foc, vote=sc.startswith("choice_vote"))
        d = ImageDraw.Draw(img)
        if sc == "choice_l2":
            R.draw_stamp(img, "МАША НАВЕРХУ", lt - 0.3, cy=960)
        if sc == "choice_r2":
            R.draw_stamp(img, "ФИЛЬТР?", lt - 0.3, col=(200, 120, 20), cy=960)
        if sc == "choice_vote2":
            s = back_out(lt / 0.5)
            d.text((540, 960), "СЕРИЯ 6 — ВЫБИРАЕТЕ ВЫ", font=font(int(44 * s) + 1), fill=YEL, anchor="mm")
        return
    raise KeyError(sc)


R.render_scene = render_scene


def sfx_events(add, S, L, nxt, fx):
    th, pp, ca, wh, bo, ra, mo = (fx[k] for k in ("thud", "pop", "cash", "whoosh", "boom", "rain", "motor"))
    add(S("prev_lock"), wh(0.8)); add(S("prev_deal"), wh(0.6))
    add(S("votes"), wh(1.0)); add(S("votes") + 0.9, th())
    add(S("sign") + 1.0, wh(0.3)); add(S("fine") + 0.8, th())
    add(S("team"), mo(L("team") + 0.4))
    add(S("cut"), ra(L("cut") + 0.3) * 1.6)
    add(S("door_fall"), bo() * 0.7); add(S("door_fall"), th())
    add(S("gena_out"), wh(1.0)); add(S("hello"), pp())
    add(S("papa"), bo() * 0.5); add(S("son") + 0.3, th()); add(S("son2"), wh(0.8))
    add(S("mine"), th()); add(S("masha_no"), pp()); add(S("go_away"), wh(2.0) * 0.4)
    add(S("convoy"), mo(L("convoy") + 0.5))
    add(S("who"), pp()); add(S("piano"), pp()); add(S("piano") + 0.2, ca())
    add(S("seven"), th()); add(S("cans"), wh(1.0))
    add(S("print"), pp()); add(S("booth") + 0.5, th()); add(S("code"), ca()); add(S("salary"), pp())
    add(S("montage"), wh(1.5)); add(S("ash"), wh(1.8))
    add(S("rumble"), bo() * 0.4)
    add(S("night_m"), th() * 0.6); add(S("masha_fence"), pp())
    add(S("school"), wh(1.0)); add(S("dig"), pp())
    add(S("drawing2"), pp())
    add(S("vent"), ra(L("vent") + L("vent1") + L("vent2") + L("vent3") + 1.5) * 0.3)
    add(S("vent2") + 0.5, th()); add(S("vent3") + 0.6, th())
    add(S("hatch"), wh(1.0)); add(S("map"), pp()); add(S("worth") + 0.3, th())
    add(S("flip"), wh(0.8)); add(S("note") + 1.5, bo() * 0.4)
    add(S("choice"), wh(0.5)); add(S("choice") + 0.15, wh(0.5)); add(S("choice") + 0.5, pp())
    add(S("choice_l"), pp()); add(S("choice_l2") + 0.3, th()); add(S("choice_r"), pp()); add(S("choice_r2") + 0.3, th())
    add(S("sting"), mo(L("sting") + L("clock") + 1.0))
    add(S("clock"), th())


if __name__ == "__main__":
    R.main()
