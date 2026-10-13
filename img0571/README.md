# IMG_0571: video TOFU "Fokus belajar" (Aster Edu)

Status: **preview sahaja, belum render final.** Video asal 2:59 (rakaman mentah dengan ambilan semula) dipotong ke 42.8 s.

- `edit/transcript.json`, `edit/chunks0.json`: transkrip Whisper large-v3 dengan masa setiap perkataan (bahagian 0:13–1:03 ditranskrip semula ikut blok).
- `scripts/edl.py` → `edit/edl.json`: ambilan terbaik setiap ayat, disusun semula (hook di depan, pengenalan dari 2:48 dipindah selepas hook), dipotong pada sempadan frame.
- `scripts/plan.py` → `edit/plan.json`: sari kata, grafik, SFX, punch-in ikut masa video baru.
- `scripts/sfx.py` → `edit/sfx/`: sound effect dijana sendiri, bebas hak cipta.
- `scripts/grade.sh`, `edit/grade_filter.txt`, `edit/vigmask.png` (`scripts/masks.py`): grade natural (warna kulit asal, kontras +4%, sharpen, vignette halus).
- `scripts/broll.py`: masukkan B-roll sebenar (Mixkit Free License, senarai dalam `edit/plan.json` → `broll`). Klip sumber tidak disimpan dalam repo.
- `scripts/proxy.py`: potong proxy 540p (graded + asal) dengan audio dibersih (−14 LUFS).
- `scripts/build_preview.py` + `preview/template.html`: halaman preview interaktif.

Video sumber: Google Drive (tidak disimpan dalam repo kerana saiz).
