# Builds the preview proxies from edit/plan.json: graded.mp4 (cut + grade + cleaned voice) and orig.mp4 (cut only, silent).
# These are low-res previews for the review page, not the final render.
import json,subprocess,sys
src,plan,outdir=sys.argv[1:4]
P=json.load(open(plan))
GRADE=("colorchannelmixer=rr=0.93:gg=0.985:bb=1.09,curves=all='0/0.035 0.25/0.24 0.5/0.535 0.8/0.855 1/0.97',"
       "eq=contrast=1.03:saturation=0.9:gamma=1.09,huesaturation=saturation=-0.3:colors=y:strength=1,"
       "huesaturation=saturation=-0.12:intensity=0.02:colors=r:strength=1")
def build(graded):
    fc=[];n=len(P["cuts"])
    for i,c in enumerate(P["cuts"]):
        fc.append(f"[0:v]trim={c['src_in']}:{c['src_out']},setpts=PTS-STARTPTS[v{i}]")
        d=c["src_out"]-c["src_in"]
        fc.append(f"[0:a]atrim={c['src_in']}:{c['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.015:.3f}:d=0.015[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[cv][ca]")
    v="[cv]"
    if graded:
        fc+=[ "[1]format=gbrp[m1]","[2]format=gbrp[m2]",
              f"{v}format=gbrp,{GRADE},format=gbrp,split[ga][gb]","[gb]eq=brightness=0.05:gamma=1.12,format=gbrp[gbr]",
              "[ga][gbr][m1]maskedmerge[gf]","[gf]split[gc][gd]","[gd]eq=brightness=-0.08,format=gbrp[gdk]","[gdk][gc][m2]maskedmerge[gv]"];v="[gv]"
    fc.append(f"{v}tpad=start_mode=clone:start_duration={P.get('intro',0)}:stop_mode=clone:stop_duration={P['outro']},scale=-2:1280,format=yuv420p[vo]")
    fc.append(f"[ca]highpass=f=80,afftdn=nr=8:nf=-42,deesser=i=0.3,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,"
              f"equalizer=f=3200:t=q:w=1.2:g=2,loudnorm=I=-15:TP=-1.5:LRA=7,aresample=48000,aformat=channel_layouts=stereo[an]")
    # the thumbnail intro: real leading silence (adelay after loudnorm was silently not applied)
    fc.append(f"aevalsrc=0|0:s=48000:c=stereo:d={P.get('intro',0)}[sil]")
    fc.append(f"[sil][an]concat=n=2:v=0:a=1,apad=pad_dur={P['outro']}[ao]")
    out=f"{outdir}/{'graded' if graded else 'orig'}-v5.mp4"
    cmd=["ffmpeg","-v","error","-y","-i",src,"-i","edit/facemask.png","-i","edit/vigmask.png","-filter_complex",";".join(fc),"-map","[vo]"]
    if not graded: fc[-1]=fc[-1].replace("[ao]","[ao];[ao]anullsink")
    cmd[cmd.index("-filter_complex")+1]=";".join(fc)
    cmd+=(["-map","[ao]","-c:a","aac","-b:a","128k","-ar","48000"] if graded else ["-an"])
    cmd+=["-c:v","libx264","-preset","slow","-crf","25" if graded else "27","-g","15","-movflags","+faststart","-t",str(P["duration"]+P["outro"]),out]
    subprocess.run(cmd,check=True);print("wrote",out)
for g in sys.argv[4:] or ['graded','orig']: build(g=='graded')
