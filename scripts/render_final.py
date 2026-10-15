# usage: render_final.py <adudu1|adudu2> base.mkv pagedir out.mp4 [port]
# pagedir holds the preview page (index.html, <id>/plan.json, sfx/*.wav). The page runs in render mode
# (?render=<id>): every frame it lays out the overlay at time t with all CSS animations pinned to t, and
# Chromium screenshots it with a transparent background. Each frame of base.mkv is zoomed exactly like the
# preview (scale about 50%/oy%), the overlay is alpha-blended on top, and the SFX are mixed under the voice.
import json,os,subprocess,sys,threading,http.server,functools
import numpy as np,cv2
from playwright.sync_api import sync_playwright
vid,base,pagedir,out=sys.argv[1:5];port=int(sys.argv[5]) if len(sys.argv)>5 else 8790
plan=json.load(open(f"{pagedir}/{vid}/plan.json"));D=plan["duration"];FPS=30;N=int(round(D*FPS));W,H=1080,1920
tmp=out+".mix.wav"

# ---- audio: voice (already cleaned, -14 LUFS) + SFX at the preview's gains, limited to -1.5 dBTP
ins=["-i",base];fl=[]
for i,s in enumerate(plan["sfx"]):
    ins+=["-i",f"{pagedir}/sfx/{s['name']}.wav"];ms=int(round(s["t"]*1000))
    fl.append(f"[{i+1}:a]aresample=48000,aformat=channel_layouts=mono,volume={s['gain']*0.85:.3f},adelay={ms}:all=1[s{i}]")
mix="".join(f"[s{i}]" for i in range(len(plan["sfx"])))
fl.append(f"[0:a]aformat=channel_layouts=mono[v];[v]{mix}amix=inputs={len(plan['sfx'])+1}:normalize=0:duration=first,alimiter=limit=0.84:level=false,atrim=0:{D}[a]")
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",";".join(fl),"-map","[a]","-ac","2","-ar","48000",tmp],check=True)

# ---- zoom curve, same easing as the page
Z=plan["zoom"]
def ease(x): return 2*x*x if x<.5 else 1-(-2*x+2)**2/2
def zoom(t):
    if t<=Z[0]["t"]: return Z[0]["scale"],Z[0]["oy"]
    for a,b in zip(Z,Z[1:]):
        if t<=b["t"]:
            k=ease((t-a["t"])/max(1e-3,b["t"]-a["t"]));return a["scale"]+(b["scale"]-a["scale"])*k,a["oy"]+(b["oy"]-a["oy"])*k
    return Z[-1]["scale"],Z[-1]["oy"]

# ---- static server for the page
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,".html":"text/html; charset=utf-8"}
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(("127.0.0.1",port),functools.partial(Q,directory=pagedir));threading.Thread(target=srv.serve_forever,daemon=True).start()

dec=subprocess.Popen(["ffmpeg","-v","error","-i",base,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",tmp,
    "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-r",str(FPS),
    "-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",out],stdin=subprocess.PIPE)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg=b.new_page(viewport={"width":W,"height":H},device_scale_factor=1)
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/index.html?render={vid}");pg.evaluate("window.__ready")
    last=None
    for i in range(N):
        t=i/FPS;raw=dec.stdout.read(W*H*3)
        if len(raw)<W*H*3: raw=last   # base ends a frame early: hold the last frame
        last=raw;f=np.frombuffer(raw,np.uint8).reshape(H,W,3)
        s,oy=zoom(t)
        if abs(s-1)>1e-4:
            cx,cy=W/2,H*oy/100;M=np.float32([[s,0,cx*(1-s)],[0,s,cy*(1-s)]])
            f=cv2.warpAffine(f,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
        pg.evaluate(f"window.__frame({t})")
        ov=cv2.imdecode(np.frombuffer(pg.screenshot(clip={"x":0,"y":0,"width":W,"height":H},omit_background=True,type="png"),np.uint8),cv2.IMREAD_UNCHANGED)
        a=ov[:,:,3:4].astype(np.float32)/255
        f=(f.astype(np.float32)*(1-a)+ov[:,:,:3].astype(np.float32)*a).astype(np.uint8)
        enc.stdin.write(f.tobytes())
        if i%300==0: print(f"{vid} {t:6.1f}/{D:.1f}s",flush=True)
    b.close()
enc.stdin.close();enc.wait();dec.kill();srv.shutdown();os.remove(tmp)
if errs: print("page errors:",errs[:5])
print("wrote",out,"rc",enc.returncode)
