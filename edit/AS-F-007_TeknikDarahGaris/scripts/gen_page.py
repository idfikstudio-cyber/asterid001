import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan as P
o = P.o; D = round(P.TOTAL, 2)
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
caps = []
for c in P.caps:
    w = []
    for t, h in zip(c["toks"], c["hl"]):
        q = None; fix = None
        if t.startswith("TANGAN"): q = True
        if t in ("BADLI", "SHAH"): fix = "Belisha (transkrip); nama disahkan Farhan"
        w.append({"t": t.capitalize() if False else t.lower(), "hl": h, "fix": fix, "q": q})
    caps.append({"s": round(o(c["s"]), 2), "e": round(o(c["e2"]), 2), "w": w})
# restore proper casing for terms
TERMS = {"darjah": "Darjah", "ok": "OK", "rm20": "RM20", "bm,": "BM,", "bi,": "BI,", "math,": "Math,", "science": "Science", "sejarah": "Sejarah", "dm": "DM", "ustaz": "Ustaz", "badli": "Badli", "shah": "Shah", "a": "A"}
for c in caps:
    for i, w in enumerate(c["w"]):
        w["t"] = TERMS.get(w["t"], w["t"])
    c["w"][0]["t"] = c["w"][0]["t"][:1].upper() + c["w"][0]["t"][1:]
KIND = {"namepill": "Label nama", "bignum": "Angka besar", "bignum_panel": "Angka besar", "note": "Nota kertas", "step": "Langkah",
        "counter": "Bulatan kiraan", "answer": "Jawapan", "follow": "CTA Follow", "carry": "Cip", "lowerthird": "Lower third", "redpill": "Pil", "photo": "B-roll foto", "price": "Pelekat harga", "subjects": "Cip subjek", "dmpill": "Pil CTA"}
def desc(e):
    k = e["kind"]
    if k == "note": return e["head"] + ": " + " / ".join(t for _, t in e["lines"])
    if k == "step": return f"LANGKAH {e['n']}: {e['text']}"
    if k == "follow": return "Wajah bulatan emas + Follow saya + @aster.edu_tpg"
    if k == "photo": return f"Foto {e['name']} (B-ROLL/Badli_Shah_2018.jpg) + label {e['name']} · {e['role']} + petikan “{e['quote']}”"
    if k == "price": return f"Bintang kuning: {e['sub']} {e['text']}"
    if k == "subjects": return e["head"] + ": " + ", ".join(t for _, t in e["items"])
    return e.get("text", "")
mg = [[0, 1.0, "Thumbnail", "TAK HAFAL SIFIR? / GUNA GARISAN! + pil Darjah 4, 5 & 6 + nota 321 × 3 = ?"],
      [0, D, "Watermark", "asteredu11.com.my sepanjang video, putih ±40% + bayang halus; atas-kiri 13%, dialih ke kanan atas semasa skrin terbelah"],
      [round(o(P.SPLIT[0]), 2), round(o(P.SPLIT[1]), 2), "Skrin terbelah", "B-roll iPad atas (bingkai kuning), Cikgu bawah, jalur kuning DARAB GARIS · CIKGU ALFARHAN"]]
for e in P.E: mg.append([round(o(e["s"]), 2), round(o(e["e"]), 2), KIND[e["kind"]], desc(e)])
mg.append([round(P.THUMB + P.CONTENT, 2), D, "End card", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA BOFU 'WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas', asteredu11.com.my besar, WhatsApp 011-5596 9070"])
mg.sort(key=lambda x: x[0])
sfx = sorted([[round(t, 2), n] for t, n, g in P.SFX])
seg = [[0, 1.0, "Thumbnail", "Hook TAK HAFAL SIFIR? / GUNA GARISAN!"],
       [1.0, o(10.15), "Pembuka", "Untuk ibu ayah anak Darjah 4, 5 dan 6 · label Cikgu AlFarhan · 118%"],
       [o(10.15), o(20.10), "Masalah", "321 × 3 besar · nota Masalah sebenar: tak tahu sifir 3 · punch-in 132%"],
       [o(20.10), o(52.65), "Soalan 1: 321 × 3", "Skrin terbelah, B-roll iPad: garisan 3-2-1, 3 garisan melintang, kira titik bertemu → 963"],
       [o(52.65), o(86.95), "Soalan 2: 241 × 4", "CTA Follow · skrin terbelah: garisan 2-4-1, 4 garisan, 16 (tulis 6, 1 naik ke atas) → 964"],
       [o(86.95), o(97.15), "Pesan Ustaz", "Foto Ustaz Badli Shah (Timbalan Mufti Pahang) + petikan kata-katanya"],
       [o(97.15), P.THUMB + P.CONTENT, "Jualan", "Lower third MATH TURBO 2027 · pil Pendaftaran 2027 dibuka · bintang RM20 · cip 5 SUBJEK · pil DM saya"],
       [P.THUMB + P.CONTENT, D, "End card", "CTA BOFU WhatsApp + asteredu11.com.my"]]
seg = [[round(a, 2), round(b, 2), c, d] for a, b, c, d in seg]
broll = []
for a, b, txt in [(20.10, 25.6, "321 × 3 di skrin iPad"), (25.6, 30.0, "Garisan menegak 3 · 2 · 1 dilukis"), (30.0, 35.2, "3 garisan melintang (kali dengan 3)"),
                  (35.2, 50.0, "Tanda merah: kira titik bertemu → 3, 6, 9"), (50.0, 52.6, "Jawapan 9 6 3 digaris"),
                  (52.65, 56.2, "241 × 4"), (56.2, 65.9, "Garisan menegak 2 · 4 · 1 (beku sementara bahagian padam dilangkau)"), (65.91, 67.5, "4 garisan melintang"),
                  (67.5, 78.4, "Kira titik bertemu → 4, 16 (tulis 6, angka 1 naik ke atas dan dibulatkan)"), (78.4, 86.95, "Kira 9, jawapan 9 6 4 digaris")]:
    broll.append([round(o(a), 2), round(o(b), 2), txt + f" (B-roll {P.broll_t(a):.0f}–{P.broll_t(b-0.01):.0f} s)"])
zoom = [{"t": round(o(a), 2) if a > 0 else 1.0, "m": f"{int(round(z*100))}%"} for a, b, z in P.ZOOM if a < 110] + \
       [{"t": round(o(a), 2), "m": f"Skrin terbelah {int(round(z*100))}%"} for a, b, z in P.SPLITZOOM]
zoom.sort(key=lambda x: x["t"])
DATA = {"caps": caps, "mg": mg, "sfx": sfx, "zoom": zoom, "dur": D, "broll": broll}
DONE = [
 ["v2: ID AS-F-007", "Fail RAW kini AS-F-007_TeknikDarahGaris; semua output guna ID ini.", None],
 ["v2: meja tidak lagi cacat", "Bingkai v1 meregang meja di bawah. Kini dipotong terus dari rakaman asal (zoom 118% / 132% berpusat pada muka), tiada piksel diregang.", 3.0],
 ["v2: watermark tidak ganggu nota", "Kelegapan diturunkan ke ±40%. Dalam skrin terbelah watermark dialih ke kanan atas panel, jauh dari tulisan di iPad.", 27.0],
 ["v2: semua nombor B-roll nampak", "Panel B-roll lebih tinggi (crop 1440×1327). Jawapan 9 6 3 dan 9 6 4, nombor 6 dan angka 1 yang naik ke atas kini dalam skrin. Label LANGKAH dan kotak jawapan dialih ke bawah, di luar panel B-roll.", round(o(79.0), 2)],
 ["v2: 16 = tulis 6, angka 1 naik ke atas", "Cip kuning '16: tulis 6, angka 1 naik ke atas' semasa Cikgu sebut 'Kalau 16 yang ni tangan 1', ikut penerangan Farhan.", round(o(76.36), 2)],
 ["v3: Kata-kata Ustaz Badli Shah di bawah gambar", "Foto (B-ROLL/Badli_Shah_2018.jpg) + label 'Ustaz Badli Shah · Timbalan Mufti Pahang' + petikan “Kalau plan A tak jadi, masih ada 25 lagi alphabet untuk kita boleh guna” (teks Farhan). Sisipan dipanjangkan ke 6.7 s (87.7–94.5 s sumber) supaya sempat dibaca; nota 'Pesan Ustaz' lama dibuang. Caption 'Ustaz Badli Shah bagitahu'.", round(o(87.74), 2)],
 ["v2: TOFU+BOFU", "Hitam + kuning ikut rujukan TOFU+BOFU_Sifir9. Lower third MATH TURBO 2027, pil 'Pendaftaran 2027 dibuka', bintang RM20, cip 5 subjek, pil DM saya, end card CTA BOFU WhatsApp. CTA Follow kini di tengah video (0:53).", round(o(97.2), 2)],
 ["v2: muzik Wholesome", "Kevin MacLeod (incompetech.com), CC BY 4.0. Kredit dalam caption TikTok.", 2.0],
 ["Jawapan disemak", "321 × 3 = 963 dan 241 × 4 = 964: sama seperti disebut dan ditulis dalam B-roll.", round(o(51.1), 2)],
 ["Harga & subjek tepat", "'Pendaftaran serendah RM20' dan '5 subjek: BM, BI, Math, Science dan Sejarah' dipapar seperti disebut; sepadan rujukan-aster.txt.", round(o(101.6), 2)],
 ["Durasi dikekalkan", "112.8 s (melebihi sasaran 30–60 s) dikekalkan atas arahan Farhan.", None],
 ["Audio", "−14.0 LUFS, puncak −1.5 dBTP. Muzik 23 dB di bawah suara dengan ducking.", 40.0],
]
TODO = [
 ["Lower third MATH TURBO 2027 + pil 'Pendaftaran 2027 dibuka'", "Cikgu sebut 'kita dah buka pendaftaran' tetapi tidak sebut 'Math Turbo' atau '2027'. Diletak ikut DNA (bila beralih ke jualan), sama seperti AS-F-003 yang diluluskan. Buang jika tidak mahu.", round(o(97.2), 2)],
 ["CTA end card WhatsApp vs 'DM saya'", "Cikgu sebut 'DM saya' (dipapar sebagai pil). End card guna CTA BOFU DNA: WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas.", round(o(106.76), 2)],
 ["Caption 'tangan 1'", "Caption ikut sebutan ('Kalau 16 yang ni tangan 1'); penerangan '16: tulis 6, angka 1 naik ke atas' dipapar sebagai cip. Beritahu jika mahu caption diubah.", round(o(76.36), 2)],
 ["Sisipan foto Ustaz 6.7 s", "Peraturan umum hadkan B-roll 3 s setiap sisipan; dipanjangkan atas permintaan Farhan supaya petikan sempat dibaca. Suara Cikgu terus berjalan.", round(o(87.74), 2)],
 ["Fail video tidak dimuat naik ke Drive", "RINGKASAN.txt disimpan dalam 02_EDITED/_PREVIEW/; video preview dan thumbnail ada dalam halaman ini.", None],
]
TT = "Anak Darjah 4, 5 & 6 susah nak darab 3 digit sebab tak hafal sifir? Cuba teknik darab guna garisan ✏️ 321 × 3 = 963, 241 × 4 = 964. Pendaftaran serendah RM20 untuk 5 subjek, DM saya untuk keterangan lanjut 📩\n\nMuzik: “Wholesome” Kevin MacLeod (incompetech.com), CC BY 4.0"
HS = "#cikgualfarhan #teknikdarab #matematik #tipsbelajar #asteredu"
tpl = open(os.path.join(P.S, "page", "template.html")).read()
js = "const DATA=" + json.dumps(DATA, ensure_ascii=False) + ";\nconst SEG=" + json.dumps(seg, ensure_ascii=False) + ";\nconst DONE=" + json.dumps(DONE, ensure_ascii=False) + ";\nconst TODO=" + json.dumps(TODO, ensure_ascii=False) + ";\nconst TT=" + json.dumps(TT, ensure_ascii=False) + ";\nconst HS=" + json.dumps(HS) + ";"
html = tpl.replace("/*DATA*/", js).replace("{{VER}}", VER).replace("{{DUR}}", f"{D:.1f}")
open(os.path.join(P.S, "page", "index.html"), "w").write(html)
json.dump({"TT": TT, "HS": HS, "TODO": TODO, "seg": seg, "mg": mg, "sfx": sfx, "broll": broll}, open(os.path.join(P.W, "pagedata.json"), "w"), ensure_ascii=False, indent=1)
print("ok", D, len(caps))
