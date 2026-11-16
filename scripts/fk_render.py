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

# ---- outro (BRAND/Outro Potrait.mp4) + tagline & CTA (v3) ----
OUTRO_N = int(round(END * FPS))      # 121 frame: animasi logo sahaja, buang ekor putih kosong
TEXT_IN = 55                          # wordmark statik dari frame ~55 (1.83 s)
# Dalam fail asal: simbol FK (frame 0-37) berpusat x=538 (sudah tengah); wordmark (frame 45+) berpusat x=569.
# Alih wordmark sahaja ke x=540, dengan peralihan lembut semasa transisi (frame 37-47).
def outro_dx(k):
    a = min(1.0, max(0.0, (k - 37) / 10.0)); a = a * a * (3 - 2 * a)
    return (W // 2 - 569) * a

def outro_text():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2                       # wordmark dialih ke tengah (lihat outro_dx)
    f1 = ImageFont.truetype("/root/.fonts/Montserrat-SemiBold.ttf", 52)
    tag = P.get("tagline", "Design Dulu, Baru Bina")
    y = 1150
    d.text((cx - d.textlength(tag, font=f1) / 2, y), tag, font=f1, fill=GREEN + (255,))
    f2 = ImageFont.truetype("/root/.fonts/Montserrat-ExtraBold.ttf", 46)
    cta = P.get("cta", "DM untuk keterangan lanjut")
    y += 120
    bw = d.textlength(cta, font=f2) + 90
    d.rounded_rectangle((cx - bw / 2, y - 26, cx + bw / 2, y + 74), 24, fill=GREEN + (255,))
    d.text((cx - d.textlength(cta, font=f2) / 2, y), cta, font=f2, fill=(255, 255, 255, 255))
    a = np.array(im).astype(np.float32) / 255
    return cv2.cvtColor((a[..., :3] * 255).astype(np.uint8), cv2.COLOR_RGB2BGR).astype(np.float32), a[..., 3:4]

import os
REUSE = os.environ.get("REUSE") == "1" and os.path.exists(OUT + ".noass.mp4")
OT_RGB, OT_A = outro_text()

# ---- ikon butang SAVE (bookmark) ditekan: pop masuk, tekan pada +0.45 s (isi hijau + riak), pudar keluar ----
def save_icon(t):
    """t = saat sejak ikon mula. Pulang (rgb float32, alpha) saiz penuh, atau None."""
    S = P.get("save_icon")
    dur = S["e"] - S["s"]
    if t < 0 or t > dur:
        return None
    tap = 0.45
    sc = 0.6 + 0.4 * min(1, t / 0.15)
    if tap <= t < tap + 0.12: sc *= 0.88                       # butang tertekan
    fade = min(1.0, (dur - t) / 0.2)
    filled = t >= tap
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy, R = W // 2, 1060, int(110 * sc)
    if filled and t < tap + 0.5:                              # riak bulat
        rr = int(R + (t - tap) / 0.5 * 120); ra = int(200 * (1 - (t - tap) / 0.5))
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255, ra), width=8)
    d.ellipse((cx - R - 6, cy - R - 6 + 10, cx + R + 6, cy + R + 6 + 10), fill=(0, 0, 0, 70))   # bayang
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255, 255))
    bw, bh = int(R * 0.9), int(R * 1.15)
    x0, y0 = cx - bw // 2, cy - bh // 2
    poly = [(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh), (cx, y0 + int(bh * 0.72)), (x0, y0 + bh)]
    if filled:
        d.polygon(poly, fill=GREEN + (255,))
    else:
        d.line(poly + [poly[0]], fill=GREEN + (255,), width=max(6, int(R * 0.12)), joint="curve")
    a = np.array(im).astype(np.float32) / 255
    a[..., 3] *= fade
    return cv2.cvtColor((a[..., :3] * 255).astype(np.uint8), cv2.COLOR_RGB2BGR).astype(np.float32), a[..., 3:4]
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
      if P.get("save_icon"):
          si = save_icon(t - P["save_icon"]["s"])
          if si is not None:
              out = (out.astype(np.float32) * (1 - si[1]) + si[0] * si[1]).astype(np.uint8)
      last = out
      enc.stdin.write(out.tobytes())
  # outro: crossfade 0.25 s dari frame terakhir, teks muncul perlahan selepas logo statik
  oc = cv2.VideoCapture(f"{WD}/outro.mp4")
  for k in range(OUTRO_N):
      ok, of = oc.read()
      if not ok:
          break
      bgc = tuple(int(v) for v in of[40, 40])
      of = cv2.warpAffine(of, np.float32([[1, 0, outro_dx(k)], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_CONSTANT, borderValue=bgc)
      ta = min(1.0, max(0.0, (k - TEXT_IN) / 12.0))
      if ta > 0:
          of = (of.astype(np.float32) * (1 - OT_A * ta) + OT_RGB * OT_A * ta).astype(np.uint8)
      xa = min(1.0, k / 8.0)
      enc.stdin.write((cv2.addWeighted(of, xa, last, 1 - xa, 0) if xa < 1 else of).tobytes())
  enc.stdin.close(); enc.wait()

# ---- audio: denoise ringan, suara -14 LUFS / -1 dBTP, SFX lembut ----
total = P["total"]
inputs = ["-i", f"{WD}/a_src.wav"]
flt = [f"[0:a]highpass=f=70,afftdn=nr=8:nf=-42,adelay={int(OFF*1000)}|{int(OFF*1000)},apad=whole_dur={total}[v]"]
mix = ["[v]"]
for k, s in enumerate(P["sfx"]):
    inputs += ["-i", f"{WD}/sfx/{s['f']}.wav"]
    d = int((s["t"] + OFF) * 1000)
    vol = {"softpop": 0.22, "softwhoosh": 0.18, "click": 0.35}.get(s["f"], 0.2)
    flt.append(f"[{k+1}:a]aformat=channel_layouts=stereo,volume={vol},adelay={d}|{d}[s{k}]"); mix.append(f"[s{k}]")
flt.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.85:level=false,aresample=48000[a]")
apath = OUT + ".a.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(flt), "-map", "[a]",
                "-t", str(total), "-ar", "48000", apath + ".1.wav"], check=True)
# laluan 2: ukur loudness sebenar, betulkan gain ke -14 LUFS, limiter true peak <= -1 dBTP
import re as _re
meas = subprocess.run(["ffmpeg", "-i", apath + ".1.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(_re.findall(r"I:\s+(-?[0-9.]+) LUFS", meas)[-1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", apath + ".1.wav", "-af",
                f"volume={-14.0 - I:.2f}dB,alimiter=limit=0.85:level=false", "-ar", "48000", apath], check=True)
os.remove(apath + ".1.wav")
vf = f"ass={ASS}"
if (OW, OH) != (W, H):
    vf += f",scale={OW}:{OH}:flags=lanczos"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", apath, "-vf", vf, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "slow", "-crf", CRF, "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
# thumbnail PNG (frame 0.5s, dengan teks hook)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.5", "-i", tmp, "-frames:v", "1", "-vf", f"ass={ASS}", THUMB], check=True)
print("ok", OUT)
