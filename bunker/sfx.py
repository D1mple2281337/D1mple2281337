#!/usr/bin/env python3
"""Синтез звуковых эффектов по таймингам. python3 sfx.py timings.json out.wav [ep2]"""
import sys, json, numpy as np, wave
sr=44100; tm=json.load(open(sys.argv[1]))["segments"]
dur=tm[-1][1]+4; n=int(sr*dur); out=np.zeros(n); rng=np.random.default_rng(3)
def add(t0, x):
    i=int(t0*sr); j=min(n,i+len(x)); out[i:j]+=x[:j-i]
def tt(d): return np.arange(int(sr*d))/sr
def thud():  # удар штампа
    t=tt(0.35); return 0.9*np.sin(2*np.pi*(60+120*np.exp(-t*25))*t)*np.exp(-t*12)+0.3*rng.standard_normal(len(t))*np.exp(-t*40)
def pop():
    t=tt(0.18); return 0.4*np.sin(2*np.pi*(500+900*t)*t)*np.exp(-t*25)
def cash():
    t=tt(0.6); return 0.35*(np.sin(2*np.pi*1320*t)+0.6*np.sin(2*np.pi*1980*t))*np.exp(-t*7)
def whoosh(d=0.6):
    t=tt(d); x=rng.standard_normal(len(t)); x=np.convolve(x,np.ones(30)/30,'same')
    return 0.8*x*np.sin(np.pi*t/d)
def boom():
    t=tt(2.0); x=np.convolve(rng.standard_normal(len(t)),np.ones(80)/80,'same')
    return 2.5*x*np.exp(-t*2)+0.8*np.sin(2*np.pi*40*t)*np.exp(-t*2.5)
def rain(d):
    t=tt(d); x=rng.standard_normal(len(t)); x=x-np.convolve(x,np.ones(4)/4,'same')
    return 0.12*x*np.minimum(1,np.minimum(t/0.5,(d-t)/0.5))
def motor(d):
    t=tt(d); return 0.12*np.sign(np.sin(2*np.pi*38*t))*(0.6+0.4*np.sin(2*np.pi*3*t))*np.minimum(1,np.minimum(t/0.3,(d-t)/0.3))
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import importlib
EP = importlib.import_module(sys.argv[3]) if len(sys.argv) > 3 else None
import render
SEGMENTS = render.SEGMENTS
assert len(SEGMENTS) == len(tm), "число сегментов не совпадает с таймингами"
idx = {}
for k, sg in enumerate(SEGMENTS): idx.setdefault(sg["scene"], k)
S = lambda name: tm[idx[name]][0] if idx[name] else 0.0
L = lambda name: tm[idx[name]][1] - tm[idx[name]][0]
nxt = lambda name: tm[idx[name] + 1][0]
if EP:
    EP.sfx_events(add, S, L, nxt, dict(thud=thud, pop=pop, cash=cash, whoosh=whoosh, boom=boom, rain=rain, motor=motor))
else:
    add(S("tv"), pop()); add(S("tv") + 1.2, pop())
    add(S("asteroid"), whoosh(1.5)); add(S("asteroid") + 0.9, pop())
    add(S("loan"), cash()); add(S("loan") + 0.8, thud())
    add(S("doubt"), whoosh(0.8))
    add(S("doubt2") + 0.2, thud()); add(S("doubt2") + 1.6, thud())
    add(S("list"), pop())
    for nm in ("city", "field2", "rain", "choice"): add(S(nm), pop())
    add(S("city_price") + 0.3, thud()); add(S("city_price"), whoosh(1.5))
    add(S("field") + 1.0, thud()); add(S("field"), cash())
    add(S("shovel") + 0.5, thud())
    add(S("excav"), motor(L("excav") + 0.3))
    add(S("pit"), cash()); add(S("pit") + 0.2, thud())
    add(S("rain"), rain(nxt("rain") - S("rain") + 0.8))
    add(S("flood") + 0.5, thud())
    add(S("pump") + 0.8, motor(L("pump") - 0.6) * 0.6)
    add(S("dry"), cash()); add(S("dry") + 0.8, thud())
    add(S("list2") + 0.5, pop())
    add(S("choice"), whoosh(0.5)); add(S("choice") + 0.15, whoosh(0.5)); add(S("choice") + 0.5, pop())
    add(S("choice_l"), pop()); add(S("choice_r"), pop())

out=out/max(1,np.max(np.abs(out))/0.9)
w=wave.open(sys.argv[2],'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
