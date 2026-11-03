#!/usr/bin/env python3
"""Build the preview Artifact page + RINGKASAN.txt for AS-F-006.
usage: page.py <workdir> <out_dir>"""
import json, os, sys, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
WD, OUTD = sys.argv[1], sys.argv[2]
sys.argv = ["render.py", WD, "0.5", os.path.join(OUTD, "_unused.mp4")]
R = runpy.run_path(os.path.join(HERE, "render.py"), run_name="lib")
P, s2o, CAPS, TOTAL, VEND = R["P"], R["src2out"], R["CAPS"], R["TOTAL"], R["T_VOICE_END"]
r2 = lambda x: round(x, 2)
S = lambda t: r2(s2o(t))
FIXED = {"teroka": "troker"}
FIXED_NUM = {(9.16, "1, 1"), (36.08, "1, 1"), (37.84, "33")}

caps = []
for c in CAPS:
    ws = []
    for w in c["words"]:
        bare = w["w"].rstrip(".,?!")
        fix = FIXED.get(bare)
        if w.get("solo") and abs(w["s"] - 37.84) < 0.01: fix = "32 (transkrip 1), 33 (transkrip 2)"
        ws.append(dict(t=w["w"], hl=bool(w.get("hot")), fix=fix, q=w.get("solo") and 11.8 > w["s"] > 10.8))
    caps.append(dict(s=r2(c["s"]), e=r2(c["e"]), w=ws))

ph = {p["id"]: p for p in P["phases"]}
seg = [[0, 1.0, "Thumbnail", "TEKNIK DARAB PANTAS / ADA SYARAT! + PART 2"],
       [1.0, S(3.22), "Episod lepas", "Kad Episod lepas (88 × 4 = 352) → Hari ni: Syarat-syaratnya, label Cikgu AlFarhan"],
       [S(3.22), S(19.02), "Syarat 1", "Skrin terbelah, papan kapur: nombor digit yang SAMA · 11 22 33 44 · cop SAMA"],
       [S(19.02), S(26.38), "Syarat 2", "Darab dengan nombor APA PUN · 88 × 4 · cop BOLEH"],
       [S(26.38), S(40.20), "Tak boleh semua", "12 13 15 dipangkah merah (tak sama) · 11 22 33 44 · CTA Follow tengah video"],
       [S(40.40), S(54.30), "Konsep & pola", "Skrin penuh, cip KONSEP + POLA"],
       [S(54.30), S(63.16), "Masalah sebenar", "Nota kertas: Tak faham konsep / Pola / Tak faham cerita · Macam mana nak MINAT?"],
       [S(63.16), VEND, "Jualan", "Lower third MATH TURBO 2027 · pil Pendaftaran 2027 dibuka · bintang RM20 · DM saya"],
       [VEND, TOTAL, "End card", "WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas + asteredu11.com.my + WhatsApp"]]

mg = [[0, 1.0, "Thumbnail", "TEKNIK DARAB PANTAS / ADA SYARAT! / PART 2"],
      [0, TOTAL, "Watermark", "asteredu11.com.my sepanjang video, putih ±70% + bayang halus, atas-kiri 13%"],
      [S(P["episod"]["lepas"][0]), S(P["episod"]["lepas"][1]), "Kad Episod lepas", "Teknik darab PANTAS · 88 × 4 = 352"],
      [S(P["episod"]["hari"][0]), S(P["episod"]["hari"][1]), "Kad Hari ni", "Syarat-syaratnya"],
      [S(P["name_label"][0]), S(P["name_label"][1]), "Label nama", "Cikgu AlFarhan"],
      [S(3.22), S(40.20), "Skrin terbelah", "Papan kapur hitam 'Teknik Darab · Part 2' atas, Cikgu bawah, jalur kuning + label TEKNIK DARAB · CIKGU ALFARHAN"]]
B = P["board"]
for txt, x, t0, t1 in B["A"]["nums"]: mg.append([S(t0), S(ph["A"]["t1"]), "Papan", f"{txt} ditulis, dibulatkan pada {S(t1):.1f}"])
mg.append([S(B["A"]["stamp"][1]), S(ph["A"]["t1"]), "Cop", "SAMA ✓"])
mg.append([S(B["B"]["eq"][0][1]), S(ph["B"]["t1"]), "Papan", "88 × 4, kedua-dua 8 dibulatkan (Sama)"])
mg.append([S(B["B"]["stamp"][1]), S(ph["B"]["t1"]), "Cop", "BOLEH ✓"])
mg.append([S(B["C"]["head"][1]), S(ph["C"]["t1"]), "Papan", "Tak boleh semua nombor (merah)"])
for txt, x, t0, tx in B["C"]["bad"]: mg.append([S(t0), S(ph["C"]["t1"]), "Papan", f"{txt} dipangkah merah pada {S(tx):.1f}"])
for txt, x, t0 in B["C"]["good"]: mg.append([S(t0), S(ph["C"]["t1"]), "Papan", f"{txt} (kuning, dibulatkan)"])
mg.append([S(B["C"]["stamp"][1]), S(ph["C"]["t1"]), "Cop", "SAMA ✓"])
c0, c1, c2, c3 = P["chips"][0]
mg += [[S(P["follow_cta"][0]), S(P["follow_cta"][1]), "CTA Follow", "Wajah bulatan emas + Follow saya + @aster.edu_tpg"],
       [S(c0), S(c1), "Cip", "KONSEP + POLA"], [S(c2), S(c3), "Cip", "KONSEP + POLA"],
       [S(P["note"]["t0"]), S(P["note"]["t1"]), "Nota kertas", "Masalah sebenar: ✗ Tak faham konsep · ✗ Pola · ✗ Tak faham cerita"],
       [S(P["minat"][0]), S(P["minat"][1]), "Soalan", "Macam mana nak MINAT?"],
       [S(P["lower_third"][0]), S(P["lower_third"][1]), "Lower third", "MATH TURBO 2027 · Untuk anak sekolah rendah · Tahun 4, 5 & 6"],
       [S(P["pill_2027"][0]), S(P["pill_2027"][1]), "Pil", "Pendaftaran 2027 dibuka"],
       [S(P["price"][0]), S(P["price"][1]), "Pelekat harga", "Bintang: Pendaftaran serendah RM20 sahaja"],
       [S(P["dm"][0]), S(P["dm"][1]), "CTA", "DM saya untuk keterangan lanjut"],
       [VEND, TOTAL, "End card", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
mg.sort(key=lambda m: m[0])
sfx = [[r2(s2o(t) if b == "s" else t), n] for t, n, g, b in P["sfx"]]
board = [[S(ph["A"]["t0"]), S(ph["A"]["t1"]), "Syarat 1 · Nombor digit yang SAMA · 11 22 33 44 · cop SAMA ✓"],
         [S(ph["B"]["t0"]), S(ph["B"]["t1"]), "Syarat 2 · Darab dengan nombor APA PUN · 88 × 4 · cop BOLEH ✓"],
         [S(ph["C"]["t0"]), S(ph["C"]["t1"]), "Tak boleh semua nombor · 12 13 15 dipangkah · 11 22 33 44 · cop SAMA ✓"]]
zoom = []
for t, z in P["zoom_full"]:
    if not (P["split_src"][0] <= t < P["split_src"][1]):
        zoom.append(dict(t=S(t), m={"1.0": "100%", "1.1": "110%", "1.22": "122% punch-in"}[z]))
for t, z in P["zoom_split"]: zoom.append(dict(t=S(t), m=f"Skrin terbelah {int(round(z*100))}%"))
zoom.sort(key=lambda x: x["t"])

DONE = [
 ["Jenis footage: sudah ditrim", "Satu take tanpa ulangan, isi tidak dipotong. 5 senyap pendek (0.35–0.55 s) dipendekkan; 73.8 s → 72.6 s isi.", S(10.1)],
 ["Gaya TOFU+BOFU (HYBRID)", "Ikut rujukan TOFU+BOFU_Sifir9 dan AS-F-003: hitam + kuning, kad Episod lepas / Hari ni (topik bersambung dari Part 1), papan kapur skrin terbelah, lower third MATH TURBO 2027 + pil 'Pendaftaran 2027 dibuka' bila Cikgu beralih ke jualan, CTA BOFU di end card.", 1.2],
 ["Senarai nombor disemak dua kali", "Whisper tulis '11, 1, 1, 2, 2, 2...' dan '22, 32, 33, 44'. Transkrip kedua dengar 'sebelas, satu satu, dua puluh dua, dua dua, tiga tiga, tiga puluh tiga, empat empat, empat puluh empat' dan 'satu satu, 22, 33, 44'. Tiada 32 disebut, jadi papan dan caption tunjuk 11 22 33 44.", S(36.08)],
 ["Ejaan 'teroka'", "Whisper tulis 'troker'; transkrip kedua dengar 'teroka'. Caption guna 'teroka'.", S(42.06)],
 ["Harga tepat", "'Pendaftaran serendah RM20 sahaja' dipapar seperti disebut; sepadan rujukan-aster.txt (booking/pendaftaran RM20). Tiada diskaun atau tawaran ditambah.", S(70.76)],
 ["Nota 'Masalah sebenar' (TOFU)", "Tiga baris muncul ikut sebutan: Tak faham konsep · Pola · Tak faham cerita.", S(54.3)],
 ["Muzik sama dengan Part 1", "“Wholesome”, Kevin MacLeod (incompetech.com), CC BY 4.0, sudah diluluskan bersama Part 1. Kredit dalam caption TikTok.", 2.0],
 ["Wajah, bukan logo · watermark · safe zone", "Bulatan emas guna Logo SocMed Aster; tiada Logo Rasmi Aster. asteredu11.com.my sepanjang video. Teks di atas 80% frame dan di luar jalur kanan 15%.", TOTAL - 1.0],
 ["End card BOFU", "WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070, @aster.edu_tpg.", TOTAL - 0.7],
]
TODO = [
 ["Durasi 75.0 s", "Melebihi sasaran BOFU 30–60 s. Isi tidak dipotong (satu take, tiada ulangan). Beritahu jika mahu buang mana-mana bahagian.", None],
 ["\"2, 2\" diulang (0:10.6–0:12.2)", "Selepas '22' Cikgu sebut '2, 2' — transkrip pertama dengar ia dua kali. Caption satu baris '2, 2' sahaja. Sila dengar.", S(10.90)],
 ["Lower third MATH TURBO 2027", "Cikgu sebut 'Tuition untuk 2027' tetapi tidak sebut nama 'Math Turbo'. Lower third nama program diwajibkan DNA (HYBRID, bila beralih ke jualan) dan sama seperti AS-F-003 yang diluluskan. Buang jika tidak mahu.", S(63.16)],
 ["CTA end card WhatsApp vs 'DM saya'", "Cikgu sebut 'DM saya' (dipapar sebagai pil DM). End card guna CTA BOFU DNA: WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas.", S(71.84)],
 ["Tiada B-roll Part 2", "Folder B-ROLL hanya ada B-roll Part 1 dan AS-F-003. Bahagian mengajar guna papan kapur animasi.", S(3.22)],
 ["Fail video tidak dapat dimuat naik ke Drive", "RINGKASAN.txt disimpan dalam 02_EDITED/_PREVIEW/; video preview dan thumbnail ada dalam halaman ini.", None],
]
TT = ("Teknik darab pantas ada syarat tau! ✏️ Nombor mesti digit yang sama: 11, 22, 33, 44. "
      "Anak Tahun 4, 5 & 6 seronok belajar Matematik bila faham konsep dan pola. Pendaftaran tuisyen 2027 serendah RM20 sahaja, DM saya 📩"
      "\n\nMuzik: “Wholesome” Kevin MacLeod (incompetech.com), CC BY 4.0")
HS = "#cikgualfarhan #teknikdarab #matematik #tuisyenonline #asteredu"

DATA = dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=r2(TOTAL), broll=board)
tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf8").read()
js = lambda o: json.dumps(o, ensure_ascii=False)
html = (tpl.replace("__DATA__", js(DATA)).replace("__SEG__", js(seg)).replace("__DONE__", js(DONE))
        .replace("__TODO__", js(TODO)).replace("__TT__", js(TT)).replace("__HS__", js(HS)).replace("__DUR__", f"{TOTAL:.1f}"))
open(os.path.join(OUTD, "index.html"), "w", encoding="utf8").write(html)

fmt = lambda t: f"{int(t//60)}:{t%60:04.1f}"
L = ["AS-F-006_TeknikDarab Part 2 — RINGKASAN PREVIEW", f"Aster · TOFU+BOFU (gaya HYBRID hitam + kuning) · spokesperson FARHAN · durasi {TOTAL:.1f} s · preview 540x960", "",
     "1. TEKS HOOK / THUMBNAIL", "   TEKNIK DARAB PANTAS / ADA SYARAT! + pil PART 2", f"   Frame: Cikgu tersenyum (sumber 1:{P['thumb_src_t']-60:04.1f}). Fail: AS-F-006_TeknikDarab Part 2_THUMB.png", "",
     "2. CAPTION PENUH (burn-in, ikut sebutan)"]
for c in caps: L.append(f"   {fmt(c['s'])}  " + " ".join(w["t"] for w in c["w"]))
L += ["", "3. SFX, ANIMASI & PAPAN (masa video)"]
for m in mg: L.append(f"   {fmt(m[0])}–{fmt(m[1])}  {m[2]}: {m[3]}")
L.append("   SFX: " + ", ".join(f"{fmt(t)} {n}" for t, n in sfx))
L += ["", "4. CTA", "   Tengah video (±0:36): Follow saya @aster.edu_tpg (wajah bulatan emas)",
      "   Jualan: lower third MATH TURBO 2027 + pil Pendaftaran 2027 dibuka + bintang 'Pendaftaran serendah RM20 sahaja' + pil DM saya",
      "   End card (BOFU): WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas · asteredu11.com.my · WhatsApp 011-5596 9070", "",
      "5. PERLU SEMAK"]
for d in TODO: L.append(f"   - {d[0]}: {d[1]}")
L += ["", "6. CAPTION TIKTOK + 5 HASHTAG", "   " + TT.replace("\n", "\n   "), "   " + HS, ""]
open(os.path.join(OUTD, "AS-F-006_TeknikDarab Part 2_RINGKASAN.txt"), "w", encoding="utf8").write("\n".join(L))
print("ok")
