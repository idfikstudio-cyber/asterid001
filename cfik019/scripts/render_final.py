# Final render of CFik019 at 1080x1920 / 30fps.
#   assets -> graded main-video frames, 3D pan frames and HD stills under <work>/hd/
#   audio  -> voice (cleaned, +intro silence) + music bed + SFX, mixed to -14 LUFS
#   frames -> draws every frame through preview/index.html#render (same code as the approved preview)
#   mux    -> H.264 + AAC mp4, plus the thumbnail JPG
# usage: render_final.py <step> <source video> <scenes.json> <cfik017 dir> <work dir> <out dir>
import sys,os,json,subprocess,shutil
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(HERE);sys.path.insert(0,HERE)
step,SRC,SCENES,C17,WORK,OUT=sys.argv[1:7]
P=json.load(open(f"{ROOT}/edit/plan.json"));FPS=30;W,H=1080,1920
TOTAL=P["duration"]+P["outro"];NF=int(round(TOTAL*FPS))
HD=f"{WORK}/hd";os.makedirs(HD,exist_ok=True);os.makedirs(OUT,exist_ok=True)
VOICE=("highpass=f=80,afftdn=nr=8:nf=-42,deesser=i=0.3,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,"
       "equalizer=f=3200:t=q:w=1.2:g=2,loudnorm=I=-15:TP=-1.5:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
def run(c): subprocess.run(c,check=True)
def pan_frames():
    import pano,broll_pans
    sc=json.load(open(SCENES));out={}
    for name,(s,a,b,dur) in broll_pans.pans(sc).items():
        a=(s["hlookat"]+a[0],a[1],a[2]);b=(s["hlookat"]+b[0],b[1],b[2]);n=int(round(dur*FPS))
        d=f"{HD}/pans/{name}";os.makedirs(d,exist_ok=True)
        from PIL import Image
        for i in range(n):
            k=pano.ease(i/max(1,n-1));v=[a[j]+(b[j]-a[j])*k for j in range(3)]
            p=f"{d}/{i+1:04d}.jpg"
            if not os.path.exists(p): Image.fromarray(pano.view(s["dir"],*v,W=W,H=H)).save(p,quality=95)
        Image.open(f"{d}/{n:04d}.jpg").save(f"{HD}/pans/{name}_end.jpg",quality=95)
        out[name]=n;print("pan",name,n,flush=True)
    json.dump(out,open(f"{HD}/pan_frames.json","w"))

if step=="assets":
    from proxy import GRADE
    os.makedirs(f"{HD}/main",exist_ok=True)
    fc=(f"[1]format=gbrp[m1];[2]format=gbrp[m2];[0:v]format=gbrp,{GRADE},format=gbrp,split[ga][gb];[gb]eq=brightness=0.05:gamma=1.12,format=gbrp[gbr];"
        f"[ga][gbr][m1]maskedmerge[gf];[gf]split[gc][gd];[gd]eq=brightness=-0.08,format=gbrp[gdk];[gdk][gc][m2]maskedmerge,"
        f"tpad=start_mode=clone:start_duration={P['intro']}:stop_mode=clone:stop_duration={P['outro']+1},fps={FPS},format=yuvj444p[v]")
    run(["ffmpeg","-v","error","-y","-i",SRC,"-i",f"{ROOT}/edit/facemask.png","-i",f"{ROOT}/edit/vigmask.png","-filter_complex",fc,
         "-map","[v]","-frames:v",str(NF),"-q:v","1",f"{HD}/main/%05d.jpg"])
    print("main frames",len(os.listdir(f"{HD}/main")),flush=True)
    pan_frames()
    # HD stills: "3D yang tepat" render + pencil sketch, and the finished-project photo
    import pano,broll_pans,numpy as np
    from PIL import Image,ImageOps,ImageFilter
    sc=json.load(open(SCENES));p,t,yaw,pitch,fov=broll_pans.RENDER_STILL
    s=[x for x in sc if x["project"]==p and x["title"].strip()==t][0]
    im=pano.view(s["dir"],s["hlookat"]+yaw,pitch,fov,W=W,H=H);Image.fromarray(im).save(f"{HD}/pans/render_living.jpg",quality=95)
    g=ImageOps.grayscale(Image.fromarray(im));inv=ImageOps.invert(g).filter(ImageFilter.GaussianBlur(13))
    a=np.asarray(g,float);bb=np.asarray(inv,float);d=np.clip(a*255/(255-bb+1e-3),0,255);d=np.clip((d-170)/85,0,1)**1.6
    paper=np.array([244,239,231],float);ink=np.array([48,73,69],float)
    Image.fromarray((ink+(paper-ink)*d[...,None]).astype("uint8")).save(f"{HD}/pans/render_living_sketch.jpg",quality=95)
    os.makedirs(f"{HD}/broll",exist_ok=True)
    ImageOps.fit(Image.open(os.path.join(C17,"[After 1] Family Area.jpg")).convert("RGB"),(W,H),Image.LANCZOS).save(f"{HD}/broll/family.jpg",quality=95)
    print("stills done")

elif step=="audio":
    A=f"{WORK}/audio";os.makedirs(A,exist_ok=True)
    run(["ffmpeg","-v","error","-y","-i",SRC,"-filter_complex",
         f"[0:a]{VOICE}[an];aevalsrc=0|0:s=48000:c=stereo:d={P['intro']}[sil];[sil][an]concat=n=2:v=0:a=1,apad=whole_dur={TOTAL}[o]",
         "-map","[o]","-c:a","pcm_s16le",f"{A}/voice.wav"])
    run(["python3",f"{HERE}/sfx.py",f"{A}","%.2f"%TOTAL])  # music bed at the full length (SFX themselves come from preview/sfx)
    ins=["-i",f"{A}/voice.wav","-i",f"{A}/music.wav"];fc=["[1:a]volume=0.16[mus]"];tags=["[0:a]","[mus]"]
    for i,x in enumerate(P["sfx"]):
        ins+=["-i",f"{ROOT}/preview/sfx/{x['name']}.wav"];ms=int(round(x["t"]*1000))
        fc.append(f"[{i+2}:a]aresample=48000,volume={x['gain']},adelay={ms}|{ms}[s{i}]");tags.append(f"[s{i}]")
    fc.append("".join(tags)+f"amix=inputs={len(tags)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=9,aresample=48000,atrim=0:{TOTAL}[mix]")
    run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",";".join(fc),"-map","[mix]","-c:a","pcm_s16le",f"{A}/mix.wav"])
    print("audio mixed")

elif step=="frames":
    import asyncio,http.server,threading,functools
    pf=json.load(open(f"{HD}/pan_frames.json"))
    link=f"{ROOT}/preview/hd"
    if not os.path.islink(link): os.symlink(HD,link)
    os.makedirs(f"{WORK}/frames",exist_ok=True)
    srv=http.server.ThreadingHTTPServer(("127.0.0.1",8777),functools.partial(http.server.SimpleHTTPRequestHandler,directory=f"{ROOT}/preview"))
    srv.RequestHandlerClass.log_message=lambda *a:None
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    from playwright.async_api import async_playwright
    async def main():
        async with async_playwright() as p:
            b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
            pg=await b.new_page(viewport={"width":W,"height":H},device_scale_factor=1)
            errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
            await pg.goto("http://127.0.0.1:8777/index.html#render");await pg.wait_for_function("window.__renderFrame!==undefined")
            await pg.evaluate("document.fonts.ready");await pg.evaluate(f"window.__mainFrames={len(os.listdir(HD+'/main'))}")
            for i in range(NF):
                out=f"{WORK}/frames/{i+1:05d}.jpg"
                if os.path.exists(out): continue
                await pg.evaluate("([t,f,pf])=>window.__renderFrame(t,f,pf)",[i/FPS,FPS,pf])
                await pg.screenshot(path=out,type="jpeg",quality=95)
                if i%60==0: print("frame",i,"/",NF,flush=True)
            print("errors:",errs);await b.close()
    asyncio.run(main());srv.shutdown();os.unlink(link)

elif step=="mux":
    name="CFik019_FiK-Studio_1080x1920"
    run(["ffmpeg","-v","error","-y","-framerate",str(FPS),"-i",f"{WORK}/frames/%05d.jpg","-i",f"{WORK}/audio/mix.wav",
         "-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","16","-profile:v","high","-pix_fmt","yuv420p",
         "-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-r",str(FPS),
         "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart","-shortest",f"{OUT}/{name}.mp4"])
    shutil.copy(f"{WORK}/frames/{int(FPS*P['intro']):05d}.jpg",f"{OUT}/CFik019_thumbnail_1080x1920.jpg")
    print("wrote",OUT)
