# Voice clean-up + SFX mix + 2-pass loudnorm (-14 LUFS, -1 dBTP). Optional music (from brand MUSIC/ only) ducked ~23 dB under voice.
# usage: python3 aster_audio.py <plan.json> <src.mp4> <sfx_dir> <out.wav> [music.wav]
import json, subprocess, sys, os
plan_p, src, SFXD, out = sys.argv[1:5]
music = sys.argv[5] if len(sys.argv) > 5 else None
P = json.load(open(plan_p))
total = P["intro"] + P["src_duration"] + P["outro"]
ms = int(P["intro"] * 1000)
inputs = ["-i", src]; fl = [f"[0:a]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,highpass=f=75,afftdn=nf=-28:nr=8,"
                            f"acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,adelay={ms}|{ms},apad=whole_dur={total}[v]"]
labels = ["[v]"]
for k, s in enumerate(P["sfx"]):
    inputs += ["-i", os.path.join(SFXD, s["name"] + ".wav")]; t = int(s["t"] * 1000)
    fl.append(f"[{k+1}:a]aresample=48000,pan=mono|c0=c0,volume={s['gain']},adelay={t}|{t}[s{k}]"); labels.append(f"[s{k}]")
mix = "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first[m0]"
fl.append(mix)
last = "[m0]"
if music:
    n = len(P["sfx"]) + 1; inputs += ["-stream_loop", "-1", "-i", music]
    fl.append(f"[{n}:a]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,volume=-23dB,atrim=0:{total},afade=t=out:st={total-1.2}:d=1.2[mu]")
    fl.append(f"[mu][v2]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[mud]")
    fl[0] = fl[0].replace("[v]", "[vv]") ; fl.insert(1, "[vv]asplit=2[v][v2]")
    fl.append(f"[m0][mud]amix=inputs=2:normalize=0:duration=first[m1]"); last = "[m1]"
graph = ";".join(fl)
def run(extra, af_tail, dst):
    return subprocess.run(["ffmpeg", "-v", "info", "-y", *inputs, "-filter_complex", graph + f";{last}{af_tail}[o]", "-map", "[o]", "-t", str(total), *extra, dst], capture_output=True, text=True)
r = run(["-f", "null"], "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-")
js = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]; m = json.loads(js)
tail = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
        f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000,alimiter=limit=0.84:level=false")
r = run(["-ar", "48000", "-c:a", "pcm_s16le"], tail, out)
if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
print("ok", out)
