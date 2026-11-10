# YM-F-010 render: python3 render.py <dl_dir> <out.mp4> [W]   (W=540 preview, 1080 final)
import json, os, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
DL, OUT = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 540
H = W * 16 // 9
FPS = 30
FINAL = W >= 1080
P = json.load(open(os.path.join(HERE, "plan.json")))
DUR, TH, BODY = P["dur"], P["thumb"], P["body_dur"]
SFXDIR = os.path.join(HERE, "..", "..", "edit", "sfx")

NAVY = (42, 59, 143); ACC = (41, 171, 226); INK = (35, 31, 32); GREY = (231, 232, 233); WHITE = (255, 255, 255)
OK = (31, 157, 85); WARN = (232, 163, 23); BAD = (217, 54, 79)
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(w, px):
    k = (w, int(px))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + f"Inter-{w}.otf", int(px))
    return _fc[k]
u = lambda f: f * W  # unit relatif lebar

GRADE = "eq=brightness=0.015:contrast=1.04:saturation=1.06" + (",unsharp=5:5:0.25" if FINAL else "")
C0, C1 = P["cuts"][0]

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def pop(t, t0, d=0.18):
    x = (t - t0) / d
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return ease(x) * (1 + 0.1 * math.sin(math.pi * x))

def rr(d, box, r, **kw): d.rounded_rectangle([round(v) for v in box], radius=round(r), **kw)

def text_w(f, s): return f.getlength(s)

# ---------- pembaca frame ----------
class Reader:
    def __init__(self, args, w=W, h=H):
        self.n = w * h * 3; self.w, self.h = w, h
        self.p = subprocess.Popen(["ffmpeg", "-v", "error"] + args + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None
    def read(self):
        b = self.p.stdout.read(self.n)
        if len(b) == self.n: self.last = Image.frombytes("RGB", (self.w, self.h), b)
        return self.last.copy() if self.last else Image.new("RGB", (self.w, self.h))
    def close(self):
        try: self.p.stdout.close(); self.p.kill()
        except Exception: pass

RAW = os.path.join(DL, "raw.mp4")
body = Reader(["-i", RAW, "-vf", f"select='not(between(t,{C0},{C1}))',setpts=N/{FPS}/TB,fps={FPS},{GRADE},scale={W}:{H}:flags=lanczos"])

def zoom_img(im, z, ax=0.5, ay=0.25, out=None):
    if abs(z - 1) < 1e-3: return im
    w, h = im.size; cw, ch = w / z, h / z
    x0 = ax * w - ax * cw; y0 = ay * h - ay * ch
    return im.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def zoom_at(t):
    z = 1.0
    for t0, zz in P["zoom"]:
        if t >= t0: z = zz
    return z

# ---------- B-roll ----------
class Broll:
    def __init__(self, b):
        self.b = b; cx, cy, cw, ch = b["crop"]
        dur = b["e"] - b["s"] + 0.3
        self.r = Reader(["-ss", str(b["at"]), "-i", os.path.join(DL, b["file"]), "-t", f"{dur:.2f}",
                         "-vf", f"fps={FPS},crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos"])
    def map(self, x, y, kb):
        cx, cy, cw, ch = self.b["crop"]
        X = (x - cx) * W / cw; Y = (y - cy) * H / ch
        return (X - W / 2) * kb + W / 2, (Y - H / 2) * kb + H / 2
    def frame(self, t):
        b = self.b; im = self.r.read(); ct = b["at"] + (t - b["s"])
        cx, cy, cw, ch = b["crop"]
        for x0, y0, x1, y1, f0, f1 in b["blur"]:
            if f0 <= ct <= f1:
                X0 = max(0, (x0 - cx) * W / cw); Y0 = max(0, (y0 - cy) * H / ch)
                X1 = min(W, (x1 - cx) * W / cw); Y1 = min(H, (y1 - cy) * H / ch)
                if X1 - X0 > 2 and Y1 - Y0 > 2:
                    box = tuple(int(v) for v in (X0, Y0, X1, Y1))
                    reg = im.crop(box).filter(ImageFilter.GaussianBlur(u(0.022)))
                    im.paste(reg, box)
        k0, k1 = b["kb"]; prog = (t - b["s"]) / max(0.01, b["e"] - b["s"])
        kb = k0 + (k1 - k0) * prog
        im = zoom_img(im, kb, 0.5, 0.5)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for c0, c1, ra, rb in b["callout"]:
            if c0 <= ct <= c1:
                f = (ct - c0) / max(0.01, c1 - c0)
                r = [ra[i] + (rb[i] - ra[i]) * f for i in range(4)]
                p0 = self.map(r[0], r[1], kb); p1 = self.map(r[2], r[3], kb)
                a = ease((ct - c0) / 0.2)
                grow = u(0.02) * (1 - a)
                box = (p0[0] - grow, p0[1] - grow, p1[0] + grow, p1[1] + grow)
                rr(d, box, u(0.025), outline=ACC + (int(255 * a),), width=max(2, round(u(0.008))))
                rr(d, (box[0] - u(0.008), box[1] - u(0.008), box[2] + u(0.008), box[3] + u(0.008)), u(0.03),
                   outline=ACC + (int(90 * a),), width=max(1, round(u(0.006))))
        im = im.convert("RGBA"); im.alpha_composite(lay)
        if b.get("label"): draw_tag(im, b["label"], t - b["s"])
        return im.convert("RGB")

def draw_tag(im, s, lt):
    a = ease(lt / 0.25)
    d = ImageDraw.Draw(im)
    f = font("SemiBold", u(0.034)); tw = text_w(f, s)
    x, y = u(0.06), H * 0.625 + u(0.02) * (1 - a)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    rr(dl, (x, y, x + tw + u(0.06), y + u(0.07)), u(0.035), fill=NAVY + (int(235 * a),))
    dl.text((x + u(0.03), y + u(0.035)), s, font=f, fill=WHITE + (int(255 * a),), anchor="lm")
    im.alpha_composite(lay)

# ---------- caption ----------
def draw_caption(lay, t):
    c = next((c for c in P["caps"] if c["s"] <= t < c["e"]), None)
    if not c: return
    d = ImageDraw.Draw(lay)
    size = u(0.075); f = font("ExtraBold", size)
    parts = [w["t"] for w in c["w"]]
    total = text_w(f, " ".join(parts)) + (len(parts) - 1) * size * 0.1
    maxw = W * 0.74
    if total > maxw:
        size *= maxw / total; f = font("ExtraBold", size); total = text_w(f, " ".join(parts)) + (len(parts) - 1) * size * 0.1
    s = pop(t, c["s"], 0.12); sc = 0.92 + 0.08 * min(s, 1.0)
    cx, cy = W * 0.46, H * 0.728
    sw = max(2, round(size * 0.11))
    x = cx - total / 2
    for w in c["w"]:
        txt = w["t"]; col = ACC if w["hl"] else WHITE
        d.text((x, cy + (1 - sc) * size), txt, font=f, fill=col + (255,), anchor="lm", stroke_width=sw, stroke_fill=(15, 18, 40, 235))
        x += text_w(f, txt + " ") + sw * 0.9

# ---------- grafik ----------
def card(d, box, a, fill=WHITE):
    rr(d, (box[0], box[1] + u(0.012), box[2], box[3] + u(0.012)), u(0.04), fill=(10, 15, 50, int(60 * a)))
    rr(d, box, u(0.04), fill=fill + (int(250 * a),))

def check(d, cx, cy, s, col, a, wd=None):
    wd = wd or max(2, round(s * 0.22))
    d.line([(cx - s * 0.45, cy), (cx - s * 0.12, cy + s * 0.33), (cx + s * 0.5, cy - s * 0.38)], fill=col + (int(255 * a),), width=wd, joint="curve")

def cross(d, cx, cy, s, col, a):
    wd = max(2, round(s * 0.22))
    d.line([(cx - s * .4, cy - s * .4), (cx + s * .4, cy + s * .4)], fill=col + (int(255 * a),), width=wd)
    d.line([(cx - s * .4, cy + s * .4), (cx + s * .4, cy - s * .4)], fill=col + (int(255 * a),), width=wd)

def g_label(d, lay, g, t):
    a = ease((t - g["s"]) / 0.25) * (1 - ease((t - (g["e"] - 0.25)) / 0.25))
    s = "Farhan · Yuran.my"; f = font("SemiBold", u(0.034)); tw = text_w(f, s)
    x, y = u(0.06) - u(0.03) * (1 - a), H * 0.115
    rr(d, (x, y, x + tw + u(0.06), y + u(0.07)), u(0.035), fill=NAVY + (int(235 * a),))
    d.text((x + u(0.03), y + u(0.035)), s, font=f, fill=WHITE + (int(255 * a),), anchor="lm")

def fade(t, g, fi=0.2, fo=0.2): return ease((t - g["s"]) / fi) * (1 - ease((t - (g["e"] - fo)) / fo))

def g_status(d, lay, g, t):
    A = fade(t, g)
    f = font("Bold", u(0.05)); y = H * 0.465
    for i, (name, t0, kind) in enumerate(P["status"]):
        p = pop(t, t0 - 0.08, 0.2)
        if p <= 0: continue
        a = min(1, p) * A; col = {"ok": OK, "warn": WARN, "bad": BAD}[kind]
        x = u(0.08) + u(0.03) * (1 - min(1, p)); yy = y + i * u(0.13)
        tw = text_w(f, name); h = u(0.1)
        rr(d, (x, yy + u(0.01), x + tw + u(0.18), yy + h + u(0.01)), h / 2, fill=(10, 15, 50, int(60 * a)))
        rr(d, (x, yy, x + tw + u(0.18), yy + h), h / 2, fill=WHITE + (int(250 * a),))
        d.ellipse((x + u(0.022), yy + u(0.022), x + u(0.078), yy + h - u(0.022)), fill=col + (int(255 * a),))
        if kind == "ok": check(d, x + u(0.05), yy + h / 2, u(0.032), WHITE, a)
        elif kind == "warn": d.text((x + u(0.05), yy + h / 2), "!", font=font("Black", u(0.04)), fill=WHITE + (int(255 * a),), anchor="mm")
        else:
            d.line([(x + u(0.05), yy + h / 2 - u(0.014)), (x + u(0.05), yy + h / 2)], fill=WHITE + (int(255 * a),), width=max(2, round(u(0.007))))
            d.line([(x + u(0.05), yy + h / 2), (x + u(0.062), yy + h / 2 + u(0.008))], fill=WHITE + (int(255 * a),), width=max(2, round(u(0.007))))
        d.text((x + u(0.105), yy + h / 2), name, font=f, fill=INK + (int(255 * a),), anchor="lm")

def receipt(d, x, y, s, a):
    pts = [(x, y), (x + s * .7, y), (x + s * .7, y + s)]
    n = 5
    for i in range(n + 1):
        pts.append((x + s * .7 - i * s * .7 / n, y + s - (s * .08 if i % 2 else 0)))
    pts.append((x, y))
    d.polygon(pts, fill=GREY + (int(255 * a),), outline=NAVY + (int(255 * a),))
    for i in range(3):
        d.line([(x + s * .12, y + s * (.22 + i * .2)), (x + s * .58, y + s * (.22 + i * .2))], fill=NAVY + (int(200 * a),), width=max(1, round(s * .05)))

def g_manual(d, lay, g, t):
    A = fade(t, g) * min(1, pop(t, g["s"]))
    x0, y0, x1, y1 = u(0.16), H * 0.50, u(0.80), H * 0.50 + u(0.2)
    card(d, (x0, y0, x1, y1), A)
    receipt(d, x0 + u(0.05), y0 + u(0.05), u(0.11), A)
    f = font("Bold", u(0.055)); d.text((x0 + u(0.2), (y0 + y1) / 2), "Resit manual", font=f, fill=INK + (int(255 * A),), anchor="lm")
    t0 = g["s"] + 0.55
    if t > t0:
        k = ease((t - t0) / 0.2)
        d.line([(x0 + u(0.2), (y0 + y1) / 2), (x0 + u(0.2) + (u(0.37)) * k, (y0 + y1) / 2)], fill=BAD + (int(255 * A),), width=max(2, round(u(0.01))))
        cross(d, x1 - u(0.02), y0 + u(0.02), u(0.06) * pop(t, t0), BAD, A)

def g_attend(d, lay, g, t):
    A = fade(t, g) * min(1, pop(t, g["s"]))
    x0, y0, x1 = u(0.14), H * 0.44, u(0.78)
    rh = u(0.085); hd = u(0.1); y1 = y0 + hd + rh * 4 + u(0.03)
    card(d, (x0, y0, x1, y1), A)
    rr(d, (x0, y0, x1, y0 + hd), u(0.04), fill=NAVY + (int(250 * A),), corners=(True, True, False, False))
    d.text((x0 + u(0.05), y0 + hd / 2), "Kehadiran", font=font("Bold", u(0.045)), fill=WHITE + (int(255 * A),), anchor="lm")
    bars = [0.28, 0.34, 0.24, 0.31]
    for i in range(4):
        yy = y0 + hd + u(0.015) + i * rh; cy = yy + rh / 2
        d.ellipse((x0 + u(0.04), cy - u(0.032), x0 + u(0.104), cy + u(0.032)), fill=GREY + (int(255 * A),))
        rr(d, (x0 + u(0.13), cy - u(0.015), x0 + u(0.13) + u(bars[i]), cy + u(0.015)), u(0.015), fill=GREY + (int(255 * A),))
        bx = x1 - u(0.12)
        box = (bx, cy - u(0.035), bx + u(0.07), cy + u(0.035))
        tt = P["ticks"][i] if i < 3 else P["cross"]
        if t >= tt:
            p = min(1, pop(t, tt, 0.15)); col = OK if i < 3 else BAD
            rr(d, box, u(0.012), fill=col + (int(255 * A),))
            if i < 3: check(d, bx + u(0.035), cy, u(0.04) * p, WHITE, A)
            else: cross(d, bx + u(0.035), cy, u(0.04) * p, WHITE, A)
        else:
            rr(d, box, u(0.012), outline=(150, 155, 170, int(255 * A)), width=max(2, round(u(0.005))))

def docicon(d, x, y, s, a, col=ACC):
    f = s * 0.28
    d.polygon([(x, y), (x + s * .75 - f, y), (x + s * .75, y + f), (x + s * .75, y + s), (x, y + s)], fill=col + (int(255 * a),))
    d.polygon([(x + s * .75 - f, y), (x + s * .75, y + f), (x + s * .75 - f, y + f)], fill=(200, 235, 250, int(255 * a)))
    for i in range(2):
        d.line([(x + s * .14, y + s * (.5 + i * .2)), (x + s * .6, y + s * (.5 + i * .2))], fill=WHITE + (int(230 * a),), width=max(1, round(s * .07)))

def dlicon(d, cx, cy, s, a):
    wd = max(2, round(s * 0.14)); c = NAVY + (int(255 * a),)
    d.line([(cx, cy - s * .45), (cx, cy + s * .15)], fill=c, width=wd)
    d.line([(cx - s * .3, cy - s * .12), (cx, cy + s * .18), (cx + s * .3, cy - s * .12)], fill=c, width=wd, joint="curve")
    d.line([(cx - s * .4, cy + s * .42), (cx + s * .4, cy + s * .42)], fill=c, width=wd)

def g_docs(d, lay, g, t):
    A = fade(t, g) * min(1, pop(t, g["s"]))
    # grid 2 lajur di paras dada supaya muka Farhan tidak ditutup
    x0, y0, x1 = u(0.08), H * 0.44, u(0.84)
    hd = u(0.1); rh = u(0.1); gap = u(0.02)
    y1 = y0 + hd + gap + rh * 3 + gap * 2 + u(0.02)
    card(d, (x0, y0, x1, y1), A)
    rr(d, (x0, y0, x1, y0 + hd), u(0.04), fill=NAVY + (int(250 * A),), corners=(True, True, False, False))
    docicon(d, x0 + u(0.045), y0 + u(0.022), u(0.056), A, WHITE)
    d.text((x0 + u(0.115), y0 + hd / 2), "Dokumen", font=font("Bold", u(0.045)), fill=WHITE + (int(255 * A),), anchor="lm")
    dl_a = A
    d.line([(x1 - u(0.06), y0 + hd * .28), (x1 - u(0.06), y0 + hd * .6)], fill=WHITE + (int(255 * dl_a),), width=max(2, round(u(0.007))))
    d.line([(x1 - u(0.08), y0 + hd * .48), (x1 - u(0.06), y0 + hd * .64), (x1 - u(0.04), y0 + hd * .48)], fill=WHITE + (int(255 * dl_a),), width=max(2, round(u(0.007))))
    d.line([(x1 - u(0.085), y0 + hd * .76), (x1 - u(0.035), y0 + hd * .76)], fill=WHITE + (int(255 * dl_a),), width=max(2, round(u(0.007))))
    cw = (x1 - x0 - u(0.04) - gap) / 2
    for i, (name, t0) in enumerate(P["docs"]):
        if t < t0 - 0.08: continue
        p = min(1, pop(t, t0 - 0.08, 0.18)); a = A * p
        col, row = i % 2, i // 2
        cx0 = x0 + u(0.02) + col * (cw + gap); cy0 = y0 + hd + gap + row * (rh + gap)
        dy = u(0.02) * (1 - p)
        rr(d, (cx0, cy0 + dy, cx0 + cw, cy0 + rh + dy), u(0.025), fill=(234, 246, 252, int(255 * a)))
        docicon(d, cx0 + u(0.025), cy0 + dy + rh / 2 - u(0.03), u(0.06), a)
        f = font("SemiBold", u(0.04))
        if text_w(f, name) > cw - u(0.1): f = font("SemiBold", u(0.04) * (cw - u(0.1)) / text_w(f, name))
        d.text((cx0 + u(0.085), cy0 + dy + rh / 2), name, font=f, fill=INK + (int(255 * a),), anchor="lm")

LOGO = Image.open(os.path.join(DL, "logo_white.png")).convert("RGBA")
def paste_logo(lay, cx, cy, w, a):
    lg = LOGO.resize((round(w), round(w * LOGO.height / LOGO.width)), Image.LANCZOS)
    if a < 1:
        al = lg.split()[3].point(lambda v: int(v * a)); lg.putalpha(al)
    lay.alpha_composite(lg, (round(cx - lg.width / 2), round(cy - lg.height / 2)))

def g_logo(d, lay, g, t):
    p = pop(t, g["s"], 0.2); A = fade(t, g, 0.15, 0.2)
    if p <= 0: return
    w = u(0.46) * (0.85 + 0.15 * min(p, 1.05)); h = w * 0.42
    cx, cy = W * 0.46, H * 0.56
    rr(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=NAVY + (int(245 * A),))
    paste_logo(lay, cx, cy, w * 0.62, A)

def g_comment(d, lay, g, t):
    A = fade(t, g) * min(1, pop(t, g["s"]))
    cx, cy, w, h = W * 0.46, H * 0.55, u(0.34), u(0.2)
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    rr(d, (box[0], box[1] + u(0.012), box[2], box[3] + u(0.012)), u(0.06), fill=(10, 15, 50, int(60 * A)))
    rr(d, box, u(0.06), fill=WHITE + (int(250 * A),), outline=NAVY + (int(255 * A),), width=max(2, round(u(0.008))))
    d.polygon([(cx - w * .25, box[3] - 2), (cx - w * .1, box[3] - 2), (cx - w * .3, box[3] + u(0.06))], fill=WHITE + (int(250 * A),))
    d.line([(cx - w * .1, box[3]), (cx - w * .3, box[3] + u(0.06)), (cx - w * .25, box[3])], fill=NAVY + (int(255 * A),), width=max(2, round(u(0.008))))
    for i in range(3):
        ph = (t * 3 - i * 0.33) % 1
        o = u(0.015) * max(0, math.sin(ph * math.pi * 2))
        r = u(0.022); x = cx + (i - 1) * u(0.08)
        d.ellipse((x - r, cy - r - o, x + r, cy + r - o), fill=ACC + (int(255 * A),))

def g_cta(d, lay, g, t):
    A = fade(t, g, 0.2, 0.25) * min(1, pop(t, g["s"]))
    f = font("Bold", u(0.052)); s = "Sesi demo Yuran.my"; tw = text_w(f, s)
    cx, cy = W * 0.46, H * 0.53; h = u(0.12); w = tw + u(0.14)
    tap = t - (g["s"] + 0.15); press = 0.96 if 0 < tap < 0.12 else 1.0
    bw, bh = w * press, h * press
    rr(d, (cx - bw / 2, cy - bh / 2 + u(0.012), cx + bw / 2, cy + bh / 2 + u(0.012)), bh / 2, fill=(10, 15, 50, int(70 * A)))
    rr(d, (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), bh / 2, fill=ACC + (int(255 * A),))
    d.text((cx, cy), s, font=f, fill=WHITE + (int(255 * A),), anchor="mm")
    if 0 < tap < 0.6:
        r = u(0.04) + u(0.12) * ease(tap / 0.6)
        d.ellipse((cx + w * .3 - r, cy - r, cx + w * .3 + r, cy + r), outline=WHITE + (int(200 * A * (1 - tap / 0.6)),), width=max(2, round(u(0.008))))
    bob = u(0.02) * math.sin(t * 2 * math.pi * 1.4)
    ay = cy + h / 2 + u(0.07) + bob; s2 = u(0.06)
    d.line([(cx, ay - s2), (cx, ay + s2 * .6)], fill=WHITE + (int(255 * A),), width=max(3, round(u(0.014))))
    d.line([(cx - s2 * .6, ay), (cx, ay + s2 * .7), (cx + s2 * .6, ay)], fill=WHITE + (int(255 * A),), width=max(3, round(u(0.014))), joint="curve")
    d.line([(cx, ay - s2), (cx, ay + s2 * .6)], fill=NAVY + (int(255 * A),), width=max(2, round(u(0.007))))

GF = {"label": g_label, "status": g_status, "manual": g_manual, "attend": g_attend, "docs": g_docs,
      "logo": g_logo, "comment": g_comment, "cta": g_cta}

# ---------- thumbnail & end card ----------
def make_thumb():
    r = Reader(["-ss", str(P["thumb_src"]), "-i", RAW, "-frames:v", "1", "-vf", f"{GRADE},scale={W}:{H}:flags=lanczos"])
    im = zoom_img(r.read(), 1.06, 0.5, 0.22).convert("RGBA"); r.close()
    g = Image.new("L", (1, 256))
    for y in range(256): g.putpixel((0, y), int(225 * max(0, (y / 255 - 0.42) / 0.58) ** 1.3))
    grad = Image.new("RGBA", (W, H), (12, 18, 55, 255)); grad.putalpha(g.resize((W, H)))
    im.alpha_composite(grad)
    d = ImageDraw.Draw(im)
    lines = [("ANDA PERLUKAN", 0.088, None), ("SISTEM", 0.165, None), ("MACAM MANA?", 0.108, ACC)]
    x = u(0.07); y = H * 0.505; maxw = W * 0.76
    for s, sz, box in lines:
        f = font("Black", u(sz))
        if text_w(f, s) > maxw - (u(0.06) if box else 0): f = font("Black", u(sz) * (maxw - (u(0.06) if box else 0)) / text_w(f, s))
        asc, desc = f.getmetrics(); hh = asc * 0.78
        if box:
            tw = text_w(f, s)
            rr(d, (x, y, x + tw + u(0.06), y + hh + u(0.06)), u(0.025), fill=box + (255,))
            d.text((x + u(0.03), y + u(0.03) + hh), s, font=f, fill=WHITE, anchor="ls")
            y += hh + u(0.06) + u(0.02)
        else:
            d.text((x, y + hh), s, font=f, fill=WHITE, anchor="ls", stroke_width=max(1, round(u(0.004))), stroke_fill=(12, 18, 55))
            y += hh + u(0.03)
    assert y < H * 0.80, y
    return im.convert("RGB")

def make_end():
    im = Image.new("RGBA", (W, H), NAVY + (255,)); d = ImageDraw.Draw(im)
    # hiasan lembut: bulatan biru aksen
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.ellipse((W * 0.55, -W * 0.25, W * 1.35, W * 0.55), fill=ACC + (40,))
    dl.ellipse((-W * 0.4, H * 0.72, W * 0.35, H * 0.72 + W * 0.75), fill=ACC + (28,))
    im.alpha_composite(lay)
    paste_logo(im, W / 2, H * 0.36, u(0.52), 1.0)
    f = font("ExtraBold", u(0.062))
    parts = [("Cara ", WHITE), ("MUDAH", ACC), (" Urus Yuran", WHITE)]
    tw = sum(text_w(f, s) for s, _ in parts); x = W / 2 - tw / 2
    for s, c in parts: d.text((x, H * 0.49), s, font=f, fill=c, anchor="lm"); x += text_w(f, s)
    f2 = font("SemiBold", u(0.042)); s = "Follow untuk tips urus yuran sekolah"
    tw = text_w(f2, s)
    rr(d, (W / 2 - tw / 2 - u(0.05), H * 0.565, W / 2 + tw / 2 + u(0.05), H * 0.565 + u(0.1)), u(0.05), outline=WHITE, width=max(2, round(u(0.005))))
    d.text((W / 2, H * 0.565 + u(0.05)), s, font=f2, fill=WHITE, anchor="mm")
    d.text((W / 2, H * 0.66), "hello@yuran.my", font=font("Medium", u(0.042)), fill=(210, 220, 245), anchor="mm")
    return im.convert("RGB")

# ---------- render ----------
def main():
    thumb = make_thumb(); end = make_end()
    thumb.save(OUT.replace(".mp4", "_THUMB.png"))
    tmpv = OUT + ".v.mp4"
    crf = "19" if FINAL else "22"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", crf, "-pix_fmt", "yuv420p", "-r", str(FPS), tmpv], stdin=subprocess.PIPE)
    N = round(DUR * FPS); nb = round(BODY * FPS)
    act = {}; bi = 0; prev_end = None
    for i in range(N):
        t = i / FPS
        if t < TH: fr = thumb
        elif bi < nb:
            bf = body.read(); bi += 1
            fr = zoom_img(bf, zoom_at(t))
            for b in P["br"]:
                if b["s"] <= t < b["e"]:
                    if b["id"] not in act: act[b["id"]] = Broll(b)
                    bimg = act[b["id"]].frame(t)
                    a = min(1, (t - b["s"]) / 0.12, (b["e"] - t) / 0.12)
                    fr = Image.blend(fr, bimg, max(0, a)) if a < 1 else bimg
                elif b["id"] in act and t >= b["e"]:
                    act.pop(b["id"]).r.close()
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for g in P["g"]:
                if g["s"] <= t < g["e"]: GF[g["k"]](d, lay, g, t)
            draw_caption(lay, t)
            fr = fr.convert("RGBA"); fr.alpha_composite(lay); fr = fr.convert("RGB")
        else:
            lt = t - (TH + BODY)
            fr = Image.blend(prev_end, end, ease(lt / 0.25)) if lt < 0.25 and prev_end else end
        if bi < nb or t < TH: prev_end = fr
        enc.stdin.write(fr.tobytes())
        if i % 150 == 0: print(f"{t:5.1f}/{DUR}", flush=True)
    enc.stdin.close(); enc.wait(); body.close()
    audio(OUT + ".a.m4a")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", OUT + ".a.m4a", "-c", "copy", "-movflags", "+faststart", "-shortest", OUT], check=True)
    os.remove(tmpv)

def audio(path):
    ins = ["-i", RAW]; fc = [f"[0:a]aselect='not(between(t,{C0},{C1}))',asetpts=N/SR/TB,aresample=48000,highpass=f=70,afftdn=nr=8:nf=-42,"
                             f"acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150:makeup=2,adelay={int(TH*1000)}|{int(TH*1000)},apad=whole_dur={DUR}[v]"]
    mix = ["[v]"]
    for j, (t, n, db) in enumerate(P["sfx"]):
        ins += ["-i", os.path.join(SFXDIR, n + ".wav")]
        fc.append(f"[{j+1}:a]aresample=48000,volume={db}dB,adelay={int(t*1000)}|{int(t*1000)}[s{j}]"); mix.append(f"[s{j}]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{DUR}[m]")
    pre = path + ".pre.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", "[m]", "-ac", "2", pre], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
          f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", ln + ",aresample=48000", "-c:a", "aac", "-b:a", "192k" if FINAL else "128k", path], check=True)
    os.remove(pre)

if __name__ == "__main__":
    main()
