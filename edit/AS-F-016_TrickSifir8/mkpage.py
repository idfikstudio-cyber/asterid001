"""Halaman preview + RINGKASAN AS-F-016. python3 mkpage.py <out_dir>"""
import json,re,sys,os
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import timeline as T
OUT=sys.argv[1];o=lambda s:round(T.s2o(s),2)
caps=json.load(open(f"{HERE}/caps.json"))
C=[]
for s,e,txt in caps:
    ws=[]
    for w in txt.split():
        t=w.lstrip("*");fx={"trick":"trik","DM":"Dan"}.get(t)
        ws.append({"t":t,"hl":w.startswith("*"),"fix":fx,"q":t=="DM"})
    C.append({"s":s,"e":e,"w":ws})
sfx=[[x["t"],x["name"]] for x in json.load(open(f"{HERE}/sfx.json"))]
E0=round(T.DUR-T.END,2)
MG=[[0,1.0,"Thumbnail","Cikgu pandang kamera + TRICK SIFIR 8 / UNTUK ANAK LEMAH SIFIR + tulisan 8 × 7 = 56"],
[0,T.DUR,"Watermark","asteredu11.com.my sepanjang video (termasuk thumbnail & end card), putih ±40% + bayang halus, atas-kiri 12%"],
[1.3,o(3.2),"Label nama","Wajah bulatan emas + Cikgu AlFarhan"],[o(0.3),o(3.25),"Tajuk","Anak masih lemah SIFIR 8?"],
[o(3.2),o(32.7),"Skrin terbelah + B-roll papan (29 s)","B-Roll Sifir 8 (rakaman skrin iPad) di atas, Cikgu di bawah, garis kuning SIFIR 8 · CIKGU ALFARHAN; tulisan diselaraskan dengan setiap nombor disebut"],
[o(3.28),o(8.1),"LANGKAH 1","Tulis 0 → 4 · sorotan ikut nombor"],[o(8.18),o(12.2),"LANGKAH 2","Sambung 4 → 8 di sebelah"],
[o(12.26),o(20.1),"LANGKAH 3","Gandaan 2 dari bawah: 0, 2, 4, 6, 8 · pil ↑ mula dari bawah"],[o(20.16),o(22.2),"CTA Follow","Kad Cikgu AlFarhan · @aster.edu_tpg · Follow saya (TOFU, tengah video)"],
[o(20.16),o(26.45),"LANGKAH 4","Sebelah pun gandaan 2"],[o(26.5),o(27.3),"Cop","SIFIR 8 SIAP ✓"],[o(26.5),o(32.3),"SIAP","Baca setiap baris = jawapan · label 1 × 8 = … 5 × 8 = ikut sebutan"],
[o(32.64),o(33.5),"Pil kuning","Mudah kan? ✓"],[o(33.54),o(37.0),"Kad","Sebenarnya banyak cara & trick kuasai sifir"],[o(37.06),o(40.95),"Teks besar","Salah satunya memang / Tak semua anak mampu MENGHAFAL (dipangkah)"],
[o(41.0),o(44.95),"Kad","Jadi kami datangkan PELBAGAI CARA untuk anak kuasai sifir ✓"],[o(45.1),o(53.76),"Pil merah","Pendaftaran 2027 dibuka (mula jualan)"],[o(45.1),o(47.6),"Kad","Ibu ayah jangan berputus asa 💪"],
[o(47.7),o(50.4),"Lower third","MATH TURBO 2027 · Tuisyen online bersama Cikgu AlFarhan"],[o(50.4),o(52.1),"Pil kuning","SUKSES dalam peperiksaan ✓"],[o(52.12),o(53.76),"Pil","DM kami"],
[E0,T.DUR,"End card","Hitam + kuning: wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
ZOOM=[{"t":(o(s) if s>0 else 1.0),"m":("skrin terbelah (bawah)" if T.TEACH[0]<=s<T.TEACH[1] else ("112% punch-in" if i%2 else "100%"))} for i,s in enumerate(T.SENT)]
SEG=[[0,1.0,"Thumbnail","TRICK SIFIR 8"],[1.0,o(3.28),"Pembuka","Anak masih lemah sifir 8?"],[o(3.28),o(8.18),"Langkah 1","0 → 4"],[o(8.18),o(12.26),"Langkah 2","4 → 8"],
[o(12.26),o(20.16),"Langkah 3","Gandaan 2 dari bawah"],[o(20.16),o(26.5),"Langkah 4","Sebelah gandaan 2 · CTA Follow"],[o(26.5),o(32.64),"Siap","1 × 8 … 4 × 8 dan seterusnya"],
[o(32.64),o(45.1),"Kenapa","Mudah · banyak cara · tak semua mampu menghafal · pelbagai cara"],[o(45.1),E0,"Jualan","Pendaftaran 2027 · jangan berputus asa · MATH TURBO 2027 · DM kami"],[E0,T.DUR,"End card","CTA BOFU + asteredu11.com.my"]]
TODO=[["'DM kami'","Transkrip dengar 'Dan kami untuk keterangan lanjut'. Caption ditulis 'DM kami' (sama seperti 'DM saya' yang disahkan dalam AS-F-015). Sahkan.",o(52.12)],
["Susun atur: skrin terbelah biasa","Footage ini berpakaian kemas, jadi saya guna gaya HYBRID biasa (papan atas, Cikgu penuh di bawah) dan bukan wajah dalam bulatan seperti Sifir 6. Beritahu jika mahu bulatan supaya siri sekata.",o(5.0)],
["ID fail skrip berbeza","Video: AS-F-016-Trick Sifir 8.mp4; skrip: AS-F-015_Trick Sifir 8.txt (sama seperti Sifir 6). Saya guna AS-F-016 ikut nama video dan arahan. Tag skrip TOFU+BOFU → HYBRID.",None],
["Lower third MATH TURBO 2027 + pil Pendaftaran 2027 dibuka","Tidak disebut; ikut DNA HYBRID dan video Aster sebelum ini.",o(45.1)]]
DONE=[["Kandungan papan disemak","Jawapan 08, 16, 24, 32, 40 | 48, 56, 64, 72, 80 betul; sebutan sepadan dengan tulisan.",o(27.14)],
["Papan diselaraskan dengan suara","B-roll dirakam berasingan (41 s): setiap nombor muncul dan disorot ketika disebut; label 1 × 8 = … mengikut sebutan.",o(9.68)],
["Durasi 56.3 s","Dalam sasaran BOFU 30–60 s. Satu take, tiada potongan (jeda tulis dikekalkan untuk rentak mengajar).",None],
["Thumbnail","Frame Cikgu senyum pandang kamera (0:01.5). Hook 4 + 4 perkataan dalam safe zone.",0.5],
["Muzik rasmi Aster","Aster_MuzikLatar_Ceria_100BPM. Tiada kredit perlu.",2.0],
["Safe zone & watermark","Teks di atas 80% frame dan di luar jalur kanan 15%; watermark sepanjang video.",0.5]]
TT="Anak masih lemah sifir 8? Cuba trick ni 👇 Tulis 0 hingga 4, sebelah tu 4 hingga 8. Lepas tu gandaan 2 dari bawah (0, 2, 4, 6, 8) untuk kedua-dua lajur. Siap sifir 8! Tak semua anak mampu menghafal, jadi kami datangkan pelbagai cara untuk anak kuasai sifir. Ibu ayah jangan berputus asa, DM kami untuk keterangan lanjut."
HS="#sifir8 #cikgualfarhan #trickmatematik #tuisyenonline #asteredu"
P={"DATA":{"caps":C,"mg":MG,"sfx":sfx,"zoom":ZOOM,"dur":round(T.DUR,2),"broll":[[o(3.2),o(32.7)]]},"SEG":SEG,"TODO":TODO,"DONE":DONE,"TT":TT,"HS":HS}
t=open(f"{HERE}/../AS-F-015_TrickSifir6/preview_page.html").read()
t=re.sub(r"const P=\{.*?\};\n","const P=__P__;\n",t,count=1,flags=re.S)
R=[("<title>AS-F-015 Trick Sifir 6</title>","<title>AS-F-016 Trick Sifir 8</title>"),
('<h1>AS-F-015 <mark>Trick Sifir 6</mark>: final</h1>','<h1>AS-F-016 <mark>Trick Sifir 8</mark>: preview</h1>'),
(re.search(r'<span class="status">.*?</span>\n',t).group(0),f'<span class="status"><b>Menunggu semakan</b> TOFU+BOFU → HYBRID · preview v1 · 540×960 · {T.DUR:.1f} saat · skrin terbelah</span>\n'),
(re.search(r'aria-valuemax="[\d.]+"',t).group(0),f'aria-valuemax="{T.DUR:.2f}"'),
(re.search(r'<p>Satu take: hanya.*?</p>',t,re.S).group(0),'<p>Satu take, tiada potongan: jeda semasa menulis dikekalkan supaya ibu sempat ikut. Video = thumbnail 1 s + isi 53.8 s + end card 1.5 s. Tag <b>TOFU+BOFU</b> → gaya <b>HYBRID hitam + kuning</b>: pembuka talking head, kemudian <b>skrin terbelah</b> (papan B-Roll Sifir 8 di atas, Cikgu di bawah) dengan LANGKAH 1–4, kemudian sebab trick ini dan jualan.</p>'),
('<div class="h">Malam yang tenang: ibu boleh ajar sifir 6 dalam 3 langkah</div>','<div class="h">Sifir 8 siap dalam 4 langkah, tanpa menghafal</div>'),
("<p>Dalam bulatan: selang-seli 100% dan 113% setiap ayat; muka kekal di sepertiga atas bulatan.</p>","<p>Talking head: selang-seli 100% dan 112% setiap ayat, berpaut pada muka (mata di sepertiga atas). Skrin terbelah: Cikgu di panel bawah.</p>"),
('"asf013-tab"','"asf016-tab"')]
for x,y in R:
    assert x in t,x[:60];t=t.replace(x,y)
a=t.index("<h3>Wajah dalam bulatan (dicerahkan)</h3>");b=t.index("<h3>Audio</h3>")
t=t[:a]+"""<h3>Colour grade</h3>
        <div class="tbl"><table><thead><tr><th>Langkah</th><th>Nilai</th><th>Kesan</th></tr></thead><tbody>
          <tr><td>Kecerahan</td><td class="n">gamma 0.92, +3%</td><td>Pencahayaan studio sudah baik; muka diangkat sedikit.</td></tr>
          <tr><td>Saturasi</td><td class="n">×1.05</td><td>Warna lebih hidup; warna kulit asli kekal (tiada anjakan hue).</td></tr>
          <tr><td>Papan B-roll</td><td class="n">dipotong ke kawasan tulisan, ×1.25</td><td>Nombor besar dan jelas di telefon.</td></tr>
        </tbody></table></div>
        """+t[b:]
t=t.replace("tick lembut (setiap nombor ditulis), ding (LANGKAH, selesai, jualan, end card), swoosh (pangkah HAFAL), click (DM)","tick lembut (setiap nombor ditulis), ding (LANGKAH, siap, jualan, end card), swoosh (pangkah MENGHAFAL), click (DM)")
t=t.replace('title="Perlu disahkan: 1 + 5 = 6"','title="Perlu disahkan: transkrip \\u2018Dan kami\\u2019"')
t=t.replace("__P__",json.dumps(P,ensure_ascii=False))
open(f"{OUT}/index.html","w").write(t)
json.dump(P,open(f"{HERE}/pagedata.json","w"),ensure_ascii=False)
f=lambda x:f"{int(x//60)}:{x%60:04.1f}"
L=["AS-F-016_Trick Sifir 8 — RINGKASAN PREVIEW",f"Aster · TOFU+BOFU → HYBRID (hitam + kuning) · spokesperson FARHAN · durasi {T.DUR:.1f} s · preview 540x960 · skrin terbelah","",
"1. TEKS HOOK / THUMBNAIL"," TRICK SIFIR 8 / UNTUK ANAK LEMAH SIFIR + tulisan '8 × 7 = 56'"," Frame Cikgu senyum pandang kamera (sumber 0:01.5). Fail: AS-F-016_Trick Sifir 8_THUMB.png","","2. CAPTION PENUH (burn-in, ikut sebutan)"]
L+=[f" {f(c[0])} {c[2].replace('*','')}" for c in caps]
L+=["","3. SFX, ANIMASI & B-ROLL (masa video)"]+[f" {f(m[0])}–{f(m[1])} {m[2]}: {m[3]}" for m in MG]
L+=[" SFX: "+", ".join(f"{f(t)} {n}" for t,n in sfx)," Zoom: "+", ".join(f"{f(z['t'])} {z['m']}" for z in ZOOM)]
L+=["","4. CTA"," Tengah video (TOFU, ±0:21): kad Follow saya @aster.edu_tpg"," Pil 'DM kami' (ikut sebutan)"," End card (HYBRID → CTA BOFU): WhatsApp Cikgu AlFarhan untuk daftar / cuba kelas · asteredu11.com.my · WhatsApp 011-5596 9070 · @aster.edu_tpg"]
L+=["","5. PERLU SEMAK"]+[f" - {a}: {b}" for a,b,_ in TODO]
L+=["","6. CAPTION TIKTOK + 5 HASHTAG"," "+TT,""," "+HS,""," Muzik: Aster_MuzikLatar_Ceria_100BPM (muzik rasmi Aster, tiada kredit perlu)","","Artifact preview: __URL__"]
open(f"{HERE}/RINGKASAN.txt","w").write("\n".join(L)+"\n")
