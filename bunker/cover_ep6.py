#!/usr/bin/env python3
"""Обложка серии 6. python3 cover_ep6.py out/cover_ep6.jpg"""
import sys
from PIL import Image, ImageDraw
import render as R
import ep6

img = Image.new("RGB", (R.W, R.H), R.BOTTOM)
d = ep6.school_yard(img, 0, red=0.6, sign=True)
for j in range(2):
    ep6.draw_truck(d, 120 - j * 330, army=True)
ep6.draw_soldier(d, 330, R.GROUND + 4, 1.2, 0)
d.rectangle([480, R.GROUND - 14, 600, R.GROUND + 4], fill=(20, 20, 24))
ep6.draw_kid(d, 560, R.GROUND + 4, 1.15, **ep6.MASHA)
ep6.draw_arkady(d, 720, R.GROUND + 4, 1.3, 0, face=-1, pale=True)
R.draw_hud(img, 41, 100, 400, None, -1)
d = ImageDraw.Draw(img)
ep6.outlined(d, (540, 290), "ОН ВЫБРАЛ", 110, R.WHITE, 12)
ep6.outlined(d, (540, 430), "ДОЧЬ", 170, R.YEL, 14)
R.draw_stamp(img, "НОВАЯ ДАТА УДАРА…", 1.0, cy=610)
d = ImageDraw.Draw(img)
d.rectangle([0, R.SOIL_BOT, R.W, R.H], fill=R.BOTTOM)
d.rounded_rectangle([340, 1430, 740, 1530], radius=20, fill=R.YEL)
d.text((540, 1480), "СЕРИЯ 6", font=R.font(64), fill=(20, 16, 20), anchor="mm")
d.text((540, 1610), "ВПУСТИТЬ или НИКОГО?", font=R.font(52), fill=R.WHITE, anchor="mm")
img.save(sys.argv[1], quality=95)
