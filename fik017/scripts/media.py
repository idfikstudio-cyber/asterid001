# Builds timeline-length proxy videos (black outside their segments) + VO stem + full audio mix.
import json,subprocess,sys,wave,os
import numpy as np
S=sys.argv[1]; P=json.load(open(S+"/build/plan.json")); DUR=P["dur"]; SR=44100
def run(a): subprocess.run(a,check=True)
def tl_video(src,segs,out,w):
    parts=[];fc=[];i=0
    inputs=[]
    t=0.0
    for t0,a,d in segs:
        if t0>t: fc.append(f"color=c=black:s={w}x{w*16//9}:r=30:d={t0-t:.3f}[g{i}]");parts.append(f"[g{i}]")
        fc.append(f"[0:v]trim={a}:{a+d},setpts=PTS-STARTPTS,scale={w}:{w*16//9}:force_original_aspect_ratio=increase,crop={w}:{w*16//9},fps=30,setsar=1[s{i}]");parts.append(f"[s{i}]")
        t=t0+d;i+=1
    if t<DUR: fc.append(f"color=c=black:s={w}x{w*16//9}:r=30:d={DUR-t:.3f}[g{i}]");parts.append(f"[g{i}]")
    fc.append("".join(parts)+f"concat=n={len(parts)}:v=1:a=0[v]")
    run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",";".join(fc),"-map","[v]","-c:v","libx264","-crf","27","-preset","slow","-g","15","-pix_fmt","yuv420p","-movflags","+faststart",out])
os.makedirs(S+"/build/vid",exist_ok=True)
tl_video(S+"/logo/CFik016.MOV",P["founder"],S+"/build/vid/founder.mp4",540)
tl_video(S+"/src/Client Respon.MOV",P["client"],S+"/build/vid/client.mp4",360)
# VO stem: cleaned voice (highpass, gentle denoise, compression), placed on timeline
def load(path):
    w=wave.open(path); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    return x.reshape(-1,w.getnchannels())
run(["ffmpeg","-v","error","-y","-i",S+"/logo/CFik016.MOV","-af","highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=7","-ar",str(SR),"-ac","2",S+"/work/vo_clean.wav"])
src=load(S+"/work/vo_clean.wav")
N=int(DUR*SR); vo=np.zeros((N,2),np.float32); duck=np.zeros(N,np.float32)
for t0,a,b in P["vo"]:
    seg=src[int(a*SR):int(b*SR)].copy(); f=int(0.03*SR)
    seg[:f]*=np.linspace(0,1,f)[:,None]; seg[-f:]*=np.linspace(1,0,f)[:,None]
    i=int(t0*SR); vo[i:i+len(seg)]+=seg; duck[max(0,i-int(.15*SR)):i+len(seg)+int(.25*SR)]=1
k=int(0.25*SR); duck=np.convolve(duck,np.ones(k)/k,"same")
mus=load(S+"/build/music.wav")[:N]; mus=np.pad(mus,((0,N-len(mus)),(0,0)))
mus*= (1-0.72*duck)[:,None]*0.55            # music sits under VO (~-11 dB while talking)
fx=np.zeros((N,2),np.float32)
for c in P["sfx"]:
    x=load(S+f"/build/sfx/{c['n']}.wav"); i=int(c["t"]*SR); x=x[:N-i]
    fx[i:i+len(x)]+=x*c["g"]*0.42
mix=vo*1.0+mus+fx
pk=np.abs(mix).max(); mix=mix/max(pk,1)*0.95 if pk>0.95 else mix
def save(p,x):
    with wave.open(p,"w") as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())
save(S+"/work/mix.wav",mix)
run(["ffmpeg","-v","error","-y","-i",S+"/work/mix.wav","-b:a","160k",S+"/build/mix.mp3"])
print("peak",pk)
