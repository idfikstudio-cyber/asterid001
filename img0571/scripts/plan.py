# Edit plan for IMG_0571 on the OUTPUT timeline: captions, motion graphics, sfx, zoom.
# usage: plan.py edl.json plan.json
import json,re,sys
d=json.load(open(sys.argv[1]))
SEGS={s["id"]:s for s in d["segments"]};END=d["end_card"]
W=d["words"]
def at(seg,txt,n=0):
    """output time of the n-th word in segment `seg` whose text starts with `txt`"""
    m=[w for w in W if w["seg"]==seg and re.sub(r"\W","",w["w"]).lower().startswith(txt.lower())]
    return m[n]["s"]
def seg_in(i): return SEGS[i]["out_in"]
def seg_out(i): return round(SEGS[i]["out_in"]+SEGS[i]["src_out"]-SEGS[i]["src_in"],3)

# ---- captions: <=3 words, break on punctuation / segment change ----
EMPH={"fokus","gangguan","sejam","3","jam","handphone","scroll-scroll","otak","merewang","telefon","ganggu","komen","tuisyen","online","10","17","bebel","ceramah","bernilai","semua","percaya"}
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if re.fullmatch(r"\d+",w["w"]) and nxt and nxt["seg"]==w["seg"]: continue  # keep "5 minit" together
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["seg"]!=w["seg"] or nxt["s"]-w["e"]>0.45:
        end=nxt["s"] if nxt and nxt["seg"]==w["seg"] and nxt["s"]-w["e"]<0.45 else w["e"]+0.12
        chunks.append({"s":cur[0]["s"],"e":round(end,3),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"],**({"hot":1} if re.sub(r"[^\w-]","",x["w"]).lower() in EMPH else {})} for x in cur]});cur=[]
for a,b in zip(chunks,chunks[1:]): a["e"]=min(a["e"],b["s"])
# the hook line is shown as the big title instead
chunks=[c for c in chunks if c["s"]>=seg_in("S")-0.01]

# ---- motion graphics ----
S0=seg_in("S");FULL_END=round(at("S","lebih")-0.02,3)
G=[
 {"s":0.0,"e":END["out_in"],"kind":"brand","note":"Logo teks Aster Edu kecil di penjuru, sepanjang video (bina kepercayaan)"},
 {"s":0.0,"e":S0,"kind":"hook","text":["PERCAYA","ATAU TIDAK?"],"note":"Hook: tajuk besar, terus ke soalan"},
 {"s":S0,"e":FULL_END,"kind":"compare-full","note":"B-roll grafik skrin penuh: 1 jam fokus. Juga menutup saat penyampai menoleh ke tepi"},
 {"s":FULL_END,"e":seg_out("S"),"kind":"compare","reveal":round(at("S","3")-FULL_END,2),"notif":round(at("S","handphone")-FULL_END,2),"timer":round(at("S","setiap")-FULL_END,2),"note":"Kad banding: 1 jam fokus vs 3 jam + scroll handphone setiap 5 minit"},
 {"s":seg_in("I")+0.05,"e":seg_out("I"),"kind":"name","name":"Al-Farhan","role":"Pengasas Aster Edu","chip":"Tuisyen online · umur 10–17 tahun","chipAt":round(at("I","10")-seg_in("I")-0.05,2),"note":"Lower-third: nama, jawatan, julat umur"},
 {"s":round(at("F","sejam")-0.05,3),"e":seg_out("F"),"kind":"equation","a":"1 JAM","b":"FOKUS","bAt":round(at("F","fokus")-at("F","sejam")+0.05,2),"note":"Kata kunci: 1 jam + fokus = ✓"},
 {"s":round(at("O","fokus")-0.05,3),"e":seg_out("O"),"kind":"checklist","rows":[["ok","Fokus"],["no","Masa yang panjang"]],"rowAt":[0,round(at("O","masa")-at("O","fokus"),2)],"note":"Otak perlukan fokus, bukan masa panjang"},
 {"s":round(at("R","panjang")-0.1,3),"e":seg_out("R"),"kind":"meter","text":"Tahap fokus","drainAt":0.15,"redAt":round(at("R","merewang")-at("R","panjang")+0.1,2),"note":"Meter fokus menurun bila belajar terlalu lama"},
 {"s":round(seg_in("V")+0.05,3),"e":seg_out("V"),"kind":"player","bubbles":[["bebel…",round(at("V","bebel")-seg_in("V")-0.05,2)],["ceramah…",round(at("V","ceramah")-seg_in("V")-0.05,2)]],"note":"Analogi: video panjang = orang kata bebel, ceramah"},
 {"s":round(at("T","telefon")-0.1,3),"e":seg_out("T"),"kind":"phone","chips":[["📚","Masa belajar",round(at("T","masa",0)-at("T","telefon")+0.1,2)],["😴","Masa tidur",round(at("T","masa",1)-at("T","telefon")+0.1,2)],["🍽️","Masa makan",round(at("T","masa",2)-at("T","telefon")+0.1,2)]],"allAt":round(at("T","semua")-at("T","telefon")+0.1,2),"note":"Telefon ganggu: belajar, tidur, makan"},
 {"s":round(at("K","cuba")-0.1,3),"e":END["out_in"],"kind":"comment","text":"Setuju? Komen di bawah","note":"Ajak komen (penyampai sendiri sebut 'Cuba komen')"},
 {"s":END["out_in"],"e":d["duration"],"kind":"endcard","note":"Kad CTA: DM untuk info pakej (tiada harga, tiada nombor telefon)"},
]
# ---- real B-roll (Mixkit Free License: commercial use, no attribution). cx = crop centre (0-1) of the 16:9 clip ----
BROLL=[
 {"s":round(at("S","jam",0)-0.02,3),"e":round(at("S","setiap")-0.02,3),"clip":"4908","src":2.5,"cx":0.76,"title":"Tangan scroll telefon sebelah laptop & buku nota","url":"https://mixkit.co/free-stock-video/person-working-while-scrolling-on-social-networks-4908/"},
 {"s":round(at("F","anak")-0.02,3),"e":round(at("F","itu")-0.02,3),"clip":"4761","src":1.0,"cx":0.42,"title":"Pelajar fokus menulis","url":"https://mixkit.co/free-stock-video/concentrated-boy-studying-at-home-4761/"},
 {"s":round(at("R","otak")-0.02,3),"e":seg_out("R"),"clip":"28321","src":4.6,"cx":0.33,"title":"Pelajar kusut pegang kepala","url":"https://mixkit.co/free-stock-video/frustrated-student-at-his-school-studying-his-notes-28321/"},
 {"s":round(at("T","masa",0)-0.02,3),"e":round(at("T","masa",1)-0.02,3),"clip":"4908","src":7.6,"cx":0.6,"title":"Telefon masa belajar","url":"https://mixkit.co/free-stock-video/person-working-while-scrolling-on-social-networks-4908/"},
 {"s":round(at("T","masa",1)-0.02,3),"e":round(at("T","masa",2)-0.02,3),"clip":"39789","src":4.0,"cx":0.7,"title":"Telefon masa tidur","url":"https://mixkit.co/free-stock-video/girl-lying-down-chatting-on-her-cell-phone-before-sleeping-39789/"},
 {"s":round(at("T","masa",2)-0.02,3),"e":round(at("T","semua")-0.02,3),"clip":"4857","src":8.0,"cx":0.6,"title":"Telefon masa makan","url":"https://mixkit.co/free-stock-video/couple-having-breakfast-cereal-and-see-their-cell-phones-4857/"},
 {"s":END["out_in"],"e":d["duration"],"clip":"50127","src":1.0,"cx":0.47,"blur":1,"title":"Latar kad akhir: pelajar membaca di rumah","url":"https://mixkit.co/free-stock-video/a-young-student-reads-information-from-a-book-at-home-50127/"},
]
# ---- sfx (kept minimal and quiet) ----
SFX=[(0.02,"soft",0.35),(S0-0.06,"whoosh",0.35),(at("S","handphone"),"notif",0.45),(seg_in("I")+0.08,"pop",0.3),
     (at("F","fokus"),"ding",0.22),(at("T","telefon"),"notif",0.4),(at("K","cuba"),"pop",0.32),(END["out_in"],"soft",0.4)]
SFX=[{"t":round(t,3),"name":n,"gain":g} for t,n,g in SFX]
# ---- zoom keyframes (time, scale) – hard changes at cuts hide jump cuts, eased punch-ins on emphasis ----
Z=[]
def hold(t0,t1,s): Z.extend([(t0,s),(t1-0.001,s)])
def punch(t0,t1,s0,s1,at_,ramp=0.22): Z.extend([(t0,s0),(at_,s0),(at_+ramp,s1),(t1-0.001,s1)])
hold(0,seg_out("P"),1.28)
punch(seg_in("S"),seg_out("S"),1.06,1.16,at("S","handphone")-0.05)
hold(seg_in("I"),seg_out("I"),1.14)
punch(seg_in("F"),seg_out("F"),1.0,1.16,at("F","fokus")-0.1)
hold(seg_in("O"),seg_out("O"),1.14)
Z.extend([(seg_in("R"),1.0),(seg_out("R")-0.001,1.08)])  # slow creep: tension
hold(seg_in("V"),seg_out("V"),1.12)
punch(seg_in("T"),seg_out("T"),1.0,1.18,at("T","semua")-0.08)
hold(seg_in("K"),seg_out("K"),1.26)
Z.append((END["out_in"],1.0))
Z=[{"t":round(t,3),"scale":s} for t,s in Z]
json.dump({"duration":d["duration"],"cuts":[{"out":s["out_in"],"src_in":s["src_in"],"src_out":s["src_out"],"id":s["id"],"note":s["note"]} for s in d["segments"]],
           "end_card":END["out_in"],"origin":{"x":46,"y":40},"captions":chunks,"graphics":G,"broll":BROLL,"sfx":SFX,"zoom":Z},open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"caption chunks;",len(G),"graphics;",len(SFX),"sfx")
for g in G: print(f'{g["s"]:6.2f}-{g["e"]:6.2f} {g["kind"]}')
