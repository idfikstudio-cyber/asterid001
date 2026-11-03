# AS-F-005_TeknikDarab Part 1 (Aster, TOFU)

Status: **preview v1, menunggu komen Farhan.** Artifact: https://claude.ai/artifact/6riWfLffZ9GNdG6RVTb8jh

- `plan.json`: potongan, zoom, skrin terbelah, padanan B-roll ikut sebutan, grafik, SFX (masa sumber).
- `render.py <workdir> <scale> <out.mp4>`: render (0.5 = preview 540x960, 1.0 = final 1080x1920).
  workdir perlu: `raw.mp4`, `broll.mp4`, `logo.png` (Logo SocMed Aster), `music.mp3`, `fonts/` (Poppins P600–P900, Caveat), `raw_tr.json`.
- `page.py` + `page_template.html`: halaman Artifact + RINGKASAN.txt.
- `transcript.json`: Whisper large-v3, masa setiap perkataan.
- Muzik: "Wholesome", Kevin MacLeod (incompetech.com), CC BY 4.0 — kredit wajib dalam caption.
