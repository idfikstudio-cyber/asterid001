# Bina data halaman preview (preview/AS-F-004.html) + RINGKASAN.txt dari plan.json.
# usage: python3 build_page.py OUTDIR
import json,os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); out=sys.argv[1]
P=json.load(open(os.path.join(HERE,"plan.json")))
ORIG={"puan-puan":"perempuan","kaji":"haji","sahaja":"saja","melainkan":"memalainkan","bertapak":"bertapa","team":"tim"}
caps=[{"s":c["s"],"e":c["e"],"w":[{"t":w["w"],"hl":bool(w.get("hot")),"fix":ORIG.get(w["w"].rstrip(".,?!"))} for w in c["words"]]} for c in P["captions"]]
D=P["duration"]; CE=P["content_end"]
LAB={"series":"Label siri","name":"Label nama","bignum":"Angka besar","note":"Nota tangan","check":"Senarai semak","strike":"Dipangkah","rec":"Kad rakaman","book":"Ikon buku","book-x":"Buku dipangkah","follow":"CTA Follow","years":"Tahun"}
def desc(g):
    if g["kind"]=="check": return " / ".join(i[0] for i in g["items"])
    if g["kind"]=="note": return f'{g["title"]}: {g["text"]}'
    if g["kind"]=="years": return f'{g["text"]} → {g["to"]}'
    return g["text"]+(f' · {g["sub"]}' if g.get("sub") else "")
mg=[[0,P["thumb"],"Thumbnail","TUITION 2026 SELESAI! + pil Terima kasih, ibu ayah"],[0,D,"Watermark","asteredu11.com.my sepanjang video, putih 68% + bayang halus, atas-kiri 12%"]]
mg+=[[g["s"],g["e"],LAB[g["kind"]],desc(g)] for g in P["graphics"]]
mg+=[[CE,D,"End card","Wajah bulatan emas, Cikgu AlFarhan, @aster.edu_tpg, CTA Follow, asteredu11.com.my besar, WhatsApp 011-5596 9070"]]
sfx=[[s["t"],s["name"]] for s in P["sfx"]]
zoom=[{"t":z["t"],"m":{"B":"112% (asas)","P":"125% punch-in","push":"112→122% tolak perlahan"}[z["mode"]]} for z in P["zoom"]]
o=lambda x:x  # masa sudah dalam output
SEG=[[0,1.0,"Thumbnail","TUITION 2026 SELESAI! · Terima kasih, ibu ayah"],
 [1.0,9.5,"Terima kasih 2026","Label siri + nama, angka 2026 SELESAI, nota Terima kasih, ibu ayah"],
 [9.5,42.0,"Apa yang kami sediakan","Senarai semak guru pakar / skill / teknik, 1 GURU dipangkah → 2 GURU, rakaman LIFETIME, nota Masalah sebenar, bahan belajar"],
 [42.0,51.5,"Bersandar pada Allah","CTA Follow tengah video (wajah bulatan emas), zoom tolak perlahan"],
 [51.5,60.0,"Sambung 2027","Angka 2027 + Sambung bersama kami, 2026 → 2027"],
 [60.0,80.4,"Terima kasih & doa","Nota Jutaan terima kasih, nota Doa seorang guru, zoom tolak perlahan"],
 [80.4,CE,"Penutup","Label siri, nota Doakan kami: Terus menabur bakti"],
 [CE,D,"End card","Follow untuk tips belajar anak seterusnya + asteredu11.com.my + WhatsApp"]]
DONE=[
 ["Jenis footage: satu take berterusan","Tiada take ulangan atau ayat silap. Isi tidak dipotong; hanya 3 senyap lebih 0.3 s dibuang (padding 0.08 s).",17.0],
 ["Muzik latar ikut mood","Mood video: hangat, bersyukur, penutup tahun. Muzik piano lembut + petikan gitar + pad, D major, 84 BPM, mula perlahan dan naik sedikit selepas 23 s. Sekitar 22 dB di bawah suara dengan ducking; naik sedikit di thumbnail dan end card.",2.0],
 ["Gaya TOFU","Biru gelap + kuning, nota tulisan tangan (termasuk 'Masalah sebenar'), ikon, CTA Follow dengan wajah dalam bulatan emas di tengah video (ikut rujukan-gaya-TOFU).",43.0],
 ["Ejaan dibetulkan","puan-puan (transkrip: perempuan), ulang kaji (haji), sahaja (saja), melainkan (memalainkan), bertapak (bertapa), team (tim). Disemak dengan transkrip kedua.",30.0],
 ["Angka tepat","2026, 2027, dua guru dalam satu kelas: dipapar seperti disebut.",23.5],
 ["Wajah, bukan logo","Bulatan emas guna Logo SocMed Aster. Tiada Logo Rasmi Aster / ASTER EDU, tiada aset Fi-k Studio atau Yuran.my.",43.0],
 ["Watermark & safe zone","asteredu11.com.my sepanjang video termasuk thumbnail dan end card. Teks di atas 80% frame dan di luar jalur kanan 15%.",20.0],
 ["End card TOFU","Wajah bulatan emas + Cikgu AlFarhan + @aster.edu_tpg, CTA 'Follow untuk tips belajar anak seterusnya', asteredu11.com.my besar, WhatsApp 011-5596 9070.",CE+0.8],
]
TODO=[
 ["Muzik dari luar MUSIC/","Folder MUSIC/ Aster kosong, jadi muzik ini dijana sendiri (scripts/music.py, asal dan bebas hak cipta). Peraturan biasa: muzik hanya dari MUSIC/. Sahkan boleh guna, atau letak trek berlesen dalam MUSIC/ dan saya tukar.",5.0],
 ["Nama fail: AS-F-003 atau AS-F-004?","Video bernama AS-F-003_Penutup2026.mp4 tetapi skrip AS-F-004_Penutup2026.txt, dan AS-F-003 sudah dipakai untuk SoalanMath dalam log. Saya guna AS-F-004."],
 ["\"Hanya Allah dan Tuhan sahaja\"","Dua transkrip dengar ayat yang sama. Sila dengar dan sahkan caption.",44.6],
 ["\"Dengan hormat dan terhormatnya\"","Caption ikut apa yang didengar. Sahkan ejaan.",78.0],
 ["\"Kami sediakan\" dibuang dari caption","Whisper tulis 'Kami sediakan bersama dengan kami' pada 0:50.6 (keyakinan 0%). Semakan kedua dengar 'pembelajaran bersama dengan kami' sahaja, jadi caption ikut itu.",50.5],
 ["Durasi 88.6 s","Melebihi sasaran TOFU 20–45 s. Isi tidak dipotong (satu take, tiada ulangan)."],
 ["Thumbnail","Hook: TUITION 2026 SELESAI! + 'Terima kasih, ibu ayah' atas frame Cikgu tersenyum (sumber 1:20.4).",0.3],
 ["Tiada B-roll","B-ROLL/ hanya ada AS-F-003_Broll_SoalanMath (rakaman iPad soalan darab), tidak sesuai untuk video penutup."],
 ["Fail BRAND tiada","BRAND/warna.txt dan rujukan-aster.txt tiada dalam folder BRAND/. Video ini tiada harga, jadi tiada fakta harga untuk disemak. Font: Poppins + Caveat."],
]
TT="Tuition 2026 dah selesai 🎓 Terima kasih ibu ayah yang percaya dengan kami tahun ni. Doakan saya & team terus menabur bakti untuk generasi baru 💛"
HS="#cikgualfarhan #asteredu #tuitiononline #terimakasihibuayah #2027"
data=dict(DATA=dict(caps=caps,mg=mg,sfx=sfx,zoom=zoom,dur=D),SEG=SEG,DONE=DONE,TODO=TODO,TT=TT,HS=HS)
tpl=open(os.path.join(HERE,"page_template.html")).read()
js="\n".join(f"const {k}={json.dumps(v,ensure_ascii=False)};" for k,v in data.items())
open(os.path.join(out,"index.html"),"w").write(tpl.replace("/*DATA*/",js))
# RINGKASAN.txt
fmt=lambda t:f"{int(t//60)}:{t%60:04.1f}"
L=["AS-F-004_Penutup2026 — RINGKASAN PREVIEW (Aster, TOFU)","",
 "1) HOOK / THUMBNAIL","   TUITION 2026 SELESAI!  ·  pil: Terima kasih, ibu ayah  (frame Cikgu tersenyum, sumber 1:20.4)","",
 "2) CAPTION PENUH"]+[f"   {fmt(c['s'])}  "+" ".join(w["t"] for w in c["w"]) for c in caps]+["",
 "3) GRAFIK, SFX & B-ROLL (masa video)"]+[f"   {fmt(m[0])}–{fmt(m[1])}  {m[2]}: {m[3]}" for m in mg]+[
 "   SFX: "+", ".join(f"{fmt(s[0])} {s[1]}" for s in sfx),
 "   Zoom: "+", ".join(f"{fmt(z['t'])} {z['m']}" for z in zoom),
 "   B-roll: tiada (B-ROLL/ tiada klip sesuai)",
 "   Muzik: muzik asal dijana sendiri (piano + petikan + pad, D major 84 BPM), ~22 dB bawah suara + ducking","",
 "4) CTA","   Tengah video: Follow saya (wajah bulatan emas + @aster.edu_tpg)","   End card: Follow untuk tips belajar anak seterusnya + asteredu11.com.my + WhatsApp 011-5596 9070","",
 "5) PERLU SEMAK"]+[f"   - {t[0]}: {t[1]}" for t in TODO]+["",
 "6) CAPTION TIKTOK",f"   {TT}",f"   {HS}",""]
open(os.path.join(out,"AS-F-004_Penutup2026_RINGKASAN.txt"),"w").write("\n".join(L))
print("ok",len(caps))
