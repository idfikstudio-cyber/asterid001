# Audio: potong ikut EDL (fade 12 ms), denoise ringan, kompres, SFX, loudness -14 LUFS / -1 dBTP.
# usage: python3 audio.py timeline.json main.mp4 sfx_dir out.wav
import json, subprocess, sys, re
tl = json.load(open(sys.argv[1])); MAIN, SFXD, OUT = sys.argv[2], sys.argv[3], sys.argv[4]
T0, DUR = tl["thumb"], tl["dur"]
parts, labels = [], []
for i, (a, b) in enumerate(tl["keep"]):
    d = b - a
    parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d - 0.012:.3f}:d=0.012[s{i}]")
    labels.append(f"[s{i}]")
voice = ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=0:a=1," \
        "highpass=f=80,afftdn=nr=8:nf=-42,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2," \
        f"adelay={int(T0 * 1000)}:all=1,apad=whole_dur={DUR:.3f},aformat=sample_rates=48000:channel_layouts=stereo[v]"
inputs = ["-i", MAIN]; fx = []
for j, s in enumerate(tl["sfx"]):
    inputs += ["-i", f"{SFXD}/{s['name']}.wav"]
    fx.append(f"[{j + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={s['gain'] * 0.45:.3f},adelay={int(s['t'] * 1000)}:all=1[x{j}]")
mix = f"[v]{''.join(f'[x{j}]' for j in range(len(fx)))}amix=inputs={len(fx) + 1}:normalize=0:duration=first,atrim=0:{DUR:.3f}"
def run(extra, out):
    g = voice + ";" + ";".join(fx) + ";" + mix + extra
    return subprocess.run(["ffmpeg", "-v", "info", "-y", *inputs, "-filter_complex", g, *out], capture_output=True, text=True)
r = run(",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", ["-f", "null", "-"])
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr).group(0))
ln = (f",loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
r = run(ln, ["-c:a", "pcm_s16le", OUT]); print(r.returncode, r.stderr[-400:] if r.returncode else "ok")
r = subprocess.run(["ffmpeg", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
print("\n".join(l for l in r.stderr.splitlines()[-12:] if re.search(r"I:|Peak:|LRA:", l)))
