# Audio for the preview, all on the edited (E) timeline:
#   voice_clean.wav / voice_orig.wav  (talk audio with the quiz gap + end hold inserted)
#   sfx.wav    (every cue in plan.json)
#   music.wav  (synthesized light pluck loop, ducked under the voice)
# usage: mix.py <talk.mp4> <outdir>
import json, os, subprocess, sys, wave
import numpy as np
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SR = 48000
plan = json.load(open(os.path.join(ROOT, "edit/sifir9/plan.json")))
talk, out = sys.argv[1], sys.argv[2]
N = int(plan["dur"] * SR)
chain = open(os.path.join(ROOT, "edit/sifir9/audio_chain.txt")).read().strip()

def decode(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "2", "-ar", str(SR)]
    if af: cmd += ["-af", af]
    raw = subprocess.run(cmd + ["-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def save(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(os.path.join(out, name), "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def lay(src):  # place talk pieces per EDL; holds are silent
    y = np.zeros((N, 2), np.float32)
    for p in plan["edl"]:
        if p["src"] != "talk": continue
        a, b, e0 = int(p["s0"] * SR), int(p["s1"] * SR), int(p["e0"] * SR)
        seg = src[a:b]; seg = seg[: N - e0]
        fade = min(len(seg), int(0.01 * SR))  # 10ms fades at every join
        seg[:fade] *= np.linspace(0, 1, fade)[:, None]; seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
        y[e0:e0 + len(seg)] += seg
    return y

voice = lay(decode(talk, chain + ",lowpass=f=16000"))
save("voice_clean.wav", voice)
save("voice_orig.wav", lay(decode(talk)))

# sfx
sfx = np.zeros((N, 2), np.float32)
cache = {}
for c in plan["sfx"]:
    if c["f"] not in cache: cache[c["f"]] = decode(os.path.join(ROOT, "edit/sifir9/sfx", c["f"] + ".wav"))
    s = cache[c["f"]] * 10 ** (c["db"] / 20); i = int(c["t"] * SR); s = s[: N - i]
    sfx[i:i + len(s)] += s
save("sfx.wav", sfx * 0.9)

# music: C G Am F, 100 bpm, Karplus-Strong plucks + soft bass + kick + shaker
rng = np.random.default_rng(3)
bpm = plan["music"]["bpm"]; beat = 60 / bpm; m = np.zeros(N)
def pluck(f, d, bright=0.5):
    n = int(d * SR); p = max(2, int(SR / f)); buf = rng.uniform(-1, 1, p); y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % p]; buf[i % p] = bright * buf[i % p] + (1 - bright) * buf[(i + 1) % p] * 0.996 + (0.5 - bright) * 0
    return y
def note(midi): return 440 * 2 ** ((midi - 69) / 12)
chords = [[60, 64, 67, 72], [55, 62, 67, 71], [57, 60, 64, 69], [53, 60, 65, 69]]
roots = [36, 43, 45, 41]
pl_cache = {}
t = 0.0; k = 0
while t < plan["dur"]:
    ch = chords[(k // 8) % 4]; root = roots[(k // 8) % 4]
    i = int(t * SR)
    pat = [0, 2, 1, 3, 2, 1, 3, 2]
    mid = ch[pat[k % 8]] + (12 if k % 16 in (6, 14) else 0)
    if mid not in pl_cache: pl_cache[mid] = pluck(note(mid), beat * 1.5, 0.5)
    s = pl_cache[mid] * (0.55 if k % 2 else 0.75); s = s[: N - i]; m[i:i + len(s)] += s
    if k % 2 == 0:  # bass on beats, sine with soft attack
        d = int(beat * 0.9 * SR); tt = np.arange(d) / SR
        b = np.sin(2 * np.pi * note(root) * tt) * np.minimum(1, tt * 60) * np.exp(-tt * 2.5) * 0.6
        b = b[: N - i]; m[i:i + len(b)] += b
    if k % 4 == 0:  # kick on 1 and 3
        d = int(0.25 * SR); tt = np.arange(d) / SR
        kk = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 14) * 0.7
        kk = kk[: N - i]; m[i:i + len(kk)] += kk
    d = int(0.05 * SR)  # shaker 8ths
    sh = rng.standard_normal(d) * np.exp(-np.arange(d) / SR * 90) * (0.10 if k % 2 else 0.05)
    sh = np.diff(sh, prepend=0); sh = sh[: N - i]; m[i:i + len(sh)] += sh
    t += beat / 2; k += 1
m /= np.abs(m).max()
# duck: voice envelope (RMS over 50ms, smoothed) pulls music down by duck_db
hop = int(0.05 * SR); v = voice.mean(1)
env = np.sqrt(np.convolve(v ** 2, np.ones(hop) / hop, mode="same"))
on = (env > 0.02).astype(float)
k_att = np.exp(-1 / (0.04 * SR)); k_rel = np.exp(-1 / (0.35 * SR)); g = np.zeros(N); s = 0.0
for i in range(0, N, 64):  # coarse 64-sample control rate
    tgt = on[i]; kk = k_att if tgt > s else k_rel; s = tgt + (s - tgt) * kk ** 64; g[i:i + 64] = s
base = 10 ** (plan["music"]["base_db"] / 20); duck = 10 ** (plan["music"]["duck_db"] / 20)
gain = base * (1 - g * (1 - duck))
q0, qd = plan["quiz"]["t0"], plan["quiz"]["dur"]; end0 = [x for x in plan["segments"] if x["id"] == "end"][0]["t0"]
tt = np.arange(N) / SR
lift = np.where((tt > q0) & (tt < q0 + qd), 2.0, 1.0) * np.where(tt > end0, 2.2, 1.0)
fade = np.clip((plan["dur"] - tt) / 1.2, 0, 1) * np.clip(tt / 0.3, 0, 1)
mus = (m * gain * lift * fade).astype(np.float32)
save("music.wav", np.stack([mus, mus], 1))
print("ok", N / SR)
