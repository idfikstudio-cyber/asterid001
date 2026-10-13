# As003: video TOFU tuisyen online (Aster Edu / Math Turbo)

Status: **preview sahaja, belum render final.**

Sumber: 2 video dari folder Google Drive "As003" (`IMG_0573.MOV` 2:01, `IMG_0575.MOV` 0:46). Tidak disimpan dalam repo kerana saiz.
Hasil: satu video 9:16, **0:52** (sasaran bawah 1:30).

- `edit/transcript_IMG_0573.json`, `edit/transcript_IMG_0575.json`: transkrip Whisper large-v3 (dengan VAD), masa setiap perkataan.
- `edit/edl.json`: take terbaik bagi setiap ayat dan susunan baru. Hook "Pokok takkan terus berbuah…" dari IMG_0575 dibawa ke depan. Pause > 0.3s dipendekkan.
- `edit/transcript_cut.json`: transkrip audio selepas potong (untuk semak potongan dan caption).
- `edit/plan.json`: caption, B-roll, motion graphic, SFX, zoom, muzik dan end card, ikut masa video baru.
- `scripts/`: `transcribe.py`, `probe.py` (semak tetingkap audio), `edl.py`, `cutaudio.py`, `grade.sh` (grade per video + key light muka), `render_base.py`, `plan.py`, `build_proxy.py` (B-roll + audio), `music.sh` (muzik dengan ducking).
- `preview/`: halaman preview interaktif. Fail proxy (`graded.mp4`, `orig.mp4`, `music.mp3`) tidak disimpan dalam git.

B-roll: Mixkit (Stock Video Free License: video sebenar, boleh guna untuk iklan, tiada kredit diperlukan). Muzik: Mixkit #22 (Stock Music Free License). SFX: dijana sendiri.
