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
 {"s":4.98,"e":11.40,"kind":"list","eyebrow":"Masalah biasa","items":[["Tak tahu nak mula dari mana",6.96],["Takut kena tipu harga kontraktor",9.04]],"note":"Senarai masalah muncul ikut ayat"},
 {"s":11.50,"e":16.76,"kind":"strike","eyebrow":"Renovate ikut agak-agak","items":[["Kos meletup",13.32],["Kerja ulang-alik",14.52],["Hasil tak seperti impian",15.92]],"note":"Akibat dipangkah satu per satu"},
 {"s":18.74,"e":19.72,"kind":"brand","note":"Logo Fi-K Studio (hijau) pada 'Fi-K Studio'"},
 {"s":26.72,"e":28.10,"kind":"az","steps":["Konsep","3D","Bajet","Bina","Serah kunci"],"note":"Garis proses A ke Z atas montaj"},
 {"s":29.26,"e":DUR,"kind":"cta","text":"DM kami","sub":"untuk keterangan lanjut","note":"CTA tenang, ikon kapal terbang kertas"},
 {"s":DUR,"e":DUR+OUTRO,"kind":"outro","note":"Kad penutup krim + logo hijau"},
]
SFX=[(0.00,"air",0.5),(0.05,"thud",0.5),(1.72,"whoosh",0.4),(3.76,"thud",0.35),(4.98,"whoosh",0.3),(6.96,"tick",0.5),(9.04,"tick",0.5),
 (11.50,"whoosh",0.3),(13.32,"tick",0.45),(14.52,"tick",0.45),(15.92,"tick",0.45),(16.76,"whoosh",0.45),(18.74,"chime",0.55),
 (19.72,"pen",0.45),(20.40,"shimmer",0.45),(21.12,"swipe",0.45),(21.40,"tick",0.3),(21.80,"tick",0.3),(23.08,"swipe",0.45),
 (23.50,"tick",0.3),(23.85,"tick",0.3),(24.20,"tick",0.3),(25.24,"swipe",0.4),(25.92,"swipe",0.35),(26.60,"swipe",0.35),(26.72,"pen",0.35),
 (27.28,"swipe",0.35),(27.66,"chime",0.35),(27.96,"whoosh",0.4),(29.26,"thud",0.35),(DUR,"whoosh",0.45),(DUR+0.25,"chime",0.6)]
# Face zoom (time, scale, originY%). Instant steps land on sentence starts or hide under B-roll; pushes ease over 0.3s.
Z=[(0,1.0,40),(3.70,1.0,40),(3.98,1.12,32),(4.97,1.12,32),(4.98,1.0,40),(9.03,1.0,40),(9.04,1.1,33),(11.49,1.1,33),(11.50,1.0,40),
   (13.31,1.0,40),(13.32,1.12,32),(14.51,1.12,32),(14.52,1.06,36),(16.76,1.06,36),(18.74,1.0,40),(27.96,1.0,40),(29.25,1.0,40),(29.26,1.1,33),(DUR,1.1,33)]
json.dump({"duration":DUR,"outro":OUTRO,"cuts":[{"id":"full","src_in":0,"src_out":SRC_DUR,"out":0}],
 "captions":chunks,"words":W,"broll":B,"graphics":G,
 "sfx":[{"t":round(t,3),"name":n,"gain":g} for t,n,g in SFX],"zoom":[{"t":t,"scale":s,"oy":y} for t,s,y in Z]},
 open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"caption chunks; duration",DUR,"+ outro",OUTRO)
