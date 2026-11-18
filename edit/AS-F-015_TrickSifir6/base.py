"""Lapisan asas AS-F-015: latar hitam+kuning, papan B-roll (diselaras dgn suara), wajah dalam bulatan emas (dicerahkan).
python3 base.py <W> <out.mp4>"""
import sys,os,subprocess,cv2,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import timeline as T, facelib as F
W=int(sys.argv[1]);H=W*16//9;OUT=sys.argv[2];s=W/1080
RAW=f"{F.S}/dl/raw.mp4";BR=f"{F.S}/dl/broll.mp4"
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def bg():
    r=np.hypot((xx-W*.5)/W,(yy-H*.40)/H*1.0)
    base=np.clip(1-r*1.5,0,1)[...,None]
    c0=np.array([8,8,8],np.float32);c1=np.array([36,36,40],np.float32)
    im=c0+(c1-c0)*base
    return im
BG=bg()
GLOW=np.exp(-((xx-W*.5)**2+(yy-770*s)**2)/(2*(330*s)**2))[...,None]   # cahaya kuning lembut di belakang bulatan besar
YEL=np.array([31,210,255],np.float32)  # BGR #ffd21f
class Seq:
    def __init__(s_,p): s_.c=cv2.VideoCapture(p);s_.i=-1;s_.f=None
    def get(s_,i):
        while s_.i<i:
            ok,f=s_.c.read()
            if not ok:break
            s_.i+=1;s_.f=f
        return s_.f
raw=Seq(RAW);br=Seq(BR)
BR_BAD={65}
# digit "6" tulisan Cikgu (dari "36") untuk ganti "5" di 6x1
_c=cv2.VideoCapture(BR);_c.set(cv2.CAP_PROP_POS_FRAMES,int(T.BOARD6["src_t"]*30));_ok,_bf=_c.read();_c.release()
_x0,_y0,_x1,_y1=T.BOARD6["src"];_six=_bf[_y0-4:_y1+4,_x0-4:_x1+4].astype(np.float32)
_six=cv2.resize(_six,None,fx=T.BOARD6["scale"],fy=T.BOARD6["scale"],interpolation=cv2.INTER_CUBIC)
_sa=np.clip((_six.max(2,keepdims=True)-25)/120,0,1)
def blueish(f):
    hh=cv2.cvtColor(f,cv2.COLOR_BGR2HSV);return (hh[...,0]>95)&(hh[...,0]<135)&(hh[...,1]>60)&(hh[...,2]>50)
def fix6(f,bt):
    if bt<T.BOARD6["t0"]:return f
    f=f.copy();ex0,ey0,ex1,ey1=T.BOARD6["erase"];reg=f[ey0:ey1,ex0:ex1]
    m=cv2.dilate(blueish(reg).astype(np.uint8),np.ones((5,5),np.uint8))>0;reg[m]=0
    k=min(1.0,(bt-T.BOARD6["t0"])/(T.BOARD6["t1"]-T.BOARD6["t0"]))
    h,w=_six.shape[:2];cx,cy=T.BOARD6["dst_c"];px,py=int(cx-w/2),int(cy-h/2)
    a=_sa.copy();a[int(h*k):]=0                                   # muncul dari atas ke bawah seperti ditulis
    f[py:py+h,px:px+w]=(f[py:py+h,px:px+w]*(1-a)+_six*a).astype(np.uint8)
    return f
ff=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
N=int(round(T.DUR*30)) if len(sys.argv)<4 else int(sys.argv[3])
thumb=None
cap=cv2.VideoCapture(RAW);cap.set(cv2.CAP_PROP_POS_FRAMES,int(T.THUMB_SRC*30));ok,thumbf=cap.read();cap.release()
bx,by,bw,bh=T.BCROP;PW,PH=int(bw*T.BSCALE*s),int(bh*T.BSCALE*s);PX,PY=int(T.BPOS[0]*s),int(T.BPOS[1]*s)
for n in range(N):
    t=n/30;src=T.o2s(t)
    if t>=T.DUR-T.END: src=None
    im=BG.copy()
    p=T.phase(src) if t>=T.THUMB else 0.0
    if t<T.DUR-T.END:
        im=im*(1-0.0*GLOW)+YEL*0.10*GLOW*(1-p)
        # papan
        if p>0.001:
            bi=int(round(T.board(src)*30))
            if bi in BR_BAD: bi-=1                      # frame rosak (papan kosong sekejap) dalam rakaman skrin asal
            bf=fix6(br.get(bi),bi/30)
            pan=cv2.resize(bf[by:by+bh,bx:bx+bw],(PW,PH),interpolation=cv2.INTER_AREA).astype(np.float32)
            reg=im[PY:PY+PH,PX:PX+PW]
            im[PY:PY+PH,PX:PX+PW]=reg*(1-p)+pan*p
        # wajah dalam bulatan
        fs=thumbf if src is None else raw.get(int(round(src*30)))
        fsrc=T.THUMB_SRC if src is None else src
        cx,cy,d=T.circle(src);cx,cy,d=cx*s,cy*s,d*s
        R=int(d/2);_,g=F.crop(fs,fsrc,zoom=T.zoom(src),out=2*R)
        ring=max(2,int(round(d*0.035)));P=ring+int(30*s)
        cxi,cyi=int(round(cx)),int(round(cy))
        x0,y0,x1,y1=max(cxi-R-P,0),max(cyi-R-P,0),min(cxi+R+P,W),min(cyi+R+P,H)
        dd=np.hypot(xx[y0:y1,x0:x1]-cxi,yy[y0:y1,x0:x1]-cyi)
        reg=im[y0:y1,x0:x1]
        sh=np.clip((R+ring+18*s-dd)/(26*s),0,1)[...,None]*0.55
        reg=reg*(1-sh)
        rm=np.clip(R+ring-dd+0.5,0,1)[...,None]
        reg=reg*(1-rm)+YEL*rm
        gi=np.zeros((y1-y0,x1-x0,3),np.float32)
        fx0,fy0=cxi-R-x0,cyi-R-y0
        gy0,gx0=max(fy0,0),max(fx0,0);gy1,gx1=min(fy0+2*R,y1-y0),min(fx0+2*R,x1-x0)
        gi[gy0:gy1,gx0:gx1]=g[gy0-fy0:gy1-fy0,gx0-fx0:gx1-fx0]
        fm=np.clip(R-dd+0.5,0,1)[...,None]
        reg=reg*(1-fm)+gi*fm
        im[y0:y1,x0:x1]=reg
    ff.stdin.write(np.clip(im,0,255).astype(np.uint8).tobytes())
    if n%300==0: print(n,N,flush=True)
ff.stdin.close();ff.wait()
