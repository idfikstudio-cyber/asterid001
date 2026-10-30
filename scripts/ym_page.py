import json,sys
S=sys.argv[1]; m=json.load(open(S+"/edit/tmp540/meta.json"))
FIXES={"pula":"pulang"}
caps=[{"s":round(c["s"],2),"e":round(c["e"],2),"w":[{"t":w,"hl":h,"fix":FIXES.get(w.rstrip("?")) if any(x[0] in ("tadi","collection") for x in c["w"]) else None} for w,h in c["w"]]} for c in m["caps"]]
G={"label":"Label nama","rows":"Kad senarai","broll":"B-roll sistem","callout":"Callout","chip":"Chip ikon","pile":"B-roll animasi","timebar":"Bar masa","comment":"Gelembung komen"}
D={"label":"Farhan · Yuran.my (pil biru, atas-kiri)","rows":None,"broll":"Senarai invois Yuran.my (demo), nama/item & jumlah individu diblur, zoom perlahan ke lajur Status",
"callout":"Tally ke tak? + kotak sorotan lajur PAID/UNPAID","chip":"↻ Ulang setiap hari","pile":"Animasi sendiri: resit, rekod yuran & invois bertimbun, jam berpusing laju",
"timebar":"Waktu mengajar: bar biru dimakan 'dicuri kerja admin'","comment":"Setuju atau tak setuju? Kongsi pendapat di ruang komen"}
ROWS={2.55:"Rutin harian cikgu: Pagi kutip yuran / Tengah hari buat resit / Petang buat syllabus / Malam kira yuran",24.1:"Cikgu KAFA: ✓ Mendidik / ✗ Kerani sekolah (dipangkah)"}
mg=[[0,1.0,"Thumbnail","CIKGU KAFA atau KERANI? atas frame Farhan menunjuk (sumber 0:25.8)"]]
for t0,t1,k in m["gfx"]: mg.append([round(t0,2),round(t1,2),G[k],ROWS.get(round(t0,2)) if k=="rows" else D[k]])
mg.append([round(m["end0"],2),round(m["dur"],2),"End card","Kad profil TikTok Yuran.My Street @yuran.my (avatar dari BRAND/Yuran Tiktok.jpg), butang + Follow berdenyut dengan riak ketuk, CTA Follow TikTok Yuran.my untuk tips urus yuran sekolah, Cara MUDAH Urus Yuran, hello@yuran.my"])
mg.sort()
cuts=[1.0];[cuts.append(cuts[-1]+b-a) for a,b in m["edl"]]
zoom=[{"t":round(cuts[i],2),"m":("130% punch-in" if z>1.2 else "115% (asas)")} for i,z in enumerate(m["zoom"])]
data={"caps":caps,"mg":mg,"sfx":[[round(t,2),n] for t,n,g in m["sfx"]],"zoom":zoom,"dur":round(m["dur"],2)}
E=round(m["end0"],2)
SEG=[[0,1.0,"Thumbnail","CIKGU KAFA atau KERANI?"],[1.0,2.57,"Hook","Cikgu KAFA ataupun kerani sebenarnya? Label Farhan · Yuran.my"],
[2.57,10.8,"Rutin harian","Kad rutin pagi→malam, B-roll sistem 'Tally ke tak?'"],[10.8,14.93,"Ulang setiap hari","Chip ↻ Ulang setiap hari"],
[14.93,19.53,"PnP berkualiti","Talking head sahaja, punch-in"],[19.53,24.1,"Kerja admin curi waktu","B-roll animasi resit bertimbun, bar Waktu mengajar"],
[24.1,27.97,"Mendidik, bukan kerani","Kad ✓ Mendidik / ✗ Kerani sekolah"],[27.97,E,"Ajak komen","Gelembung Setuju atau tak setuju?"],[E,data["dur"],"End card","Follow TikTok @yuran.my + hello@yuran.my"]]
DONE=[["Guna video trim Farhan","TOFU_CikguatauKerani.mp4 (28.6 s, 1080×1920). Isi tidak dipotong. v1 (potongan saya dari MOV mentah) dibuang.",1.0],
["Grafik dikurangkan","v1 ada kad 'Bila waktunya?' dan lebih banyak elemen bertindih. v2: satu elemen pada satu masa, dan bahagian 'Bila waktu cikgu nak pastikan PnP…' dibiarkan bersih.",15.0],
["Isu v1 selesai sendiri","'Kerja admin' kini jelas dalam transkrip. Baris 'update surat' dan 'bila sepatutnya' tiada dalam video trim.",19.6],
["Durasi dalam sasaran TOFU","31.1 s = thumbnail 1 s + isi 28.6 s + end card 1.5 s."],
["Thumbnail 1 saat","CIKGU KAFA / atau / KERANI? atas frame Farhan menunjuk ke kamera (sumber 0:25.8). Tiada logo di awal. PNG berasingan dieksport.",0.3],
["Caption","Sepanjang video, 1–3 perkataan, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2. Dalam safe zone. Atas B-roll, caption dapat pil biru gelap.",3.0],
["B-roll & privasi","B-roll sistem dari B-ROLL/Sek-Integrasi-Demo-Yuran.My (2.5 s), lajur nama/item dan jumlah individu diblur. B-roll kedua: animasi resit/invois yang saya jana sendiri (berlesen penuh).",8.6],
["Brand","Biru #2A3B8F + aksen #29ABE2, logo putih atas latar biru, tiada aset Fi-k Studio atau Aster. Tiada harga, statistik atau tawaran ditambah.",30.0],
["End card: Follow TikTok Yuran.my","Kad profil TikTok dari aset baru BRAND/Yuran Tiktok.jpg: avatar logo, Yuran.My Street, @yuran.my, butang + Follow (biru aksen, berdenyut + riak ketuk), CTA 'Follow TikTok Yuran.my untuk tips urus yuran sekolah', 'Cara MUDAH Urus Yuran', hello@yuran.my. Bilangan follower/likes dari screenshot tidak dipaparkan (statistik). Butang Follow guna biru brand, bukan merah TikTok.",30.0],
["Audio","Denoise ringan, compressor, −13.9 LUFS, true peak −2.1 dBTP. Muzik ~22 dB bawah suara dengan ducking."]]
TODO=[["\"Pagi tadi pula collection\"","Transkrip dengar 'pulang'. Caption tulis 'pula'. Sila dengar dan sahkan.",9.4],
["Ejaan PnP","Disebut 'P-N-P'. Caption 'PnP'. Jika mahu istilah rasmi 'PdP', beritahu.",16.5],
["Muzik dijana sendiri","Folder MUSIC/ Yuran.my tiada; Farhan pilih muzik jana sendiri (korporat ringan, 100 BPM, bebas hak cipta)."],
["Tiada video rujukan gaya","BRAND/ tiada rujukan-gaya-*.mp4. Diedit ikut DNA Yuran.my sahaja (Farhan setuju)."],
["Avatar end card resolusi rendah","Avatar diambil dari screenshot BRAND/Yuran Tiktok.jpg (bulatan ~172 px), dibesarkan ~1.7× untuk final 1080p. Lebih tajam jika ada fail gambar profil TikTok asal."],
["Gambar 'Pecah masuk KAFA' tidak digunakan","Video tidak menyebut kecurian/tunai, jadi gambar berita itu akan menambah fakta. Ada juga muka suspek dan nama sekolah."],
["Preview MP4 belum di Drive","Alat Drive yang saya ada tidak dapat muat naik fail video besar. RINGKASAN dan log sudah dikemas kini; MP4 preview ada di halaman ini."]]
TT="Cikgu KAFA masuk untuk mendidik, bukan jadi kerani sekolah. Pagi kutip yuran, tengah hari buat resit, malam kira yuran… bila masa nak pastikan PnP berkualiti? Setuju ke tak setuju? Komen di bawah."
HS="#cikgukafa #sekolahkafa #yuranmy #kerjaadmin #cikgu"
tpl=open(S+"/page_tpl.html").read()
out=(tpl.replace("__DATA__",json.dumps(data,ensure_ascii=False)).replace("__SEG__",json.dumps(SEG,ensure_ascii=False))
 .replace("__DONE__",json.dumps(DONE,ensure_ascii=False)).replace("__TODO__",json.dumps(TODO,ensure_ascii=False))
 .replace("__TT__",json.dumps(TT,ensure_ascii=False)).replace("__HS__",json.dumps(HS)).replace("__DUR__",str(data["dur"])))
open(S+"/art/index.html","w").write(out)
json.dump({"caps":caps,"mg":mg,"sfx":data["sfx"],"todo":TODO,"tt":TT,"hs":HS},open(S+"/art/ringkasan.json","w"),ensure_ascii=False)
print("ok")
