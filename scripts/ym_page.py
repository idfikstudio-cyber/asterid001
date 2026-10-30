import json,sys
S=sys.argv[1]; m=json.load(open(S+"/edit/tmp540/meta.json"))
FIXES={"kerani":"kranik","admin":"MA","surat":"turat","punya":"pun lah"}
caps=[{"s":round(c["s"],2),"e":round(c["e"],2),"w":[{"t":w,"hl":h,"fix":FIXES.get(w.rstrip("?"))} for w,h in c["w"]]} for c in m["caps"]]
G={"label":"Label nama","rows":"Kad senarai","broll":"B-roll sistem","callout":"Callout","chip":"Chip ikon","pile":"B-roll animasi","timebar":"Bar masa","comment":"Gelembung komen"}
D={"label":"Farhan · Yuran.my (pil biru, atas-kiri)","rows":None,"broll":"Senarai invois Yuran.my (demo), nama/item & jumlah individu diblur, zoom perlahan ke lajur Status",
"callout":"Tally ke tak? + kotak sorotan lajur PAID/UNPAID","chip":"↻ Ulang setiap hari","pile":"Animasi sendiri: resit, rekod yuran & surat bertimbun, jam berpusing laju",
"timebar":"Waktu mengajar: bar biru dimakan 'dicuri kerja admin'","comment":"Setuju atau tak setuju? Kongsi pendapat di ruang komen"}
ROWS={2.8:"Rutin harian cikgu: Pagi kutip yuran / Tengah hari buat resit / Petang buat syllabus / Malam kira yuran",17.95:"Bila waktunya? Fokus buat syllabus / Fokus buat PnP / PnP berkualiti",36.95:"Cikgu KAFA: ✓ Mendidik / ✗ Kerani sekolah (dipangkah)"}
mg=[[0,1.0,"Thumbnail","CIKGU KAFA atau KERANI? atas frame Farhan menunjuk (sumber 1:22.9)"]]
for t0,t1,k in m["gfx"]: mg.append([round(t0,2),round(t1,2),G[k],ROWS.get(round(t0,2)) if k=="rows" else D[k]])
mg.append([round(m["end0"],2),round(m["dur"],2),"End card","Logo putih atas biru #2A3B8F, Cara MUDAH Urus Yuran, Follow untuk tips urus yuran sekolah, hello@yuran.my"])
mg.sort()
cuts=[1.0];[cuts.append(cuts[-1]+b-a) for a,b in m["edl"]]
zoom=[{"t":round(cuts[i],2),"m":("130% punch-in" if z>1.2 else "115% (asas)")} for i,z in enumerate(m["zoom"])]
data={"caps":caps,"mg":mg,"sfx":[[round(t,2),n] for t,n,g in m["sfx"]],"zoom":zoom,"dur":round(m["dur"],2)}
E=round(m["end0"],2)
SEG=[[0,1.0,"Thumbnail","CIKGU KAFA atau KERANI?"],[1.0,2.97,"Hook","Cikgu KAFA ataupun kerani sebenarnya? Label Farhan · Yuran.my"],
[2.97,13.75,"Rutin harian","Kad rutin pagi→malam, B-roll sistem 'Tally ke tak?'"],[13.75,17.96,"Ulang setiap hari","Chip ↻ Ulang setiap hari"],
[17.96,29.91,"Bila waktunya?","Kad 3 soalan: syllabus, PnP, PnP berkualiti"],[29.91,36.93,"Kerja admin curi waktu","B-roll animasi resit bertimbun, bar Waktu mengajar"],
[36.93,41.03,"Mendidik, bukan kerani","Kad ✓ Mendidik / ✗ Kerani sekolah"],[41.03,E,"Ajak komen","Gelembung Setuju atau tak setuju?"],[E,data["dur"],"End card","CTA TOFU + hello@yuran.my"]]
DONE=[["Footage mentah: take ulangan dibuang","92.1 s mentah jadi 41.8 s isi. Dibuang: take pertama 'Pagi kutip yuran', dua take awal 'malam pula kira yuran', mula palsu 'Bila sebenarnya', 'bila… bila sepatutnya, bila' yang tersangkut, tiga take awal 'Kerja admin…', dan semua senyap lebih 0.3 s (padding 0.1 s). Susunan ayat tidak diubah.",2.97],
["Durasi dalam sasaran TOFU","44.3 s = thumbnail 1 s + isi 41.8 s + end card 1.5 s (sasaran 20–45 s)."],
["Thumbnail 1 saat","CIKGU KAFA / atau / KERANI? (KERANI biru aksen) atas frame Farhan menunjuk ke kamera. Tiada logo di awal. PNG berasingan dieksport.",0.3],
["Punch-in & framing","Asas 115%, punch-in 130% setiap 2–3 potongan (12 potongan). Mata di sepertiga atas frame."],
["Caption","Sepanjang video, 1–3 perkataan, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2: KAFA, kerani, yuran, resit, tally, fokus, berkualiti, admin, senyap-senyap, curi, mendidik, komen. Dalam safe zone (atas 80%, luar jalur kanan 15%). Atas B-roll, caption dapat pil biru gelap.",11.0],
["B-roll & privasi","B-roll sistem dari B-ROLL/Sek-Integrasi-Demo-Yuran.My (2.8 s). Lajur nama/item dan jumlah individu diblur; hanya Status PAID/UNPAID dan butang kelihatan. B-roll kedua ialah animasi yang saya jana sendiri (berlesen penuh, tiada stok luar).",10.6],
["Brand","Biru #2A3B8F + aksen #29ABE2, logo putih atas latar biru (tiada shadow/lutsinar), tiada aset Fi-k Studio atau Aster. Tiada harga, statistik atau tawaran ditambah.",43.0],
["End card TOFU","Logo Yuran.my putih, 'Cara MUDAH Urus Yuran', CTA 'Follow untuk tips urus yuran sekolah', hello@yuran.my.",43.0],
["Audio","Denoise ringan, compressor, −13.9 LUFS, true peak −1.7 dBTP. Muzik sekitar 21–25 dB bawah suara dengan ducking."]]
TODO=[["\"Kerja admin\"?","Whisper dengar 'Kerja MA / AMA'. Saya tulis 'admin' ikut konteks. Sila dengar dan sahkan.",30.0],
["\"Malam pula update surat\"?","Tiga transkrip dengar 'durat / turat / jurat'. Caption tulis 'surat' (paling hampir dari segi bunyi). Baris ini tidak dimasukkan dalam kad rutin sehingga disahkan.",8.6],
["\"Pagi tadi punya collection\"","Transkrip dengar 'pula' / 'pun lah'. Caption guna 'punya'. Sahkan.",12.5],
["Buang 'bila sepatutnya, bila'","Antara 'untuk mengajar' dan 'bila waktu cikgu…' Farhan tersangkut ('bila… bila sepatutnya, bila,'). Saya buang dan sambung terus ke 'bila waktu cikgu nak pastikan…'. Sahkan atau minta dikembalikan.",25.06],
["Ejaan PnP","Disebut 'P-N-P'. Caption 'PnP'. Jika mahu istilah rasmi 'PdP', beritahu.",23.5],
["Muzik dijana sendiri","Folder MUSIC/ Yuran.my tiada; Farhan pilih muzik jana sendiri (scripts/music.py: korporat ringan, C–Am–F–G, 100 BPM, bebas hak cipta)."],
["Tiada video rujukan gaya","BRAND/ tiada rujukan-gaya-*.mp4. Diedit ikut DNA Yuran.my sahaja (Farhan setuju)."],
["Logo resolusi rendah","Logo Yuran White.png hanya 250×150 (logo sebenar ~197×65 px), jadi end card besarkan ~2.4×. Untuk final 1080p lebih tajam jika ada logo PNG/SVG besar."],
["Footage 720×1280","Sumber 720p. Final 1080×1920 akan di-upscale + zoom 115–130%, jadi sedikit lembut."],
["Gambar 'Pecah masuk KAFA' tidak digunakan","4 gambar berita kecurian di B-ROLL/ tidak sesuai: video ini tidak menyebut kecurian/tunai, jadi guna gambar itu akan menambah fakta. Ada juga muka suspek dan nama sekolah."],
["Preview MP4 belum di Drive","Alat Drive yang saya ada tidak dapat muat naik fail video besar. RINGKASAN dan log sudah dimuat naik; MP4 preview ada di halaman ini."]]
TT="Cikgu KAFA masuk untuk mendidik, bukan jadi kerani sekolah. Pagi kutip yuran, tengah hari buat resit, malam kira collection… bila masa nak fokus PnP? Setuju ke tak setuju? Komen di bawah."
HS="#cikgukafa #sekolahkafa #yuranmy #kerjaadmin #cikgu"
tpl=open(S+"/page_tpl.html").read()
out=(tpl.replace("__DATA__",json.dumps(data,ensure_ascii=False)).replace("__SEG__",json.dumps(SEG,ensure_ascii=False))
 .replace("__DONE__",json.dumps(DONE,ensure_ascii=False)).replace("__TODO__",json.dumps(TODO,ensure_ascii=False))
 .replace("__TT__",json.dumps(TT,ensure_ascii=False)).replace("__HS__",json.dumps(HS)).replace("__DUR__",str(data["dur"])))
open(S+"/art/index.html","w").write(out)
json.dump({"caps":caps,"mg":mg,"sfx":data["sfx"],"todo":TODO,"tt":TT,"hs":HS},open(S+"/art/ringkasan.json","w"),ensure_ascii=False)
print("ok")
