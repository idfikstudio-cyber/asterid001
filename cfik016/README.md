# CFik016: edit TikTok Fi-K Studio (sebutan "Fikir")

Status: **preview sahaja, belum render final.** Preview: https://claude.ai/artifact/4EuXJE9CYeZ8UHG1LKuLau

- `edit/transcript_source.json`: transkrip Whisper large-v3 video asal (3:00, 720×1280).
- `edit/edl.json` (dari `scripts/edl.py`): 9 potongan, satu take terbaik setiap ayat. Hook (0:37 asal) dipindah ke depan. Ayat "Fikir Studio, inilah fungsi, inilah kami" dibuang (tak lancar). "Fi-" tersangkut di 0:14 juga dibuang. Tempoh baru 0:35.1.
- `edit/transcript_cut.json`: transkrip semula video selepas potong (semak tiada perkataan terpotong/berulang).
- `scripts/cut.sh`: potong ikut EDL. `scripts/grade.sh` + `edit/keymask.png`: colour grade + lampu muka.
- `scripts/plan.py` → `preview/plan.json`: caption, motion graphic, slot B-roll, SFX, zoom.
- `preview/index.html`: halaman preview (perlu `graded.mp4`/`orig.mp4` proxy; tidak disimpan dalam git). SFX dari `../edit/sfx`.

Video sumber: folder Google Drive (CFik016.MOV), tidak disimpan dalam repo.
- `edit/logo/`: logo Fi-K Studio (hijau, putih). Preview guna hijau (`preview/logo-green.png`) sebab logo muncul atas dinding cerah.
- Keputusan: B-roll animasi dikekalkan, CTA DM untuk TikTok/Instagram/Facebook, tiada muzik latar, tiada end card.

## Render final
`final/FiK_Studio_TikTok_1080x1920.mp4` (tidak disimpan dalam git): 1080×1920, 30 fps, H.264 CRF 17 + AAC 192k, −13.6 LUFS.
1. Frame grade 1080×1920: `scripts/grade.sh` → `preview/_frames/%05d.jpg`
2. Lapisan grafik/caption/zoom: `node scripts/render_overlay.js http://localhost:PORT OUT 0 1051` (halaman preview dengan `?render`, setiap animasi dikawal ikut masa frame)
3. Audio: `scripts/mix_audio.py` (suara + SFX ikut `plan.json`)
