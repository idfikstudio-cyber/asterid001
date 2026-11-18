S=/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad/a10; cd $S
W=$1; H=$((W*16/9)); OUT=$2
GR="eq=brightness=0.02:contrast=1.06:saturation=1.06:gamma=1.04,colorbalance=rs=-0.03:bs=0.02:rm=-0.02:bm=0.01,curves=all='0/0.02 0.25/0.23 0.5/0.52 0.8/0.84 1/0.99'"
# zoom keyed on CONTENT time (video t - 1)
Z="$(python3 -I -c "
K=[(1.0,1.06),(3.52,1.12),(6.47,1.06),(9.37,1.13),(12.37,1.06),(14.47,1.12),(17.99,1.06),(19.36,1.14),(22.64,1.06),(26.30,1.11),(29.82,1.05),(35.16,1.13),(38.70,1.06),(40.26,1.12),(43.30,1.06)]
e=str(K[-1][1])
for i in range(len(K)-1,0,-1): e=f'if(lt(t,{K[i][0]-1:.2f}),{K[i-1][1]},{e})'
print(e)")"
ffmpeg -v error -y -i raw.mp4 -loop 1 -t 1.0 -framerate 30 -i work/thumbsrc.png -f lavfi -t 1.5 -i "color=c=black:s=${W}x${H}:r=30" -filter_complex "
[0:v]split=3[v1][v2][v3];
[v1]trim=0:2.52,setpts=PTS-STARTPTS[a];[v2]trim=2.89:17.36,setpts=PTS-STARTPTS[b];[v3]trim=17.77:44.60,setpts=PTS-STARTPTS[c];
[a][b][c]concat=n=3:v=1:a=0,fps=30,$GR,scale=w='trunc(${W}*($Z)/2)*2':h=-2:eval=frame,crop=${W}:${H}:(iw-${W})/2:ih-${H},setsar=1,format=yuv420p[ct];
[1:v]$GR,scale=$((W*112/100/2*2)):-2,crop=${W}:${H}:(iw-${W})/2:ih-${H},setsar=1,fps=30,format=yuv420p[t];
[2:v]setsar=1,format=yuv420p[e];
[t][ct][e]concat=n=3:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 16 -preset fast -r 30 $OUT
