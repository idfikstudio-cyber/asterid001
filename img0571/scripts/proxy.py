# Cut preview proxies from the full-length proxies using edl.json.
# usage: proxy.py edl.json graded_full.mp4 orig_full.mp4 source.MOV outdir
import json,sys,subprocess
d=json.load(open(sys.argv[1]));G,O,SRC,OUT=sys.argv[2:6]
segs=d["segments"];ec=d["end_card"];F=0.012  # 12 ms audio fades at every splice
def cut(video,name,audio):
    fc=[];n=len(segs)
    for i,s in enumerate(segs):
        fc.append(f"[0:v]trim={s['src_in']}:{s['src_out']},setpts=PTS-STARTPTS[v{i}]")
        if audio: fc.append(f"[1:a]atrim={s['src_in']}:{s['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d={F},afade=t=out:st={s['src_out']-s['src_in']-F}:d={F}[a{i}]")
    # end card: blurred freeze of the last frame
    fc.append(f"[0:v]trim={ec['freeze_src']}:{ec['freeze_src']+0.04},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={ec['dur']},trim=duration={ec['dur']},gblur=sigma=18,eq=brightness=-0.06[v{n}]")
    if audio: fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={ec['dur']}[a{n}]")
    pairs="".join(f"[v{i}]"+(f"[a{i}]" if audio else "") for i in range(n+1))
    fc.append(f"{pairs}concat=n={n+1}:v=1:a={1 if audio else 0}[v]"+("[araw]" if audio else ""))
    if audio: fc.append("[araw]highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
    cmd=["ffmpeg","-v","error","-y","-i",video]+(["-i",SRC] if audio else [])+["-filter_complex",";".join(fc),"-map","[v]"]+(["-map","[a]","-c:a","aac","-b:a","128k","-ar","48000"] if audio else ["-an"])
    cmd+=["-c:v","libx264","-preset","medium","-crf","24" if audio else "28","-g","15","-pix_fmt","yuv420p","-movflags","+faststart",f"{OUT}/{name}"]
    subprocess.run(cmd,check=True)
cut(G,"graded.mp4",True);cut(O,"orig.mp4",False)
