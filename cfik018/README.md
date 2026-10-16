# CFik018: video TOFU interior design (Fi-K Studio)

Status: **preview sahaja, belum render final.**

Sumber: `Konten Fi-k/CFik018/IMG_1472.MOV` (1:53, 720×1280) dari Google Drive. Tidak disimpan dalam repo.
Hasil: satu video 9:16, **0:47** (sasaran tidak lebih 1:00).

- `edit/transcript_IMG_1472.json`: transkrip Whisper large-v3, masa setiap perkataan.
- `edit/edl.json`: take terbaik setiap ayat, pause > 0.3s dipendekkan. Hook "Ramai hampir rugi berbelas ribu…" (take kedua).
- `edit/transcript_cut.json`: transkrip selepas potong (semakan + caption).
- `edit/plan.json`: caption, B-roll, motion graphic, SFX, zoom, muzik, end card.
- `scripts/`: `transcribe.py`, `probe.py`, `edl.py`, `cutaudio.py`, `grade.sh` (betulkan warna lampu tungsten + key light muka), `render_base.py`, `plan.py`, `build_proxy.py` (B-roll video landskap/potret + foto), `music.sh`.
- `preview/`: halaman preview interaktif. Fail proxy (`graded.mp4`, `orig.mp4`, `music.mp3`) tidak disimpan dalam git.

Logo: Logo White (watermark + end card atas hijau jenama #304945).
B-roll: Mixkit (Stock Video Free License) + foto projek Fi-K sendiri dari folder CFik017. Muzik: Mixkit #282 (Stock Music Free License). SFX: dijana sendiri.
