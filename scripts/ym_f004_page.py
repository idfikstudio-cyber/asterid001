# Bina halaman preview Artifact YM-F-004 (susun atur sama seperti YM-F-001..003).
# usage: python3 ym_f004_page.py <out.html>
import json, sys, importlib.util, os
sys.argv_saved = sys.argv
spec = importlib.util.spec_from_file_location("r", os.path.join(os.path.dirname(__file__), "ym_f004_render.py"))
src = open(spec.origin).read().split("# ---------- frames sumber")[0]
src = src.replace("SRC, JAIS, LOGO, SFX, OUT = sys.argv[1:6]", "SRC=JAIS=LOGO=SFX=OUT=''").replace("W = int(sys.argv[6])", "W = 1080")
src = src.replace("CRF = sys.argv[7] if len(sys.argv) > 7 else \"20\"", "CRF='20'").replace("os.makedirs(OUT, exist_ok=True)", "")
full = open(spec.origin).read()
src += "\n" + full[full.index("SFXL = ["):full.index("def audio")]
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
        if w["t"] == "mintak": w["fix"] = "minta"
        if w["t"] == "remindkan.": w["fix"] = "remind kan"

mg = [
 [0, 1.0, "Thumbnail", "Thumbnail 1 s: PALING BERAT / JADI CIKGU / KAFA (KAFA dalam kotak biru aksen) atas frame Farhan pandang kamera (sumber 0:05.0)"],
 [O + R["LABEL_IN"], O + R["LABEL_OUT"], "Label nama", "Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"],
 [O + R["JAIS_IN"], O + R["JAIS_OUT"], "Logo JAIS", "Logo JAIS (B-ROLL/Logo JAIS.png) atas kad putih berbingkai biru aksen, pop masuk tepat sebelum “JAIS” dan keluar selepas “report”. Diletak di dada, muka tidak ditutup; caption turun sedikit"],
 [O + R["CMT_IN"], R["BODY_END"], "Motion komen", "Panel komen gaya TikTok naik dari bawah → “pernah” ditaip dalam kotak komen → butang hantar ditekan → komen “Pernah” (anda · baru sahaja) muncul + ikon hati menyala"],
 [R["BODY_END"], D, "End card", "Logo putih + Cara MUDAH Urus Yuran + Follow untuk tips urus yuran sekolah + hello@yuran.my"],
]
sfx = [[round(t, 2), f.replace(".wav", "")] for t, f, g in R["SFXL"]]
zoom = []
for t, z in R["ZOOM"]:
    zoom.append({"t": round(t + O, 2), "m": "100% (asas)" if z == 1 else f"{round(z*100)}% punch-in"})
SEG = [
 [0, 1.0, "Thumbnail", "Hook PALING BERAT JADI CIKGU KAFA"],
 [1.0, 8.32, "Bukan mengajar", "Yang paling berat bukan mengajar atau tanda buku, tapi nak ingatkan pasal yuran. Label Farhan · Yuran.my"],
 [8.32, 19.03, "Segan", "Segan dengan ibu bapa, takut murid lupa sampaikan, tak sampai hati. Punch-in pada emosi"],
 [19.03, 22.12, "Kena collect", "Duit sekolah kena kutip, nanti JAIS minta report. Logo JAIS muncul"],
 [22.12, R["BODY_END"], "Ajakan komen", "Pernah rasa macam ni? Motion komen “pernah” di ruangan komen"],
 [R["BODY_END"], D, "End card", "CTA TOFU + hello@yuran.my"],
]
DONE = [
 ["Guna video trim Farhan", "TOFU_Paling_berat_bagi_guru_KAFA.mp4 (24.2 s, 1080×1920, HEVC). Isi tidak dipotong; tiada senyap lebih 0.3 s.", 1.0],
 ["Thumbnail 1 saat", "PALING BERAT / JADI CIKGU / KAFA (5 perkataan, dari ayat pertama yang disebut) atas frame Farhan pandang kamera (sumber 0:05.0). Tiada logo di awal. PNG 1080×1920 berasingan dieksport.", 0.3],
 ["Logo JAIS (arahan Farhan)", "Muncul pada “Nanti JAIS mintak report” (0:21.1–0:22.5). Logo asal tidak diubah warna, tidak diputar atau diherotkan; atas kad putih supaya jelas atas baju berjalur. Pop masuk + SFX pop lembut.", 21.1],
 ["Motion komen (arahan Farhan)", "Pada “Komen pernah kalau pernah alami”: panel komen naik, perkataan “pernah” ditaip huruf demi huruf (bunyi tick lembut), butang hantar ditekan (click), komen “Pernah” masuk ke ruangan komen dan hati menyala. Komen ditulis sebagai “anda”, bukan akaun sebenar, jadi tiada komen palsu.", 23.05],
 ["Caption", "Sepanjang video, 1–4 perkataan ikut ritma, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2: berat, yuran, segan, takut, JAIS, report, pernah. Dalam safe zone (di atas 20% bawah, tidak masuk jalur kanan 15%). Caption naik di atas panel komen pada akhir video.", 3.0],
 ["Punch-in", "100% ↔ 112–115% pada permulaan ayat (tiada potongan isi). Mata kekal di sepertiga atas frame.", 4.55],
 ["Brand", "Biru #2A3B8F + aksen #29ABE2, logo Yuran.my putih atas latar biru tanpa shadow/watermark, ruang kosong di sekeliling logo. Tiada aset Fi-k Studio atau Aster. Tiada harga, diskaun atau statistik.", R["BODY_END"] + 0.3],
 ["Audio", "High-pass 70 Hz, denoise ringan, kompresor lembut, normalize −14.0 LUFS (peak −1.5 dBFS). 9 SFX lembut jauh di bawah suara.", None],
]
TODO = [
 ["Ejaan “mintak” (transkrip: “minta”)", "Caption ikut sebutan Farhan dalam arahan: “mintak”. Jika mahu ejaan baku “minta”, beritahu.", 21.5],
 ["“nak remindkan” (transkrip: “remind kan”)", "Dibaca sebagai “remindkan” (takut dia lupa nak remindkan). Sahkan.", 14.86],
 ["Logo JAIS ialah logo pihak ketiga", "Fail dari B-ROLL/Logo JAIS.png, guna atas arahan Farhan. Video hanya sebut JAIS minta report, tiada dakwaan kerjasama atau sokongan JAIS. Pastikan Farhan selesa memaparkan logo agensi kerajaan.", 21.2],
 ["Tiada muzik latar", "MUSIC/ Yuran.my kosong. Farhan pilih preview tanpa muzik. Muzik boleh ditambah sebelum final jika ada fail dalam MUSIC/.", None],
 ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (Farhan setuju teruskan ikut DNA).", None],
 ["CTA end card ikut DNA TOFU", "“Follow untuk tips urus yuran sekolah”. YM-F-001 yang diluluskan guna kad profil TikTok @yuran.my; beritahu jika mahu gaya itu.", R["BODY_END"] + 0.4],
 ["Tiada B-roll", "Video ini tentang perasaan cikgu, tiada bahagian yang menerangkan sistem, jadi B-roll sistem tidak diselitkan. Gambar ‘Pecah masuk KAFA’ tidak berkaitan.", None],
 ["Preview MP4 belum di Drive", "Alat Drive yang ada tidak dapat muat naik fail video/gambar besar. RINGKASAN dan log dimuat naik ke Drive; MP4 preview dan thumbnail ada di halaman ini.", None],
]
TT = "Paling berat jadi cikgu KAFA bukan mengajar, tapi nak ingatkan pasal yuran. Segan dengan ibu bapa, tak sampai hati nak tanya. Tapi duit sekolah tetap kena kutip, nanti JAIS minta report. Pernah rasa macam ni? Komen “pernah” 👇"
HS = "#cikgukafa #sekolahkafa #yuranmy #yuransekolah #gurukafa"

data = {"caps": caps, "mg": [[round(a, 2), round(b, 2), k, d] for a, b, k, d in mg], "sfx": sfx, "zoom": zoom, "dur": D}
tpl = open(os.path.join(os.path.dirname(__file__), "ym_page_template.html")).read()
js = (f"const DATA={json.dumps(data, ensure_ascii=False)};\nconst SEG={json.dumps([[round(a,2),round(b,2),k,d] for a,b,k,d in SEG], ensure_ascii=False)};\n"
      f"const DONE={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in DONE], ensure_ascii=False)};\n"
      f"const TODO={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in TODO], ensure_ascii=False)};\n"
      f"const TT={json.dumps(TT, ensure_ascii=False)};\nconst HS={json.dumps(HS)};\n")
out = tpl.replace("/*DATA*/", js).replace("{{DUR}}", f"{D:.1f}").replace("{{NQ}}", str(len(TODO)))
open(sys.argv_saved[1], "w").write(out)
json.dump({"data": data, "SEG": SEG, "DONE": DONE, "TODO": TODO, "TT": TT, "HS": HS}, open(sys.argv_saved[1] + ".json", "w"), ensure_ascii=False, indent=1)
print("OK", D, len(caps))
