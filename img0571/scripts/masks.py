import numpy as np,sys
from PIL import Image,ImageFilter
W,H=1080,1920;y,x=np.mgrid[0:H,0:W]/np.array([H,W])[:,None,None] if False else np.mgrid[0:H,0:W]
x=x/W;y=y/H
# key light: soft ellipse on face/upper torso (face ~x.45 y.42)
k=np.exp(-(((x-0.45)/0.22)**2+((y-0.45)/0.15)**2))
Image.fromarray((k*255).astype(np.uint8)).save(sys.argv[1]+"/keymask.png")
# vignette: 1 at edges
r=np.sqrt(((x-0.47)/0.62)**2+((y-0.48)/0.62)**2)
v=np.clip((r-0.55)/0.6,0,1)**1.6
Image.fromarray((v*255).astype(np.uint8)).save(sys.argv[1]+"/vigmask.png")
