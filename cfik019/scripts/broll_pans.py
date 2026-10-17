# Renders the B-roll camera pans and the 3D still (+ pencil sketch) from Fi-K's aihouse 360 tours.
# usage: broll_pans.py scenes.json outdir [W H]
import sys,json,os
sys.path.insert(0,os.path.dirname(__file__))
import pano,numpy as np
from PIL import Image
sc=json.load(open(sys.argv[1]));out=sys.argv[2];W,H=(int(sys.argv[3]),int(sys.argv[4])) if len(sys.argv)>4 else (720,1280)
os.makedirs(out,exist_ok=True)
def S(project,title,nth=0):
    m=[s for s in sc if s["project"]==project and s["title"].strip()==title];return m[nth]
# name: (scene, (yaw,pitch,fov) start, end, seconds); yaw is relative to the tour's default heading
PANS={
 "living_banglo":(S("S156754984","Living"),(0,-4,80),(45,-3,70),2.0),
 "dining_banglo":(S("S156754984","living"),(222,-5,76),(262,-4,70),2.3),
 "kitchen_teres":(S("S160622290","dry kitchen"),(8,-4,76),(55,-3,70),2.4),
 "m_master":(S("S157125126","masterbed PROP."),(-12,-6,74),(10,-5,68),0.9),
 "m_kids":(S("S156754984","girlsroom"),(28,-6,74),(52,-5,68),0.9),
 "m_bath":(S("S156754984","master bath"),(35,-6,74),(70,-5,68),0.9),
 "m_condo":(S("S152542130","dining"),(-30,-5,74),(8,-4,68),0.9),
}
only=set(sys.argv[5:])
for name,(s,a,b,dur) in PANS.items():
    if only and name not in only: continue
    a=(s["hlookat"]+a[0],a[1],a[2]);b=(s["hlookat"]+b[0],b[1],b[2])
    pano.pan(s["dir"],a,b,dur,f"{out}/{name}.mp4",W=W,H=H);print("pan",name)
    Image.fromarray(pano.view(s["dir"],*a,W=W,H=H)).save(f"{out}/{name}.jpg",quality=82)  # poster frame
# 3D still for "3D yang tepat" + colour-dodge pencil sketch tinted Fi-K green on paper
s=S("S157125126","Living PROP.")
im=pano.view(s["dir"],s["hlookat"]-14,-4,74,W=W,H=H);Image.fromarray(im).save(f"{out}/render_living.jpg",quality=86)
from PIL import ImageOps,ImageFilter
g=ImageOps.grayscale(Image.fromarray(im));inv=ImageOps.invert(g).filter(ImageFilter.GaussianBlur(9))
a=np.asarray(g,float);bb=np.asarray(inv,float);d=np.clip(a*255/(255-bb+1e-3),0,255);d=np.clip((d-170)/85,0,1)**1.6
paper=np.array([244,239,231],float);ink=np.array([48,73,69],float)
Image.fromarray((ink+(paper-ink)*d[...,None]).astype("uint8")).save(f"{out}/render_living_sketch.jpg",quality=86)
print("stills done")
