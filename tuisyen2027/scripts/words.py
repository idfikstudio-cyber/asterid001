# Petakan masa perkataan (sumber) ke garis masa selepas potong.
import json,sys
SEGS=[(0.00,1.56),(1.78,3.98),(8.52,11.30),(11.62,16.10),(16.38,17.92)]
FIX={"tuition":"tuisyen","BMBI,":"BM, BI,"}
out=[];off=0
words=[w for s in json.load(open(sys.argv[1])) for w in s["words"]]
for a,b in SEGS:
    for w in words:
        m=(w["s"]+w["e"])/2
        if a<=m<b or 0<a-m<0.35: out.append({"w":FIX.get(w["w"].strip(),w["w"].strip()),"s":round(off+max(w["s"],a)-a,3),"e":round(off+min(w["e"],b)-a,3)})
    off+=b-a
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
print(" ".join(f"{w['w']}@{w['s']}" for w in out))
