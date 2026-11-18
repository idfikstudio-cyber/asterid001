"""Halaman preview + RINGKASAN AS-F-015. python3 mkpage.py <out_dir>"""
import json,re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import timeline as T
HERE=os.path.dirname(os.path.abspath(__file__));OUT=sys.argv[1];o=lambda s:round(T.s2o(s),2)
caps=json.load(open(f"{HERE}/caps.json"))
FIX={"trick":"trik","tuisyen":"tuition","DM":"jadi M","mampu":"mahu (semakan kedua: mampu)","hafal":None}
C=[]
for s,e,txt in caps:
    ws=[];sec=False
    for w in txt.split():
        t=w.lstrip("*");fx=FIX.get(t) if t in("trick","tuisyen","DM") else None
        if t=="mampu" and 59<s<61: fx="mahu (semakan kedua: mampu)"
        if t=="6" and abs(s-o(45.70))<0.3: fx="5 (sebutan asal; diganti 'enam' Cikgu sendiri)"
        q=False
        ws.append({"t":t,"hl":w.startswith("*"),"fix":fx,"q":q})
    C.append({"s":s,"e":e,"w":ws})
sfx=[[x["t"],x["name"]] for x in json.load(open(f"{HERE}/sfx.json"))]
E0=round(T.DUR-T.END,2)
MG=[[0,1.0,"Thumbnail","Wajah dalam bulatan emas + TRICK SIFIR 6 / UNTUK IBU AJAR ANAK + tulisan 6 × 7 = 7 + 35 = 42"],
[0,T.DUR,"Watermark","asteredu11.com.my sepanjang video (termasuk thumbnail & end card), putih ±40% + bayang halus, atas-kiri 12%"],
[1.0,T.DUR-T.END,"Wajah dalam bulatan","Atas arahan Farhan: wajah HANYA dalam bulatan emas (tiada talking head penuh). Dicerahkan + lampu muka lembut. Besar (Ø640) masa bercakap, kecil (Ø280) masa papan."],
[1.3,4.3,"Label nama","Wajah bulatan emas + Cikgu AlFarhan"],[o(0.3),o(3.4),"Kad kertas","🌙 Dah nak dekat 12 tengah malam"],
[o(5.5),o(11.5),"Tajuk","Trick kuasai SIFIR 6"],[o(7.92),o(9.45),"Pil","untuk ibu-ibu ajar anak"],[o(9.5),o(11.55),"Pil kuning","Cuba dengan anak ✓"],
[o(11.6),o(55.45),"B-roll papan (43 s)","B-Roll Sifir 6 (rakaman skrin iPad) dalam bingkai kuning; tulisan diselaraskan dengan setiap nombor yang disebut; bulatan wajah kecil di bawah"],
[o(11.9),o(22.0),"Label siri","SIFIR 6 · CIKGU ALFARHAN"],[o(22.05),o(29.95),"LANGKAH 1","Tulis nombor 1 → 10 · sorotan baris ikut nombor disebut"],
[o(30.0),o(42.45),"LANGKAH 2","Gandaan 5: 5 → 50 · sorotan baris"],[o(30.0),o(34.0),"CTA Follow","Kad Cikgu AlFarhan · @aster.edu_tpg · Follow saya (TOFU, tengah video)"],
[o(42.52),o(54.05),"LANGKAH 3","Tambah = jawapan! · sorotan seluruh baris"],[o(54.1),o(55.2),"Cop","SIFIR 6 SELESAI ✓"],
[o(55.04),o(56.2),"Kad","Kenapa buat trick ni? 🤔"],[o(56.26),o(58.64),"Pil kuning","Kena FAHAM ✓"],[o(58.68),o(60.55),"Teks besar","Tak semua anak mampu HAFAL (dipangkah)"],
[o(60.58),o(68.05),"Kad","Trick lain supaya anak masih MAMPU jawab soalan sifir ✓"],[o(68.1),o(76.1),"Pil merah","Pendaftaran 2027 dibuka (mula jualan)"],
[o(68.1),o(70.9),"Lower third","MATH TURBO 2027 · Tuisyen online bersama Cikgu AlFarhan"],[o(71.0),o(72.3),"Pil","Subjek teras"],[o(72.3),o(72.95),"Pil","DM saya"],[o(72.95),o(76.16),"Pil","Jadual kelas"],
[E0,T.DUR,"End card","Hitam + kuning: wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
ZOOM=[]
for i,s in enumerate(T.SENT): ZOOM.append({"t":o(s) if s>0 else 1.0,"m":("113% punch-in" if i%2 else "100%")+(" (bulatan kecil)" if T.TEACH[0]<=s<T.TEACH[1] else "")})
SEG=[[0,1.0,"Thumbnail","TRICK SIFIR 6"],[1.0,o(11.6),"Pembuka","12 tengah malam · trick sifir 6 untuk ibu ajar anak"],
[o(11.6),o(22.02),"Papan sedia","Sifir 6 ditulis 1–10, ada tambah dan sama dengan"],[o(22.02),o(30.0),"Langkah 1","Tulis 1 → 10"],
[o(30.0),o(42.52),"Langkah 2","Gandaan 5: 5 → 50 · CTA Follow"],[o(42.52),o(55.04),"Langkah 3","Tambah = jawapan · Selesai sifir 6"],
[o(55.04),o(68.1),"Kenapa","Kena faham · tak semua anak mampu hafal · trick lain"],[o(68.1),E0,"Jualan","Pendaftaran 2027 · MATH TURBO 2027 · subjek teras · DM · jadual kelas"],[E0,T.DUR,"End card","CTA BOFU + asteredu11.com.my"]]
TODO=[]
DONE=[["v2: 6 × 1 = 1 + 5 = 6 (pilihan B Farhan)","Sebutan 'lima' kedua (sumber 0:45.70–46.16) diganti dengan suara Cikgu sendiri menyebut 'enam' dari kiraan 1–10 (sumber 0:27.08–27.50); aras suara dipadankan, panjang kekal. Papan: '5' dipadam dan diganti '6' tulisan tangan Cikgu (digit 6 dari '36', baris 6 × 6), muncul seperti ditulis. Caption '6'. Disahkan transkrip: '1 tambah 5, 6, 12, 18'.",o(45.70)],
["v2: disahkan Farhan","'boleh DM saya' ✓ · 'tak semua anak mampu hafal' ✓ · ejaan 'trick' ✓ · durasi 77.4 s + B-roll papan ±43 s dikekalkan kerana video mengajar ✓ · ID ditukar kepada AS-F-015 (ikut skrip) ✓",o(71.94)],
["Lower third MATH TURBO 2027 + pil Pendaftaran 2027 dibuka","Ikut DNA HYBRID (bila beralih ke jualan) dan AS-F-012 yang diluluskan.",o(68.1)],
["Wajah dalam bulatan sahaja + dicerahkan","Tiada talking head penuh. Wajah dipotong mengikut kedudukan muka (dijejak), midtone diangkat, kontras ringan, lampu muka lembut, sedikit licin (kusam berkurang); hue kulit tidak dianjak.",2.0],
["Gaya HYBRID hitam + kuning","Ikut rujukan TOFU+BOFU_Sifir9: papan + LANGKAH 1/2/3, CTA Follow tengah video, lower third + pil Pendaftaran 2027 dibuka, end card CTA BOFU.",o(22.05)],
["Papan diselaraskan dengan suara","Setiap nombor (1–10, 5–50, jawapan) muncul dan disorot tepat ketika disebut.",o(34.18)],
["Potongan","Footage satu take: buang tersilap mula 'Prosesnya adalah,' + senyap 0.24 s. Disemak semula dengan transkrip: 'Prosesnya macam mana? Prosesnya kita tulis saja…'",o(20.66)],
["Muzik rasmi Aster","Aster_MuzikLatar_Ceria_100BPM. Tiada kredit perlu.",2.0],
["Safe zone & watermark","Teks di atas 80% frame dan di luar jalur kanan 15%; watermark asteredu11.com.my sepanjang video.",0.5]]
TT="Trick sifir 6 yang ibu boleh ajar anak sebelum tidur 🌙 Tulis 1 hingga 10, sebelah tu gandaan 5 (5 hingga 50), lepas tu tambah sahaja! Tak semua anak mampu hafal sifir, jadi trick macam ni bantu anak jawab soalan sifir. Ibu ayah yang cari tuisyen subjek teras untuk anak, DM saya 👇"
HS="#sifir6 #cikgualfarhan #trickmatematik #tuisyenonline #asteredu"
P={"DATA":{"caps":C,"mg":MG,"sfx":sfx,"zoom":ZOOM,"dur":round(T.DUR,2),"broll":[[o(11.6),o(55.45)]]},"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS}
t=open(f"{HERE}/../AS-F-012_Darjah6_ke_T1/preview_page.html").read()
t=re.sub(r"const P=\{.*?\};\n","const P=__P__;\n",t,count=1,flags=re.S)
a=t.index('<div class="pane" id="p-ga"');b=t.index('<div class="pane" id="p-q"')
GA="""<div class="pane" id="p-ga" role="tabpanel" hidden>
        <h2>Warna dan audio</h2>
        <h3>Wajah dalam bulatan (dicerahkan)</h3>
        <div class="tbl"><table><thead><tr><th>Langkah</th><th>Nilai</th><th>Kesan</th></tr></thead><tbody>
          <tr><td>Potongan bulatan</td><td class="n">2.15 × lebar muka, muka di ±38% tinggi</td><td>Wajah sahaja yang jelas; baju yang kurang kemas tidak menonjol. Mengikut gerak kepala (dilicinkan 1.5 s).</td></tr>
          <tr><td>Kecerahan (midtone)</td><td class="n">L gamma 0.66 (ruang Lab)</td><td>Muka tidak gelap; highlight tidak terbakar.</td></tr>
          <tr><td>Kontras</td><td class="n">×1.06, +1.5%</td><td>Lebih jelas tanpa nampak keras.</td></tr>
          <tr><td>Lampu muka</td><td class="n">+14% berpusat pada muka</td><td>Wajah nampak lebih segar dan cergas.</td></tr>
          <tr><td>Kulit</td><td class="n">licin ringan 55%, chroma ×1.04, hue tidak dianjak</td><td>Kurang kusam; warna kulit asli kekal (tidak oren / pucat).</td></tr>
          <tr><td>Latar</td><td class="n">hitam arang + cahaya kuning lembut</td><td>Ikut gaya HYBRID hitam + kuning.</td></tr>
        </tbody></table></div>
        <h3>Audio</h3>
        <div class="tbl"><table><thead><tr><th>Langkah</th><th>Kesan</th></tr></thead><tbody>
          <tr><td>High-pass 80 Hz + noise reduction ringan + compressor 2.5:1 + EQ kejelasan +1.5 dB @3.5 kHz</td><td>Suara jelas dan sekata.</td></tr>
          <tr><td>Muzik latar</td><td>Muzik rasmi Aster: Aster_MuzikLatar_Ceria_100BPM (MUSIC/). Tiada kredit perlu. ±23 dB di bawah suara, naik pada thumbnail dan end card.</td></tr>
          <tr><td>SFX</td><td>Pop (grafik), whoosh (tukar babak), tick lembut (setiap nombor ditulis), ding (LANGKAH, selesai, jualan, end card), swoosh (pangkah HAFAL), click (DM).</td></tr>
          <tr><td>Loudness akhir</td><td>−14.0 LUFS, true peak −1.0 dBTP.</td></tr>
        </tbody></table></div>
      </div>
      """
t=t[:a]+GA+t[b:]
ED_OLD=re.search(r'<p>Footage satu take.*?</p>',t,re.S).group(0)
R=[("<title>AS-F-012 Darjah 6 ke T1</title>","<title>AS-F-015 Trick Sifir 6</title>"),
('<h1>AS-F-012 <mark>Darjah 6 ke Tingkatan 1</mark>: final</h1>','<h1>AS-F-015 <mark>Trick Sifir 6</mark>: preview</h1>'),
(re.search(r'<span class="status">.*?</span>\n',t).group(0),f'<span class="status"><b>Menunggu kelulusan final</b> TOFU+BOFU → HYBRID · preview v2 · 540×960 · {T.DUR:.1f} saat · wajah dalam bulatan</span>\n'),
('aria-valuemax="24.58"',f'aria-valuemax="{T.DUR:.2f}"'),
(ED_OLD,'<p>Satu take: hanya tersilap mula "Prosesnya adalah," dan senyap 0.24 s dibuang. Video = thumbnail 1 s + isi 74.9 s + end card 1.5 s. Atas arahan Farhan, wajah dipapar <b>dalam bulatan emas sahaja</b> dan dicerahkan. Tag <b>TOFU+BOFU</b> → gaya <b>HYBRID hitam + kuning</b>: pembuka (bulatan besar), papan B-Roll Sifir 6 dengan LANGKAH 1–3 (bulatan kecil di bawah), sebab trick ini, kemudian jualan.</p>'),
('<div class="h">Jangan tunggu Tingkatan 1: kukuhkan asas sekarang</div>','<div class="h">Malam yang tenang: ibu boleh ajar sifir 6 dalam 3 langkah</div>'),
("<p>Selang-seli 106% dan 111–113% ikut ayat; zoom berpaut di bawah supaya mata Cikgu naik ke bahagian atas frame.</p>","<p>Dalam bulatan: selang-seli 100% dan 113% setiap ayat; muka kekal di sepertiga atas bulatan.</p>"),
('title="Perlu disahkan: rujukan-aster.txt = RM99"','title="Perlu disahkan: 1 + 5 = 6"'),
('"asf012-tab"','"asf013-tab"')]
for x,y in R:
    assert x in t,x[:60];t=t.replace(x,y)
t=t.replace('"asf012-tab"','"asf013-tab"')
t=t.replace("__P__",json.dumps(P,ensure_ascii=False))
open(f"{OUT}/index.html","w").write(t)
json.dump(P,open(f"{HERE}/pagedata.json","w"),ensure_ascii=False)
# ---- RINGKASAN ----
f=lambda x:f"{int(x//60)}:{x%60:04.1f}"
L=[f"AS-F-015_Trick Sifir 6 — RINGKASAN PREVIEW",f"Aster · TOFU+BOFU → HYBRID (hitam + kuning) · spokesperson FARHAN · durasi {T.DUR:.1f} s · preview 540x960 · wajah dalam bulatan sahaja (arahan Farhan)","",
"1. TEKS HOOK / THUMBNAIL"," TRICK SIFIR 6 / UNTUK IBU AJAR ANAK + tulisan '6 × 7 = 7 + 35 = 42'",f" Wajah dalam bulatan emas (sumber 1:{T.THUMB_SRC-60:04.1f}). Fail: AS-F-015_Trick Sifir 6_THUMB.png","","2. CAPTION PENUH (burn-in, ikut sebutan)"]
L+=[f" {f(c[0])} {c[2].replace('*','')}" for c in caps]
L+=["","3. SFX, ANIMASI & B-ROLL (masa video)"]+[f" {f(m[0])}–{f(m[1])} {m[2]}: {m[3]}" for m in MG]
L+=[" SFX: "+", ".join(f"{f(t)} {n}" for t,n in sfx)," Zoom (dalam bulatan): "+", ".join(f"{f(z['t'])} {z['m']}" for z in ZOOM)]
L+=["","4. CTA"," Tengah video (TOFU, ±0:30): kad Follow saya @aster.edu_tpg"," Pil 'DM saya' (ikut sebutan) + 'Jadual kelas'"," End card (HYBRID → CTA BOFU): WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas · asteredu11.com.my · WhatsApp 011-5596 9070 · @aster.edu_tpg"]
L+=["","5. PERLU SEMAK"," Tiada (semua perkara v1 diputuskan Farhan). Pembetulan v2:"]+[f" - {a}: {b}" for a,b,_ in DONE[:2]]
L+=["","6. CAPTION TIKTOK + 5 HASHTAG"," "+TT,""," "+HS,""," Muzik: Aster_MuzikLatar_Ceria_100BPM (muzik rasmi Aster, tiada kredit perlu)"]
open(f"{HERE}/RINGKASAN.txt","w").write("\n".join(L)+"\n")
