# Final 1080x1920 render: cover + cut graded video (+ end-card hold), camera zoom from plan, overlay PNGs on top,
# cleaned voice + SFX mix at -14 LUFS.
# usage: python3 at001_final.py source.mp4 look.mp4 plan.json cover.png overlay_dir sfx_dir out.mp4
import sys,json,subprocess,os,cv2,numpy as np
src,look,planf,cover,ovd,sfxd,dst=sys.argv[1:8]
P=json.load(open(planf));FPS=30;W,H=1080,1920
TH=P.get("thumb",0);END=round(P["total"]-P["duration"],3);N=round(P["total"]*FPS)
tmp=dst+".parts";os.makedirs(tmp,exist_ok=True)
C=P["cuts"]
v="".join(f"[0:v]trim={c['src_in']}:{c['src_out']},setpts=PTS-STARTPTS[v{i}];" for i,c in enumerate(C))
a="".join(f"[1:a]atrim={c['src_in']}:{c['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={c['src_out']-c['src_in']-0.008:.3f}:d=0.008[a{i}];" for i,c in enumerate(C))
cat="".join(f"[v{i}]" for i in range(len(C)))+f"concat=n={len(C)}:v=1:a=0[vc];"+"".join(f"[a{i}]" for i in range(len(C)))+f"concat=n={len(C)}:v=0:a=1[ac]"
VOICE="highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000"
# 1) base picture: cover (TH s) + cut graded video + frozen last frame for the end card
subprocess.run(["ffmpeg","-v","error","-y","-i",look,"-i",src,"-loop","1","-framerate",str(FPS),"-t",str(TH),"-i",cover,"-filter_complex",
  v+a+cat+f";[vc]tpad=stop_mode=clone:stop_duration={END},fps={FPS},setsar=1[vb];[2:v]scale={W}:{H},fps={FPS},format=yuv420p,setsar=1[cv];[cv][vb]concat=n=2:v=1:a=0[v];[ac]anullsink",
  "-map","[v]","-c:v","libx264","-preset","fast","-crf","12","-pix_fmt","yuv420p",f"{tmp}/base.mp4"],check=True)
# 2) audio: voice (delayed by the cover) + every SFX at its time and gain
ins=["-i",src]
af=a.replace("[1:a]","[0:a]")+"".join(f"[a{i}]" for i in range(len(C)))+f"concat=n={len(C)}:v=0:a=1[ac];[ac]{VOICE},adelay={int(TH*1000)}:all=1,apad=whole_dur={P['total']}[vo];"
mix=["[vo]"]
for k,s in enumerate(P["sfx"]):
    ins+=["-i",os.path.join(sfxd,s["name"]+".wav")]
    af+=f"[{k+1}:a]aresample=48000,volume={s['gain']*0.9:.3f},adelay={int(round(s['t']*1000))}:all=1[s{k}];";mix.append(f"[s{k}]")
af+="".join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{P['total']},loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000[mx]"
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",af,"-map","[mx]","-c:a","pcm_s16le",f"{tmp}/mix.wav"],check=True)
# 3) composite: zoom (same easing as the preview) + overlay
Z=P["zoom"]
def ease(x): return 2*x*x if x<.5 else 1-(-2*x+2)**2/2
def zoom(t):
    if t<=Z[0]["t"]:return Z[0]["scale"],Z[0]["oy"]
    for i in range(1,len(Z)):
        if t<=Z[i]["t"]:
            A,B=Z[i-1],Z[i];k=ease((t-A["t"])/max(1e-3,B["t"]-A["t"]));return A["scale"]+(B["scale"]-A["scale"])*k,A["oy"]+(B["oy"]-A["oy"])*k
    return Z[-1]["scale"],Z[-1]["oy"]
dec=subprocess.Popen(["ffmpeg","-v","error","-i",f"{tmp}/base.mp4","-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",f"{tmp}/mix.wav",
  "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","17","-profile:v","high","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",dst],stdin=subprocess.PIPE)
for i in range(N):
    raw=dec.stdout.read(W*H*3)
    if len(raw)<W*H*3:break
    f=np.frombuffer(raw,np.uint8).reshape(H,W,3);t=i/FPS
    s,oy=zoom(t)
    if s>1.001:
        ox,oyp=W/2,H*oy/100;M=np.float32([[s,0,(1-s)*ox],[0,s,(1-s)*oyp]])
        f=cv2.warpAffine(f,M,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT)
    o=cv2.imread(f"{ovd}/o{i:05d}.png",cv2.IMREAD_UNCHANGED)
    if o is not None and o.ndim==3 and o.shape[2]==3: f=o   # fully opaque frame (full-screen b-roll / end card) is saved without alpha
    elif o is not None and o[...,3].any():
        al=o[...,3:].astype(np.float32)/255;f=(f*(1-al)+o[...,:3]*al+.5).astype(np.uint8)
    enc.stdin.write(f.tobytes())
    if i%150==0:print("frame",i,"/",N,flush=True)
enc.stdin.close();enc.wait();print("done",dst)
