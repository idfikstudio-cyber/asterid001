# Bina halaman preview Artifact YM-F-007 (susun atur sama seperti YM-F-001..006).
# usage: python3 ym_f007_page.py <out.html> [lufs-text]
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
full = open(os.path.join(HERE, "ym_f007_render.py")).read()
src = full.split("# ---------- frames sumber")[0]
src = src.replace("SRC, AS, SFX, MUS, OUT = sys.argv[1:6]", "SRC=AS=SFX=MUS=OUT=''").replace("W = int(sys.argv[6])", "W = 1080")
src = src.replace("CRF = sys.argv[7] if len(sys.argv) > 7 else \"20\"", "CRF='20'").replace("os.makedirs(OUT, exist_ok=True)", "")
src += "\nTAP = 0.80\n" + full[full.index("SFXL = ["):full.index("def audio")]
R = {}; exec(src, R)
O = R["OFF"]; D = round(R["TOTAL"], 3); BE = R["BODY_END"]
LUFS = sys.argv[2] if len(sys.argv) > 2 else "−14.0 LUFS, peak −1.4 dBFS."

caps = []
for a, b, s in R["CAP"]:
    w = []
    for i, p in enumerate(s.split("*")):
        for t in p.split():
            fx = "Otober (transkrip)" if t.strip(".,?") == "Oktober" else None
            w.append({"t": t, "hl": i % 2 == 1, "fix": fx})
    caps.append({"s": round(a + O, 2), "e": round(b + O, 2), "w": w})

DESC = {
 "dash": "dashboard atas (Good Morning, 200 Active Asset, 1 Active Event)",
 "ovd": "kad Overdue: 43 Overdue Invoices, RM 6,450 Overdue Amount, 4 Average Days Overdue",
 "oct": "Collection Stats by Month (pilihan bulan)", "jun": "Jun 2026: RM 0, 0.00%",
 "jul": "Julai 2026: RM 2,600, 100.00%", "aug": "Ogos 2026: RM 8,750, 100.00%",
 "sep": "September 2026: RM 34,300, 100.00%", "oct2": "Oktober 2026: RM 21,500, 68.75%",
}
BRT = {"dash": "0:02", "ovd": "0:54", "oct": "1:01", "jun": "1:14", "jul": "1:26", "aug": "1:44", "sep": "1:56", "oct2": "2:20"}
mg = [[0, 1.0, "Thumbnail", "Thumbnail 1 s: PANTAU yuran / dalam / 2 MINIT (kotak biru aksen) + potongan dashboard telefon (September 100%), atas frame Farhan pegang handphone (sumber 0:25.3)"],
      [O + R["LABEL_IN"], O + R["LABEL_OUT"], "Label nama", "Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"],
      [O + R["CARD_TP"][0], O + R["CARD_TP"][1], "Kad grafik", "Tak payah tunggu → ✗ Admin → ✗ Kerani → ✗ Siapa-siapa"],
      [O + R["CARD_DEV"][0], O + R["CARD_DEV"][1], "Kad grafik", "Check sendiri guna → [Handphone] → [Tablet] → [Komputer] → ✓ Apa sahaja device + internet"]]
for a, b, txt, sub in R["NUMS"]:
    mg.append([O + a, O + b, "Angka", "“" + txt.replace("*", "") + "” teks besar" + (f" + “{sub}”" if sub else "")])
for a, b, key, rings in R["BR"]:
    labs = [l for _, _, l in rings if l]
    mg.append([O + a, O + b, "B-roll Pantau Yuran", f"B-Roll Pantau Yuran.mp4 ({BRT[key]}): {DESC[key]}; zoom perlahan + callout biru" + (" + pil " + ", ".join(f"“{l}”" for l in labs) if labs else "")])
mg.append([O + R["CMT_IN"], O + R["CMT_OUT"], "Motion komen", "Panel komen: “Nak tengok cara follow up?” → “Nak” ditaip → butang hantar berdenyut, pada “Nak saya tunjuk tak? Macam mana nak follow up?”"])
mg.append([BE, D, "End card", "Logo putih + Cara MUDAH Urus Yuran + kad profil TikTok @yuran.my, + Follow ditekan jadi Following ✓ + Follow TikTok Yuran.my untuk tips urus yuran sekolah"])
mg.sort(key=lambda x: x[0])
sfx = [[round(t, 2), f.replace(".wav", "")] for t, f, gn in R["SFXL"]]
zoom = [{"t": round(t + O, 2), "m": "100% (asas)" if z == 1 else f"{round(z*100)}% punch-in"} for t, z in R["ZOOM"]]
SEG = [
 [0, 1.0, "Thumbnail", "Hook PANTAU YURAN DALAM 2 MINIT + dashboard telefon"],
 [1.0, O + 11.26, "Hook & device", "2 minit; tak payah tunggu admin/kerani; check sendiri guna handphone, tablet, komputer"],
 [O + 11.26, O + 25.02, "Dashboard", "Pantau prestasi yuran: unpaid, overdue, berapa lama overdue (B-roll dashboard & overdue)"],
 [O + 25.02, O + 43.58, "Demo handphone", "Login → 200 pelanggan, 1 program, view overdue (B-roll)"],
 [O + 43.58, O + 53.44, "Bulanan collection", "Pilih bulan; Jun belum guna sistem: tiada rekod"],
 [O + 53.44, O + 75.06, "Julai–September", "Julai 100%, Ogos peningkatan 100%, September peningkatan 100%, tiada overdue"],
 [O + 75.06, O + 83.44, "Oktober", "Hampir 70% dikutip, tinggal 30%"],
 [O + 83.44, BE, "Follow up?", "Nak saya tunjuk cara follow up? (motion komen) + gurauan sakit perut"],
 [BE, D, "End card", "CTA TOFU Follow TikTok @yuran.my"],
]
DONE = [
 ["B-roll “B-Roll Pantau Yuran” (arahan Farhan)", "Rakaman skrin telefon diselitkan pada setiap perkara yang Farhan terangkan semasa demo: dashboard, unpaid/overdue (43 invois), berapa lama overdue (4 hari purata), 200 pelanggan, 1 program, Collection Stats by Month, Jun (RM 0), Julai 100%, Ogos & September (peningkatan), Oktober 68.75% (“hampir 70%”). Setiap sisipan ≤ 3 s, zoom perlahan dan callout biru pada kad yang disebut; suara terus berjalan. Notifikasi WhatsApp yang muncul dalam rakaman (2:32) tidak digunakan.", O + R["BR"][0][0]],
 ["Guna video trim Farhan", "TOFU_PantauYuran.mp4 (90.7 s, 1080×1920, HEVC). Tiada take ulangan; satu jeda 0.31 s sahaja (0:43.3), isi tidak dipotong.", 1.0],
 ["Thumbnail 1 saat", "PANTAU yuran dalam 2 MINIT (dari tajuk skrip & ayat pertama) + potongan dashboard telefon. Tiada logo di awal. PNG 1080×1920 dieksport.", 0.3],
 ["Angka tepat seperti disebut", "2 minit, 200 pelanggan, 100% (Julai, Ogos, September), hampir 70%, 30%. Angka RM pada skrin B-roll tidak dijadikan teks besar kerana tidak disebut.", O + 1.1],
 ["Caption", "Sepanjang video, 1–4 perkataan, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2: pantau yuran, 2 minit, dashboard, unpaid, overdue, 200, nama bulan, 100%, 70%, 30%, peningkatan, record/data, follow up.", 3.0],
 ["End card TOFU", "CTA Follow TikTok @yuran.my, gaya YM-F-004 hingga 006 yang diluluskan.", BE + 0.3],
 ["Audio", "High-pass 70 Hz, denoise ringan, kompresor lembut, normalize −14 LUFS; muzik ~24 dB di bawah suara dengan ducking.", None],
]
TODO = [
 ["Durasi 93.2 s melebihi TOFU (20–45 s)", "Isi tidak dipotong. Jika mahu pendekkan, Farhan boleh pilih bahagian untuk dibuang, contohnya gurauan penutup (1:26.8–1:31.4) atau ulangan “bila kita semak pada bulan Jun”.", None],
 ["Gurauan sakit perut / “nak membuang” di penutup", "“Sebab tengah sakit perut ni. Nak membuang jap. Saya follow up dalam toilet lah eh.” dikekalkan kerana video sudah ditrim. DNA Yuran.my minta nada sopan & profesional; sahkan Farhan selesa ia kekal dalam video akaun syarikat.", O + 85.82],
 ["Data dalam B-roll Pantau Yuran", "Angka agregat akaun (200 aset, RM 21,500, RM 6,450 overdue dan lain-lain) dipaparkan tanpa blur. Tiada nama pelajar atau nombor telefon kelihatan. Sahkan akaun ini akaun demo, atau pelanggan setuju angka dipaparkan.", O + R["BR"][0][0]],
 ["“200 pelanggan” vs “Active Asset”", "Farhan sebut 200 pelanggan; kad dalam sistem berlabel “200 ACTIVE ASSET”. Pil tulis “200 pelanggan” ikut apa yang disebut.", O + 35.1],
 ["“Oktober” (transkrip: “Otober”)", "Caption guna ejaan baku ‘Oktober’.", O + 75.06],
 ["“hampir 70%” vs skrin 68.75%", "Teks ikut apa yang disebut (“hampir 70%”); skrin menunjukkan 68.75%, selari dengan ‘hampir’.", O + 79.5],
 ["Muzik dari luar folder MUSIC/", "MUSIC/ Yuran.my kosong. Guna “Dreaming Big” (Ahjay Stelino), Mixkit Stock Music Free License, sama seperti YM-F-005/006.", None],
 ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (Farhan setuju ikut DNA untuk video sebelum ini).", None],
 ["Preview MP4 belum di Drive", "Alat Drive tidak dapat muat naik fail video besar. RINGKASAN dimuat naik ke 02_EDITED/_PREVIEW; MP4 preview dan thumbnail ada di halaman ini.", None],
]
TT = "Pantau yuran dalam 2 minit je, tak payah tunggu admin atau kerani. Buka dashboard Yuran.my guna handphone: berapa unpaid, berapa overdue, kutipan setiap bulan. Nak tengok cara follow up? Comment “nak” 👇"
HS = "#yuranmy #yuransekolah #sekolahkafa #pantauyuran #dashboard"

data = {"caps": caps, "mg": [[round(a, 2), round(b, 2), k, d] for a, b, k, d in mg], "sfx": sfx, "zoom": zoom, "dur": D}
tpl = open(os.path.join(HERE, "ym_f007_template.html")).read()
r2 = lambda L: [[a, b] + ([round(c, 2)] if c is not None else []) for a, b, c in L]
js = (f"const DATA={json.dumps(data, ensure_ascii=False)};\nconst SEG={json.dumps([[round(a,2),round(b,2),k,d] for a,b,k,d in SEG], ensure_ascii=False)};\n"
      f"const DONE={json.dumps(r2(DONE), ensure_ascii=False)};\nconst TODO={json.dumps(r2(TODO), ensure_ascii=False)};\n"
      f"const TT={json.dumps(TT, ensure_ascii=False)};\nconst HS={json.dumps(HS)};\n")
out = tpl.replace("/*DATA*/", js).replace("{{DUR}}", f"{D:.1f}").replace("{{NQ}}", str(len(TODO))).replace("{{LUFS}}", LUFS)
open(sys.argv[1], "w").write(out)
json.dump({"data": data, "SEG": SEG, "DONE": DONE, "TODO": TODO, "TT": TT, "HS": HS}, open(sys.argv[1] + ".json", "w"), ensure_ascii=False, indent=1)
print("OK", D, len(caps))
