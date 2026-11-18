"""Audio AS-F-015: suara (EDL) dijernihkan -> -14 LUFS, muzik rasmi Aster + SFX. python3 build_audio.py <work_dir>"""
import subprocess,json,re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import timeline as T
WD=sys.argv[1];HERE=os.path.dirname(os.path.abspath(__file__));RAW=f"{WD}/../dl/raw.mp4"
SFXD=f"{HERE}/../sfx";MUS=f"{HERE}/../../aster/music/Aster_MuzikLatar_Ceria_100BPM.mp3"
o=T.s2o;D=T.DUR;E0=D-T.END
SFX=[(0.0,"pop",.6),(0.95,"whoosh",.55),(1.3,"pop",.35),(o(0.3),"pop",.35),(o(5.5),"whoosh",.45),(o(5.62),"ding",.4),(o(7.92),"pop",.35),(o(9.5),"pop",.35),
(o(11.6),"whoosh",.5),(o(11.9),"pop",.3),(o(22.05),"ding",.35),(o(30.0),"ding",.35),(o(30.25),"pop",.35),(o(42.52),"ding",.35),
(o(54.1),"ding",.45),(o(54.12),"impact",.3),(o(55.0),"whoosh",.5),(o(55.1),"pop",.35),(o(56.26),"pop",.4),(o(58.68),"pop",.35),(o(60.25),"swoosh_down",.4),
(o(60.58),"pop",.35),(o(68.1),"whoosh",.45),(o(68.15),"ding",.4),(o(71.0),"pop",.35),(o(72.3),"click",.45),(o(72.95),"pop",.35),(E0,"whoosh",.45),(E0+0.08,"ding",.35)]
for col in (T.NW,T.KW,T.RW):
    for s,e in col: SFX.append((o(s),"tick",.22))
SFX.sort()
def run(c): return subprocess.run(c,shell=True,capture_output=True,text=True)
# --- tampal "enam" (Cikgu sendiri) ganti "lima" kedua; panjang dikekalkan supaya semua masa sama ---
import numpy as np,wave
run(f"ffmpeg -v error -y -i {RAW} -ac 1 -ar 48000 -c:a pcm_s16le {WD}/src48.wav")
w=wave.open(f"{WD}/src48.wav");a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32);w.close()
R=48000;(d0,d1),(s0,s1)=T.AUDIO_PATCH["dst"],T.AUDIO_PATCH["src"]
clip=a[int(s0*R):int(s1*R)].copy();dst=a[int(d0*R):int(d1*R)]
g=np.sqrt((dst**2).mean())/np.sqrt((clip**2).mean());clip*=min(max(g,0.7),1.4)
n=int(0.012*R);rmp=np.linspace(0,1,n)
seg=np.zeros(len(dst),np.float32);seg[:len(clip)]=clip
seg[:n]=seg[:n]*rmp+dst[:n]*(1-rmp)                    # silang-pudar di awal
tail=len(clip);seg[tail-n:tail]*=rmp[::-1]
seg[tail-n:]+=dst[tail-n:]*np.concatenate([rmp,np.ones(len(dst)-tail)])*0.0+0
b=a.copy();b[int(d0*R):int(d0*R)+len(dst)]=seg
w=wave.open(f"{WD}/src_patched.wav","w");w.setnchannels(1);w.setsampwidth(2);w.setframerate(R);w.writeframes(np.clip(b,-32768,32767).astype(np.int16).tobytes());w.close()
RAW=f"{WD}/src_patched.wav"
parts=[f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.02:.3f}:d=0.02[v{i}]" for i,(a,b) in enumerate(T.EDL)]
cat=";".join(parts)+";"+"".join(f"[v{i}]" for i in range(len(T.EDL)))+f"concat=n={len(T.EDL)}:v=0:a=1[c]"
pre="highpass=f=80,afftdn=nr=10:nf=-45:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,equalizer=f=3500:t=q:w=1:g=1.5"
run(f'ffmpeg -v error -y -i {RAW} -filter_complex "{cat};[c]{pre}[o]" -map "[o]" -ar 48000 {WD}/voice_pre.wav')
r=run(f'ffmpeg -hide_banner -i {WD}/voice_pre.wav -af loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
ln=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
run(f'ffmpeg -v error -y -i {WD}/voice_pre.wav -af "{ln},aresample=48000,adelay={int(T.THUMB*1000)}:all=1,apad=whole_dur={D:.2f}" -ac 2 {WD}/voice.wav')
mus=f"atrim=0:{D:.2f},asetpts=PTS-STARTPTS,aresample=48000,volume='if(lt(t,0.9),0.25,if(lt(t,1.2),0.25-(t-0.9)/0.3*0.184,if(lt(t,{E0:.2f}),0.066,0.066+min((t-{E0:.2f})/0.3,1)*0.184)))':eval=frame,afade=t=out:st={D-0.55:.2f}:d=0.55"
inputs=f'-i {WD}/voice.wav -i "{MUS}" ';fl=f"[1:a]{mus}[m];"
for i,(t,n,g) in enumerate(SFX):
    inputs+=f"-i {SFXD}/{n}.wav ";fl+=f"[{i+2}:a]aresample=48000,volume={g},adelay={int(t*1000)}:all=1[s{i}];"
fl+="[0:a][m]"+"".join(f"[s{i}]" for i in range(len(SFX)))+f"amix=inputs={len(SFX)+2}:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]"
r=run(f'ffmpeg -v error -y {inputs} -filter_complex "{fl}" -map "[a]" -t {D:.2f} {WD}/mix_pre.wav');print(r.stderr[-300:])
r=run(f'ffmpeg -hide_banner -i {WD}/mix_pre.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
run(f'ffmpeg -v error -y -i {WD}/mix_pre.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true,aresample=48000" {WD}/mix.wav')
r=run(f'ffmpeg -hide_banner -i {WD}/mix.wav -af ebur128=peak=true -f null -');print(r.stderr[-330:])
json.dump([{"t":round(t,2),"name":n} for t,n,g in SFX],open(f"{HERE}/sfx.json","w"))
