# Bina halaman preview Artifact YM-F-006 (susun atur sama seperti YM-F-001..005).
# usage: python3 ym_f006_page.py <out.html>
import json, sys, importlib.util, os
sys.argv_saved = sys.argv
spec = importlib.util.spec_from_file_location("r", os.path.join(os.path.dirname(__file__), "ym_f006_render.py"))
src = open(spec.origin).read().split("# ---------- frames sumber")[0]
src = src.replace("SRC, BROLL, LOGO, SFX, OUT = sys.argv[1:6]", "SRC=BROLL=LOGO=SFX=OUT=''").replace("W = int(sys.argv[6])", "W = 1080")
src = src.replace("CRF = sys.argv[7] if len(sys.argv) > 7 else \"20\"", "CRF='20'").replace("os.makedirs(OUT, exist_ok=True)", "")
full = open(spec.origin).read()
src += "\nTAP = 0.75\nRCP_ITEMS = [(RCP[0] + 0.15 + i * 0.42, 0, 0, 0) for i in range(8)]\n" + full[full.index("SFXL = ["):full.index("def audio")]
R = {}; exec(src, R)
O = R["OFF"]; D = round(R["TOTAL"], 3)

caps = []
for a, b, s in R["CAP"]:
    w = []
    for i, p in enumerate(s.split("*")):
        for t in p.split():
            w.append({"t": t, "hl": i % 2 == 1, "fix": None})
    caps.append({"s": round(a + O, 2), "e": round(b + O, 2), "w": w})
for c in caps:
    for w in c["w"]:
        fx = {"resit.": "risik", "resit": "risik", "Pro+,": "ProPlus", "sekolah-sekolah": "kola-kola", "link": "lini"}
        if w["t"] in fx: w["fix"] = fx[w["t"]]

g = lambda k: R[k]
mg = [
 [0, 1.0, "Thumbnail", "Thumbnail 1 s: JAIS / MINTAK / REPORT? (REPORT? dalam kotak biru aksen) + kad logo JAIS (kiri muka), atas frame Farhan (sumber 0:11.5)"],
 [O + g("LABEL_IN"), O + g("LABEL_OUT"), "Label nama", "Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"],
 [O + g("JAIS_IN"), O + g("JAIS_OUT"), "Logo JAIS", "B-ROLL/Logo JAIS.png atas kad putih (gaya YM-F-004), pop masuk pada “laporan kat JAIS”"],
 [O + g("CAL")[0], O + g("CAL")[1], "Kad grafik", "Ikon kalendar “Hujung bulan” → ikon dokumen “Laporan ke JAIS”"],
 [O + g("RCP")[0], O + g("RCP")[1], "Motion", "Resit-resit jatuh dan bertimbun satu demi satu (“Kumpullah semua resit…”). Grafik buatan sendiri, tiada data sebenar"],
 [O + g("SHEET")[0], O + g("SHEET")[1], "Motion", "Hamparan gaya Excel: baris ditaip satu-satu → sel salah bertanda merah ✗ (“salah lagi”) → jam berputar laju + “Berjam-jam hilang”. Tiada data sebenar (bar kelabu)"],
 [O + g("LOGO_IN"), O + g("LOGO_OUT"), "Logo", "Logo Yuran.my putih atas pil biru #2A3B8F (tiada shadow) pada “Yuran.my”"],
 [O + g("BA")[0], O + g("BA")[1], "B-roll sistem", "B-ROLL/B-Roll_SistemYuran.my.mp4 @1:56.6: menu Advanced Reports, Invoice List Report → Collection Report. Jadual kosong, tiada data pelanggan"],
 [O + g("BB")[0], O + g("BB")[1], "B-roll app", "B-ROLL/B-Roll Pantau Yuran.mp4 @1:41: dashboard Collection Stats (Ogos 2026). Semua angka RM, peratus dan bilangan diblur"],
 [O + g("MASA")[0], O + g("MASA")[1], "Kad grafik", "✗ Masa untuk buat rekod (garis potong) → ✓ Masa dengan pelajar"],
 [O + g("PKG")[0], O + g("PKG")[1], "Kad pakej", "Pakej Pro+ → ✓ Sesuai untuk KAFA → ✓ Tiada kontrak. Tiada harga dipaparkan (tidak disebut)"],
 [O + g("CTA")[0], O + g("CTA")[1], "CTA", "Kad profil TikTok Yuran.My Street, link bio yuran.my/daftar/?tiktok diketuk (riak) pada “link in bio”"],
 [R["BODY_END"], D, "End card", "Logo putih + Cara MUDAH Urus Yuran + kad profil dengan link bio diketuk + Klik link di bio untuk demo sistem Yuran.my"],
]
sfx = [[round(t, 2), f.replace(".wav", "")] for t, f, gg in R["SFXL"]]
zoom = []
for t, z in R["ZOOM"]:
    zoom.append({"t": round(t + O, 2), "m": "100% (asas)" if z == 1 else f"{round(z*100)}% punch-in"})
SEG = [
 [0, 1.0, "Thumbnail", "Hook JAIS MINTAK REPORT? + logo JAIS"],
 [1.0, O + 12.84, "Laporan JAIS", "Asyik nak hantar laporan JAIS, hujung bulan, kumpul resit. Muzik 1 (sibuk/tegang)"],
 [O + 12.84, O + 18.66, "Excel & salah", "Type satu-satu dalam Excel, salah lagi, berjam-jam hilang"],
 [O + 18.66, O + 27.84, "Yuran.my", "Template khas untuk JAIS, data kutipan tersusun rapi. Muzik bertukar ke muzik 2 (harapan)"],
 [O + 27.84, O + 33.32, "Masa pelajar", "Masa buat rekod jadi masa dengan pelajar"],
 [O + 33.32, R["BODY_END"], "Pro+ & demo", "Pakej Pro+, tiada kontrak, klik link in bio untuk demo"],
 [R["BODY_END"], D, "End card", "CTA BOFU: Klik link di bio untuk demo"],
]
DONE = [
 ["Guna video trim Farhan", "BOFU_JAIS_Mintak_Report_KAFA.mp4 (41.2 s, 1080×1920, HEVC). Isi tidak dipotong; tiada senyap lebih 0.3 s.", 1.0],
 ["Thumbnail 1 saat", "JAIS / MINTAK / REPORT? (dari tajuk skrip) + kad logo JAIS sebagai hook tambahan (seperti YM-F-004). Tiada logo Yuran.my di awal. PNG 1080×1920 berasingan dieksport.", 0.3],
 ["Babak masalah dengan motion", "Logo JAIS, kalendar hujung bulan, resit bertimbun, hamparan Excel ditaip → salah → jam berjam-jam. Semua grafik buatan sendiri tanpa data sebenar.", O + 2.7],
 ["B-roll sistem Yuran.my", "Template/laporan: halaman Invoice List Report → Collection Report dari B-Roll_SistemYuran.my (jadual kosong). Data kutipan: dashboard dari B-Roll Pantau Yuran (B-roll baru), angka diblur. Setiap sisipan 3 s, suara terus berjalan.", O + g("BA")[0]],
 ["Muzik berlesen ikut babak", "Babak masalah (0:00–0:19.7): “Complicated”, Arulo — rentak sibuk. Crossfade 1 s pada “Inilah keistimewaan Yuran.my” ke “Driving Ambition”, Ahjay Stelino — muzik harapan. Kedua-dua Mixkit Stock Music Free License. ~24 dB di bawah suara dengan ducking.", O + 18.66],
 ["CTA BOFU ikut percakapan", "“Cuba klik link in bio. Kita demo dulu” → kad profil TikTok dengan link bio diketuk; end card “Klik link di bio untuk demo sistem Yuran.my”, tanpa emel (seperti YM-F-004/005).", O + g("CTA")[0]],
 ["Caption & ejaan", "1–4 perkataan, Inter ExtraBold. Ejaan DNA: resit (transkrip ‘risik’), Pro+ (transkrip ‘ProPlus’), Yuran.my, KAFA. Kata kunci biru: laporan, JAIS, report, resit, Excel, salah, berjam-jam, template, kutipan, rapi, rekod, pelajar, Pro+, kontrak, demo, link in bio.", 3.0],
 ["Brand & fakta", "Tiada harga, diskaun atau statistik ditambah. Pakej Pro+ dipaparkan tanpa harga kerana tidak disebut.", O + g("PKG")[0]],
 ["Audio", "High-pass 70 Hz, denoise ringan, kompresor lembut, normalize −14.0 LUFS (peak −1.6 dBFS).", None],
]
TODO = [
 ["“banyak lah kena bawa report”", "Bunyi kurang jelas pada 0:04.4–0:06.0; Whisper dengar ‘banyak lah kena bawa report’. Sahkan ayat sebenar.", 4.4],
 ["“sekolah-sekolah KAFA” (transkrip: “kola-kola KAFA”)", "Dibaca sebagai ‘sekolah-sekolah KAFA’. Sahkan. Kad pakej tulis ‘Sesuai untuk KAFA’.", 36.3],
 ["“link in bio” (transkrip: “lini bio”)", "Caption tulis ‘link in bio’. Sahkan jika Farhan sebut ‘link di bio’.", 38.6],
 ["“Ini yang biasa saya terima”", "Sahkan perkataan ‘terima’ (mungkin ‘dengar’).", 1.6],
 ["Template khas JAIS", "Tiada rakaman skrin template berlabel JAIS dalam B-ROLL/. Video tunjuk halaman Collection Report / Invoice List Report sebagai laporan sistem. Jika ada rakaman template JAIS sebenar, beri dan saya ganti.", O + g("BA")[0]],
 ["“Tak ada kontrak” & Pakej Pro+", "Fakta disebut Farhan; dipaparkan seperti disebut. Sahkan dengan VHA Cognitive bahawa Pro+ memang tanpa kontrak.", O + g("PKG")[1] - 0.8],
 ["CTA BOFU: link di bio, bukan DNA", "DNA BOFU: ‘Hubungi kami untuk demo sistem Yuran.my’. Ikut percakapan dan gaya YM-F-002/003: ‘Klik link di bio untuk demo sistem Yuran.my’. Link bio dari BRAND/Yuran Tiktok.jpg; sahkan masih sama.", R["BODY_END"] + 0.3],
 ["Muzik dari luar folder MUSIC/", "MUSIC/ masih kosong. Mixkit Complicated (Arulo) & Driving Ambition (Ahjay Stelino), Mixkit Stock Music Free License.", O + 18.66],
 ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (ikut DNA seperti YM-F-004/005).", None],
 ["Preview MP4 belum di Drive", "Alat Drive tidak dapat muat naik fail besar. MP4 preview dan thumbnail ada di halaman ini.", None],
]
TT = "JAIS mintak report hujung bulan? Kumpul resit, type satu-satu dalam Excel, salah lagi… berjam-jam hilang. Dengan Yuran.my, template laporan untuk JAIS dah siap dan data kutipan tersusun rapi. Pakej Pro+, tiada kontrak. Klik link di bio untuk demo dulu 👆"
HS = "#sekolahkafa #gurukafa #yuranmy #laporanjais #yuransekolah"

data = {"caps": caps, "mg": [[round(a, 2), round(b, 2), k, d] for a, b, k, d in mg], "sfx": sfx, "zoom": zoom, "dur": D}
tpl = open(os.path.join(os.path.dirname(__file__), "ym_f006_template.html")).read()
js = (f"const DATA={json.dumps(data, ensure_ascii=False)};\nconst SEG={json.dumps([[round(a,2),round(b,2),k,d] for a,b,k,d in SEG], ensure_ascii=False)};\n"
      f"const DONE={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in DONE], ensure_ascii=False)};\n"
      f"const TODO={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in TODO], ensure_ascii=False)};\n"
      f"const TT={json.dumps(TT, ensure_ascii=False)};\nconst HS={json.dumps(HS)};\n")
out = tpl.replace("/*DATA*/", js).replace("{{DUR}}", f"{D:.1f}").replace("{{NQ}}", str(len(TODO)))
open(sys.argv_saved[1], "w").write(out)
json.dump({"data": data, "SEG": SEG, "DONE": DONE, "TODO": TODO, "TT": TT, "HS": HS}, open(sys.argv_saved[1] + ".json", "w"), ensure_ascii=False, indent=1)
print("OK", D, len(caps))
