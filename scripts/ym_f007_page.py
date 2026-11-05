# Bina halaman preview Artifact YM-F-007 (susun atur sama seperti YM-F-001..006).
# usage: python3 ym_f007_page.py <out.html>
import json, sys, importlib.util, os
sys.argv_saved = sys.argv
spec = importlib.util.spec_from_file_location("r", os.path.join(os.path.dirname(__file__), "ym_f007_render.py"))
src = open(spec.origin).read().split("# ---------- frames sumber")[0]
src = src.replace("SRC, BROLL, LOGO, SFX, OUT = sys.argv[1:6]", "SRC=BROLL=LOGO=SFX=OUT=''").replace("W = int(sys.argv[6])", "W = 1080")
src = src.replace("CRF = sys.argv[7] if len(sys.argv) > 7 else \"20\"", "CRF='20'").replace("os.makedirs(OUT, exist_ok=True)", "")
full = open(spec.origin).read()
src += "\nTAP = 0.75\n" + full[full.index("SFXL = ["):full.index("def audio")]
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
        fx = {"*Selak,*": "Select", "Selak,": "Select", "selak,": "select", "selak.": "select", "hutang": "utang"}
        if w["t"] in fx: w["fix"] = fx[w["t"]]

g = lambda k: R[k]
mg = [
 [0, 1.0, "Thumbnail", "Thumbnail 1 s: SIAPA / BELUM / BAYAR? (BAYAR? dalam kotak merah) + kad status kecil (Dah bayar / ? / Belum) di atas kiri, atas frame Farhan (sumber 0:00.9)"],
 [O + g("LABEL_IN"), O + g("LABEL_OUT"), "Label nama", "Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"],
 [O + g("BOOK")[0], O + g("BOOK")[1], "Motion", "Buku rekod dibuka, muka surat diselak tiga kali tepat pada “selak, selak, selak”"],
 [O + g("LIST")[0], O + g("LIST")[1], "Kad grafik", "Senarai: “Dah bayar” → ✗ Tak direkod (pada “record”), “Belum bayar” → ✗ Tiada reminder (pada “reminder”). Nama sebagai bar kelabu"],
 [O + g("CHAT")[0], O + g("CHAT")[1], "Motion", "Mesej ke ibu bapa ditaip “Assalamualaikum puan, yuran bulan ni…” lalu dipadam semula (segan-segan)"],
 [O + g("WRONG")[0], O + g("WRONG")[1], "Kad grafik", "✗ Kita kata: Belum bayar → ✓ Sebenarnya: Dah bayar"],
 [O + g("LOGO_IN"), O + g("LOGO_OUT"), "Logo", "Logo Yuran.my putih atas pil biru #2A3B8F (tiada shadow)"],
 [O + g("BA")[0], O + g("BA")[1], "B-roll sistem", "B-ROLL/B-Roll_SistemYuran.my.mp4 @0:31.3: senarai invois ditapis Overdue (merah); callout biru pada lajur Status. Nama pelajar (Items) dan jumlah RM individu diblur"],
 [O + g("BB")[0], O + g("BB")[1], "B-roll sistem", "B-ROLL/B-Roll_SistemYuran.my.mp4 @0:44.3: senarai invois ditapis Paid (hijau) pada “Dikemas kini setiap kali pembayaran masuk”; callout lajur Status, data peribadi diblur"],
 [O + g("TEPAT")[0], O + g("TEPAT")[1], "Kad grafik", "✓ Follow up tepat → ✓ Tak perlu teka-teka"],
 [O + g("REM")[0], O + g("REM")[1], "Motion", "Butang “Hantar reminder” diketuk → “Reminder dihantar ✓” (grafik ringkas, bukan rakaman skrin)"],
 [O + g("CTA")[0], O + g("CTA")[1], "CTA", "Kad profil TikTok Yuran.My Street, link bio yuran.my/daftar/?tiktok diketuk pada “Klik link di bio”"],
 [R["BODY_END"], D, "End card", "Logo putih + Cara MUDAH Urus Yuran + kad profil dengan link bio diketuk + Klik link di bio untuk demo sistem Yuran.my"],
]
sfx = [[round(t, 2), f.replace(".wav", "")] for t, f, gg in R["SFXL"]]
zoom = []
for t, z in R["ZOOM"]:
    zoom.append({"t": round(t + O, 2), "m": "100% (asas)" if z == 1 else f"{round(z*100)}% punch-in"})
SEG = [
 [0, 1.0, "Thumbnail", "Hook SIAPA BELUM BAYAR? + kad status"],
 [1.0, O + 5.32, "Buka buku", "Siapa belum bayar bulan ni? Buka buku, selak, selak, selak. Muzik 1 (tegang)"],
 [O + 5.32, O + 11.38, "Lupa rekod", "Dah bayar tapi lupa rekod, belum bayar tapi lupa reminder"],
 [O + 11.38, O + 20.54, "Segan & tersalah", "Segan nak follow up, takut tersalah: dah bayar tapi kita kata belum"],
 [O + 20.54, O + 29.32, "Status Yuran.my", "Status dalam sistem, dikemas kini setiap kali bayaran masuk, follow up tepat. Muzik bertukar ke muzik 2 (harapan)"],
 [O + 29.32, R["BODY_END"], "Reminder & demo", "Klik reminder terus hantar; klik link di bio untuk demo"],
 [R["BODY_END"], D, "End card", "CTA BOFU: Klik link di bio untuk demo"],
]
DONE = [
 ["Guna video (tiada take ulangan)", "TOFU+BOFU_Siapa_belum_bayar.mp4 (34.7 s, 1080×1920, HEVC). Transkrip tiada take ulangan, jadi dianggap sudah ditrim; isi tidak dipotong (satu jeda 0.47 s selepas “Settle” dikekalkan).", 1.0],
 ["Thumbnail 1 saat", "SIAPA / BELUM / BAYAR? (dari tajuk skrip & ayat pertama) + kad status kecil sebagai hook tambahan. Tiada logo Yuran.my di awal. PNG 1080×1920 berasingan dieksport.", 0.3],
 ["Babak masalah dengan motion", "Buku diselak ikut “selak, selak, selak”, senarai dah bayar/belum bayar dengan ✗, mesej ditaip lalu dipadam (segan), kad “Kita kata vs Sebenarnya”. Semua grafik buatan sendiri tanpa data sebenar.", O + 1.42],
 ["B-roll status sistem", "B-Roll_SistemYuran.my: senarai invois ditapis Overdue (merah) pada “tunjukkan status ni”, kemudian Paid (hijau) pada “Dikemas kini setiap kali pembayaran masuk”. Callout biru pada lajur Status. Nama pelajar & jumlah RM individu diblur.", O + g("BA")[0]],
 ["Muzik berlesen ikut babak", "Babak masalah (0:00–0:21.5): “Echoes”, Andrew Ev — atmosfera tegang. Crossfade 1 s pada “Yuran.my tunjukkan status ni” ke “Discover”, Eugenio Mininni — orchestral pop yang memberi harapan. Mixkit Stock Music Free License. ~24 dB di bawah suara dengan ducking.", O + 20.54],
 ["CTA ikut percakapan", "“Klik link di bio untuk demo sistem Yuran.my” → kad profil TikTok dengan link bio diketuk; end card sama seperti YM-F-006, tanpa emel.", O + g("CTA")[0]],
 ["Caption & ejaan", "1–4 perkataan, Inter ExtraBold. Kata kunci biru: belum bayar, buku, selak, dah bayar, record, reminder, segan-segan, takut, tersalah, Yuran.my, status, dikemas kini, pembayaran, tepat, demo.", 3.0],
 ["Audio", "High-pass 70 Hz, denoise ringan, kompresor lembut, normalize −14.0 LUFS (peak −1.7 dBFS).", None],
]
TODO = [
 ["“Selak, selak, selak” (transkrip: “Select”)", "Dibaca sebagai ‘selak’ (menyelak buku). Sahkan.", 4.64],
 ["“Settle.” dan “Confirm.”", "Perkataan pendek selepas ‘status ni’ (0:24.3) dan ‘tepat’ (0:28.5) didengar ‘Settle’ dan ‘Confirm’. Sahkan.", 24.34],
 ["“collect hutang” (transkrip: “collect utang”)", "Caption tulis ‘hutang’ (ejaan baku). Sahkan.", 14.58],
 ["Video tidak dinyatakan ‘sudah ditrim’", "Transkrip tiada take ulangan atau gagap, jadi saya anggap sudah ditrim dan tidak memotong isi. Beritahu jika ini footage mentah.", None],
 ["Reminder: grafik, bukan rakaman skrin", "Tiada rakaman butang reminder dalam B-ROLL/; dipaparkan butang ringkas “Hantar reminder”. Jika ada rakaman skrin reminder sebenar, beri dan saya ganti.", O + g("REM")[0]],
 ["CTA BOFU: link di bio", "Ikut percakapan (sama seperti YM-F-006). DNA BOFU: ‘Hubungi kami untuk demo sistem Yuran.my’. Tag skrip TOFU+BOFU.", R["BODY_END"] + 0.3],
 ["Muzik dari luar folder MUSIC/", "MUSIC/ masih kosong. Mixkit Echoes (Andrew Ev) & Discover (Eugenio Mininni), Mixkit Stock Music Free License.", O + 20.54],
 ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (ikut DNA seperti YM-F-004..006).", None],
 ["Preview MP4 belum di Drive", "Alat Drive tidak dapat muat naik fail besar. MP4 preview dan thumbnail ada di halaman ini.", None],
]
TT = "Siapa belum bayar bulan ni? Selak buku, dah bayar tapi lupa rekod, belum bayar tapi lupa reminder. Nak follow up pun segan, takut tersalah. Dengan Yuran.my, status bayaran dikemas kini setiap kali bayaran masuk. Klik link di bio untuk demo sistem Yuran.my 👆"
HS = "#sekolahkafa #gurukafa #yuranmy #yuransekolah #kutipanyuran"

data = {"caps": caps, "mg": [[round(a, 2), round(b, 2), k, d] for a, b, k, d in mg], "sfx": sfx, "zoom": zoom, "dur": D}
tpl = open(os.path.join(os.path.dirname(__file__), "ym_f007_template.html")).read()
js = (f"const DATA={json.dumps(data, ensure_ascii=False)};\nconst SEG={json.dumps([[round(a,2),round(b,2),k,d] for a,b,k,d in SEG], ensure_ascii=False)};\n"
      f"const DONE={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in DONE], ensure_ascii=False)};\n"
      f"const TODO={json.dumps([[a,b] + ([round(c,2)] if c is not None else []) for a,b,c in TODO], ensure_ascii=False)};\n"
      f"const TT={json.dumps(TT, ensure_ascii=False)};\nconst HS={json.dumps(HS)};\n")
out = tpl.replace("/*DATA*/", js).replace("{{DUR}}", f"{D:.1f}").replace("{{NQ}}", str(len(TODO)))
open(sys.argv_saved[1], "w").write(out)
json.dump({"data": data, "SEG": SEG, "DONE": DONE, "TODO": TODO, "TT": TT, "HS": HS}, open(sys.argv_saved[1] + ".json", "w"), ensure_ascii=False, indent=1)
print("OK", D, len(caps))
