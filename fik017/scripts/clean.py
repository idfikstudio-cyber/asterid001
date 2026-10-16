# Colour CLEAN only (no grade): neutralise colour cast measured on near-neutral bright pixels,
# then a gentle 0.3%/99.7% levels stretch. Hue/saturation/contrast curve of the design untouched.
import sys,glob,os,json
import numpy as np
from PIL import Image, ImageOps
src,dst=sys.argv[1],sys.argv[2]
names={
 "Client.jpg":"client","Dry Kitchen.jpg":"a_drykitchen","Toilet.jpg":"a_toilet",
 "[After 1] Family Area.jpg":"a_family1","[After 2] Family Area.jpg":"a_family2",
 "[After1] Dinning Area.jpg":"a_dining1","[After2] Dinning Area.jpg":"a_dining2","[After3] Dinning Area Another Angle.jpg":"a_dining3",
 "[Before 2] Dinning Area.jpg":"b_dining2","[Before 2] Toilet.jpg":"b_toilet2","[Before] Dinning Area.jpg":"b_dining",
 "[Before] Dry Kitchen Before.jpg":"b_drykitchen","[Before] Living Area.jpg":"b_living","[Before] Rest Area.jpg":"b_rest",
 "[Before] Toilet.jpg":"b_toilet","[Before] Wet Kitchen Before.jpg":"b_wetkitchen"}
log={}
for f,n in names.items():
    im=ImageOps.exif_transpose(Image.open(os.path.join(src,f))).convert("RGB")
    a=np.asarray(im).astype(np.float32)/255
    lum=a.mean(2); sat=a.max(2)-a.min(2)
    m=(lum>np.percentile(lum,60))&(lum<0.97)&(sat<0.12)
    g=a[m].mean(0) if m.sum()>500 else a.reshape(-1,3).mean(0)
    gain=g.mean()/g; # before photos: 60% toward neutral; finished design & 3D: 30% so warm lighting intended by the design stays
    gain=1+(gain-1)*(0.6 if n.startswith('b_') else 0.3)
    gain=np.clip(gain,0.94,1.06)
    b=a*gain
    lo=np.percentile(b,0.3); hi=np.percentile(b,99.7)
    b=np.clip((b-lo)/max(hi-lo,1e-3),0,1)
    out=Image.fromarray((b*255+.5).astype(np.uint8))
    out.save(os.path.join(dst,n+".jpg"),quality=90)
    im.save(os.path.join(dst,n+"_orig.jpg"),quality=90)
    log[n]={"src":f,"size":im.size,"wb_gain":[round(float(x),3) for x in gain],"levels":[round(float(lo),3),round(float(hi),3)]}
json.dump(log,open(os.path.join(dst,"clean_log.json"),"w"),indent=1)
for k,v in log.items(): print(k,v["size"],v["wb_gain"],v["levels"])
