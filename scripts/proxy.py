# usage: proxy.py src.mp4 edl.json grade.txt af.txt outdir [height] [final]
# Writes outdir/graded.mp4 (cut + crop 9:16 + grade + cleaned audio) and outdir/orig.mp4 (same cut, untouched, no audio) for the preview wipe.
# With "final": only base.mkv (crf 12 video, PCM audio), the input for render_final.py.
import json,subprocess,sys
src,edl,gradef,aff,out=sys.argv[1:6];H=int(sys.argv[6]) if len(sys.argv)>6 else 960
E=json.load(open(edl));G=open(gradef).read().strip();AF=open(aff).read().strip()
W=H*9//16;FINAL=len(sys.argv)>7 and sys.argv[7]=="final"
def graph(grade):
    f=[f"[0:a]{AF},aresample=48000[ac]" if grade else "","[ac]asplit=%d%s"%(len(E["segments"]),"".join(f"[a{i}]" for i in range(len(E["segments"])))) if grade else ""]
    f=[x for x in f if x]
    f.append("[0:v]split=%d%s"%(len(E["segments"]),"".join(f"[v{i}]" for i in range(len(E["segments"])))))
    cat=""
    for i,s in enumerate(E["segments"]):
        f.append(f"[v{i}]trim={s['src_in']}:{s['src_out']},setpts=PTS-STARTPTS[t{i}]")
        if grade:
            d=s["src_out"]-s["src_in"]
            f.append(f"[a{i}]atrim={s['src_in']}:{s['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.015:.3f}:d=0.015[u{i}]")
            cat+=f"[t{i}][u{i}]"
        else: cat+=f"[t{i}]"
    n=len(E["segments"])
    vchain=f"crop=1080:1920:0:60,{G+',' if grade else ''}scale={W}:{H}:flags=lanczos,tpad=stop_mode=clone:stop_duration={E['tail']},fps=30,format=yuv420p"
    if grade:
        f.append(f"{cat}concat=n={n}:v=1:a=1[cv][ca]");f.append(f"[cv]{vchain}[vo]");f.append(f"[ca]apad=pad_dur={E['tail']}[ao]")
    else:
        f.append(f"{cat}concat=n={n}:v=1:a=0[cv]");f.append(f"[cv]{vchain}[vo]")
    return ";".join(f)
for name,grade,br in ((("graded",True,"1100k"),) if FINAL else (("graded",True,"1100k"),("orig",False,"550k"))):
    cmd=["ffmpeg","-v","error","-y","-i",src,"-filter_complex",graph(grade),"-map","[vo]"]
    if FINAL:
        cmd+=["-map","[ao]","-c:a","pcm_s16le","-c:v","libx264","-preset","medium","-crf","12","-t",str(E["duration"]),f"{out}/base.mkv"]
        subprocess.run(cmd,check=True);print("wrote base");continue
    cmd+=(["-map","[ao]","-c:a","aac","-b:a","96k"] if grade else ["-an"])
    cmd+=["-c:v","libx264","-preset","medium","-b:v",br,"-maxrate",br,"-bufsize","2M","-g","30","-movflags","+faststart","-t",str(E["duration"]),f"{out}/{name}.mp4"]
    subprocess.run(cmd,check=True);print("wrote",name)
