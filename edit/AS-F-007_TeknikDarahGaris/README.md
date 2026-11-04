# AS-F-007_TeknikDarahGaris (Aster, TOFU+BOFU)

Status: **SIAP. Final 1080x1920 dirender 4 Nov 2026** (`render.py 1.0`), dihantar terus kepada Farhan. Artifact: https://claude.ai/artifact/4ysUSXgB97DgriaW82GiW9

Struktur kerja (sama seperti scratchpad sesi): `dl/` (main.mp4, broll.mp4, face.png, badli.jpg dari Drive), `fonts/` (Poppins, Caveat), `work/`, `page/`, `scripts/`.

1. `scripts/transcribe.py work/main16.wav work/transcript.json` (Whisper large-v3, masa per perkataan)
2. `scripts/plan.py`: potongan senyap, peta B-roll ikut sebutan, zoom, caption, grafik, SFX
3. muzik: "Wholesome" Kevin MacLeod (CC BY 4.0) ditukar ke `work/music.wav`; `scripts/music.py` (muzik dijana sendiri v1) tidak lagi digunakan
4. `scripts/render.py 0.5 work/prev_v.mp4 work/thumb_540.png` (preview) atau `1.0` (final 1080x1920)
5. `scripts/audio.py work/mix.wav`: denoise, SFX, muzik + ducking, -14 LUFS / -1.5 dBTP
6. `scripts/gen_page.py v1`: halaman preview Artifact dari `page/template.html`

SFX dari `edit/sfx/`.
