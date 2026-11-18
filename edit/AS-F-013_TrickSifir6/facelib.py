import cv2,json,numpy as np
S="/tmp/claude-0/-home-user-asterid001/58f87d4b-48fa-5a83-9e41-2c541a3f1986/scratchpad/a13"
import os
_f=np.array(json.load(open(os.path.join(os.path.dirname(__file__),"face.json"))))
_t=np.arange(0,76.4,1/30)
FX=np.interp(_t,_f[:,0],_f[:,1]);FY=np.interp(_t,_f[:,0],_f[:,2])
k=np.ones(45)/45
FX=np.convolve(np.pad(FX,22,mode="edge"),k,"valid");FY=np.convolve(np.pad(FY,22,mode="edge"),k,"valid")
FW=float(np.median(_f[:,3]))
def center(ts):
    i=min(int(round(ts*30)),len(FX)-1);return FX[i],FY[i]
def grade(x):
    # cerahkan wajah: angkat bayang/midtone, kekal hue kulit
    f=x.astype(np.float32)/255
    lab=cv2.cvtColor(f,cv2.COLOR_BGR2Lab)
    L=lab[...,0]/100
    L=np.clip(L,0,1)**0.66                       # angkat midtone
    L=np.clip((L-0.5)*1.06+0.5+0.015,0,1)        # kontras ringan
    lab[...,0]=L*100
    lab[...,1]*=1.04;lab[...,2]*=1.04             # sedikit lebih segar, hue sama
    o=cv2.cvtColor(lab,cv2.COLOR_Lab2BGR)
    return (np.clip(o,0,1)*255+.5).astype(np.uint8)
def crop(frame,ts,zoom=1.0,out=600):
    fx,fy=center(ts);S=2.15*FW/zoom
    cx=fx;cy=fy+0.16*S
    x0=int(round(min(max(cx-S/2,0),1080-S)));y0=int(round(min(max(cy-S/2,0),1920-S)))
    c=frame[y0:y0+int(S),x0:x0+int(S)]
    c=cv2.resize(c,(out,out),interpolation=cv2.INTER_AREA)
    # lampu muka lembut (radial) supaya wajah lebih hidup
    c2=cv2.bilateralFilter(c,7,22,7);c2=cv2.addWeighted(c,0.45,c2,0.55,0)
    g=grade(c2)
    yy,xx=np.mgrid[0:out,0:out]/out
    m=np.exp(-(((xx-0.5)/0.28)**2+((yy-0.40)/0.30)**2))[...,None]
    g=np.clip(g.astype(np.float32)*(1+0.14*m)+9*m,0,255).astype(np.uint8)
    return c,g
