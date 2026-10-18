# Aster3: edit iklan tuisyen (TikTok/Reels)

Status: **preview sahaja, belum render final.**

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (video asal `Aster3.mp4`, 62.3s, 1080×1920).
- `edit/edl.json`: senarai potongan. Hook (0:51.2–0:54.2) dipindah ke depan, dan 4 pause dibuang. Tempoh baru 61.5s.
- `edit/plan.json`: caption, motion graphic, sound effect dan zoom, ikut masa video baru.
- `edit/sfx/`: sound effect yang dijana sendiri (`scripts/sfx.py`), bebas hak cipta.
- `scripts/grade.sh` + `edit/keymask.png`, `edit/vigmask.png`: colour grade dan lampu muka (ffmpeg).
- `preview/index.html`: halaman preview interaktif (perlu `graded.mp4`/`orig.mp4` proxy di folder sama; tidak disimpan dalam git).

Video sumber: folder Google Drive "Aster" (tidak disimpan dalam repo kerana saiz).

# Sifir 9: video TOFU/BOFU (Papan tulis + AsSifir)

Status: **preview sahaja, belum render final.** Video sumber dari Google Drive (tidak disimpan dalam repo).

- `edit/sifir9/transcript_raw.json`: transkrip Whisper large-v3 video `AsSifir.mp4` (56.1s).
- `scripts/sifir9/plan.py` → `edit/sifir9/plan.json`: timeline 59.5s (video bercakap penuh + end card 3.4s), caption yang dibetulkan, peta retime papan tulis, cue grafik dan SFX.
- `scripts/sifir9/comp.py`: susun video asas (wajah penuh / papan + wajah) dengan papan di-retime ikut suara.
- `scripts/sifir9/mix.py`: audio bersih (`edit/sifir9/audio_chain.txt`), SFX, muzik latar dijana sendiri dengan ducking.
- `scripts/sifir9/sfx_extra.py` + `scripts/sfx.py` → `edit/sifir9/sfx/`.
- `edit/sifir9/grade.txt`: colour grade (kulit kekal, cast kuning dibuang).
- `preview/sifir9/index.html`: preview interaktif (perlu proxy media yang dijana oleh skrip di atas).

## Render final (Sifir 9)
1. `CRF=12 python3 scripts/sifir9/comp.py AsSifir.mp4 "Papan tulis.MP4" base_1080.mp4 graded 1080`
2. Serve `preview/sifir9/` (server yang sokong range request), kemudian `node scripts/sifir9/render_overlay.js http://localhost:PORT/index.html ov 30 4` → frame grafik telus + `zoom.json`.
3. `python3 scripts/sifir9/mix.py AsSifir.mp4 aud` dan `python3 scripts/sifir9/final.py base_1080.mp4 ov aud render/Sifir9_AsterEdu_1080x1920.mp4`.
