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
        if t == "USTAZ": fix = "Belisha / Malaysia (nama tidak jelas, tidak dipapar)"; q = True
        w.append({"t": t.capitalize() if False else t.lower(), "hl": h, "fix": fix, "q": q})
    caps.append({"s": round(o(c["s"]), 2), "e": round(o(c["e2"]), 2), "w": w})
# restore proper casing for terms
TERMS = {"darjah": "Darjah", "ok": "OK", "rm20": "RM20", "bm,": "BM,", "bi,": "BI,", "math,": "Math,", "science": "Science", "sejarah": "Sejarah", "dm": "DM", "ustaz": "Ustaz", "a": "A"}
for c in caps:
    for i, w in enumerate(c["w"]):
        w["t"] = TERMS.get(w["t"], w["t"])
    c["w"][0]["t"] = c["w"][0]["t"][:1].upper() + c["w"][0]["t"][1:]
KIND = {"namepill": "Label nama", "bignum": "Angka besar", "bignum_panel": "Angka besar", "note": "Nota kertas", "step": "Langkah",
        "counter": "Bulatan kiraan", "answer": "Jawapan", "follow": "CTA Follow", "price": "Pelekat harga", "subjects": "Cip subjek", "dmpill": "Pil CTA"}
def desc(e):
    k = e["kind"]
    if k == "note": return e["head"] + ": " + " / ".join(t for _, t in e["lines"])
    if k == "step": return f"LANGKAH {e['n']}: {e['text']}"
    if k == "follow": return "Wajah bulatan emas + Follow saya + @aster.edu_tpg"
    if k == "price": return f"Bintang kuning: {e['sub']} {e['text']}"
    if k == "subjects": return e["head"] + ": " + ", ".join(t for _, t in e["items"])
    return e.get("text", "")
mg = [[0, 1.0, "Thumbnail", "TAK HAFAL SIFIR? / GUNA GARISAN! + pil Darjah 4, 5 & 6 + nota 321 × 3 = ?"],
      [0, D, "Watermark", "asteredu11.com.my sepanjang video, putih ±67% + bayang halus, atas-kiri 13%"],
      [round(o(P.SPLIT[0]), 2), round(o(P.SPLIT[1]), 2), "Skrin terbelah", "B-roll iPad atas (bingkai kuning), Cikgu bawah, jalur kuning DARAB GARIS · CIKGU ALFARHAN"]]
for e in P.E: mg.append([round(o(e["s"]), 2), round(o(e["e"]), 2), KIND[e["kind"]], desc(e)])
mg.append([round(P.THUMB + P.CONTENT, 2), D, "End card", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA TOFU 'Follow untuk tips belajar anak seterusnya', asteredu11.com.my besar, WhatsApp 011-5596 9070"])
mg.sort(key=lambda x: x[0])
sfx = sorted([[round(t, 2), n] for t, n, g in P.SFX])
seg = [[0, 1.0, "Thumbnail", "Hook TAK HAFAL SIFIR? / GUNA GARISAN!"],
       [1.0, o(10.15), "Pembuka", "Untuk ibu ayah anak Darjah 4, 5 dan 6 · label Cikgu AlFarhan · 100%"],
       [o(10.15), o(20.10), "Masalah", "321 × 3 besar · nota Masalah sebenar: tak tahu sifir 3 · punch-in 113%"],
       [o(20.10), o(52.65), "Soalan 1: 321 × 3", "Skrin terbelah, B-roll iPad: garisan 3-2-1, 3 garisan melintang, kira titik bertemu → 963"],
       [o(52.65), o(86.95), "Soalan 2: 241 × 4", "Skrin terbelah: garisan 2-4-1, 4 garisan, 16 (tangan 1) → 964"],
       [o(86.95), o(97.15), "Pesan", "CTA Follow tengah video · nota Plan A tak jadi / 25 lagi alphabet"],
       [o(97.15), P.THUMB + P.CONTENT, "Pendaftaran", "Bintang RM20 · cip 5 SUBJEK · pil DM saya · punch-in 113%"],
       [P.THUMB + P.CONTENT, D, "End card", "CTA TOFU + asteredu11.com.my + WhatsApp"]]
seg = [[round(a, 2), round(b, 2), c, d] for a, b, c, d in seg]
broll = []
for a, b, txt in [(20.10, 25.6, "321 × 3 di skrin iPad"), (25.6, 30.0, "Garisan menegak 3 · 2 · 1 dilukis"), (30.0, 35.2, "3 garisan melintang (kali dengan 3)"),
                  (35.2, 50.0, "Tanda merah: kira titik bertemu → 3, 6, 9"), (50.0, 52.6, "Jawapan 9 6 3 digaris"),
                  (52.65, 56.2, "241 × 4"), (56.2, 65.9, "Garisan menegak 2 · 4 · 1 (beku sementara bahagian padam dilangkau)"), (65.91, 67.5, "4 garisan melintang"),
                  (67.5, 78.4, "Kira titik bertemu → 4, 16, tangan 1 dibulatkan"), (78.4, 86.95, "Jawapan 9 6 4 digaris + 964")]:
    broll.append([round(o(a), 2), round(o(b), 2), txt + f" (B-roll {P.broll_t(a):.0f}–{P.broll_t(b-0.01):.0f} s)"])
zoom = [{"t": round(o(a), 2) if a > 0 else 1.0, "m": f"{int(round(z*100))}%"} for a, b, z in P.ZOOM if a < 110] + \
       [{"t": round(o(a), 2), "m": f"Skrin terbelah {int(round(z*100))}%"} for a, b, z in P.SPLITZOOM]
zoom.sort(key=lambda x: x["t"])
DATA = {"caps": caps, "mg": mg, "sfx": sfx, "zoom": zoom, "dur": D, "broll": broll}
DONE = [
 ["Jenis footage: sudah ditrim", "Satu take, isi tidak dipotong. 3 senyap 0.35–0.48 s dipendekkan ke ±0.2 s (111.0 s → 110.4 s isi).", 34.0],
 ["Gaya TOFU (rujukan-gaya-TOFU)", "Biru gelap + kuning, nota kertas tulisan tangan 'Masalah sebenar', CTA Follow wajah bulatan emas di tengah video, end card CTA TOFU.", 15.0],
 ["B-roll B-Roll-AS-F-006_TeknikDarahGaris", "Rakaman iPad (tiada audio) dipadan ikut sebutan: setiap garisan dan nombor muncul bila Cikgu menyebutnya. Bahagian menunggu dipercepat; bahagian lukis dan padam garisan (3:00–3:22) dilangkau.", 27.0],
 ["Jawapan disemak", "321 × 3 = 963 dan 241 × 4 = 964: sama seperti disebut dan seperti ditulis dalam B-roll.", round(o(51.1), 2)],
 ["Harga & subjek tepat", "'Pendaftaran serendah RM20' dan '5 subjek: BM, BI, Math, Science dan Sejarah' dipapar seperti disebut; sepadan rujukan-aster.txt. Tiada nama program, diskaun atau tawaran ditambah.", round(o(101.6), 2)],
 ["Ejaan", "Topik fail 'TeknikDarahGaris' dibaca sebagai Darab Garis; label guna 'DARAB GARIS'. 'anak -anak' → anak-anak, 'jadual -jadual' → jadual-jadual, 'Ok' → OK.", 3.0],
 ["Bingkai & safe zone", "Rakaman asal letak mata Cikgu di 48% tinggi frame; bingkai diangkat 280 px (meja dipanjangkan di bawah) supaya mata di sepertiga atas. Caption di atas garis 80% dan di luar jalur kanan 15%.", 5.0],
 ["Wajah, bukan logo · watermark", "Bulatan emas guna Logo SocMed Aster; tiada Logo Rasmi Aster. asteredu11.com.my sepanjang video termasuk thumbnail.", round(D - 0.7, 2)],
 ["Audio", "−14.0 LUFS, puncak −1.5 dBTP. Muzik 23 dB di bawah suara dengan ducking.", 40.0],
]
TODO = [
 ["Durasi 112.8 s", "Melebihi sasaran TOFU 20–45 s. Footage sudah ditrim, jadi isi tidak dipotong. Beritahu jika mahu buang mana-mana bahagian (contoh: soalan kedua atau pesan ustaz).", None],
 ["Nama ustaz tidak jelas", "Transkrip pertama dengar 'Ustaz Belisha', transkrip kedua 'Ustaz Malaysia'. Caption hanya 'Ustaz bagitahu'. Beri nama yang betul jika mahu dipapar.", round(o(87.74), 2)],
 ["'Kalau 16 yang ni tangan 1'", "Dua transkrip dengar 'tangan 1' (maksud bawa 1 ke digit seterusnya). Caption ikut sebutan; sila dengar.", round(o(76.36), 2)],
 ["Tag TOFU tetapi ada bahagian jualan", "Cikgu sebut pendaftaran RM20, 5 subjek dan 'DM saya'. Ikut tag skrip TOFU, end card guna CTA Follow dan tiada lower third program. Tukar ke HYBRID/BOFU jika mahu CTA WhatsApp.", round(o(97.2), 2)],
 ["ID AS-F-006 bertindih", "Log sudah ada AS-F-006 = 'TeknikDarab Part 2'. Fail ini juga AS-F-006 (TeknikDarahGaris). Nama fail output ikut fail RAW; sahkan ID yang betul.", None],
 ["Muzik latar", "Folder MUSIC/ kosong. Muzik ringan dijana sendiri (tiada hak cipta, cara sama AS-F-004 yang diluluskan). Beritahu jika mahu guna trek 'Wholesome' seperti Part 1 & 2, atau tiada muzik.", 2.0],
 ["B-roll skrin terbelah ±66 s", "B-roll ditunjuk sebagai panel atas sepanjang bahagian mengajar (suara dan wajah kekal), sama seperti AS-F-005 yang diluluskan, bukan sisipan 3 s.", 22.0],
 ["Fail video tidak dapat dimuat naik ke Drive", "Connector Drive tidak menerima fail video; RINGKASAN.txt disimpan dalam 02_EDITED/_PREVIEW/; video preview dan thumbnail ada dalam halaman ini.", None],
]
TT = "Anak Darjah 4, 5 & 6 susah nak darab 3 digit sebab tak hafal sifir? Cuba teknik darab guna garisan ✏️ 321 × 3 = 963, 241 × 4 = 964. Pendaftaran serendah RM20 untuk 5 subjek, DM saya untuk keterangan lanjut 📩"
HS = "#cikgualfarhan #teknikdarab #matematik #tipsbelajar #asteredu"
tpl = open(os.path.join(P.S, "page", "template.html")).read()
js = "const DATA=" + json.dumps(DATA, ensure_ascii=False) + ";\nconst SEG=" + json.dumps(seg, ensure_ascii=False) + ";\nconst DONE=" + json.dumps(DONE, ensure_ascii=False) + ";\nconst TODO=" + json.dumps(TODO, ensure_ascii=False) + ";\nconst TT=" + json.dumps(TT, ensure_ascii=False) + ";\nconst HS=" + json.dumps(HS) + ";"
html = tpl.replace("/*DATA*/", js).replace("{{VER}}", VER).replace("{{DUR}}", f"{D:.1f}")
open(os.path.join(P.S, "page", "index.html"), "w").write(html)
json.dump({"TT": TT, "HS": HS, "TODO": TODO, "seg": seg, "mg": mg, "sfx": sfx, "broll": broll}, open(os.path.join(P.W, "pagedata.json"), "w"), ensure_ascii=False, indent=1)
print("ok", D, len(caps))
