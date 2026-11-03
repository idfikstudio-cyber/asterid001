#!/usr/bin/env python3
"""Build the preview Artifact page + RINGKASAN.txt for AS-F-005.
usage: page.py <workdir> <out_dir>   (workdir must contain raw_tr.json + fonts like render.py)"""
import json, os, re, sys, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
WD, OUTD = sys.argv[1], sys.argv[2]
sys.argv = ["render.py", WD, "0.5", os.path.join(OUTD, "_unused.mp4")]
R = runpy.run_path(os.path.join(HERE, "render.py"), run_name="lib")   # reuse timeline + captions
P, s2o, CAPS, TOTAL, VEND = R["P"], R["src2out"], R["CAPS"], R["TOTAL"], R["T_VOICE_END"]
r2 = lambda x: round(x, 2)
FIXED = {"“GOOD”": "good", "Settle!": "Settle."}
REVIEW = {"Dia", "pandai"}

caps = [dict(s=r2(c["s"]), e=r2(c["e"]), w=[dict(t=w["w"], hl=bool(w.get("hot")), fix=FIXED.get(w["w"]),
        q=w["w"] in REVIEW and 18.5 < w["s"] < 19.5) for w in c["words"]]) for c in CAPS]

S = lambda t: r2(s2o(t))
seg = [[0, 1.0, "Thumbnail", "TEKNIK DARAB PANTAS! + pil DARJAH 4, 5 & 6 (frame Cikgu thumbs-up, sumber 0:39.5)"],
       [1.0, S(5.16), "Pengenalan", "Label nama Cikgu AlFarhan, kad DARJAH 4, 5 & 6"],
       [S(5.16), S(11.04), "3 soalan", "Skrin terbelah masuk: papan biru gelap (B-roll iPad), kotak kuning ikut soalan dibaca"],
       [S(11.04), S(19.5), "88 × 4", "Langkah 1: 8 × 4 = 32 · Langkah 2: 3 + 2 = 5 (papan tulis 352 serentak)"],
       [S(19.5), S(27.48), "99 × 2", "CTA Follow saya (tengah video) · 9 × 2 = 18 · 8 + 1 = 9"],
       [S(27.48), S(35.40), "66 × 5", "6 × 5 = 30 · 3 + 0 = 3 · Settle! (tanda semak)"],
       [S(35.40), S(38.94), "Ada syarat", "Kembali skrin penuh, nota kertas 'Teknik ni ada SYARAT!'"],
       [S(38.94), VEND, "Komen & Part 2", "Bubble komen TikTok 'Comment GOOD', kad NANTI PART 2"],
       [VEND, TOTAL, "End card", "Follow untuk tips belajar anak seterusnya + asteredu11.com.my + WhatsApp"]]

mg = [[0, 1.0, "Thumbnail", "TEKNIK DARAB / PANTAS! + DARJAH 4, 5 & 6"],
      [0, TOTAL, "Watermark", "asteredu11.com.my sepanjang video, putih ±70% + bayang halus, atas-kiri 13%"],
      [S(P["name_label"][0]), S(P["name_label"][1]), "Label nama", "Cikgu AlFarhan"],
      [S(P["darjah_card"][0]), S(P["darjah_card"][1]), "Kad angka", "DARJAH 4, 5 & 6"],
      [S(5.16), S(35.40), "Skrin terbelah", "Papan 'Teknik Darab' (B-roll iPad, latar biru gelap) atas, Cikgu bawah, jalur kuning + label TEKNIK DARAB · CIKGU ALFARHAN"]]
for r in P["row_flash"]:
    mg.append([S(r["t0"]), S(r["t1"]), "Kotak soalan", ["88 × 4", "99 × 2", "66 × 5"][r["row"]]])
for L in P["langkah"]:
    mg.append([S(L["t0"]), S(L["t1"]), f"Langkah {L['n']}", f"{L['eq']} = {L['res']} (jawapan muncul {S(L['tres']):.2f})"])
for sp, eq in zip(P["plus_arrows"], ["3 + 2 → 5 (tengah 352)", "1 + 8 → 9 (tengah 198)", "3 + 0 → 3 (tengah 330)"]):
    mg.append([S(sp["t_first"]), S(sp["t1"]), "Anak panah +", f"Bulatan + anak panah dari dua digit luar ke ruang tengah, lencana + : {eq}"])
mg += [[S(P["follow_cta"][0]), S(P["follow_cta"][1]), "CTA Follow", "Wajah bulatan emas + Follow saya + @aster.edu_tpg"],
       [S(P["syarat_note"][0]), S(P["syarat_note"][1]), "Nota kertas", "Teknik ni ada SYARAT! + ikon amaran"],
       [S(P["comment_bubble"][0]), S(P["comment_bubble"][1]), "Bubble komen", "@aster.edu_tpg · Comment “GOOD” di ruangan komen"],
       [S(P["part2_card"][0]), S(P["part2_card"][1]), "Kad", "NANTI PART 2 ▸"],
       [VEND, TOTAL, "End card", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA Follow, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
mg.sort(key=lambda m: m[0])
sfx = [[r2(s2o(t) if b == "s" else t), n] for t, n, g, b in P["sfx"]]
broll = [[S(m["s0"]), S(m["s1"]), m["b0"], m["b1"]] for m in P["broll_map"]]

zoom = []
for t, z in P["zoom_full"]:
    if not (5.16 <= t < 35.40): zoom.append(dict(t=S(t), m={"1.0": "100% (skrin penuh)", "1.1": "110%", "1.22": "122% punch-in"}[z]))
for t, z in P["zoom_split"]:
    zoom.append(dict(t=S(t), m=f"Skrin terbelah {int(round(z*100))}%"))
zoom.sort(key=lambda x: x["t"])

DONE = [
 ["v2: tali di atas frame dibuang", "Jalur/tali tergantung di bahagian atas dinding (bergoyang sedikit) dipadam pada setiap frame: kawasan itu dibina semula dari warna dinding di kiri-kanannya, dengan tepi lembut. Termasuk thumbnail.", 4.5],
 ["v2: thumbnail jadi satu blok tajuk", "Pil DARJAH 4, 5 & 6 kini terus di bawah PANTAS! (tidak lagi jauh di bawah).", 0.3],
 ["v2: jalan kira + untuk digit tengah", "Setiap contoh: bila Cikgu sebut 'tambah', dua digit luar dibulatkan, anak panah melengkung ke ruang tengah dan lencana + muncul. 88 × 4: 3 + 2 → 5 · 99 × 2: 8 + 1 → 9 · 66 × 5: 3 + 0 → 3. Anak panah ikut urutan sebutan Cikgu.", S(16.14)],
 ["Jenis footage: sudah ditrim", "Satu take bersih tanpa ulangan, jadi isi tidak dipotong. 3 senyap pendek (0.30–0.35 s) dipendekkan, dilindungi pertukaran zoom. 42.9 s → 42.5 s isi.", S(11.8)],
 ["Gaya ikut rujukan TOFU+BOFU_Sifir9", "Skrin terbelah: papan atas (tajuk tulisan tangan 'Teknik Darab', pil LANGKAH 1/2, penanda baris kuning) dan Cikgu di bawah, jalur kuning + label siri. Warna TOFU Aster: biru gelap + kuning (latar hitam iPad ditukar ke biru gelap).", S(13.0)],
 ["B-roll dipadan dengan sebutan", "B-Roll-AS-F-005 (rakaman iPad 1:57) dipotong dan dipercepat supaya setiap coretan muncul tepat bila Cikgu sebut: lengkung, 32, 5, garis bawah, 18, 9, 30, 3, tanda semak. Bar status iPad dan tarikh dipotong keluar.", S(13.24)],
 ["Muzik latar berlesen", "“Wholesome”, Kevin MacLeod (incompetech.com), lesen CC BY 4.0: piano/akustik ceria, sesuai keluarga. 23 dB di bawah suara semasa bercakap; naik pada thumbnail dan end card.", 2.0],
 ["Angka tepat seperti disebut", "88 × 4, 99 × 2, 66 × 5, 8 × 4 = 32, 3 + 2 = 5, 9 × 2 = 18 (disebut '1, 8'), 8 + 1 = 9, 6 × 5 = 30, 3 + 0 = 3 (disebut 'kosong'). Darjah 4, 5 dan 6.", S(11.04)],
 ["CTA Follow tengah video", "Wajah dalam bulatan emas + Follow saya + @aster.edu_tpg pada ±0:20 (TOFU).", S(19.5)],
 ["Wajah, bukan logo", "Bulatan emas guna Logo SocMed Aster. Tiada Logo Rasmi Aster / ASTER EDU, tiada aset Fi-k Studio atau Yuran.my.", TOTAL - 1.0],
 ["Watermark & safe zone", "asteredu11.com.my sepanjang video termasuk thumbnail dan end card. Semua teks di atas 80% frame dan di luar jalur kanan 15%.", 3.0],
 ["End card TOFU", "Wajah bulatan emas + Cikgu AlFarhan + @aster.edu_tpg, CTA 'Follow untuk tips belajar anak seterusnya', asteredu11.com.my besar, WhatsApp 011-5596 9070.", TOTAL - 0.7],
 ["Durasi 45.0 s", "Dalam sasaran TOFU 20–45 s (thumbnail 1 s + isi 42.5 s + end card 1.5 s).", None],
]
TODO = [
 ["Muzik dari luar folder MUSIC/", "Ikut arahan sesi: MUSIC/ kosong, jadi saya pilih “Wholesome” oleh Kevin MacLeod (incompetech.com), lesen Creative Commons BY 4.0 (boleh guna komersial, WAJIB beri kredit). Kredit sudah dimasukkan dalam caption TikTok. Jika lulus, cadang simpan trek ini dalam MUSIC/ untuk rujukan (saya tidak boleh muat naik 14 MB melalui connector).", 2.0],
 ["\"Dia pandai\" (0:19.7)", "Whisper dengar 'Dia pandai'; transkrip kedua dengar lain ('Jepang dia'). Sila dengar dan sahkan caption ini.", S(18.82)],
 ["B-roll lebih 3 saat", "Peraturan umum: B-roll maks 3 s setiap sisipan. Di sini papan tulis dipapar ±30 s sebagai skrin terbelah (Cikgu kekal di separuh bawah, suara berterusan), ikut rujukan TOFU+BOFU_Sifir9 dan AS-F-003 yang diluluskan. Sahkan gaya ini OK.", S(5.16)],
 ["\"9\" disebut dua kali (0:27.9)", "'8 tambah 1, 9. 9, 66 × 5' — caption ikut sebutan.", S(27.06)],
 ["End card tanpa logo rasmi", "Rujukan Sifir9 guna logo segitiga Aster di end card, tetapi DNA Aster larang Logo Rasmi Aster. Saya ikut DNA: wajah dalam bulatan emas.", TOTAL - 1.0],
 ["Nota 'Masalah Sebenar' tidak dipakai", "Video ini tiada masalah ibu bapa disebut. Gantinya nota kertas 'Teknik ni ada SYARAT!' (disebut Cikgu) dalam gaya kertas nota TOFU.", S(36.14)],
 ["Fail video tidak dapat dimuat naik ke Drive", "Connector Drive tidak boleh muat naik video/PNG sebesar ini. RINGKASAN.txt sudah disimpan dalam 02_EDITED/_PREVIEW/; video preview dan thumbnail ada dalam halaman ini.", None],
]
TT = ("Teknik darab pantas untuk anak Darjah 4, 5 & 6 ✏️ Cuba 88 × 4, 99 × 2 dan 66 × 5 dengan anak malam ni. "
      "Teknik ni ada syarat tau, comment GOOD untuk Part 2 👇\n\nMuzik: “Wholesome” Kevin MacLeod (incompetech.com), CC BY 4.0")
HS = "#cikgualfarhan #teknikdarab #matematik #sekolahrendah #asteredu"

DATA = dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=r2(TOTAL), broll=broll)
tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf8").read()
js = lambda o: json.dumps(o, ensure_ascii=False)
html = (tpl.replace("__DATA__", js(DATA)).replace("__SEG__", js(seg)).replace("__DONE__", js(DONE))
        .replace("__TODO__", js(TODO)).replace("__TT__", js(TT)).replace("__HS__", js(HS)).replace("__DUR__", f"{TOTAL:.1f}"))
open(os.path.join(OUTD, "index.html"), "w", encoding="utf8").write(html)

# ---------- RINGKASAN.txt ----------
fmt = lambda t: f"{int(t//60)}:{t%60:04.1f}"
L = ["AS-F-005_TeknikDarab Part 1 — RINGKASAN PREVIEW", f"Aster · TOFU · spokesperson FARHAN · durasi {TOTAL:.1f} s · preview 540x960", "",
     "1. TEKS HOOK / THUMBNAIL", "   TEKNIK DARAB / PANTAS!  + pil: DARJAH 4, 5 & 6", "   Frame: Cikgu thumbs-up tersenyum (sumber 0:39.5). Fail: AS-F-005_TeknikDarab Part 1_THUMB.png", "",
     "2. CAPTION PENUH (burn-in, ikut sebutan)"]
for c in caps: L.append(f"   {fmt(c['s'])}  " + " ".join(w["t"] for w in c["w"]))
L += ["", "3. SFX, ANIMASI & B-ROLL (masa video)"]
for m in mg: L.append(f"   {fmt(m[0])}–{fmt(m[1])}  {m[2]}: {m[3]}")
L.append("   B-roll: B-ROLL/B-Roll-AS-F-005_TeknikDarab Part 1.MP4, skrin terbelah atas, dipadan ikut sebutan:")
for b in broll: L.append(f"     video {fmt(b[0])}–{fmt(b[1])}  ←  B-roll {b[2]:.1f}–{b[3]:.1f} s")
L.append("   SFX: " + ", ".join(f"{fmt(t)} {n}" for t, n in sfx))
L += ["", "4. CTA", "   Tengah video (0:20): Follow saya @aster.edu_tpg (wajah bulatan emas)",
      "   End card (TOFU): Follow untuk tips belajar anak seterusnya · asteredu11.com.my · WhatsApp 011-5596 9070", "",
      "5. PERLU SEMAK"]
for d in TODO: L.append(f"   - {d[0]}: {d[1]}")
L += ["", "6. CAPTION TIKTOK + 5 HASHTAG", "   " + TT.replace("\n", "\n   "), "   " + HS, ""]
open(os.path.join(OUTD, "AS-F-005_TeknikDarab Part 1_RINGKASAN.txt"), "w", encoding="utf8").write("\n".join(L))
print("ok")
