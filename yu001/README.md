# YU001: iklan Yuran.my untuk guru KAFA (TikTok)

Status: **preview sahaja, belum render final.**

Video sumber dan aset ada dalam folder Google Drive "YU001-YU010" (tidak disimpan dalam git kerana saiz dan wajah murid).

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (27.9 s, 1080×1920, 30 fps).
- `edit/caps.json`: caption 1–3 perkataan + ayat penuh. Pembetulan: Kafar→KAFA, Ruga→Tugas, telikan→tally-kan, jais→JAIS.
- `edit/face_manual_boxes.json`: kotak wajah yang ditambah secara manual selepas pengesan YuNet (`scripts/faces.py`, `scripts/blur.py`).
- `scripts/look.py`: segmentasi orang (MediaPipe selfie multiclass), bokeh latar (disc blur bertopeng), colour grade dan relight muka.
- `scripts/music.py`: muzik latar asal yang dijana dengan kod (bebas lesen). SFX dijana oleh `../scripts/sfx.py`.
- `preview/template.html`: halaman preview interaktif; `__DATA__` diganti dengan `edit/caps.json`.

B-roll (Pexels, lesen komersial percuma): 7401908 (Al-Quran), 6700265 (kira wang), 7560165 (menulis), 6780089 (kalkulator).
