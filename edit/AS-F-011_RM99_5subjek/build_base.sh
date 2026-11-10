S=/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad/a11; cd $S
W=$1; H=$((W*16/9)); OUT=$2
GR="eq=brightness=0.02:contrast=1.06:saturation=1.06:gamma=1.04,colorbalance=rs=-0.03:bs=0.02:rm=-0.02:bm=0.01,curves=all='0/0.02 0.25/0.23 0.5/0.52 0.8/0.84 1/0.99'"
Z="$(python3 -I -c "
K=[(1.0,1.06),(4.6,1.12),(8.12,1.05),(13.56,1.12),(16.86,1.06),(19.80,1.04),(21.04,1.12)]
e=str(K[-1][1])
for i in range(len(K)-1,0,-1): e=f'if(lt(t,{K[i][0]-1:.2f}),{K[i-1][1]},{e})'
print(e)")"
ffmpeg -v error -y -i raw.mp4 -loop 1 -t 1.0 -framerate 30 -i work/thumbsrc.png -f lavfi -t 1.5 -i "color=c=black:s=${W}x${H}:r=30" -filter_complex "
[0:v]trim=0:21.5,setpts=PTS-STARTPTS,fps=30,$GR,scale=w='trunc(${W}*($Z)/2)*2':h=-2:eval=frame,crop=${W}:${H}:(iw-${W})/2:ih-${H},setsar=1,format=yuv420p[ct];
[1:v]$GR,scale=$((W*112/100/2*2)):-2,crop=${W}:${H}:(iw-${W})/2:ih-${H},setsar=1,fps=30,format=yuv420p[t];
[2:v]setsar=1,format=yuv420p[e];
[t][ct][e]concat=n=3:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 16 -preset fast -r 30 $OUT
