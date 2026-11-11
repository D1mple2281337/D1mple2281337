#!/usr/bin/env python3
"""Выравнивание сценария по паузам в озвучке (ffmpeg silencedetect + DP по слогам).
Каждое предложение должно заканчиваться паузой; абзацы = группы предложений.
python3 align.py voice.mp3 script.txt timings.json"""
import sys, re, json, subprocess
audio, script, out = sys.argv[1:4]
paras = [re.sub(r"\[[^\]]*\]", "", p).strip() for p in open(script, encoding="utf-8").read().split("\n\n") if p.strip()]
sents, owner = [], []
for i, p in enumerate(paras):
    for s in re.split(r"(?<=[.?!:])\s+", p):
        if s.strip(): sents.append(s); owner.append(i)
syl = lambda s: len(re.findall(r"[аеёиоуыэюяАЕЁИОУЫЭЮЯ]", s)) + 0.6
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",audio]))
log = subprocess.run(["ffmpeg","-i",audio,"-af","silencedetect=noise=-40dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",log)]
en=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",log)]
pairs=list(zip(st,en+[dur]*(len(st)-len(en))))
s0 = pairs[0][1] if pairs and pairs[0][0] < 0.05 else 0.0
s1 = pairs[-1][0] if pairs and pairs[-1][1] >= dur-0.05 else dur
sil=[(a,b) for a,b in pairs if a > s0+0.2 and b < s1-0.1]
n=len(sents)-1; m=len(sil)
w=[syl(s) for s in sents]
# DP по позиции: стоимость = отклонение темпа речи каждого предложения от среднего
rate=(s1-s0-sum(b-a for a,b in sil)*0.5)/sum(w)
INF=1e18
# state: (i предложений закрыто, j-я пауза последняя)
dp=[[INF]*(m+1) for _ in range(n+1)]; bk=[[0]*(m+1) for _ in range(n+1)]
end_of=lambda j: s0 if j==0 else sil[j-1][1]
dp[0][0]=0
for i in range(1,n+1):
    for j in range(1,m+1):
        a=sil[j-1][0]
        best,bj=INF,0
        for k in range(0,j):
            if dp[i-1][k]>=INF: continue
            L=a-end_of(k); e=w[i-1]*rate
            c=dp[i-1][k]+((L-e)/e)**2*e - 0.6*(sil[j-1][1]-sil[j-1][0])
            if c<best: best,bj=c,k
        dp[i][j]=best; bk[i][j]=bj
# закрыть последнее предложение
fin=min(range(n,m+1),key=lambda j: dp[n][j]+(((s1-end_of(j))-w[-1]*rate)/(w[-1]*rate))**2*w[-1]*rate if dp[n][j]<INF else INF)
pick=[]; j=fin
for i in range(n,0,-1): pick.append(j); j=bk[i][j]
pick=pick[::-1]
spans=[]; prev=s0
for i in range(len(sents)):
    e = sil[pick[i]-1][0] if i<n else s1
    spans.append((prev,e))
    if i<n: prev=sil[pick[i]-1][1]
segs=[]
for p in range(len(paras)):
    idx=[k for k in range(len(sents)) if owner[k]==p]
    segs.append([round(spans[idx[0]][0],3), round(spans[idx[-1]][1],3)])
for (a,b),p in zip(segs,paras): print(f"{a:6.2f}-{b:6.2f} ({b-a:4.2f}) {p[:58]}")
json.dump({"segments":segs,"duration":dur},open(out,"w"),ensure_ascii=False,indent=1)
