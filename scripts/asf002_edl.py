# Cut list for AS-F-002: remove silences > 0.3 s (keep 0.1 s padding each side), map words to output timeline.
import json,sys,wave,numpy as np
wav,tr,out=sys.argv[1:4]
w=wave.open(wav);sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768
hop=sr//100;db=20*np.log10(np.sqrt(np.convolve(a**2,np.ones(hop*2)/(hop*2),"same"))[::hop]+1e-9)
dur=len(a)/sr;quiet=db<-40
PAD=0.10;MIN=0.30
segs=[];start=0.0;i=0;n=len(quiet)
while i<n:
    if quiet[i]:
        j=i
        while j<n and quiet[j]: j+=1
        s,e=i/100,j/100
        if e-s>MIN and s>0.05:
            if e>=dur-0.01: segs.append((start,s+PAD));start=None;break
            segs.append((start,s+PAD));start=e-PAD
        i=j
    else: i+=1
if start is not None: segs.append((start,dur))
segs=[(round(s,2),round(e,2)) for s,e in segs if e-s>0.05]
words=[x for s in json.load(open(tr)) for x in s["words"]]
offs=[];o=0
for s,e in segs: offs.append(o);o+=e-s
def m(t):
    for (s,e),of in zip(segs,offs):
        if s<=t<=e: return of+t-s
    for (s,e),of in zip(segs,offs):  # inside a removed gap: snap to next segment start
        if t<s: return of
    return o
W=[{"w":x["w"].strip(),"s":round(m(x["s"]),3),"e":round(m(x["e"]),3),"src":round(x["s"],2)} for x in words]
json.dump({"segments":[{"src_in":s,"src_out":e,"out_in":round(of,3)} for (s,e),of in zip(segs,offs)],"duration":round(o,3),"words":W},open(out,"w"),ensure_ascii=False,indent=1)
print(len(segs),"segments, duration",round(o,2),"from",round(dur,2))
for (s,e),of in zip(segs,offs): print(f"{s:6.2f}-{e:6.2f} -> {of:6.2f}")
