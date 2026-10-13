import json,sys
SEG=[("hook",51.24,54.17),("A",0.00,20.83),("B",20.97,30.79),("C",30.93,47.80),("D",47.99,51.24),("E",54.28,57.45),("F",57.66,62.276)]
def out_off(i): return sum(e-s for _,s,e in SEG[:i])
def place(mid):
    for i,(_,s,e) in enumerate(SEG):
        if s<=mid<e: return i
    # word straddles a removed gap: give it to the segment that starts right after
    c=[(s-mid,i) for i,(_,s,_) in enumerate(SEG) if 0<s-mid<0.35]
    return min(c)[1] if c else None
if __name__=="__main__":
    t=json.load(open(sys.argv[1]))
    words=[w for s in t for w in s["words"] if w["s"]<59.15]  # drop whisper tail repeat
    out=[]
    for w in words:
        i=place((w["s"]+w["e"])/2)
        if i is None: continue
        _,s,e=SEG[i];o=out_off(i)
        out.append({"w":w["w"].strip(),"seg":SEG[i][0],"s":round(o+max(w["s"],s)-s,3),"e":round(o+min(w["e"],e)-s,3)})
    out.sort(key=lambda x:x["s"])
    json.dump({"segments":[{"id":n,"src_in":s,"src_out":e,"out_in":round(out_off(i),3)} for i,(n,s,e) in enumerate(SEG)],"duration":round(out_off(len(SEG)),3),"words":out},open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
