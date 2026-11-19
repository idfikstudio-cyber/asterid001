# Jana muzik latar instrumental "cozy" (lo-fi lembut) sendiri, bebas hak cipta.
# Elektrik piano (FM ringkas) + bass lembut + kick/shaker perlahan + vinyl hiss halus.
# Guna: python3 ym_music.py out.wav [saat]
import sys, numpy as np, wave

SR = 44100
BPM = float(sys.argv[4]) if len(sys.argv) > 4 else 78
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 11)
beat = 60 / BPM
bar = 4 * beat
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)

def midi(n): return 440 * 2 ** ((n - 69) / 12)

def ep(freq, dur, vel=0.25):
    t = np.arange(int(SR * dur)) / SR
    mod = np.sin(2 * np.pi * freq * 2 * t) * 1.2 * np.exp(-t * 3)
    env = np.exp(-t * 1.6) * (1 - np.exp(-t * 200))
    s = np.sin(2 * np.pi * freq * t + mod) * env
    s += 0.25 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 4) * env
    return vel * s

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig)); buf[i:j] += gain * sig[: j - i]

# Progresi hangat: Fmaj7 - Em7 - Dm9 - Cmaj7 (berulang)
prog = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60, 64], [48, 52, 55, 59]]
bass = [41, 40, 38, 36]
nbars = int(DUR / bar) + 1
for b in range(nbars):
    t0 = b * bar
    ch = prog[b % 4]
    for k, n in enumerate(ch):  # strum lembut
        s = ep(midi(n + 12), bar * 1.1, 0.11)
        add(L, t0 + k * 0.025, s, 0.9 if k % 2 else 0.6)
        add(R, t0 + k * 0.025, s, 0.6 if k % 2 else 0.9)
    # nota ulangan di beat 3.5
    for n in ch[1:3]:
        s = ep(midi(n + 12), beat * 1.5, 0.07)
        add(L, t0 + 2.5 * beat, s); add(R, t0 + 2.5 * beat, s)
    # melodi ringkas pentatonik
    if b % 2 == 1:
        mel = rng.choice([72, 74, 76, 79, 81], 3)
        for m, off in zip(mel, [0.5, 1.5, 3.0]):
            s = ep(midi(m), beat, 0.06)
            add(L, t0 + off * beat, s, 0.8); add(R, t0 + off * beat + 0.012, s, 0.8)
    # bass
    t = np.arange(int(SR * bar)) / SR
    bs = 0.22 * np.sin(2 * np.pi * midi(bass[b % 4]) * t) * np.exp(-t * 0.9) * (1 - np.exp(-t * 80))
    add(L, t0, bs); add(R, t0, bs)
    # kick lembut (beat 1 & 3) + shaker
    for k in (0, 2.5):
        tk = np.arange(int(SR * 0.3)) / SR
        kick = 0.35 * np.sin(2 * np.pi * (55 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 12)
        add(L, t0 + k * beat, kick); add(R, t0 + k * beat, kick)
    for k in range(8):
        ts = np.arange(int(SR * 0.06)) / SR
        sh = 0.025 * rng.standard_normal(len(ts)) * np.exp(-ts * 60)
        add(L if k % 2 else R, t0 + k * beat / 2 + 0.01, sh)

# low-pass ringan (purata bergerak) + hiss vinyl
def lp(x, k=6): return np.convolve(x, np.ones(k) / k, mode="same")
L, R = lp(L), lp(R)
hiss = 0.004 * lp(rng.standard_normal(N), 3)
L += hiss; R += hiss
# fade in/out
f = int(SR * 2); env = np.ones(N); env[:f] = np.linspace(0, 1, f); env[-f * 2:] = np.linspace(1, 0, f * 2)
L *= env; R *= env
pk = max(abs(L).max(), abs(R).max()); L /= pk / 0.8; R /= pk / 0.8
st = (np.stack([L, R], 1) * 32767).astype(np.int16)
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
print("ok", DUR)
