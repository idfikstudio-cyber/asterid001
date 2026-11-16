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

# ---- motion zoom pada muka (v2) ----
_fj = json.load(open(f"{WD}/face.json"))
_fp = np.array(_fj["pts"], float)
_fi = np.arange(_fj["n"])
FX = np.interp(_fi, _fp[:, 0], _fp[:, 1]); FY = np.interp(_fi, _fp[:, 0], _fp[:, 2])
_k = np.ones(31) / 31   # licin ~1 s supaya kamera tak goyang
FX = np.convolve(np.pad(FX, 15, mode="edge"), _k, "valid"); FY = np.convolve(np.pad(FY, 15, mode="edge"), _k, "valid")

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def zoom_at(t):
    zs = P["zoom"]
    for z in zs:
        if z["s"] <= t < z["e"]:
            return z["z0"] + (z["z1"] - z["z0"]) * ease((t - z["s"]) / max(0.3, z["e"] - z["s"]))
    # celah antara ayat: kekal pada nilai akhir ayat sebelum
    prev = [z for z in zs if z["e"] <= t]
    return prev[-1]["z1"] if prev else zs[0]["z0"]

def punch(f, z, i=None):
    if z <= 1.001:
        return f
    fx = FX[min(i, len(FX) - 1)] if i is not None else W / 2
    fy = FY[min(i, len(FY) - 1)] if i is not None else H * 0.4
    w, h = W / z, H / z
    # letak muka pada 50% lebar & 36% tinggi tetingkap (mata di sepertiga atas), kemudian kekang dalam frame
    x0 = min(max(fx - 0.5 * w, 0), W - w)
    y0 = min(max(fy - 0.36 * h, 0), H - h)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

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
    ly = 470
    im.paste(logo, (cx - lw // 2, ly), logo)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype("/root/.fonts/Montserrat-SemiBold.ttf", 50)
    tag = "We Design, You Build."
    y = ly + logo.height + 70
    d.text((cx - d.textlength(tag, font=f1) / 2, y), tag, font=f1, fill=GREEN)
    f3 = ImageFont.truetype("/root/.fonts/Montserrat-Bold.ttf", 42)
    fol = "Follow untuk tips reno seterusnya"
    y += 120
    d.text((cx - d.textlength(fol, font=f3) / 2, y), fol, font=f3, fill=GREEN)
    f2 = ImageFont.truetype("/root/.fonts/Montserrat-ExtraBold.ttf", 44)
    lines = ["DM / WhatsApp kami untuk", "3D design rumah anda"]
    y += 110
    bw = max(d.textlength(l, font=f2) for l in lines) + 80
    d.rounded_rectangle((cx - bw / 2, y - 30, cx + bw / 2, y + 2 * 62 + 20), 22, fill=GREEN)
    for l in lines:
        d.text((cx - d.textlength(l, font=f2) / 2, y), l, font=f2, fill="white"); y += 62
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

import os
REUSE = os.environ.get("REUSE") == "1" and os.path.exists(OUT + ".noass.mp4")
ec = end_card()
BOKEH = os.environ.get("BOKEH", "bokeh_full.mp4")
cap = cv2.VideoCapture(f"{WD}/{BOKEH}")
src_frames = []  # baca berurutan
brs = {b["clip"]: cv2.VideoCapture(f"{WD}/br/{b['clip']}.mp4") for b in P["broll"]}

tmp = OUT + ".noass.mp4"
if not REUSE:
  enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
  # thumbnail frame: dari masa sumber 'thumb_t'
  tt = P.get("thumb_t", 2.0)
  c2 = cv2.VideoCapture(f"{WD}/{BOKEH}"); c2.set(cv2.CAP_PROP_POS_MSEC, tt * 1000)
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
      out = grade(punch(f, zoom_at(t), i))
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
