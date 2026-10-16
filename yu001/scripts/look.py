# Grade + relight + bokeh for YU001.  usage: look.py in.mp4 model.tflite out.mp4 [W H] [--frames t1,t2 outdir]
import sys,subprocess,numpy as np,cv2,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
src,model,out=sys.argv[1:4];W,H=1080,1920
OW,OH=(int(sys.argv[4]),int(sys.argv[5])) if len(sys.argv)>5 and not sys.argv[4].startswith("--") else (W,H)
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=model),output_confidence_masks=True))
def disc(r):
    k=np.zeros((2*r+1,2*r+1),np.float32);cv2.circle(k,(r,r),r,1,-1,cv2.LINE_AA);return k/k.sum()
K=disc(7)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32);vig=1-0.22*np.clip(((xx/W-.5)**2*1.6+(yy/H-.45)**2)*2.2,0,1)**1.4
def curve(x):  # gentle S with highlight roll-off (keeps skin from clipping)
    x=np.clip(x,0,1);s=x+0.06*np.sin(2*np.pi*x)*(1-x)*1.2  # mild contrast
    return 1-(1-s)**1.04*0.985+0.0  # tiny lift of blacks handled below
prev=None
def frame(img):
    global prev
    rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb)))
    m=1-r.confidence_masks[0].numpy_view().astype(np.float32)   # person prob
    m=cv2.resize(m,(W,H));prev=m if prev is None else 0.6*m+0.4*prev;m=prev
    m=cv2.GaussianBlur(np.clip((m-0.35)/0.4,0,1),(0,0),2.5)
    f=img.astype(np.float32)/255
    # ---- bokeh: mask-normalised disc blur at 1/4 res so the person doesn't bleed into the background
    sw,sh=W//4,H//4;fs=cv2.resize(f,(sw,sh),interpolation=cv2.INTER_AREA);bs=cv2.resize(1-m,(sw,sh))[...,None]
    hl=np.clip((fs.max(2,keepdims=True)-0.72)*3,0,1)       # boost highlights so they bloom into discs
    num=cv2.filter2D(fs*(1+1.5*hl)*bs,-1,K);den=cv2.filter2D(np.repeat(bs,3,2),-1,K)+1e-4
    bg=cv2.resize(np.clip(num/den,0,1.2),(W,H),interpolation=cv2.INTER_CUBIC)
    a=m[...,None];f=f*a+bg*(1-a)
    # ---- grade
    f=f[...,::-1]  # RGB
    f=f*np.array([0.975,1.0,1.03],np.float32)                 # neutralise the yellow room light
    lum=f@np.array([.2126,.7152,.0722],np.float32)
    lift=0.06*(1-lum)**2*a[...,0]                              # soft key: lift subject shadows/mids only
    f=f+lift[...,None]
    f=f*(1-0.10*(1-a))                                         # drop background ~10% for separation
    f=np.clip(f,0,1);f=f+0.05*np.sin(2*np.pi*f)*(1-f)          # mild S contrast
    f=np.where(f>0.85,0.85+(f-0.85)*0.6,f)                     # highlight roll-off (no blown skin)
    lum=(f@np.array([.2126,.7152,.0722],np.float32))[...,None]
    f=f+(1-lum)**3*np.array([-0.012,0.004,0.018])+lum**3*np.array([0.015,0.006,-0.012])  # teal shadows / warm highlights
    hsv_s=1.08;f=lum+(f-lum)*hsv_s
    f=f*vig[...,None]
    f=np.clip(f*0.985+0.012,0,1)                               # soft film black
    return cv2.cvtColor((f*255+0.5).astype(np.uint8),cv2.COLOR_RGB2BGR)
if "--frames" in sys.argv:
    ts=sys.argv[sys.argv.index("--frames")+1].split(",");od=sys.argv[sys.argv.index("--frames")+2]
    for t in ts:
        prev=None;cap=cv2.VideoCapture(src);cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000);_,im=cap.read()
        cv2.imwrite(f"{od}/before_{t}.jpg",im);cv2.imwrite(f"{od}/after_{t}.jpg",frame(im))
    sys.exit()
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{OW}x{OH}","-r","30","-i","-","-i",src,"-map","0:v","-map","1:a","-c:v","libx264","-crf","20","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",out],stdin=subprocess.PIPE)
n=0
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3:break
    o=frame(np.frombuffer(b,np.uint8).reshape(H,W,3))
    if (OW,OH)!=(W,H):o=cv2.resize(o,(OW,OH),interpolation=cv2.INTER_AREA)
    enc.stdin.write(o.tobytes());n+=1
    if n%100==0:print(n,flush=True)
enc.stdin.close();enc.wait();print("done",n)
