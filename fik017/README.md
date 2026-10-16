# CFik017: video handover Fi-K Studio (Reels/TikTok 9:16)

Status: **preview sahaja, belum render final.**

Bahan sumber (tidak disimpan dalam git): folder Drive projek CFik017 (gambar sebelum/selepas, `Client Respon.MOV`), folder logo (`Logo Green.png`, `Logo White.png`, `CFik016.MOV` = pengasas bercakap), render 3D aihouse `S50330334` (cube map `show_{f,b,l,r,u,d}.jpg`).

- `scripts/clean.py`: clean warna sahaja (neutral WB maks 6%, levels). Tiada grade. Log dalam `edit/clean_log.json`.
- `scripts/transcribe.py`: Whisper large-v3 → `edit/transcript_cfik016.json`.
- `scripts/plan.py` → `edit/plan.json`: timeline 66 s, take VO terpilih, caption, babak, cue SFX.
- `scripts/sfx.py`, `scripts/music.py`: SFX dan muzik dijana sendiri (bebas hak cipta).
- `scripts/media.py`: proxy video ikut timeline, VO dibersihkan, mix audio −16 LUFS.
- `preview/index.html`: preview interaktif (perlukan `img/`, `pano/`, `vid/`, `mix.mp3`, `plan.json` di folder sama).
