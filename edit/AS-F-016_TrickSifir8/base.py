"""Lapisan asas AS-F-016: talking head penuh (punch-in ikut muka) <-> skrin terbelah (papan B-roll atas, Cikgu bawah).
python3 base.py <W> <out.mp4> [n_frames]"""
import sys,os,json,subprocess,cv2,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import timeline as T
WD="/tmp/claude-0/-home-user-asterid001/58f87d4b-48fa-5a83-9e41-2c541a3f1986/scratchpad/a16"
W=int(sys.argv[1]);H=W*16//9;OUT=sys.argv[2];s=W/1080
_f=np.array(json.load(open(f"{HERE}/face.json")));_t=np.arange(0,54.5,1/30)
FX=np.interp(_t,_f[:,0],_f[:,1]);FY=np.interp(_t,_f[:,0],_f[:,2]);k=np.ones(45)/45
FX=np.convolve(np.pad(FX,22,mode="edge"),k,"valid");FY=np.convolve(np.pad(FY,22,mode="edge"),k,"valid")
def fc(t): i=min(int(round(t*30)),len(FX)-1); return FX[i],FY[i]
LUT=np.clip(((np.arange(256)/255)**0.92*1.03-0.005)*255,0,255).astype(np.uint8)   # cerah & jelas sedikit
def grade(f):
    g=cv2.LUT(f,LUT).astype(np.float32);m=g.mean(2,keepdims=True)
    return np.clip(m+(g-m)*1.05,0,255).astype(np.uint8)
def full(f,t,z):
    fx,fy=fc(t);w,h=1080/z,1920/z
    x0=min(max(fx-0.5*w,0),1080-w);y0=min(max(fy-0.38*h,0),1920-h)
    M=np.float32([[z*s,0,-x0*z*s],[0,z*s,-y0*z*s]])
    return cv2.warpAffine(f,M,(W,H),flags=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
def split(f,bf,t):
    im=np.zeros((H,W,3),np.uint8);im[:]=(10,10,10)
    bx,by,bw,bh=T.BCROP;PW,PH=int(bw*T.BSCALE*s),int(bh*T.BSCALE*s)
    im[int(T.BPOS[1]*s):int(T.BPOS[1]*s)+PH,int(T.BPOS[0]*s):int(T.BPOS[0]*s)+PW]=cv2.resize(bf[by:by+bh,bx:bx+bw],(PW,PH),interpolation=cv2.INTER_AREA)
    fx,fy=fc(t);ph=1920-T.DIV;x0=int(min(max(fx-540,0),0));y0=int(min(max(fy-330,0),1920-ph))
    bot=f[y0:y0+ph,0:1080]
    im[int(T.DIV*s):,:]=cv2.resize(bot,(W,H-int(T.DIV*s)),interpolation=cv2.INTER_AREA)
    return im
class Seq:
    def __init__(s_,p): s_.c=cv2.VideoCapture(p);s_.i=-1;s_.f=None
    def get(s_,i):
        while s_.i<i:
            ok,f=s_.c.read()
            if not ok:break
            s_.i+=1;s_.f=f
        return s_.f
raw=Seq(f"{WD}/dl/raw.mp4");br=Seq(f"{WD}/dl/broll.mp4")
c=cv2.VideoCapture(f"{WD}/dl/raw.mp4");c.set(cv2.CAP_PROP_POS_FRAMES,int(T.THUMB_SRC*30));_,thumbf=c.read();c.release()
ff=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
N=int(round(T.DUR*30)) if len(sys.argv)<4 else int(sys.argv[3])
last=None
for n in range(N):
    t=n/30;src=T.o2s(t)
    if t>=T.DUR-T.END:
        im=last if last is not None else np.zeros((H,W,3),np.uint8)
    else:
        f=thumbf if src is None else raw.get(int(round(src*30)))
        ts=T.THUMB_SRC if src is None else src
        f=grade(f);p=T.phase(src)
        A=full(f,ts,T.zoom(src)) if p<0.999 else None
        if p>0.001:
            B=split(f,br.get(int(round(T.board(src)*30))),ts)
            im=B if A is None else (A*(1-p)+B*p).astype(np.uint8)
        else: im=A
        last=im
    ff.stdin.write(im.tobytes())
    if n%300==0: print(n,N,flush=True)
ff.stdin.close();ff.wait()
