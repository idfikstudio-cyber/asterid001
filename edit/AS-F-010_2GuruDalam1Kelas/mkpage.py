import json,re
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad"
caps=json.load(open(f"{S}/a10/work/caps.json"))
FIX={"garang":"garam","Taip":"Baik","peel":"pengen (disahkan Farhan: peel)"}
C=[]
for s,e,txt in caps:
  ws=[]
  for w in txt.split():
    hl=w.startswith("*");q=w.startswith("~");t=w.lstrip("*~");base=re.sub(r"\W","",t)
    ws.append({"t":t,"hl":hl,"fix":FIX.get(base),"q":q})
  C.append({"s":s,"e":e,"w":ws})
sfx=[]
src=open(f"{S}/a10/work/build_audio.py").read()
for t,n in re.findall(r'\(([\d.]+),"(\w+)",',src): sfx.append([float(t),n])
MG=[[0,1.0,"Thumbnail","ANAK MENANGIS / BILA ULANG KAJI? + pil 2 GURU dalam 1 KELAS"],
[0,46.32,"Watermark","asteredu11.com.my sepanjang video (termasuk thumbnail & end card), putih ±40% + bayang halus, atas-kiri 11%"],
[1.0,3.5,"Kad kertas","Jam 9:00 MALAM · ulang kaji (jarum bergerak)"],[1.3,4.3,"Label nama","Wajah bulatan emas + Cikgu AlFarhan"],
[4.85,6.45,"Pil","termenung... (ikon buku)"],[8.77,9.35,"Pil kuning","ada yang MENANGIS"],
[10.55,14.4,"Bubble","IBU AYAH: Kenapa tak faham lagi ni?"],[12.37,14.4,"Bubble","IBU AYAH: Kenapa tak ulang kaji lagi ni?"],
[14.47,17.95,"Kad kertas","ESOK · Babak yang sama (ikon ulang)"],[17.45,19.3,"Pil","Sakit... tak nak pergi sekolah"],
[19.36,22.62,"Teks coret","ANAK BUKAN MALAS (garis merah dari 19.96)"],[21.6,22.62,"Teks coret","IBU BUKAN GARANG (garis merah dari 21.95)"],
[22.64,26.2,"Nota kertas","Masalah sebenar: ✗ Asas tak kukuh lagi (24.66)"],[23.0,26.2,"CTA Follow","Wajah bulatan emas + Cikgu AlFarhan + @aster.edu_tpg + Follow saya (tengah video, TOFU)"],
[26.3,31.6,"Pil merah","Pendaftaran 2027 dibuka (mula bahagian jualan)"],[26.3,28.0,"Lower third","MATH TURBO 2027 · Tuisyen online bersama Cikgu AlFarhan"],
[28.08,34.9,"Kad 2 GURU","2 GURU dalam 1 KELAS · Guru 1: Mengajar (29.82) · Guru 2: Jawab soalan anak (31.7)"],
[35.16,40.2,"Pil kuning","Tak perlu takut bertanya ✓"],[37.06,40.2,"Kad","Kamera: tak payah buka · Mikrofon: tak payah (38.7)"],
[40.26,43.25,"Mockup chat kelas","Anak · taip sahaja (titik menaip) → Cikgu kedua: Jawab soalan anak ✓ (41.8)"],
[43.3,44.82,"Pil","DM kami"],[44.82,46.32,"End card","Hitam + kuning: wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
ZOOM=[(0,"112% (thumbnail)"),(1.0,"106%"),(3.52,"112% (sorok potongan senyap)"),(6.47,"106%"),(9.37,"113% punch-in"),(12.37,"106%"),(14.47,"112% punch-in"),(17.99,"106% (sorok potongan senyap)"),(19.36,"114% punch-in"),(22.64,"106%"),(26.30,"111% punch-in"),(29.82,"105%"),(35.16,"113% punch-in"),(38.70,"106%"),(40.26,"112% punch-in"),(43.30,"106%")]
SEG=[[0,1.0,"Thumbnail","ANAK MENANGIS BILA ULANG KAJI? + 2 GURU dalam 1 KELAS"],[1.0,9.37,"Malam ulang kaji","Jam 9:00 malam · termenung · ada yang menangis"],
[9.37,19.36,"Tekanan","Bubble IBU AYAH x2 · Esok babak yang sama · Sakit, tak nak pergi sekolah"],[19.36,26.3,"Punca","Coret MALAS / GARANG · Masalah sebenar: asas tak kukuh · CTA Follow"],
[26.3,35.16,"2 guru 1 kelas","Pendaftaran 2027 dibuka · MATH TURBO 2027 · kad 2 GURU"],[35.16,44.82,"Tak perlu takut","Kamera / mikrofon tak payah buka · chat: taip, cikgu kedua jawab · DM kami"],[44.82,46.32,"End card","CTA BOFU WhatsApp + asteredu11.com.my"]]
TODO=[]
DONE=[["v2: 'satu peel anak'","Disahkan Farhan: ayat penuh 'Kadang-kadang ada satu peel anak' (transkrip dengar 'pengen'). Caption dikemas kini.",16.55],["Lower third MATH TURBO 2027 + pil Pendaftaran 2027 dibuka","Disahkan Farhan: kekal.",26.3],["Nada pil MENANGIS + bubble IBU AYAH","Disahkan Farhan: OK.",8.77],["CTA","Pil DM kami (ikut sebutan) + end card CTA BOFU WhatsApp.",43.3],["Tiada B-roll","Mockup chat kelas ialah lukisan ringkas (tiada nama pelajar).",40.26],["Tag TOFU+BOFU → gaya HYBRID hitam + kuning","Ikut rujukan TOFU+BOFU_Sifir9: kad kertas putih, teks coret merah, CTA Follow tengah video, lower third program + pil Pendaftaran 2027 dibuka bila masuk jualan, end card CTA BOFU.",19.36],
["Jenis footage: sudah ditrim","Satu take tanpa ulangan. Dua senyap dipendekkan (0:02.5–0:02.9 dan 0:17.4–0:17.8); potongan disorok dengan pertukaran zoom.",3.52],
["Disemak dengan transkrip kedua","'garam' → garang; 'Baik sahaja' → Taip sahaja (kedua-dua model setuju dengan prompt konteks).",22.0],
["Fakta disebut sahaja","2 guru dalam 1 kelas (seorang mengajar, seorang jawab soalan) sepadan rujukan-aster.txt. Tiada harga disebut, jadi tiada harga dipapar.",28.08],
["Muzik rasmi Aster","Aster_MuzikLatar_Ceria_100BPM (DNA baru). Tiada kredit perlu dalam caption.",2.0],
["Wajah, bukan logo · safe zone","Bulatan emas guna Logo SocMed Aster; teks di atas 80% frame dan di luar jalur kanan 15%.",45.5],
["Durasi 46.3 s","Dalam sasaran BOFU 30–60 s.",None]]
TT="Pukul 9 malam, anak termenung depan buku... ada yang menangis 😢 Anak bukan malas, ibu pun bukan garang. Asas belum kukuh. Kelas kami ada 2 guru dalam 1 kelas: seorang mengajar, seorang jawab soalan. Anak tak perlu buka kamera, taip je soalan ✍️ DM untuk info lanjut 👇"
HS="#cikgualfarhan #tuisyenonline #ibubapa #tipsbelajar #asteredu"
DATA={"caps":C,"mg":MG,"sfx":sfx,"zoom":[{"t":t,"m":m} for t,m in ZOOM],"dur":46.32,"broll":[]}
json.dump({"DATA":DATA,"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS},open(f"{S}/a10/work/pagedata.json","w"),ensure_ascii=False)
t=open(f"{S}/work/tpl.html").read()
R=[("<title>AS-F-009 Kelas Percuma</title>","<title>AS-F-010 2 Guru 1 Kelas</title>"),
("Gaya BOFU Aster: merah + kuning.","Gaya HYBRID Aster: hitam + kuning."),
("--accent:#c4141c","--accent:#8a6400"),("--c-seg:#5c0b0f","--c-seg:#1b1b1b"),
('<h1>AS-F-009 <mark>Kelas Percuma</mark>: final</h1>','<h1>AS-F-010 <mark>2 Guru Dalam 1 Kelas</mark>: final</h1>'),
('<b>Final siap</b> BOFU · v2 ikut pembetulan Farhan 10 Nov 2026 · final 1080×1920 · 28.5 saat','<b>Menunggu semakan</b> TOFU+BOFU · preview v1 · 540×960 · 46.3 saat'),
('aria-valuemax="28.45"','aria-valuemax="46.32"'),
("harga disahkan Farhan (RM99).","frasa kurang jelas disemak dengan transkrip kedua."),
('<p>Footage satu take tanpa ulangan dan tiada senyap lebih 0.3 s, jadi isi tidak dipotong (25.95 s). Video = thumbnail 1 saat + isi + end card 1.5 saat. Tag <b>BOFU</b> (baris pertama skrip): gaya BOFU Aster <b>merah + kuning</b> ikut video rujukan BOFU_Aster: banner atas 0–8 saat sahaja lalu fade, tiket, bintang harga, bulatan bilangan subjek, cip subjek, mockup telefon asteredu11.com.my.</p>',
 '<p>Footage satu take tanpa ulangan; dua senyap dipendekkan (44.6 s → 43.8 s). Video = thumbnail 1 saat + isi + end card 1.5 saat. Tag <b>TOFU+BOFU</b> (baris pertama skrip) → gaya <b>HYBRID hitam + kuning</b> ikut rujukan TOFU+BOFU_Sifir9: separuh pertama cerita masalah (TOFU: kad kertas, nota Masalah sebenar, CTA Follow), separuh kedua jualan (pil Pendaftaran 2027 dibuka, lower third MATH TURBO 2027, kad 2 GURU, CTA BOFU). Tiada skrin terbelah kerana tiada bahagian mengajar.</p>'),
('<div class="h">Lega: ada kelas percuma untuk kukuhkan asas</div>','<div class="h">Faham risau ibu: bukan salah anak, bukan salah ibu</div>'),
("<p>Selang-seli 103–107% dan 110–115% ikut ayat; zoom berpaut di bawah supaya mata Cikgu naik ke bahagian atas frame.</p>","<p>Selang-seli 105–106% dan 111–114% ikut ayat; zoom berpaut di bawah supaya mata Cikgu naik ke bahagian atas frame. Dua potongan senyap disorok di bawah pertukaran zoom.</p>"),
("<td>Pop (grafik), whoosh (tukar babak), ding (4P, rakaman, end card), cha-ching (harga), click (tiket, DM), impact lembut (cop PERCUMA JE!).</td>","<td>Tick (jam), pop (grafik), whoosh (tukar babak), swoosh turun (menangis), bonk lembut (sakit), click (garis coret, kamera/mikrofon), ding (jualan, cikgu kedua jawab, end card), impact lembut (kad 2 GURU).</td>"),
("<td>−13.9 LUFS, true peak −1.3 dBTP. Final: H.264 High CRF 18, 30 fps, AAC 192 kbps 48 kHz.</td>","<td>−14.0 LUFS, true peak −1.7 dBTP.</td>"),
("<td>Muzik asal dijana sendiri (ceria ringan: marimba, pad, bass, perkusi lembut; C major 100 BPM). Bebas hak cipta, tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td>","<td>Muzik rasmi Aster: Aster_MuzikLatar_Ceria_100BPM (MUSIC/). Bebas hak cipta, tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td>"),
('title="Perlu disahkan: rujukan-aster.txt = RM99"','title="Perlu disahkan: perkataan kurang jelas"'),
]
for a,b in R:
  assert a in t,a; t=t.replace(a,b)
t=t.replace('"asf009-tab"','"asf010-tab"')
open(f"{S}/a10/page/index.html","w").write(t.replace("__DATA__",json.dumps({"DATA":DATA,"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS},ensure_ascii=False)))
print(len(sfx))
