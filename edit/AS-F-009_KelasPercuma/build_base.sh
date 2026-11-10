# usage: build_base.sh W out.mp4
S=/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad; cd $S
W=$1; H=$((W*16/9)); OUT=$2
GR="eq=brightness=0.02:contrast=1.06:saturation=1.06:gamma=1.04,colorbalance=rs=-0.03:bs=0.02:rm=-0.02:bm=0.01,curves=all='0/0.02 0.25/0.23 0.5/0.52 0.8/0.84 1/0.99'"
# zoom keyed on SOURCE time (video t - 1.0)
Z="if(lt(t,3.48),1.06,if(lt(t,5.08),1.11,if(lt(t,8.06),1.06,if(lt(t,11.06),1.15,if(lt(t,13.88),1.07,if(lt(t,16.9),1.1,if(lt(t,20.36),1.03,if(lt(t,23.36),1.12,1.05))))))))"
ffmpeg -v error -y -i raw/AS-F-009_KelasPercuma.mp4 -loop 1 -t 1.0 -framerate 30 -i work/thumbsrc.png -f lavfi -t 1.5 -i "color=c=black:s=${W}x${H}:r=30" -filter_complex "
[0:v]trim=0:25.95,setpts=PTS-STARTPTS,fps=30,$GR,scale=w='trunc(${W}*($Z)/2)*2':h=-2:eval=frame,crop=${W}:${H}:(iw-${W})/2:ih-${H},setsar=1,format=yuv420p[c];
[1:v]$GR,scale=$((W*112/100/2*2)):-2,crop=${W}:${H}:(iw-${W})/2:ih-${H},setsar=1,fps=30,format=yuv420p[t];
[2:v]setsar=1,format=yuv420p[e];
[t][c][e]concat=n=3:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 16 -preset fast -r 30 $OUT
