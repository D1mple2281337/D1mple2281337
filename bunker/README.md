# Бункер за 25 000 $ — серия 1

Вертикальное видео 1080×1920, ~60 с, в формате «челлендж с бюджетом и сроком»:
у героя 25 000 $ и 365 дней до апокалипсиса, чтобы построить бункер.
В конце серии развилка — зрители выбирают в комментариях: **БЕТОН** или **КОНТЕЙНЕР**.

Готовое видео: `out/bunker_ep1_fish.mp4` (актуальная версия: новости о конце света → кредит в банке → «а если не наступит?»).
`out/bunker_ep1.mp4` — первая версия с ElevenLabs и старым началом (её `timings.json` к текущему `render.py` не подходит).

## Сборка
```bash
python3 music.py audio/music.wav 62                 # фоновая музыка (синтез)
python3 align.py audio/voice_a.mp3 voice_script.txt timings.json   # тайминги абзацев
python3 sfx.py timings.json audio/sfx.wav           # звуковые эффекты
ffmpeg -i audio/voice_a.mp3 -i audio/music.wav -i audio/sfx.wav -filter_complex \
 "[0:a]aresample=44100,acompressor=threshold=-18dB:ratio=3,volume=1.6,asplit[vk][vm];[1:a]volume=0.16[m];[2:a]volume=0.45[s];[m][vk]sidechaincompress=threshold=0.05:ratio=4:release=300[md];[md][vm][s]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.95" \
 -ac 2 audio/mix.wav
ffmpeg -i audio/mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 audio/mix_norm.wav
python3 render.py --timings timings.json --audio audio/mix_norm.wav --out out/bunker_ep1.mp4
```
Озвучка: ElevenLabs, голос «Evgeniy Rybakov», модель eleven_v4 (текст — `voice_script.txt`).
Субтитры/сцены — в `SEGMENTS` в `render.py` (`*жёлтый*`, `!красный!`).

## Итог серии 1
- Участок: −4 000 $ · Котлован: −2 500 $ · Дренаж и насос: −1 500 $
- Осталось **17 000 $** и **330 дней**, бункер готов на 30 %

## Вариант с озвучкой Fish Audio (`out/bunker_ep1_fish.mp4`)
Голос «Энергичный Рассказчик» (`48ec28a45588422b977a86460c11977f`), модель `s2.1-pro-free`.
Каждый абзац озвучивается отдельно, поэтому тайминги субтитров точные (`timings_fish.json`).
```bash
FISH_MODEL=s2.1-pro-free python3 fish_tts.py voice_script.txt 48ec28a45588422b977a86460c11977f audio/fish
python3 sfx.py timings_fish.json audio/sfx_fish.wav && python3 music.py audio/music_fish.wav 57
# сведение — как выше, с audio/fish/voice.wav; затем:
python3 render.py --timings timings_fish.json --audio audio/mix_fish_norm.wav --out out/bunker_ep1_fish.mp4
```

## Серия 2 — зрители выбрали БЕТОН (`out/bunker_ep2.mp4`, обложка `out/cover_ep2.jpg`)
«В прошлой серии» → итоги голосования → сосед дядя Гена → заливка бетона → радио «удар 97 %» и письмо банка → ограбление (600 $) → запись камеры: зелёный сапог → полиция → Гена в тапочках, сапоги слишком чистые → звонок «могу помочь» → выбор: **ЗАЙМ** или **ДЯДЯ ГЕНА** + «кто вор?». ~2:20.
Паузы: `[pause N]` в конце абзаца `voice_script_ep2.txt`; общий интервал — `GAP=0.5`.
Сценарий и сцены — `ep2.py` (переиспользует `render.py`), озвучка — `voice_script_ep2.txt`.
```bash
GAP=0.5 FISH_MODEL=s2.1-pro-free TIMINGS_OUT=timings_ep2.json python3 fish_tts.py voice_script_ep2.txt 48ec28a45588422b977a86460c11977f audio/fish_ep2
python3 sfx.py timings_ep2.json audio/sfx_ep2.wav ep2 && python3 music.py audio/music_ep2.wav 143
# сведение как выше (audio/fish_ep2/voice.wav -> audio/mix_ep2_norm.wav), затем:
python3 ep2.py --timings timings_ep2.json --audio audio/mix_ep2_norm.wav --out out/bunker_ep2.mp4
python3 cover_ep2.py out/cover_ep2.jpg
```

## Серия 3 — зрители выбрали СОСЕДА (`out/bunker_ep3.mp4`, ~2:17, обложка `out/cover_ep3.jpg`)
Деньги Гены и договор на салфетке → дверь, вентиляция, еда (88 %) → ночные походы Гены, снова зелёные сапоги →
камера в бункере → **поворот 1:** вор — Гена, но он спас героя от «серьёзных людей» (10 000 $ = украденные 7 900 + пенсия) →
**поворот 2:** Гена — бывший астроном, удар через **60 дней** → 40 соседей не знают → чёрная машина, номер на 66 →
выбор: **РАССКАЗАТЬ ВСЕМ** или **МОЛЧАТЬ**.
```bash
GAP=0.5 FISH_MODEL=s2.1-pro-free TIMINGS_OUT=timings_ep3.json python3 fish_tts.py voice_script_ep3.txt 48ec28a45588422b977a86460c11977f audio/fish_ep3
python3 sfx.py timings_ep3.json audio/sfx_ep3.wav ep3 && python3 music.py audio/music_ep3.wav 140
# сведение как выше -> audio/mix_ep3_norm.wav
python3 ep3.py --timings timings_ep3.json --audio audio/mix_ep3_norm.wav --out out/bunker_ep3.mp4
python3 cover_ep3.py out/cover_ep3.jpg
```
