# usage: transcribe.py in.wav out.json  (Whisper large-v3, Malay, word timestamps)
import json,sys,wave
import numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
wf=wave.open(sys.argv[1]);a=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs,info=m.transcribe(a,language="ms",word_timestamps=True,beam_size=5,condition_on_previous_text=False,
    vad_filter=True,vad_parameters={"min_silence_duration_ms":300,"speech_pad_ms":150},
    initial_prompt="Interior design, renovation, Pinterest, dapur, kabinet, 3D, Fi-K Studio.")
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}",flush=True)
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
