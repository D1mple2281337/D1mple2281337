#!/usr/bin/env python3
"""Синтез звуковых эффектов по таймингам. python3 sfx.py timings.json out.wav"""
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
S=lambda i: tm[i][0] if i else 0.0
add(S(0)+0.1, pop())
add(S(1)+0.0, whoosh(1.2)); add(S(1)+1.2, boom()); add(S(1)+0.4, thud())
add(S(3)+0.0, pop())
for i in (4,7,11,16): add(S(i), pop())
add(S(5)+0.3, thud()); add(S(5), whoosh(1.5))
add(S(6)+1.0, thud()); add(S(6), cash())
add(S(8)+0.5, thud())
add(S(9), motor(tm[9][1]-tm[9][0]+0.3))
add(S(10)+0.0, cash()); add(S(10)+0.2, thud())
add(S(11), rain(tm[12][0]-tm[11][0]+0.8))
add(S(12)+0.5, thud())
add(S(13)+0.8, motor(tm[13][1]-tm[13][0]-0.6)*0.6)
add(S(14), cash()); add(S(14)+0.8, thud())
add(S(15)+0.5, pop())
add(S(16), whoosh(0.5)); add(S(16)+0.15, whoosh(0.5)); add(S(16)+0.5, pop())
add(S(17), pop()); add(S(18), pop())
out=out/max(1,np.max(np.abs(out))/0.9)
w=wave.open(sys.argv[2],'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
