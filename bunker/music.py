#!/usr/bin/env python3
"""Синтез фоновой музыки (тревожный пульс) — без внешних файлов. python3 music.py out.wav seconds"""
import sys, numpy as np, wave
sr=44100; dur=float(sys.argv[2]); n=int(sr*dur); t=np.arange(n)/sr
bpm=100; beat=60/bpm
# басовый дрон по аккордам Am - F - C - G
roots=[55.0,43.65,65.41,49.0]
bar=beat*4
idx=((t//bar)%4).astype(int)
f=np.array(roots)[idx]
ph=np.cumsum(2*np.pi*f/sr)
pad=0.18*np.sin(ph)+0.08*np.sin(2*ph)+0.05*np.sin(3.01*ph)
# пульс-кик
bt=t%beat; kick=0.5*np.sin(2*np.pi*(50+90*np.exp(-bt*30))*bt)*np.exp(-bt*9)
# хэт на восьмые
rng=np.random.default_rng(1); noise=rng.standard_normal(n)
et=t%(beat/2); hat=0.04*noise*np.exp(-et*60)
# арпеджио
at=t%(beat/2); step=((t//(beat/2))%8).astype(int)
mult=np.array([2,3,4,3,2,4,3,5])[step]
arp=0.06*np.sin(2*np.pi*f*mult*at*1.0)*np.exp(-at*8)
x=pad+kick+hat+arp
fade=np.minimum(1,np.minimum(t/1.5,(dur-t)/2.0)); x*=fade
x=x/np.max(np.abs(x))*0.9
w=wave.open(sys.argv[1],'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
