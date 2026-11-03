# AS-F-006_TeknikDarab Part 2 (Aster, TOFU+BOFU → gaya HYBRID hitam + kuning)

Status: **preview v1, menunggu komen Farhan.** Artifact: https://claude.ai/artifact/VXFpJ63bDwRtM1bLJPLFNy

- `plan.json`: potongan, zoom, papan kapur (Syarat 1 / Syarat 2 / Tak boleh), grafik jualan, SFX (masa sumber).
- `render.py <workdir> <scale> <out.mp4>`: 0.5 = preview 540x960, 1.0 = final 1080x1920.
  workdir: `raw.mp4`, `logo.png` (Logo SocMed Aster), `music.mp3`, `fonts/` (Poppins P600–P900, Caveat), `raw_tr.json`.
- `page.py` + `page_template.html`: halaman Artifact + RINGKASAN.txt.
- `transcript.json`: Whisper large-v3. Senarai nombor disemak dengan transkrip kedua (11, 22, 33, 44; tiada 32).
- Muzik: "Wholesome", Kevin MacLeod (incompetech.com), CC BY 4.0 — kredit wajib dalam caption.
