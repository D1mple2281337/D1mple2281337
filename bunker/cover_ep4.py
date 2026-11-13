#!/usr/bin/env python3
"""Обложка серии 4. python3 cover_ep4.py out/cover_ep4.jpg"""
import sys
from PIL import Image, ImageDraw
import render as R
import ep4

img = Image.new("RGB", (R.W, R.H), R.BOTTOM)
d = ep4.field(img, 0, red=0.9)
for k in range(5):
    ep4.meteor(d, 300 + k * 170, 160 + (k % 2) * 90, 14 + (k % 3) * 6, 0)
ep4.draw_keypad(d, 330, 690, 0.8, status="err")
R.draw_hero(d, 760, R.GROUND + 4, 1.4, 0, face=-1)
R.draw_hud(img, 50, 0, 400, None, -1)
d = ImageDraw.Draw(img)
ep4.outlined(d, (540, 290), "ОН ЗАПЕР", 120, R.WHITE, 12)
ep4.outlined(d, (540, 430), "МЕНЯ СНАРУЖИ", 96, R.RED, 12)
d.rectangle([0, R.SOIL_BOT, R.W, R.H], fill=R.BOTTOM)
d.rounded_rectangle([340, 1430, 740, 1530], radius=20, fill=R.YEL)
d.text((540, 1480), "СЕРИЯ 4", font=R.font(64), fill=(20, 16, 20), anchor="mm")
d.text((540, 1610), "БАНК или СОСЕДИ?", font=R.font(56), fill=R.WHITE, anchor="mm")
img.save(sys.argv[1], quality=95)
