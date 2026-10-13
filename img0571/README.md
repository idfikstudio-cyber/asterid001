# IMG_0571: video TOFU "Fokus belajar" (Aster Edu)

Status: **diluluskan, render final 1080×1920.** Video asal 2:59 (rakaman mentah dengan ambilan semula) dipotong ke 42.8 s.

- `edit/transcript.json`, `edit/chunks0.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (bahagian 0:13–1:03 ditranskrip semula ikut blok).
- `scripts/edl.py` → `edit/edl.json`: ambilan terbaik setiap ayat, disusun semula (hook di depan, pengenalan dari 2:48 dipindah selepas hook), dipotong pada sempadan frame.
- `scripts/plan.py` → `edit/plan.json`: sari kata, grafik, SFX, punch-in ikut masa video baru.
- `scripts/sfx.py` → `edit/sfx/`: sound effect dijana sendiri, bebas hak cipta.
- `scripts/grade.sh`, `edit/grade_filter.txt`, `edit/vigmask.png` (`scripts/masks.py`): grade natural (warna kulit asal, kontras +4%, sharpen, vignette halus).
- `scripts/broll.py`: masukkan B-roll sebenar (Mixkit Free License, senarai dalam `edit/plan.json` → `broll`). Klip sumber tidak disimpan dalam repo.
- `scripts/proxy.py`: potong proxy 540p (graded + asal) dengan audio dibersih (−14 LUFS).
- `scripts/build_preview.py` + `preview/template.html`: halaman preview interaktif.

Video sumber: Google Drive (tidak disimpan dalam repo kerana saiz).

## Render final
1. `scripts/grade.sh` (atau filter dalam `edit/grade_filter.txt`) → master graded 1080×1920.
2. `scripts/build_preview.py` → halaman preview; layankan dengan `python3 -m http.server`.
3. `node scripts/render_overlay.js http://localhost:PORT/index.html ovdir 42.776`: grafik + sari kata sebagai PNG telus (mod `#render` dalam halaman yang sama dengan preview).
4. `scripts/final.py`: potong, punch-in (zoompan, keyframe sama dengan preview), B-roll, overlay, SFX → MP4 H.264 + AAC.
