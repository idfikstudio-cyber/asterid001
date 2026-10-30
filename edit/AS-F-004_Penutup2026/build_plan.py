# Pelan edit AS-F-004_Penutup2026 (Aster, TOFU). Semua masa grafik ditulis ikut masa SUMBER,
# kemudian ditukar ke garis masa output (thumbnail 1 s + potongan senyap).
# usage: python3 build_plan.py transcript.json plan.json
import json,re,sys
THUMB=1.0
# senyap >0.3 s (silencedetect -35 dB), dibuang dengan padding 0.08 s
SIL=[(17.58,17.92),(57.51,57.87),(69.61,69.97)]
CUT=[(a+0.08,b-0.08) for a,b in SIL]
SRC_END=86.70
KEEP=[];p=0.0
for a,b in CUT: KEEP.append((p,a)); p=b
KEEP.append((p,SRC_END))
def o(t):  # masa sumber -> masa output
    off=THUMB
    for a,b in KEEP:
        if t<b: return round(off+max(t,a)-a,3)
        off+=b-a
    return round(off,3)
DUR=o(SRC_END); END=1.5; TOTAL=round(DUR+END,3)

# ---- caption ----
t=json.load(open(sys.argv[1]))
FIX={"perempuan":"puan-puan","haji":"kaji","saja":"sahaja","memalainkan":"melainkan","bertapa":"bertapak","tim":"team"}
W=[]
for w in (w for s in t for w in s["words"]):
    x=w["w"].strip()
    if 49.6<w["s"]<49.9: continue          # "Kami sediakan" halusinasi Whisper (p=0.00); disemak semula: "bersama dengan kami"
    if x.startswith("-") and W: W[-1]["w"]+=x; W[-1]["e"]=w["e"]; continue
    core=re.sub(r"[.,?!]$","",x); W.append({"w":x.replace(core,FIX.get(core,core)),"s":w["s"],"e":w["e"]})
HOT={"2026","2027","terima","kasih","pakar","skill","teknik","dua","rakaman","lifetime","bahan","belajar","sukses","jutaan","doa","bakti","Allah","terbaik","faham","kaji"}
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w); nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.3:
        e=nxt["s"] if nxt and nxt["s"]-w["e"]<0.6 else w["e"]+0.2
        chunks.append({"s":o(cur[0]["s"]),"e":o(e),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":o(x["s"]),
            **({"hot":1} if re.sub(r"\W","",x["w"]).lower() in {h.lower() for h in HOT} else {})} for x in cur]}); cur=[]

# ---- grafik (masa sumber) ----
G=[
 dict(s=0.05,e=2.25,kind="series",text="PENUTUP 2026 · CIKGU ALFARHAN",note="Label siri di awal isi"),
 dict(s=0.25,e=3.30,kind="name",text="Cikgu AlFarhan",note="Label nama sekali di awal isi"),
 dict(s=1.30,e=3.20,kind="bignum",text="2026",sub="SELESAI ✓",note="Angka disebut: 'tahun 2026'"),
 dict(s=3.40,e=8.00,kind="note",title="Masa untuk...",text="Terima kasih, ibu ayah!",note="Nota tulisan tangan (gaya TOFU)"),
 dict(s=12.30,e=19.60,kind="check",items=[["Guru pakar subjek",12.70],["Skill",16.82],["Teknik menjawab exam",17.94]],note="Senarai semak muncul ikut percakapan"),
 dict(s=20.20,e=22.05,kind="strike",text="1 GURU · 1 KELAS",note="'bukan satu guru dalam satu kelas' – dipangkah"),
 dict(s=22.30,e=24.40,kind="bignum",text="2 GURU",sub="DALAM 1 KELAS",note="Angka disebut: 'dua guru dalam satu kelas'"),
 dict(s=25.10,e=29.60,kind="rec",text="Akses rakaman",sub="LIFETIME",note="Kad rakaman + ikon main"),
 dict(s=29.80,e=34.95,kind="note",title="Masalah sebenar",text="Topik kurang faham? Ulang kaji!",note="Nota 'Masalah Sebenar' (gaya TOFU)"),
 dict(s=35.60,e=39.85,kind="book",text="Bahan belajar disediakan",note="Ikon buku"),
 dict(s=39.88,e=41.15,kind="book-x",text="Tak payah cari buku luar",note="Buku luar dipangkah"),
 dict(s=41.30,e=46.40,kind="follow",text="@aster.edu_tpg",note="CTA tengah video: Follow saya, wajah dalam bulatan emas"),
 dict(s=51.60,e=55.30,kind="bignum",text="2027",sub="SAMBUNG BERSAMA KAMI",note="Angka disebut: 'tahun 2027'"),
 dict(s=56.40,e=59.10,kind="years",text="2026",to="2027",note="'2027 berbanding 2026'"),
 dict(s=63.70,e=66.30,kind="note",title="Kepada semua ibu ayah",text="Jutaan terima kasih",note="Nota tulisan tangan"),
 dict(s=71.70,e=79.55,kind="note",title="Doa seorang guru",text="Anak murid terus sukses",note="Nota tulisan tangan, momen emosi"),
 dict(s=79.68,e=81.50,kind="series",text="PENUTUP 2026 · CIKGU ALFARHAN",note="Pembahagi bahagian penutup"),
 dict(s=81.60,e=86.50,kind="note",title="Doakan kami",text="Terus menabur bakti",note="Nota tulisan tangan"),
]
for g in G: g["s"],g["e"]=o(g["s"]),o(g["e"])
for g in G:
    if g["kind"]=="check": g["items"]=[[a,o(b)] for a,b in g["items"]]
# SFX (masa sumber); 'end' = end card
SFX=[(0.0,"impact",0.55),(0.06,"whoosh",0.5),(1.30,"pop",0.6),(1.50,"ding",0.45),(3.40,"whoosh",0.45),(12.70,"tick",0.5),(16.82,"tick",0.5),
 (17.94,"tick",0.5),(20.25,"bonk",0.45),(22.30,"pop",0.6),(22.40,"ding",0.45),(25.10,"whoosh",0.45),(26.42,"pop",0.5),(29.80,"pop",0.45),
 (35.60,"pop",0.45),(39.90,"bonk",0.4),(41.30,"whoosh",0.45),(42.40,"click",0.6),(51.60,"pop",0.55),(53.54,"ding",0.4),(56.40,"whoosh",0.45),
 (63.70,"pop",0.45),(71.70,"whoosh",0.4),(79.68,"whoosh",0.45),(81.60,"pop",0.45)]
SFX=[{"t":o(a) if a>0 else a,"name":n,"gain":g} for a,n,g in SFX]+[{"t":DUR,"name":"whoosh","gain":0.5},{"t":DUR+0.15,"name":"ding","gain":0.4}]
# zoom: 'B' 1.12 (mata ~35%), 'P' 1.25 punch-in, 'push' tolak perlahan (momen emosi)
ZS=[(0.0,"B"),(2.32,"P"),(8.56,"B"),(11.70,"P"),(15.42,"B"),(19.68,"P"),(22.08,"B"),(24.50,"P"),(29.24,"B"),(35.20,"P"),(39.88,"B"),
    (41.24,"push"),(50.70,"B"),(54.46,"P"),(59.38,"B"),(63.76,"P"),(66.14,"B"),(71.28,"push"),(79.68,"B"),(81.60,"P")]
Z=[{"t":o(a),"mode":m} for a,m in ZS]
json.dump({"duration":TOTAL,"content_end":DUR,"thumb":THUMB,"keep":KEEP,"captions":chunks,"graphics":G,"sfx":SFX,"zoom":Z,
  "thumb_src":80.45,"hook":["TUITION","2026","SELESAI!"],"hook_sub":"Terima kasih, ibu ayah"},open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print("durasi",TOTAL,"caption",len(chunks))
for c in chunks[:5]+chunks[-4:]: print(c["s"],c["e"]," ".join(x["w"] for x in c["words"]))
