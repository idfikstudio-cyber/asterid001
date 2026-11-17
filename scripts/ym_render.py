"""Render video tutorial Yuran.my (talking head + mod tutorial rakaman skrin).

python3 ym_render.py <edit_dir> <raw.mp4> <broll.mp4> <brand_dir> <sfx_dir> <music.wav> <out.mp4> [scale] [plan_out.json]
scale 0.5 = preview 540x960, 1.0 = final 1080x1920.
Semua koordinat dalam config ialah ruang 1080x1920.
"""
import json, re, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ED, RAW, BROLL, BRAND, SFXD, MUSIC, OUT = sys.argv[1:8]
SC = float(sys.argv[8]) if len(sys.argv) > 8 else 0.5
PLAN_OUT = sys.argv[9] if len(sys.argv) > 9 else None
C = json.load(open(f"{ED}/config.json"))
T = json.load(open(f"{ED}/transcript.json"))
FPS = 30
W, H = int(1080 * SC), int(1920 * SC)
B1, B2, WH, INK, GR = (42, 59, 143), (41, 171, 226), (255, 255, 255), (20, 24, 50), (231, 232, 233)
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
def F(p, s): return ImageFont.truetype(p, max(8, int(s * SC)))
def S(v): return int(round(v * SC))

R0, R1 = C["raw_in"], C["raw_out"]
D = R1 - R0
THUMB, ENDC = 1.0, C["end_card"]
TOTAL = THUMB + D + ENDC
NF = int(round(TOTAL * FPS))

# ---------- kapsyen ----------
FIX = C["fix"]; FIX_AT = {round(float(k), 2): v for k, v in C["fix_at"].items()}
KEY = {k.lower() for k in C["key"]}
words = []
for s in T:
    for w in s["words"]:
        if w["s"] >= R1: continue
        raw = w["w"].strip()
        if raw.startswith("-") and words and raw.lstrip("-").lower() not in ("generate",):
            words[-1]["t"] += raw; words[-1]["e"] = w["e"]; continue
        if raw.startswith("-") and words:
            words[-1]["t"] += raw; words[-1]["e"] = w["e"]; continue
        if raw.startswith(".") and words:
            words[-1]["t"] += raw; words[-1]["e"] = w["e"]; continue
        core = re.sub(r"[^\w\-.]", "", raw).rstrip(".")
        t = raw
        if round(w["s"], 2) in FIX_AT: t = raw.replace(core, FIX_AT[round(w["s"], 2)])
        elif raw in FIX: t = FIX[raw]
        elif core in FIX: t = raw.replace(core, FIX[core])
        words.append({"t": t, "s": w["s"], "e": w["e"]})
for w in words:
    c = re.sub(r"[^\w\-.]", "", w["t"]).rstrip(".").lower()
    w["hl"] = c in KEY or c.split("-")[0] in KEY
# kumpulan 1-4 perkataan, pecah pada tanda baca / jeda
groups = []; cur = []
for i, w in enumerate(words):
    cur.append(w)
    txt = " ".join(x["t"] for x in cur)
    nxt = words[i + 1] if i + 1 < len(words) else None
    brk = (w["t"][-1] in ",.?!" or len(cur) >= 4 or len(txt) >= 18 or (nxt and nxt["s"] - w["e"] > 0.25) or nxt is None)
    if brk:
        groups.append({"s": cur[0]["s"], "e": cur[-1]["e"], "w": [dict(x) for x in cur]}); cur = []
for i, g in enumerate(groups):
    nx = groups[i + 1]["s"] if i + 1 < len(groups) else g["e"] + 0.4
    g["e"] = min(max(g["e"] + 0.15, g["s"] + 0.5), nx)
    for x in g["w"]: x["t"] = x["t"].rstrip(",.")

# ---------- babak tutorial ----------
STEPS = C["steps"]
def step_at(r):
    for st in STEPS:
        if st["r0"] <= r < st["r1"]: return st
    return None
def broll_t(st, r):
    m = st["map"]
    for (a, ba), (b, bb) in zip(m, m[1:]):
        if a <= r <= b: return ba + (bb - ba) * (r - a) / max(1e-6, b - a)
    return m[-1][1]

# ---------- aset pra-render ----------
def rr_mask(w, h, rad):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), rad, fill=255); return m
CS = 0.80
CW, CH = int(W * CS), int(H * CS)
CX, CY = (W - CW) // 2, S(250)
CARD_MASK = rr_mask(CW, CH, S(44))
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((CX, CY + S(14), CX + CW, CY + CH + S(14)), S(44), fill=(0, 0, 0, 120))
SHADOW = shadow.filter(ImageFilter.GaussianBlur(S(22)))

def pill_img(n, title):
    f1, f2 = F(FX, 46), F(FB, 40)
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    nw, tw = d0.textlength(str(n), font=f1), d0.textlength(title, font=f2)
    w, h = int(nw + tw + S(150)), S(90)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=WH)
    d.ellipse((S(8), S(8), S(82), S(82)), fill=B2)
    d.text((S(45), h // 2), str(n), font=f1, fill=WH, anchor="mm")
    d.text((S(98), h // 2), title, font=f2, fill=B1, anchor="lm")
    return im
PILLS = {(st["n"], st["title"]): pill_img(st["n"], st["title"]) for st in STEPS}

def chip_label(text, bg=B2, fs=38):
    f = F(FX, fs); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1))); tw = d0.textlength(text, font=f)
    w, h = int(tw + S(56)), S(fs * 1.85)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg); d.text((w / 2, h / 2), text, font=f, fill=WH, anchor="mm")
    return im

LOGO_W = Image.open(f"{BRAND}/logo_white.png").convert("RGBA")

def thumb_img():
    im = Image.open(os.environ["THUMB_SRC"]).convert("RGB").resize((W, H))
    g = Image.new("L", (1, H), 0)
    for y in range(int(H * 0.47), H): g.putpixel((0, y), int(235 * (y - H * 0.47) / (H * 0.53)))
    im.paste(Image.new("RGB", (W, H), INK), (0, 0), g.resize((W, H))); d = ImageDraw.Draw(im)
    y = S(1020)
    for t, k in C["hook"]:
        if k == "pill":
            f = F(FX, 50); tw = d.textlength(t, font=f)
            d.rounded_rectangle((S(80), y, S(80) + tw + S(60), y + S(80)), S(40), fill=B2)
            d.text((S(110), y + S(40)), t, font=f, fill=WH, anchor="lm"); y += S(110)
        else:
            d.text((S(80), y), t, font=F(FX, 96), fill=B2 if k == "a" else WH, stroke_width=S(4), stroke_fill=INK); y += S(108)
    return im

def end_img():
    im = Image.new("RGB", (W, H), B1); d = ImageDraw.Draw(im)
    lw = S(560); lg = LOGO_W.resize((lw, int(lw * LOGO_W.height / LOGO_W.width)), Image.LANCZOS)
    im.paste(lg, ((W - lw) // 2, S(640)), lg)
    d.text((W / 2, S(1060)), C["tagline"], font=F(FX, 64), fill=WH, anchor="mm")
    d.rounded_rectangle((S(110), S(1180), S(970), S(1290)), S(55), fill=B2)
    d.text((W / 2, S(1235)), C["cta"], font=F(FB, 40), fill=WH, anchor="mm")
    d.text((W / 2, S(1380)), C["email"], font=F(FB, 46), fill=GR, anchor="mm")
    return im

# ---------- pembaca video berurutan ----------
class Reader:
    def __init__(self, path, vf, ss=0.0):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path, "-vf", f"{vf},fps={FPS},scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.idx, self.ss, self.frame = -1, ss, None
    def get(self, t):
        want = max(0, int(round((t - self.ss) * FPS)))
        while self.idx < want:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            self.frame = b; self.idx += 1
        return Image.frombuffer("RGB", (W, H), self.frame)
GRADE = "eq=contrast=1.04:brightness=0.015:saturation=1.05:gamma=1.02,unsharp=5:5:0.3"
raw = Reader(RAW, GRADE, 0.0)
br = Reader(BROLL, "null", 0.0)

# ---------- penolong lukisan ----------
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def caption(img, r, mode):
    g = next((g for g in groups if g["s"] <= r < g["e"]), None)
    if not g: return
    d = ImageDraw.Draw(img); f = F(FX, 66 if mode == "talk" else 56)
    sp = d.textlength(" ", font=f)
    ws = [(x["t"], x["hl"]) for x in g["w"]]
    tw = sum(d.textlength(t, font=f) for t, _ in ws) + sp * (len(ws) - 1)
    maxw = S(900) if mode == "talk" else S(640)
    if tw > maxw: f = F(FX, (66 if mode == "talk" else 56) * maxw / tw); sp = d.textlength(" ", font=f); tw = maxw
    cx, cy = (W / 2, S(1340)) if mode == "talk" else (S(650), S(1390))
    if mode == "tut":
        d.rounded_rectangle((cx - tw / 2 - S(26), cy - S(46), cx + tw / 2 + S(26), cy + S(46)), S(22), fill=INK)
    x = cx - tw / 2
    for t, hl in ws:
        d.text((x, cy), t, font=f, fill=B2 if hl else WH, anchor="lm", stroke_width=S(7) if mode == "talk" else 0, stroke_fill=INK)
        x += d.textlength(t, font=f) + sp

def paste_a(img, ov, x, y, a=1.0):
    if a <= 0: return
    if a < 1:
        ov = ov.copy(); ov.putalpha(ov.getchannel("A").point(lambda v: int(v * a)))
    img.paste(ov, (int(x), int(y)), ov)

def ring(img, cx, cy, r, ph, label, a):
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    k = r + S(10) + ph * S(40); al = int(160 * (1 - ph) * a)
    d.ellipse((cx - k, cy - k, cx + k, cy + k), outline=B2 + (al,), width=S(8))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=B2 + (int(45 * a),), outline=B2 + (int(255 * a),), width=S(10))
    img.alpha_composite(o)
    if label:
        lb = chip_label(label, fs=38 if len(label) > 2 else 48)
        lx = min(max(cx - lb.width / 2, S(30)), W - lb.width - S(30))
        ly = cy + r + S(22) if cy + r + S(110) < H * 0.78 else cy - r - lb.height - S(22)
        paste_a(img, lb, lx, ly, a)

def blur_boxes(fr, bt):
    for b in C["blur"]:
        if b["b0"] <= bt <= b["b1"]:
            x0, y0, x1, y1 = [S(v) for v in b["box"]]
            reg = fr.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(S(16)))
            fr.paste(reg, (x0, y0))
    return fr

def face_pip(rf):
    cs = S(560); x0, y0 = S(550) - cs // 2, S(760) - cs // 2
    d = S(230); f = rf.crop((x0, y0, x0 + cs, y0 + cs)).resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    return f, m

zc = C["zoom_cuts"]
def zoom_at(r):
    i = max(k for k, z in enumerate(zc) if z <= r)
    return 1.0 if i % 2 == 0 else 1.12

ICON = {}
def icon_card(text):
    if text not in ICON:
        f = F(FB, 40); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1))); tw = d0.textlength(text, font=f)
        w, h = int(tw + S(110)), S(84)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=WH)
        d.ellipse((S(14), S(16), S(66), S(68)), fill=B2)
        d.line((S(28), S(43), S(37), S(52), S(54), S(32)), fill=WH, width=S(6))
        d.text((S(82), h // 2), text, font=f, fill=B1, anchor="lm")
        ICON[text] = im
    return ICON[text]

def chip_store(dev, store):
    w, h = S(760), S(120)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), S(30), fill=WH)
    d.rounded_rectangle((0, 0, S(280), h - 1), S(30), fill=B1)
    d.text((S(140), h / 2), dev, font=F(FX, 44), fill=WH, anchor="mm")
    d.text((S(520), h / 2), store, font=F(FB, 48), fill=B1, anchor="mm")
    return im
CHIPS = [chip_store(c["dev"], c["store"]) for c in C["chips"]]
LABEL = chip_label(C["label"]["text"], bg=B1, fs=40)

# ---------- pelan untuk halaman preview ----------
plan = {"total": round(TOTAL, 2), "thumb": THUMB, "groups": [{"s": round(g["s"] + THUMB, 2), "e": round(g["e"] + THUMB, 2), "w": [[x["t"], x["hl"]] for x in g["w"]]} for g in groups],
        "steps": [{"n": s["n"], "title": s["title"], "s": round(s["r0"] + THUMB, 2), "e": round(s["r1"] + THUMB, 2), "b0": s["map"][0][1], "b1": s["map"][-1][1]} for s in STEPS],
        "taps": [{"t": round(tp["r"] + THUMB, 2), "label": tp["label"]} for tp in C["taps"]]}
if PLAN_OUT: json.dump(plan, open(PLAN_OUT, "w"), ensure_ascii=False, indent=1)

# ---------- gelung frame ----------
THUMB_IMG, END_IMG = thumb_img(), end_img()
THUMB_IMG.save(OUT.replace(".mp4", "_THUMB.png"))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium" if SC < 1 else "slow", "-crf", "23" if SC < 1 else "18", "-pix_fmt", "yuv420p", OUT + ".v.mp4"], stdin=subprocess.PIPE)
prev_mode = None; mode_t0 = 0.0
for fi in range(NF):
    t = fi / FPS
    if t < THUMB:
        enc.stdin.write(THUMB_IMG.tobytes()); continue
    if t >= THUMB + D:
        enc.stdin.write(END_IMG.tobytes()); continue
    r = R0 + t - THUMB
    rf = raw.get(r)
    st = step_at(r)
    mode = "tut" if st else "talk"
    if mode != prev_mode: mode_t0, prev_mode = r, mode
    if mode == "talk":
        z = zoom_at(r)
        if z > 1:
            cw, ch = W / z, H / z; x0 = (W - cw) / 2 + S(10); y0 = S(110)
            img = rf.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS).convert("RGBA")
        else:
            img = rf.convert("RGBA")
        # label nama
        lb = C["label"]
        if lb["s"] <= r < lb["e"]:
            a = min(ease((r - lb["s"]) / 0.3), ease((lb["e"] - r) / 0.3)); paste_a(img, LABEL, S(70), S(300) - (1 - a) * S(20), a)
        # ikon manfaat
        for i, ic in enumerate(C["icons"]):
            if ic["r"] <= r < C["icons_end"]:
                a = min(ease((r - ic["r"]) / 0.25), ease((C["icons_end"] - r) / 0.3)); card = icon_card(ic["text"])
                paste_a(img, card, S(70) - (1 - a) * S(40), S(820) + i * S(110), a)
        for i, c in enumerate(C["chips"]):
            if c["r"] <= r < C["chips_end"]:
                a = min(ease((r - c["r"]) / 0.25), ease((C["chips_end"] - r) / 0.3))
                paste_a(img, CHIPS[i], S(160), S(860) + i * S(150) + (1 - a) * S(30), a)
        for k in ("resit_card", "anywhere_card"):
            rc = C[k]
            if rc["r"] <= r < rc["e"]:
                a = min(ease((r - rc["r"]) / 0.25), ease((rc["e"] - r) / 0.3)); card = icon_card(rc["text"])
                paste_a(img, card, (W - card.width) / 2, S(930) + (1 - a) * S(30), a)
        if mode_t0 > 0 and r - mode_t0 < 0.25:   # masuk semula dari tutorial: fade ringkas
            pass
        caption(img, r, "talk")
    else:
        bt = broll_t(st, r)
        sf = blur_boxes(br.get(bt).copy(), bt)
        bg = sf.resize((W // 10, H // 10)).filter(ImageFilter.GaussianBlur(3)).resize((W, H))
        img = Image.blend(bg, Image.new("RGB", (W, H), B1), 0.82).convert("RGBA")
        img.alpha_composite(SHADOW)
        k = ease((r - mode_t0) / 0.35) if r - mode_t0 < 0.35 else 1.0
        card = sf.resize((CW, CH))
        if k < 1:
            sc = 0.92 + 0.08 * k; cw2, ch2 = int(CW * sc), int(CH * sc)
            c2 = card.resize((cw2, ch2)); m2 = CARD_MASK.resize((cw2, ch2))
            img.paste(c2, ((W - cw2) // 2, CY + (CH - ch2) // 2), m2)
        else:
            img.paste(card, (CX, CY), CARD_MASK)
        def P(x, y): return CX + S(x) * CS, CY + S(y) * CS
        # PIC berkelip
        pc = C["pic"]
        if pc["r"] <= r < pc["e"]:
            on = (int((r - pc["r"]) * 2.5) % 2 == 0)
            x0, y0 = P(pc["x0"], pc["y0"]); x1, y1 = P(pc["x1"], pc["y1"])
            o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
            d.rounded_rectangle((x0 - S(12), y0 - S(10), x1 + S(12), y1 + S(10)), S(16), outline=B2 + ((255 if on else 90),), width=S(8), fill=B2 + ((50 if on else 15),))
            img.alpha_composite(o)
            lbp = chip_label(pc["label"], fs=36); paste_a(img, lbp, (W - lbp.width) / 2, y1 + S(30), 1.0)
        # kad nota
        nt = C["note"]
        if nt["r"] <= r < nt["e"]:
            a = min(ease((r - nt["r"]) / 0.25), ease((nt["e"] - r) / 0.3)); card = icon_card(nt["text"])
            paste_a(img, card, (W - card.width) / 2, S(1100) + (1 - a) * S(30), a)
        # bulatan klik
        for tp in C["taps"]:
            dt = r - tp["r"]
            if -0.25 <= dt < 1.1:
                a = ease((dt + 0.25) / 0.25) if dt < 0 else (1.0 if dt < 0.85 else max(0.0, 1 - (dt - 0.85) / 0.25))
                ph = ((dt + 0.25) % 0.6) / 0.6
                cx, cy = P(tp["x"], tp["y"]); ring(img, cx, cy, S(tp["rad"]) * CS / 0.8 * 0.8, ph, tp["label"], a)
        # pil langkah
        pl = PILLS[(st["n"], st["title"])]
        paste_a(img, pl, (W - pl.width) / 2, S(110))
        # PIP Farhan
        f, m = face_pip(rf)
        d = ImageDraw.Draw(img); px, py = S(40), S(1250)
        d.ellipse((px - S(6), py - S(6), px + f.width + S(6), py + f.height + S(6)), fill=WH)
        img.paste(f, (px, py), m)
        caption(img, r, "tut")
    enc.stdin.write(img.convert("RGB").tobytes())
    if fi % 300 == 0: print(f"{t:6.1f}/{TOTAL:.1f}", flush=True)
enc.stdin.close(); enc.wait()

# ---------- audio ----------
sfx = []
for tp in C["taps"]: sfx.append((tp["r"] + THUMB - 0.05, "click.wav", -6))
for ic in C["icons"]: sfx.append((ic["r"] + THUMB, "pop.wav", -10))
for c in C["chips"]: sfx.append((c["r"] + THUMB, "tick.wav", -8))
sfx.append((C["note"]["r"] + THUMB, "pop.wav", -10))
sfx.append((C["resit_card"]["r"] + THUMB, "pop.wav", -10))
sfx.append((140.4 + THUMB, "ding.wav", -12))
inp = ["-i", RAW, "-i", MUSIC]; fl = []
fl.append(f"[0:a]atrim={R0}:{R1},asetpts=PTS-STARTPTS,highpass=f=80,afftdn=nf=-28:nr=10,loudnorm=I=-14:TP=-1.5:LRA=9,adelay={int(THUMB*1000)}|{int(THUMB*1000)},apad=whole_dur={TOTAL}[v]")
fl.append("[v]asplit=2[v1][vsc]")
fl.append(f"[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume=-27dB,afade=t=in:d=1.5,afade=t=out:st={TOTAL-2}:d=2[m0]")
fl.append("[m0][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[m]")
mix = ["[v1]", "[m]"]
for i, (at, f, g) in enumerate(sfx):
    inp += ["-i", f"{SFXD}/{f}"]
    fl.append(f"[{i+2}:a]volume={g}dB,adelay={int(at*1000)}|{int(at*1000)}[s{i}]"); mix.append(f"[s{i}]")
fl.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.89,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fl), "-map", "[a]", "-c:a", "pcm_s16le", OUT + ".a.wav"], check=True)
# normalize akhir -14 LUFS / -1 dBTP
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".v.mp4", "-i", OUT + ".a.wav", "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k" if SC >= 1 else "128k", "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT], check=True)
os.remove(OUT + ".v.mp4"); os.remove(OUT + ".a.wav")
print("siap", OUT)
