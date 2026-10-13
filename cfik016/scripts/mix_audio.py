# usage: mix_audio.py cut.mp4 plan.json sfxdir out.wav  -> voice (cleaned, -14 LUFS) + SFX at plan times, limited
import json,subprocess,sys
src,plan,sfxdir,out=sys.argv[1:]
P=json.load(open(plan));ins=["-i",src];f=["[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=44100[v]"];labs="[v]"
for i,s in enumerate(P["sfx"],1):
    ins+=["-i",f"{sfxdir}/{s['name']}.wav"]; d=int(s["t"]*1000)
    f.append(f"[{i}:a]aresample=44100,volume={s['gain']*0.8*0.6:.3f},adelay={d}|{d}[s{i}]"); labs+=f"[s{i}]"
f.append(f"{labs}amix=inputs={len(P['sfx'])+1}:normalize=0:duration=first,volume=-1.3dB,alimiter=limit=0.85[a]")
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",";".join(f),"-map","[a]","-c:a","pcm_s16le",out],check=True)
