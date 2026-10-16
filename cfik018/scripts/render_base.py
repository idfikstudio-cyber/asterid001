# Render the talking-head base track from the EDL, graded or original, at preview or full size.
# usage: render_base.py edl.json A.MOV B.MOV maskdir out.mp4 graded|orig WIDTH
import json,subprocess,sys,os
e=json.load(open(sys.argv[1]));src={"A":sys.argv[2],"B":sys.argv[3]};md=sys.argv[4];out=sys.argv[5];mode=sys.argv[6];W=int(sys.argv[7]);H=W*16//9
def sh_var(name):
    return subprocess.check_output(["bash","-c",f". {os.path.dirname(os.path.abspath(__file__))}/grade.sh; printf %s \"${name}\""]).decode()
def graph(grade,key):
    return subprocess.check_output(["bash","-c",f'. {os.path.dirname(os.path.abspath(__file__))}/grade.sh; graph "$1" "$2"',"_",grade,key]).decode().strip()
tmp=out+".parts";os.makedirs(tmp,exist_ok=True);lst=[]
for k,p in enumerate(e["parts"]):
    d=p["out"]-p["in"];f=f"{tmp}/{k:02d}.mp4";lst.append(f)
    args=["ffmpeg","-v","error","-y","-ss",f"{p['in']:.3f}","-t",f"{d:.3f}","-i",src[p["clip"]]]
    if mode=="graded":
        c=p["clip"];args+=["-loop","1","-i",f"{md}/key{c}.png","-loop","1","-i",f"{md}/vig.png",
            "-filter_complex",graph(sh_var(f"GRADE_{c}"),sh_var(f"KEY_{c}"))+f",scale={W}:{H}:flags=lanczos[v]","-map","[v]"]
    else:
        args+=["-vf",f"scale={W}:{H}:flags=lanczos,format=yuv420p","-map","0:v"]
    args+=["-map","0:a","-shortest","-r","30000/1001","-c:v","libx264","-preset","fast","-crf","16","-c:a","pcm_s16le","-t",f"{d:.3f}",f]
    subprocess.run(args,check=True)
open(f"{tmp}/list.txt","w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in lst))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{tmp}/list.txt","-c","copy",out],check=True)
