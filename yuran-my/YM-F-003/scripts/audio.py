# Campuran audio: suara (denoise ringan) + 2 muzik Mixkit (ducking) + SFX lembut -> -14 LUFS / -1 dBTP
# python3 audio.py plan.json raw.mp4 musicA.mp3 musicB.mp3 sfxdir out.wav
import json, re, subprocess, sys
plan, raw, mA, mB, sfxd, out = sys.argv[1:7]
P = json.load(open(plan))
T0, END, DUR = P["t0"], P["end"], P["duration"]
A, B = P["music"]
def lufs(args):
    o = subprocess.run(["ffmpeg", "-hide_banner"] + args + ["-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
# aras muzik: -14 LUFS suara; muzik 24 dB di bawah semasa bercakap (-38), naik ke -26 bila tiada suara (thumbnail/end card)
gV = -14 - lufs(["-i", raw, "-vn"])
gA, gB = -38 - lufs(["-i", mA]), -38 - lufs(["-i", mB])
duck = (f"if(lt(t,{T0-0.15}),3.98,if(lt(t,{T0+0.15}),3.98-(t-{T0-0.15})/0.3*2.98,"
        f"if(lt(t,{END-0.2}),1,if(lt(t,{END+0.2}),1+(t-{END-0.2})/0.4*2.98,3.98))))")   # +12 dB luar suara
f = [f"[0:a]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,highpass=f=70,afftdn=nr=8:nf=-42,volume={gV}dB,adelay={int(T0*1000)},apad=whole_dur={DUR}[vo]",
     f"[1:a]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,atrim=start={A['offset']}:duration={A['to']+0.6},asetpts=PTS-STARTPTS,volume={gA}dB,afade=t=out:st={A['to']-0.6}:d=1.2[ma]",
     f"[2:a]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,atrim=start={B['offset']}:duration={DUR-B['from']},asetpts=PTS-STARTPTS,volume={gB}dB,afade=t=in:d=1.0,afade=t=out:st={DUR-B['from']-0.8}:d=0.8,adelay={int(B['from']*1000)}[mb]",
     f"[ma][mb]amix=inputs=2:normalize=0,volume='{duck}':eval=frame,apad=whole_dur={DUR}[mu]"]
ins = ["-i", raw, "-i", mA, "-i", mB]
sx = []
for i, s in enumerate(P["sfx"]):
    ins += ["-i", f"{sfxd}/{s['name']}.wav"]
    f.append(f"[{3+i}:a]aresample=48000,pan=mono|c0=c0,volume={s['gain']*0.45:.3f},adelay={int(s['t']*1000)}[s{i}]")
    sx.append(f"[s{i}]")
f.append("".join(sx) + f"amix=inputs={len(sx)}:normalize=0,apad=whole_dur={DUR}[sf]")
f.append(f"[vo][mu][sf]amix=inputs=3:normalize=0,atrim=duration={DUR}[mix]")
tmp = out + ".mix.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(f), "-map", "[mix]", "-c:a", "pcm_s24le", tmp], check=True)
# loudnorm 2 laluan (linear) ke -14 LUFS, -1 dBTP
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(o[o.rindex("{"):])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", ln + ",volume=0.4dB,aresample=48000,alimiter=limit=0.89:level=false", "-ac", "2", "-c:a", "pcm_s24le", out], check=True)
print("suara/muzik dB:", round(gV, 1), round(gA, 1), round(gB, 1))
