# Renders perspective views and slow camera pans from Fi-K's aihouse 360 tours (krpano cube faces l,f,r,b,u,d).
# view(): one frame; pan(): an mp4 clip with eased yaw/pitch/fov moves, so B-roll has real camera motion.
import numpy as np, os, sys, json, subprocess
from PIL import Image
_cache={}
def faces(d):
    if d not in _cache: _cache.clear();_cache[d]={f:np.asarray(Image.open(f"{d}/{f}.jpg").convert("RGB"),np.float32) for f in "lfrbud"}
    return _cache[d]
def view(d,yaw,pitch,fov,W=720,H=1280):
    F=faces(d);N=F["f"].shape[0]
    # camera rays: x right, y up, z forward; fov is horizontal, degrees
    t=np.tan(np.radians(fov)/2);xs=(np.arange(W)+.5)/W*2-1;ys=1-(np.arange(H)+.5)/H*2
    x,y=np.meshgrid(xs*t,ys*t*H/W);z=np.ones_like(x)
    p,q=np.radians(pitch),np.radians(yaw)
    y2=y*np.cos(p)+z*np.sin(p);z2=-y*np.sin(p)+z*np.cos(p);x2=x
    x3=x2*np.cos(q)+z2*np.sin(q);z3=-x2*np.sin(q)+z2*np.cos(q);y3=y2
    ax,ay,az=np.abs(x3),np.abs(y3),np.abs(z3);out=np.zeros((H,W,3),np.float32)
    sel={"f":(az>=ax)&(az>=ay)&(z3>0),"b":(az>=ax)&(az>=ay)&(z3<=0),"r":(ax>az)&(ax>=ay)&(x3>0),"l":(ax>az)&(ax>=ay)&(x3<=0),
         "u":(ay>ax)&(ay>az)&(y3>0),"d":(ay>ax)&(ay>az)&(y3<=0)}
    for f,m in sel.items():
        X,Y,Z=x3[m],y3[m],z3[m]
        if f=="f": u,v=X/Z,-Y/Z
        elif f=="b": u,v=X/Z,Y/Z*1  ;
        if f=="b": u,v=-X/-Z,-Y/-Z
        elif f=="r": u,v=-Z/X,-Y/X
        elif f=="l": u,v=Z/-X,-Y/-X
        elif f=="u": u,v=X/Y,Z/Y
        elif f=="d": u,v=X/-Y,-Z/-Y
        px=np.clip((u+1)/2*N-.5,0,N-1.001);py=np.clip((v+1)/2*N-.5,0,N-1.001)
        x0=px.astype(int);y0=py.astype(int);fx=(px-x0)[:,None];fy=(py-y0)[:,None];I=F[f]
        out[m]=(I[y0,x0]*(1-fx)*(1-fy)+I[y0,x0+1]*fx*(1-fy)+I[y0+1,x0]*(1-fx)*fy+I[y0+1,x0+1]*fx*fy)
    return out.clip(0,255).astype(np.uint8)
def ease(x): return x*x*(3-2*x)
def pan(d,a,b,dur,path,fps=30,W=720,H=1280,crf=21):
    """a,b = (yaw,pitch,fov) start/end; eased move"""
    n=int(round(dur*fps))
    pr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
        "-c:v","libx264","-preset","slow","-crf",str(crf),"-pix_fmt","yuv420p","-g","15","-movflags","+faststart",path],stdin=subprocess.PIPE)
    for i in range(n):
        k=ease(i/max(1,n-1));v=[a[j]+(b[j]-a[j])*k for j in range(3)]
        pr.stdin.write(view(d,*v,W=W,H=H).tobytes())
    pr.stdin.close();pr.wait()
if __name__=="__main__":
    # contact sheet: each scene at its default heading, 4 headings
    sc=json.load(open(sys.argv[1]));out=sys.argv[2];os.makedirs(out,exist_ok=True)
    for i,s in enumerate(sc):
        tiles=[view(s["dir"],s["hlookat"]+o,0,90,W=180,H=320) for o in (0,90,180,270)]
        Image.fromarray(np.hstack(tiles)).save(f"{out}/{i:02d}.jpg",quality=80)
