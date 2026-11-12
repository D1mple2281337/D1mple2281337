#!/usr/bin/env python3
"""Обложка серии 3. python3 cover_ep3.py out/cover_ep3.jpg"""
import sys
from PIL import Image, ImageDraw
import render as R
import ep3

img = Image.new("RGB", (R.W, R.H), R.BOTTOM)
d = ep3.interior(img, 0, mess=True)
ep3.draw_gena(d, 300, R.SOIL_BOT - 56, 1.5, 0, boots=True, sus=True)
R.draw_hero(d, 830, R.SOIL_BOT - 56, 1.5, 0, shovel=True, dig=0.2, face=-1)
ov = Image.new("RGBA", (R.W, R.H), (120, 0, 0, 70)); img.paste(ov, (0, 0), ov)
R.draw_hud(img, 60, 88, 2600, None, -1)
d = ImageDraw.Draw(img)
ep3.outlined(d, (540, 300), "ВОР — СОСЕД?", 110, R.WHITE, 12)
ep3.outlined(d, (540, 500), "60 ДНЕЙ", 170, R.RED, 14)
R.draw_stamp(img, "ОН ЗНАЕТ ПРАВДУ", 1.0, cy=690)
d = ImageDraw.Draw(img)
d.rectangle([0, R.SOIL_BOT, R.W, R.H], fill=R.BOTTOM)
d.rounded_rectangle([340, 1430, 740, 1530], radius=20, fill=R.YEL)
d.text((540, 1480), "СЕРИЯ 3", font=R.font(64), fill=(20, 16, 20), anchor="mm")
d.text((540, 1610), "РАССКАЗАТЬ или МОЛЧАТЬ?", font=R.font(50), fill=R.WHITE, anchor="mm")
img.save(sys.argv[1], quality=95)
