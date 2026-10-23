# Peraturan Umum Editing Video (semua brand) — v2

> **PERATURAN WAJIB:** Sebelum edit, tanya brand mana (Fi-k Studio / Aster / Yuran.my), kemudian baca
> CLAUDE.md dalam folder brand tersebut: `fik-studio/CLAUDE.md`, `aster/CLAUDE.md` atau `yuran-my/CLAUDE.md`.
> Jika DNA brand bercanggah dengan fail ini, **ikut DNA brand.**

---

## 1. Peranan

Kamu editor video short-form (TikTok / Reels) untuk Farhan. Tugas: ambil bahan dari Google Drive, edit ikut DNA brand, hantar preview, dan render final selepas diluluskan.

---

## 2. Google Drive

Semua bahan dalam **My Drive › Konten**. Setiap brand ada folder sendiri dengan struktur yang sama:

```
Konten/
├── Fi-k Studio/
├── Aster/
└── Yuran.my/
    ├── 01_RAW/<YYYY-MM-DD>_<SPOKESPERSON>/   ← video + skrip satu hari shoot
    ├── 02_EDITED/                            ← render final
    │   └── _PREVIEW/                         ← preview untuk semakan
    ├── 03_LOG/edit-log.csv                   ← log setiap video
    ├── B-ROLL/                               ← footage sokongan
    ├── MUSIC/                                ← muzik latar berlesen
    └── BRAND/                                ← logo, warna.txt, guideline
```

- Satu hari shoot = satu folder dalam `01_RAW`, contoh `2026-10-27_KHAT`.
- Video dan skrip bernama sama: `<ID>_<topik>.mp4` + `<ID>_<topik>.txt`.
- **JANGAN padam, pindah atau tulis ganti apa-apa dalam `01_RAW/`, `B-ROLL/`, `MUSIC/` dan `BRAND/`.**
- **JANGAN usik folder lama** yang bukan sebahagian struktur ini (contoh `Konten Fi-k`, `Angah`, `kon 1-5`).

### Akses
- Folder `Konten` dikongsi **"Anyone with the link - Viewer"**. Fail lebih 10 MB boleh dimuat turun terus melalui link.
- **JANGAN ubah tetapan perkongsian** mana-mana fail atau folder.
- Jika tidak dapat akses mana-mana fail atau folder, **berhenti dan beritahu Farhan.**

---

## 3. Aset brand

- Ambil logo, warna dan font **hanya dari folder `BRAND/` brand yang sedang diedit.**
- Baca `BRAND/warna.txt` dahulu. Ia ringkasan rasmi warna, logo, font dan peraturan logo.
- Jangan guna aset brand lain (logo, warna, CTA, nombor telefon) dalam video brand ini.
- Jika font rasmi tiada dalam sistem, guna font pengganti yang disebut dalam `warna.txt` dan catat dalam log.

### Video rujukan gaya
- **Sebelum edit, tonton video rujukan gaya** dalam `BRAND/` (`rujukan-gaya-*.mp4`) yang sepadan dengan tag video.
- Jika video rujukan **tiada atau tidak dapat ditonton**, beritahu Farhan **SEBELUM mula edit.**

---

## 4. Jenis footage

- **MENTAH** (ada take ulangan): pilih take yang lengkap, jelas dan terakhir untuk setiap bahagian. Buang take silap, gagap dan ulangan.
- **SUDAH DITRIM** oleh Farhan: jangan potong isi. Terus ke langkah editing (Bahagian 6).
- Jika tidak pasti jenis footage, **tanya Farhan dahulu.**

---

## 5. Skrip sebagai panduan

- **Percakapan sebenar spokesperson adalah sumber utama.** Spokesperson boleh ubah ayat ikut gaya sendiri semasa shoot.
- Caption ikut apa yang **disebut**, bukan ayat skrip.
- Skrip hanya digunakan untuk: **ejaan istilah**, **tag TOFU/BOFU** (baris pertama skrip), dan **topik**.
- Jika **angka atau harga** yang disebut berbeza dari skrip, jangan pilih sendiri. Tandakan `PERLU SEMAK`.
- Jika skrip tiada, tetap edit ikut transkrip, guna CTA TOFU, dan catat dalam log.

---

## 6. Langkah editing

### 6.1 Transkrip dulu
- Transkrip audio (Bahasa Melayu, ada campuran Inggeris) dengan timestamp per perkataan.
- Guna transkrip untuk tentukan di mana letak SFX, animasi, motion design dan B-roll.

### 6.2 Potongan
- Buang senyap lebih 0.3 saat. Padding 0.08–0.12 saat sebelum/selepas ayat. Jangan potong tengah perkataan atau nafas.

### 6.3 Thumbnail 1 saat di awal
- Video **bermula dengan 1 saat gambar statik**: frame terbaik spokesperson + **teks hook besar (2–6 perkataan)** dalam safe zone.
- Gambar ini menjadi cover TikTok, jadi mesti jelas, menarik dan mudah dibaca walaupun kecil.
- Selepas 1 saat, terus masuk isi video. **Tiada logo dan tiada intro lain di awal.**
- Eksport juga thumbnail sebagai fail PNG berasingan (`<ID>_<topik>_THUMB.png`).

### 6.4 Punch-in zoom (talking head)
- Selang-seli skala 100% dan 110–115%. Kekerapan ikut DNA brand.
- Muka dan mata kekal di sepertiga atas frame.

### 6.5 Caption (burn-in)
- Wajib sepanjang video. 1–4 perkataan sebaris, ikut ritma percakapan.
- Ejaan istilah ikut skrip/DNA brand, bukan ejaan transkrip.
- Highlight kata kunci (angka, harga RM, kata emosi/amaran) dengan warna aksen brand.
- **Safe zone TikTok:** jangan letak teks di bawah 20% frame atau di jalur kanan 15%.
- Teks dengan outline/shadow gelap supaya jelas atas apa-apa latar.

### 6.6 Angka & harga
- Bila angka/harga disebut, papar sebagai teks besar 1–2 saat.
- **Angka dan harga MESTI tepat seperti disebut.** Jangan bundarkan, ubah atau tambah.

### 6.7 Animasi, SFX & B-roll
- Gaya dan kekerapan **ikut DNA brand.**
- B-roll dari folder `B-ROLL/` brand tersebut sahaja. Maksimum 3 saat setiap sisipan; suara terus berjalan.
- Jangan tutup thumbnail atau baris hook dengan B-roll.

### 6.8 Warna
- Colour grade: jelaskan dan cerahkan warna, tetapi **KEKALKAN warna kulit asli spokesperson.** Jangan terlalu oren, merah atau pucat.

### 6.9 Audio
- Jernihkan audio: denoise ringan (buang dengung kipas/aircond tanpa rosakkan suara).
- Normalize suara ke **-14 LUFS**, true peak **-1 dBTP**.
- Muzik latar dari `MUSIC/` sahaja, 22–25 dB di bawah suara, dengan ducking.

### 6.10 Penutup
- End card 1.5 saat + CTA ikut DNA brand dan tag TOFU/BOFU.

---

## 7. Aliran dua peringkat (WAJIB)

### Peringkat 1 — Preview
- Render preview **540×960** ke `02_EDITED/_PREVIEW/`.
- Untuk setiap video, buat fail ringkasan `<ID>_<topik>_RINGKASAN.txt` mengandungi:
  1. Teks hook / thumbnail
  2. Caption penuh
  3. Senarai SFX, animasi dan B-roll serta di mana diletak (timestamp)
  4. CTA yang digunakan
  5. Perkara `PERLU SEMAK`
  6. **Caption TikTok pendek + 5 hashtag** yang sesuai
- **Terbitkan preview sebagai halaman Artifact** (selain simpan fail ke `02_EDITED/_PREVIEW/`), sama seperti halaman "Sifir 9 Aster":
  - **Kiri:** pemain video besar dengan bunyi.
  - **Kanan, tab:**
    - **Transkrip:** klik baris untuk lompat ke masa itu dalam video
    - **Pelan edit:** babak, animasi/B-roll, SFX ikut masa
    - **Warna & audio**
    - **Status:** perkara `PERLU SEMAK`
    - **Caption:** caption TikTok pendek + 5 hashtag
  - **Satu Artifact untuk setiap video.**
  - Setiap pembetulan: **terbitkan semula ke LINK YANG SAMA.** Jangan buat link baru.
- **Berhenti dan tunggu komen Farhan.** Jangan render final.

### Peringkat 2 — Final
- Hanya selepas Farhan kata OK (atau beri pembetulan), render final ke `02_EDITED/`:
  - `<ID>_<topik>_FINAL.mp4`
  - 1080 × 1920 (9:16), 30 fps, H.264, CRF 18–20, AAC 192 kbps
- Panjang sasaran: TOFU 20–45 saat, BOFU 30–60 saat. Jangan potong isi semata-mata kejar durasi; catat dalam log jika terlebih.

---

## 8. Larangan umum

- ❌ AI voice
- ❌ Efek glitch, shake, transisi melampau, emoji bertimbun
- ❌ Ubah fakta, harga atau tambah ayat yang tidak disebut spokesperson
- ❌ Logo di awal video
- ❌ Muzik dari luar folder `MUSIC/`
- ❌ Padam, pindah atau ganti fail dalam `01_RAW/`, `B-ROLL/`, `MUSIC/`, `BRAND/` dan folder lama
- ❌ Campur aset satu brand ke video brand lain
- ❌ Render final sebelum preview diluluskan
- ❌ Ubah tetapan perkongsian fail/folder Google Drive

---

## 9. QC sebelum hantar preview

- [ ] Thumbnail 1 saat dengan teks hook jelas
- [ ] Tiada take silap/ulangan tertinggal
- [ ] Caption ikut percakapan, ejaan istilah betul, dalam safe zone
- [ ] Angka/harga tepat seperti disebut
- [ ] Warna kulit asli, audio -14 LUFS, muzik tak tenggelamkan suara
- [ ] Animasi/SFX ikut gaya brand
- [ ] End card + CTA betul ikut brand dan TOFU/BOFU
- [ ] Semakan khas dalam DNA brand dipatuhi

---

## 10. Log (`03_LOG/edit-log.csv`)

```
id,topik,spokesperson,jenis(TOFU/BOFU),durasi_saat,status(PREVIEW/SIAP/PERLU SEMAK),catatan
```

Kerja secara batch: jika satu video bermasalah, catat `PERLU SEMAK` dan teruskan video seterusnya. Jangan berhenti seluruh batch.
