import json,re,sys
# CFik019 is already trimmed by the client: keep the original timeline untouched (no cuts, no reordering).
# B-roll and graphics are laid on top; times below are seconds in the original video.
SRC_DUR=31.068;OUTRO=2.2;DUR=SRC_DUR
FIX={"Fikir":"Fi-K","kontakter.":"kontraktor.","money":"mana"}
UNSURE={"mana"}  # whisper heard "money"; context says "seperti mana"
t=json.load(open(sys.argv[1]))
W=[]
for w in (w for s in t for w in s["words"]):
    txt=FIX.get(w["w"].strip(),w["w"].strip())
    if txt.startswith("-") and W: W[-1]["w"]+=txt;W[-1]["e"]=w["e"];continue
    W.append({"w":txt,"s":round(w["s"],3),"e":round(w["e"],3),"fix":txt!=w["w"].strip()})
HOT={"kunci","rumah","betul-betul.","tipu","kontraktor.","agak-agak,","meletup,","ulang-alik","impikan.","Fi-K","Studio,","3D","ukuran","anggaran","harga","A","Z","DM"}
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nx=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nx or nx["s"]-w["e"]>0.3:
        end=nx["s"] if nx and nx["s"]-w["e"]<0.3 else w["e"]+0.15
        chunks.append({"s":cur[0]["s"],"e":round(end,3),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"],**({"hot":1} if x["w"] in HOT else {}),**({"fix":1} if x["fix"] else {}),**({"unsure":1} if x["w"].strip(".,") in UNSURE else {})} for x in cur]});cur=[]
# B-roll: "pan" = camera move rendered from Fi-K's 360 design tours (aihouse); "still" = photo with slow push-in
B=[
 {"s":0.00,"e":1.72,"kind":"pan","clip":"living_banglo","eyebrow":"Rekaan 3D Fi-K Studio","label":"","note":"Hook visual: pan ruang tamu rekaan Fi-K, terus nampak hasil"},
 {"s":11.50,"e":13.32,"kind":"pan","clip":"dream_teres","eyebrow":"","label":"","note":"Rumah impian dulu: pan ruang tamu, sebelum dikoyak pada 'kos meletup'"},
 {"s":16.76,"e":18.74,"kind":"pan","clip":"dining_banglo","eyebrow":"Rekaan 3D Fi-K Studio","label":"Rumah yang korang impikan","note":"Pada 'seperti mana yang kita impikan'"},
 {"s":19.72,"e":21.12,"kind":"still","img":"render_living","sketch":"render_living_sketch","eyebrow":"Rekaan 3D Fi-K Studio","label":"3D yang tepat","note":"Lakaran garis bertukar jadi render 3D"},
 {"s":21.12,"e":23.08,"kind":"still","img":"family","dims":1,"eyebrow":"Projek siap Fi-K Studio","label":"Ikut ukuran sebenar","note":"Gambar projek siap (CFik017) + garis dimensi"},
 {"s":23.08,"e":25.24,"kind":"pan","clip":"kitchen_teres","quote":["Kabinet & kaunter","Kemasan dinding & lantai","Lampu & pendawaian"],"eyebrow":"Rekaan 3D Fi-K Studio","label":"Anggaran harga jelas","note":"Pan dapur kering + kad sebut harga"},
 {"s":25.24,"e":25.92,"kind":"pan","clip":"m_master","eyebrow":"Rekaan 3D Fi-K Studio","label":"Bilik tidur utama","note":"Montaj A-Z: 4 rumah berbeza"},
 {"s":25.92,"e":26.60,"kind":"pan","clip":"m_kids","eyebrow":"Rekaan 3D Fi-K Studio","label":"Bilik anak","note":"Montaj"},
 {"s":26.60,"e":27.28,"kind":"pan","clip":"m_bath","eyebrow":"Rekaan 3D Fi-K Studio","label":"","note":"Montaj (bilik air utama), label diganti garis A-Z"},
 {"s":27.28,"e":27.96,"kind":"pan","clip":"m_condo","eyebrow":"Rekaan 3D Fi-K Studio","label":"","note":"Montaj (ruang makan kondo), label diganti garis A-Z"},
]
G=[
 {"s":0.00,"e":1.72,"kind":"hook","lines":["Baru dapat","kunci rumah?"],"note":"Hook: soalan terus kepada sasaran"},
 {"s":3.76,"e":4.95,"kind":"pill","text":"Dengar ni dulu","note":"Penegasan + punch-in"},
 {"s":4.98,"e":6.96,"kind":"pill","text":"2 masalah paling biasa","note":"Set-up untuk kad masalah"},
 {"s":6.96,"e":9.04,"kind":"problem","n":"Masalah 01","lines":[[["Tak",6.96],["tahu",7.48],["nak",7.76]],[["mula",7.90,"it"],["dari",8.12],["mana",8.42]]],"slash":8.72,"note":"Kad penuh skrin tanpa wajah: perkataan ikut suara, kemudian slash"},
 {"s":9.04,"e":11.50,"kind":"problem","n":"Masalah 02","lines":[[["Takut",9.04],["kena",9.86],["tipu",9.98,"it"]],[["harga",10.46],["kontraktor",11.00]]],"slash":11.32,"note":"Kad penuh skrin tanpa wajah: perkataan ikut suara, kemudian slash"},
 {"s":11.50,"e":13.32,"kind":"pill","text":"Renovate ikut agak-agak?","note":"Soalan pembuka akibat"},
 {"s":13.32,"e":14.52,"kind":"tear","img":"dream_teres_end","a":"Kos","b":"meletup.","note":"Gambar rumah impian koyak dua, teks 'Kos meletup' di belakang"},
 {"s":14.52,"e":16.76,"kind":"kinetic","phrases":[{"t":14.52,"a":"Kerja","b":"ulang-alik.","fx":"shuttle"},{"t":15.92,"a":"Hasil tak seperti","b":"impian.","fx":"drift"}],"note":"Wajah dikabur + digelapkan, frasa besar dengan gerakan ikut maksud"},
 {"s":18.74,"e":19.72,"kind":"brand","note":"Logo Fi-K Studio (hijau) pada 'Fi-K Studio'"},
 {"s":26.72,"e":28.10,"kind":"az","steps":["Konsep","3D","Bajet","Bina","Serah kunci"],"note":"Garis proses A ke Z atas montaj"},
 {"s":29.26,"e":DUR,"kind":"cta","text":"DM kami","sub":"untuk keterangan lanjut","note":"CTA tenang, ikon kapal terbang kertas"},
 {"s":DUR,"e":DUR+OUTRO,"kind":"outro","note":"Kad penutup krim + logo hijau"},
]
SFX=[(0.00,"air",0.5),(0.05,"thud",0.5),(1.72,"whoosh",0.4),(3.76,"thud",0.35),(4.98,"tick",0.4),
 (6.96,"whoosh",0.5),(6.98,"thud",0.45),(7.48,"tick",0.3),(7.90,"tick",0.3),(8.72,"slash",0.85),
 (9.04,"whoosh",0.45),(9.06,"thud",0.45),(9.98,"tick",0.3),(11.00,"tick",0.3),(11.32,"slash",0.85),(11.50,"whoosh",0.4),
 (13.24,"rip",0.8),(13.40,"boom",0.7),(14.52,"swipe",0.5),(14.80,"swipe",0.35),(15.92,"air",0.45),(16.76,"whoosh",0.45),(18.74,"chime",0.55),
 (19.72,"pen",0.45),(20.40,"shimmer",0.45),(21.12,"swipe",0.45),(21.40,"tick",0.3),(21.80,"tick",0.3),(23.08,"swipe",0.45),
 (23.50,"tick",0.3),(23.85,"tick",0.3),(24.20,"tick",0.3),(25.24,"swipe",0.4),(25.92,"swipe",0.35),(26.60,"swipe",0.35),(26.72,"pen",0.35),
 (27.28,"swipe",0.35),(27.66,"chime",0.35),(27.96,"whoosh",0.4),(29.26,"thud",0.35),(DUR,"whoosh",0.45),(DUR+0.25,"chime",0.6)]
# Face zoom (time, scale, originY%). Instant steps land on sentence starts or hide under B-roll; pushes ease over 0.3s.
Z=[(0,1.0,40),(3.70,1.0,40),(3.98,1.12,32),(4.97,1.12,32),(4.98,1.0,40),(6.96,1.0,40),(11.49,1.0,40),(11.50,1.08,35),(13.31,1.08,35),
   (13.32,1.0,40),(16.76,1.16,32),(18.74,1.0,40),(27.96,1.0,40),(29.25,1.0,40),(29.26,1.1,33),(DUR,1.1,33)]
# 1s thumbnail (option A) before the content: shift every source-timed event by INTRO
INTRO=1.0
sh=lambda x:round(x+INTRO,3)
for c in chunks:
    c["s"],c["e"]=sh(c["s"]),sh(c["e"])
    for w in c["words"]: w["s"]=sh(w["s"])
for w in W: w["s"],w["e"]=sh(w["s"]),sh(w["e"])
for g in B+G:
    g["s"],g["e"]=sh(g["s"]),sh(g["e"])
    if "slash" in g: g["slash"]=sh(g["slash"])
    if g.get("kind")=="problem": g["lines"]=[[[w[0],sh(w[1])]+w[2:] for w in l] for l in g["lines"]]
    for ph in g.get("phrases",[]): ph["t"]=sh(ph["t"])
G.insert(0,{"s":0,"e":INTRO,"kind":"thumb","note":"Thumbnail pilihan A selama 1 saat, kemudian terus masuk konten"})
SFX=[(0.0,"thud",0.45),(0.82,"whoosh",0.45)]+[(sh(t),n,g) for t,n,g in SFX]
Z=[(0,1.0,40)]+[(sh(t),sc,y) for t,sc,y in Z]
SRC_DUR,DUR=SRC_DUR,round(DUR+INTRO,3)
json.dump({"duration":DUR,"outro":OUTRO,"intro":INTRO,"cuts":[{"id":"full","src_in":0,"src_out":SRC_DUR,"out":INTRO}],
 "captions":chunks,"words":W,"broll":B,"graphics":G,
 "sfx":[{"t":round(t,3),"name":n,"gain":g} for t,n,g in SFX],"zoom":[{"t":t,"scale":s,"oy":y} for t,s,y in Z]},
 open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"caption chunks; duration",DUR,"+ outro",OUTRO)
