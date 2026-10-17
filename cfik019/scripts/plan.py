import json,re,sys
# Source cuts (seconds in CFik019). Hook line moved to the front; short dead air trimmed.
SEG=[("hook",11.42,14.20),("A",0.12,4.97),("B",5.08,7.32),("C",7.45,9.70),("D",9.83,11.32),("E",14.31,28.14),("F",28.33,30.95)]
OUTRO=2.2
def out_off(i): return sum(e-s for _,s,e in SEG[:i])
def o(src,seg=None):
    """map a source time to the output timeline (first segment containing it, or the named one)"""
    for i,(n,s,e) in enumerate(SEG):
        if (seg is None or n==seg) and s-0.02<=src<=e+0.02: return round(out_off(i)+min(max(src,s),e)-s,3)
    raise ValueError(src)
DUR=round(out_off(len(SEG)),3)
FIX={"Fikir":"Fi-K","kontakter.":"kontraktor.","money":"mana"}
UNSURE={"mana"}  # whisper heard "money"; context says "seperti mana"
t=json.load(open(sys.argv[1]))
W=[]
for w in (w for s in t for w in s["words"]):
    txt=FIX.get(w["w"].strip(),w["w"].strip())
    if txt.startswith("-") and W: W[-1]["w"]+=txt;W[-1]["e"]=w["e"];continue
    W.append({"w":txt,"s":w["s"],"e":w["e"],"fix":txt!=w["w"].strip()})
words=[]
def seg_of(m):
    for n,s,e in SEG:
        if s<=m<e: return n
    # word whose midpoint sits in a trimmed pause belongs to the segment that starts right after it
    c=[(s-m,n) for n,s,_ in SEG if 0<s-m<0.4]
    return min(c)[1] if c else None
for w in W:
    n=seg_of((w["s"]+w["e"])/2)
    if n is None: continue
    _,s,e=next(x for x in SEG if x[0]==n)
    words.append(dict(w,s=o(max(w["s"],s),n),e=o(max(min(w["e"],e),max(w["s"],s)+.05),n),seg=n,src=w["s"]))
words.sort(key=lambda x:x["s"])
HOT={"kunci","rumah","betul-betul.","tipu","kontraktor.","agak-agak,","meletup,","ulang-alik","impikan.","Fi-K","Studio,","3D","ukuran","anggaran","harga","A","Z","DM"}
chunks=[];cur=[]
for i,w in enumerate(words):
    cur.append(w);nx=words[i+1] if i+1<len(words) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nx or nx["s"]-w["e"]>0.3 or nx["seg"]!=w["seg"]:
        end=nx["s"] if nx and nx["s"]-w["e"]<0.3 else w["e"]+0.12
        chunks.append({"s":cur[0]["s"],"e":round(end,3),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"],**({"hot":1} if x["w"] in HOT else {}),**({"fix":1} if x["fix"] else {}),**({"unsure":1} if x["w"].strip(".,") in UNSURE else {})} for x in cur]});cur=[]
next(x for c in chunks for x in c["words"] if x["w"]=="agak-agak")["w"]+="?"  # "Kalau renovation ikut agak-agak?" reads as the hook question
# Motion graphics, keyed to source words then mapped to output time
G=[
 {"s":0,"e":o(14.20,"hook"),"kind":"hook","lines":["Renovate ikut","agak-agak?"],"punch":"Kos meletup.","punch_at":o(13.32,"hook"),"note":"Hook: masalah paling sakit dulu (dipindah dari 0:11)"},
 {"s":o(0.17),"e":o(3.50),"kind":"key","text":"Baru dapat kunci rumah?","draw_at":o(1.14),"note":"Ikon kunci dilukis garis halus, sasar penonton"},
 {"s":o(5.08),"e":o(11.32),"kind":"list","eyebrow":"Masalah biasa","items":[["Tak tahu nak mula dari mana",o(6.96)],["Takut kena tipu harga kontraktor",o(9.04)]],"note":"Senarai masalah muncul ikut ayat"},
 {"s":o(14.31),"e":o(18.66),"kind":"strike","eyebrow":"Renovate ikut agak-agak","items":[["Kos meletup",o(14.31)],["Kerja ulang-alik",o(14.52)],["Hasil tak seperti impian",o(15.92)]],"note":"Ulang 3 akibat, dipangkah satu per satu"},
 {"s":o(18.74),"e":o(19.72),"kind":"brand","note":"Logo Fi-K Studio (hijau) atas kad krim, masuk tepat pada 'Fi-K Studio'"},
 {"s":o(19.72),"e":o(21.12),"kind":"broll","img":"dining","sketch":"dining_sketch","label":"Rekaan 3D yang tepat","note":"B-roll CFik017: lakaran garis bertukar jadi gambar sebenar (3D ke realiti)"},
 {"s":o(21.12),"e":o(23.08),"kind":"broll","img":"family","dims":1,"label":"Ikut ukuran sebenar","note":"B-roll: garis dimensi dilukis atas dinding TV, punch-in ke panel kayu"},
 {"s":o(23.08),"e":o(25.24),"kind":"broll","img":"kitchen","quote":["Kabinet & kaunter","Kemasan dinding & lantai","Lampu & pendawaian"],"label":"Anggaran harga jelas","note":"B-roll: dapur kering, punch-in ke kaunter marmar + kad sebut harga ringkas"},
 {"s":o(25.24),"e":o(26.72),"kind":"broll","img":"toilet","label":"Kemasan sampai siap","note":"B-roll: butiran jubin mozek bilik air"},
 {"s":o(26.72),"e":o(28.14),"kind":"az","steps":["Konsep","3D","Bajet","Bina","Serah kunci"],"note":"Garis proses A ke Z dilukis kiri ke kanan"},
 {"s":o(28.40),"e":DUR,"kind":"cta","text":"DM kami","sub":"untuk keterangan lanjut","note":"CTA tenang, ikon kapal terbang kertas"},
 {"s":DUR,"e":DUR+OUTRO,"kind":"outro","note":"Kad penutup krim + logo hijau"},
]
SFX=[(0.00,"thud",0.55),(0.02,"air",0.5),(o(13.32,"hook"),"tick",0.6),(o(0.12,"A"),"whoosh",0.45),(o(1.14),"pen",0.4),
 (o(3.64),"thud",0.35),(o(5.08),"whoosh",0.35),(o(6.96),"tick",0.5),(o(9.04),"tick",0.5),
 (o(14.31),"tick",0.45),(o(14.52),"tick",0.45),(o(15.92),"tick",0.45),(o(18.74),"chime",0.55),(o(19.72),"whoosh",0.5),(o(19.80),"pen",0.45),(o(20.50),"shimmer",0.45),
 (o(21.12),"swipe",0.45),(o(21.40),"tick",0.35),(o(21.80),"tick",0.35),(o(23.08),"swipe",0.45),(o(23.50),"tick",0.35),(o(23.85),"tick",0.35),(o(24.20),"tick",0.35),
 (o(25.24),"swipe",0.45),(o(26.72),"whoosh",0.45),(o(26.80),"pen",0.4),(o(27.66),"chime",0.4),(o(28.40),"thud",0.35),(DUR,"whoosh",0.45),(DUR+0.25,"chime",0.6)]
# Zoom keyframes: (time, scale, originY%). Steps land on cuts (hidden by the cut); pushes inside a shot ease over 0.3s.
Z=[(0,1.16,30),(o(14.20,"hook")-.001,1.16,30),(o(0.12,"A"),1.0,40),(o(3.60),1.0,40),(o(3.90),1.12,32),(o(4.97),1.12,32),
   (o(5.08,"B"),1.0,40),(o(7.32,"B"),1.0,40),(o(7.45,"C"),1.08,34),(o(9.70,"C"),1.08,34),(o(9.83,"D"),1.14,30),(o(11.32,"D"),1.14,30),
   (o(14.31,"E"),1.0,40),(o(16.55),1.0,40),(o(16.85),1.08,34),(o(19.70),1.08,34),(o(26.72),1.0,40),(o(28.14,"E"),1.0,40),(o(28.33,"F"),1.1,32),(DUR,1.1,32)]
cuts=[{"id":n,"src_in":s,"src_out":e,"out":round(out_off(i),3)} for i,(n,s,e) in enumerate(SEG)]
pauses=[(4.97,5.08),(7.32,7.45),(9.70,9.83),(11.32,11.42),(14.20,14.31),(28.14,28.33)]
json.dump({"duration":DUR,"outro":OUTRO,"cuts":cuts,"removed":[{"src_in":a,"src_out":b} for a,b in pauses],
 "captions":chunks,"words":[{k:w[k] for k in ("w","s","e","src","fix")} for w in words],"graphics":G,
 "sfx":[{"t":round(t,3),"name":n,"gain":g} for t,n,g in SFX],"zoom":[{"t":round(t,3),"scale":s,"oy":y} for t,s,y in Z]},
 open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print("duration",DUR,"+ outro",OUTRO);print("\n".join(f"{c['s']:6.2f} {' '.join(x['w'] for x in c['words'])}" for c in chunks))
