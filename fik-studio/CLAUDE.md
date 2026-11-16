# DNA Editing — Fi-k Studio (v3)

> Ikut juga peraturan umum dalam `../CLAUDE.md`. Fail ini hanya perkara khusus Fi-k Studio.
> Folder Drive: **Konten › Fi-k Studio**
>
> **v3 (16 Nov 2026)** dikunci dari FK-F-007 "Punca Renovate Lambat Siap" yang diluluskan Farhan.
> Video contoh: https://claude.ai/artifact/5zAKQgNo7fkCJ1htsBU21t · skrip: `scripts/bokeh.py`, `fk_plan.py`, `fk_render.py`, `fk_page.py`.
> Jika fail ini bercanggah dengan `../CLAUDE.md`, **ikut fail ini.**

---

## 1. Brand & rasa

**Fi-k Studio**, studio interior design di Selangor.
- Tagline dalam video: **"Design Dulu, Baru Bina"** (ganti "We Design, You Build." dalam semua video baru).

- **Tenang, premium, pakar, mesra.** Rasa nasihat dari kawan yang memang pakar, bukan iklan yang menjerit.
- **Human touch.** Brand menekankan design dibuat manusia. JANGAN guna visual AI-generated atau stock footage yang berpura-pura jadi projek kami.
- Kemas dan bersih, bukan sarat efek.

---

## 2. Aset brand (folder `BRAND/`)

Baca `BRAND/warna.txt`. Ringkasan:
- Warna utama: **#304945** (hijau gelap), putih **#FFFFFF**, hitam **#000000**
- Highlight caption: kotak **#304945** dengan teks putih
- Logo: `Logo Green.png` (latar cerah), `Logo White.png` (latar gelap / atas video)
- **Outro: `Outro Potrait.mp4`** (1080×1920, animasi logo atas latar putih). Lihat Bahagian 8.
- Rujukan: `Brand Guideline Fi-k Studio.png`
- **Video rujukan gaya:** `BRAND/rujukan video/Apa beza Kontraktor, Arkitek dan Interior Design.mp4`
- Font: belum ditetapkan dalam guideline. Guna **Montserrat** (Black untuk caption & hook, ExtraBold untuk tajuk poin, SemiBold untuk label/tagline).
- Jangan ubah warna, bentuk atau perkadaran logo. Jangan tambah shadow.

---

## 3. Penamaan fail

- Khat: `FK-K-001_<topik>.mp4`
- Farhan: `FK-F-001_<topik>.mp4`

---

## 4. Spokesperson

### Khat (Lead Interior Designer) — `FK-K-*`
- Pertama kali buat video; ramai video tanpa muka atau separuh muka: tangan melakar, screen record AIHouse, voiceover.
- Footage tangan/skrin: zoom perlahan (Ken Burns 100% → 108% sepanjang klip).
- **Jangan crop atau zoom yang memaksa muka masuk frame** jika dia tiada dalam shot.
- Thumbnail 1 saat: jika tiada muka Khat, guna frame lakaran/3D terbaik + teks hook.
- Rasa: lembut, teliti, pakar.
- Label kecil sekali di awal isi (selepas thumbnail, ±3 saat): "Khat · Lead Interior Designer".

### Farhan (Founder) — `FK-F-*`
- Kebanyakan talking head.
- Rasa: tegas, bertenaga, macam abang yang pesan supaya jangan kena tipu kontraktor.
- Label kecil sekali di awal isi (pil hijau #304945, kiri atas, ±3 saat): "Farhan · Founder Fi-k Studio".

---

## 5. Rupa video talking head (WAJIB, v3)

### 5.1 Bokeh halus — latar MESTI masih nampak
- Kaburkan latar dengan **halus**, bukan bokeh tebal. Bokeh tebal nampak "fake" (ditolak Farhan dalam v1).
- Cara (`scripts/bokeh.py`, argumen `RAD=8 SHARP=0.35`):
  - Segmentasi orang setiap frame (MediaPipe selfie multiclass), topeng dilicinkan antara frame.
  - Blur cakera kecil (jejari ±8 px @1080p), **berperingkat ikut jarak dari badan**: dekat badan kurang kabur, jauh lebih kabur.
  - Tepi badan dilembutkan (feather) supaya tak nampak "cut-out". Grain sangat halus.
- Subjek dijernihkan sedikit: denoise ringan + sharpen lembut (0.35). Jangan over-sharpen.
- Semak: rak, panel, pokok di latar masih boleh dikenal.

### 5.2 Motion zoom pada muka (ganti punch-in lompat)
- **Zoom in perlahan** sepanjang satu ayat, **zoom out perlahan** pada ayat seterusnya: 100% ↔ 114%, ease in/out.
- Pusat zoom ikut **muka yang dijejak setiap frame** (MediaPipe face detector), dilicinkan ±1 saat supaya tak goyang.
- Mata kekal di sepertiga atas frame.

### 5.3 Colour grade
- Kontras ×1.04, saturasi ×1.05, cerah +0.01. Tiada anjakan hue (kulit asli).

---

## 6. Caption & grafik (gaya video rujukan, warna brand)

### Caption
- **Satu perkataan sebaris** (perkataan ≤3 huruf boleh digabung dengan seterusnya), HURUF BESAR, Montserrat Black ±120 px @1080p.
- Putih + outline gelap nipis + **stroke luar hijau #304945**. Pop-in kecil (86% → 100%, 90 ms).
- Kedudukan ±73% tinggi frame, dalam safe zone (bukan bawah 20%, bukan jalur kanan 15%).
- **Kata kunci** dalam **kotak hijau #304945, teks putih**: angka, lambat, delay, jangan, penting, salahkan, pertama/kedua/ketiga, kabinet, tak tepat, agreement, design, settle, harga RM, "2 kali ganda", "rugi", "tertipu", "wajib", "bajet".
- Jangan papar caption yang sama dengan kad angka besar pada masa yang sama.
- Istilah yang mesti dieja betul: ID, 3D, AIHouse, kabinet, quotation, kontraktor, Design & Build, reno.
- Warna merah/pink dalam video rujukan **ditukar ke hijau #304945**.

### Thumbnail / hook (1 saat)
- Pilih frame yang menyokong hook (contoh: Farhan tunjuk 3 jari untuk "3 PUNCA").
- Teks hook besar Montserrat Black **hijau #304945 + stroke putih tebal + bayang lembut**, 2 baris (baris 1 besar, contoh "3 PUNCA"; baris 2 lebih kecil, contoh "RENO LAMBAT SIAP"), bahagian bawah-tengah (±70–80% tinggi), tidak tutup muka atau tangan.

### Grafik
- **Tajuk poin** (kotak hijau #304945, teks putih, ExtraBold, kiri atas): "#1 …", "#2 …", "#3 …", "PALING PENTING". Kekal sepanjang poin itu diterangkan.
- **Angka besar** 1–2 saat di tengah dada (hijau #304945 + stroke putih), tepat seperti disebut (contoh "3 PERKARA", "SEMINGGU DUA", "3 MINGGU").

### SFX & muzik
- SFX sedikit dan lembut sahaja: "pop" lembut pada angka, "whoosh" lembut pada B-roll (dijana sendiri).
- **Tiada muzik latar** (ditetapkan Farhan) melainkan diminta.

---

## 7. B-roll

- **Hanya B-roll projek sebenar Fi-k Studio** dari `B-ROLL/` (Video Onprogress, Video Projek Dah Siap, Projek Discussion Kontraktor, dll.).
- **Sisip kira-kira setiap 8 saat** supaya video tak bosan. Setiap sisipan ≤3 saat, skrin penuh, crossfade 0.15 s, suara terus berjalan.
- **JANGAN letak B-roll pada poin penting:** hook, kad angka, tajuk poin (#1/#2/#3), "paling penting", dan CTA. Muka spokesperson mesti nampak pada saat itu. Jarak lebih panjang di sekitar poin penting adalah OK.
- Padankan dengan ayat (projek ongoing, kabinet/ukuran, dokumen/agreement, projek siap, design).
- Elak klip resolusi rendah (contoh `IMG_0535.MOV` 352×640) jika ada pilihan lain.

---

## 8. Penutup (outro)

- Guna **`BRAND/Outro Potrait.mp4`** sebagai penutup (ganti end card statik).
  - Guna **4.0 saat pertama sahaja** (frame 0–120): selepas itu fail hanya skrin putih kosong.
  - Crossfade 0.25 saat dari frame terakhir isi ke outro.
- Selepas wordmark statik (±1.85 s dalam outro), teks muncul perlahan di bawah wordmark (pusat x ≈ 569):
  - Tagline: **"Design Dulu, Baru Bina"** (Montserrat SemiBold, hijau #304945)
  - CTA: kotak hijau #304945, teks putih: **"DM untuk keterangan lanjut"**
- **CTA cukup "DM untuk keterangan lanjut"** untuk TOFU dan BOFU, kecuali Farhan minta lain.
- Caption TikTok juga ditutup dengan "DM untuk keterangan lanjut".

---

## 9. Semakan khas Fi-k Studio

- [ ] Tiada visual AI atau stock footage menyamar projek kami
- [ ] Label spokesperson betul (Khat / Farhan)
- [ ] Muka Khat tidak dipaksa masuk frame
- [ ] Bokeh halus, latar masih jelas nampak, tepi badan tak nampak cut-out
- [ ] Motion zoom in/out lancar, berpusat pada muka
- [ ] B-roll ±setiap 8 s, tiada B-roll pada poin penting
- [ ] Caption 1 perkataan, kata kunci dalam kotak #304945
- [ ] Outro brand + "Design Dulu, Baru Bina" + "DM untuk keterangan lanjut"
- [ ] Tiada muzik (kecuali diminta)
