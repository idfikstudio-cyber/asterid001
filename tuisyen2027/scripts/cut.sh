#!/bin/bash
# Potong pause + take berulang, grade warna, bersihkan audio.
# Guna: cut.sh <src.mp4> <workdir>
set -e
SRC=$1; W=$2; mkdir -p $W/frames
# segmen sumber (saat): take kedua senarai subjek dikekalkan, take pertama (3.98-8.52) dan ekor (17.92-) dibuang
SEGS="0.00:1.56 1.78:3.98 8.52:11.30 11.62:16.10 16.38:17.92"
GRADE="hqdn3d=1.2:1.2:3:3,scale=1080:1920:flags=lanczos,curves=all='0/0 0.12/0.13 0.35/0.41 0.6/0.66 0.85/0.88 1/0.97',eq=contrast=1.04:saturation=1.08,colorbalance=rs=0.01:bs=-0.01:rh=-0.01:bh=0.01,unsharp=5:5:0.5:5:5:0.0"
V="";A="";n=0;FC=""
for s in $SEGS; do a=${s%:*}; b=${s#*:}; d=$(python3 -c "print($b-$a)")
  FC+="[0:v]trim=$a:$b,setpts=PTS-STARTPTS[v$n];[0:a]atrim=$a:$b,asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st=$(python3 -c "print($d-0.012)"):d=0.012[a$n];"
  V+="[v$n][a$n]"; n=$((n+1)); done
FC+="${V}concat=n=$n:v=1:a=1[cv][ca];[cv]fps=30000/1001,$GRADE[gv];"
FC+="[ca]highpass=f=80,afftdn=nr=10:nf=-50,equalizer=f=280:t=q:w=1.2:g=-2.5,equalizer=f=3800:t=q:w=1.5:g=2.5,equalizer=f=9000:t=h:w=2000:g=1.5,deesser=i=0.35,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[aa]"
ffmpeg -v error -y -i $SRC -filter_complex "$FC" -map "[gv]" -q:v 2 $W/frames/%04d.jpg -map "[aa]" -ac 2 $W/voice.wav
ls $W/frames | wc -l; ffprobe -v error -show_entries format=duration -of csv=p=0 $W/voice.wav
