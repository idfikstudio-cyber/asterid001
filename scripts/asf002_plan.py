# Plan for AS-F-002 (SPM 2026, TOFU): captions, graphics, sfx, zoom on the OUTPUT timeline.
# Output = 1.0 s thumbnail + content (edl) + 1.5 s end card.
import json,re,sys
edl=json.load(open(sys.argv[1]))
THUMB=1.0;END=1.5
CONTENT=edl["duration"];DUR=round(THUMB+CONTENT+END,3)
FIX={"kuniakan":"kurniakan","gabrah":"gabra","taker":"tackle","Taker":"Tackle"}
W=[]
for w in edl["words"]:
    t=w["w"];core=re.sub(r"[.,?!]","",t);t=t.replace(core,FIX.get(core,core))
    x=dict(w,w=t,fix=core if core in FIX else None,s=round(w["s"]+THUMB,3),e=round(w["e"]+THUMB,3))
    if t.startswith("-") and W: W[-1]["w"]+=t;W[-1]["e"]=x["e"];continue
    W.append(x)
def at(word,n=1,field="s"):
    k=0
    for x in W:
        if re.sub(r"[.,?!]","",x["w"]).lower()==word.lower():
            k+=1
            if k==n: return x[field]
    raise KeyError(word)
def src(t):  # source time -> output time
    for sg in edl["segments"]:
        if sg["src_in"]<=t<=sg["src_out"]: return round(THUMB+sg["out_in"]+t-sg["src_in"],3)
    for sg in edl["segments"]:
        if t<sg["src_in"]: return round(THUMB+sg["out_in"],3)
    return round(THUMB+CONTENT,3)
# caption chunks: <=3 words, break on punctuation or gap > 0.35 s
HOT={"spm","esok","ketenangan","tenang","tenang-tenang","gabra","takut","senang","susah","kosong","good","luck","sukses","kejayaan","tackle"}
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.35:
        e=nxt["s"] if nxt and nxt["s"]-w["e"]<0.6 else w["e"]+0.2
        chunks.append({"s":cur[0]["s"],"e":round(min(e,THUMB+CONTENT),3),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"],"fix":x["fix"],
            "hot":re.sub(r"\W","",x["w"].lower()) in HOT or x["w"].lower().startswith("tenang")} for x in cur]});cur=[]
C0,C1=THUMB,round(THUMB+CONTENT,3)
G=[
 {"s":0,"e":THUMB,"kind":"thumb","note":"Thumbnail 1 s: hook SPM ESOK? JANGAN GABRA!"},
 {"s":0,"e":DUR,"kind":"watermark","note":"asteredu11.com.my sepanjang video, putih 66% + bayang halus, atas-kiri 14%"},
 {"s":C0,"e":src(10.0),"kind":"topbox","note":"Kotak atas: CALON SPM 2026 / SPM 2026 · CIKGU ALFARHAN"},
 {"s":C0+0.2,"e":C0+3.2,"kind":"label","note":"Label Cikgu AlFarhan + wajah bulatan emas"},
 {"s":at("esok"),"e":src(4.9),"kind":"sticker","text":"BERMULA ESOK!","tone":"red","note":"Pelekat merah BERMULA ESOK!"},
 {"s":at("ketenangan"),"e":src(8.5),"kind":"pill","text":"KETENANGAN JIWA","note":"Pil hati: ketenangan jiwa"},
 {"s":at("Jangan"),"e":src(15.45),"kind":"note","title":"INGAT!","lines":[["Jangan gabra",at("Jangan")],["Jangan takut",at("jangan",2)],["Tenang je lah",at("tenang")]],"note":"Nota tulisan tangan: Jangan gabra / Jangan takut / Tenang je lah"},
 {"s":at("Pastikan"),"e":src(28.0),"kind":"check","note":"Senarai semak strategi jawab (item muncul & ditanda ikut sebutan)"},
 {"s":src(28.0),"e":src(31.95),"kind":"follow","note":"CTA tengah: kad TikTok @aster.edu_tpg + Follow → Followed"},
 {"s":src(32.05),"e":at("Jawab",2)-0.05,"kind":"check","note":"Senarai semak kembali: item 3 Jangan tinggal kosong"},
 {"s":at("Jawab",2),"e":min(at("Jawab",2)+3.0,at("jawab",3,"e")+0.1),"kind":"paper","note":"Sisipan penuh: kertas jawapan diisi (≤3 s, suara berjalan)"},
 {"s":at("biarkan")-0.1,"e":src(45.3),"kind":"stamp","text":"JANGAN BIAR KOSONG!","note":"Cop merah JANGAN BIAR KOSONG!"},
 {"s":at("Good"),"e":src(48.3),"kind":"goodluck","note":"GOOD LUCK! + SUKSES SELALU dengan bintang"},
 {"s":at("kejayaan"),"e":src(51.6),"kind":"pill","text":"KEJAYAAN MENUJU KAMU","icon":"star","note":"Pil bintang: kejayaan menuju kamu"},
 {"s":src(51.7),"e":C1,"kind":"topbox","note":"Kotak atas kembali"},
 {"s":C1,"e":DUR,"kind":"endcard","note":"End card: wajah bulatan emas, Cikgu AlFarhan, logo TikTok + @aster.edu_tpg, CTA follow, asteredu11.com.my"},
]
# the top box also fills the gap between the paper insert and the stamp
G.insert(-2,{"s":G[10]["e"],"e":G[11]["s"],"kind":"topbox","note":"Kotak atas"})
CHECK=[ # item text, appear, tick, re-highlight times
 {"text":"Jawab soalan senang dulu","in":at("jawab"),"tick":at("dulu",1,"e"),"hl":[at("tackle",2)]},
 {"text":"Soalan susah kemudian","in":at("bagi"),"tick":at("susah",1,"e"),"hl":[at("kemudian",2)]},
 {"text":"Jangan tinggal kosong","in":at("tinggalkan"),"tick":at("kosong",1,"e"),"hl":[]},
]
FOLLOW_TAP=src(29.4)
PAPER_LINES=[round(at("Jawab",2)+d,3) for d in (0.15,0.9,1.65)]
SFX=[(0.0,"impact",0.5),(0.95,"whoosh",0.5),(C0+0.2,"pop",0.45),(at("esok"),"pop",0.55),(at("ketenangan"),"pop",0.45),
 (at("Jangan"),"whoosh",0.4)]+[(l[1],"click",0.45) for l in G[6]["lines"]]+[(at("Pastikan"),"whoosh",0.45)]
for c in CHECK: SFX+=[(c["in"],"pop",0.4),(c["tick"],"ding",0.4)]
SFX+=[(src(28.0),"whoosh",0.45),(src(28.1),"pop",0.45),(FOLLOW_TAP,"click",0.6),(src(32.05),"whoosh",0.4),
 (G[10]["s"]-0.05,"whoosh",0.5)]+[(t,"tick",0.4) for t in PAPER_LINES]+[(G[10]["e"]-0.05,"whoosh",0.4),
 (G[11]["s"],"impact",0.5),(at("Good")-0.25,"riser",0.3),(at("Good"),"ding",0.5),(at("sukses"),"pop",0.4),(at("kejayaan"),"ding",0.4),
 (C1-0.05,"whoosh",0.5),(C1+0.25,"ding",0.4)]
SFX=sorted([{"t":round(t,3),"name":n,"gain":g} for t,n,g in SFX],key=lambda x:x["t"])
# punch-in: alternate 100% / 113% every 2-3 cuts (groups 2,3,2,3...)
Z=[];gi=0;left=2;zoom=False
for i,sg in enumerate(edl["segments"]):
    Z.append(1.13 if zoom else 1.0);left-=1
    if left==0: zoom=not zoom;gi+=1;left=2 if gi%2==0 else 3
json.dump({"duration":DUR,"thumb":THUMB,"end":END,"content":CONTENT,"segments":edl["segments"],"zoom":Z,"captions":chunks,"graphics":G,
  "check":CHECK,"follow_tap":FOLLOW_TAP,"paper_lines":PAPER_LINES,"sfx":SFX},open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print("dur",DUR,"chunks",len(chunks),"sfx",len(SFX))
for g in G: print(f'{g["s"]:6.2f}-{g["e"]:6.2f} {g["kind"]:9s} {g["note"]}')
