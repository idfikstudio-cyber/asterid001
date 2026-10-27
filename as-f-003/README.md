# AS-F-003 SoalanMath (Aster · TOFU+BOFU · Farhan)

Status: **preview sahaja, belum render final.** Video sumber dan b-roll ada dalam Drive (Konten › Aster), tidak disimpan dalam git.

- `transcript.json`: transkrip Whisper large-v3 (masa setiap perkataan) bagi `01_RAW/2026-10-27_FARHAN/AS-F-003_SoalanMath.mp4`.
- `build.py` → `timeline.json`: EDL (hanya senyap >0.3 s dibuang; footage sudah ditrim), caption, grafik, SFX, punch-in, peta masa b-roll iPad.
- `overlay.html` + `render_overlay.js`: lapisan grafik (gaya HYBRID hitam + kuning) dirender sebagai PNG lutsinar setiap bingkai.
- `compose.py`: gabung talking head (grade + punch-in), skrin terbelah dengan `B-ROLL/AS-F-003_Broll_SoalanMath.MP4`, dan lapisan grafik.
- `audio.py`: potong ikut EDL, denoise ringan, kompres, SFX (`../edit/sfx`), -14 LUFS.
- `gen_page.py` + `page_template.html`: halaman preview (Artifact) dan `RINGKASAN.txt`.

Render final (selepas diluluskan): `render_overlay.js … 1080 30`, kemudian `compose.py … 1080 out.mp4 19`.
