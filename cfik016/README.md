# CFik016: edit TikTok Fikir Studio

Status: **preview sahaja, belum render final.** Preview: https://claude.ai/artifact/4EuXJE9CYeZ8UHG1LKuLau

- `edit/transcript_source.json`: transkrip Whisper large-v3 video asal (3:00, 720×1280).
- `edit/edl.json` (dari `scripts/edl.py`): 11 potongan, satu take terbaik setiap ayat. Hook (0:37 asal) dipindah ke depan. Tempoh baru 0:38.5.
- `edit/transcript_cut.json`: transkrip semula video selepas potong (semak tiada perkataan terpotong/berulang).
- `scripts/cut.sh`: potong ikut EDL. `scripts/grade.sh` + `edit/keymask.png`: colour grade + lampu muka.
- `scripts/plan.py` → `preview/plan.json`: caption, motion graphic, slot B-roll, SFX, zoom.
- `preview/index.html`: halaman preview (perlu `graded.mp4`/`orig.mp4` proxy; tidak disimpan dalam git). SFX dari `../edit/sfx`.

Video sumber: folder Google Drive (CFik016.MOV), tidak disimpan dalam repo.
