# usage: cutaudio.py edl.json A.wav B.wav out.wav  -> concatenates EDL parts with 12ms crossfade-free micro fades
import json,subprocess,sys
e=json.load(open(sys.argv[1]));src={"A":sys.argv[2],"B":sys.argv[3]}
inputs=[];fc=[]
for k,p in enumerate(e["parts"]):
    d=p["out"]-p["in"]
    inputs+=["-ss",str(p["in"]),"-t",f"{d:.3f}","-i",src[p["clip"]]]
    fc.append(f"[{k}]afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{k}]")
fc.append("".join(f"[a{k}]" for k in range(len(e["parts"])))+f"concat=n={len(e['parts'])}:v=0:a=1[o]")
subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(fc),"-map","[o]",sys.argv[4]],check=True)
