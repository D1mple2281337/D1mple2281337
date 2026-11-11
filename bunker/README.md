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
