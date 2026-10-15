# usage: edl2.py transcript.json keep.json audio16k.wav out_edl.json
# keep.json: {"segments":[[id,src_in,src_out],...],"fix":{"word":"Fixed","word@12.34":"Fixed"},"tail":seconds_of_freeze,
#             "bounds":{"id":[src_in_override,src_out_override]}}
# Whisper word ends run early (up to ~0.3s), so each boundary is moved out to real silence:
#  end   -> first run of >=50ms below the speech threshold after the word end (searched up to 0.7s), +40ms tail
#  start -> last run of >=50ms below the threshold before the word start (searched up to 0.4s), -30ms lead
# "bounds" pins a boundary by hand when the automatic one is wrong (null keeps the automatic one).
import json,sys,wave,numpy as np
t,keep,wav,out=sys.argv[1:5]
T=json.load(open(t));K=json.load(open(keep))
wf=wave.open(wav);sr=wf.getframerate();a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(float)/32768
hop=int(sr*.01);DB=20*np.log10(np.array([np.sqrt(np.mean(a[i:i+hop]**2))+1e-9 for i in range(0,len(a)-hop,hop)]))
THR=np.percentile(DB,10)+10   # ~10 dB above the room-noise floor
RUN=5
def quiet_after(x,limit=.7):
    i0=int(x*100)
    for i in range(i0,min(len(DB)-RUN,i0+int(limit*100))):
        if (DB[i:i+RUN]<THR).all(): return i/100+.04
    j=i0+int(np.argmin(DB[i0:i0+int(.5*100)]));return j/100      # no silence: deepest dip
def quiet_before(x,limit=.4):
    i0=int(x*100)
    for i in range(i0,max(RUN,i0-int(limit*100)),-1):
        if (DB[i-RUN:i]<THR).all(): return max(0,i/100-.03)
    j=i0-int(.3*100)+int(np.argmin(DB[i0-int(.3*100):i0]));return j/100
SEG=[]
B=K.get("bounds",{})
for sid,s,e in K["segments"]:
    ns,ne=quiet_before(s),quiet_after(e)
    if sid in B:
        if B[sid][0] is not None: ns=B[sid][0]
        if B[sid][1] is not None: ne=B[sid][1]
    SEG.append((sid,round(ns,2),round(ne,2)))
for i in range(1,len(SEG)):   # never overlap the previous kept piece
    if SEG[i][1]<SEG[i-1][2] and SEG[i][1]>SEG[i-1][1]: SEG[i]=(SEG[i][0],SEG[i-1][2],SEG[i][2])
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
print(f"{len(SEG)} segments, speech {dur:.2f}s + tail {K.get('tail',0)}s  (threshold {THR:.1f} dB)")
for (sid,s,e),(_,s0,e0) in zip(SEG,K["segments"]): print(f"  {sid:>4} {s0:7.2f}->{s:7.2f}  {e0:7.2f}->{e:7.2f}")
