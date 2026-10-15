# Aster3: edit iklan tuisyen (TikTok/Reels)

Status: **preview sahaja, belum render final.**

- `edit/transcript.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (video asal `Aster3.mp4`, 62.3s, 1080×1920).
- `edit/edl.json`: senarai potongan. Hook (0:51.2–0:54.2) dipindah ke depan, dan 4 pause dibuang. Tempoh baru 61.5s.
- `edit/plan.json`: caption, motion graphic, sound effect dan zoom, ikut masa video baru.
- `edit/sfx/`: sound effect yang dijana sendiri (`scripts/sfx.py`), bebas hak cipta.
- `scripts/grade.sh` + `edit/keymask.png`, `edit/vigmask.png`: colour grade dan lampu muka (ffmpeg).
- `preview/index.html`: halaman preview interaktif (perlu `graded.mp4`/`orig.mp4` proxy di folder sama; tidak disimpan dalam git).

Video sumber: folder Google Drive "Aster" (tidak disimpan dalam repo kerana saiz).

# Adudu1 + Adudu2: Teknik Belon Adudu (2 video berasingan)

Status: **preview sahaja, belum render final.** Preview: https://claude.ai/artifact/VumjkzERSCrszijCaYF6bx

- `edit/adudu{1,2}/transcript.json`: transkrip Whisper large-v3 (masa setiap perkataan).
- `edit/adudu{1,2}/keep.json` → `scripts/edl2.py` → `edl.json`: bahagian yang disimpan. Setiap titik potong dianjak ke senyap sebenar (masa Whisper selalu awal); `bounds` mengunci titik yang disemak dengar. `scripts/checkcuts.py` transkrip semula setiap sempadan untuk kesan perkataan terpotong.
- `edit/adudu{1,2}/edl_v1.json`: garis masa preview pertama. Masa dalam `plan_adudu.py` ditulis ikut garis masa ini dan dipetakan ke potongan semasa.
  - Adudu1 (engagement): 42.0 s → 39.1 s. Hook "Mostly anak kita tak boleh jawab" dipindah dari 0:34 ke depan; ulangan dan 6 jeda dibuang; 4.2 s kad kuiz di hujung.
  - Adudu2 (edukasi): 2:10.3 → 1:50.8. Pengisi dan ulangan dibuang; 7.6 s untuk jawapan 357 + CTA.
- `scripts/plan_adudu.py` → `edit/adudu{1,2}/plan.json`: caption, grafik, langkah B-roll papan putih, SFX dan zoom ikut masa video baru.
- `edit/grade.txt`, `edit/audio.txt`: rantaian ffmpeg untuk colour grade dan pembersihan suara (`MODEL` = RNNoise `sh.rnnn`).
- `scripts/proxy.py`: render proxy preview (crop 9:16 + grade + audio bersih). Render final guna rantaian sama pada 1080×1920.
- `scripts/sfx2.py`: SFX tambahan dijana sendiri (marker, belon pecah, chime, zap, boop).
- `preview/adudu/index.html`: halaman preview (perlu `adudu{1,2}/{plan.json,graded.mp4,orig.mp4}` dan `sfx/` di folder sama).
- `scripts/render_final.py`: render final. Halaman preview dibuka dalam mod render (`?render=adudu1`), setiap frame grafik dirakam dengan latar telus (semua animasi CSS dikunci pada masa frame), lalu ditindih pada `base.mkv` (dari `proxy.py ... 1920 final`) bersama zoom yang sama dan SFX. Output 1080×1920, 30 fps, H.264 + AAC 192k.
