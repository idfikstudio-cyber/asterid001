# Jana halaman Artifact storyboard (draf) untuk video tutorial Yuran.my.
# python3 ym_storyboard_page.py <sb_out_dir> <music_mp3> <out_html>
import sys, base64, json, html

SB, MUS, OUT = sys.argv[1:4]
def b64(p, mime): return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()

# [id gambar, label, masa raw (s,e), tajuk babak, ucapan (ringkas), visual, interaktif/SFX, sumber B-roll]
SCENES = [
 ["s0_thumb", "Thumbnail", (None, None), "Cover 1 saat",
  "—", "Frame terbaik Farhan (senyum, pegang telefon) + hook besar 3 baris dalam safe zone kiri.",
  "Statik 1.0 s. Tiada logo, tiada muzik masuk lagi.", "Raw 2:30"],
 ["s1_intro", "Intro", (0.0, 20.0), "Apa yang ahli boleh buat",
  "“Saya nak tunjukkan macam mana ahli kita boleh install aplikasi Yuran.my … boleh pantau apa yang nak dibayar, terus buat pembayaran, download resit.”",
  "Talking head, punch-in 100% ↔ 112% setiap 2–3 potongan. Label “Farhan · Yuran.my” ±3 s. Tiga ikon kecil muncul satu-satu: Bayar dalam app · Pantau invois · Muat turun resit.",
  "Pop lembut × 3 ikut sebutan. Muzik cozy masuk perlahan (−24 dB).", "—"],
 ["s1b_stores", "Peranti", (20.1, 33.8), "Install ikut peranti",
  "“Kalau Android, Play Store. Kalau iOS, App Store. Kalau Huawei, Huawei App Store.”",
  "Talking head + 3 cip putih muncul tepat pada sebutan (25.5 s / 27.6 s / 29.5 s). Teks sahaja, tiada logo kedai pihak ketiga.",
  "Tick lembut setiap cip.", "—"],
 ["s2_playstore", "Langkah 1", (34.0, 39.2), "Cari Yuran.my di Play Store",
  "“Pergi sahaja bahagian Play Store, cari sahaja Yuran.my, selepas tu install sahaja.”",
  "Mod tutorial: rakaman skrin dalam kad bulat atas latar biru #2A3B8F (kabur). Pil langkah di atas. Iklan dan apl lain dalam Play Store dikaburkan.",
  "Bulatan “klik” biru #29ABE2 berdenyut pada carian → butang Install. SFX klik lembut setiap tekan.", "B-roll 0:00–0:20 (dipercepat 3×)"],
 ["s3_open", "Langkah 2", (39.3, 46.3), "Buka aplikasi",
  "“Selepas dah install, boleh sahaja pergi ke apps tu, pergi Yuran.my, masuk …”",
  "Kad skrin; zoom perlahan 100% → 115% ke butang Open, kemudian ikon apl.",
  "Bulatan pada Open → ikon Yuran.my. Klik lembut.", "B-roll 0:20–0:24"],
 ["s4_lang", "Langkah 3", (46.4, 57.2), "Allow, pilih bahasa, tambah sekolah",
  "“Allow sahaja … pilihan bahasa Melayu ataupun bahasa English. Kat sini ada bahagian tambah, add new school.”",
  "Kad skrin; potong masa menunggu. Tiga sasaran ditunjuk ikut urutan sebutan.",
  "Bulatan: Allow → ikon bahasa (🌐 dalam apl) → Add New School/Organization. Klik × 3.", "B-roll 0:24–0:58"],
 ["s5_url", "Langkah 4", (57.4, 74.2), "Masukkan URL institusi",
  "“URL ni kena minta bahagian admin … setiap institusi … kita memang sediakan URL masing-masing.”",
  "Kad skrin + kad nota kecil: “URL diberi oleh admin institusi”. Selang 3–4 s kembali ke Farhan penuh supaya tidak monoton.",
  "Bulatan pada medan URL → Continue. Pop lembut untuk kad nota.", "B-roll 0:56–1:40 (masa idle dibuang)"],
 ["s6_login", "Langkah 5", (74.3, 96.0), "Log masuk",
  "“… nama institusi … ahli boleh telefon nombor yang tertera … nombor PIC … masukkan email … tekan sahaja login.”",
  "Kad skrin. Emel, kata laluan dan nombor telefon dikaburkan. Label kecil “Nombor PIC institusi” atas kawasan kabur.",
  "Bulatan: nama institusi → nombor PIC → medan emel → Login. Klik lembut.", "B-roll 1:40–3:20 (1:44–2:56 idle dibuang)"],
 ["s7_school", "Langkah 6", (96.1, 103.3), "Pilih institusi",
  "“Bila dah login, inilah paparan institusi yang kita nak buat pembayaran.”",
  "Kad skrin. Emel di bawah nama institusi dikaburkan.", "Bulatan pada kad institusi. Klik.", "B-roll 3:24–3:36"],
 ["s8b_pip", "Langkah 7", (103.5, 111.4), "Semak invois tertunggak",
  "“Kalau ada banyak invoice yang belum bayar, yang ni akan tulis overdue …”",
  "Contoh susun atur dengan Farhan dalam bulatan kecil (PIP) kiri bawah, supaya wajah spokesperson kekal sepanjang tutorial. Avatar pengguna dikaburkan.",
  "Bulatan pada senarai Unpaid Invoices; sorotan pada label OVERDUE.", "B-roll 3:36–4:04"],
 ["s9_select", "Langkah 8", (111.5, 131.4), "Bayar satu-satu atau pukal",
  "“Ada dua cara … tekan sahaja satu dan buat pembayaran … secara pukal, tekan bahagian sini, pilih invoice … satu, dua, tiga … Make a payment.”",
  "Dua bahagian: (a) satu invois → Make Payment; (b) ikon senarai → pilih 3 invois. Lencana nombor 1-2-3 muncul serentak dengan sebutan “satu, dua, tiga”.",
  "Pop × 3 untuk lencana. Bulatan pada Make Payment.", "B-roll 4:04–4:32"],
 ["s11_bank", "Langkah 9", (131.7, 135.8), "Pilih bank & teruskan",
  "“Lepas tu, pilih bayaran … menggunakan bank apa. Then, proceed with payment.”",
  "Kad skrin; potong terus ke senarai bank.", "Bulatan: Online Banking (FPX) → bank → Proceed With Payment.", "B-roll 4:36–4:50"],
 ["s13_resit", "Resit", (136.2, 155.7), "Resit automatik",
  "“Sistem akan auto-generate receipt … Mudah kan? … anytime, anywhere … terus dapat receipt secara automatik.”",
  "Kembali ke Farhan penuh. Kata “automatik” & “resit” di-highlight biru #29ABE2. Ikon resit ringkas muncul sekali.",
  "Ding lembut pada “Mudah kan?”. Muzik naik sedikit menjelang penutup.", "Talking head"],
 ["s12_end", "End card", (None, None), "Penutup 1.5 s",
  "—", "Latar biru #2A3B8F, logo putih (tiada shadow/lutsinar), “Cara MUDAH Urus Yuran”, CTA TOFU, hello@yuran.my.",
  "Muzik fade out.", "BRAND/Logo Yuran White.png"],
]

TX = """0:00|Saya nak tunjukkan macam mana ahli kita boleh install aplikasi Yuran.my dan menggunakan aplikasi Yuran.my untuk buat pembayaran.
0:07|Dalam aplikasi Yuran.my yang kita sediakan, ahli boleh buat pembayaran melalui app sahaja.
0:12|[Bukan terdekat pembayaran]?, boleh pantau apa yang nak dibayar, boleh terus buat pembayaran dan boleh ambil resit dan download resit yang kita dah bayar.
0:20|Cara untuk install aplikasi Yuran.my, boleh pergi install apps mengikut device masing-masing.
0:25|Contoh kalau Android, Play Store. Kalau iOS, App Store. Kalau Huawei, Huawei App Store.
0:31|Macam contoh yang sekarang ni saya gunakan Android.
0:34|Pergi sahaja bahagian Play Store, cari sahaja Yuran.my, selepas tu install sahaja.
0:39|Selepas dah install, boleh sahaja pergi ke apps tu, pergi Yuran.my, masuk, kemudian ada paparan seperti ini.
0:46|Allow sahaja. Selepas dah masuk dalam apps tu, kita ada beberapa pilihan.
0:50|Sama ada nak pilihan bahasa Melayu ataupun bahasa English.
0:53|Kat sini ada bahagian tambah, add new school. Tekan sahaja bahagian add new school.
0:57|Yang ni URL ni kena minta bahagian admin. Admin kena sediakan kepada ahli apa yang kena isi di bahagian sini.
1:03|Sebabnya, setiap institusi yang menggunakan sistem Yuran.my, kita memang sediakan URL masing-masing.
1:08|Setiap institusi lain-lain lah ya, saya letakkan yang ni sistem demo lah sebab saya akan gunakan sistem demo.
1:14|Bila dah masuk, ada beberapa perkara yang kita boleh lihat.
1:17|Di bahagian sini, Sek Integrasi Demo tu, yang itu nama institusi lah ya.
1:22|Kalau ahli ada problem tentang apps, ahli boleh telefon nombor yang tertera dalam apps.
1:26|Yang itu adalah nombor PIC untuk setiap institusi.
1:30|Selepas tu masukkan email. Email ni adalah email yang berdaftar lah ya.
1:33|Selepas dah masukkan ID dan password, tekan sahaja login.
1:36|Bila dah login, inilah paparan institusi yang kita nak buat pembayaran.
1:39|Selepas kita masuk, inilah paparan untuk kita punya institusi.
1:43|Kalau ada banyak invoice yang belum bayar, yang ni akan tulis overdue-overdue semua tu lah.
1:48|Jadi, ahli boleh tengok apa sahaja yang nak kena bayar.
1:51|Kalau ahli nak buat pembayaran, ada dua cara. Satu cara adalah, buat satu-satu. Tekan sahaja satu dan buat pembayaran.
1:58|Tapi kalau ada banyak invoice dan nak buat pembayaran secara pukal ataupun banyak, tekan sahaja bahagian sini.
2:04|Pilih sahaja invoice yang nak dibayar. Satu, dua, tiga.
2:07|Kat situ ada paparan harga, hanya terus buat pembayaran sahaja. Make a payment.
2:11|Lepas tu, pilih bayaran untuk bayaran menggunakan bank apa. Then, proceed with payment.
2:16|Selepas buat pembayaran, sistem akan auto-generate receipt untuk ahli-ahli. Mudah kan?
2:21|Jadinya, ahli boleh buat pembayaran anytime, anywhere. Selagi mana [ada] internet …
2:25|… dan selepas buat pembayaran, ahli terus dapat receipt secara automatik.
2:29|Dah tak perlulah ahli minta receipt pada kita pada waktu-waktu yang kita not available.
2:34|Selamat menggunakan Yuran.my. Terima kasih."""

ASK = [
 ("Panjang video", "Ucapan sebenar ±2:36; selepas buang senyap dijangka ±2:15. Sasaran TOFU ialah 20–45 s, tetapi ini tutorial evergreen. Cadangan saya: kekalkan versi penuh (semua langkah) dan catat dalam log. Pilihan lain: tambah versi pendek ±60 s (langkah 1–5 sahaja)."),
 ("B-roll lebih 3 s", "Peraturan umum hadkan B-roll 3 s setiap sisipan. Untuk tutorial, rakaman skrin perlu jadi visual utama 34 s–2:16. Saya anggap arahan “tutorial interaktif” Farhan membenarkan ini; sahkan."),
 ("Susun atur tutorial", "Cadangan: rakaman skrin dalam kad atas latar biru + Farhan dalam bulatan PIP kiri bawah (lihat Langkah 7). Alternatif: skrin penuh tanpa PIP, selang-seli dengan Farhan penuh."),
 ("Video rujukan gaya", "Tiada fail rujukan-gaya-*.mp4 dalam BRAND/ Yuran.my. Mengikut peraturan, saya maklumkan sebelum edit. Teruskan tanpa rujukan?"),
 ("Muzik", "Folder MUSIC/ tiada dalam Konten › Yuran.my. Saya jana sendiri lagu instrumental cozy (lo-fi, 78 BPM, bebas hak cipta). Sampel di bawah. Jika ada lagu berlesen pilihan, letak dalam MUSIC/."),
 ("ID video", "Fail skrip bernama FK-F-011_… (awalan Fi-k Studio). Untuk Yuran.my saya cadang guna YM-F-011_Tutorial install Apps Yuran.my."),
 ("Data dalam B-roll", "Saya akan kaburkan emel, kata laluan, avatar, nombor telefon PIC, dan iklan/apl lain dalam Play Store. Adakah Sek Integrasi Demo dan jumlah invois (RM 1.19, RM 35.00, RM 185.00) data demo? Jika ya, jumlah boleh kekal kelihatan; jika tidak, saya kaburkan."),
 ("Ayat tidak jelas", "0:12 transkrip berbunyi “Bukan terdekat pembayaran” (mungkin “boleh semak pembayaran”?). 2:21 “Selagi mana adik internet” saya baca sebagai “selagi mana ada internet”. Sahkan caption."),
 ("Skrin resit", "B-roll berhenti di halaman “Redirecting to payment gateway”. Tiada rakaman skrin resit. Babak resit akan guna Farhan + ikon resit, kecuali ada rakaman resit tambahan."),
 ("Huawei", "Disebut “Huawei App Store”. Nama rasmi kedai ialah AppGallery. Caption ikut sebutan; cip boleh tulis “AppGallery”. Sahkan."),
]

def fmt(t):
    return "—" if t is None else f"{int(t // 60)}:{int(t % 60):02d}"

total = 155.7
rows = []
strip = []
for sid, lab, (a, b), title, say, vis, inter, src in SCENES:
    img = b64(f"{SB}/{sid}.jpg", "image/jpeg")
    tm = "0:00 · 1.0 s" if lab == "Thumbnail" else ("akhir · 1.5 s" if lab == "End card" else f"{fmt(a)}–{fmt(b)} · {b - a:.0f} s")
    kind = "tutorial" if lab.startswith("Langkah") else ("brand" if lab in ("Thumbnail", "End card") else "talk")
    rows.append(f"""<article class="scene" id="{sid}" data-kind="{kind}">
  <figure><img src="{img}" alt="Mockup {html.escape(lab)}: {html.escape(title)}" loading="lazy" width="540" height="960"></figure>
  <div class="sbody">
    <div class="shead"><span class="tag t-{kind}">{html.escape(lab)}</span><span class="time">{tm}</span></div>
    <h3>{html.escape(title)}</h3>
    <dl>
      <dt>Ucapan</dt><dd class="say">{html.escape(say)}</dd>
      <dt>Visual</dt><dd>{html.escape(vis)}</dd>
      <dt>Interaktif & SFX</dt><dd>{html.escape(inter)}</dd>
      <dt>Sumber</dt><dd class="src">{html.escape(src)}</dd>
    </dl>
  </div>
</article>""")
    w = 1.0 if a is None else (b - a)
    strip.append(f'<a href="#{sid}" class="seg k-{kind}" style="flex:{w:.1f}" title="{html.escape(lab)}: {html.escape(title)}"><span>{html.escape(lab.replace("Langkah ", "L"))}</span></a>')

tx = "".join(f'<li><span class="ts">{l.split("|")[0]}</span><span>{html.escape(l.split("|")[1]).replace("[", "<mark>").replace("]", "</mark>")}</span></li>' for l in TX.split("\n"))
ask = "".join(f'<li><h4>{html.escape(h)}</h4><p>{html.escape(p)}</p></li>' for h, p in ASK)
mus = b64(MUS, "audio/mpeg")

page = open(__file__.replace("ym_storyboard_page.py", "ym_storyboard_tpl.html")).read()
for k, v in {"{{ROWS}}": "\n".join(rows), "{{STRIP}}": "".join(strip), "{{TX}}": tx, "{{ASK}}": ask, "{{MUS}}": mus, "{{NASK}}": str(len(ASK))}.items():
    page = page.replace(k, v)
open(OUT, "w").write(page)
print(OUT, len(page) // 1024, "KB")
