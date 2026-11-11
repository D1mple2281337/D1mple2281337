#!/usr/bin/env python3
"""Озвучка через Fish Audio по абзацам + точные тайминги.
python3 fish_tts.py voice_script.txt <voice_id> audio/fish  -> audio/fish/voice.wav, timings_fish.json
Ключ: заголовок Authorization подставляет прокси окружения (FISH_API_KEY не нужен)."""
import sys, os, re, json, subprocess, urllib.request
script, voice, outdir = sys.argv[1:4]
model = os.environ.get("FISH_MODEL", "s1")
os.makedirs(outdir, exist_ok=True)
paras = [re.sub(r"\[[^\]]*\]", "", p).strip() for p in open(script, encoding="utf-8").read().split("\n\n") if p.strip()]
GAP = 0.4
files = []
for i, p in enumerate(paras):
    fn = f"{outdir}/p{i:02d}.mp3"
    if not os.path.exists(fn):
        body = json.dumps({"text": p, "reference_id": voice, "format": "mp3", "mp3_bitrate": 192,
                           "normalize": True, "latency": "normal"}).encode()
        req = urllib.request.Request("https://api.fish.audio/v1/tts", data=body, method="POST", headers={
            "Authorization": "Bearer " + os.environ.get("FISH_API_KEY", "proxy-injected"),
            "Content-Type": "application/json", "model": model})
        with urllib.request.urlopen(req, timeout=120) as r:
            open(fn, "wb").write(r.read())
    files.append(fn)
    print("ok", i, p[:50], flush=True)
# обрезать тишину по краям, склеить с паузами, посчитать тайминги
segs, t, parts = [], 0.0, []
for i, fn in enumerate(files):
    tr = f"{outdir}/t{i:02d}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fn, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                    "-ar", "44100", "-ac", "1", tr], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tr]))
    segs.append([round(t, 3), round(t + d, 3)])
    parts.append(tr); t += d + GAP
gap = f"{outdir}/gap.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP), gap], check=True)
lst = f"{outdir}/list.txt"
with open(lst, "w") as f:
    for k, pth in enumerate(parts):
        f.write(f"file '{os.path.abspath(pth)}'\n")
        if k < len(parts) - 1: f.write(f"file '{os.path.abspath(gap)}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, f"{outdir}/voice.wav"], check=True)
json.dump({"segments": segs, "duration": t}, open("timings_fish.json", "w"), indent=1)
for (a, b), p in zip(segs, paras): print(f"{a:6.2f}-{b:6.2f} {p[:50]}")
