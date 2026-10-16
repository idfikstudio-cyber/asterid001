# Fi-k Studio: Reel TOFU 360° (PT22 Lembah Keramat)

Sumber: tour 720° AIHouse https://www.aihouse.com/720/S50330334 (10 scene).
Link ini ialah tour 360° (gambar cubemap), bukan fail video. Jadi video ini dijana terus
daripada gambar 360° tersebut: kamera bergerak (pan/zoom) dalam setiap bilik.

Output: `FiK_TOFU_360_Reel.mp4`, 1080×1920, 30fps, 41s, H.264 + AAC (−14 LUFS).
Fail video tidak disimpan dalam git (`*.mp4` di-ignore).

## Struktur video (kenapa ia "interaktif")

| Masa | Babak | Elemen penglibatan |
|---|---|---|
| 0–3.4s | **Hook**: "SEBELUM RENOVATE... Tengok dulu rumah anda siap, dalam 3D" | Ikon drag 360° (beri rasa macam boleh pusing sendiri) |
| 3.4–12.2s | Guest Area → Living | Hotspot berdenyut ikut objek (gaya tour 360°): partition slat, feature wall TV |
| 12.2–16.8s | **POLL A/B**: Ruang Makan vs Dapur Island | "KOMEN A atau B" + bar masa mengira detik |
| 16.8–31.4s | Dining → Dry Kitchen → Wet Kitchen → Bathroom | Hotspot setiap bilik + bar progress 6 bilik di atas |
| 31.4–35s | "Semua ini dirancang dalam 3D SEBELUM satu bata pun diubah." | Mesej nilai: nampak hasil dulu, keputusan lebih yakin |
| 35–41s | **CTA**: FI-K STUDIO · Interior Design & Build · **KOMEN "360"** | Comment-to-DM (algoritma suka komen) + "Simpan video ni" |

Muzik dan SFX dijana sendiri (`scripts/mix.py`, `edit/sfx/`), jadi bebas hak cipta.
Lagu asal dalam tour AIHouse (`videoplayback.mp4`) **tidak** digunakan kerana sumbernya tidak jelas.

## Caption cadangan (IG / TikTok / FB)

> Sebelum hancurkan dinding, tengok dulu rumah anda **siap**, dalam 3D 360° 👀
>
> Ini projek PT22 Lembah Keramat: guest area, living, dining, dapur kering + basah, bilik air.
> Semua dirancang dalam 3D dulu, jadi tuan rumah nampak hasil akhir sebelum kerja bermula.
>
> 👉 Kalau rumah anda, mana nak reno dulu? **Komen A (ruang makan) atau B (dapur)**
> 👉 Nak pusing sendiri tour 360° penuh? **Komen "360"**, kami DM link.
>
> #interiordesign #designandbuild #renovasirumah #rekaanrumah #hiasanrumah #renorumah
> #interiormalaysia #3Drender #rumahteres #idearumah #FiKStudio

## Balasan DM untuk orang yang komen "360"

> Hai! Terima kasih komen 😊 Ni link tour 360° penuh projek PT22 Lembah Keramat:
> https://www.aihouse.com/720/S50330334
> Boleh drag untuk pusing & klik anak panah untuk masuk bilik lain.
> Kalau nak rumah anda pun dirancang dalam 3D macam ni, boleh share sikit: jenis rumah & kawasan mana?

(Gunakan auto-reply ManyChat/IG atau balas manual. Soalan terakhir itu yang tolak lead ke MOFU.)

## Tips posting

- Pin komen sendiri: "A atau B? 👇 Komen 360 untuk tour penuh".
- Balas setiap komen A/B dengan soalan susulan (contoh: "B! Dapur sekarang jenis apa?"). Ini naikkan reach.
- Tambah voiceover sendiri kalau mahu (lebih personal). Muzik sudah dicampur perlahan, VO boleh atas.
- Siri: setiap projek baru = format sama, tukar link tour sahaja.

## Render semula

```bash
# 1. muat turun cubemap (f,b,l,r,u,d) setiap scene ke <dir>/<scene>/  (lihat SCENES di bawah)
# 2. preview (setiap 15 frame, jpg kecil)
python3 tofu/scripts/render.py <dir> <out_dir> --preview
# 3. render penuh + audio
python3 tofu/scripts/render.py <dir> video_noaudio.mp4
python3 tofu/scripts/mix.py video_noaudio.mp4 edit/sfx FiK_TOFU_360_Reel.mp4
```

Perlu: ffmpeg, Python 3 + numpy, pillow, opencv-python-headless.
Shot, masa, sudut kamera, teks hotspot: semua dalam `SHOTS` / `ROOMS` di `tofu/scripts/render.py`.

Cubemap: `https://ai-render1.3vjia.com/UpFile_Render/C00000022/DesignSchemeRenderCutFile/50330334/<fileid>/show_<f|b|l|r|u|d>.jpg`

| folder | scene | fileid |
|---|---|---|
| 01_guest1 | GUEST AREA | 1fe4dff197ff436ab9e04b50da961e67 |
| 02_guest2 | GUEST AREA | 44d306a70c5140038a6aac623579e21d |
| 03_living1 | LIVING | 72c26bc9f13f44bc96d02cf38071dc5f |
| 04_living2 | LIVING | 9d522dadb7d24b7d9d5408169b91f3e6 |
| 05_dining | DINING | 76b1ce3b110947138e3a904d53ddf960 |
| 06_leisure1 | LEISURE AREA | 562a491cc2604d99a269e9c1d74019c4 |
| 07_drykitchen | DRY KITCHEN | 31bcfb0b540343cd90cbfcbaecdc23a9 |
| 08_leisure2 | LEISURE AREA | de459177b67f410ead5c6cd4ce104472 |
| 09_wetkitchen | WET KITCHEN | a8ee3af165ac4d9fa3676c90f2078ff1 |
| 10_bathroom | BATHROOM | 60155a72b65c48928e763a488b736e7b |
