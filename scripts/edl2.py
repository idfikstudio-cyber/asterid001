# usage: edl2.py transcript.json keep.json audio16k.wav out_edl.json
# keep.json: {"segments":[[id,src_in,src_out],...],"fix":{"word":"Fixed"},"tail":seconds_of_freeze}
# Each cut boundary is nudged to the quietest 10ms frame within +-0.12s so no breath/click is left at the join.
import json,sys,wave,numpy as np
t,keep,wav,out=sys.argv[1:5]
T=json.load(open(t));K=json.load(open(keep))
wf=wave.open(wav);sr=wf.getframerate();a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(float)
hop=int(sr*.01);E=np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0,len(a)-hop,hop)])
def quiet(x,lo,hi):
    i0,i1=max(0,int((x-lo)*100)),min(len(E)-1,int((x+hi)*100))
    return (i0+int(np.argmin(E[i0:i1+1])))/100 if i1>i0 else x
SEG=[]
for sid,s,e in K["segments"]:
    SEG.append((sid,round(quiet(s,.12,.04),2),round(quiet(e,.04,.12),2)))
def off(i): return sum(e-s for _,s,e in SEG[:i])
words=[w for s in T for w in s["words"]]
FIX=K.get("fix",{})
W=[]
for w in words:
    m=(w["s"]+w["e"])/2
    for i,(sid,s,e) in enumerate(SEG):
        if s<=m<e:
            o=off(i);txt=w["w"].strip();txt=FIX.get(f'{txt}@{w["s"]:.2f}',FIX.get(txt,txt))
            W.append({"w":txt,"seg":sid,"src":round(w["s"],2),"s":round(o+max(w["s"],s)-s,3),"e":round(o+min(w["e"],e)-s,3)});break
W.sort(key=lambda x:x["s"])
dur=off(len(SEG))
json.dump({"segments":[{"id":sid,"src_in":s,"src_out":e,"out_in":round(off(i),3)} for i,(sid,s,e) in enumerate(SEG)],
           "speech_end":round(dur,3),"tail":K.get("tail",0),"duration":round(dur+K.get("tail",0),3),"words":W},
          open(out,"w"),ensure_ascii=False,indent=1)
print(f"{len(SEG)} segments, speech {dur:.2f}s + tail {K.get('tail',0)}s")
