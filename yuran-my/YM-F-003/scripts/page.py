# plan.json -> preview/index.html (halaman Artifact) + RINGKASAN.txt
import json, sys
P = json.load(open(sys.argv[1]))
out_html, out_txt = sys.argv[2], sys.argv[3]
DUR = P["duration"]
FIXES = {"Dari": "Hari", "tanya": "yang"}   # perkataan dibetulkan dari transkrip -> asal
caps = []
for c in P["captions"]:
    caps.append({"s": c["s"], "e": c["e"], "w": [{"t": w["w"], "hl": bool(w.get("hot")), "fix": FIXES.get(w["w"])} for w in c["words"]]})
KIND = {"thumb": "Thumbnail", "label": "Label nama", "versus": "Kad dua pihak", "versus-ok": "Kad dua pihak", "chip": "Chip ikon",
        "broll-book": "B-roll motion", "notfound": "Ikon", "broll-ledger": "B-roll motion", "logo": "Logo", "broll-screen": "B-roll",
        "broll-search": "B-roll motion", "broll-video": "B-roll app", "callout": "Callout", "cta-bio": "Panduan link bio", "endcard": "End card"}
mg = [[g["s"], g["e"], KIND[g["kind"]], g["note"] + (f" — “{g['text']}”" if g.get("text") else "")] for g in P["graphics"]]
sfx = [[s["t"], s["name"]] for s in P["sfx"]]
zoom = [{"t": round(z["src"] + P["t0"], 2), "m": ("115% punch-in" if z["scale"] > 1.1 else "105% (asas)")} for z in P["zoom"]]
SEG = [[0, 1.0, "Thumbnail", "DAH BAYAR, TAPI TIADA REKOD? atas frame Farhan (sumber 0:05.3)"],
       [1.0, 7.86, "Konflik", "Ibu bapa ✓ Dah bayar vs Cikgu ✗ Belum bayar, “?” pada Siapa betul. Label Farhan · Yuran.my"],
       [7.86, 13.9, "Cari resit", "B-roll motion: buku resit diselak Jan → Okt, kemudian resit bertaburan + kanta + cop TAK JUMPA (tutup saat Farhan tunduk)"],
       [13.9, 25.9, "Tegang", "Punch-in pada emosi: tegang, tertuduh, tak dipercayai, tak amanah"],
       [25.9, 32.94, "Punca: rekod manual", "Chip Resit tak dibuat, B-roll motion buku rekod manual"],
       [32.94, 37.1, "Dengan Yuran.my", "Logo putih atas pil biru, B-roll invois sistem (status PAID, data diblur)"],
       [37.1, 45.6, "Resit automatik", "B-roll app Yuran.my sebenar: senarai Payments → ketuk → resit PDF (data diblur), chip app ibu bapa, B-roll dashboard cikgu (angka diblur)"],
       [45.6, 47.96, "Tiada siapa disalahkan", "Kad Ibu bapa ✓ Cikgu ✓ (ulang motif awal)"],
       [47.96, 49.646, "CTA link di bio", "Kad profil TikTok, jari ketuk yuran.my/daftar/?tiktok"],
       [49.646, DUR, "End card", "Logo + Cara MUDAH Urus Yuran + Klik link di bio + hello@yuran.my"]]
DONE = [["Guna video trim Farhan", "TOFU+BOFU_Dahbayar_tapi_tiada_rekod.mp4 (48.6 s, 1080×1920). Isi tidak dipotong; tiada take ulangan.", 1.0],
        ["Thumbnail 1 saat", "DAH BAYAR, / TAPI TIADA / REKOD? (dari tajuk skrip) atas frame Farhan bertanya (sumber 0:05.3). Tiada logo di awal. PNG 1080×1920 berasingan dieksport.", 0.3],
        ["Caption", "Sepanjang video, 1–4 perkataan ikut ritma, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2 (resit, rekod, automatik, manual, Yuran.my, dashboard, tegang, tertuduh…). Dalam safe zone (atas 20% bawah, kiri dari 15% kanan); semasa CTA caption turun sedikit supaya jari ketuk link kelihatan.", 3.0],
        ["B-roll dari folder brand", "B-Roll_SistemYuran.my.mp4: senarai invois (0:29, zoom ke status PAID) dan dashboard (0:01). Nama pelajar, no. IC, no. invois, jumlah yuran dan semua angka statistik diblur. Setiap sisipan ≤3 s, suara terus berjalan.", 34.2],
        ["v2: B-roll pada saat Farhan tunduk", "Komen Farhan: pada “paling latest” (0:11.9–0:13.9) Farhan tidak memandang kamera. Kini ditutup dengan B-roll motion baru: resit bertaburan atas meja, kanta mencari, cop TAK JUMPA tepat pada “Tak jumpa”. Wajah kembali pada “Suasana jadi tegang”.", 12.2],
        ["v2: B-roll app Yuran.my sebenar", "Komen Farhan: pada “Lepas pembayaran diterima, resit automatik dihantar” kini guna B-ROLL/Apps Yuran.my.MP4 dalam bingkai telefon: senarai Payments, jari ketuk resit (0:43.6–0:45.0), resit PDF dibuka (0:46.5–0:48.1) dan kad resit di-zoom + callout “Resit dalam app Yuran.my”. Nama pembayar, emel, telefon, nama pelajar/IC, jumlah dan key transaksi diblur. 3.0 s.", 37.1],
        ["B-roll tambahan berlesen", "Klip stok percuma yang ditemui (Mixkit dokumen/kertas) rupanya Restricted License (peribadi sahaja), jadi tidak digunakan. B-roll motion dibuat sendiri (hak milik penuh): buku resit diselak, resit bertaburan + TAK JUMPA, buku rekod manual. Tiada data sebenar.", 8.0],
        ["Muzik luar berlesen", "MUSIC/ kosong. Dicari di Mixkit: “Minimal Emotion” (Alejandro Magaña) untuk babak masalah, bertukar ke “Motivating Mornings” (Ahjay Stelino) pada “Dengan Yuran.my”. Kedua-dua Mixkit Stock Music Free License: komersial termasuk media sosial, tiada atribusi.", 32.9],
        ["CTA: cara klik link di bio TikTok", "Pada “Nak demo? Klik link di bio”: kad profil TikTok (BRAND/Yuran Tiktok.jpg), jari bergerak dan ketuk yuran.my/daftar/?tiktok dengan riak. End card ulang dengan sorotan berdenyut pada link. Bilangan following/followers/likes diblur.", 48.0],
        ["Brand", "Biru #2A3B8F + aksen #29ABE2, logo putih atas latar biru tanpa shadow/watermark, tiada aset Fi-k Studio atau Aster. Tiada harga, diskaun atau statistik direka.", 33.0],
        ["Audio", "High-pass, denoise ringan, normalize −14.0 LUFS (true peak −4.1 dBTP). Muzik 24 dB di bawah suara dengan ducking; naik pada thumbnail & end card."]]
TODO = [["“Dari helai demi helai” (transkrip: “Hari”)", "Bunyi awal ayat kurang jelas; mungkin “Cari helai demi helai”. Caption guna “Dari”. Beritahu jika perkataan sebenar lain.", 8.9],
        ["“Tak payah datang tanya cikgu” (transkrip: “yang”)", "Whisper dengar “datang yang cikgu”; dengan konteks dibaca “tanya”. Sahkan perkataan sebenar.", 42.6],
        ["“But itulah masalah”", "Perkataan pertama pendek dan kurang jelas (“But”/“Tapi”). Caption ikut transkrip: “But”.", 27.9],
        ["CTA klik link di bio, bukan CTA DNA", "Skrip bertag TOFU+BOFU. DNA: TOFU “Follow untuk tips…”, BOFU “Hubungi kami untuk demo”. Ikut arahan Farhan, CTA = klik link di bio (seperti disebut “Nak demo? Klik link di bio”). hello@yuran.my kekal di end card.", 48.5],
        ["Link bio yuran.my/daftar/?tiktok", "Dari screenshot BRAND/Yuran Tiktok.jpg. Sahkan link masih sama di profil TikTok.", 50.0],
        ["Durasi 51.1 s", "Melebihi sasaran TOFU (20–45 s) tetapi dalam sasaran BOFU (30–60 s). Isi tidak dipotong."],
        ["Muzik dari luar folder MUSIC/", "MUSIC/ Yuran.my kosong dan Farhan minta carian luar. Cadangan: simpan kedua-dua lagu Mixkit dalam MUSIC/ sebagai rekod lesen."],
        ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (Farhan setuju teruskan ikut DNA). Gaya ikut YM-F-001/002 yang diluluskan."],
        ["Gambar ‘Pecah masuk KAFA’ tidak digunakan", "Topik video ialah rekod bayaran, bukan kecurian; gambar berita itu juga memaparkan nama sekolah."],
        ["Preview MP4 belum di Drive", "Alat Drive yang ada tidak dapat muat naik fail video/gambar besar. RINGKASAN dan log dimuat naik; MP4 preview dan thumbnail ada di halaman ini dan dalam chat."]]
TT = "Ibu bapa kata dah bayar, cikgu kata belum. Buku resit diselak helai demi helai, tak jumpa. Rupanya resit lupa nak buat. Dengan Yuran.my, setiap bayaran direkod dan resit automatik dihantar. Nak demo? Klik link di bio."
HS = "#yuransekolah #sekolahkafa #yuranmy #gurukafa #ibubapa"
data = {"caps": caps, "mg": mg, "sfx": sfx, "zoom": zoom, "dur": DUR}
J = lambda x: json.dumps(x, ensure_ascii=False)
h = open(sys.argv[4]).read()
for k, v in {"__DATA__": J(data), "__SEG__": J(SEG), "__DONE__": J(DONE), "__TODO__": J(TODO), "__TT__": J(TT), "__HS__": J(HS),
             "__DUR__": f"{DUR:.1f}", "__NSFX__": str(len(sfx))}.items():
    h = h.replace(k, v)
open(out_html, "w").write(h)

def fmt(t): return f"{int(t // 60)}:{t % 60:04.1f}"
L = ["RINGKASAN — YM-F-003_Dahbayar_tapi_tiada_rekod (PREVIEW v2, 30/10/2026)", f"Spokesperson: Farhan · Tag: TOFU+BOFU · Durasi: {DUR:.1f} s · Preview 540x960", "",
     "1. TEKS HOOK / THUMBNAIL", "   DAH BAYAR, / TAPI TIADA / REKOD?  (frame sumber 0:05.3, 1 saat, tiada logo)", "",
     "2. CAPTION PENUH (ikut percakapan)"]
L += [f"   {fmt(c['s'])}  " + " ".join(w["w"] for w in c["words"]) for c in P["captions"]]
L += ["", "3. SFX, ANIMASI & B-ROLL (masa video)"]
ev = sorted([(g[0], f"{g[2]}: {g[3]} (hingga {fmt(g[1])})") for g in mg] + [(s[0], f"SFX: {s[1]}") for s in sfx])
L += [f"   {fmt(t)}  {d}" for t, d in ev]
L += ["", "4. CTA", "   Klik link di bio (panduan ketuk profil TikTok yuran.my/daftar/?tiktok) + end card: logo putih, Cara MUDAH Urus Yuran, hello@yuran.my", "",
      "5. PERLU SEMAK"]
L += [f"   - {t[0]}: {t[1]}" for t in TODO]
L += ["", "6. CAPTION TIKTOK + HASHTAG", "   " + TT, "   " + HS, "",
      "MUZIK: Minimal Emotion (Alejandro Magaña) + Motivating Mornings (Ahjay Stelino), Mixkit Stock Music Free License.",
      "FONT: Inter (ganti Acumin Pro, tiada dalam sistem)."]
open(out_txt, "w").write("\n".join(L) + "\n")
