#!/bin/sh
# usage: cut.sh SRC.MOV edl.json OUT.mp4 [vf]   -> cut timeline (audio 15ms fades at each join)
SRC=$1; EDL=$2; OUT=$3; VF=${4:-null}
FC=$(python3 - "$EDL" "$VF" <<'P'
import json,sys
s=json.load(open(sys.argv[1]))["segments"];f=[];c=""
for i,g in enumerate(s):
    a,b=g["src_in"],g["src_out"];d=b-a
    f.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
    f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d-0.015:.3f}:d=0.015[a{i}]")
    c+=f"[v{i}][a{i}]"
f.append(f"{c}concat=n={len(s)}:v=1:a=1[cv][ca]");f.append(f"[cv]{sys.argv[2]}[vo]")
print(";".join(f))
P
)
ffmpeg -v error -y -i "$SRC" -filter_complex "$FC" -map "[vo]" -map "[ca]" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$OUT"
