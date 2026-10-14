# Aster3: edit iklan tuisyen (TikTok/Reels)

Status: **preview sahaja, belum render final.**

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (video asal `Aster3.mp4`, 62.3s, 1080×1920).
- `edit/edl.json`: senarai potongan. Hook (0:51.2–0:54.2) dipindah ke depan, dan 4 pause dibuang. Tempoh baru 61.5s.
- `edit/plan.json`: caption, motion graphic, sound effect dan zoom, ikut masa video baru.
- `edit/sfx/`: sound effect yang dijana sendiri (`scripts/sfx.py`), bebas hak cipta.
- `scripts/grade.sh` + `edit/keymask.png`, `edit/vigmask.png`: colour grade dan lampu muka (ffmpeg).
- `preview/index.html`: halaman preview interaktif (perlu `graded.mp4`/`orig.mp4` proxy di folder sama; tidak disimpan dalam git).

Video sumber: folder Google Drive "Aster" (tidak disimpan dalam repo kerana saiz).

## Tuisyen Online 2027 (`tuisyen2027/`)

Status: **render final siap** (`output/Aster_Tuisyen_Online_2027.mp4`, 14.4s, 1080×1920, -14 LUFS; tidak disimpan dalam git).

1. `scripts/cut.sh <src.mp4> <work>`: buang pause & take berulang (19.7s → 12.6s), colour grade, bersihkan audio.
2. `scripts/words.py`: masa perkataan untuk caption.
3. `node scripts/render.mjs <work>/frames <out>`: render `compose.html` (hook, caption, B-roll, motion graphic, end card).
4. `scripts/mix.py`: muzik latar dijana sendiri + SFX (`edit/sfx`) + ducking, kemudian ffmpeg mux.
