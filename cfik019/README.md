# CFik019: edit Fi-K Studio (Reels/TikTok 9:16)

Status: **sudah dirender** (`output/CFik019_FiK-Studio_1080x1920.mp4`, 34.2s, 1080×1920, 30fps, −14 LUFS; tidak disimpan dalam git).
Preview: https://claude.ai/artifact/WPTVJ9gTpVbvEMaKV5o7Kd

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (video asal `CFik019`, 31.1s, 1080×1920, HEVC).
- `edit/plan.json`: kapsyen, motion graphic, B-roll, SFX dan punch-in atas masa video asal. Video **tidak dipotong** (klien sudah trim). Thumbnail pilihan A 1s di depan + 31.07s video + kad penutup 2.2s; semua masa dalam plan = masa asal + 1s.
- `scripts/plan.py`: jana `plan.json` dari transkrip.
- `scripts/proxy.py` + `edit/facemask.png`, `edit/vigmask.png`: proxy preview (cut + colour grade + lampu muka + audio dibersihkan).
- `scripts/sfx.py`: SFX lembut dan pad muzik ambien, dijana sendiri (bebas hak cipta).
- `scripts/broll.py`: gambar projek siap CFik017 + logo.
- `scripts/pano.py`, `scripts/broll_pans.py`: B-roll kamera bergerak dari tur 360 aihouse Fi-K (S156754984, S160622290, S157125126, S152542130).
  Muat turun cube face: `aih_fetch.py` di scratchpad (tidak disimpan; nama klien dalam tur tidak dipaparkan).
- `preview/index.html`: halaman preview interaktif. Proxy `graded-v5.mp4` / `orig-v5.mp4` tidak disimpan dalam git.

Sumber: folder Google Drive "Konten Fi-k" (tidak disimpan dalam repo kerana saiz).

## Render final
`scripts/render_final.py` dengan langkah `assets` → `audio` → `frames` → `mux`.
Setiap frame dilukis oleh `preview/index.html#render` (kod yang sama dengan preview yang diluluskan): frame video
dimasukkan sebagai imej dan setiap animasi CSS dikunci pada masa frame itu, jadi hasilnya tepat sama dengan preview.
