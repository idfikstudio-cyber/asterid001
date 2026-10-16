# Aster3: edit iklan tuisyen (TikTok/Reels)

Status: **preview sahaja, belum render final.**

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (video asal `Aster3.mp4`, 62.3s, 1080×1920).
- `edit/edl.json`: senarai potongan. Hook (0:51.2–0:54.2) dipindah ke depan, dan 4 pause dibuang. Tempoh baru 61.5s.
- `edit/plan.json`: caption, motion graphic, sound effect dan zoom, ikut masa video baru.
- `edit/sfx/`: sound effect yang dijana sendiri (`scripts/sfx.py`), bebas hak cipta.
- `scripts/grade.sh` + `edit/keymask.png`, `edit/vigmask.png`: colour grade dan lampu muka (ffmpeg).
- `preview/index.html`: halaman preview interaktif (perlu `graded.mp4`/`orig.mp4` proxy di folder sama; tidak disimpan dalam git).

Video sumber: folder Google Drive "Aster" (tidak disimpan dalam repo kerana saiz).

# AT001: "Anak lemah sifir" (video TOFU, berasingan)

Status: **preview sahaja, belum render final.**

- `at001/edit/transcript.json`: transkrip Whisper large-v3 (28.4s, 1080×1920). "CP" → "sifir" dan "block mic" → "blok minda" disahkan dengan pass kedua.
- `at001/edit/plan.json`: 2 pause dibuang (28.1s) + kad penutup 1.5s. Caption, motion graphic, B-roll tulisan tangan, sound effect dan zoom ikut masa video baru (`scripts/at001_plan.py`).
- `at001/edit/sfx/`: sound effect dijana sendiri (`scripts/sfx.py` + `scripts/sfx_extra.py`), bebas hak cipta.
- `scripts/look.py`: bokeh f/2.8 (segmentasi badan MediaPipe setiap frame) + colour grade yang melindungi warna kulit.
- `scripts/at001_proxy.sh`: potong + bersihkan audio (−14 LUFS) + proxy 540p untuk preview.
- `at001/thumbnail/thumb.html` → `AT001_cover.png`: thumbnail 1 saat di awal video + cover TikTok (teks dalam crop grid 3:4).
- `at001/preview/index.html`: halaman preview interaktif (perlu `graded.mp4`, `orig.mp4`, `audio_orig.mp3`, `plan.json`, `sfx/` di folder sama).
