# YM-F-003 Dahbayar_tapi_tiada_rekod (Yuran.my, Farhan, TOFU+BOFU)

Status: **SIAP** — final dirender 30/10/2026 selepas preview v2 diluluskan (`YM-F-003_Dahbayar_tapi_tiada_rekod_FINAL.mp4`, 1080×1920, 30 fps, H.264 CRF 19, AAC 192k, -14.0 LUFS; tidak disimpan dalam git). Halaman preview: https://claude.ai/artifact/2FxM2W16aB7TJHV3KEZEC9

- `transcript.json`: Whisper large-v3, masa setiap perkataan (video trim Farhan, 48.6 s).
- `scripts/plan.py` → `plan.json`: caption, grafik, SFX, zoom dan muzik ikut masa output (thumbnail 1 s + isi + end card 1.5 s).
- `overlay.html` + `scripts/render.js`: caption & motion graphic dirender sebagai PNG lutsinar (Playwright).
- `scripts/base.py`: grade + punch-in + thumbnail pegun. `scripts/audio.py`: denoise, muzik Mixkit dengan ducking, SFX, -14 LUFS.
- `scripts/screens.py`: frame B-ROLL sistem dengan data diblur → `assets/`.
- `scripts/page.py`: halaman preview Artifact + RINGKASAN.txt.

Render final (selepas lulus): `base.py ... 1080 1920`, `render.js plan.json <dir> 1`, overlay + `audio.py`, encode H.264 CRF 19, AAC 192k.
Muzik: Mixkit #160 "Minimal Emotion" + #33 "Motivating Mornings" (Mixkit Stock Music Free License). SFX: `scripts/sfx.py` di root.
