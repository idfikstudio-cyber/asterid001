import json,re
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad"
caps=json.load(open(f"{S}/a12/work/caps.json"))
FIX={"pecahan":"Jahang","perpuluhan":"pepuhang","kuatkan":"buatkan"}
C=[{"s":s,"e":e,"w":[{"t":w.lstrip("*"),"hl":w.startswith("*"),"fix":FIX.get(re.sub(r"\W","",w.lstrip("*"))),"q":False} for w in txt.split()]} for s,e,txt in caps]
sfx=[[x["t"],x["name"]] for x in json.load(open(f"{S}/a12/work/sfx.json"))]
MG=[[0,1.0,"Thumbnail","TINGKATAN 1 / ALGEBRA MENUNGGU! + pil Kelas Sabtu PERCUMA"],
[0,24.58,"Watermark","asteredu11.com.my sepanjang video (termasuk thumbnail & end card), putih ±40% + bayang halus, atas-kiri 11%"],
[1.0,2.9,"Kad kertas","Siapa ada anak · Tingkatan 1?"],[1.3,4.3,"Label nama","Wajah bulatan emas + Cikgu AlFarhan"],
[2.96,6.36,"Papan hitam","ALGEBRA · x + 5 = 12 ditulis huruf demi huruf"],[4.64,6.36,"Cip","Pecahan 4.6 · Perpuluhan 5.2 · Peratus 5.8"],
[6.38,8.95,"Nota kertas","Kalau asas... ✗ Darjah 6 lemah lagi (7.6)"],[6.6,8.95,"CTA Follow","Wajah bulatan emas + Cikgu AlFarhan + @aster.edu_tpg + Follow saya (TOFU)"],
[9.0,12.8,"Teks besar","TINGKATAN 1 · step paling NGERI (11.8)"],[12.82,14.0,"Pil kuning","Sekarang masa terbaik ✓"],
[14.04,16.3,"B-roll (2.3 s)","Kad pencapaian pelajar Aster April 2026: Tingkatan 1 (Testimoni 8) → Tingkatan 3 (Testimoni 3) → Tingkatan 4 Teras (Testimoni 9); latar gelap, zoom perlahan; suara terus berjalan"],
[16.42,19.8,"Pil merah","Pendaftaran 2027 dibuka (mula jualan)"],[16.42,17.6,"Lower third","MATH TURBO 2027 · Tuisyen online bersama Cikgu AlFarhan"],
[17.26,19.8,"Kad","Kelas hari Sabtu · PERCUMA · untuk pelajar sekolah menengah (18.4)"],[19.82,21.1,"Pil kuning","Kuatkan ALGEBRA ✓"],[21.18,23.08,"Pil","DM saya"],
[23.08,24.58,"End card","Hitam + kuning: wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
ZOOM=[(0,"112% (thumbnail)"),(1.0,"106%"),(4.64,"112% punch-in"),(6.38,"106%"),(9.0,"113% punch-in"),(12.82,"106%"),(14.04,"B-roll penuh skrin"),(16.42,"111% punch-in"),(19.82,"106%"),(21.18,"112% punch-in")]
SEG=[[0,1.0,"Thumbnail","TINGKATAN 1 / ALGEBRA MENUNGGU!"],[1.0,6.38,"Tingkatan 1","Siapa ada anak Tingkatan 1? · papan ALGEBRA · pecahan, perpuluhan, peratus"],
[6.38,12.82,"Masalah","Asas Darjah 6 lemah · CTA Follow · step paling NGERI"],[12.82,16.42,"Masa terbaik","Sekarang masa terbaik · B-roll kad pencapaian pelajar"],
[16.42,21.18,"Kelas percuma","Pendaftaran 2027 dibuka · MATH TURBO 2027 · Kelas Sabtu PERCUMA untuk sekolah menengah · kuatkan algebra"],[21.18,23.08,"CTA","DM saya"],[23.08,24.58,"End card","CTA BOFU WhatsApp + asteredu11.com.my"]]
TODO=[["B-roll kad pencapaian: nama penuh & markah kelihatan","Farhan sahkan wajah boleh dipapar. Kad juga menunjukkan nama penuh pelajar dan markah (tidak diblur). Beritahu jika nama perlu diblur. Markah tidak disebut Cikgu; ia sebahagian daripada gambar bukti.",14.04],
["Kad PERCUMA: 'untuk pelajar sekolah menengah'","Dipapar seperti disebut. Dalam AS-F-009 Cikgu sebut kelas Sabtu percuma 'untuk pelajar yang berdaftar dengan kami sahaja'. Sila sahkan dua kenyataan ini selari.",18.42],
["'kuatkan algebra'","Transkrip utama 'buatkan algebra'; semakan kedua (large-v3) 'kuatkan algebra'. Caption guna 'kuatkan'.",19.82],
["Lower third MATH TURBO 2027 + pil Pendaftaran 2027 dibuka","Ikut DNA HYBRID dan AS-F-010 yang diluluskan.",16.42],
["Durasi 24.6 s","Bawah sasaran BOFU 30–60 s. Isi tidak dipanjangkan.",None],
["Fail video tidak dapat dimuat naik ke Drive","Had 10 MB connector; preview + thumbnail ada dalam halaman ini.",None]]
DONE=[["Tag TOFU+BOFU → gaya HYBRID hitam + kuning","Ikut TOFU+BOFU_Sifir9 dan AS-F-010: papan hitam algebra, nota kertas, CTA Follow tengah video, lower third + pil Pendaftaran 2027 dibuka, end card CTA BOFU.",2.96],
["B-roll testimoni baru","Kad pencapaian sebenar dari B-ROLL (disahkan Farhan boleh guna). 2.3 s, bawah had 3 s; tidak menutup thumbnail atau baris hook.",14.04],
["Disemak dengan transkrip kedua","'Jahang, pepuhang' → pecahan, perpuluhan (dengan prompt konteks).",4.64],
["Jenis footage: sudah ditrim","Satu take tanpa ulangan; tiada senyap > 0.3 s. Audio dikekalkan hingga hujung rakaman (22.08 s) supaya 'lanjut' tidak terpotong.",21.7],
["Masa SFX disahkan","Senarai SFX khas video ini (disemak selepas dijana, berbeza dari AS-F-009/010/011).",None],
["Muzik rasmi Aster","Aster_MuzikLatar_Ceria_100BPM. Tiada kredit perlu.",2.0],
["Wajah Cikgu, bukan logo · safe zone","Bulatan emas guna Logo SocMed Aster; teks di atas 80% frame dan di luar jalur kanan 15%.",23.5]]
TT="Anak nak masuk Tingkatan 1? Algebra menunggu! Pecahan, perpuluhan, peratus... kalau asas Darjah 6 masih lemah, Tingkatan 1 boleh jadi step paling ngeri 😰 Sekarang masa terbaik. Kelas hari Sabtu PERCUMA untuk pelajar sekolah menengah, untuk kuatkan algebra. DM untuk info 👇"
HS="#cikgualfarhan #tingkatan1 #algebra #tuisyenonline #asteredu"
DATA={"caps":C,"mg":MG,"sfx":sfx,"zoom":[{"t":t,"m":m} for t,m in ZOOM],"dur":24.58,"broll":[[14.04,16.3]]}
P={"DATA":DATA,"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS}
json.dump(P,open(f"{S}/a12/work/pagedata.json","w"),ensure_ascii=False)
t=open(f"{S}/work/tpl.html").read()
R=[("<title>AS-F-009 Kelas Percuma</title>","<title>AS-F-012 Darjah 6 ke T1</title>"),("Gaya BOFU Aster: merah + kuning.","Gaya HYBRID Aster: hitam + kuning."),
("--accent:#c4141c","--accent:#8a6400"),("--c-seg:#5c0b0f","--c-seg:#1b1b1b"),
('<h1>AS-F-009 <mark>Kelas Percuma</mark>: final</h1>','<h1>AS-F-012 <mark>Darjah 6 ke Tingkatan 1</mark>: preview</h1>'),
('<b>Menunggu semakan</b> BOFU · preview v1 · 540×960 · 28.5 saat','<b>Menunggu semakan</b> TOFU+BOFU · preview v1 · 540×960 · 24.6 saat'),
('aria-valuemax="28.45"','aria-valuemax="24.58"'),("harga disahkan Farhan (RM99).","frasa kurang jelas disemak dengan transkrip kedua."),
('<div class="legend"><span><i style="background:var(--c-seg)"></i>Babak</span>','<div class="legend"><span><i style="background:var(--c-seg)"></i>Babak</span><span><i style="background:var(--c-br)"></i>B-roll</span>'),
('<p>Footage satu take tanpa ulangan dan tiada senyap lebih 0.3 s, jadi isi tidak dipotong (25.95 s). Video = thumbnail 1 saat + isi + end card 1.5 saat. Tag <b>BOFU</b> (baris pertama skrip): gaya BOFU Aster <b>merah + kuning</b> ikut video rujukan BOFU_Aster: banner atas 0–8 saat sahaja lalu fade, tiket, bintang harga, bulatan bilangan subjek, cip subjek, mockup telefon asteredu11.com.my.</p>',
 '<p>Footage satu take tanpa ulangan dan tiada senyap lebih 0.3 s, jadi isi tidak dipotong (22.08 s, hingga hujung rakaman). Video = thumbnail 1 saat + isi + end card 1.5 saat. Tag <b>TOFU+BOFU</b> → gaya <b>HYBRID hitam + kuning</b>: separuh pertama masalah Tingkatan 1 (papan algebra, nota, CTA Follow), B-roll kad pencapaian pelajar, kemudian jualan (Pendaftaran 2027 dibuka, MATH TURBO 2027, kelas Sabtu percuma).</p>'),
('<div class="h">Lega: ada kelas percuma untuk kukuhkan asas</div>','<div class="h">Jangan tunggu Tingkatan 1: kukuhkan asas sekarang</div>'),
("<p>Selang-seli 103–107% dan 110–115% ikut ayat; zoom berpaut di bawah supaya mata Cikgu naik ke bahagian atas frame.</p>","<p>Selang-seli 106% dan 111–113% ikut ayat; zoom berpaut di bawah supaya mata Cikgu naik ke bahagian atas frame.</p>"),
("<td>Pop (grafik), whoosh (tukar babak), ding (4P, rakaman, end card), cha-ching (harga), click (tiket, DM), impact lembut (cop PERCUMA JE!).</td>","<td>Pop (grafik), whoosh (tukar babak, B-roll), tick (tulis algebra), bonk lembut (lemah lagi), impact lembut (NGERI), click (tukar kad B-roll), ding (masa terbaik, jualan, end card).</td>"),
("<td>−13.9 LUFS, true peak −1.3 dBTP. Final: H.264 High CRF 18, 30 fps, AAC 192 kbps 48 kHz.</td>","<td>−13.8 LUFS, true peak −1.5 dBTP.</td>"),
("<td>Muzik asal dijana sendiri (ceria ringan: marimba, pad, bass, perkusi lembut; C major 100 BPM). Bebas hak cipta, tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td>","<td>Muzik rasmi Aster: Aster_MuzikLatar_Ceria_100BPM (MUSIC/). Tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td>")]
for a,b in R:
  assert a in t,a; t=t.replace(a,b)
t=t.replace('"asf009-tab"','"asf012-tab"')
open(f"{S}/a12/page/index.html","w").write(t.replace("__DATA__",json.dumps(P,ensure_ascii=False)))
