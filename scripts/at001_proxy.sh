#!/bin/bash
# Build 540p preview proxies for AT001 from plan.json cuts.
# usage: at001_proxy.sh source.mp4 look_full.mp4 plan.json outdir look_nobokeh.mp4 cover.png
# the cover is held for plan.thumb seconds in front of the talking (silent), then the edit follows
set -e
SRC=$1 LOOK=$2 PLAN=$3 OUT=$4 LOOK_NB=$5 COVER=$6
mkdir -p "$OUT"
read -r END_CARD THUMB <<<"$(python3 -c "import json;p=json.load(open('$PLAN'));print(round(p['total']-p['duration'],3),p.get('thumb',0))")"
TH_MS=$(python3 -c "print(int($THUMB*1000))")
# cover as a $THUMB s clip at 540x960/30fps, joined in front of every proxy
ffmpeg -v error -y -loop 1 -framerate 30 -t "$THUMB" -i "$COVER" -vf "scale=540:960:flags=lanczos,format=yuv420p" -c:v libx264 -crf 18 "$OUT/.cover.mp4"
# trim+concat filter for N cuts; 8 ms audio fades at every join so cuts don't click
FC=$(python3 - "$PLAN" <<'EOF'
import json,sys
c=json.load(open(sys.argv[1]))["cuts"];v=a=""
for i,x in enumerate(c):
    s,e=x["src_in"],x["src_out"]
    v+=f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];"
    a+=f"[1:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={e-s-0.008:.3f}:d=0.008[a{i}];"
n=len(c)
print(v+a+"".join(f"[v{i}]" for i in range(n))+f"concat=n={n}:v=1:a=0[vc];"+"".join(f"[a{i}]" for i in range(n))+f"concat=n={n}:v=0:a=1[ac]")
EOF
)
# voice clean-up: rumble cut, light denoise, less mud, more presence, de-ess, gentle compression, -14 LUFS
VOICE="highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=44100"
ffmpeg -v error -y -i "$LOOK" -i "$SRC" -i "$OUT/.cover.mp4" -filter_complex "$FC;[vc]tpad=stop_mode=clone:stop_duration=$END_CARD,scale=540:960:flags=lanczos,fps=30,setsar=1[vb];[2:v]setsar=1[cv];[cv][vb]concat=n=2:v=1:a=0[v];[ac]$VOICE,adelay=$TH_MS:all=1,apad=pad_dur=$END_CARD[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 23 -g 15 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$OUT/graded.mp4"
ffmpeg -v error -y -i "$LOOK_NB" -i "$SRC" -i "$OUT/.cover.mp4" -filter_complex "$FC;[vc]tpad=stop_mode=clone:stop_duration=$END_CARD,scale=540:960:flags=lanczos,fps=30,setsar=1[vb];[2:v]setsar=1[cv];[cv][vb]concat=n=2:v=1:a=0[v];[ac]$VOICE,adelay=$TH_MS:all=1,apad=pad_dur=$END_CARD[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 23 -g 15 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$OUT/graded_nb.mp4"
ffmpeg -v error -y -i "$SRC" -i "$SRC" -i "$OUT/.cover.mp4" -filter_complex "$FC;[vc]tpad=stop_mode=clone:stop_duration=$END_CARD,scale=540:960:flags=lanczos,fps=30,setsar=1[vb];[2:v]setsar=1[cv];[cv][vb]concat=n=2:v=1:a=0[v];[ac]anullsink" \
  -map "[v]" -an -c:v libx264 -preset slow -crf 25 -g 15 -pix_fmt yuv420p -movflags +faststart "$OUT/orig.mp4"
# A/B of audio only (original vs cleaned), for the "Audio" tab
ffmpeg -v error -y -i "$SRC" -i "$SRC" -filter_complex "$FC;[vc]nullsink;[ac]adelay=$TH_MS:all=1[ad]" -map "[ad]" -c:a libmp3lame -b:a 128k "$OUT/audio_orig.mp3"
rm -f "$OUT/.cover.mp4"
ls -la "$OUT"
