#!/usr/bin/env python3
"""Обложка серии 1 (1080x1920). python3 cover.py out/cover_ep1.jpg"""
import sys, math
from PIL import Image, ImageDraw
import render as R

img = Image.new("RGB", (R.W, R.H), R.BOTTOM)
d = R.draw_sky(img, 0.0, red=0.85)
R.draw_landscape(d)
R.draw_ground(d, pit_w=360, pit_d=270, water=0.0, cx=620)
# метеор
mx, my = 830, 560
for k in range(16):
    tx, ty = mx + k * 24, my - k * 34; r = 44 - k * 2.4
    d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=R.lc((255, 225, 130), (200, 60, 30), k / 16))
d.ellipse([mx - 50, my - 50, mx + 50, my + 50], fill=(255, 244, 210))
# экскаватор + герой
R.draw_excavator(d, 250, 0.7, 0)
R.draw_hero(d, 930, R.GROUND + 4, 1.5, 0)
# отметка глубины
d.line([(830, R.GROUND), (830, R.GROUND + 270)], fill=R.YEL, width=6)
d.text((850, R.GROUND + 140), "6 М", font=R.font(52), fill=R.YEL, anchor="lm")
# HUD
R.draw_hud(img, 365, 0, 25000, None, -1)
d = ImageDraw.Draw(img)

def outlined(xy, text, f, fill, stroke=10):
    d.text(xy, text, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(10, 8, 12))

outlined((540, 330), "БУНКЕР", R.font(170), R.WHITE, 12)
outlined((540, 500), "ЗА 25 000 $", R.font(130), R.YEL, 12)
R.draw_stamp(img, "ГОД ДО КОНЦА СВЕТА", 1.0, cy=670)
# нижняя плашка
d = ImageDraw.Draw(img)
d.rectangle([0, R.SOIL_BOT, R.W, R.H], fill=R.BOTTOM)
d.rounded_rectangle([340, 1430, 740, 1530], radius=20, fill=R.YEL)
d.text((540, 1480), "СЕРИЯ 1", font=R.font(64), fill=(20, 16, 20), anchor="mm")
d.text((540, 1610), "ТЫ РЕШАЕШЬ, ЧТО ДАЛЬШЕ", font=R.font(46), fill=R.WHITE, anchor="mm")
img.save(sys.argv[1], quality=95)
