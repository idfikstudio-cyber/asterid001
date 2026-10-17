# CFik019: edit Fi-K Studio (Reels/TikTok 9:16)

Status: **preview sahaja, belum render final.**
Preview: https://claude.ai/artifact/WPTVJ9gTpVbvEMaKV5o7Kd

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (video asal `CFik019`, 31.1s, 1080×1920, HEVC).
- `edit/plan.json`: potongan, kapsyen, motion graphic, B-roll, SFX dan punch-in, ikut masa video baru (30.06s + kad penutup 2.2s).
  Hook "Kalau renovation ikut agak-agak, kos meletup" (asal 0:11.4) dipindah ke depan; 6 pause pendek dibuang.
- `scripts/plan.py`: jana `plan.json` dari transkrip.
- `scripts/proxy.py` + `edit/facemask.png`, `edit/vigmask.png`: proxy preview (cut + colour grade + lampu muka + audio dibersihkan).
- `scripts/sfx.py`: SFX lembut dan pad muzik ambien, dijana sendiri (bebas hak cipta).
- `scripts/broll.py`: B-roll dari gambar "After" folder CFik017 + versi lakaran pensel + logo.
- `preview/index.html`: halaman preview interaktif. Proxy `graded.mp4` / `orig.mp4` tidak disimpan dalam git.

Sumber: folder Google Drive "Konten Fi-k" (tidak disimpan dalam repo kerana saiz).
