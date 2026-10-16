# Build the edit plan (output timeline) for CFik018: captions, B-roll, motion graphics, SFX, zoom, music, end card.
# usage: plan.py cut.json edl.json out.json [edl_v1.json]
# INTRO: the cover (thumbnail A) is held for INTRO seconds before the talking head; every time is shifted by it at the end.
# Hand-placed times below are written on the v1 timeline (preview 1); with edl_v1.json they are remapped through
# source time onto the current EDL, so they follow later trims. A time inside removed footage snaps to the next kept moment.
import json,re,sys
words=[w for s in json.load(open(sys.argv[1])) for w in s["words"]]
edl=json.load(open(sys.argv[2]));SPEECH=edl["duration"]
V1J=json.load(open(sys.argv[4])) if len(sys.argv)>4 else None
V1=V1J["parts"] if V1J else None
V1END=V1J["duration"] if V1J else SPEECH
def R(t):
    if V1 is None: return t
    if t>=V1END-1e-6: return round(SPEECH+(t-V1END),2)
    src=None
    for p in V1:
        d=p["out"]-p["in"]
        if p["t"]-1e-6<=t<=p["t"]+d+1e-6: src=p["in"]+(t-p["t"]);break
    if src is None: src=V1[-1]["out"]
    best=None
    for p in edl["parts"]:
        if p["in"]-1e-6<=src<=p["out"]+1e-6: return round(p["t"]+src-p["in"],2)
        if p["in"]>src and (best is None or p["in"]<best["in"]): best=p
    return round(best["t"],2) if best else round(SPEECH,2)
FIX={"Pita":"Peti","Itu":None,"masalahnya,":"Masalahnya,"}
W=[]
for w in words:
    t=w["w"].strip()
    if t in FIX:
        if FIX[t] is None: continue
        t=FIX[t]
    if t.startswith("-") and W: W[-1]["w"]+=t;W[-1]["e"]=w["e"];continue
    W.append({"w":t,"s":round(w["s"],2),"e":round(w["e"],2)})
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.4:
        end=nxt["s"] if nxt and nxt["s"]-w["e"]<0.4 else w["e"]+0.15
        chunks.append({"s":cur[0]["s"],"e":round(end,2),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"]} for x in cur]});cur=[]
HOT={"rugi","berbelas","ribu","Pinterest","15","kaki","9","je","muat","sempit","berlaga-laga","3D","ukuran","sebenar","detect","dinding","susah","mahal","beribu","hilang","follow","share"}
for c in chunks:
    for x in c["words"]:
        if re.sub(r"[^\w-]","",x["w"]) in HOT: x["hot"]=1
END=round(V1END,2);DUR=round(END+4.0,2)  # v1 timeline; remapped below
# B-roll. src = "mixkit" (Mixkit Stock Video Free License) or "fik" (Fi-K Studio's own project photo, CFik017 folder).
# x = horizontal crop centre (0..1) for a 9:16 window; portrait sources ignore it.
B=[
 {"s":2.67,"e":4.55,"id":"41178","src":"mixkit","t":5,"x":0.55,"d":"Scroll gambar inspirasi rumah di tablet","why":"'satu gambar dekat Pinterest'"},
 {"s":7.80,"e":10.70,"id":"41184","src":"mixkit","t":3,"x":0.5,"d":"Klien simpan gambar dapur idaman","why":"'nak buat macam dia jumpa dekat Pinterest'"},
 {"s":12.30,"e":15.10,"id":"43033","src":"mixkit","t":2,"x":0.50,"d":"Dapur moden yang luas","why":"'dapur dekat gambar Pinterest tu 15 kaki'"},
 {"s":15.10,"e":17.30,"id":"wetkitchen","src":"fik","file":"[Before] Wet Kitchen Before.jpg","x":0.42,"d":"Dapur sebenar rumah klien (sebelum reno)","why":"'rumah korang tu 9 kaki je'"},
 {"s":24.45,"e":26.25,"id":"29982","src":"mixkit","t":3,"x":0.58,"d":"Pereka bekerja dengan model 3D","why":"'bila kami lukis ikut 3D'"},
 {"s":26.25,"e":28.05,"id":"23392","src":"mixkit","t":3,"x":0.45,"d":"Ukur ruang sebenar","why":"'ukuran sebenar rumah korang'"},
 {"s":31.15,"e":32.70,"id":"39692","src":"mixkit","t":2,"x":0.5,"d":"Gerudi papan kabinet","why":"'sebelum papan tu mula melekat…'"},
 {"s":32.70,"e":34.30,"id":"39684","src":"mixkit","t":2,"x":0.45,"d":"Tukang pasang papan","why":"'…dekat dinding'"},
]
G=[
 {"s":0.00,"e":4.55,"kind":"hook","text":["RUGI BERIBU","SEBAB 1 GAMBAR"],"sub":"dari Pinterest","note":"Tajuk hook: kerugian + Pinterest, terus di saat pertama"},
 {"s":1.75,"e":4.55,"kind":"loss","text":"−RM10,000+","note":"Angka rugi 'berbelas ribu' dicop merah"},
 {"s":8.70,"e":10.70,"kind":"pin","text":"Dapur idaman","sub":"Disimpan dari Pinterest","note":"Kad 'gambar disimpan' (reka sendiri, tiada logo Pinterest)"},
 {"s":12.35,"e":15.10,"kind":"dim","text":"15 kaki","tone":"ok","note":"Garis ukuran 15 kaki di atas dapur dalam gambar"},
 {"s":15.13,"e":17.30,"kind":"dim","text":"9 kaki je","tone":"bad","note":"Garis ukuran 9 kaki (merah) di atas dapur sebenar"},
 {"s":17.45,"e":22.45,"kind":"plan","items":[["Peti ais tak muat",18.17],["Laluan sempit",19.53],["Pintu kabinet berlaga",21.55]],"note":"Pelan atas dapur 9 kaki: peti ais terkeluar, laluan mengecil, pintu bertembung"},
 {"s":28.10,"e":31.10,"kind":"detect","text":"Masalah dikesan awal","sub":"sebelum mula renovate","note":"Lencana: masalah dijumpa dalam 3D"},
 {"s":34.43,"e":41.30,"kind":"compare","a":["Ubah dalam 3D","Tak susah, tak mahal"],"b":["Ubah masa renovasi","Beribu hilang"],"tb":37.57,"note":"Banding kos: ubah dalam 3D vs ubah masa renovasi"},
 {"s":41.45,"e":END,"kind":"follow","times":[41.52,42.48],"note":"Butang Follow + Share muncul ikut suara"},
 {"s":END,"e":DUR,"kind":"endcard","note":"End card Fi-K Studio (logo putih atas hijau jenama)",
  "line1":"Rancang dalam 3D dulu.","line2":"Baru renovate.","cta":"Follow Fi-K Studio untuk tips reno"},
]
SFX=[(0.00,"impact",0.75),(0.02,"whoosh",0.5),(1.75,"swoosh_down",0.6),(2.21,"bonk",0.45),(2.67,"whoosh",0.4),(4.55,"whoosh",0.35),
 (7.80,"whoosh",0.4),(8.72,"pop",0.55),(12.30,"whoosh",0.45),(12.40,"riser",0.3),(14.40,"ding",0.5),(15.10,"impact",0.55),(16.30,"bonk",0.5),
 (17.47,"pop",0.5),(18.17,"tick",0.6),(19.53,"tick",0.6),(21.55,"bonk",0.55),(24.45,"whoosh",0.4),(26.25,"whoosh",0.35),(28.12,"ding",0.6),
 (31.15,"whoosh",0.35),(34.45,"pop",0.55),(36.40,"ding",0.5),(37.60,"whoosh",0.45),(39.55,"swoosh_down",0.6),(40.10,"bonk",0.45),
 (41.50,"click",0.7),(42.48,"pop",0.6),(END,"whoosh",0.6),(END+0.6,"ding",0.45)]
SFX=[{"t":round(t,2),"name":n,"gain":g} for t,n,g in SFX]
Z=[(0,1.12,40),(2.60,1.12,40),(4.70,1.0,40),(10.85,1.0,40),(10.90,1.08,38),(12.30,1.08,38),(17.45,1.0,40),(22.41,1.0,40),(22.45,1.06,38),
   (24.45,1.06,38),(28.05,1.0,40),(28.10,1.10,38),(31.15,1.10,38),(34.43,1.0,40),(39.50,1.0,40),(39.55,1.16,38),(41.30,1.16,38),(41.45,1.04,40),(END,1.04,40)]
Z=[{"t":round(t,2),"scale":s,"oy":o} for t,s,o in Z]
for b in B: b["s"],b["e"]=R(b["s"]),R(b["e"])
for g in G:
    g["s"],g["e"]=R(g["s"]),R(g["e"])
    if "items" in g: g["items"]=[[x,R(t)] for x,t in g["items"]]
    if "tb" in g: g["tb"]=R(g["tb"])
    if "times" in g: g["times"]=[R(t) for t in g["times"]]
SFX=[dict(x,t=R(x["t"])) for x in SFX]
Z=[dict(z,t=R(z["t"])) for z in Z]
DUR,END=R(DUR),round(SPEECH,2)
INTRO=1.0
SH=lambda t:round(t+INTRO,2)
for c in chunks:
    c["s"],c["e"]=SH(c["s"]),SH(c["e"])
    for x in c["words"]: x["s"]=SH(x["s"])
for b in B: b["s"],b["e"]=SH(b["s"]),SH(b["e"])
for g in G:
    g["s"],g["e"]=SH(g["s"]),SH(g["e"])
    if "items" in g: g["items"]=[[x,SH(t)] for x,t in g["items"]]
    if "tb" in g: g["tb"]=SH(g["tb"])
    if "times" in g: g["times"]=[SH(t) for t in g["times"]]
SFX=[dict(x,t=SH(x["t"])) for x in SFX]+[{"t":0.0,"name":"pop","gain":0.6},{"t":0.72,"name":"whoosh","gain":0.55}]
SFX.sort(key=lambda x:x["t"])
Z=[{"t":0.0,"scale":1.12,"oy":40}]+[dict(z,t=SH(z["t"])) for z in Z]
DUR,END=SH(DUR),SH(END)
json.dump({"duration":DUR,"speech_end":END,"intro":{"s":0.0,"e":INTRO,"file":"cover.png"},"parts":edl["parts"],"segments":edl["segments"],"captions":chunks,"broll":B,"graphics":G,"sfx":SFX,"zoom":Z,
  "logo":"logo-white.png","music":{"file":"music.mp3","id":282,"offset":9,"note":"Lo-fi beat santai, Mixkit Stock Music Free License"}},open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"caption chunks; duration",DUR)
