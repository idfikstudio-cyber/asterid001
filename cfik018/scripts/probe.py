# usage: probe.py clip.wav start end [start end ...]  -> transcribe each window separately (no VAD), print words
import sys,wave
import numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
wf=wave.open(sys.argv[1]);a=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768
v=list(map(float,sys.argv[2:]))
for s,e in zip(v[::2],v[1::2]):
    segs,_=m.transcribe(a[int(s*16000):int(e*16000)],language="ms",word_timestamps=True,beam_size=5,condition_on_previous_text=False,vad_filter=False)
    ws=[f"{w.word.strip()}@{s+w.start:.2f}" for sg in segs for w in sg.words]
    print(f"[{s}-{e}]"," ".join(ws),flush=True)
