#!/usr/bin/env python3
"""Бункер за 25 000 $ — серия 4 (зрители выбрали МОЛЧАТЬ).

Машина 66 — коллекторы банка; банк знает про астероид и забирает бункеры должников.
Осколки падают раньше, правительство признаёт 57 дней, соседка с внуками просит пустить — герой врёт.
Банк пытается вскрыть бункер, приезжают военные. Резкий поворот: Гена меняет код и запирается
внутри со своей тайной внучкой. Герой снаружи: 50 дней, 400 $.
Финал: СДЕЛКА С БАНКОМ или СОСЕДИ.

  python3 ep4.py --timings timings_ep4.json --audio audio/mix_ep4_norm.wav --out out/bunker_ep4.mp4
"""
import math, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import ep3
from ep2 import draw_gena, bubble, draw_house, draw_shed, PX0, PX1, PD
from ep3 import (draw_bunker_plus, draw_car, interior, night_overlay, flashlight, field, outlined, STEEL)
from render import (W, H, GROUND, font, lerp, lc, clamp, ease_io, ease_out, back_out,
                    WHITE, GREY, YEL, RED, GREEN, BLUE)

EP3_SCENE = R.render_scene
R.INIT = (60.0, 88.0, 2600.0)
R.EP_LABEL = "СЕРИЯ 4"
R.END_LINES = ("БАНК или СОСЕДИ?", "ПИШИ В КОММЕНТАРИЯХ")
R.CHOICE_CARDS = [("БАНК", "bank", RED, 280, "ДВЕРЬ ВСКРОЮТ", "ГЕНУ — НАВЕРХ"),
                  ("СОСЕДИ", "village", GREEN, 800, "ВСЕ ВМЕСТЕ", "0 $ И 50 ДНЕЙ")]

S_ = dict
R.SEGMENTS[:] = [
    # --- повтор ---
    S_(cap="В прошлой серии дядя Гена признался: это он меня !ограбил! — чтобы спасти.", scene="prev_confess"),
    S_(cap="А потом сказал страшное: астероид прилетит через !60 дней!.", scene="prev_sixty"),
    S_(cap="Вы решили *молчать*. Никому ни слова.", scene="votes"),
    # --- банк ---
    S_(cap="Но сначала — !чёрная машина! у забора.", scene="car"),
    S_(cap="Из неё выходят двое. В костюмах. Улыбаются.", scene="suits_out"),
    S_(cap="— Добрый вечер. *Банк*. Отдел взыскания.", scene="suits_card"),
    S_(cap="— Так это вы мне звонили? С номера на !66!?", scene="suits_q"),
    S_(cap="— Мы. Хотели помочь. Вы отказались.", scene="suits_a"),
    S_(cap="— Ваше поле куплено на наши деньги. Это !залог!.", scene="collateral"),
    S_(cap="— Значит, и всё, что на нём стоит, — тоже !наше!.", scene="bunker_ours"),
    S_(cap="— У вас *7 дней*, чтобы освободить участок.", scene="seven"),
    S_(cap="Они уезжают. А дядя Гена смотрит им вслед и тихо говорит:", scene="leave"),
    S_(cap="— Они знают. Банк знает про !60 дней!.", scene="bank_knows"),
    S_(cap="— Поэтому кредиты раздавали всем подряд. Люди строят бункеры — а банк их !забирает!.", scene="scheme"),
    S_(cap="— Мы не первые. И !не последние!.", scene="map"),
    # --- подготовка ---
    S_(cap="План такой: меняем *код*. Теперь его знаем только мы двое.", scene="code"),
    S_(cap="На последние деньги — замки, решётки и солнечная панель. Минус *2 200 $*.", scene="locks",
       budget=400, delta=-2200, pct=95),
    S_(cap="Бункер готов на *95 %*.", scene="ready"),
    # --- осколки ---
    S_(cap="Ночь третьего дня.", scene="night3", days=57),
    S_(cap="Небо !загорается!.", scene="sky_fire"),
    S_(cap="Это не салют. Это !осколки астероида!. Они прилетели раньше.", scene="fragments"),
    S_(cap="Один падает прямо !за забором!.", scene="impact"),
    S_(cap="Воронка — три метра. Бункер — *цел*.", scene="crater"),
    S_(cap="Утром по всем каналам — !экстренное заявление!.", scene="tv"),
    S_(cap="Правительство признаёт: удар не через год. А через !57 дней!. Гена был прав — день в день.",
       scene="tv57"),
    S_(cap="Мы молчали зря. Теперь знают !все!.", scene="all_know"),
    S_(cap="В посёлке паника. Сорок человек — и !ни одного бункера!.", scene="panic"),
    # --- тётя Валя ---
    S_(cap="Ко мне стучится соседка. *Тётя Валя*, с внуками.", scene="valya"),
    S_(cap="— Сынок, у тебя же что-то строили в поле… !Пусти детей!.", scene="valya_ask"),
    S_(cap="Я смотрю на дядю Гену. Он !молчит!.", scene="gena_silent"),
    S_(cap="Еды — на двоих. Места — на двоих.", scene="two"),
    S_(cap="И я говорю: — Простите. Там просто !погреб!.", scene="lie"),
    S_(cap="Тётя Валя уходит. Внуки !оборачиваются!.", scene="kids_back"),
    # --- штурм ---
    S_(cap="Седьмой день. Возвращается !чёрная машина!. С ней — грузовик и экскаватор.", scene="return",
       days=53),
    S_(cap="Мы спускаемся в бункер и закрываем *гермодверь*.", scene="lock_in"),
    S_(cap="Сверху !скрежет!. Они пытаются её вскрыть.", scene="sparks"),
    S_(cap="Не выходит. Сталь — *как на подводной лодке*.", scene="holds"),
    S_(cap="Тогда экскаватор начинает копать. !Сбоку!.", scene="dig_side"),
    S_(cap="Ковш бьёт в бетон. Раз. !Второй!.", scene="hit"),
    S_(cap="И тут — !сирены!.", scene="sirens"),
    S_(cap="Это не полиция. Это *военные*.", scene="army"),
    S_(cap="Банковских выводят из машины. Экскаватор !глохнет!.", scene="arrest"),
    S_(cap="По громкоговорителю: всем, у кого есть укрытия, — !зарегистрироваться!.", scene="loud"),
    S_(cap="Укрытия будут !распределять!. Значит, и наш тоже.", scene="distribute"),
    S_(cap="Дядя Гена хлопает меня по плечу: — Не бойся. У меня есть *план*.", scene="plan"),
    # --- поворот ---
    S_(cap="Ночью я поднимаюсь наверх — набрать воды.", scene="water"),
    S_(cap="Возвращаюсь. Ввожу код.", scene="keypad", days=50),
    S_(cap="!ОШИБКА!.", scene="err1"),
    S_(cap="Ещё раз. !ОШИБКА!.", scene="err2"),
    S_(cap="В динамике — голос дяди Гены.", scene="intercom"),
    S_(cap="— Прости, сынок. Я !поменял код!.", scene="sorry", pct=0),
    S_(cap="— Тут со мной *Маша*. Моя внучка. Я привёз её ещё неделю назад.", scene="masha"),
    S_(cap="Те коробки, что он носил по ночам… там были !детские вещи!.", scene="boxes_flash"),
    S_(cap="— Еды на двоих. Места на двоих. А нас !трое!.", scene="three"),
    S_(cap="Я стою над своим бункером. Своим кредитом. !Своей ямой!.", scene="alone"),
    S_(cap="*50 дней*. *400 $*. И !никакого бункера!.", scene="nothing"),
    S_(cap="А со стороны дороги снова светят фары. !Чёрная машина!.", scene="car_again"),
    S_(cap="Из окна высовывается тот самый банкир: — Ну что? Теперь *поговорим*?", scene="banker"),
    S_(cap="— Мы вскроем дверь. Вы получите место. Но бункер — !банку!.", scene="deal"),
    # --- выбор ---
    S_(cap="Два варианта. И оба — !предательство!.", scene="choice", tag="ВЫБОР"),
    S_(cap="Первый: *сделка с банком*. Дверь вскроют — но Гену с внучкой !выставят наверх!.",
       scene="choice_l", tag="ВЫБОР"),
    S_(cap="Второй: пойти к *тёте Вале* и соседям. Признаться, что врал, и строить новый бункер — "
           "*вместе*. Без денег.", scene="choice_r", tag="ВЫБОР"),
    S_(cap="Но поверят ли они тому, кто !захлопнул перед ними дверь!?", scene="choice_r2", tag="ВЫБОР"),
    S_(cap="Пиши в комментариях: *банк* или *соседи*.", scene="choice_vote", tag="ВЫБОР"),
    S_(cap="Следующая серия — !по вашему выбору!.", scene="choice_vote2", tag="ВЫБОР"),
]

SUIT = (34, 36, 44)
ARMY = (70, 90, 50)


# ---------- персонажи и объекты ----------

def draw_suit(d, x, y, s=1.0, t=0.0, face=1, smile=True, walk=False, glasses=True):
    bob = abs(math.sin(t * 9)) * 5 * s if walk else 0
    leg = math.sin(t * 9) * 12 * s if walk else 0
    d.line([(x - 10 * s, y - 70 * s - bob), (x - 12 * s + leg, y)], fill=SUIT, width=int(16 * s))
    d.line([(x + 10 * s, y - 70 * s - bob), (x + 12 * s - leg, y)], fill=SUIT, width=int(16 * s))
    by = y - 70 * s - bob
    d.rounded_rectangle([x - 32 * s, by - 96 * s, x + 32 * s, by + 4 * s], radius=int(10 * s), fill=SUIT)
    d.polygon([(x - 12 * s, by - 96 * s), (x, by - 60 * s), (x + 12 * s, by - 96 * s)], fill=WHITE)
    d.polygon([(x - 5 * s, by - 88 * s), (x + 5 * s, by - 88 * s), (x + 3 * s, by - 50 * s), (x - 3 * s, by - 50 * s)],
              fill=(170, 30, 40))
    hy = by - 124 * s
    d.ellipse([x - 26 * s, hy - 28 * s, x + 26 * s, hy + 28 * s], fill=(232, 196, 164))
    d.chord([x - 27 * s, hy - 30 * s, x + 27 * s, hy], 180, 360, fill=(30, 26, 24))
    if glasses:
        d.rectangle([x - 20 * s + 8 * s * face, hy - 2 * s, x + 24 * s + 8 * s * face, hy + 10 * s], fill=(10, 10, 12))
    if smile:
        d.arc([x - 14 * s + 6 * s * face, hy + 6 * s, x + 18 * s + 6 * s * face, hy + 22 * s], 10, 170,
              fill=(120, 40, 40), width=int(4 * s))


def draw_soldier(d, x, y, s=1.0, t=0.0, face=1):
    d.line([(x - 10 * s, y - 70 * s), (x - 12 * s, y)], fill=ARMY, width=int(18 * s))
    d.line([(x + 10 * s, y - 70 * s), (x + 12 * s, y)], fill=ARMY, width=int(18 * s))
    by = y - 70 * s
    d.rounded_rectangle([x - 34 * s, by - 96 * s, x + 34 * s, by + 4 * s], radius=int(12 * s), fill=ARMY)
    hy = by - 124 * s
    d.ellipse([x - 26 * s, hy - 28 * s, x + 26 * s, hy + 28 * s], fill=(226, 186, 150))
    d.chord([x - 32 * s, hy - 40 * s, x + 32 * s, hy + 8 * s], 180, 360, fill=(60, 80, 44))
    d.ellipse([x + 8 * s * face - 4 * s, hy + 2 * s, x + 8 * s * face + 4 * s, hy + 10 * s], fill=(30, 30, 30))


def draw_kid(d, x, y, s=1.0, col=(230, 90, 110), face=1, hair=(110, 70, 40)):
    d.line([(x - 6 * s, y - 40 * s), (x - 7 * s, y)], fill=(60, 60, 90), width=int(10 * s))
    d.line([(x + 6 * s, y - 40 * s), (x + 7 * s, y)], fill=(60, 60, 90), width=int(10 * s))
    d.rounded_rectangle([x - 20 * s, y - 100 * s, x + 20 * s, y - 38 * s], radius=int(8 * s), fill=col)
    d.ellipse([x - 20 * s, y - 142 * s, x + 20 * s, y - 102 * s], fill=(240, 200, 170))
    d.chord([x - 21 * s, y - 146 * s, x + 21 * s, y - 116 * s], 180, 360, fill=hair)
    d.ellipse([x + 6 * s * face - 3 * s, y - 126 * s, x + 6 * s * face + 3 * s, y - 120 * s], fill=(30, 30, 30))


def draw_valya(d, x, y, s=1.0, face=1):
    d.polygon([(x - 40 * s, y), (x + 40 * s, y), (x + 28 * s, y - 110 * s), (x - 28 * s, y - 110 * s)],
              fill=(150, 70, 110))
    d.rounded_rectangle([x - 30 * s, y - 170 * s, x + 30 * s, y - 100 * s], radius=int(12 * s), fill=(150, 70, 110))
    hy = y - 196 * s
    d.ellipse([x - 25 * s, hy - 26 * s, x + 25 * s, hy + 26 * s], fill=(236, 194, 160))
    d.chord([x - 30 * s, hy - 34 * s, x + 30 * s, hy + 10 * s], 180, 360, fill=(220, 120, 60))   # платок
    d.polygon([(x - 30 * s, hy - 4 * s), (x - 40 * s, hy + 30 * s), (x - 20 * s, hy + 8 * s)], fill=(220, 120, 60))
    d.ellipse([x + 8 * s * face - 4 * s, hy, x + 8 * s * face + 4 * s, hy + 8 * s], fill=(30, 30, 30))


def draw_truck(d, x, army=False):
    y = GROUND
    col = ARMY if army else (200, 90, 40)
    d.rectangle([x - 220, y - 190, x + 60, y - 50], fill=col if army else (150, 150, 156))
    if army:
        d.chord([x - 220, y - 240, x + 60, y - 140], 180, 360, fill=(80, 100, 60))
        d.ellipse([x - 120, y - 150, x - 60, y - 90], outline=WHITE, width=5)
        d.text((x - 90, y - 120), "★", font=font(40), fill=WHITE, anchor="mm")
    d.rounded_rectangle([x + 60, y - 160, x + 170, y - 50], radius=14, fill=col)
    d.rectangle([x + 90, y - 145, x + 155, y - 100], fill=(150, 200, 230))
    for wx in (x - 160, x - 40, x + 120):
        d.ellipse([wx - 36, y - 72, wx + 36, y], fill=(20, 20, 24))
        d.ellipse([wx - 14, y - 50, wx + 14, y - 22], fill=(90, 90, 96))


def icon_bank(d, cx, cy, s):
    d.polygon([(cx - 140 * s, cy - 50 * s), (cx, cy - 120 * s), (cx + 140 * s, cy - 50 * s)], fill=(210, 206, 196))
    for k in range(5):
        x = cx - 110 * s + k * 55 * s
        d.rectangle([x - 12 * s, cy - 46 * s, x + 12 * s, cy + 60 * s], fill=(226, 222, 212))
    d.rectangle([cx - 150 * s, cy + 60 * s, cx + 150 * s, cy + 80 * s], fill=(180, 174, 164))
    d.text((cx, cy - 72 * s), "$", font=font(int(40 * s) + 1), fill=(170, 40, 40), anchor="mm")


def icon_village(d, cx, cy, s):
    for k, col in enumerate([(150, 70, 110), (120, 128, 66), (110, 70, 60), (60, 120, 160), (230, 90, 110)]):
        x = cx - 120 * s + k * 60 * s
        hh = 1 if k < 4 else 0.7
        d.rounded_rectangle([x - 22 * s, cy - 10 * s * hh, x + 22 * s, cy + 80 * s], radius=int(8 * s), fill=col)
        d.ellipse([x - 20 * s, cy - 54 * s * hh, x + 20 * s, cy - 14 * s * hh], fill=(236, 194, 160))
    d.line([(cx + 120 * s, cy - 90 * s), (cx + 150 * s, cy + 40 * s)], fill=(140, 100, 60), width=int(8 * s))
    d.polygon([(cx + 140 * s, cy + 30 * s), (cx + 170 * s, cy + 24 * s), (cx + 172 * s, cy + 70 * s),
               (cx + 150 * s, cy + 74 * s)], fill=(170, 175, 185))


R.ICONS["bank"] = icon_bank
R.ICONS["village"] = icon_village


def draw_keypad(d, cx, cy, s, status=None, digits=0):
    d.rounded_rectangle([cx - 170 * s, cy - 260 * s, cx + 170 * s, cy + 260 * s], radius=int(22 * s), fill=(40, 42, 50),
                        outline=(120, 120, 130), width=int(6 * s))
    col = {None: (30, 60, 40), "ok": (40, 160, 80), "err": (200, 40, 40)}[status]
    d.rectangle([cx - 130 * s, cy - 220 * s, cx + 130 * s, cy - 130 * s], fill=col)
    txt = "ОШИБКА" if status == "err" else ("* " * digits).strip()
    d.text((cx, cy - 175 * s), txt, font=font(int(48 * s) + 1), fill=WHITE, anchor="mm")
    for r_ in range(4):
        for c_ in range(3):
            x = cx - 90 * s + c_ * 90 * s; y = cy - 60 * s + r_ * 80 * s
            d.rounded_rectangle([x - 34 * s, y - 30 * s, x + 34 * s, y + 30 * s], radius=int(8 * s), fill=(80, 82, 92))
            lab = "123456789*0#"[r_ * 3 + c_]
            d.text((x, y), lab, font=font(int(34 * s) + 1), fill=WHITE, anchor="mm")


def tinted_prev(img, gt):
    ov = Image.new("RGBA", (W, H), (60, 40, 20, 70)); img.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(img)
    d.rectangle([20, 200, W - 20, R.SOIL_BOT - 10], outline=(240, 236, 226), width=6)
    if int(gt * 2) % 2 == 0:
        d.ellipse([50, 225, 80, 255], fill=RED)
    d.text((95, 240), "В ПРОШЛОЙ СЕРИИ", font=font(40), fill=WHITE, anchor="lm")


def shake(img, amt, gt):
    if amt <= 0: return
    dx = int(math.sin(gt * 70) * amt); dy = int(math.cos(gt * 53) * amt)
    cp = img.crop((0, 0, W, R.SOIL_BOT))
    img.paste((0, 0, 0), (0, 0, W, R.SOIL_BOT))
    img.paste(cp, (dx, dy))


def meteor(d, x, y, r, t, col=(255, 200, 100)):
    for q in range(8):
        tx, ty, rr = x + (q + 1) * 18 * r / 20, y - (q + 1) * 26 * r / 20, r * (1 - q * 0.1)
        d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=lc(col, (160, 40, 20), q / 8))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 210))


def draw_tv(d, img, cx, cy, s, headline, sub, gt, lt):
    tw_, th_ = 760 * s, 470 * s
    d.rounded_rectangle([cx - tw_ / 2 - 24, cy - th_ / 2 - 24, cx + tw_ / 2 + 24, cy + th_ / 2 + 24],
                        radius=26, fill=(36, 36, 42))
    blink = int(gt * 3) % 2 == 0
    d.rectangle([cx - tw_ / 2, cy - th_ / 2, cx + tw_ / 2, cy + th_ / 2], fill=(150, 20, 24) if blink else (120, 14, 20))
    d.text((cx, cy - th_ / 2 + 70 * s), headline, font=font(int(64 * s) + 1), fill=WHITE, anchor="mm")
    d.text((cx, cy + 20 * s), sub, font=font(int(110 * s) + 1), fill=(255, 230, 80), anchor="mm")
    bw, bh = int(tw_), int(70 * s)
    band = Image.new("RGB", (max(1, bw), max(1, bh)), (250, 220, 40))
    bd = ImageDraw.Draw(band)
    tick = "ПРАВИТЕЛЬСТВО ПРИЗНАЛО: УДАР ЧЕРЕЗ 57 ДНЕЙ  •  "
    f_ = font(int(36 * s) + 1)
    twt = bd.textlength(tick, font=f_)
    x = -((lt * 260) % twt)
    while x < bw:
        bd.text((x, bh / 2), tick, font=f_, fill=(30, 20, 20), anchor="lm"); x += twt
    img.paste(band, (int(cx - tw_ / 2), int(cy + th_ / 2 - bh)))


# ---------- сцены ----------

def render_scene(img, seg, i, lt, p, gt, st):
    sc = seg["scene"]
    dur = seg["dur"]

    if sc in ("prev_confess", "prev_sixty"):
        EP3_SCENE(img, dict(seg, scene="confess" if sc == "prev_confess" else "sixty"), i, lt + 0.6, p, gt, st)
        tinted_prev(img, gt)
        return
    if sc == "votes":
        d = field(img, gt)
        k = ease_out(clamp((lt - 0.2) / 1.2))
        for j, (lab, val, col) in enumerate([("МОЛЧАТЬ", 58, BLUE), ("РАССКАЗАТЬ", 42, YEL)]):
            y = 470 + j * 190
            d.text((90, y - 60), lab, font=font(52), fill=col, anchor="lm")
            d.rounded_rectangle([90, y - 20, 990, y + 60], radius=20, fill=(30, 34, 52))
            wv = 900 * val / 100 * k
            if wv > 30: d.rounded_rectangle([90, y - 20, 90 + wv, y + 60], radius=20, fill=col)
            d.text((990, y - 60), f"{int(val * k)} %", font=font(52), fill=WHITE, anchor="rm")
        if lt > 1.3:
            R.draw_stamp(img, "НИКОМУ НИ СЛОВА", lt - 1.3, col=(40, 90, 200), cy=880)
        return

    # --- банкиры у забора (ночь) ---
    if sc in ("car", "suits_out", "suits_card", "suits_q", "suits_a", "collateral", "bunker_ours", "seven",
              "leave", "bank_knows"):
        d = field(img, gt)
        cx = 190
        if sc == "car":
            cx = lerp(-300, 190, ease_out(clamp(lt / 1.4)))
        if sc == "leave":
            cx = lerp(190, -400, ease_io(clamp((lt - 0.3) / 1.8)))
        night_overlay(img, 120)
        d = ImageDraw.Draw(img)
        draw_car(d, cx, gt)
        draw_gena(d, 820, GROUND + 4, 1.25, gt, boots=False, face=-1, sus=sc in ("bank_knows",))
        R.draw_hero(d, 950, GROUND + 4, 1.25, gt, face=-1)
        if sc not in ("car", "leave", "bank_knows"):
            k = ease_out(clamp(lt / 1.0)) if sc == "suits_out" else 1
            draw_suit(d, lerp(300, 470, k), GROUND + 4, 1.3, gt, walk=k < 1)
            draw_suit(d, lerp(260, 610, k), GROUND + 4, 1.3, gt, walk=k < 1)
        if sc == "suits_card":
            s = back_out(lt / 0.4)
            d.rounded_rectangle([540 - 280 * s, 470 - 130 * s, 540 + 280 * s, 470 + 130 * s], radius=14, fill=WHITE)
            d.text((540, 430), "БАНК", font=font(int(70 * s) + 1), fill=(20, 20, 30), anchor="mm")
            d.text((540, 510), "ОТДЕЛ ВЗЫСКАНИЯ", font=font(int(38 * s) + 1, True), fill=RED, anchor="mm")
        if sc == "suits_q":
            bubble(d, 860, 470, "ЭТО ВЫ ЗВОНИЛИ?", 42, tail=1)
        if sc == "suits_a":
            bubble(d, 520, 470, "МЫ. ХОТЕЛИ ПОМОЧЬ.", 42, col=(20, 20, 26), tcol=WHITE, tail=-1)
        if sc == "collateral":
            R.draw_stamp(img, "ПОЛЕ = ЗАЛОГ", lt - 0.4, cy=470)
        if sc == "bunker_ours":
            R.draw_stamp(img, "БУНКЕР = БАНКУ", lt - 0.5, cy=470)
            d = ImageDraw.Draw(img)
            d.line([(560, 620), (560, GROUND + 60)], fill=RED, width=10)
            d.polygon([(530, GROUND + 30), (590, GROUND + 30), (560, GROUND + 80)], fill=RED)
        if sc == "seven":
            outlined(d, (540, 470), "7 ДНЕЙ", 180, RED)
        if sc == "bank_knows":
            outlined(d, (540, 470), "ОНИ ЗНАЮТ", 120, RED)
        return
    if sc in ("scheme", "map"):
        img.paste((22, 26, 40), (0, 0, W, R.SOIL_BOT))
        d = ImageDraw.Draw(img)
        if sc == "scheme":
            steps = [("КРЕДИТ", YEL, 300), ("БУНКЕР", BLUE, 560), ("БАНКУ", RED, 820)]
            for k, (lab, col, y) in enumerate(steps):
                s = back_out((lt - k * 0.7) / 0.4)
                if s < 0.02: continue
                d.rounded_rectangle([540 - 260 * s, y - 80 * s, 540 + 260 * s, y + 80 * s], radius=20, fill=col)
                d.text((540, y), lab, font=font(int(80 * s) + 1), fill=(20, 16, 20), anchor="mm")
                if k and s > 0.9:
                    d.polygon([(510, y - 160), (570, y - 160), (540, y - 100)], fill=WHITE)
            outlined(d, (540, 1060), "СХЕМА", 70, WHITE)
        else:
            # карта области с бункерами
            d.rounded_rectangle([80, 240, 1000, 1180], radius=30, fill=(46, 70, 52))
            d.line([(80, 700), (1000, 640)], fill=(90, 90, 96), width=14)
            d.line([(500, 240), (560, 1180)], fill=(90, 90, 96), width=14)
            rnd = R.random.Random(11)
            pts = [(rnd.randrange(140, 940), rnd.randrange(300, 1120)) for _ in range(18)]
            n = int(len(pts) * clamp(lt / max(0.5, dur - 0.4)))
            for k, (x, y) in enumerate(pts[:n + 1]):
                d.rectangle([x - 20, y - 14, x + 20, y + 14], fill=(150, 152, 156))
                d.line([(x - 26, y - 26), (x + 26, y + 26)], fill=RED, width=8)
                d.line([(x + 26, y - 26), (x - 26, y + 26)], fill=RED, width=8)
            d.ellipse([505, 655, 545, 695], fill=YEL)
            d.text((560, 620), "МЫ", font=font(40), fill=YEL, anchor="lm")
            outlined(d, (540, 300), f"ЗАБРАНО: {min(n + 1, len(pts))}", 64, RED)
        return

    # --- подготовка ---
    if sc in ("code", "locks", "ready"):
        d = field(img, gt)
        draw_gena(d, 230, GROUND + 4, 1.25, gt, boots=False)
        R.draw_hero(d, 880, GROUND + 4, 1.25, gt, face=-1)
        if sc == "code":
            draw_keypad(d, 540, 560, 0.95, status="ok" if lt > 1.6 else None, digits=min(6, int(lt * 4)))
        if sc in ("locks", "ready"):
            # решётка, замки, солнечная панель
            d.polygon([(800, GROUND - 40), (960, GROUND - 40), (930, GROUND - 120), (830, GROUND - 120)], fill=(40, 60, 120))
            for k in range(4):
                d.line([(830 + k * 33, GROUND - 120), (812 + k * 45, GROUND - 40)], fill=(150, 170, 220), width=3)
            d.line([(880, GROUND - 40), (880, GROUND)], fill=(80, 80, 86), width=8)
            for x in range(600, 704, 20):
                d.line([(x, GROUND - 60), (x, GROUND - 26)], fill=(60, 60, 66), width=5)
            d.rectangle([636, GROUND - 40, 664, GROUND - 14], fill=(220, 180, 50))
        if sc == "ready":
            outlined(d, (540, 470), "95 %", 180, GREEN)
        return

    # --- осколки ---
    if sc in ("night3", "sky_fire", "fragments", "impact", "crater"):
        red = {"night3": 0, "sky_fire": ease_io(lt / 1.0), "fragments": 1, "impact": 1, "crater": 0.6}[sc]
        d = R.draw_sky(img, gt, red)
        R.draw_landscape(d); R.draw_ground(d); R.draw_fence(d, 60, 250)
        if sc == "crater":
            d.chord([40, GROUND - 40, 300, GROUND + 160], 0, 180, fill=(30, 20, 16))
            for k in range(5):
                a = gt * 1.2 + k
                d.ellipse([170 + math.cos(a) * 40 - 30, GROUND - 120 - k * 50 - (gt * 30) % 40,
                           170 + math.cos(a) * 40 + 30, GROUND - 60 - k * 50 - (gt * 30) % 40], fill=(110, 110, 116))
        draw_bunker_plus(d)
        draw_gena(d, 820, GROUND + 4, 1.2, gt, boots=False, face=-1)
        R.draw_hero(d, 950, GROUND + 4, 1.2, gt, face=-1)
        if sc in ("sky_fire", "fragments"):
            for k in range(7):
                ft = (gt * 0.7 + k * 0.37) % 1.0
                meteor(d, 1100 - ft * 900 + k * 40, 120 + ft * 600, 10 + (k % 3) * 6, gt)
        if sc == "impact":
            mt = clamp(lt / 0.8)
            if mt < 1:
                meteor(d, lerp(900, 170, mt), lerp(150, GROUND - 20, mt), 40, gt)
            else:
                k = clamp((lt - 0.8) / 0.8)
                d.ellipse([170 - 400 * k, GROUND - 300 * k, 170 + 400 * k, GROUND + 100 * k], fill=(255, 220, 140))
                shake(img, 14 * (1 - k), gt)
        if sc == "crater":
            outlined(d, (540, 430), "3 М", 140, YEL)
            R.draw_stamp(img, "БУНКЕР ЦЕЛ", lt - 0.6, col=(40, 150, 70), cy=600)
        return
    if sc in ("tv", "tv57", "all_know"):
        d = R.draw_sky(img, gt, 0.3)
        R.draw_landscape(d); R.draw_ground(d)
        draw_bunker_plus(d)
        s = back_out(lt / 0.4) if sc == "tv" else 1
        draw_tv(d, img, 470, 560, 0.9 * s if s > 0.02 else 0.02, "ЭКСТРЕННО", "57 ДНЕЙ" if sc != "tv" else "!!!", gt, lt)
        d = ImageDraw.Draw(img)
        draw_gena(d, 960, GROUND + 4, 1.2, gt, boots=False, face=-1)
        if sc == "tv57" and lt > 2.0:
            R.draw_stamp(img, "ГЕНА БЫЛ ПРАВ", lt - 2.0, col=(40, 150, 70), cy=920)
        if sc == "all_know":
            R.draw_stamp(img, "ЗНАЮТ ВСЕ", lt - 0.3, cy=920)
        return
    if sc == "panic":
        d = R.draw_sky(img, gt, 0.5)
        R.draw_landscape(d); R.draw_ground(d)
        rnd = R.random.Random(5)
        for k in range(9):
            x = 60 + k * 125; hh = 120 + rnd.randrange(60)
            d.rectangle([x - 50, GROUND - hh, x + 50, GROUND], fill=(130 + rnd.randrange(30), 90, 60))
            d.polygon([(x - 62, GROUND - hh), (x, GROUND - hh - 60), (x + 62, GROUND - hh)], fill=(100, 100, 110))
        for k in range(7):   # бегущие люди
            x = ((gt * (180 + k * 30) + k * 160) % 1300) - 100
            col = [(150, 70, 110), (60, 120, 160), (200, 80, 40), (120, 128, 66)][k % 4]
            d.rounded_rectangle([x - 18, GROUND - 120, x + 18, GROUND - 50], radius=8, fill=col)
            d.ellipse([x - 16, GROUND - 156, x + 16, GROUND - 124], fill=(236, 194, 160))
            leg = math.sin(gt * 14 + k) * 14
            d.line([(x, GROUND - 50), (x - leg, GROUND)], fill=(50, 50, 60), width=10)
            d.line([(x, GROUND - 50), (x + leg, GROUND)], fill=(50, 50, 60), width=10)
        outlined(d, (540, 430), "ПАНИКА", 150, RED)
        outlined(d, (540, 580), "0 БУНКЕРОВ НА 40 ЧЕЛОВЕК", 46, WHITE)
        return

    # --- тётя Валя ---
    if sc in ("valya", "valya_ask", "gena_silent", "two", "lie", "kids_back"):
        d = field(img, gt, red=0.3)
        vx = 140
        if sc == "valya":
            vx = lerp(-100, 140, ease_out(clamp(lt / 1.4)))
        if sc == "kids_back":
            vx = lerp(140, -260, ease_io(clamp((lt - 0.3) / 2.0)))
        draw_valya(d, vx, GROUND + 4, 1.25, face=1 if sc != "kids_back" else -1)
        draw_kid(d, vx + 80, GROUND + 4, 1.1, col=(230, 90, 110), face=1 if sc != "kids_back" else 1)
        draw_kid(d, vx + 150, GROUND + 4, 0.95, col=(80, 150, 220), face=1, hair=(220, 190, 90))
        draw_gena(d, 830, GROUND + 4, 1.2, gt, boots=False, face=-1, sus=sc == "gena_silent")
        R.draw_hero(d, 680, GROUND + 4, 1.3, gt, face=-1)
        if sc == "valya_ask":
            bubble(d, 300, 450, "ПУСТИ ДЕТЕЙ…", 52, tail=-1)
        if sc == "gena_silent":
            outlined(d, (830, 600), "…", 120, WHITE)
        if sc == "two":
            outlined(d, (540, 450), "МЕСТ: 2", 120, YEL)
            outlined(d, (540, 580), "ЛЮДЕЙ: 5", 80, RED)
        if sc == "lie":
            bubble(d, 680, 460, "ТАМ ПРОСТО ПОГРЕБ", 44, tail=1)
            R.draw_stamp(img, "СОВРАЛ", lt - 1.2, cy=650)
        if sc == "kids_back":
            outlined(d, (540, 470), "…", 160, WHITE)
        return

    # --- штурм ---
    if sc in ("return", "dig_side", "hit", "sirens", "army", "arrest", "loud", "distribute"):
        d = field(img, gt, red=0.3)
        ex_x = 900
        if sc == "return":
            k = ease_out(clamp(lt / 2.0))
            draw_car(d, lerp(-400, 140, k), gt)
            draw_truck(d, lerp(-900, -250, k) + 200)
            R.draw_excavator(d, lerp(1400, 900, k), 0.4, gt)
        else:
            draw_car(d, 140, gt)
            arm = 0.5 + 0.5 * math.sin(gt * 3) if sc in ("dig_side", "hit") else 0.2
            R.draw_excavator(d, ex_x, arm, gt)
            if sc in ("dig_side", "hit", "sirens"):
                d.polygon([(PX1 + 10, GROUND), (PX1 + 140, GROUND), (PX1 + 60, GROUND + 180), (PX1 + 10, GROUND + 200)],
                          fill=(40, 28, 22))
        if sc in ("army", "arrest", "loud", "distribute"):
            k = ease_out(clamp(lt / 1.5)) if sc == "army" else 1
            draw_truck(d, lerp(-500, 220, k), army=True)
            draw_soldier(d, 520, GROUND + 4, 1.25, gt)
            draw_soldier(d, 620, GROUND + 4, 1.25, gt, face=-1)
        if sc == "arrest":
            draw_suit(d, 720, GROUND + 4, 1.25, gt, smile=False)
            d.line([(700, GROUND - 160), (740, GROUND - 160)], fill=(180, 180, 190), width=8)
        if sc in ("sirens", "army", "arrest"):
            c = RED if int(gt * 6) % 2 else BLUE
            ov = Image.new("RGBA", (W, H), c + (50,)); img.paste(ov, (0, 0), ov)
            d = ImageDraw.Draw(img)
            if sc == "sirens":
                outlined(d, (540, 470), "УИУ-УИУ", 120, WHITE)
        if sc == "hit":
            shake(img, 10 if (lt % 0.9) < 0.25 else 0, gt)
            d = ImageDraw.Draw(img)
            outlined(d, (540, 470), "БАХ!" if lt < 1.2 else "БАХ! БАХ!", 130, YEL)
        if sc == "loud":
            d.polygon([(380, 520), (460, 500), (560, 440), (560, 640), (460, 580), (380, 560)], fill=(200, 200, 210))
            bubble(d, 760, 480, "ЗАРЕГИСТРИРОВАТЬ", 40, col=(40, 70, 40), tcol=WHITE, tail=-1)
            bubble(d, 760, 580, "ВСЕ УКРЫТИЯ", 40, col=(40, 70, 40), tcol=WHITE, tail=-1)
        if sc == "distribute":
            R.draw_stamp(img, "УКРЫТИЕ ИЗЪЯТЬ?", lt - 0.4, cy=470)
        return
    if sc in ("lock_in", "sparks", "holds", "plan"):
        d = interior(img, gt, lamp=0.8)
        hy = R.SOIL_BOT - 56
        draw_gena(d, 300, hy, 1.4, gt, boots=False, face=1)
        R.draw_hero(d, 640, hy, 1.4, gt, face=-1)
        if sc == "lock_in":
            k = ease_out(clamp(lt / 1.2))
            d.rectangle([780, 200, 880, 200 + 30 * k], fill=STEEL)
            outlined(d, (480, 400), "ЗАКРЫТО", 90, GREEN)
        if sc == "sparks":
            for k in range(14):
                a = gt * 9 + k
                x = 830 + math.cos(a) * (30 + (k * 17) % 60); y = 230 + abs(math.sin(a)) * (40 + (k * 13) % 80)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 220, 80))
            outlined(d, (480, 400), "СКРЕЖЕТ", 90, RED)
            shake(img, 4, gt)
        if sc == "holds":
            R.draw_stamp(img, "ДВЕРЬ ДЕРЖИТ", lt - 0.3, col=(40, 150, 70), cy=420)
        if sc == "plan":
            bubble(d, 330, 420, "У МЕНЯ ЕСТЬ ПЛАН", 44, tail=-1)
            d.ellipse([440, hy - 260, 480, hy - 220], fill=(236, 190, 152))   # рука на плече
        return

    # --- поворот ---
    if sc in ("water", "keypad", "err1", "err2", "intercom", "sorry", "masha", "three"):
        d = field(img, gt, red=0.2)
        night_overlay(img, 140)
        d = ImageDraw.Draw(img)
        if sc == "water":
            k = ease_out(clamp(lt / 1.6))
            R.draw_hero(d, lerp(650, 900, k), GROUND + 4, 1.3, gt, walk=k < 1)
            d.rectangle([lerp(650, 900, k) + 30, GROUND - 130, lerp(650, 900, k) + 70, GROUND - 70], fill=(110, 170, 230))
            return
        R.draw_hero(d, 820, GROUND + 4, 1.3, gt, face=-1)
        d.rectangle([850, GROUND - 130, 890, GROUND - 70], fill=(110, 170, 230))
        if sc in ("keypad", "err1", "err2"):
            st_ = None if sc == "keypad" else "err"
            if sc == "err2" and lt < 0.5:
                st_ = None
            draw_keypad(d, 480, 560, 0.95, status=st_, digits=min(6, int(lt * 5)) if sc != "err1" else 6)
            if st_ == "err":
                ov = Image.new("RGBA", (W, H), (200, 0, 0, 40 if int(gt * 8) % 2 else 0)); img.paste(ov, (0, 0), ov)
        else:
            # динамик
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([340, 380, 620, 640], radius=24, fill=(50, 52, 60), outline=(120, 120, 130), width=6)
            for k in range(6):
                d.line([(380, 420 + k * 34), (580, 420 + k * 34)], fill=(30, 30, 34), width=10)
            if int(gt * 5) % 2 == 0:
                d.ellipse([462, 600, 498, 630], fill=GREEN)
            for k in range(3):
                r = 50 + k * 40 + (gt * 80) % 40
                d.arc([480 - r - 200, 510 - r, 480 + r - 200, 510 + r], 140, 220, fill=(200, 200, 220), width=5)
            if sc == "sorry":
                bubble(d, 480, 300, "Я ПОМЕНЯЛ КОД", 48, col=(196, 196, 202), tail=-1)
            if sc == "masha":
                bubble(d, 480, 300, "ТУТ СО МНОЙ МАША", 44, col=(196, 196, 202), tail=-1)
                # врезка: девочка в бункере
                d.rounded_rectangle([620, 660, 1000, 960], radius=20, fill=(60, 60, 66), outline=WHITE, width=5)
                draw_kid(d, 760, 930, 1.3, col=(230, 200, 60), hair=(200, 120, 50))
                draw_gena(d, 900, 930, 0.9, gt, boots=False, face=-1)
            if sc == "three":
                outlined(d, (480, 300), "НАС ТРОЕ", 100, RED)
        return
    if sc == "boxes_flash":
        d = field(img, gt)
        night_overlay(img, 140)
        d = ImageDraw.Draw(img)
        draw_gena(d, 400, GROUND + 4, 1.4, gt, boots=True)
        s = back_out(lt / 0.5)
        cx, cy = 600, 560
        d.rectangle([cx - 200 * s, cy - 60 * s, cx + 200 * s, cy + 160 * s], fill=(170, 130, 80), outline=(120, 90, 50),
                    width=6)
        if s > 0.5:   # мишка и платье
            d.ellipse([cx - 150, cy - 140, cx - 30, cy - 20], fill=(170, 110, 60))
            d.ellipse([cx - 160, cy - 160, cx - 120, cy - 120], fill=(170, 110, 60))
            d.ellipse([cx - 60, cy - 160, cx - 20, cy - 120], fill=(170, 110, 60))
            d.ellipse([cx - 110, cy - 100, cx - 70, cy - 60], fill=(220, 180, 140))
            d.polygon([(cx + 40, cy - 30), (cx + 150, cy - 30), (cx + 180, cy + 60), (cx + 10, cy + 60)], fill=(230, 120, 160))
        ov = Image.new("RGBA", (W, H), (120, 80, 40, 50)); img.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(img)
        d.text((60, 240), "ТЕ НОЧИ", font=font(40), fill=WHITE, anchor="lm")
        return
    if sc in ("alone", "nothing", "car_again", "banker", "deal"):
        d = field(img, gt, red=0.8)
        R.draw_hero(d, 640, GROUND + 4, 1.4, gt, face=-1 if sc != "alone" else 1)
        if sc == "alone":
            outlined(d, (540, 450), "СВОЯ ЯМА", 120, WHITE)
        if sc == "nothing":
            outlined(d, (540, 380), "50 ДНЕЙ", 110, RED)
            outlined(d, (540, 510), "400 $", 110, YEL)
            outlined(d, (540, 640), "0 БУНКЕРОВ", 80, WHITE)
        if sc in ("car_again", "banker", "deal"):
            k = ease_out(clamp(lt / 1.6)) if sc == "car_again" else 1
            draw_car(d, lerp(-400, 200, k), gt)
            flashlight(img, lerp(-400, 200, k) - 194, GROUND - 82, 1, a=90, spread=80, length=700)
            d = ImageDraw.Draw(img)
            if sc in ("banker", "deal"):
                draw_suit(d, 230, GROUND - 60, 0.7, gt)   # из окна
                bubble(d, 360, 430, "ТЕПЕРЬ ПОГОВОРИМ?" if sc == "banker" else "БУНКЕР — БАНКУ", 46,
                       col=(20, 20, 26), tcol=WHITE, tail=-1)
        return
    if sc.startswith("choice"):
        foc = {"choice_l": 0, "choice_r": 1, "choice_r2": 1}.get(sc)
        field(img, gt, red=0.6)
        R.draw_choice(img, lt if sc == "choice" else 5.0, gt, focus=foc, vote=sc.startswith("choice_vote"))
        d = ImageDraw.Draw(img)
        if sc == "choice_r2":
            R.draw_stamp(img, "ПОВЕРЯТ?", lt - 0.3, cy=960)
        if sc == "choice_vote2":
            s = back_out(lt / 0.5)
            d.text((540, 960), "СЕРИЯ 5 — ВЫБИРАЕТЕ ВЫ", font=font(int(44 * s) + 1), fill=YEL, anchor="mm")
        return
    raise KeyError(sc)


R.render_scene = render_scene


def sfx_events(add, S, L, nxt, fx):
    th, pp, ca, wh, bo, ra, mo = (fx[k] for k in ("thud", "pop", "cash", "whoosh", "boom", "rain", "motor"))
    add(S("prev_confess"), wh(0.8)); add(S("prev_sixty"), bo() * 0.4)
    add(S("votes"), wh(1.2)); add(S("votes") + 1.3, th())
    add(S("car"), mo(L("car") + 0.4))
    add(S("suits_out"), pp()); add(S("suits_card"), pp())
    add(S("collateral") + 0.4, th()); add(S("bunker_ours") + 0.5, th()); add(S("seven"), bo() * 0.4)
    add(S("leave"), mo(1.8) * 0.6); add(S("bank_knows"), bo() * 0.3)
    for k in range(3): add(S("scheme") + k * 0.7, pp())
    add(S("map"), wh(1.0))
    for k in range(6): add(S("code") + k * 0.25, pp() * 0.5)
    add(S("code") + 1.6, ca()); add(S("locks"), ca()); add(S("ready"), pp())
    add(S("sky_fire"), wh(1.5)); add(S("fragments"), wh(2.0))
    add(S("impact") + 0.8, bo()); add(S("crater") + 0.6, th())
    add(S("tv"), pp()); add(S("tv57") + 2.0, th()); add(S("all_know") + 0.3, th())
    add(S("panic"), wh(1.5))
    add(S("valya"), pp()); add(S("lie") + 1.2, th()); add(S("kids_back"), wh(1.5) * 0.5)
    add(S("return"), mo(L("return") + 0.5))
    add(S("lock_in") + 0.6, th())
    add(S("sparks"), ra(L("sparks") + 0.4) * 1.5); add(S("holds") + 0.3, th())
    add(S("dig_side"), mo(L("dig_side") + L("hit")))
    for k in range(3): add(S("hit") + k * 0.9, bo() * 0.6)
    add(S("sirens"), wh(1.0)); add(S("army"), mo(1.5)); add(S("arrest"), th())
    add(S("distribute") + 0.4, th())
    for k in range(6): add(S("keypad") + k * 0.2, pp() * 0.5)
    add(S("err1"), th()); add(S("err2") + 0.5, th())
    add(S("sorry"), bo() * 0.5); add(S("masha"), pp()); add(S("boxes_flash"), wh(0.8))
    add(S("three"), th()); add(S("nothing"), bo() * 0.5)
    add(S("car_again"), mo(L("car_again") + 0.5))
    add(S("choice"), wh(0.5)); add(S("choice") + 0.15, wh(0.5)); add(S("choice") + 0.5, pp())
    add(S("choice_l"), pp()); add(S("choice_r"), pp()); add(S("choice_r2") + 0.3, th())


if __name__ == "__main__":
    R.main()
