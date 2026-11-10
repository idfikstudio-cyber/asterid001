# YM-F-010 Sistem Macam Mana (Yuran.my, TOFU, Farhan)

Status: **Preview v1, menunggu komen Farhan.** Preview: https://claude.ai/artifact/3H3vre2r4djUEvaw38A6Up

Sumber (Drive, tidak disimpan dalam git): `Konten/Yuran.my/01_RAW/2026-11-10_010_FARHAN/TOFU_SistemMacamMana.mp4`,
B-roll `DownloadDocument.mp4`, `UploadDocument.MP4`, `B-Roll Pantau Yuran.mp4`, `Apps Yuran.my.MP4`, logo `BRAND/Logo Yuran White.png`.

- `transcript.json`: Whisper large-v3, masa setiap perkataan.
- `plan.py` → `plan.json`: caption, B-roll (crop, blur data, callout), grafik, SFX, zoom pada garis masa video siap.
- `render.py <dl_dir> <out.mp4> [540|1080]`: render preview (540) atau final (1080, CRF 19, AAC 192k). Fail dalam `<dl_dir>`: raw.mp4, pantau.mp4, apps.mp4, DownloadDocument.mp4, UploadDocument.mp4, logo_white.png.
- `notes.py` + `build_page.py <out_dir>`: halaman Artifact preview dan `_RINGKASAN.txt`.
