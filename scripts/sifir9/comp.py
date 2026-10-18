# Base composite for the preview (no graphics; those are live HTML in preview/sifir9).
# Streams both sources once: the talk video per the EDL, the board through the retime map.
# usage: comp.py <talk.mp4> <board.mp4> <out.mp4> graded|orig [width=540]
import json, os, subprocess, sys
import numpy as np
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
plan = json.load(open(os.path.join(ROOT, "edit/sifir9/plan.json")))
talk, board, out, mode = sys.argv[1:5]
W = int(sys.argv[5]) if len(sys.argv) > 5 else 540; H = W * 16 // 9; s = W / 1080
FPS, BFPS = 30, 60
grade = open(os.path.join(ROOT, "edit/sifir9/grade.txt")).read().strip()
B = plan["board"]; bx, by, bw, bh = B["src_crop"]
BH = round(1180 * s); BW = round(bw * BH / bh); BX = (W - BW) // 2
FACE_Y0 = round(H * 355 / 960)

def reader(cmd, w, h):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: return
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)

vf_t = (grade + "," if mode == "graded" else "") + f"scale={W}:{H}:flags=lanczos"
tr = reader(["ffmpeg", "-v", "error", "-i", talk, "-vf", vf_t, "-r", str(FPS), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], W, H)
vf_b = f"crop={bw}:{bh}:{bx}:{by},drawbox=x={B['mask_x_from'] - bx}:y=0:w={bw}:h={bh}:color=black:t=fill,drawbox=x=0:y=0:w={bw}:h={B['mask_top']}:color=black:t=fill,scale={BW}:{BH}:flags=lanczos"
br = reader(["ffmpeg", "-v", "error", "-i", board, "-vf", vf_b, "-r", str(BFPS), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], BW, BH)

def bmap(t):  # E time -> board source time (monotone; "cut" just starts a new piece)
    pts = [p for p in B["map"] if p != "cut"]
    if t <= pts[0][0]: return pts[0][1]
    for (t0, b0), (t1, b1) in zip(pts, pts[1:]):
        if t0 <= t <= t1: return b0 + (b1 - b0) * (t - t0) / max(t1 - t0, 1e-6)
    return pts[-1][1]
def talk_t(t):  # E time -> talk time (holds return their frame)
    for p in plan["edl"]:
        if p["src"] == "talk" and p["e0"] <= t < p["e0"] + p["s1"] - p["s0"]: return p["s0"] + t - p["e0"]
        if p["src"] == "hold" and p["e0"] <= t < p["e0"] + p["dur"]: return p["frame"]
    return plan["edl"][-1]["frame"]
def layout(t):
    for g in plan["segments"]:
        if g["t0"] <= t < g["t1"]: return g["layout"]
    return "end"

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                       stdin=subprocess.PIPE)
tf, ti, bf, bi = None, -1, None, -1
nfr = int(plan["dur"] * FPS)
for i in range(nfr):
    t = i / FPS
    want = int(round(talk_t(t) * FPS))
    while ti < want:
        nxt = next(tr, None)
        if nxt is None: break
        tf, ti = nxt, ti + 1
    lay = layout(t)
    if lay in ("split", "quiz"):
        wb = int(round(bmap(t) * BFPS))
        while bi < wb:
            nxt = next(br, None)
            if nxt is None: break
            bf, bi = nxt, bi + 1
        fr = np.zeros((H, W, 3), np.uint8)
        fr[:BH, BX:BX + BW] = bf
        fh = H - BH
        fr[BH:] = tf[FACE_Y0:FACE_Y0 + fh]
    else:
        fr = tf
    enc.stdin.write(np.ascontiguousarray(fr).tobytes())
enc.stdin.close(); enc.wait()
print("wrote", out, nfr, "frames")
