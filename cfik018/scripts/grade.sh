# Colour grade for CFik018 (IMG_1472.MOV, 720x1280, warm tungsten office).
# Inputs: [0]=video  [1]=face key mask  [2]=vignette mask (grey, multiply), all 720x1280.
# Look: correct the orange cast toward neutral-warm (light-blue shirt reads blue again), richer blacks,
# soft S-curve, keep skin warm and natural, gentle face key, subtle vignette, light sharpen.
GRADE_A="colorchannelmixer=rr=0.87:gg=0.975:bb=1.11,curves=all='0/0.02 0.2/0.17 0.5/0.52 0.8/0.84 1/0.97',eq=contrast=1.04:saturation=1.0"
KEY_A="eq=gamma=1.20:saturation=1.03"
graph(){ # $1=grade chain  $2=key (face light) chain
  echo "[0:v]format=gbrp,$1,format=gbrp,split[g][g2];[g2]$2,format=gbrp[b];[1:v]format=gbrp[m];[g][b][m]maskedmerge[l];[2:v]format=gray[v];[l]format=gbrp[lr];[v]format=gbrp[vr];[lr][vr]blend=all_mode=multiply,cas=0.4,format=yuv420p"
}
