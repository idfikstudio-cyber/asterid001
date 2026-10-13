# Build preview/plan.json: captions, motion graphics, SFX and zoom on the OUTPUT timeline (seconds).
import json,re,sys
tr=json.load(open(sys.argv[1]));edl=json.load(open(sys.argv[2]))
FIX={"PK":"Fikir","VK":"Fikir","inter-design":"interior design","inter":"interior","-design,":"design,","-design":"design","Session":"suggestion","Desain":"design"}
W=[]
for s in tr:
    for w in s["words"]:
        t=w["w"].strip();t=FIX.get(t,t)
        W.append({"w":re.sub(r"^studio","Studio",t),"s":w["s"],"e":w["e"]})
    W[-1]["brk"]=1  # whisper segment end = sentence/phrase end
for w in W:  # sentence-case from whisper segment starts
    if w["w"] in ("Dan","Boleh","Kita","Untuk","Macam","Sebelum","Design") and w["s"]>26: w["w"]=w["w"].lower()
W[0]["w"]="Klien"
# caption chunks: <=3 words, break on punctuation or >0.4s gap
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or w.get("brk") or not nxt or nxt["s"]-w["e"]>0.4:
        end=nxt["s"] if nxt and nxt["s"]-w["e"]<0.4 else w["e"]+0.2
        chunks.append({"s":cur[0]["s"],"e":end,"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"]} for x in cur]});cur=[]
HOT={"design","renovation","kontraktor","Fikir","studio","layout","3D","drawing","DM","visual","terbaik","cantikkan","A","Z","sendiri","susah"}
for c in chunks:
    for x in c["words"]:
        if x["w"] in HOT or x["w"].lower() in HOT: x["hot"]=1
G=[
 {"s":0.00,"e":3.88,"kind":"hook","text":["DAH TAHU","RUMAH IMPIAN,","TAPI SUSAH NAK","TERANG KAT KONTRAKTOR?"],"note":"Hook: masalah klien (dipindah dari minit 0:37 video asal)"},
 {"s":1.95,"e":3.88,"kind":"confused","note":"Ikon kontraktor keliru (???) masa sebut 'kontraktor'"},
 {"s":4.00,"e":8.70,"kind":"atoz","text":"Design → Renovation","note":"Bar A sampai Z, isi ikut ucapan"},
 {"s":8.80,"e":13.80,"kind":"split","a":"Design","b":"Renovation","note":"Dua kad: Design (kami) | Renovation (kontraktor sendiri)"},
 {"s":14.01,"e":15.55,"kind":"brand","text":"FIKIR STUDIO","sub":"Design · Layout · 3D","note":"Logo reveal + kilauan cahaya masa sebut 'Fikir Studio'"},
 {"s":15.54,"e":19.29,"kind":"services","items":[["Layout",15.56],["3D",16.18],["Drawing",17.08]],"note":"3 kad servis muncul ikut perkataan"},
 {"s":15.55,"e":19.29,"kind":"broll","label":"B-ROLL: pelan lantai → render 3D","note":"Slot B-roll (PIP). Sementara: animasi pelan lantai melukis diri jadi 3D. Ganti dengan render sebenar Fikir Studio"},
 {"s":19.41,"e":24.79,"kind":"flow","items":[["Design dulu",19.84],["Visual akhir",21.70],["Kontraktor sendiri",23.68]],"note":"Aliran 3 langkah, setiap langkah tick ikut ucapan"},
 {"s":19.41,"e":23.39,"kind":"beforeafter","label":"B-ROLL: before / after","note":"Slot B-roll: lakaran bilik kosong → render siap (wipe). Ganti dengan before/after projek sebenar"},
 {"s":25.00,"e":28.74,"kind":"dm","text":"Hai Fikir Studio! Nak design rumah 🏠","reply":"Boleh! Kami bagi suggestion terbaik ✨","note":"Mockup DM: mesej masuk + balasan"},
 {"s":28.79,"e":34.39,"kind":"handoff","text":"Design siap → kontraktor","note":"Kertas pelan terbang ke topi keselamatan kontraktor"},
 {"s":34.24,"e":35.60,"kind":"cta","text":"DM KAMI SEKARANG","sub":"Konsultasi design rumah","note":"CTA berdenyut"},
]
SFX=[(0.0,"riser",0.3),(0.04,"impact",0.75),(1.95,"bonk",0.45),(3.96,"whoosh",0.7),(6.26,"pop",0.5),(6.92,"pop",0.55),(8.40,"ding",0.4),
 (8.78,"whoosh",0.55),(10.02,"pop",0.5),(11.26,"pop",0.5),(13.30,"riser",0.35),(14.02,"impact",0.8),(14.30,"whoosh",0.5),
 (15.50,"swoosh_down",0.5),(15.58,"pop",0.6),(16.18,"pop",0.6),(17.08,"pop",0.6),(19.42,"whoosh",0.6),(19.84,"click",0.6),(21.70,"click",0.6),
 (23.68,"click",0.6),(25.22,"ding",0.7),(26.34,"pop",0.5),(28.82,"whoosh",0.6),(31.64,"swoosh_down",0.6),(33.04,"chaching",0.5),(34.24,"click",0.8),(34.26,"whoosh",0.5)]
SFX=[{"t":t,"name":n,"gain":g} for t,n,g in SFX]
# zoom: alternate framing at every cut so jump cuts read as intentional camera moves; punch-ins on key lines
Z=[(0,1.16,20),(3.94,1.16,20),(3.98,1.0,40),(8.72,1.0,40),(8.76,1.10,34),(13.95,1.10,34),(14.01,1.0,40),(14.39,1.0,40),(14.43,1.18,28),
   (16.85,1.18,28),(16.89,1.0,40),(19.34,1.0,40),(19.41,1.10,34),(24.97,1.10,34),(25.03,1.0,40),(28.77,1.0,40),(28.83,1.12,32),(32.90,1.15,31),(34.24,1.0,40),(35.6,1.0,40)]
Z=[{"t":t,"scale":s,"oy":o} for t,s,o in Z]
cuts=[{"out":s["out_in"],"src_in":s["src_in"],"src_out":s["src_out"],"id":s["id"],"text":s["text"]} for s in edl["segments"]]
json.dump({"duration":35.55,"cuts":cuts,"captions":chunks,"graphics":G,"sfx":SFX,"zoom":Z},open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"chunks");[print(round(c["s"],2)," ".join(x["w"] for x in c["words"])) for c in chunks]
# source transcript with keep/drop marks for the transcript tab
if len(sys.argv)>4:
    src=json.load(open(sys.argv[4]));segs=edl["segments"];P=json.load(open(sys.argv[3]))
    rows=[]
    for s in src:
        ws=[w for w in s["words"]]
        # whisper stretches a word after a pause back over the pause; its real onset is just before the next word
        mid=[(ws[i+1]["s"]-0.15 if w["e"]-w["s"]>0.6 and i+1<len(ws) else (w["s"]+w["e"])/2) for i,w in enumerate(ws)]
        kept=[any(g["src_in"]-0.1<=m<=g["src_out"]+0.05 for g in segs) for m in mid]
        rows.append({"s":round(s["start"],2),"words":[[w["w"].strip(),int(k)] for w,k in zip(ws,kept)]})
    P["source"]=rows;json.dump(P,open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
