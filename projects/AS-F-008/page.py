#!/usr/bin/env python3
"""Build the preview Artifact page + RINGKASAN.txt for AS-F-008.
usage: page.py <workdir> <out_dir>"""
import json, os, sys, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
WD, OUTD = sys.argv[1], sys.argv[2]
sys.argv = ["render.py", WD, "0.5", os.path.join(OUTD, "_unused.mp4")]
R = runpy.run_path(os.path.join(HERE, "render.py"), run_name="lib")
P, s2o, CAPS, TOTAL, VEND = R["P"], R["src2out"], R["CAPS"], R["TOTAL"], R["T_VOICE_END"]
r2 = lambda x: round(x, 2)
S = lambda t: r2(s2o(t))
FIXED = {"darab": "darah", "Darjah": "darjah", "“SAMA”": "Sama"}

caps = [dict(s=r2(c["s"]), e=r2(c["e"]), w=[dict(t=w["w"], hl=bool(w.get("hot")), fix=FIXED.get(w["w"].rstrip(".,?!")), q=False) for w in c["words"]]) for c in CAPS]

seg = [[0, 1.0, "Thumbnail", "MASIH KIRA / GUNA JARI? + pil Anak Darjah 5"],
       [1.0, S(6.76), "Masalah", "Pil DARJAH 5, kad kertas 7 × 8 = ?, kiraan jari, Ibu mula GERAM, Tapi tunggu..."],
       [S(6.76), S(10.90), "Punca", "BUKAN salah anak ✓ · nota Masalah sebenar: Asas sifir belum kukuh (cop PUNCA) · CTA Follow"],
       [S(10.90), VEND, "Ajak komen", "Bubble komen: Cuba komen di ruangan komen · Komen: SAMA · Anak masih lemah?"],
       [VEND, TOTAL, "End card", "Follow untuk tips belajar anak seterusnya + asteredu11.com.my + WhatsApp"]]
Q = P["q_card"]
mg = [[0, 1.0, "Thumbnail", "MASIH KIRA / GUNA JARI? / Anak Darjah 5"],
      [0, TOTAL, "Watermark", "asteredu11.com.my sepanjang video, putih ±40% + bayang halus, atas-kiri 13%"],
      [S(P["name_label"][0]), S(P["name_label"][1]), "Label nama", "Cikgu AlFarhan"],
      [S(P["darjah_chip"][0]), S(Q["t0"]), "Pil", "DARJAH 5"],
      [S(Q["t0"]), S(Q["t1"]), "Kad kertas", "7 × 8 = ? ditulis ikut sebutan, '?' bergoyang, '. . .' bila 'dia diam'"],
      [S(P["tally"]["t0"]), S(P["tally"]["t1"]), "Kiraan jari", "Garisan tally bertambah (jari gerak)"],
      [S(P["geram"][0]), S(P["geram"][1]), "Pil merah", "Ibu mula GERAM"],
      [S(P["tunggu"][0]), S(P["tunggu"][1]), "Pil", "Tapi tunggu..."],
      [S(P["bukan_salah"][0]), S(P["bukan_salah"][1]), "Pil", "✓ BUKAN salah anak"],
      [S(P["note"]["t0"]), S(P["note"]["t1"]), "Nota kertas", "Masalah sebenar: ✗ Asas sifir belum kukuh · cop PUNCA dari " + f"{S(P['note']['punca']):.1f}"],
      [S(P["follow_cta"][0]), S(P["follow_cta"][1]), "CTA Follow", "Wajah bulatan emas + Follow saya + @aster.edu_tpg (tengah video)"],
      [S(P["bubble"]["t0"]), S(P["bubble"]["t1"]), "Bubble komen", "@aster.edu_tpg · Cuba komen di ruangan komen · Komen: SAMA (dari " + f"{S(P['bubble']['sama']):.1f})"],
      [S(P["lemah"][0]), S(P["lemah"][1]), "Pil", "Anak masih lemah?"],
      [VEND, TOTAL, "End card", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA Follow, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
mg.sort(key=lambda m: m[0])
sfx = [[r2(s2o(t) if b == "s" else t), n] for t, n, g, b in P["sfx"]]
zoom = [dict(t=S(t), m={"1.0": "100%", "1.1": "110%", "1.22": "122% punch-in"}[z]) for t, z in P["zoom_full"]]

DONE = [
 ["Jenis footage: sudah ditrim", "Satu take tanpa ulangan, isi tidak dipotong. Satu senyap 0.3 s dipendekkan dan senyap di hujung dibuang.", S(3.85)],
 ["Disemak dengan transkrip kedua", "'7 darah 8' → '7 darab 8' (transkrip kedua: 'Tujuh darab lapan. Dia diam. Jari gerak.'). Perkataan selepas 'ruangan komen' ialah 'Sama' — dipapar sebagai perkataan untuk dikomen: “SAMA”.", S(1.70)],
 ["Ejaan istilah", "Darjah (huruf besar) ikut DNA.", 1.0],
 ["Gaya TOFU", "Biru gelap + kuning, kertas nota, nota 'Masalah sebenar', CTA Follow wajah bulatan emas di tengah video, end card CTA TOFU.", S(7.98)],
 ["Muzik", "“Wholesome”, Kevin MacLeod (incompetech.com), CC BY 4.0 — sama seperti AS-F-005 hingga AS-F-007. Kredit dalam caption TikTok.", 2.0],
 ["Watermark ±40%", "Ikut arahan Farhan untuk AS-F-007: asteredu11.com.my putih ±40% dengan bayang halus, sepanjang video.", 3.0],
 ["Wajah, bukan logo · safe zone", "Bulatan emas guna Logo SocMed Aster; tiada Logo Rasmi Aster. Teks di atas 80% frame dan di luar jalur kanan 15%.", TOTAL - 1.0],
 ["Durasi 20.2 s", "Dalam sasaran TOFU 20–45 s.", None],
]
TODO = [
 ["Tiada B-roll", "Folder B-ROLL tiada rakaman untuk AS-F-008. Video guna grafik sahaja (kad 7 × 8, kiraan jari, nota).", None],
 ["Grafik 'Ibu mula GERAM' dan 'Anak masih lemah?'", "Ayat ikut sebutan Cikgu. Pil merah 'GERAM' ialah emosi; beritahu jika mahu lebih lembut (DNA: mesra, bukan menakutkan).", S(5.26)],
 ["Fail video tidak dapat dimuat naik ke Drive", "RINGKASAN.txt disimpan dalam 02_EDITED/_PREVIEW/; video preview dan thumbnail ada dalam halaman ini.", None],
]
TT = ("Anak Darjah 5 masih kira guna jari bila jumpa 7 × 8? Ini bukan salah anak, asas sifir belum kukuh ✏️ "
      "Anak ibu ayah macam ni? Komen SAMA 👇\n\nMuzik: “Wholesome” Kevin MacLeod (incompetech.com), CC BY 4.0")
HS = "#cikgualfarhan #sifir #matematik #tipsbelajar #asteredu"

DATA = dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=r2(TOTAL), broll=[])
tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf8").read()
js = lambda o: json.dumps(o, ensure_ascii=False)
html = (tpl.replace("__DATA__", js(DATA)).replace("__SEG__", js(seg)).replace("__DONE__", js(DONE))
        .replace("__TODO__", js(TODO)).replace("__TT__", js(TT)).replace("__HS__", js(HS)).replace("__DUR__", f"{TOTAL:.1f}"))
open(os.path.join(OUTD, "index.html"), "w", encoding="utf8").write(html)

fmt = lambda t: f"{int(t//60)}:{t%60:04.1f}"
L = ["AS-F-008_Anak_Kira_GunaTangan — RINGKASAN PREVIEW", f"Aster · TOFU (biru gelap + kuning) · spokesperson FARHAN · durasi {TOTAL:.1f} s · preview 540x960", "",
     "1. TEKS HOOK / THUMBNAIL", "   MASIH KIRA / GUNA JARI? + pil 'Anak Darjah 5'", f"   Frame: Cikgu ke kamera (sumber 0:{P['thumb_src_t']:04.1f}). Fail: AS-F-008_Anak_Kira_GunaTangan_THUMB.png", "",
     "2. CAPTION PENUH (burn-in, ikut sebutan)"]
for c in caps: L.append(f"   {fmt(c['s'])}  " + " ".join(w["t"] for w in c["w"]))
L += ["", "3. SFX & ANIMASI (masa video; tiada B-roll)"]
for m in mg: L.append(f"   {fmt(m[0])}–{fmt(m[1])}  {m[2]}: {m[3]}")
L.append("   SFX: " + ", ".join(f"{fmt(t)} {n}" for t, n in sfx))
L += ["", "4. CTA", "   Tengah video (±0:10): Follow saya @aster.edu_tpg (wajah bulatan emas)",
      "   Bubble komen: Cuba komen di ruangan komen · Komen: SAMA",
      "   End card (TOFU): Follow untuk tips belajar anak seterusnya · asteredu11.com.my · WhatsApp 011-5596 9070", "",
      "5. PERLU SEMAK"]
for d in TODO: L.append(f"   - {d[0]}: {d[1]}")
L += ["", "6. CAPTION TIKTOK + 5 HASHTAG", "   " + TT.replace("\n", "\n   "), "   " + HS, ""]
open(os.path.join(OUTD, "AS-F-008_Anak_Kira_GunaTangan_RINGKASAN.txt"), "w", encoding="utf8").write("\n".join(L))
print("ok")
