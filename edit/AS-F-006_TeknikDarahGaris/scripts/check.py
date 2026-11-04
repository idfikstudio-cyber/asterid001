import sys,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
for f,p in [("clipA.wav","Kalau 16, yang ni simpan 1. Bawa 1."),("clipB.wav","Ustaz bagitahu kalau plan A tak jadi")]:
  wf=wave.open(f);a=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768
  for temp in (0.0,):
    for prompt in (None,p):
      segs,_=m.transcribe(a,language="ms",beam_size=5,initial_prompt=prompt,temperature=temp)
      print(f,prompt is not None,[s.text for s in segs],flush=True)
  segs,_=m.transcribe(a,language="en",beam_size=5)
  print(f,"en",[s.text for s in segs],flush=True)
