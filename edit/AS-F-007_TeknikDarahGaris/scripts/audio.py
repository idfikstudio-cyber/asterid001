import sys, os, subprocess, json, wave, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan as P
SR = 48000; OUT = sys.argv[1]
WK = P.W; REPO = "/home/user/asterid001"
def run(c): subprocess.run(c, check=True)
# 1) voice: cut, light denoise, highpass, gentle compression
f = []
for i, (a, b) in enumerate(P.KEEP):
    f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b-a-0.01}:d=0.01[a{i}]")
f.append("".join(f"[a{i}]" for i in range(len(P.KEEP))) + f"concat=n={len(P.KEEP)}:v=0:a=1,aresample={SR},pan=mono|c0=0.5*c0+0.5*c1,highpass=f=75,afftdn=nr=10:nf=-42:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2[v]")
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(P.S, "dl", "main.mp4"), "-filter_complex", ";".join(f), "-map", "[v]", os.path.join(WK, "voice_raw.wav")])
def rd(p):
    w = wave.open(p); n = w.getnframes(); ch = w.getnchannels(); sr = w.getframerate()
    x = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    x = x.reshape(-1, ch).mean(1)
    if sr != SR:
        t = np.arange(int(len(x) * SR / sr)) / SR; x = np.interp(t, np.arange(len(x)) / sr, x)
    return x
N = int(P.TOTAL * SR) + SR // 10
voice = np.zeros(N); v = rd(os.path.join(WK, "voice_raw.wav")); i0 = int(P.THUMB * SR); voice[i0:i0 + len(v)] = v[:N - i0]
# 2) sfx
sfx = np.zeros(N)
for t, name, g in P.SFX:
    x = rd(os.path.join(REPO, "edit", "sfx", name + ".wav")) * 10 ** (g / 20)
    i = int(t * SR); j = min(N, i + len(x)); sfx[i:j] += x[:j - i]
# 3) music with ducking (voice envelope)
m = rd(os.path.join(WK, "music.wav"))
mus = np.zeros(N); mus[:min(N, len(m))] = m[:N]
env = np.abs(voice); k = int(0.05 * SR)
env = np.convolve(env, np.ones(k) / k, "same")
act = (env > 0.01).astype(float)
k2 = int(0.25 * SR); act = np.convolve(act, np.ones(k2) / k2, "same").clip(0, 1)
# voice RMS vs music RMS -> music ~23 dB under voice while talking, ~ -17 dB in gaps/thumb/end
vr = np.sqrt(np.mean(v[np.abs(v) > 0.01] ** 2)); mr = np.sqrt(np.mean(m ** 2))
base = vr / mr * 10 ** (-23 / 20)
duck = base * (1 + act * 0) * np.where(act > 0, 1.0, 1.0)
gain = base * (10 ** (6 / 20) * (1 - act) + act)  # +6 dB when voice absent
mus *= gain
mix = voice + sfx + mus
st = np.stack([mix, mix], 1)
st = np.clip(st, -1, 1)
tmp = os.path.join(WK, "mix_pre.wav")
with wave.open(tmp, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
# 4) two-pass loudnorm -14 LUFS / -1 dBTP
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
js = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,alimiter=limit=0.84:level=false"
run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af + f",aresample={SR}", OUT])
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print("\n".join(r.splitlines()[-12:]))
print("music under voice dB ~", 23)
