#!/usr/bin/env python3
"""Обложка серии 5. python3 cover_ep5.py out/cover_ep5.jpg"""
import sys
from PIL import Image, ImageDraw
import render as R
import ep5

img = Image.new("RGB", (R.W, R.H), R.BOTTOM)
d = ep5.field(img, 0, red=0.6)
ep5.night_overlay(img, 90)
d = ImageDraw.Draw(img)
ep5.draw_car(d, 120, 0)
ep5.draw_arkady(d, 360, R.GROUND + 4, 1.4, 0, pale=True)
ep5.draw_gena(d, 700, R.GROUND + 4, 1.4, 0, boots=False, face=-1)
ep5.draw_kid(d, 790, R.GROUND + 4, 1.1, face=-1, **ep5.MASHA)
R.draw_hud(img, 42, 0, 400, None, -1)
d = ImageDraw.Draw(img)
ep5.outlined(d, (540, 300), "БАНКИР —", 120, R.WHITE, 12)
ep5.outlined(d, (540, 450), "ЕГО СЫН", 140, R.RED, 12)
R.draw_stamp(img, "ПАПА?!", 1.0, cy=620)
d = ImageDraw.Draw(img)
d.rectangle([0, R.SOIL_BOT, R.W, R.H], fill=R.BOTTOM)
d.rounded_rectangle([340, 1430, 740, 1530], radius=20, fill=R.YEL)
d.text((540, 1480), "СЕРИЯ 5", font=R.font(64), fill=(20, 16, 20), anchor="mm")
d.text((540, 1610), "ПРОВЕСТИ или ПРЕДУПРЕДИТЬ?", font=R.font(46), fill=R.WHITE, anchor="mm")
img.save(sys.argv[1], quality=95)
