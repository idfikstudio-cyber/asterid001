# Overlay B-roll (landscape/portrait video or still photo) on the talking-head base and finish the voice.
# usage: build_proxy.py plan.json base.mov mixkit_dir fik_photo_dir out.mp4 graded|orig WIDTH
import json,subprocess,sys
P=json.load(open(sys.argv[1]));base,md,fd,out,mode,W=sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],int(sys.argv[7]);H=W*16//9
DUR,END=P["duration"],P["speech_end"]
# B-roll look: tame warm/cold stock differences toward the same clean, slightly warm finish as the talking head
LOOK="curves=all='0/0.02 0.2/0.17 0.5/0.52 0.8/0.84 1/0.97',eq=contrast=1.03:saturation=0.97,colorbalance=rh=0.01:bh=-0.01"
def size(path):
    w,h=subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",path]).decode().strip().split(",")[:2]
    return int(w),int(h)
inp=["-i",base];fc=[f"[0:v]tpad=stop_mode=clone:stop_duration={DUR-END+0.5:.2f},trim=0:{DUR},setpts=PTS-STARTPTS[v0]"];last="v0"
for k,b in enumerate(P["broll"],1):
    d=b["e"]-b["s"]
    if b["src"]=="fik":
        path=f"{fd}/{b['file']}";inp+=["-loop","1","-framerate","30000/1001","-t",f"{d+0.1:.2f}","-i",path]
    else:
        path=f"{md}/{b['id']}.mp4";inp+=["-ss",str(b["t"]),"-t",f"{d+0.1:.2f}","-i",path]
    sw,sh=size(path)
    cw=min(sw,round(sh*9/16));ch=min(sh,round(sw*16/9))
    cx=max(0,min(sw-cw,b["x"]*sw-cw/2));cy=(sh-ch)/2
    push=(f"crop={cw}:{ch}:{cx:.0f}:{cy:.0f},scale=w='2*trunc({W}*(1+0.07*t/{d:.2f})/2)':h='2*trunc({H}*(1+0.07*t/{d:.2f})/2)':eval=frame:flags=bicubic,"
          f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2")
    g=LOOK+"," if mode=="graded" else ""
    fc.append(f"[{k}:v]setpts=PTS-STARTPTS,fps=30000/1001,format=yuv420p,{push},{g}setsar=1,setpts=PTS+{b['s']}/TB[b{k}]")
    fc.append(f"[{last}][b{k}]overlay=enable='between(t,{b['s']},{b['e']-0.001})':eof_action=pass[v{k}]");last=f"v{k}"
fc.append(f"[{last}]format=yuv420p[vout]")
A="highpass=f=80,afftdn=nr=8:nf=-42,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7" if mode=="graded" else "anull"
fc.append(f"[0:a]{A},apad,atrim=0:{DUR}[aout]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fc),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","slow","-crf","26","-profile:v","high","-pix_fmt","yuv420p","-movflags","+faststart","-c:a","aac","-b:a","128k","-ar","48000",out],check=True)
