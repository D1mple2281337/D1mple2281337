#!/usr/bin/env python3
"""Обложка серии 2. python3 cover_ep2.py out/cover_ep2.jpg"""
import sys
from PIL import Image, ImageDraw
import render as R
import ep2

img = Image.new("RGB", (R.W, R.H), R.BOTTOM)
d = R.draw_sky(img, 0.0, red=0.35)
R.draw_landscape(d); R.draw_ground(d); R.draw_fence(d, 60, 250)
ep2.draw_bunker(d, walls=1, roof=True)
ep2.draw_shed(d, 880, broken=True)
ep2.draw_thief(d, 1010, 0.3)
R.draw_hero(d, 560, R.GROUND + 4, 1.1, 0)
R.draw_hud(img, 296, 60, 600, None, -1)
d = ImageDraw.Draw(img)
o = lambda xy, t, f, c: d.text(xy, t, font=f, fill=c, anchor="mm", stroke_width=12, stroke_fill=(10, 8, 12))
o((540, 290), "ОСТАЛОСЬ", R.font(120), R.WHITE)
o((540, 450), "600 $", R.font(190), R.RED)
R.draw_stamp(img, "МЕНЯ ОГРАБИЛИ", 1.0, cy=600)
d = ImageDraw.Draw(img)
d.rectangle([0, R.SOIL_BOT, R.W, R.H], fill=R.BOTTOM)
d.rounded_rectangle([340, 1430, 740, 1530], radius=20, fill=R.YEL)
d.text((540, 1480), "СЕРИЯ 2", font=R.font(64), fill=(20, 16, 20), anchor="mm")
d.text((540, 1610), "ЗАЙМ или СОСЕД?", font=R.font(56), fill=R.WHITE, anchor="mm")
img.save(sys.argv[1], quality=95)
