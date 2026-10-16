# Final render for CFik018 (1080x1920): cover intro + graded talking head with zoom punch-ins + B-roll
# + burned-in overlay layer (captions, motion graphics, logo, end card; PNG frames exported from the
# preview page in #render mode) + voice, ducked music and SFX.
# Pass a base already padded past the speech (cloned last frame) so it runs under the end card.
# usage: build_final.py plan.json base1080_padded.mov broll_dir fik_photo_dir cover.png overlay_dir music.m4a sfx_dir out.mp4
import json,os,subprocess,sys
P=json.load(open(sys.argv[1]));base,bd,fd,cover,ovd,music,sfxd,out=sys.argv[2:10]
W,H=1080,1920;FPS="30000/1001"
DUR,END=P["duration"],P["speech_end"];IN=P.get("intro",{}).get("e",0)
LOOK="curves=all='0/0.02 0.2/0.17 0.5/0.52 0.8/0.84 1/0.97',eq=contrast=1.03:saturation=0.97,colorbalance=rh=0.01:bh=-0.01"
def size(path):
    w,h=subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",path]).decode().strip().split(",")[:2]
    return int(w),int(h)
# zoom: same keyframes and ease-in-out-quad as the preview, evaluated on the output clock T = t + IN
def zexpr(key):
    Z=P["zoom"];e=f"{Z[-1][key]}"
    for a,b in reversed(list(zip(Z,Z[1:]))):
        if b["t"]-a["t"]<1e-6: continue
        x=f"((T-{a['t']})/{b['t']-a['t']:.3f})";ease=f"if(lt({x},0.5),2*{x}*{x},1-pow(-2*{x}+2,2)/2)"
        e=f"if(lt(T,{b['t']}),{a[key]}+({b[key]-a[key]})*{ease},{e})"
    return e.replace("T",f"(t+{IN})")
zs=zexpr("scale");zo=zexpr("oy")
inp=["-i",base];fc=[]
fc.append(f"[0:v]scale=w='2*trunc({W}*({zs})/2)':h='2*trunc({H}*({zs})/2)':eval=frame:flags=bicubic,"
          f"crop={W}:{H}:x='(iw-{W})/2':y='(ih-{H})*({zo})/100',setsar=1,"
          f"tpad=stop_mode=clone:stop_duration={DUR-END+0.5:.2f},trim=0:{DUR-IN},setpts=PTS-STARTPTS[th]")
n=1
inp+=["-loop","1","-framerate",FPS,"-t",f"{IN}","-i",cover]
fc.append(f"[{n}:v]scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p,trim=0:{IN},setpts=PTS-STARTPTS[iv]");n+=1
fc.append("[iv][th]concat=n=2:v=1:a=0,format=yuv420p[v0]");last="v0"
for b in P["broll"]:
    d=b["e"]-b["s"]
    if b["src"]=="fik": path=f"{fd}/{b['file']}";inp+=["-loop","1","-framerate",FPS,"-t",f"{d+0.1:.2f}","-i",path]
    else: path=f"{bd}/{b['id']}.mp4";inp+=["-ss",str(b["t"]),"-t",f"{d+0.1:.2f}","-i",path]
    sw,sh=size(path);cw=min(sw,round(sh*9/16));ch=min(sh,round(sw*16/9))
    cx=max(0,min(sw-cw,b["x"]*sw-cw/2));cy=(sh-ch)/2
    fc.append(f"[{n}:v]setpts=PTS-STARTPTS,fps={FPS},format=yuv420p,crop={cw}:{ch}:{cx:.0f}:{cy:.0f},"
              f"scale=w='2*trunc({W}*(1+0.07*t/{d:.2f})/2)':h='2*trunc({H}*(1+0.07*t/{d:.2f})/2)':eval=frame:flags=lanczos,"
              f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,{LOOK},setsar=1,setpts=PTS+{b['s']}/TB[b{n}]")
    fc.append(f"[{last}][b{n}]overlay=enable='between(t,{b['s']},{b['e']-0.001})':eof_action=pass[v{n}]");last=f"v{n}";n+=1
inp+=["-framerate",FPS,"-i",f"{ovd}/%05d.png"]
# retime both streams by frame index so the overlay frames line up 1:1 (avoids timestamp wrap after the padded tail)
fc.append(f"[{last}]fps={FPS},setpts=N/({FPS})/TB[mainv]")
fc.append(f"[{n}:v]format=rgba,setpts=N/({FPS})/TB[ov]");fc.append(f"[mainv][ov]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[vout]");n+=1
# pass 1: video only (rendering it in the same graph as the audio mix stalled the video ~4s early)
vtmp=out+".video.mp4"
subprocess.run(["ffmpeg","-v","error","-stats","-y",*inp,"-filter_complex",";".join(fc),"-map","[vout]","-r",FPS,"-t",f"{DUR}",
  "-c:v","libx264","-preset","slow","-crf","18","-profile:v","high","-level","4.2","-pix_fmt","yuv420p","-an",vtmp],check=True)
# pass 2: audio mix, muxed onto the finished video
inp=["-i",vtmp,"-i",base];fc=[];n=2  # 0 = finished video, 1 = base (voice)
# audio: voice (cleaned, delayed past the cover), music bed, SFX
fc.append(f"[1:a]adelay={int(IN*1000)}:all=1,highpass=f=80,afftdn=nr=8:nf=-42,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{DUR}[vo]")
inp+=["-i",music];fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{DUR}[mu]");mix=["[vo]","[mu]"];n+=1
for k,s in enumerate(P["sfx"]):
    inp+=["-i",f"{sfxd}/{s['name']}.wav"]
    fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={s['gain']*0.75:.3f},adelay={int(s['t']*1000)}:all=1[s{k}]");mix.append(f"[s{k}]");n+=1
fc.append("".join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.79:level=false,atrim=0:{DUR}[aout]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fc),"-map","0:v","-map","[aout]","-t",f"{DUR}",
  "-c:v","copy","-movflags","+faststart","-c:a","aac","-b:a","192k","-ar","48000",out],check=True)
os.remove(vtmp)
