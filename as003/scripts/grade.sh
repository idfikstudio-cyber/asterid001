# Colour grade chains for As003 (portrait 1080x1920).
# Inputs: [0]=video  [1]=face key mask  [2]=vignette mask (grey, multiply).
# Look: clean neutral wall, soft S-curve, cool shadows / natural warm skin, gentle face key light, subtle vignette, light sharpen.
COMMON_PRE="curves=all='0/0.03 0.25/0.22 0.55/0.55 0.85/0.83 1/0.95',colorbalance=rs=-0.03:gs=-0.005:bs=0.035:rh=0.0:bh=-0.015"
# Clip A (IMG_0573): yellow-green wall, face darker than wall -> neutralise wall, stronger face key.
GRADE_A="$COMMON_PRE,colorbalance=rm=0.012:gm=-0.022:rh=0.015:gh=-0.018,eq=contrast=1.04:saturation=1.08,vibrance=intensity=0.12"
KEY_A="eq=gamma=1.22:saturation=1.06"
# Clip B (IMG_0575): skin too red/orange and face near clipping -> calm reds, face key pulls highlights DOWN, keep purple practical light.
GRADE_B="$COMMON_PRE,colorbalance=rm=-0.045:gm=0.005:bm=0.03,huesaturation=saturation=-0.18:colors=r+y,eq=contrast=1.04:gamma=0.99,vibrance=intensity=0.08"
KEY_B="curves=all='0/0 0.5/0.47 0.8/0.76 1/0.92'"
graph(){ # $1=grade chain  $2=key (face light) chain
  echo "[0:v]$1,split[g][g2];[g2]$2[b];[1:v]format=gray[m];[g][b][m]maskedmerge[l];[2:v]format=gray[v];[l]format=gbrp[lr];[v]format=gbrp[vr];[lr][vr]blend=all_mode=multiply,cas=0.35,format=yuv420p"
}
