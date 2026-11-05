# Bina halaman preview Artifact YM-F-005 (susun atur sama seperti YM-F-001..004).
# usage: python3 ym_f005_page.py <out.html>
import json, sys, importlib.util, os
sys.argv_saved = sys.argv
spec = importlib.util.spec_from_file_location("r", os.path.join(os.path.dirname(__file__), "ym_f005_render.py"))
src = open(spec.origin).read().split("# ---------- frames sumber")[0]
src = src.replace("SRC, BROLL, LOGO, SFX, OUT = sys.argv[1:6]", "SRC=BROLL=LOGO=SFX=OUT=''").replace("W = int(sys.argv[6])", "W = 1080")
src = src.replace("CRF = sys.argv[7] if len(sys.argv) > 7 else \"20\"", "CRF='20'").replace("os.makedirs(OUT, exist_ok=True)", "")
full = open(spec.origin).read()
src += "\nTAP = 0.80\n" + full[full.index("SFXL = ["):full.index("def audio")]
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
        if w["t"] == "bank-in.": w["fix"] = "back in"

B1, B2, B3, C1, PO = R["B1"], R["B2"], R["B3"], R["CARD1"], R["POLL"]
mg = [
 [0, 1.0, "Thumbnail", "Thumbnail 1 s: DUIT YURAN / DALAM / LACI? (LACI? dalam kotak biru aksen) + kad gambar kes pecah masuk bertanda PECAH MASUK (kiri muka), atas frame Farhan pandang kamera (sumber 0:02.4)"],
 [O + R["LABEL_IN"], O + R["LABEL_OUT"], "Label nama", "Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"],
 [O + B1[0], O + B1[1], "B-roll artikel", "B-ROLL/Pecah_masuk_Kafa.jpg: hantaran “SEKOLAH KAFAI AS SYARIFF BANTING KENA PECAH MASUK” + gambar bilik bersepah (29.03.2026). Kad atas latar kabur gelap, zoom perlahan"],
 [O + B2[0], O + B2[1], "B-roll artikel", "B-ROLL/PecahmasukKafa_3.png: “Polis buru suspek pecah masuk sekolah agama curi duit” (30 Mei 2025, CCTV). Pada " + f"{O + R['B2_STRIP']:.1f}" + " s tajuk Media Selangor “Dua suspek pecah masuk sekolah agama di Bukit Jelutong dikesan” (Pecah_masuk_Kafa 4.jpg, tajuk sahaja) masuk di bawah"],
 [O + C1[0], O + C1[1], "Kad grafik", "✗ Bukan soal amanah → ✓ Soal SISTEM (garis potong) → Sistem melindungi: ✓ Cikgu, ✓ Ibu bapa. Kad putih di dada; caption turun sedikit"],
 [O + PO[0], O + PO[1], "Kad soalan", "“Masih guna tunai?” dengan pilihan Ya / Tak (sorotan bergilir, tiada jawapan dipilih)"],
 [O + B3[0], O + B3[1], "B-roll gambar", "B-ROLL/PecahmasukKafa 2.jpg: pejabat sekolah selepas pecah masuk (29.03.2026), zoom perlahan"],
 [O + R["CMT_IN"], R["BODY_END"], "Motion komen", "Panel komen naik: “Ada sekolah kena pecah masuk?” → “Kongsikan pengalaman...” ditaip dalam kotak komen → butang hantar berdenyut pada “Cuba komen”. Tiada komen palsu dipaparkan"],
 [R["BODY_END"], D, "End card", "Logo putih + Cara MUDAH Urus Yuran + kad profil TikTok Yuran.My Street @yuran.my, butang + Follow ditekan jadi Following ✓ + Follow TikTok Yuran.my untuk tips urus yuran sekolah"],
]
sfx = [[round(t, 2), f.replace(".wav", "")] for t, f, g in R["SFXL"]]
zoom = []
for t, z in R["ZOOM"]:
    zoom.append({"t": round(t + O, 2), "m": "100% (asas)" if z == 1 else f"{round(z*100)}% punch-in"})
SEG = [
 [0, 1.0, "Thumbnail", "Hook DUIT YURAN DALAM LACI? + gambar kes pecah masuk"],
 [1.0, 6.18, "Duit dalam laci", "Kutip pagi, bank-in petang. Kalau hilang, siapa tanggung? Muzik 1 (tegang)"],
 [6.18, O + C1[0], "Kes pecah masuk", "Kes sekolah kena pecah masuk: 2 sisipan B-roll artikel. Siapa tanggung, dipersalahkan, rugi, ganti?"],
 [O + C1[0], O + 28.10, "Soal sistem", "Bukan soal amanah, soal sistem yang lindungi cikgu & ibu bapa. Muzik bertukar ke muzik 2 (harapan)"],
 [O + 28.10, O + 32.46, "Masih tunai?", "Soalan kepada sekolah/ketua guru: masih guna tunai?"],
 [O + 32.46, R["BODY_END"], "Kongsi pengalaman", "B-roll pejabat dipecah masuk + motion komen"],
 [R["BODY_END"], D, "End card", "CTA Follow TikTok @yuran.my"],
]
DONE = [
 ["Guna video trim Farhan", "TOFU_Duit_yuran_dalam_laci.mp4 (39.9 s, 1080×1920, HEVC). Isi tidak dipotong; tiada senyap lebih 0.35 s.", 1.0],
 ["Kes kecuaian / pecah masuk (arahan Farhan)", "3 sisipan B-roll dari B-ROLL/ (setiap satu 3 s, suara terus berjalan): hantaran pecah masuk KAFAI As Syariff Banting, artikel polis buru suspek pecah masuk sekolah agama curi duit + tajuk Media Selangor, dan gambar pejabat sekolah selepas dipecah masuk. Nama sekolah tidak diblur (arahan Farhan). Tiada teks atau fakta ditambah pada artikel.", O + B1[0]],
 ["Muzik berlesen ikut babak (arahan Farhan)", "Babak masalah (0:00–0:20.3): “Echoes”, Andrew Ev — atmosfera tegang tanpa jadi seram. Crossfade 1 s pada “Ini bukan soal amanah” ke “Dreaming Big”, Ahjay Stelino — muzik harapan untuk babak sistem & ajakan komen. Kedua-dua Mixkit Stock Music Free License (komersial, media sosial, tiada atribusi). ~24 dB di bawah suara dengan ducking; naik pada thumbnail & end card.", O + C1[0]],
 ["Thumbnail 1 saat", "DUIT YURAN / DALAM / LACI? (dari tajuk skrip & ayat pertama) + kad gambar kes pecah masuk sebagai hook tambahan. Tiada logo Yuran.my di awal. PNG 1080×1920 berasingan dieksport.", 0.3],
 ["Kad grafik & soalan", "“Bukan soal amanah → Soal SISTEM → Sistem melindungi Cikgu / Ibu bapa” dan “Masih guna tunai? Ya / Tak”, semua ikut ayat yang disebut. Kad putih di dada, muka tidak ditutup.", O + C1[0]],
 ["Motion komen", "Pada “Kongsikan pengalaman… Cuba komen”: panel komen gaya TikTok, ‘Kongsikan pengalaman...’ ditaip, butang hantar berdenyut. Tiada komen rekaan.", O + R["CMT_IN"]],
 ["Caption", "Sepanjang video, 1–4 perkataan, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2: yuran, laci, hilang, tanggung, pecah masuk, dipersalahkan, rugi, kurang, ganti, amanah, sistem, lindungi, tunai, komen. Caption panjang dikecilkan supaya kekal dalam safe zone.", 3.0],
 ["End card ikut YM-F-004", "CTA Follow TikTok @yuran.my, tanpa hello@yuran.my (seperti diluluskan untuk YM-F-004).", R["BODY_END"] + 0.3],
 ["Audio", "High-pass 70 Hz, denoise ringan, kompresor lembut, normalize −13.9 LUFS (peak −2.3 dBFS).", None],
]
TODO = [
 ["“bank-in” (transkrip: “back in”)", "Farhan sebut ‘pergi bank-in’; Whisper dengar ‘back in’. Caption tulis ‘bank-in’.", 3.96],
 ["Muzik dari luar folder MUSIC/", "MUSIC/ Yuran.my kosong; Farhan minta muzik berlesen. Mixkit Stock Music Free License. Cadangan: simpan Echoes (Andrew Ev) & Dreaming Big (Ahjay Stelino) dalam MUSIC/ sebagai rekod lesen.", O + C1[0]],
 ["Nama sekolah & kes sebenar dipaparkan", "Ikut arahan Farhan, nama KAFAI As Syariff Banting dan papan tanda sekolah tidak diblur. Video tidak mendakwa sekolah itu cuai; ia hanya memaparkan berita kes pecah masuk. Pastikan selesa.", O + B1[0]],
 ["Gambar pegawai polis & byline wartawan", "Artikel PecahmasukKafa_3 memaparkan gambar pegawai polis (IQBAL) dan nama wartawan seperti asal. Suspek dalam CCTV memang sudah dikaburkan oleh penerbit.", O + B2[0]],
 ["Tangkapan skrin berita pihak ketiga", "Tangkapan skrin artikel Media Selangor & portal berita dipaparkan seperti asal, tanpa logo Yuran.my di atasnya. Gambar stok dalam artikel Media Selangor tidak digunakan (tidak berkaitan).", O + R["B2_STRIP"]],
 ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (Farhan setuju ikut DNA, sama seperti YM-F-004).", None],
 ["Preview MP4 belum di Drive", "Alat Drive tidak dapat muat naik fail video/gambar besar. RINGKASAN dimuat naik; MP4 preview dan thumbnail ada di halaman ini.", None],
]
TT = "Duit yuran dalam laci, pagi kutip, petang baru nak bank-in. Kalau sekolah kena pecah masuk dan duit hilang, siapa yang tanggung? Ini bukan soal amanah, ini soal sistem yang lindungi cikgu dan ibu bapa. Sekolah anda masih guna tunai? Kongsikan pengalaman di ruangan komen 👇"
HS = "#sekolahkafa #yuransekolah #yuranmy #gurukafa #cashless"

data = {"caps": caps, "mg": [[round(a, 2), round(b, 2), k, d] for a, b, k, d in mg], "sfx": sfx, "zoom": zoom, "dur": D}
tpl = open(os.path.join(os.path.dirname(__file__), "ym_f005_template.html")).read()
js = (f"const DATA={json.dumps(data, ensure_ascii=False)};\nconst SEG={json.dumps([[round(a,2),round(b,2),k,d] for a,b,k,d in SEG], ensure_ascii=False)};\n"
      f"const DONE={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in DONE], ensure_ascii=False)};\n"
      f"const TODO={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in TODO], ensure_ascii=False)};\n"
      f"const TT={json.dumps(TT, ensure_ascii=False)};\nconst HS={json.dumps(HS)};\n")
out = tpl.replace("/*DATA*/", js).replace("{{DUR}}", f"{D:.1f}").replace("{{NQ}}", str(len(TODO)))
open(sys.argv_saved[1], "w").write(out)
json.dump({"data": data, "SEG": SEG, "DONE": DONE, "TODO": TODO, "TT": TT, "HS": HS}, open(sys.argv_saved[1] + ".json", "w"), ensure_ascii=False, indent=1)
print("OK", D, len(caps))
