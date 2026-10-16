# Thumbnail + hook: Reel TOFU PT22 Lembah Keramat

Ada 3 cover dalam `covers/`. Setiap satu ada versi 9:16 (cover Reels/TikTok) dan versi `_4x5` untuk semak
apa yang nampak di grid profil IG. Semua teks diletakkan dalam zon tengah 4:5, jadi tak terpotong.

| Cover | Teks atas gambar | Sudut psikologi | Sesuai bila |
|---|---|---|---|
| **A: Tengok Dulu** (utama) | SEBELUM RENOVATE · TENGOK DULU RUMAH ANDA SIAP DALAM 3D | Elak menyesal: "nampak dulu sebelum bayar" | Post pertama. Sama dengan hook dalam video, jadi janji cover = 3 saat pertama |
| **B: Poll A/B** | RUMAH ANDA, MANA NAK RENO DULU? komen A atau B | Pilihan mudah, mengundang komen | Untuk naikkan komen. Sesuai jadi cover video yang sama bila repost / boost |
| **C: Belum Siap** | RUMAH NI BELUM SIAP DIBINA · ini render 3D 360° | Rasa ingin tahu ("eh, ni bukan gambar sebenar?") | TikTok / FB, di mana orang scroll laju dan perlu "pattern interrupt" |

**Cadangan:** guna **A** sebagai cover utama. Simpan **B** untuk post kedua (boost atau repost minggu depan) supaya awak boleh banding mana dapat lebih komen.

## Hook teks (3 saat pertama di skrin)

Yang sudah ada dalam video:
> **SEBELUM RENOVATE...** Tengok dulu rumah anda siap, dalam 3D

Alternatif (kalau nak render versi lain, tukar teks dalam `render.py`, bahagian `# HOOK`):
1. "Rumah ni **belum siap dibina.** Ini render 3D 360°." (padan dengan cover C)
2. "Ramai menyesal lepas reno sebab **tak nampak hasil dulu.**"
3. "Nak tahu rupa rumah anda **lepas reno**, sebelum keluar duit?"
4. "Pusing 360° dalam rumah yang **belum wujud** 👀"

## Hook suara (kalau tambah voiceover)

Baca dalam 3 saat pertama, nada santai:
> "Sebelum awak pecahkan satu dinding pun, cuba tengok ni dulu. Ni rumah klien kami, siap, tapi dalam 3D."

Penutup VO (ikut CTA):
> "Nak pusing sendiri tour 360 penuh? Komen 360, saya DM link."

## Ayat pertama caption (yang nampak sebelum "...more")

Pilih satu, padankan dengan cover:
- A → "Sebelum hancurkan dinding, tengok dulu rumah anda **siap** dalam 3D 👀"
- B → "Kalau ni rumah anda, mana nak reno dulu: **A** ruang makan atau **B** dapur? 👇"
- C → "Rumah ni belum siap dibina. Semua yang awak nampak ialah render 3D 360°."

Selebihnya caption, hashtag dan balasan DM ada dalam `README.md`.

## Cara letak cover

- **Instagram Reels:** Edit cover → *Add from camera roll* → pilih fail 9:16. Kemudian semak dengan *Profile grid* preview. Bahagian `_4x5` yang akan nampak.
- **TikTok:** TikTok hanya bagi pilih frame dari video. Jadi untuk guna cover A/B/C, letak gambar cover tu sebagai frame pertama (0.1s) sebelum upload, atau guna fungsi *Upload cover* jika akaun anda ada.
- **Facebook Reels:** Thumbnail → Upload image.

## Jana semula

```bash
python3 tofu/scripts/thumbnail.py <scenes_dir> tofu/covers
```
