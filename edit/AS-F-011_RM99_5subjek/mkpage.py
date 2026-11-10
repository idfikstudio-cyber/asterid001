import json,re
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad"
caps=json.load(open(f"{S}/a11/work/caps.json"))
FIX={"Pendaftaran":"Penaftaran","hujung":"ujung"}
C=[{"s":s,"e":e,"w":[{"t":w.lstrip("*"),"hl":w.startswith("*"),"fix":FIX.get(re.sub(r"\W","",w.lstrip("*"))),"q":False} for w in txt.split()]} for s,e,txt in caps]
sfx=[[float(t),n] for t,n in re.findall(r'\(([\d.]+),"(\w+)",',open(f"{S}/a11/work/build_audio.py").read())]
MG=[[0,1.0,"Thumbnail","IBU AYAH, PERHATIAN! · 5 SUBJEK / RM99 · pil BM · BI · MATH · SAINS · SEJARAH"],
[0,24.07,"Watermark","asteredu11.com.my sepanjang video (termasuk thumbnail & end card), putih ±40% + bayang halus, atas-kiri 11%"],
[1.0,9.0,"Banner atas BOFU","IBU AYAH, PERHATIAN! + RM99 · 5 SUBJEK; SEMINGGU SEKALI! (5.5); fade 8.4–9.0"],
[1.0,2.76,"Bintang harga","RM99"],[1.3,4.3,"Label nama","Wajah bulatan emas + Cikgu AlFarhan"],[1.94,5.9,"Bulatan bilangan","5 SUBJEK"],
[2.76,5.9,"Cip subjek","BM 2.8 · BI 3.2 · Math 3.5 · Sains 3.9 · Sejarah 4.1"],
[6.3,8.1,"Pil","Melalui Zoom"],[7.04,8.1,"Pil merah","Di rumah sahaja"],
[8.12,13.5,"Senarai semak","✓ Rakaman percuma 8.1 · ✓ Modul percuma 9.2 · ✓ 2 guru dalam 1 kelas 10.3 · ✓ Nota dan modul 12.2"],
[13.56,19.74,"Kad kalendar","UJIAN BULANAN · setiap hujung bulan (15.6)"],[16.86,19.74,"Pil","Anak tahu tahap dia (graf naik)"],
[19.8,22.5,"Tiket","PENDAFTARAN RM20 SAHAJA"],[21.04,22.5,"Mockup telefon","asteredu11.com.my · wajah bulatan emas · Cikgu AlFarhan · butang Daftar Sekarang"],[21.04,22.5,"Pil","DM saya"],
[22.57,24.07,"End card","Merah + kuning: wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
ZOOM=[(0,"112% (thumbnail)"),(1.0,"106%"),(4.6,"112% punch-in"),(8.12,"105%"),(13.56,"112% punch-in"),(16.86,"106%"),(19.8,"104% (ruang tiket RM20)"),(21.04,"112% punch-in")]
SEG=[[0,1.0,"Thumbnail","5 SUBJEK / RM99"],[1.0,8.12,"Harga & subjek","Banner RM99 · 5 SUBJEK · bintang RM99 · cip subjek · seminggu sekali · Zoom · di rumah"],
[8.12,13.56,"Termasuk","Rakaman percuma · modul percuma · 2 guru · nota dan modul"],[13.56,19.8,"Ujian bulanan","Kalendar UJIAN BULANAN · anak tahu tahap dia"],
[19.8,22.57,"Daftar","Tiket PENDAFTARAN RM20 SAHAJA · mockup telefon · DM saya"],[22.57,24.07,"End card","CTA BOFU WhatsApp + asteredu11.com.my"]]
TODO=[["Durasi 24.1 s","Bawah sasaran BOFU 30–60 s. Isi tidak dipanjangkan (tiada isi tambahan disebut).",None]]
DONE=[["v2: hujung ayat 'lanjut' dipulihkan","Rakaman asal berakhir pada 21.57 s ketika 'lanjut' masih disebut; potongan v1 (21.50 s) buang 0.07 s lagi. v2 kekalkan audio hingga hujung fail, dan end card, whoosh serta kenaikan muzik dialih ke selepas suara tamat supaya '-jut' jelas.",22.2],["v2: masa SFX dibetulkan","Skrip audio v1 tersilap guna senarai masa SFX AS-F-009; kini ikut pelan edit ini.",1.0],["Disahkan Farhan","Seminggu sekali, tanpa 'sebulan', CTA WhatsApp: semua OK.",None],["Tag BOFU → gaya merah + kuning","Ikut BOFU_Aster: banner atas 0–8 saat (fade lembut), bintang harga, bulatan 5 SUBJEK, cip subjek, tiket RM20, mockup telefon asteredu11.com.my.",1.5],
["Harga tepat","RM99 untuk 5 subjek dan Pendaftaran RM20, seperti disebut dan sepadan rujukan-aster.txt. Tiada diskaun/promo direka.",1.0],
["Fakta sepadan rujukan","Zoom, rakaman, modul percuma, 2 guru dalam 1 kelas, ujian bulanan: semuanya disebut dan ada dalam rujukan-aster.txt.",8.12],
["Jenis footage: sudah ditrim","Satu take tanpa ulangan; tiada senyap > 0.3 s, jadi tiada potongan.",None],
["Ejaan","'Penaftaran' → Pendaftaran, 'ujung' → hujung; Math, BM, BI, Zoom ikut DNA.",19.8],
["Muzik rasmi Aster","Aster_MuzikLatar_Ceria_100BPM. Tiada kredit perlu dalam caption.",2.0],
["Wajah, bukan logo · safe zone","Bulatan emas guna Logo SocMed Aster; teks di atas 80% frame dan di luar jalur kanan 15%.",23.0]]
TT="RM99 untuk 5 subjek: BM, BI, Math, Sains, Sejarah 📚 Kelas Zoom seminggu sekali, dari rumah je. Rakaman & modul percuma, 2 guru dalam 1 kelas, ujian bulanan setiap hujung bulan. Pendaftaran RM20 sahaja! DM untuk info 👇"
HS="#cikgualfarhan #tuisyenonline #mathturbo #upsr #asteredu"
HS="#cikgualfarhan #tuisyenonline #kelaszoom #ibubapa #asteredu"
DATA={"caps":C,"mg":MG,"sfx":sfx,"zoom":[{"t":t,"m":m} for t,m in ZOOM],"dur":24.07,"broll":[]}
P={"DATA":DATA,"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS}
json.dump(P,open(f"{S}/a11/work/pagedata.json","w"),ensure_ascii=False)
t=open(f"{S}/work/tpl.html").read()
R=[("<title>AS-F-009 Kelas Percuma</title>","<title>AS-F-011 RM99 5 Subjek</title>"),
('<h1>AS-F-009 <mark>Kelas Percuma</mark>: final</h1>','<h1>AS-F-011 <mark>RM99, 5 Subjek</mark>: final</h1>'),
('<b>Menunggu semakan</b> BOFU · preview v1 · 540×960 · 28.5 saat','<b>Final siap</b> BOFU · v2 ikut semakan Farhan 10 Nov 2026 · final 1080×1920 · 24.1 saat · pemain: salinan 540×960 (FINAL.mp4 + THUMB.png dihantar terus)'),
('aria-valuemax="28.45"','aria-valuemax="24.07"'),("harga disahkan Farhan (RM99).","harga RM99 dan RM20 didengar jelas."),
('Footage satu take tanpa ulangan dan tiada senyap lebih 0.3 s, jadi isi tidak dipotong (25.95 s).','Footage satu take tanpa ulangan dan tiada senyap lebih 0.3 s, jadi isi tidak dipotong (21.5 s).'),
('banner atas 0–8 saat sahaja lalu fade, tiket, bintang harga, bulatan bilangan subjek, cip subjek, mockup telefon asteredu11.com.my.','banner atas 0–8 saat sahaja lalu fade, bintang harga, bulatan 5 SUBJEK, cip subjek, senarai semak, kalendar ujian bulanan, tiket RM20, mockup telefon asteredu11.com.my.'),
('<div class="h">Lega: ada kelas percuma untuk kukuhkan asas</div>','<div class="h">Jelas dan berbaloi: semua yang ibu dapat dengan RM99</div>'),
("<p>Selang-seli 103–107% dan 110–115% ikut ayat;","<p>Selang-seli 104–106% dan 112% ikut ayat;"),
("<td>Pop (grafik), whoosh (tukar babak), ding (4P, rakaman, end card), cha-ching (harga), click (tiket, DM), impact lembut (cop PERCUMA JE!).</td>","<td>Cha-ching (RM99, RM20), pop (grafik, cip subjek), ding (senarai semak, end card), whoosh (tukar babak), click (DM).</td>"),
("<td>−13.9 LUFS, true peak −1.3 dBTP. Final: H.264 High CRF 18, 30 fps, AAC 192 kbps 48 kHz.</td>","<td>−13.8 LUFS, true peak −2.0 dBTP. Final: H.264 High CRF 18, 30 fps, AAC 192 kbps 48 kHz.</td>"),
("<td>Muzik asal dijana sendiri (ceria ringan: marimba, pad, bass, perkusi lembut; C major 100 BPM). Bebas hak cipta, tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td>","<td>Muzik rasmi Aster: Aster_MuzikLatar_Ceria_100BPM (MUSIC/). Tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td>"),
('"asf009-tab"','"asf011-tab"')]
for a,b in R:
  assert a in t,a; t=t.replace(a,b)
t=t.replace('"asf009-tab"','"asf011-tab"')
open(f"{S}/a11/page/index.html","w").write(t.replace("__DATA__",json.dumps(P,ensure_ascii=False)))
