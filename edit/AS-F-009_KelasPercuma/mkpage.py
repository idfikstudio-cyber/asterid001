import json,re
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad"
h=open(f"{S}/ov/overlay.html").read()
caps=json.loads("["+re.search(r"const CAPS=\[(.*?)\];",h,re.S).group(1).replace("\n","")+"]")
FIX={"sifir":"sipir","pecahan":"pecahat","Sifir":"sipir","RM99":"RM59 (harga disahkan Farhan: RM99)"}
C=[]
for s,e,txt in caps:
  ws=[]
  for w in txt.split():
    hl=w.startswith("*");t=w.lstrip("*");base=re.sub(r"\W","",t)
    ws.append({"t":t,"hl":hl,"fix":FIX.get(base),"q":False})
  C.append({"s":s,"e":e,"w":ws})
sfx=json.load(open(f"{S}/work/sfx.json"))
MG=[[0,1.0,"Thumbnail","IBU AYAH, PERHATIAN! · ANAK LEMAH / SIFIR? · pil KELAS PERCUMA SETIAP SABTU"],
[0,28.45,"Watermark","asteredu11.com.my sepanjang video (termasuk thumbnail & end card), putih ±40% + bayang halus, atas-kiri 11%"],
[1.0,9.0,"Banner atas BOFU","IBU AYAH, PERHATIAN! + KELAS PERCUMA; SETIAP HARI SABTU! (3.5); Untuk kukuhkan sifir (4.8); fade 8.4–9.0"],
[1.3,4.3,"Label nama","Wajah bulatan emas + Cikgu AlFarhan"],
[6.08,12.0,"Kad SIFIR + 4P","SIFIR → + 4P (7.2) → Penyelesaian masalah 8.7 · Perpuluhan 9.9 · Peratus 10.8 · Pecahan 11.5"],
[12.1,14.85,"Tiket","KELAS PERCUMA + Untuk pelajar berdaftar sahaja (12.8)"],
[14.9,17.4,"Label siri","KELAS PERCUMA · CIKGU ALFARHAN"],
[14.9,16.62,"Pil","✓ Kelas tetap jalan macam biasa"],
[16.68,21.3,"Bulatan bilangan","5 SUBJEK"],
[17.5,21.3,"Bintang harga","SERENDAH RM99 (disahkan Farhan)"],
[18.9,21.3,"Cip subjek","BM 18.9 · BI 19.5 · Math 20.0 · Sains 20.4 · Sejarah 20.8"],
[21.4,23.5,"Pil merah","ADA RAKAMAN"],[22.1,23.5,"Pil","Terlepas? Jangan risau"],
[23.54,24.36,"Cop","PERCUMA JE!"],
[24.36,26.95,"Mockup telefon","asteredu11.com.my · wajah bulatan emas · Cikgu AlFarhan · butang Daftar Sekarang"],
[25.16,26.95,"Pil","DM saya"],
[26.95,28.45,"End card","Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
ZOOM=[(0,"112% (thumbnail)"),(1.0,"106%"),(4.48,"111% punch-in"),(6.08,"106%"),(9.06,"115% punch-in"),(12.06,"107%"),(14.88,"110% punch-in"),(17.9,"103% (ruang bintang harga + 5 SUBJEK)"),(21.36,"112% punch-in"),(24.36,"105%")]
SEG=[[0,1.0,"Thumbnail","ANAK LEMAH SIFIR? + KELAS PERCUMA SETIAP SABTU"],[1.0,6.08,"Tawaran","Banner IBU AYAH, PERHATIAN! / KELAS PERCUMA / SETIAP HARI SABTU! · label Cikgu AlFarhan"],
[6.08,12.06,"Isi kelas","Kad SIFIR + 4P, empat P muncul ikut sebutan"],[12.06,14.88,"Syarat","Tiket KELAS PERCUMA untuk pelajar berdaftar sahaja"],
[14.88,21.36,"Kelas biasa","Kelas tetap jalan · 5 SUBJEK · bintang SERENDAH RM99 · cip BM, BI, Math, Sains, Sejarah"],
[21.36,24.36,"Rakaman","ADA RAKAMAN · Terlepas? Jangan risau · cop PERCUMA JE!"],[24.36,26.95,"CTA","Mockup telefon asteredu11.com.my · pil DM saya"],[26.95,28.45,"End card","CTA BOFU WhatsApp + asteredu11.com.my"]]
TODO=[["Durasi 28.5 s","Bawah sasaran BOFU 30–60 s. Isi tidak dipanjangkan (tiada isi tambahan disebut).",None]]
DONE=[["v2: harga RM99","Disahkan Farhan: harga ialah RM99 (transkrip dengar RM59). Bintang harga dan caption ditukar ke SERENDAH RM99, sepadan rujukan-aster.txt.",17.5],["v2: muzik tanpa kredit","Wholesome (perlu kredit) diganti dengan muzik latar asal yang dijana sendiri: ceria ringan, marimba + pad + bass, C major 100 BPM. Bebas hak cipta, tiada kredit perlu dalam caption.",2.0],["CTA WhatsApp diluluskan","Pil DM saya (ikut sebutan) + end card CTA BOFU WhatsApp 011-5596 9070, disahkan Farhan.",27.0],["Tiada B-roll","Folder B-ROLL tiada rakaman untuk AS-F-009; video guna grafik sahaja.",None],["Tag BOFU → gaya merah + kuning","Ikut BOFU_Aster rujukan-gaya: banner atas 0–8 saat (fade lembut), tiket, bintang harga, bulatan bilangan subjek, cip subjek, mockup telefon asteredu11.com.my.",1.5],
["Jenis footage: sudah ditrim","Satu take tanpa ulangan; tiada senyap > 0.3 s, jadi tiada potongan.",None],
["Ejaan istilah","'sipir' → sifir, 'pecahat' → pecahan; 4P, Math, BM, BI ikut DNA.",5.0],
["Wajah, bukan logo","Bulatan emas guna Logo SocMed Aster; tiada Logo Rasmi Aster / ASTER EDU. Tiada aset Fi-k Studio / Yuran.my.",27.5],
["Fakta disebut sahaja","Tiada diskaun/promo direka. 5 subjek dan senarai BM, BI, Math, Sains, Sejarah sepadan rujukan-aster.txt.",18.9],
["Watermark ±40%","asteredu11.com.my sepanjang video dengan bayang halus (±40% ikut arahan Farhan untuk AS-F-007).",3.0],
["Safe zone","Teks di atas 80% frame dan di luar jalur kanan 15%.",None]]
TT="Anak lemah sifir? Kelas PERCUMA setiap hari Sabtu untuk kukuhkan sifir + 4P (penyelesaian masalah, perpuluhan, peratus, pecahan) 📚 Khas untuk pelajar berdaftar. Nak daftar? DM Cikgu AlFarhan 👇"
HS="#cikgualfarhan #kelaspercuma #sifir #tuisyenonline #asteredu"
DATA={"caps":C,"mg":MG,"sfx":[[x["t"],x["name"]] for x in sfx],"zoom":[{"t":t,"m":m} for t,m in ZOOM],"dur":28.45,"broll":[]}
json.dump({"DATA":DATA,"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS},open(f"{S}/work/pagedata.json","w"),ensure_ascii=False)
print(len(C))
