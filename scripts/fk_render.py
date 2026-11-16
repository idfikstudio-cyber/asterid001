"""Render FK-F-007: thumbnail 1s + isi (bokeh, punch-in, B-roll) + end card, kemudian caption ASS + audio.

python3 fk_render.py <work_dir> <plan.json> <captions.ass> <out.mp4> <thumb.png> <WxH> <crf>
work_dir mesti ada: bokeh_full.mp4, br/b*.mp4, sfx/*.wav, logo_green.png, a_src.wav (audio asal)
"""
import sys, json, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

WD, PLAN, ASS, OUT, THUMB, SIZE, CRF = sys.argv[1:8]
OW, OH = map(int, SIZE.split("x"))
P = json.load(open(PLAN))
FPS = 30
W, H = 1080, 1920
OFF, END = P["offset"], P["end_card"]
GREEN = (0x30, 0x49, 0x45)

def zoom_at(t):
    for z in P["zoom"]:
        if z["s"] - 0.05 <= t < z["e"] + 0.05:
            return z["z"]
    return 1.0

def punch(f, z):
    if z == 1.0:
        return f
    w, h = int(W / z), int(H / z)
    x, y = (W - w) // 2, int((H - h) * 0.25)   # muka kekal sepertiga atas
    return cv2.resize(f[y:y + h, x:x + w], (W, H), interpolation=cv2.INTER_CUBIC)

def grade(f):
    # jelas & cerah sedikit; kekal warna kulit (tiada anjakan hue)
    x = f.astype(np.float32) / 255
    x = np.clip((x - 0.5) * 1.04 + 0.5 + 0.012, 0, 1)
    g = x.mean(axis=2, keepdims=True)
    x = np.clip(g + (x - g) * 1.05, 0, 1)
    return (x * 255 + 0.5).astype(np.uint8)

# ---- end card (PIL) ----
def end_card():
    im = Image.new("RGB", (W, H), "white")
    logo = Image.open(f"{WD}/logo_green.png").convert("RGBA")
    bb = logo.getbbox(); logo = logo.crop(bb)
    lw = 640; logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    cx = int(W * 0.85 / 2) + 20
    ly = 560
    im.paste(logo, (cx - lw // 2, ly), logo)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype("/root/.fonts/Montserrat-SemiBold.ttf", 50)
    tag = "We Design, You Build."
    y = ly + logo.height + 70
    d.text((cx - d.textlength(tag, font=f1) / 2, y), tag, font=f1, fill=GREEN)
    f2 = ImageFont.truetype("/root/.fonts/Montserrat-ExtraBold.ttf", 44)
    lines = ["DM / WhatsApp kami untuk", "3D design rumah anda"]
    y += 140
    bw = max(d.textlength(l, font=f2) for l in lines) + 80
    d.rounded_rectangle((cx - bw / 2, y - 30, cx + bw / 2, y + 2 * 62 + 20), 22, fill=GREEN)
    for l in lines:
        d.text((cx - d.textlength(l, font=f2) / 2, y), l, font=f2, fill="white"); y += 62
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

import os
REUSE = os.environ.get("REUSE") == "1" and os.path.exists(OUT + ".noass.mp4")
ec = end_card()
cap = cv2.VideoCapture(f"{WD}/bokeh_full.mp4")
src_frames = []  # baca berurutan
brs = {b["clip"]: cv2.VideoCapture(f"{WD}/br/{b['clip']}.mp4") for b in P["broll"]}

tmp = OUT + ".noass.mp4"
if not REUSE:
  enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
  # thumbnail frame: dari masa sumber 'thumb_t'
  tt = P.get("thumb_t", 2.0)
  c2 = cv2.VideoCapture(f"{WD}/bokeh_full.mp4"); c2.set(cv2.CAP_PROP_POS_MSEC, tt * 1000)
  ok, th = c2.read(); th = grade(th)
  for _ in range(int(OFF * FPS)):
      enc.stdin.write(th.tobytes())

  n_src = int(round(P["src_dur"] * FPS))
  last = th
  for i in range(n_src):
      ok, f = cap.read()
      if not ok:
          f = last
      t = i / FPS
      out = grade(punch(f, zoom_at(t)))
      for b in P["broll"]:
          if b["s"] <= t < b["e"]:
              ok2, bf = brs[b["clip"]].read()
              if ok2:
                  a = min(1.0, (t - b["s"]) / 0.15, (b["e"] - t) / 0.15)
                  out = cv2.addWeighted(bf, a, out, 1 - a, 0) if a < 1 else bf
      last = out
      enc.stdin.write(out.tobytes())
  # end card fade-in 0.25s
  for k in range(int(END * FPS)):
      a = min(1.0, k / (0.25 * FPS))
      enc.stdin.write(cv2.addWeighted(ec, a, last, 1 - a, 0).tobytes())
  enc.stdin.close(); enc.wait()

# ---- audio: denoise ringan, suara -14 LUFS / -1 dBTP, SFX lembut ----
total = P["total"]
inputs = ["-i", f"{WD}/a_src.wav"]
flt = [f"[0:a]highpass=f=70,afftdn=nr=8:nf=-42,adelay={int(OFF*1000)}|{int(OFF*1000)},apad=whole_dur={total}[v]"]
mix = ["[v]"]
for k, s in enumerate(P["sfx"]):
    inputs += ["-i", f"{WD}/sfx/{s['f']}.wav"]
    d = int((s["t"] + OFF) * 1000)
    vol = 0.22 if s["f"] == "softpop" else 0.18
    flt.append(f"[{k+1}:a]aformat=channel_layouts=stereo,volume={vol},adelay={d}|{d}[s{k}]"); mix.append(f"[s{k}]")
flt.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.85:level=false,aresample=48000[a]")
apath = OUT + ".a.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(flt), "-map", "[a]",
                "-t", str(total), "-ar", "48000", apath], check=True)

vf = f"ass={ASS}"
if (OW, OH) != (W, H):
    vf += f",scale={OW}:{OH}:flags=lanczos"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", apath, "-vf", vf, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "slow", "-crf", CRF, "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
# thumbnail PNG (frame 0.5s, dengan teks hook)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.5", "-i", tmp, "-frames:v", "1", "-vf", f"ass={ASS}", THUMB], check=True)
print("ok", OUT)
