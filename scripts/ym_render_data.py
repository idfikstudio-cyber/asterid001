"""Render video Yuran.my: talking head + tindanan grafik + babak grafik penuh (ym_datatree).

python3 ym_render_data.py <edit_dir> <raw.mp4> <brand_dir> <sfx_dir> <music.wav> <out.mp4> [scale] [plan_out.json]
Env THUMB_SRC = frame PNG untuk thumbnail.
"""
import json, re, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ym_datatree as T

ED, RAW, BRAND, SFXD, MUSIC, OUT = sys.argv[1:7]
SC = float(sys.argv[7]) if len(sys.argv) > 7 else 0.5
PLAN_OUT = sys.argv[8] if len(sys.argv) > 8 else None
T.SC = SC
C = json.load(open(f"{ED}/config.json")); TR = json.load(open(f"{ED}/transcript.json"))
FPS = 30; W, H = int(1080 * SC), int(1920 * SC)
S, F, ease, ramp = T.S, T.F, T.ease, T.ramp
B1, B2, WH, INK, GR = T.B1, T.B2, T.WH, T.INK, T.GR
R0, R1 = C["raw_in"], C["raw_out"]; D = R1 - R0
THUMB, ENDC = 1.0, C["end_card"]; TOTAL = THUMB + D + ENDC; NF = int(round(TOTAL * FPS))

# ---------- caption ----------
FIX = C["fix"]; FIX_AT = {round(float(k), 2): v for k, v in C["fix_at"].items()}; KEY = set(C["key"])
words = []
for s in TR:
    for w in s["words"]:
        if w["s"] >= R1: continue
        raw = w["w"].strip()
        if (raw.startswith("-") or raw.startswith(".")) and words:
            words[-1]["t"] += raw; words[-1]["e"] = w["e"]; continue
        core = re.sub(r"[^\w\-.]", "", raw).rstrip(".")
        t = raw
        if round(w["s"], 2) in FIX_AT: t = raw.replace(core, FIX_AT[round(w["s"], 2)])
        elif raw in FIX: t = FIX[raw]
        elif core in FIX: t = raw.replace(core, FIX[core])
        words.append({"t": t, "s": w["s"], "e": w["e"], "o": raw})
for w in words:
    c = re.sub(r"[^\w\-.]", "", w["t"]).rstrip(".").lower()
    w["hl"] = c in KEY or c.split("-")[0] in KEY
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w); txt = " ".join(x["t"] for x in cur); nxt = words[i + 1] if i + 1 < len(words) else None
    if w["t"][-1] in ",.?!" or len(cur) >= 4 or len(txt) >= 18 or nxt is None or nxt["s"] - w["e"] > 0.25:
        groups.append({"s": cur[0]["s"], "e": cur[-1]["e"], "w": [dict(x) for x in cur]}); cur = []
for i, g in enumerate(groups):
    nx = groups[i + 1]["s"] if i + 1 < len(groups) else g["e"] + 0.4
    g["e"] = min(max(g["e"] + 0.15, g["s"] + 0.5), nx)
    for x in g["w"]: x["t"] = x["t"].rstrip(",.").rstrip("…")

def caption(img, r, mode):
    g = next((g for g in groups if g["s"] <= r < g["e"]), None)
    if not g: return
    d = ImageDraw.Draw(img); base = 66 if mode == "talk" else 56; f = F(T.FX, base)
    ws = [(x["t"].rstrip("."), x["hl"]) for x in g["w"]]; sp = d.textlength(" ", font=f)
    tw = sum(d.textlength(t, font=f) for t, _ in ws) + sp * (len(ws) - 1)
    maxw = S(900)
    if tw > maxw: f = F(T.FX, base * maxw / tw); sp = d.textlength(" ", font=f); tw = maxw
    cx, cy = (W / 2, S(1340)) if mode == "talk" else (W / 2, S(1440))
    if mode != "talk": d.rounded_rectangle((cx - tw / 2 - S(26), cy - S(46), cx + tw / 2 + S(26), cy + S(46)), S(22), fill=INK)
    x = cx - tw / 2
    for t, hl in ws:
        d.text((x, cy), t, font=f, fill=B2 if hl else WH, anchor="lm", stroke_width=S(7) if mode == "talk" else 0, stroke_fill=INK)
        x += d.textlength(t, font=f) + sp

# ---------- aset ----------
class Reader:
    def __init__(self, path, vf):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"{vf},fps={FPS},scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.idx, self.frame = -1, None
    def get(self, t):
        want = max(0, int(round(t * FPS)))
        while self.idx < want:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            self.frame = b; self.idx += 1
        return Image.frombuffer("RGB", (W, H), self.frame)
raw = Reader(RAW, "eq=contrast=1.04:brightness=0.015:saturation=1.05:gamma=1.02,unsharp=5:5:0.3")
BG = T.bg_blue(W, H).convert("RGBA")
FX_, FY_ = C["face"]

def thumb_img():
    im = Image.open(os.environ["THUMB_SRC"]).convert("RGB").resize((W, H))
    g = Image.new("L", (1, H), 0)
    for y in range(int(H * 0.47), H): g.putpixel((0, y), int(235 * (y - H * 0.47) / (H * 0.53)))
    im.paste(Image.new("RGB", (W, H), INK), (0, 0), g.resize((W, H))); d = ImageDraw.Draw(im); y = S(1020)
    for t, k in C["hook"]:
        if k == "pill":
            f = F(T.FX, 50); tw = d.textlength(t, font=f)
            d.rounded_rectangle((S(80), y, S(80) + tw + S(60), y + S(80)), S(40), fill=B2); d.text((S(110), y + S(40)), t, font=f, fill=WH, anchor="lm"); y += S(110)
        else:
            d.text((S(80), y), t, font=F(T.FX, 96), fill=B2 if k == "a" else WH, stroke_width=S(4), stroke_fill=INK); y += S(108)
    return im

def end_img():
    im = Image.new("RGB", (W, H), B1); d = ImageDraw.Draw(im)
    lg = Image.open(f"{BRAND}/logo_white.png").convert("RGBA"); lw = S(560); lg = lg.resize((lw, int(lw * lg.height / lg.width)), Image.LANCZOS)
    im.paste(lg, ((W - lw) // 2, S(640)), lg)
    d.text((W / 2, S(1060)), C["tagline"], font=F(T.FX, 64), fill=WH, anchor="mm")
    d.rounded_rectangle((S(110), S(1180), S(970), S(1290)), S(55), fill=B2)
    d.text((W / 2, S(1235)), C["cta"], font=F(T.FB, 40), fill=WH, anchor="mm")
    d.text((W / 2, S(1380)), C["email"], font=F(T.FB, 46), fill=GR, anchor="mm")
    return im
LABEL = T.card(C["label"]["text"], fill=B1, ink=WH, fs=36)

zc = C["zoom_cuts"]
def zoom_at(r): return 1.0 if max(k for k, z in enumerate(zc) if z <= r) % 2 == 0 else 1.12

def talk_frame(r, rf):
    z = zoom_at(r)
    if z > 1:
        cw, ch = W / z, H / z; x0 = S(FX_) - cw / 2; y0 = max(0, S(FY_) - ch * 0.30)
        x0 = min(max(0, x0), W - cw); y0 = min(y0, H - ch)
        img = rf.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS).convert("RGBA")
    else:
        img = rf.convert("RGBA")
    lb = C["label"]
    if lb["s"] <= r < lb["e"]:
        a = min(ease((r - lb["s"]) / 0.3), ease((lb["e"] - r) / 0.3)); T.paste_a(img, LABEL, S(70), S(300) - (1 - a) * S(20), a)
    m = C["messy"]; T.messy_to_tidy(img, r, m["t0"], m["snap"], m["end"])
    l4 = C["list4"]; T.list4(img, r, l4["ts"], l4["end"], chain_t=l4["chain"])
    ch = C["chips"]; T.chips_rows(img, r, ch["rows"], ch["end"])
    rd = C["ready"]; T.messy_to_tidy(img, r, rd["t0"], rd["snap"], rd["end"], label_b=rd["label"])
    caption(img, r, "talk")
    return img

def face_pip(rf, d=230):
    cs = S(560); x0, y0 = S(FX_) - cs // 2, S(FY_) - cs // 2; d = S(d)
    f = rf.crop((x0, y0, x0 + cs, y0 + cs)).resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255); return f, m

def gfx_frame(g, r, rf):
    img = BG.copy()
    if g["kind"] == "tree":
        items = {int(k): v for k, v in g["items"].items()}; names = {int(k): tuple(v) for k, v in g["names"].items()}
        T.tree(img, r, g["reveal"], names=names, items=items, title_a=ramp(r, g["s"], 0.4))
    elif g["kind"] == "abu":
        T.abu_flow(img, r, g["times"], glow_t=g["glow"], t_in=g["s"])
    elif g["kind"] == "inst":
        T.inst_list(img, r, g["s"], g["items"])
    f, m = face_pip(rf, 210); d = ImageDraw.Draw(img); px, py = S(820), S(140)   # sebaris dengan tajuk grafik
    d.ellipse((px - S(6), py - S(6), px + f.width + S(6), py + f.height + S(6)), fill=WH); img.paste(f, (px, py), m)
    caption(img, r, "gfx")
    return img

GFX = C["graphics"]
def gfx_at(r): return next((g for g in GFX if g["s"] <= r < g["e"]), None)

# ---------- pelan ----------
if PLAN_OUT:
    json.dump({"total": round(TOTAL, 2), "thumb": THUMB, "groups": [{"s": round(g["s"] + THUMB, 2), "e": round(g["e"] + THUMB, 2), "w": [[x["t"], x["hl"], x["o"]] for x in g["w"]]} for g in groups]},
              open(PLAN_OUT, "w"), ensure_ascii=False, indent=1)

# ---------- frame ----------
TH, EN = thumb_img(), end_img(); TH.save(OUT.replace(".mp4", "_THUMB.png"))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium" if SC < 1 else "slow", "-crf", "23" if SC < 1 else "18", "-pix_fmt", "yuv420p", OUT + ".v.mp4"], stdin=subprocess.PIPE)
XF = 0.3
for fi in range(NF):
    t = fi / FPS
    if t < THUMB: enc.stdin.write(TH.tobytes()); continue
    if t >= THUMB + D: enc.stdin.write(EN.tobytes()); continue
    r = R0 + t - THUMB; rf = raw.get(r)
    g = gfx_at(r)
    img = gfx_frame(g, r, rf) if g else talk_frame(r, rf)
    # crossfade pada sempadan babak
    for b in sorted({x["s"] for x in GFX} | {x["e"] for x in GFX}):
        if b <= r < b + XF:
            gp = gfx_at(b - 0.01)
            prev = gfx_frame(gp, r, rf) if gp else talk_frame(r, rf)
            img = Image.blend(prev, img, ease((r - b) / XF)); break
    enc.stdin.write(img.convert("RGB").tobytes())
    if fi % 300 == 0: print(f"{t:6.1f}/{TOTAL:.1f}", flush=True)
enc.stdin.close(); enc.wait()

# ---------- audio ----------
inp = ["-i", RAW, "-i", MUSIC]
fl = [f"[0:a]atrim={R0}:{R1},asetpts=PTS-STARTPTS,highpass=f=80,afftdn=nf=-28:nr=10,loudnorm=I=-14:TP=-1.5:LRA=9,adelay={int(THUMB*1000)}|{int(THUMB*1000)},apad=whole_dur={TOTAL}[v]",
      "[v]asplit=2[v1][vsc]",
      f"[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume=-27dB,afade=t=in:d=1.5,afade=t=out:st={TOTAL-2}:d=2[m0]",
      "[m0][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[m]"]
mix = ["[v1]", "[m]"]
for i, (at, f, gdb) in enumerate(C["sfx"]):
    inp += ["-i", f"{SFXD}/{f}"]; ms = int((at + THUMB) * 1000)
    fl.append(f"[{i+2}:a]volume={gdb}dB,adelay={ms}|{ms}[s{i}]"); mix.append(f"[s{i}]")
fl.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.84,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fl), "-map", "[a]", "-c:a", "pcm_s16le", OUT + ".a.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".v.mp4", "-i", OUT + ".a.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k" if SC >= 1 else "128k", "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT], check=True)
os.remove(OUT + ".v.mp4"); os.remove(OUT + ".a.wav")
print("siap", OUT)
