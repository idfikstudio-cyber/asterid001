# Render AS-F-004_Penutup2026. usage:
#   python3 render.py RAW.mp4 OUTDIR preview|final
# Langkah: potong+grade (ffmpeg) -> grafik PNG (render_overlay.js) -> zoom+komposit (numpy/cv2) -> audio (voice+muzik+SFX) -> mux.
import json,os,subprocess as sp,sys,numpy as np,cv2
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(os.path.dirname(HERE))
raw,out,mode=sys.argv[1],sys.argv[2],sys.argv[3]; os.makedirs(out,exist_ok=True)
P=json.load(open(os.path.join(HERE,"plan.json"))); FPS=30
W,H=(540,960) if mode=="preview" else (1080,1920)
SW,SH=1080,1920
# grade: cerahkan & jelaskan sedikit, dinding kelabu kurang sejuk, tona kulit dikekalkan (saturasi rendah, tiada anjakan merah)
GRADE="eq=brightness=0.02:contrast=1.06:saturation=1.07:gamma=1.03,colorbalance=rs=0.0:bs=-0.015:rm=0.005:bm=-0.01,curves=all='0/0.02 0.25/0.24 0.5/0.52 0.8/0.84 1/0.985',unsharp=5:5:0.35"
def run(c): print("+"," ".join(c)[:200],flush=True); sp.run(c,check=True)
tmp=os.path.join(out,"_work"); os.makedirs(tmp,exist_ok=True)
base=os.path.join(tmp,"base.mp4"); thumb=os.path.join(tmp,"thumb.png")
# 1) potongan + grade
fc="".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i,(a,b) in enumerate(P["keep"]))
n=len(P["keep"]); fc+="".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[vc][ac];[vc]{GRADE},format=yuv420p[vo]"
if not os.path.exists(base):
    run(["ffmpeg","-v","error","-y","-i",raw,"-filter_complex",fc,"-map","[vo]","-map","[ac]","-r","30","-c:v","libx264","-crf","12","-preset","fast","-c:a","pcm_s16le",base.replace(".mp4",".mov")])
    os.rename(base.replace(".mp4",".mov"),base)
run(["ffmpeg","-v","error","-y","-ss",str(P["thumb_src"]),"-i",raw,"-frames:v","1","-vf",GRADE,thumb])
# 2) grafik
ov=os.path.join(tmp,f"ov{W}")
if not os.path.exists(os.path.join(ov,"%05d.png"%(round(P["duration"]*FPS)-1))):
    run(["node",os.path.join(HERE,"render_overlay.js"),os.path.join(HERE,"plan.json"),ov,str(W),str(FPS)])
# 3) zoom + komposit
EYE,TARGET=0.42,0.34
def zoom_at(t):
    Z=P["zoom"]; k=max(i for i,z in enumerate(Z) if z["t"]<=t) if t>=Z[0]["t"] else 0
    m=Z[k]["mode"]
    if m=="B": return 1.12
    if m=="P": return 1.25
    t1=Z[k+1]["t"] if k+1<len(Z) else P["content_end"]; u=(t-Z[k]["t"])/(t1-Z[k]["t"]); u=u*u*(3-2*u)
    return 1.12+0.10*u
def crop(img,s):
    cw,ch=SW/s,SH/s; x0=(SW-cw)/2; y0=min(SH-ch,max(0,(EYE-TARGET/s)*SH))
    M=np.array([[W/cw,0,-x0*W/cw],[0,H/ch,-y0*H/ch]],np.float32)
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_AREA if W<SW/s else cv2.INTER_CUBIC)
vid=os.path.join(tmp,"video.mp4")
def composite():
    dec=sp.Popen(["ffmpeg","-v","error","-i",base,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=sp.PIPE)
    crf="23" if mode=="preview" else "19"
    enc=sp.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","medium","-crf",crf,"-pix_fmt","yuv420p",vid],stdin=sp.PIPE)
    th=crop(cv2.imread(thumb),1.18); last=None; N=round(P["duration"]*FPS)
    for i in range(N):
        t=i/FPS
        if t<P["thumb"]: fr=th.copy()
        elif t<P["content_end"]:
            buf=dec.stdout.read(SW*SH*3)
            if len(buf)==SW*SH*3: last=np.frombuffer(buf,np.uint8).reshape(SH,SW,3)
            fr=crop(last,zoom_at(t))
        else: fr=np.zeros((H,W,3),np.uint8)
        o=cv2.imread(os.path.join(ov,"%05d.png"%i),cv2.IMREAD_UNCHANGED)
        if o is not None and o.shape[2]==3: fr=o   # frame legap (end card) disimpan tanpa alfa
        elif o is not None:
            a=o[:,:,3:4].astype(np.float32)/255; fr=(fr*(1-a)+o[:,:,:3]*a).astype(np.uint8)
        if i==int(0.5*FPS): cv2.imwrite(os.path.join(out,"thumb_frame.png"),fr)
        enc.stdin.write(fr.tobytes())
    enc.stdin.close(); enc.wait(); dec.kill()
if not os.path.exists(vid) or os.environ.get("REDO"): composite()  # REDO=1 untuk render semula gambar

# 4) audio: suara (denoise ringan, -14 LUFS) + muzik asal (-22 dB bawah suara, ducking) + SFX
voice=os.path.join(tmp,"voice.wav"); music=os.path.join(tmp,"music.wav")
run(["python3","-I",os.path.join(ROOT,"scripts","music.py"),music,str(P["duration"]+0.5),"84"])
pre="highpass=f=75,afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2"
m=sp.run(["ffmpeg","-hide_banner","-i",base,"-af",pre+",loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
j=json.loads(m[m.rindex("{"):m.rindex("}")+1])
ln=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
run(["ffmpeg","-v","error","-y","-i",base,"-af",f"{pre},{ln},aresample=48000,adelay={int(P['thumb']*1000)}:all=1,apad=whole_dur={P['duration']}","-ac","2",voice])
sfx=[s for s in P["sfx"]]; ins=["-i",voice,"-i",music]+sum((["-i",os.path.join(ROOT,"edit","sfx",s["name"]+".wav")] for s in sfx),[])
# muzik: -36 LUFS bawah suara (-14) = ~22 dB; naik sedikit pada thumbnail & end card
ce=P["content_end"]; th0=P["thumb"]
mv=f"volume='if(lt(t,{th0}),0.30,if(gt(t,{ce}),0.42,0.16))':eval=frame"
f=f"[1:a]aresample=48000,{mv}[mu];[0:a]asplit=2[vo][sc];[mu][sc]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=450:makeup=1[md];"
f+="".join(f"[{k+2}:a]aresample=48000,volume={s['gain']*0.55:.3f},adelay={int(s['t']*1000)}:all=1[s{k}];" for k,s in enumerate(sfx))
f+=f"[vo][md]"+"".join(f"[s{k}]" for k in range(len(sfx)))+f"amix=inputs={len(sfx)+2}:normalize=0:duration=first,alimiter=limit=0.89:attack=3:release=60,atrim=0:{P['duration']}[aout]"
mix0=os.path.join(tmp,"mix0.wav"); run(["ffmpeg","-v","error","-y"]+ins+["-filter_complex",f,"-map","[aout]","-ac","2",mix0])
# normalisasi akhir campuran: -14 LUFS, true peak di bawah -1 dBTP selepas AAC
m=sp.run(["ffmpeg","-hide_banner","-i",mix0,"-af","loudnorm=I=-14:TP=-2:LRA=9:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
j=json.loads(m[m.rindex("{"):m.rindex("}")+1])
mix=os.path.join(tmp,"mix.wav")
run(["ffmpeg","-v","error","-y","-i",mix0,"-af",f"loudnorm=I=-14:TP=-2:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000",mix])
name="AS-F-004_Penutup2026_PREVIEW.mp4" if mode=="preview" else "AS-F-004_Penutup2026_FINAL.mp4"
run(["ffmpeg","-v","error","-y","-i",vid,"-i",mix,"-c:v","copy","-c:a","aac","-b:a","192k" if mode=="final" else "128k","-movflags","+faststart","-shortest",os.path.join(out,name)])
print(sp.run(["ffmpeg","-hide_banner","-i",os.path.join(out,name),"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr.split("Summary:")[-1])
