# usage: checkcuts.py audio16k.wav edl.json  -> transcribes the first/last ~1.6s of every kept piece so clipped or leaked words show up
import json,sys,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
wf=wave.open(sys.argv[1]);sr=wf.getframerate();a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
E=json.load(open(sys.argv[2]))
def tx(s,e):
    x=np.concatenate([np.zeros(int(sr*.3),np.float32),a[int(s*sr):int(e*sr)],np.zeros(int(sr*.3),np.float32)])
    segs,_=m.transcribe(x,language="ms",beam_size=5,vad_filter=False,condition_on_previous_text=False)
    return " ".join(s.text.strip() for s in segs)
for s in E["segments"]:
    a0,b0=s["src_in"],s["src_out"]
    print(f'{s["id"]:>4} START {a0:7.2f}: {tx(a0,min(b0,a0+1.6))!r}  |  END {b0:7.2f}: {tx(max(a0,b0-1.6),b0)!r}',flush=True)
