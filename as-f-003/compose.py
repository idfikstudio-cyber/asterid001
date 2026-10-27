# Gabung video: talking head (grade + punch-in), skrin terbelah dengan papan iPad (b-roll dipeta masa), lapisan grafik PNG.
# usage: python3 compose.py timeline.json main.mp4 broll.mp4 overlay_dir width out_video.mp4 [crf]
import json, subprocess, sys, os
import numpy as np
from PIL import Image

tl = json.load(open(sys.argv[1])); MAIN, BROLL, OV, W, OUT = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
H = W * 16 // 9; k = W / 1080; FPS = 30
GRADE = "eq=brightness=0.02:contrast=1.06:saturation=1.08:gamma=1.02,colorbalance=rm=-0.01:bm=0.01"
BW, BH = W, int(round(W * 0.8)) // 2 * 2          # papan: crop 600×480 dari rakaman iPad
THUMB_SRC = 70.2

class Reader:
    def __init__(s, path, vf, w, h):
        s.w, s.h = w, h; s.i = -1; s.f = None
        s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", vf + ",fps=30", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    def at(s, idx):
        while s.i < idx:
            b = s.p.stdout.read(s.w * s.h * 3)
            if len(b) < s.w * s.h * 3: break
            s.f = np.frombuffer(b, np.uint8).reshape(s.h, s.w, 3); s.i += 1
        return s.f

main = Reader(MAIN, f"{GRADE},scale={W}:{H}:flags=lanczos", W, H)
brd = Reader(BROLL, f"crop=600:480:100:180,scale={BW}:{BH}:flags=lanczos", BW, BH)
thumb = np.asarray(Image.open(os.path.join(os.path.dirname(OUT) or ".", "thumb_src.png")).convert("RGB").resize((W, H), Image.LANCZOS))

keep = tl["keep"]; T0 = tl["thumb"]; C = T0 + tl["content"]
def o2s(t):
    o = T0
    for a, b in keep:
        if t < o + (b - a): return a + (t - o)
        o += b - a
    return keep[-1][1]
bmap = tl["bmap"]
def o2b(t):
    if t <= bmap[0][0]: return bmap[0][1]
    for (t0, b0), (t1, b1) in zip(bmap, bmap[1:]):
        if t < t1: return b0 + (b1 - b0) * (t - t0) / (t1 - t0)
    return bmap[-1][1]
Z = tl["zoom"]
def zoom_at(src):
    z = 1.0
    for x in Z:
        if src >= x["src"] - 1e-3: z = x["z"]
    return z
def zoomed(img, z, ox=540, oy=770):
    if z == 1.0: return img
    ox, oy = ox * k, oy * k; cw, ch = W / z, H / z
    l, t = ox - ox / z, oy - oy / z
    return np.asarray(Image.fromarray(img).resize((W, H), Image.BICUBIC, box=(l, t, l + cw, t + ch)))
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3

TOP_Y, PANEL_Y, CROP_Y = int(60 * k), int(1008 * k), int(430 * k)
def split_frame(m, b):
    f = np.zeros((H, W, 3), np.uint8); f[:] = (11, 11, 13)
    f[TOP_Y:TOP_Y + BH] = b
    ph = H - PANEL_Y; f[PANEL_Y:] = m[CROP_Y:CROP_Y + ph]
    return f

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", CRF, "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
N = round(tl["dur"] * FPS); s0, s1 = tl["split"]
for i in range(N):
    t = i / FPS
    if t < T0: f = zoomed(thumb, 1.06)
    elif t < C:
        src = o2s(t); m = main.at(round(src * FPS))
        full = zoomed(m, zoom_at(src))
        if s0 <= t < s1:
            b = brd.at(round(o2b(t) * FPS))
            sp = split_frame(m, b); a = ease(min((t - s0) / 0.3, (s1 - t) / 0.3))
            f = sp if a >= 1 else (sp * a + full * (1 - a)).astype(np.uint8)
        else: f = full
    else: f = np.zeros((H, W, 3), np.uint8)
    ov = Image.open(os.path.join(OV, f"{i:05d}.png")).convert("RGBA")
    img = Image.fromarray(f).convert("RGBA"); img.alpha_composite(ov)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    if i % 300 == 0: print("frame", i, "/", N, flush=True)
enc.stdin.close(); enc.wait()
