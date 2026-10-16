"""Generate a royalty-free music bed + SFX track for the TOFU reel and mux it.

usage: python3 mix.py <video_in.mp4> <sfx_dir> <out.mp4>
"""
import subprocess
import sys
import wave

import numpy as np

from render import DUR, ROOMS, SHOTS

SR = 44100
rng = np.random.default_rng(3)
N = int(SR * DUR)


def tone(f, d, harm=((1, 1),)):
    t = np.arange(int(SR * d)) / SR
    return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in harm)


def adsr(n, a, r):
    e = np.ones(n)
    A = int(SR * a)
    e[:A] = np.linspace(0, 1, A)
    e[A:] *= np.exp(-np.arange(n - A) / (SR * r))
    return e


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    x = x[: max(0, len(buf) - i)]
    buf[i:i + len(x)] += g * x


def smooth(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def music():
    bpm, beat = 96, 60 / 96
    bar = 4 * beat
    # Fmaj7 - Am7 - Dm9 - Bbmaj7 : warm, "home" feel
    chords = [[53, 57, 60, 64], [57, 60, 64, 67], [50, 57, 60, 64], [46, 53, 57, 62]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    pad, keys, bass, drums = (np.zeros(N) for _ in range(4))
    nb = int(DUR / bar) + 1
    for b in range(nb):
        ch = chords[b % 4]
        t0 = b * bar
        for m in ch:
            x = tone(hz(m), bar + 0.4, ((1, 1), (2, 0.25), (3, 0.08)))
            x *= adsr(len(x), 0.6, 2.5)
            add(pad, x, t0, 0.09)
        add(bass, tone(hz(ch[0] - 12), bar, ((1, 1), (2, 0.3))) * adsr(int(SR * bar), 0.01, 0.9), t0, 0.32)
        # soft electric-piano arpeggio on 8ths
        for k in range(8):
            m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
            x = tone(hz(m), 0.6, ((1, 1), (2, 0.4), (4, 0.1))) * adsr(int(SR * 0.6), 0.004, 0.18)
            add(keys, x, t0 + k * beat / 2, 0.075 * (1.0 if k % 2 == 0 else 0.7))
        if 0 < b:  # drums enter after the hook bar
            for k in range(4):
                tt = np.arange(int(SR * 0.35)) / SR
                kick = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-tt * 35)) / SR) * np.exp(-tt * 9)
                if k in (0, 2):
                    add(drums, kick, t0 + k * beat, 0.55)
                if k in (1, 3):  # rim/snap
                    s = rng.standard_normal(int(SR * 0.12))
                    s = (s - smooth(s, 6)) * np.exp(-np.arange(len(s)) / (SR * 0.03))
                    add(drums, s, t0 + k * beat, 0.12)
                for h in range(2):  # hats
                    s = rng.standard_normal(int(SR * 0.05))
                    s = (s - smooth(s, 3)) * np.exp(-np.arange(len(s)) / (SR * 0.008))
                    add(drums, s, t0 + k * beat + h * beat / 2, 0.05)
    mix = pad + keys + bass + drums
    # fades: in over 0.3s, out over the last 2s
    env = np.clip(np.minimum(np.arange(N) / (0.3 * SR), (N - np.arange(N)) / (2.0 * SR)), 0, 1)
    return mix * env


def load(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2)[:, 0]
    return x.astype(float) / 32768


def sfx(d):
    out = np.zeros(N)
    whoosh, pop, ding, click, tick = (load(f"{d}/{n}.wav") for n in ("whoosh", "pop", "ding", "click", "tick"))
    add(out, pop, 0.05, 0.5)
    for k in (0.4, 0.65):
        add(out, click, k, 0.4)
    for s in SHOTS[1:]:
        add(out, whoosh, s[1] - 0.22, 0.55)
    for st in ROOMS:
        add(out, pop, st + 0.9, 0.45)
    poll = next(s for s in SHOTS if s[0] == "poll")
    add(out, ding, poll[1] + 0.3, 0.35)
    add(out, tick, poll[2] - 1.6, 0.35)
    cta = SHOTS[-1][1]
    add(out, ding, cta + 1.0, 0.4)
    return out


def main():
    vid, sfx_dir, out = sys.argv[1:4]
    m, s = music(), sfx(sfx_dir)
    # duck music under SFX a little
    duck = 1 - 0.35 * np.clip(smooth(np.abs(s), 4000) * 8, 0, 1)
    x = m * duck * 0.8 + s
    x = np.tanh(x * 1.1) / np.tanh(1.1)
    x = x / np.max(np.abs(x)) * 0.89
    pcm = (np.stack([x, x], 1) * 32767).astype(np.int16)
    wav = out + ".wav"
    with wave.open(wav, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    main()
