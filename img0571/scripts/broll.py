# Composite real B-roll onto a cut video, per plan.json "broll" (crop 9:16 from 16:9, light colour match, slow push-in).
# usage: broll.py plan.json clipdir in.mp4 out.mp4 [WxH]   (WxH default 540x960; use 1080x1920 for final)
import json,os,sys,subprocess
p=json.load(open(sys.argv[1]));CD,IN,OUT=sys.argv[2:5];W,H=map(int,(sys.argv[5] if len(sys.argv)>5 else "540x960").split("x"))
args=["ffmpeg","-v","error","-y","-i",IN];fc=[];last="0:v"
for i,b in enumerate(p["broll"]):
    dur=round(b["e"]-b["s"],3)
    args+=["-ss",str(b["src"]),"-t",str(dur+0.2),"-i",f"{CD}/{b['clip']}.mp4"]
    # crop a 9:16 window centred on cx, push in 4% over the shot, match the presenter's soft contrast
    v=(f"[{i+1}:v]fps=30000/1001,crop=ih*9/16:ih:'min(max(iw*{b['cx']}-ih*9/32,0),iw-ih*9/16)':0,scale={W*1.06:.0f}:{H*1.06:.0f},"
       f"crop={W}:{H}:'(iw-{W})/2*(1-t/{dur})':'(ih-{H})/2*(1-t/{dur})',eq=contrast=1.02:saturation=0.92")
    if b.get("blur"): v+=",gblur=sigma=10,eq=brightness=-0.04"
    fc.append(v+f",setpts=PTS-STARTPTS+{b['s']}/TB[b{i}]")
    fc.append(f"[{last}][b{i}]overlay=enable='between(t,{b['s']},{b['e']-0.001})':eof_action=pass[o{i}]");last=f"o{i}"
args+=["-filter_complex",";".join(fc),"-map",f"[{last}]","-map","0:a?","-c:a","copy","-c:v","libx264","-preset","medium","-crf",os.environ.get("CRF","24"),"-g","15","-pix_fmt","yuv420p","-movflags","+faststart",OUT]
subprocess.run(args,check=True)
