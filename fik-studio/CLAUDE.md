# DNA Editing — Fi-k Studio (v3.1)

> Ikut juga peraturan umum dalam `../CLAUDE.md`. Fail ini hanya perkara khusus Fi-k Studio.
> Folder Drive: **Konten › Fi-k Studio**
>
> **v3 (16 Nov 2026)** dikunci dari FK-F-007 "Punca Renovate Lambat Siap" yang diluluskan Farhan.
> Video contoh: https://claude.ai/artifact/5zAKQgNo7fkCJ1htsBU21t · skrip: `scripts/bokeh.py`, `fk_plan.py`, `fk_render.py`, `fk_page.py`.
> **v3.1:** digabung dengan peraturan B-roll terperinci (folder, padanan ayat, aliran cerita, Render 3D AIHouse).
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

Sumber: **Konten › Fi-k Studio › B-ROLL**. **Hanya B-roll projek sebenar Fi-k Studio.**

### 7.1 Prinsip utama
B-roll mesti sesuai dengan **apa yang spokesperson sedang cakap** pada ayat itu.
Baca transkrip baris demi baris, faham maksud setiap ayat, kemudian pilih B-roll dari folder
yang paling sesuai.

### 7.2 Rentak: kira-kira setiap 8 saat (v3)
- **Sasaran: satu sisipan kira-kira setiap 8 saat** supaya video tak bosan.
- Rentak 8 saat ialah sasaran, **bukan alasan untuk paksa B-roll**. Jika ayat pada titik itu tiada B-roll yang
  betul-betul sesuai, alih ke ayat sesuai yang terdekat (±3 saat) atau kekalkan spokesperson di skrin.
- **JANGAN letak B-roll pada poin penting:** hook, kad angka, tajuk poin (#1/#2/#3), "paling penting", dan CTA.
  Muka spokesperson mesti nampak pada saat itu. Jarak lebih panjang di sekitar poin penting adalah OK.

### 7.3 Maksud setiap folder
| Folder / sumber | Isi |
|---|---|
| `Projek Discussion Kontraktor` | Gambar perbincangan dengan kontraktor di tapak |
| `Video Onprogress` | Video site visit (projek masih dalam proses) |
| `Gambar Onprogress` | Gambar projek yang sedang dibina |
| `Gambar Projek Dah Siap` | Gambar projek yang sudah siap |
| `Video Projek Dah Siap` | Video projek yang sudah siap dibina |
| `Render 3D` | Klip rakaman AIHouse 720 yang sudah dirakam (`[PROJECT NUM]_[ruang].mp4`) |
| Sheet `Projek Fi-k Studio` | Senarai projek (konsep, jenis rumah, status) + link AIHouse 720 |

### 7.4 Padanan ikut apa yang spokesperson cakap
- **Hasil / projek akhir / "rumah client dah siap"** → Gambar/Video Projek Dah Siap
- **Transformasi / "dari kosong jadi cantik" / proses sampai siap** → Gambar Onprogress (1–2 shot)
  → Gambar/Video Projek Dah Siap, dengan transisi laju supaya nampak perubahan
- **Design / 3D / konsep (Japandi, Modern Lux, Farm House, dll.) / "client dapat tengok dulu sebelum bina"**
  → render 3D AIHouse (pilih projek yang konsepnya sama dalam sheet) → boleh sambung dengan Projek Dah Siap (3D → realiti)
- **Tapak / site visit / ukur / proses kerja / kabinet** → Video Onprogress, Gambar Onprogress
- **Kontraktor / harga / quotation / agreement / risiko kena tipu / masalah client** → Projek Discussion Kontraktor
- **Ayat yang tak jelas masuk kategori mana** → kekalkan spokesperson di skrin

### 7.5 Ikut aliran cerita (H.C.C.C.E / S.I.A.P.A)
| Bahagian | Visual |
|---|---|
| Hook / Isu | Spokesperson (wajib nampak muka) |
| Context / Akibat | Discussion Kontraktor, Video/Gambar Onprogress |
| Conflict | Discussion Kontraktor, Onprogress |
| Climax / Potensi | Render 3D → Projek Dah Siap |
| Ending / Action | Spokesperson + shot terbaik Projek Dah Siap, kemudian outro (Bahagian 8) |

> Untuk video Khat tanpa muka (lihat 4), "spokesperson" bermaksud shot utama video itu
> (tangan melakar / skrin AIHouse). Jangan paksa muka masuk frame.

### 7.6 Link AIHouse 720
- Buka link dari lajur **"Link AiHouse"** dalam sheet `Projek Fi-k Studio`, rakam paparan 720 bergerak
  (pan perlahan 8–12 saat setiap ruang, 9:16) dan jadikan klip B-roll.
- **Semak folder `B-ROLL › Render 3D` dulu** sebelum rakam baru.
- Klip baru disimpan dalam `B-ROLL › Render 3D` dengan nama `[PROJECT NUM]_[ruang].mp4` supaya boleh
  guna semula. Ini **tambah fail baru sahaja** — jangan padam, pindah atau tulis ganti fail sedia ada
  dalam `B-ROLL/` (ikut peraturan umum).

### 7.7 Peraturan teknikal
- Skrin penuh 9:16 (crop/reframe tanpa herot), crossfade 0.15 s, whoosh lembut. Audio spokesperson berterusan
  bawah B-roll (B-roll tutup visual sahaja).
- Video B-roll: ambil bahagian paling stabil dan menarik, **1.5–3 saat** setiap potongan.
- Gambar statik: **1.5–2.5 saat** setiap satu, dengan zoom/pan perlahan (Ken Burns). Jangan biar statik kaku.
- **Jangan ulang fail B-roll yang sama** dalam satu video.
- Elak klip resolusi rendah (contoh `IMG_0535.MOV` 352×640) jika ada pilihan lain.
- Fail `.HEIC` tukar ke JPG dulu sebelum guna (salinan kerja, bukan ganti fail asal).
- **Jangan paparkan nama client atau nama firma** dalam video atau caption.

### 7.8 Dalam preview
Dalam ringkasan dan tab **Pelan edit** preview, senaraikan B-roll untuk setiap sisipan:

```
[baris skrip] → [folder / nama fail] → [sebab dipilih]
```

supaya Farhan boleh tukar mana-mana B-roll sebelum render final.

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
- [ ] B-roll ±setiap 8 s, tiada B-roll pada poin penting (hook, angka, tajuk poin, CTA)
- [ ] Setiap B-roll sepadan dengan ayat yang disebut; tiada B-roll dipaksa; tiada fail berulang
- [ ] Tiada nama client / nama firma dalam video atau caption
- [ ] Senarai `[baris skrip] → [fail] → [sebab]` ada dalam preview
- [ ] Caption 1 perkataan, kata kunci dalam kotak #304945
- [ ] Outro brand + "Design Dulu, Baru Bina" + "DM untuk keterangan lanjut"
- [ ] Tiada muzik (kecuali diminta)
