import json,re,sys
t=json.load(open(sys.argv[1]))
FIX={"Kafar":"KAFA","Ruga":"Tugas","telikan":"tally-kan","jais":"JAIS"}
W=[]
for s in t:
    for w in s["words"]:
        x=w["w"].strip()
        if x.startswith("-") and W: W[-1]["w"]+=x;W[-1]["e"]=w["e"];continue
        core=re.sub(r"[.,]$","",x);x=x.replace(core,FIX.get(core,core))
        W.append({"w":x,"s":round(w["s"],2),"e":round(w["e"],2),"flag":core in FIX})
HOT={"KAFA","akaun","agama","yuran","SUWA","Tunai","baki","report","JAIS","tersusun","fokus","pengajaran","Follow","sistematik"}
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nx=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,]$",w["w"]) or not nx or nx["s"]-w["e"]>0.4:
        chunks.append({"s":cur[0]["s"],"e":round(nx["s"] if nx and nx["s"]-w["e"]<0.4 else w["e"]+0.2,2),
          "w":[{"t":re.sub(r"[.,]$","",x["w"]),"s":x["s"],"hot":int(re.sub(r"[.,]$","",x["w"]) in HOT)} for x in cur]});cur=[]
sent=[];cur=[]
for w in W:
    cur.append(w)
    if w["w"].endswith("."):sent.append({"s":cur[0]["s"],"words":[{"t":x["w"],"flag":x["flag"]} for x in cur]});cur=[]
if cur:sent.append({"s":cur[0]["s"],"words":[{"t":x["w"],"flag":x["flag"]} for x in cur]})
json.dump({"caps":chunks,"sent":sent},open(sys.argv[2],"w"),ensure_ascii=False)
print(len(chunks),"chunks");[print(s["s"]," ".join(w["t"] for w in s["words"])) for s in sent]
