# Overlay B-roll cutaways on the base talking-head track and finish audio.
# usage: build_proxy.py plan.json base.mov brolldir out.mp4 graded|orig WIDTH
import json,subprocess,sys
P=json.load(open(sys.argv[1]));base,bd,out,mode,W=sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],int(sys.argv[6]);H=W*16//9
DUR,END=P["duration"],P["speech_end"]
LOOK="curves=all='0/0.03 0.25/0.22 0.55/0.55 0.85/0.83 1/0.95',colorbalance=rs=-0.03:bs=0.035:bh=-0.015,eq=contrast=1.03:saturation=1.04"
inp=["-i",base];fc=[f"[0:v]tpad=stop_mode=clone:stop_duration={DUR-END+0.5:.2f},trim=0:{DUR},setpts=PTS-STARTPTS[v0]"]
last="v0"
for k,b in enumerate(P["broll"],1):
    d=b["e"]-b["s"];inp+=["-ss",str(b["src"]),"-t",f"{d+0.1:.2f}","-i",f"{bd}/{b['id']}.mp4"]
    # 9:16 window from 1280x720 (405 px wide), slow 6% push-in over the shot
    cx=max(0,min(1280-405,b["x"]*1280-405/2))
    push=f"crop=405:720:{cx:.0f}:0,scale=w='2*trunc({W}*(1+0.06*t/{d:.2f})/2)':h='2*trunc({H}*(1+0.06*t/{d:.2f})/2)':eval=frame:flags=bicubic,crop={W}:{H}:(iw-{W})/2:(ih-{H})/2"
    g=LOOK+"," if mode=="graded" else ""
    dim=",eq=brightness=-0.12:saturation=0.9,gblur=sigma=2" if b["e"]>=DUR-0.01 else ""
    fc.append(f"[{k}:v]setpts=PTS-STARTPTS,fps=30000/1001,{push},{g}setsar=1{dim},setpts=PTS+{b['s']}/TB[b{k}]")
    fc.append(f"[{last}][b{k}]overlay=enable='between(t,{b['s']},{b['e']-0.001})':eof_action=pass[v{k}]");last=f"v{k}"
fc.append(f"[{last}]format=yuv420p[vout]")
# voice: rumble cut, light denoise, gentle compression, broadcast loudness
A="highpass=f=80,afftdn=nr=8:nf=-42,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7" if mode=="graded" else "anull"
fc.append(f"[0:a]{A},apad,atrim=0:{DUR}[aout]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fc),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","slow","-crf","27","-profile:v","high","-pix_fmt","yuv420p","-movflags","+faststart","-c:a","aac","-b:a","128k","-ar","48000",out],check=True)
