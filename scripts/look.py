# Bokeh (f/2.8 look) + skin-protected colour grade, frame by frame.
# usage: python3 look.py in.mp4 selfie_multiclass_256x256.tflite out.mp4 [scale]
# classes of the multiclass model: 0 bg, 1 hair, 2 body-skin, 3 face-skin, 4 clothes, 5 others
import sys,subprocess,json,cv2,numpy as np,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
src,model,dst=sys.argv[1:4];sc=float(sys.argv[4]) if len(sys.argv)>4 else 1.0
pr=json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,r_frame_rate","-of","json",src]))["streams"][0]
W,H=int(pr["width"]*sc)//2*2,int(pr["height"]*sc)//2*2;fps=pr["r_frame_rate"]
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf",f"scale={W}:{H}:flags=lanczos","-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",fps,"-i","-",
  "-vf","unsharp=5:5:0.35:5:5:0","-c:v","libx264","-preset","medium","-crf","15","-pix_fmt","yuv420p",dst],stdin=subprocess.PIPE)
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=model),output_confidence_masks=True))

# --- lens: disc kernel with slightly bright rim (cat-eye-free), radius ~ f/2.8 at this distance
R=max(5,int(13*W/1080));k=2*R+1;yy,xx=np.mgrid[-R:R+1,-R:R+1];rr=np.sqrt(xx**2+yy**2)
disc=np.clip(R+.5-rr,0,1)*(1+.25*(rr/R)**4);disc=(disc/disc.sum()).astype(np.float32)
# --- grade constants (BGR order)
WB=np.array([1.13,1.00,0.95],np.float32)   # neutralise tungsten cast on wall (136,118,93 -> ~ 130,118,105)
SKIN_WB=.30                                 # skin only gets 30% of the correction: keeps natural warmth
lut=np.clip(np.interp(np.arange(256)/255,[0,.06,.25,.5,.75,.92,1],[.02,.055,.25,.535,.79,.935,.985]),0,1).astype(np.float32)  # lift + soft S
yv,xv=np.mgrid[0:H,0:W];vig=(1-.16*np.clip(((xv/W-.5)**2/.30+(yv/H-.42)**2/.42)-.25,0,1)).astype(np.float32)[...,None]
ema=None;n=0
while True:
    raw=dec.stdout.read(W*H*3)
    if len(raw)<W*H*3:break
    img=np.frombuffer(raw,np.uint8).reshape(H,W,3)
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(img[...,::-1])))
    cm=[np.squeeze(c.numpy_view()).astype(np.float32) for c in r.confidence_masks]  # 6 x 256x256
    ema=cm if ema is None else [.55*a+.45*b for a,b in zip(cm,ema)]                             # temporal smoothing: no edge flicker
    m=[cv2.resize(x,(W,H),interpolation=cv2.INTER_LINEAR) for x in ema]
    person=cv2.GaussianBlur(np.clip(1-m[0],0,1),(0,0),2.2*W/1080)
    skin=cv2.GaussianBlur(np.clip(m[2]+m[3],0,1),(0,0),4*W/1080)[...,None]
    face=cv2.GaussianBlur(m[3],(0,0),40*W/1080)[...,None]
    f=img.astype(np.float32)/255
    # white balance with skin protection
    g=1+(WB-1)*(1-skin*(1-SKIN_WB));f=f*g
    # tone curve on luma, keep chroma ratio
    Y=f@np.array([.114,.587,.299],np.float32);Yn=np.interp(np.clip(Y,0,1),np.linspace(0,1,256),lut).astype(np.float32)
    f=f*(Yn/np.maximum(Y,1e-4))[...,None]
    # saturation: +8% on scene, skin untouched
    Y=(f@np.array([.114,.587,.299],np.float32))[...,None];s=1+.08*(1-skin);f=Y+(f-Y)*s
    # soft key light on face (+6%)
    f=f*(1+.06*face)
    f=np.clip(f*vig,0,1)
    # bokeh: blur half-res, composite behind subject; light highlight bloom inside blur
    sm=cv2.resize(f,(W//2,H//2),interpolation=cv2.INTER_AREA)
    lin=sm**2.2;b=cv2.filter2D(lin,-1,disc)**(1/2.2)
    b=cv2.resize(b,(W,H),interpolation=cv2.INTER_LINEAR)
    p=person[...,None];out=f*p+b*(1-p)
    enc.stdin.write((np.clip(out,0,1)*255+.5).astype(np.uint8).tobytes());n+=1
    if n%60==0:print(n,"frames",flush=True)
enc.stdin.close();enc.wait();print("done",n)
