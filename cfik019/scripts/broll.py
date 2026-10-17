# Prepares B-roll stills (Fi-K's own CFik017 "after" photos), a pencil-sketch version for the "3D" beat, and the logos.
import sys,os
from PIL import Image,ImageOps,ImageFilter,ImageChops
src,logos,out=sys.argv[1:4]
PICK={"dining":"[After1] Dinning Area.jpg","family":"[After 1] Family Area.jpg","kitchen":"Dry Kitchen.jpg","toilet":"Toilet.jpg"}
for k,f in PICK.items():
    im=ImageOps.fit(Image.open(os.path.join(src,f)).convert("RGB"),(720,1280),Image.LANCZOS)
    im.save(f"{out}/broll/{k}.jpg",quality=86,optimize=True,progressive=True)
    if k=="dining":  # colour-dodge pencil sketch, tinted Fi-K green on paper
        g=ImageOps.grayscale(im);inv=ImageOps.invert(g).filter(ImageFilter.GaussianBlur(9))
        import numpy as np
        a=np.asarray(g,float);b=np.asarray(inv,float);d=np.clip(a*255/(255-b+1e-3),0,255)
        d=np.clip((d-170)/(255-170),0,1)**1.6
        paper=np.array([244,239,231],float);ink=np.array([48,73,69],float)
        rgb=(ink+(paper-ink)*d[...,None]).astype("uint8")
        Image.fromarray(rgb).save(f"{out}/broll/dining_sketch.jpg",quality=86,optimize=True,progressive=True)
for n in ("White","Green"):
    im=Image.open(os.path.join(logos,f"Logo {n}.png"));im=im.crop(im.getbbox());im.thumbnail((480,480),Image.LANCZOS)
    im.save(f"{out}/logo-{n.lower()}.png",optimize=True)
print(sorted(os.listdir(out+"/broll")))
