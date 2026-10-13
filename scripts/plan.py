import json,re,sys
d=json.load(open(sys.argv[1]))
FIX={"charge":"chance","redah":"rendah","RM89,":"RM89"}
# merge reduplication tokens ("anak","-anak") and apply fixes
W=[]
for w in d["words"]:
    txt=FIX.get(w["w"],w["w"])
    if txt.startswith("-") and W: W[-1]["w"]+=txt; W[-1]["e"]=w["e"]; continue
    W.append(dict(w,w=txt))
for w in W:
    if w["w"]=="Kami" and w["s"]>55: w["w"]="kami"
# fix leading "Kami" at 55.76 belongs to "bersama kami"
# caption chunks: <=3 words, break on punctuation or >0.45s gap
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w)
    nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.45:
        chunks.append({"s":cur[0]["s"],"e":(nxt["s"] if nxt and nxt["s"]-w["e"]<0.45 else w["e"]+0.15),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"]} for x in cur]});cur=[]
next(x for c in chunks for x in c["words"] if x["w"]=="exam")["w"]+="?"  # hook is a question
EMPH={"skor","lemah","gila","RM89","gagal","tinggi","Aster","Klik","exam","naik"}
for c in chunks:
    for x in c["words"]:
        if re.sub(r"\W","",x["w"]) in EMPH: x["hot"]=1
# motion graphics / sfx / zoom on OUTPUT timeline (seconds)
G=[
 {"s":0.00,"e":2.85,"kind":"hook","text":["IBU AYAH,","TAK NAK KE","ANAK-ANAK","SKOR?"],"note":"Hook: soalan terus kepada ibu bapa (dipindah dari minit 0:51)"},
 {"s":5.70,"e":8.40,"kind":"chip","pos":"top","text":"Anak lemah subjek?","tone":"warn","note":"Kenal pasti masalah ibu bapa"},
 {"s":8.53,"e":11.95,"kind":"countdown","text":"Exam makin dekat","sub":"Tinggal beberapa bulan","note":"Rasa urgent: masa makin suntuk"},
 {"s":12.19,"e":15.40,"kind":"homework","text":"Kerja rumah bertimbun","note":"Timbunan buku jatuh + pangkah"},
 {"s":15.63,"e":18.20,"kind":"target","text":"Fokus subjek lemah","note":"Gelang fokus"},
 {"s":18.37,"e":20.95,"kind":"stamp","text":"SOALAN GILA","note":"Cop 'Soalan Gila', motif berulang"},
 {"s":21.49,"e":26.10,"kind":"price","text":"4 SUBJEK","price":"RM89","sub":"Pusat Tuisyen Aster","note":"Kad harga: tawaran utama"},
 {"s":26.89,"e":28.40,"kind":"stamp-sm","text":"SOALAN GILA","note":"Ulang motif"},
 {"s":30.60,"e":33.40,"kind":"chart-down","text":"Risiko gagal","note":"Graf menurun"},
 {"s":33.58,"e":37.40,"kind":"badge","text":"Guru berpengalaman","note":"Lencana kepercayaan"},
 {"s":38.55,"e":42.50,"kind":"chart-up","text":"Target markah tinggi","note":"Graf menaik"},
 {"s":44.25,"e":45.90,"kind":"stamp-sm","text":"SOALAN GILA","note":"Ulang motif"},
 {"s":47.65,"e":49.60,"kind":"heart","text":"Kami tak nak anak tuan-tuan gagal","note":"Momen emosi: grade sedikit hangat"},
 {"s":49.69,"e":53.60,"kind":"grade-bar","from":"Rendah","to":"Naik","note":"Bar markah naik"},
 {"s":53.70,"e":58.90,"kind":"cta","text":"Klik link di bawah","sub":"Daftar sebelum exam akhir tahun","note":"CTA berdenyut + anak panah"},
 {"s":55.30,"e":58.90,"kind":"comment","text":"Komen “NAK” untuk info","note":"Ajak komen (engagement TikTok)"},
]
SFX=[(0.06,"impact",0.9),(0.0,"riser",0.35),(2.00,"pop",0.7),(2.90,"whoosh",0.8),(5.80,"pop",0.7),(8.55,"tick",0.6),(12.19,"bonk",0.7),
 (12.60,"pop",0.4),(15.60,"whoosh",0.6),(19.05,"impact",0.75),(21.45,"whoosh",0.7),(22.70,"chaching",0.85),(26.90,"pop",0.5),
 (30.62,"swoosh_down",0.7),(33.65,"ding",0.6),(38.60,"riser",0.35),(40.10,"pop",0.55),(42.70,"impact",0.6),(44.25,"pop",0.5),
 (49.75,"pop",0.5),(51.30,"ding",0.5),(53.70,"click",0.8),(53.72,"whoosh",0.6),(55.35,"pop",0.6),(58.90,"whoosh",0.7)]
SFX=[{"t":t,"name":n,"gain":g} for t,n,g in SFX]
# zoom keyframes (time, scale, originY%) – punch-ins on emphasis, eased in page / render
Z=[(0,1.18,38),(2.85,1.18,38),(2.93,1.0,40),(15.55,1.0,40),(15.63,1.12,36),(18.30,1.12,36),(18.37,1.0,40),(21.45,1.0,40),(21.49,1.08,34),
   (26.00,1.08,34),(26.10,1.0,40),(42.65,1.0,40),(42.71,1.14,36),(44.20,1.14,36),(44.25,1.0,40),(47.65,1.0,40),(49.60,1.10,36),(49.69,1.0,40),
   (53.65,1.0,40),(53.70,1.06,38),(58.90,1.06,38),(58.94,1.0,50)]
Z=[{"t":t,"scale":s,"oy":o} for t,s,o in Z]
cuts=[]
off=0
for sg in d["segments"]:
    cuts.append({"out":sg["out_in"],"src_in":sg["src_in"],"src_out":sg["src_out"],"id":sg["id"]})
json.dump({"duration":d["duration"],"cuts":cuts,"captions":chunks,"graphics":G,"sfx":SFX,"zoom":Z,"outro_at":58.94},open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"caption chunks")
for c in chunks[:6]+chunks[-5:]: print(round(c["s"],2),round(c["e"],2)," ".join(x["w"] for x in c["words"]))
