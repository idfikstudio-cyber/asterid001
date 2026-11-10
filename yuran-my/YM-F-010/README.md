# YM-F-010 Sistem Macam Mana (Yuran.my, TOFU, Farhan)

Status: **SIAP — final dirender 10/11/2026 selepas Farhan luluskan preview v1** (1080×1920, 30 fps, H.264 CRF 19, AAC 192k, −14.0 LUFS, 56.0 s). Preview: https://claude.ai/artifact/3H3vre2r4djUEvaw38A6Up

Sumber (Drive, tidak disimpan dalam git): `Konten/Yuran.my/01_RAW/2026-11-10_010_FARHAN/TOFU_SistemMacamMana.mp4`,
B-roll `DownloadDocument.mp4`, `UploadDocument.MP4`, `B-Roll Pantau Yuran.mp4`, `Apps Yuran.my.MP4`, logo `BRAND/Logo Yuran White.png`.

- `transcript.json`: Whisper large-v3, masa setiap perkataan.
- `plan.py` → `plan.json`: caption, B-roll (crop, blur data, callout), grafik, SFX, zoom pada garis masa video siap.
- `render.py <dl_dir> <out.mp4> [540|1080]`: render preview (540) atau final (1080, CRF 19, AAC 192k). Fail dalam `<dl_dir>`: raw.mp4, pantau.mp4, apps.mp4, DownloadDocument.mp4, UploadDocument.mp4, logo_white.png.
- `render_169.py <dl_dir> <out.mp4> [960|1920]`: versi melintang 16:9 (Farhan kiri, panel kanan untuk B-roll dalam bingkai telefon, kad grafik dan caption). Guna semula `render.py`.
- `notes.py` + `build_page.py <out_dir>`: halaman Artifact preview dan `_RINGKASAN.txt`.

Baris log (tambah ke `03_LOG/edit-log.csv`):

```
YM-F-010,SistemMacamMana,FARHAN,TOFU,56.0,SIAP,"Final dirender 10/11/2026 selepas Farhan luluskan preview v1 (https://claude.ai/artifact/3H3vre2r4djUEvaw38A6Up). YM-F-010_SistemMacamMana_FINAL.mp4: 1080x1920, 30fps, H.264 CRF 19, AAC 192k, -14.0 LUFS, peak -1.5 dBFS + _THUMB.png (di 02_EDITED). Fail final dihantar dalam chat Claude; perlu dimuat naik manual ke 02_EDITED (alat Drive had 4.2 MB). Video trim Farhan 53.7s, isi tidak dipotong (senyap 0.22s dibuang). Durasi 56.0s melebihi TOFU 45s. B-roll DownloadDocument (admin hantar dokumen) & UploadDocument (app ahli download) atas permintaan Farhan + Pantau Yuran + Apps Yuran.my; nama/no. pelajar, nama sekolah, jumlah RM individu diblur. Caption 'E-sijil', 'cerita dengan ni', CTA end card TOFU dan angka dashboard demo diterima seperti preview. Tiada muzik (MUSIC/ tiada). Tiada rujukan-gaya (Farhan setuju). Font Inter ganti Acumin Pro."
```
