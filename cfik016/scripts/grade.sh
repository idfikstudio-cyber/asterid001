# Mask input must be time-limited (-loop 1 -t DUR). Premium warm-neutral grade + face key light. Inputs: [0:v] video, [1:v] keymask.png (grey, 720x1280)
# Base: tame bright wall, deeper blacks, richer wood/skin, neutral whites, gentle vignette, light sharpen.
BASE="colorbalance=rs=-0.015:bs=0.02:rm=0.025:gm=0.005:bm=-0.025:rh=-0.01:bh=0.015,curves=all='0/0.0 0.08/0.05 0.3/0.27 0.55/0.55 0.8/0.78 0.93/0.88 1/0.95',eq=contrast=1.07:saturation=1.1:gamma=0.98"
KEY="eq=brightness=0.045:gamma=1.10:saturation=1.03"
GRADE_FC="[0:v]$BASE,split[b][k];[k]$KEY[kl];[1:v]scale=iw:ih,format=gray[m];[kl][m]alphamerge[ka];[b][ka]overlay=format=auto:shortest=1,vignette=a=PI/5.5,unsharp=5:5:0.45,format=yuv420p"
