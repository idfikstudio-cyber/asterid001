# Jana halaman preview (Artifact) + RINGKASAN.txt dari timeline.
# usage: python3 gen_page.py timeline.json page.html ringkasan.txt
import json, sys, html
tl = json.load(open(sys.argv[1])); D = tl["dur"]; T0 = tl["thumb"]; C = T0 + tl["content"]
def s2o(s):
    o = T0
    for a, b in tl["keep"]:
        if s < a: return o
        if s <= b: return o + s - a
        o += b - a
    return o
fmt = lambda t: f"{int(t // 60)}:{t % 60:04.1f}"
sp0, sp1 = tl["split"]
SEG = [[0, T0, "Thumbnail", "DARAB 2 NOMBOR? / CARA MUDAH!"],
       [T0, sp0, "Masalah ibu ayah", "Label Cikgu AlFarhan + wajah bulatan emas, pil Darjah 4 · 5 · 6, nota Masalah sebenar, kad Hari ni"],
       [sp0, s2o(48.34), "Soalan 1: 22 × 12", "Skrin terbelah: papan iPad atas, Cikgu bawah. LANGKAH 1–3, pop kiraan, kad JAWAPAN 264"],
       [s2o(48.34), s2o(70.85), "Soalan 2: 24 × 22", "LANGKAH 1–3, pop kiraan, kad JAWAPAN 528, pelekat Senang kan?"],
       [s2o(70.85), sp1, "Cuba sendiri: 32 × 24", "Tag CUBA SENDIRI!, bubble komen TikTok"],
       [sp1, C, "Jualan", "Lower third MATH TURBO 2027, pil Pendaftaran 2027 dibuka, DM saya, Jadual kelas / Silibus, tiket RM20, bintang 5 subjek RM99"],
       [C, D, "End card", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp, 011-5596 9070, asteredu11.com.my"]]
KIND = {"label": "Label", "pill": "Pil", "note": "Nota", "today": "Kad Hari ni", "split": "Skrin terbelah", "qtag": "Tag soalan", "step": "Langkah",
        "calc": "Pop kiraan", "answer": "Jawapan", "sticker": "Pelekat", "comment": "Bubble komen", "lower": "Lower third", "reg": "Pil daftar",
        "dm": "Kad DM", "chips": "Cip", "price1": "Tiket harga", "price2": "Bintang harga"}
def desc(g):
    k = g["kind"]
    if k == "note": return g["title"] + ": " + " ".join(g["lines"])
    if k == "today": return g["head"] + ": " + g["text"]
    if k == "split": return "Papan iPad (b-roll AS-F-003_Broll_SoalanMath) atas, Cikgu bawah, bar " + g["bar"]
    if k == "step": return f"LANGKAH {g['n']}: {g['text']}"
    if k == "answer": return f"{g['q']} = {g['ans']}"
    if k == "lower": return g["title"] + " · " + g["sub"]
    if k == "dm": return g["text"] + " " + g["sub"]
    if k == "chips": return " / ".join(g["items"])
    if k == "price1": return g["label"] + " " + g["price"]
    if k == "price2": return f"{g['top']} {g['mid']} {g['price']}"
    return g.get("text", "")
MG = [[0, T0, "Thumbnail", "Hook DARAB 2 NOMBOR? CARA MUDAH!"], [0, D, "Watermark", "asteredu11.com.my sepanjang video, putih 68% + bayang halus, atas-kiri 12%"]] + \
     [[g["s"], g["e"], KIND[g["kind"]], desc(g)] for g in tl["graphics"]] + [[C, D, "End card", SEG[-1][3]]]
cuts = [{"t": round(s2o(a), 2), "src": a} for a, b in tl["keep"]]
zoom = [{"t": z["t"], "src": z["src"], "z": z["z"]} for z in tl["zoom"]]
caps = [{"s": c["s"], "e": c["e"], "w": [{"t": w["t"], "hl": w["hl"], "fix": w.get("fix")} for w in c["w"]]} for c in tl["captions"]]

DONE = [["Footage sudah ditrim", "Ikut arahan Farhan: isi tidak dipotong. Hanya 10 jeda senyap lebih 0.3 s dibuang (padding 0.1 s): 94.2 s jadi 90.4 s.", 1.2],
        ["B-roll iPad sebagai papan", "AS-F-003_Broll_SoalanMath dipapar di skrin terbelah (gaya rujukan TOFU+BOFU Sifir 9). Rakaman iPad tidak ditrim, jadi masanya dipadan semula ikut setiap coretan supaya tulisan muncul bila disebut.", 14.0],
        ["Angka disemak", "Semua kiraan disahkan dengan transkrip kedua: 22 × 12 = 264, 24 × 22 = 528 (4 × 2 = 8 disebut dua kali). Jawapan 32 × 24 tidak dipapar, dibiar untuk penonton komen.", s2o(42.7)],
        ["Wajah, bukan logo", "Label, bubble komen dan end card guna wajah dalam bulatan emas (Logo SocMed Aster). Tiada Logo Rasmi Aster atau teks ASTER EDU.", 1.3],
        ["Watermark & safe zone", "asteredu11.com.my sepanjang video termasuk thumbnail. Semua teks di atas 80% frame dan di luar jalur kanan 15%.", 20],
        ["End card BOFU", "Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, 011-5596 9070, asteredu11.com.my besar.", C + 0.6],
        ["Harga 5 subjek RM99 (v2)", "Disahkan Farhan: 5 subjek RM99. Caption dan bintang harga ditukar. Suara di frasa ini dijernihkan (+5 dB, presence 2–4 kHz, boom 220 Hz dikurangkan) dan potongan dipanjangkan ke hujung rakaman supaya perkataan tidak terpotong.", s2o(92.3)],
        ["Pendaftaran RM20", "Disebut \"pendaftaran serendah RM20\"; sepadan rujukan-aster.txt (booking / pendaftaran RM20).", s2o(91.0)]]
TODO = [
        ["Ayat diulang", "\"Jadi macam mana pula dengan soalan?\" lalu \"Macam mana pula dengan soalan? 32 kali dengan 24\". Dikekalkan sebab footage sudah ditrim. Buang ayat pertama (jimat ±1.4 s)?", s2o(71.3)],
        ["MATH TURBO 2027 & \"Pendaftaran 2027 dibuka\"", "Lower third dan pil diletak ikut DNA gaya HYBRID. \"Math Turbo\" dan \"dibuka\" tidak disebut; \"2027\" dari \"tahun depan\". Kekal?", s2o(82.0)],
        ["CTA DM vs WhatsApp", "Farhan sebut \"DM saya untuk keterangan lanjut\". Kad DM dipapar ketika itu; end card guna CTA BOFU DNA (WhatsApp + 011-5596 9070). Ok?", s2o(85.7)],
        ["Strok merah serentak", "Dalam rakaman iPad asal, lengkung merah + baris merah + garisan muncul serentak (bukan satu-satu). Ditunjuk bila Farhan sebut \"ambil nombor yang kedua\".", s2o(28.9)],
        ["B-roll lebih 3 s", "Papan iPad di skrin terbelah ±71 s (melebihi had sisipan B-roll 3 s) kerana ia isi pengajaran, ikut gaya rujukan. Suara berjalan terus.", sp0 + 1],
        [f"Durasi {D:.1f} s", "Melebihi sasaran BOFU 30–60 s. Isi tidak dipotong (footage sudah ditrim)."],
        ["Ejaan dibetulkan", "\"Darjah\" (transkrip: dah jam / belajar), \"tuisyen\" (disebut \"tuition\"), \"silibus\" (disebut \"syllabus\"), \"kali dengan\" (transkrip: x), \"sekolah rendah\" (transkrip sekali: rumah).", s2o(2.9)],
        ["Fail rujukan gaya", "Tag TOFU+BOFU: dipakai \"TOFU+BOFU_Sifir9→ rujukan-gaya-TOFU.mp4\" (hitam + kuning, skrin terbelah). Label pembahagi ikut DNA: DARAB 2 NOMBOR · CIKGU ALFARHAN (bukan · ASTER EDU seperti rujukan)."],
        ["Muzik & fail", "Tiada muzik latar (MUSIC/ kosong). MP4 preview dan THUMB.png tidak dapat dimuat naik melalui connector Drive; ada di halaman ini."]]
TT = "Ibu ayah, anak Darjah 4, 5 & 6 ada masalah darab 2 nombor? Ni cara mudah dari Cikgu AlFarhan ✏️ Sekarang giliran anak: 32 × 24 = ? Komen jawapan di bawah! 👇"
HS = "#darab #matematik #sekolahrendah #cikgualfarhan #asteredu"
DATA = {"caps": caps, "cuts": cuts, "zoom": zoom, "mg": MG, "sfx": [[s["t"], s["name"]] for s in tl["sfx"]], "dur": D}

page = open(__file__.replace("gen_page.py", "page_template.html")).read()
page = page.replace("/*DATA*/", "const DATA=" + json.dumps(DATA, ensure_ascii=False) + ";\nconst SEG=" + json.dumps(SEG, ensure_ascii=False) +
                    ";\nconst DONE=" + json.dumps(DONE, ensure_ascii=False) + ";\nconst TODO=" + json.dumps(TODO, ensure_ascii=False) +
                    ";\nconst TT=" + json.dumps(TT, ensure_ascii=False) + ";\nconst HS=" + json.dumps(HS) + ";").replace("{{DUR}}", f"{D:.1f}")
open(sys.argv[2], "w").write(page)

L = [f"AS-F-003_SoalanMath — RINGKASAN PREVIEW (Aster Edu · TOFU+BOFU · spokesperson Farhan)",
     f"Preview 540x960, {D:.1f} saat (thumbnail 1.0 s + isi {tl['content']:.1f} s + end card 1.5 s). Footage sudah ditrim oleh Farhan; hanya jeda senyap >0.3 s dibuang (10 potongan). Tiada isi dibuang.",
     "Halaman preview: {{URL}}", "",
     "1) TEKS HOOK / THUMBNAIL", "   DARAB 2 NOMBOR? / CARA MUDAH!  (frame Cikgu AlFarhan senyum, sumber 1:10.2). Fail: AS-F-003_SoalanMath_THUMB.png", "",
     "2) CAPTION PENUH (ikut sebutan; *kata kunci kuning*)"]
for c in caps:
    L.append(f"   {fmt(c['s'])}  " + " ".join(("*" + w["t"] + "*") if w["hl"] else w["t"] for w in c["w"]))
L.append("   Ejaan dibetulkan dari transkrip: dah jam/belajar→Darjah, rumah→rendah, tuition→tuisyen, syllabus→silibus, x→kali dengan.")
L += ["", "3) ANIMASI, GRAFIK, B-ROLL & SFX (masa video preview)"]
for m in sorted(MG, key=lambda m: m[0]): L.append(f"   {fmt(m[0])}–{fmt(m[1])}  {m[2]}: {m[3]}")
L.append(f"   B-roll: AS-F-003_Broll_SoalanMath (rakaman iPad) di skrin terbelah {fmt(sp0)}–{fmt(sp1)}, masa dipadan ikut coretan.")
L.append("   Punch-in: selang-seli 100% / 112% setiap 2–3 potongan, mata di ±40% atas frame.")
L.append(f"   SFX ({len(tl['sfx'])} cue): " + ", ".join(f"{fmt(s['t'])} {s['name']}" for s in tl["sfx"]))
L += ["", "4) CTA", "   Dalam video: \"DM saya untuk keterangan lanjut\" (kad DM), pil Pendaftaran 2027 dibuka, tiket Pendaftaran serendah RM20, bintang 5 subjek RM99.",
      "   End card (BOFU): wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, \"WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas\", WhatsApp 011-5596 9070, asteredu11.com.my.", "",
      "5) PERLU SEMAK"] + [f"   - {d[0]}: {d[1]}" for d in TODO] + ["", "6) CAPTION TIKTOK + 5 HASHTAG", "   " + TT, "   " + HS, ""]
open(sys.argv[3], "w").write("\n".join(L))
print("ok", len(caps), "caption", len(MG), "grafik")
