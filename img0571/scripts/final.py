# Final 1080x1920 render: cut -> punch-in zoom -> B-roll -> graphics/captions overlay -> SFX mix.
# usage: final.py edl.json plan.json graded_full_1080.mov source.MOV clipdir overlay_png_dir sfxdir workdir out.mp4
import json,os,sys,subprocess
def zoom_expr(Z):
    """ffmpeg expression of the preview's eased zoom keyframes (in-out quad), evaluated on input time `it`"""
    def seg(i):
        a,b=Z[i],Z[i+1];dt=max(b["t"]-a["t"],1e-3);k=f"((it-{a['t']})/{dt})"
        e=f"if(lt({k},0.5),2*{k}*{k},1-pow(-2*{k}+2,2)/2)"
        return f"if(lt(it,{b['t']}),{a['scale']}+({b['scale']-a['scale']})*{e},{{}})"
    expr="{}"
    for i in range(len(Z)-1): expr=expr.replace("{}",seg(i),1)
    expr=expr.replace("{}",str(Z[-1]["scale"]))
    return f"if(lt(it,{Z[0]['t']}),{Z[0]['scale']},{expr})"
if __name__=="__main__" and sys.argv[1]=="--zoom-expr":
    print(zoom_expr(json.load(open(sys.argv[2]))["zoom"]));sys.exit()
E_,P_,G,SRC,CLIPS,OV,SFXD,WD,OUT=sys.argv[1:10]
d=json.load(open(E_));p=json.load(open(P_));segs=d["segments"];ec=d["end_card"];F=0.012
def run(a): print(" ".join(a[:6]),"…",flush=True);subprocess.run(a,check=True)
# 1. cut, one segment at a time (a single filtergraph buffers too many 1080p frames when segments are out of order)
FPS=30000/1001;lst=open(f"{WD}/segs.txt","w")
for i,s in enumerate(segs):
    nfr=round((s["src_out"]-s["src_in"])*FPS)
    run(["ffmpeg","-v","error","-y","-ss",str(s["src_in"]),"-i",G,"-frames:v",str(nfr),"-an","-c:v","libx264","-preset","fast","-crf","12","-pix_fmt","yuv420p",f"{WD}/seg{i}.mov"]);lst.write(f"file 'seg{i}.mov'\n")
run(["ffmpeg","-v","error","-y","-ss",str(ec["freeze_src"]),"-i",G,"-frames:v","1",f"{WD}/freeze.png"])
run(["ffmpeg","-v","error","-y","-loop","1","-framerate","30000/1001","-i",f"{WD}/freeze.png","-frames:v",str(round(ec["dur"]*FPS)),"-c:v","libx264","-preset","fast","-crf","12","-pix_fmt","yuv420p",f"{WD}/segend.mov"]);lst.write("file 'segend.mov'\n");lst.close()
run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{WD}/segs.txt","-c","copy",f"{WD}/1_video.mov"])
fc=[];n=len(segs)
for i,s in enumerate(segs):
    fc.append(f"[0:a]atrim={s['src_in']}:{s['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d={F},afade=t=out:st={s['src_out']-s['src_in']-F}:d={F}[a{i}]")
fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={ec['dur']}[a{n}]")
fc.append("".join(f"[a{i}]" for i in range(n+1))+f"concat=n={n+1}:v=0:a=1[araw]")
fc.append("[araw]highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]")
run(["ffmpeg","-v","error","-y","-i",SRC,"-filter_complex",";".join(fc),"-map","[a]","-c:a","pcm_s16le",f"{WD}/1_audio.wav"])
run(["ffmpeg","-v","error","-y","-i",f"{WD}/1_video.mov","-i",f"{WD}/1_audio.wav","-map","0:v","-map","1:a","-c","copy",f"{WD}/1_cut.mov"])
# 2. punch-in: same eased keyframes as the preview, origin (46%,40%); 2x upscale first so slow zooms don't jitter
Z=p["zoom"];ox=p["origin"]["x"]/100;oy=p["origin"]["y"]/100;expr=zoom_expr(Z)
open(f"{WD}/zoom_expr.txt","w").write(expr)
run(["ffmpeg","-v","error","-y","-i",f"{WD}/1_cut.mov","-vf",f"scale=2160:3840:flags=lanczos,zoompan=z='{expr}':x='(iw-iw/zoom)*{ox}':y='(ih-ih/zoom)*{oy}':d=1:s=1080x1920:fps=30000/1001",
     "-c:v","libx264","-preset","fast","-crf","12","-c:a","copy",f"{WD}/2_zoom.mov"])
# 3. B-roll
run(["env","CRF=12","python3",os.path.join(os.path.dirname(__file__),"broll.py"),P_,CLIPS,f"{WD}/2_zoom.mov",f"{WD}/3_broll.mov","1080x1920"])
# 4. overlay + 5. SFX
ins=["-i",f"{WD}/3_broll.mov","-framerate","30000/1001","-i",f"{OV}/o%05d.png"];afc=[]
for j,s in enumerate(p["sfx"]):
    ins+=["-i",f"{SFXD}/{s['name']}.wav"];ms=int(s["t"]*1000)
    afc.append(f"[{j+2}:a]aresample=48000,volume={s['gain']:.2f},adelay={ms}|{ms}[s{j}]")
m=len(p["sfx"])
fc=["[0:v][1:v]overlay=format=auto:shortest=0,format=yuv420p[v]"]+afc+["[0:a]"+"".join(f"[s{j}]" for j in range(m))+f"amix=inputs={m+1}:normalize=0:duration=first,alimiter=limit=0.89[a]"]
run(["ffmpeg","-v","error","-y"]+ins+["-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-t",str(d["duration"]),
     "-c:v","libx264","-preset","slow","-crf","17","-profile:v","high","-pix_fmt","yuv420p","-r","30000/1001","-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",OUT])
print("done",OUT)
