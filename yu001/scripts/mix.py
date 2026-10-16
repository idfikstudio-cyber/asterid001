# Final audio: voice + music bed (0.16) + SFX (same schedule/levels as preview), loudness -14 LUFS
import subprocess,sys
src,sfxdir,out=sys.argv[1:4]
SFX=[(0.00,"whoosh",.55),(1.78,"pop",.6),(2.30,"pop",.5),(4.62,"whoosh",.45),(7.08,"ding",.35),(8.20,"tick",.45),(9.52,"chaching",.45),
     (11.62,"click",.5),(12.24,"pop",.6),(15.62,"bonk",.55),(16.48,"impact",.7),(17.30,"whoosh",.45),(20.30,"ding",.4),(24.25,"click",.6)]
ins=["-i",src,"-i",f"{sfxdir}/music.wav"]+sum([["-i",f"{sfxdir}/{f}.wav"] for _,f,_ in SFX],[])
fc=["[0:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=10:release=150:makeup=1.5[v]",
    "[1:a]volume=0.16[m]"]
for i,(t,f,v) in enumerate(SFX):
    d=int(t*1000);fc.append(f"[{i+2}:a]volume={v},adelay={d}|{d}[s{i}]")
fc.append("[v][m]"+"".join(f"[s{i}]" for i in range(len(SFX)))+f"amix=inputs={len(SFX)+2}:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=11[a]")
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",";".join(fc),"-map","[a]","-ar","48000","-c:a","pcm_s16le",out],check=True)
