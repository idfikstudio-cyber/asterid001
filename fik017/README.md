# CFik017: video handover Fi-K Studio (Reels/TikTok 9:16)

Status: **preview sahaja, belum render final.**

Bahan sumber (tidak disimpan dalam git): folder Drive projek CFik017 (gambar sebelum/selepas, `Client Respon.MOV`), folder logo (`Logo Green.png`, `Logo White.png`). `CFik016.MOV` ialah konten lain dan tidak dipakai, render 3D aihouse `S50330334` (cube map `show_{f,b,l,r,u,d}.jpg`).

- `scripts/clean.py`: clean warna sahaja (neutral WB maks 6%, levels). Tiada grade. Log dalam `edit/clean_log.json`.
- `scripts/plan.py` → `edit/plan.json` (argumen transkrip tidak lagi digunakan): timeline 49.5 s tanpa voiceover, teks atas skrin, babak, cue SFX.
- `scripts/sfx.py`, `scripts/music.py`: SFX dan muzik dijana sendiri (bebas hak cipta).
- `scripts/media.py`: proxy video klien ikut timeline, mix muzik + SFX ±−16 LUFS.
- `preview/index.html`: preview interaktif (perlukan `img/`, `pano/`, `vid/`, `mix.mp3`, `plan.json` di folder sama).
