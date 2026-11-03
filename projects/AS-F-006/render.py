#!/usr/bin/env python3
"""AS-F-006_TeknikDarab Part 2 (Aster, TOFU+BOFU, gaya HYBRID hitam + kuning) — render preview/final.

usage: render.py <workdir> <scale> <out.mp4>
  workdir: has raw.mp4, logo.png, music.mp3, fonts/, raw_tr.json
  scale:   0.5 = preview 540x960, 1.0 = final 1080x1920
Design coordinates are 1080x1920; everything is multiplied by SC.
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD, SC, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SFXD = os.path.join(REPO, "edit", "sfx")
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")))
FPS = 30
W, H = int(1080 * SC), int(1920 * SC)
def s(v): return int(round(v * SC))

BLK = (14, 14, 16); BLK2 = (28, 28, 30); YEL = (255, 200, 61); WHITE = (255, 255, 255); INK = (10, 10, 12); RED = (232, 64, 56)
NAVY = INK; NAVY_D = BLK   # HYBRID: dark tone is black

# ---------------- timeline ----------------
KEEP = P["keep"]              # source segments kept
LEAD = P["thumb_dur"]         # 1 s static thumbnail
END = P["endcard_dur"]
def src2out(t):
    acc = 0.0
    for a, b in KEEP:
        if t < a: return LEAD + acc
        if t <= b: return LEAD + acc + (t - a)
        acc += b - a
    return LEAD + acc
BODY = sum(b - a for a, b in KEEP)
T_VOICE_END = LEAD + BODY
TOTAL = T_VOICE_END + END
NF = int(round(TOTAL * FPS))

# ---------------- fonts / text ----------------
FD = os.path.join(WD, "fonts")
_fc = {}
def F(name, size):
    k = (name, s(size))
    if k not in _fc: _fc[k] = ImageFont.truetype(os.path.join(FD, name), max(1, s(size)))
    return _fc[k]
_tc = {}
def text_img(txt, font, size, fill=WHITE, stroke=0, sfill=INK, shadow=0, salpha=150):
    k = (txt, font, size, fill, stroke, sfill, shadow, salpha)
    if k in _tc: return _tc[k]
    f = F(font, size); st = s(stroke); sh = s(shadow)
    l, t, r, b = f.getbbox(txt, stroke_width=st)
    pad = st + sh * 3 + 4
    im = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    if sh:
        sd = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sd).text((pad - l + sh, pad - t + sh), txt, font=f, fill=(0, 0, 0, salpha), stroke_width=st, stroke_fill=(0, 0, 0, salpha))
        im = Image.alpha_composite(im, sd.filter(ImageFilter.GaussianBlur(max(1, sh))))
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=f, fill=fill, stroke_width=st, stroke_fill=sfill)
    _tc[k] = im
    return im

def hstack(imgs, gap):
    w = sum(i.width for i in imgs) + gap * (len(imgs) - 1); h = max(i.height for i in imgs)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); x = 0
    for i in imgs: out.alpha_composite(i, (x, (h - i.height) // 2)); x += i.width + gap
    return out

def rrect(w, h, r, fill, outline=None, ow=0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=ow)
    return im

def shadowed(im, blur=10, off=6, alpha=110):
    b, o = s(blur), s(off)
    out = Image.new("RGBA", (im.width + 4 * b + o, im.height + 4 * b + o), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(a)
    out.alpha_composite(sh, (2 * b + o, 2 * b + o)); out = out.filter(ImageFilter.GaussianBlur(b))
    out.alpha_composite(im, (2 * b, 2 * b))
    return out

# ---------------- animation helpers ----------------
def ease_out_back(p):
    c1 = 1.70158; c3 = c1 + 1; p = min(max(p, 0), 1)
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2
def ease_out(p): p = min(max(p, 0), 1); return 1 - (1 - p) ** 3
def env(t, t0, t1, fin=0.18, fout=0.15):
    """(scale, alpha) for a pop-in / fade-out element"""
    if t < t0 or t > t1: return None
    sc = 0.6 + 0.4 * ease_out_back((t - t0) / fin)
    al = min(1, (t - t0) / (fin * 0.6)) * min(1, (t1 - t) / fout)
    return sc, max(0, al)

def place(canvas, im, cx, cy, scale=1.0, alpha=1.0, anchor="c", rot=0):
    if im is None or alpha <= 0: return
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    x = s(cx) - (im.width // 2 if anchor[0] in "c" else 0 if anchor[0] == "l" else im.width)
    y = s(cy) - im.height // 2
    canvas.alpha_composite(im, (x, y))

# ---------------- static assets ----------------
logo = Image.open(os.path.join(WD, "logo.png")).convert("RGBA")
def face_circle(d, ring=8):
    D, R = s(d), s(ring)
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((0, 0, D - 1, D - 1), fill=(201, 160, 52))                       # gold ring
    dr.ellipse((R // 3, R // 3, D - 1 - R // 3, D - 1 - R // 3), fill=(255, 214, 102))
    inner = D - 2 * R
    lg = logo.resize((int(inner * 1.13), int(inner * 1.13)), Image.LANCZOS)  # logo has transparent margin
    off = (lg.width - inner) // 2
    lg = lg.crop((off, off, off + inner, off + inner))
    m = Image.new("L", (inner, inner), 0); ImageDraw.Draw(m).ellipse((0, 0, inner - 1, inner - 1), fill=255)
    disc = Image.new("RGBA", (inner, inner), (30, 40, 40, 255)); disc.alpha_composite(lg)
    im.paste(disc, (R, R), m)
    return im

WATERMARK = text_img("asteredu11.com.my", "P600.ttf", 34, fill=(255, 255, 255, 180), shadow=2, salpha=235)

def caption_img(words):
    parts = []
    for w in words:
        parts.append(text_img(w["w"].upper(), "P800.ttf", 66, fill=YEL if w.get("hot") else WHITE, stroke=9, sfill=INK, shadow=3))
    pad = s(9) + s(3) * 3 + 4
    im = hstack(parts, s(20) - 2 * pad)
    maxw = s(860)
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.BICUBIC)
    return im

def pill_label(txt, size=40, fg=NAVY, bg=YEL, padx=26, pady=12):
    t = text_img(txt, "P800.ttf", size, fill=fg)
    im = rrect(t.width + s(2 * padx), t.height + s(2 * pady), s(999), bg)
    im.alpha_composite(t, (s(padx), s(pady))); return shadowed(im, 8, 4, 90)


# ================= Part 2 specific graphics =================
def chalk(txt, size, fill=WHITE, font="Caveat.ttf"):
    """chalk-style text: handwriting font, faint dusty halo"""
    k = ("chalk", txt, size, fill, font)
    if k in _tc: return _tc[k]
    t = text_img(txt, font, size, fill=fill)
    halo = t.filter(ImageFilter.GaussianBlur(max(1, s(3))))
    halo.putalpha(halo.split()[3].point(lambda v: v * 70 // 255))
    out = Image.new("RGBA", t.size, (0, 0, 0, 0)); out.alpha_composite(halo); out.alpha_composite(t)
    _tc[k] = out
    return out

def chalk_line(parts, size):
    """[('text', colour), ...] side by side"""
    return hstack([chalk(p, size, c) for p, c in parts], s(2))

def wipe(im, u):
    """reveal left→right like writing"""
    u = min(max(u, 0), 1)
    if u >= 1: return im
    w = max(1, int(im.width * u))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.paste(im.crop((0, 0, w, im.height)), (0, 0))
    return out

def write_at(canvas, im, cx, cy, t0, st, dur=0.35, alpha=1.0, anchor="c"):
    if st < t0: return
    place(canvas, wipe(im, (st - t0) / dur), cx, cy, 1.0, alpha, anchor=anchor)

def ring(canvas, cx, cy, rx, ry, t0, st, col=YEL, width=6, dur=0.3, alpha=1.0):
    if st < t0: return
    u = ease_out((st - t0) / dur)
    lay = Image.new("RGBA", (s(2 * rx + 20), s(2 * ry + 20)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).arc((s(10), s(10), s(10 + 2 * rx), s(10 + 2 * ry)), -100, -100 + 360 * u, fill=col + (int(255 * alpha),), width=max(2, s(width)))
    canvas.alpha_composite(lay, (s(cx - rx - 10), s(cy - ry - 10)))

def cross(canvas, cx, cy, r, t0, st, alpha=1.0):
    if st < t0: return
    u = ease_out((st - t0) / 0.25)
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    col = RED + (int(255 * alpha),)
    a = min(1, u * 2); b = max(0, u * 2 - 1)
    d.line((s(cx - r), s(cy - r), s(cx - r + 2 * r * a), s(cy - r + 2 * r * a)), fill=col, width=max(2, s(9)))
    if b > 0: d.line((s(cx + r), s(cy - r), s(cx + r - 2 * r * b), s(cy - r + 2 * r * b)), fill=col, width=max(2, s(9)))
    canvas.alpha_composite(lay)

def tick_icon(size, col):
    D = s(size); im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    ImageDraw.Draw(im).line([(D * .12, D * .55), (D * .40, D * .82), (D * .90, D * .18)], fill=col, width=max(2, int(D * .17)), joint="curve")
    return im
def x_icon(size, col):
    D = s(size); im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(2, int(D * .16))
    d.line([(D * .15, D * .15), (D * .85, D * .85)], fill=col, width=w); d.line([(D * .85, D * .15), (D * .15, D * .85)], fill=col, width=w)
    return im
def stamp(txt, fg=INK, bg=YEL):
    t = hstack([text_img(txt, "P900.ttf", 54, fill=fg), tick_icon(48, fg)], s(12))
    im = rrect(t.width + s(56), t.height + s(22), s(14), bg + (255,))
    im.alpha_composite(t, (s(28), s(11)))
    return im

def chalkboard():
    rng = np.random.default_rng(7)
    h = s(P["split_y"])
    base = np.zeros((h, W, 3), np.float32) + np.array(BLK, np.float32)
    dust = rng.normal(0, 1, (max(1, h // 8), max(1, W // 8))).astype(np.float32)
    dust = np.asarray(Image.fromarray(((dust - dust.min()) / (np.ptp(dust) + 1e-6) * 255).astype(np.uint8)).resize((W, h), Image.BICUBIC), np.float32) / 255
    base += (dust[..., None] - 0.5) * 10
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return im
BOARD = None

def episod_lepas():
    a = text_img("EPISOD LEPAS", "P800.ttf", 26, fill=(120, 120, 120))
    b = hstack([text_img("Teknik darab ", "P800.ttf", 40, fill=INK), pill_label("PANTAS", 30, fg=INK, padx=12, pady=4)], s(4))
    c = hstack([chalk("88 × 4 = ", 84, (40, 40, 40)), chalk("352", 84, RED)], s(4))
    w = max(a.width, b.width, c.width) + s(60); h = a.height + b.height + c.height + s(50)
    im = rrect(w, h, s(26), (255, 255, 255, 250))
    y = s(18)
    for t in (a, b): im.alpha_composite(t, (s(30), y)); y += t.height + s(4)
    im.alpha_composite(c, ((w - c.width) // 2, y))
    return shadowed(im)

def hari_ni():
    a = text_img("HARI NI", "P800.ttf", 26, fill=(120, 120, 120))
    b = hstack([text_img("Syarat-", "P800.ttf", 50, fill=INK), pill_label("syaratnya", 40, fg=INK, padx=14, pady=4)], s(2))
    w = max(a.width, b.width) + s(60); h = a.height + b.height + s(46)
    im = rrect(w, h, s(26), (255, 255, 255, 250))
    im.alpha_composite(a, (s(30), s(18))); im.alpha_composite(b, (s(30), s(22) + a.height))
    return shadowed(im)

def follow_cta():
    fc = face_circle(104, 7)
    a = text_img("Follow saya", "P800.ttf", 40, fill=INK)
    b = text_img("@aster.edu_tpg", "P600.ttf", 30, fill=(80, 80, 86))
    tw = max(a.width, b.width)
    im = rrect(fc.width + tw + s(70), fc.height + s(24), s(999), (255, 255, 255, 245), outline=YEL, ow=s(5))
    im.alpha_composite(fc, (s(12), s(12)))
    im.alpha_composite(a, (fc.width + s(30), s(16))); im.alpha_composite(b, (fc.width + s(32), s(16) + a.height))
    return shadowed(im)

def chip(txt):
    t = chalk(txt, 86, YEL)
    im = rrect(t.width + s(60), t.height + s(16), s(22), BLK + (235,), outline=YEL, ow=s(4))
    im.alpha_composite(t, (s(30), s(8)))
    return shadowed(im)

def masalah_note(lines_on):
    w = s(640)
    head = text_img("Masalah sebenar:", "Caveat.ttf", 66, fill=RED)
    rows = [hstack([x_icon(40, RED), text_img(l, "Caveat.ttf", 64, fill=INK)], s(14)) for l in lines_on]
    h = s(40) + head.height + sum(r.height for r in rows) + s(10) * len(rows) + s(30)
    h = max(h, s(330))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), s(14), fill=(255, 250, 232, 255))
    for y in range(s(96), h, s(62)): d.line((s(20), y, w - s(20), y), fill=(170, 195, 230), width=max(1, s(2)))
    d.line((s(64), 0, s(64), h), fill=(235, 120, 120), width=max(1, s(3)))
    tape = rrect(s(140), s(34), s(4), YEL + (210,)); im.alpha_composite(tape, ((w - tape.width) // 2, 0))
    y = s(30); im.alpha_composite(head, (s(84), y)); y += head.height + s(6)
    for r in rows: im.alpha_composite(r, (s(84), y)); y += r.height + s(10)
    return shadowed(im)

def lower_third():
    a = text_img("MATH TURBO 2027", "P900.ttf", 60, fill=YEL)
    b = text_img("Untuk anak sekolah rendah · Tahun 4, 5 & 6", "P700.ttf", 30, fill=WHITE)
    w = max(a.width, b.width) + s(60); h = a.height + b.height + s(30)
    im = rrect(w, h, s(18), BLK + (235,))
    bar = rrect(s(12), h, s(4), YEL + (255,)); im.alpha_composite(bar, (0, 0))
    im.alpha_composite(a, (s(34), s(10))); im.alpha_composite(b, (s(36), s(12) + a.height))
    return shadowed(im)

def pill_2027():
    t = text_img("Pendaftaran 2027 dibuka", "P800.ttf", 40, fill=WHITE)
    im = rrect(t.width + s(60), t.height + s(24), s(999), (214, 40, 40, 255))
    im.alpha_composite(t, (s(30), s(12)))
    return shadowed(im)

def price_star():
    D = s(400); im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for i in range(32):
        r = (D / 2 - s(6)) if i % 2 == 0 else (D / 2 - s(40))
        a = math.pi * 2 * i / 32 - math.pi / 2
        pts.append((D / 2 + r * math.cos(a), D / 2 + r * math.sin(a)))
    d.polygon(pts, fill=YEL, outline=INK)
    for txt, size, dy in (("Pendaftaran serendah", 30, -88), ("RM20", 130, 2), ("sahaja", 38, 92)):
        t = text_img(txt, "P900.ttf" if txt == "RM20" else "P800.ttf", size, fill=INK)
        im.alpha_composite(t, ((D - t.width) // 2, D // 2 + s(dy) - t.height // 2))
    return shadowed(im)

def dm_pill():
    ic = Image.new("RGBA", (s(70), s(70)), (0, 0, 0, 0)); d = ImageDraw.Draw(ic)
    d.ellipse((0, 0, s(69), s(69)), fill=YEL)
    d.polygon([(s(16), s(36)), (s(54), s(18)), (s(40), s(54)), (s(34), s(40))], fill=INK)  # paper plane
    t = text_img("DM saya", "P800.ttf", 46, fill=INK)
    sub = text_img("untuk keterangan lanjut", "P600.ttf", 28, fill=(70, 70, 76))
    tw = max(t.width, sub.width)
    im = rrect(ic.width + tw + s(70), max(ic.height, t.height + sub.height) + s(24), s(999), (255, 255, 255, 248), outline=YEL, ow=s(5))
    im.alpha_composite(ic, (s(14), (im.height - ic.height) // 2))
    im.alpha_composite(t, (ic.width + s(30), s(12))); im.alpha_composite(sub, (ic.width + s(32), s(12) + t.height))
    return shadowed(im)

def minat_q():
    t = text_img("Macam mana nak MINAT?", "P900.ttf", 56, fill=INK)
    im = rrect(t.width + s(60), t.height + s(26), s(20), YEL + (255,))
    im.alpha_composite(t, (s(30), s(13)))
    return shadowed(im)

def series_label():
    return pill_label("TEKNIK DARAB · CIKGU ALFARHAN", 28, fg=INK, padx=22, pady=8)

def name_label():
    a = text_img("Cikgu AlFarhan", "P800.ttf", 44, fill=INK)
    im = rrect(a.width + s(60), a.height + s(26), s(14), YEL + (255,))
    bar = rrect(s(10), a.height + s(26), s(4), INK + (255,)); im.alpha_composite(bar, (0, 0))
    im.alpha_composite(a, (s(34), s(13)))
    return shadowed(im, 8, 4, 100)

def endcard():
    g = np.linspace(0, 1, H)[:, None]
    top = np.array(BLK2, np.float32); bot = np.array(BLK, np.float32)
    grad = (top[None, :] * (1 - g) + bot[None, :] * g)
    im = Image.fromarray(np.repeat(grad[:, None, :], W, axis=1).astype(np.uint8), "RGB").convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((s(520 - 250), s(450 - 250), s(520 + 250), s(450 + 250)), fill=(255, 200, 61, 70))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s(60))))
    place(im, face_circle(340, 12), 520, 450)
    place(im, text_img("Cikgu AlFarhan", "P800.ttf", 64, fill=WHITE), 520, 685)
    place(im, text_img("@aster.edu_tpg", "P600.ttf", 42, fill=YEL), 520, 758)
    cta1 = text_img("WhatsApp Cikgu AlFarhan", "P800.ttf", 44, fill=INK)
    cta2 = text_img("untuk daftar / cuba kelas", "P800.ttf", 44, fill=INK)
    cw = max(cta1.width, cta2.width) + s(70); ch = cta1.height + cta2.height + s(34)
    box = rrect(cw, ch, s(36), YEL + (255,))
    box.alpha_composite(cta1, ((cw - cta1.width) // 2, s(16))); box.alpha_composite(cta2, ((cw - cta2.width) // 2, s(16) + cta1.height))
    place(im, shadowed(box), 520, 910)
    place(im, text_img("asteredu11.com.my", "P900.ttf", 80, fill=WHITE, shadow=3), 520, 1100)
    place(im, text_img("WhatsApp 011-5596 9070", "P700.ttf", 50, fill=YEL), 520, 1200)
    return im

# ---------------- captions ----------------
def build_captions():
    tr = json.load(open(os.path.join(WD, "raw_tr.json")))
    words = [dict(w=w["w"].strip(), s=w["s"], e=w["e"]) for seg in tr for w in seg["words"]]
    out = []
    for w in words:
        if w["w"].startswith("-") and out: out[-1]["w"] += w["w"]; out[-1]["e"] = w["e"]; continue
        out.append(w)
    for a, b, man in P["caption_override"]:          # number readouts checked against a second transcript
        out = [w for w in out if not (a <= w["s"] < b)] + [dict(w=x[0], s=x[1], e=x[2], solo=1) for x in man]
    out.sort(key=lambda w: w["s"])
    fix = P["caption_fix"]; hot = set(P["caption_hot"])
    for w in out:
        w["w"] = fix.get(w["w"], w["w"])
        bare = re.sub(r"[.,?!]", "", w["w"]).lower()
        if bare in hot or re.fullmatch(r"[\d ,]+", bare) or bare.startswith("rm"): w["hot"] = 1
    chunks, cur = [], []
    for i, w in enumerate(out):
        cur.append(w); nxt = out[i + 1] if i + 1 < len(out) else None
        brk = len(cur) >= 3 or re.search(r"[.,?!]$", w["w"]) or not nxt or nxt["s"] - w["e"] > 0.35 or w.get("solo") or (nxt and nxt.get("solo"))
        if not nxt: brk = True
        if brk:
            e = nxt["s"] if nxt and nxt["s"] - w["e"] < 0.6 else w["e"] + 0.15
            chunks.append(dict(s=src2out(cur[0]["s"]), e=src2out(min(e, KEEP[-1][1])), words=[dict(x) for x in cur])); cur = []
    merged = []
    for c in chunks:
        if merged:
            p = merged[-1]
            short = len(c["words"]) == 1 or len(p["words"]) == 1
            solo = any(x.get("solo") for x in c["words"] + p["words"])
            if short and not solo and len(p["words"]) + len(c["words"]) <= 4 and c["s"] - p["e"] < 0.3 and not re.search(r"[.?!]$", p["words"][-1]["w"]):
                p["words"] = p["words"] + c["words"]; p["e"] = c["e"]; continue
        merged.append(c)
    for c in merged:
        c["words"] = [dict(x, w=re.sub(r"[.]$", "", x["w"]) if i < len(c["words"]) - 1 else re.sub(r"[.,]$", "", x["w"])) for i, x in enumerate(c["words"])]
    return merged
CAPS = build_captions()

# ---------------- base talking-head video ----------------
def zoom_at(src_t, split):
    key = "zoom_split" if split else "zoom_full"
    z = P[key][0][1]
    for t0, zz in P[key]:
        if src_t >= t0: z = zz
    return z
def frame_full(img, z):
    zz, y0 = P["zoom_states"][str(z)]
    cw, ch = 1080 / zz, 1920 / zz; x0 = (1080 - cw) / 2
    box = tuple(int(round(v * SC)) for v in (x0, y0, x0 + cw, y0 + ch))
    return img.crop(box).resize((W, H), Image.BICUBIC)
SPLIT_Y = P["split_y"]
def frame_half(img, z):
    ph = 1920 - SPLIT_Y
    cw, ch = 1080 / z, ph / z; x0 = (1080 - cw) / 2
    y0 = P["face_y"] - P["split_face_at"] / z
    box = tuple(int(round(v * SC)) for v in (x0, y0, x0 + cw, y0 + ch))
    return img.crop(box).resize((W, s(ph)), Image.BICUBIC)

# warm indoor light: pull a little orange out, lift shadows, keep skin natural
GRADE = ("colorbalance=rs=-0.03:bs=0.02:rm=-0.02:bm=0.01:rh=-0.01,"
         "curves=all='0/0.03 0.2/0.19 0.5/0.53 0.8/0.84 1/0.98',eq=brightness=0.03:contrast=1.05:saturation=1.04:gamma=1.06")
def base_reader():
    sel = "+".join(f"between(t,{a:.3f},{b - 0.0001:.3f})" for a, b in KEEP)
    cmd = ["ffmpeg", "-v", "error", "-i", os.path.join(WD, "raw.mp4"), "-vf",
           f"select='{sel}',setpts=N/{FPS}/TB,{GRADE},scale={W}:{H}:flags=lanczos", "-r", str(FPS),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3; last = None
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        last = Image.frombuffer("RGB", (W, H), b, "raw", "RGB", 0, 1); yield last
    while True: yield last
def grab_still(t):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", os.path.join(WD, "raw.mp4"), "-frames:v", "1",
           "-vf", f"{GRADE},scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return Image.frombuffer("RGB", (W, H), subprocess.run(cmd, capture_output=True, check=True).stdout, "raw", "RGB", 0, 1)

def out2src(t):
    t -= LEAD; acc = 0.0
    for a, b in KEEP:
        if t <= acc + (b - a): return a + (t - acc)
        acc += b - a
    return KEEP[-1][1]

# ---------------- prebuilt overlays ----------------
EP_LEPAS = episod_lepas(); HARI_NI = hari_ni(); FOLLOW = follow_cta(); NAME = name_label(); SERIES = series_label()
LOWER3 = lower_third(); PILL27 = pill_2027(); PRICE = price_star(); DM = dm_pill(); MINAT = minat_q(); ENDC = endcard()
CHIP_K, CHIP_P = chip("KONSEP"), chip("POLA")
NOTES = {}
BTITLE = chalk("Teknik Darab · Part 2", 92, WHITE)
CAP_IMG = {}
def thumbnail():
    im = frame_full(grab_still(P["thumb_src_t"]), "1.0").convert("RGBA")
    l1 = text_img("TEKNIK DARAB PANTAS", "P900.ttf", 64, fill=WHITE, stroke=10, sfill=INK, shadow=5)
    l2 = text_img("ADA SYARAT!", "P900.ttf", 116, fill=YEL, stroke=13, sfill=INK, shadow=7)
    p2 = pill_label("PART 2", 54, fg=YEL, bg=INK + (255,), padx=34, pady=10)
    place(im, l1, 495, 335); place(im, l2, 495, 440, rot=3); place(im, p2, 495, 540)
    place(im, WATERMARK, 64, 250, anchor="l")
    return im
THUMB = thumbnail()
SPLIT_IN, SPLIT_OUT = P["split_src"]

def ov(t, t0, t1, im, cx, cy, **kw):
    e = env(t, t0, t1)
    if e: place(CANVAS, im, cx, cy, e[0], e[1], **kw)

def phase_alpha(ph, st):
    if not (ph["t0"] <= st < ph["t1"]): return 0
    return min(1, (st - ph["t0"]) / 0.25, (ph["t1"] - st) / 0.2)

def draw_board(c, st, yoff):
    B = P["board"]
    for ph in P["phases"]:
        a = phase_alpha(ph, st)
        if a <= 0: continue
        b = B[ph["id"]]
        if ph["id"] == "A" or ph["id"] == "B":
            write_at(c, chalk(b["head"][0], 108, YEL), 540, 330 + yoff, b["head"][1], st, alpha=a)
            write_at(c, chalk_line([(b["sub"][0][0], WHITE), (b["sub"][0][1], YEL)], 68), 540, 440 + yoff, b["sub"][1], st, 0.6, alpha=a)
        if ph["id"] == "A":
            for txt, x, t0, t1 in b["nums"]:
                write_at(c, chalk(txt, 140, WHITE), x, b["nums_y"] + yoff, t0, st, alpha=a)
                ring(c, x, b["nums_y"] + 8 + yoff, 82, 68, t1, st, alpha=a)
        if ph["id"] == "B":
            x = 360
            for txt, t0 in b["eq"]:
                im = chalk(txt, 190, YEL if txt == "4" else WHITE)
                write_at(c, im, x, b["eq_y"] + yoff, t0, st, alpha=a, anchor="l"); x += im.width / SC + 18
            if st >= b["same"]:   # circle each 8: digits are the same
                ring(c, 412, b["eq_y"] + 10 + yoff, 46, 76, b["same"], st, alpha=a)
                ring(c, 490, b["eq_y"] + 10 + yoff, 46, 76, b["same"] + 0.15, st, alpha=a)
        if ph["id"] == "C":
            write_at(c, chalk(b["head"][0], 96, RED), 540, 340 + yoff, b["head"][1], st, 0.5, alpha=a)
            for txt, x, t0, tx in b["bad"]:
                write_at(c, chalk(txt, 120, WHITE), x, b["bad_y"] + yoff, t0, st, alpha=a)
                cross(c, x, b["bad_y"] + 10 + yoff, 58, tx, st, alpha=a)
            write_at(c, chalk(b["bad_label"][0], 60, RED), 470, b["bad_y"] + 95 + yoff, b["bad_label"][1], st, alpha=a)
            for txt, x, t0 in b["good"]:
                write_at(c, chalk(txt, 120, YEL), x, b["good_y"] + yoff, t0, st, alpha=a)
                ring(c, x, b["good_y"] + 8 + yoff, 74, 60, t0 + 0.25, st, alpha=a)
        if "stamp" in b:
            txt, t0, y = b["stamp"]
            if st >= t0:
                k = ("stamp", txt)
                if k not in CAP_IMG: CAP_IMG[k] = shadowed(stamp(txt), 8, 4, 120)
                e = ease_out_back((st - t0) / 0.25)
                place(c, CAP_IMG[k], 540, y + yoff, 0.6 + 0.4 * e, a, rot=-4)

def draw_frame(t, base):
    global CANVAS, BOARD
    if t < LEAD:
        return THUMB
    if t >= T_VOICE_END:
        p = ease_out((t - T_VOICE_END) / 0.25)
        if p >= 1: return ENDC
        im = frame_full(base, "1.1").convert("RGBA")
        e = ENDC.copy(); e.putalpha(e.split()[3].point(lambda v: int(v * p)))
        im.alpha_composite(e); return im
    st = out2src(t)
    split = SPLIT_IN <= st < SPLIT_OUT
    if split:
        if BOARD is None: BOARD = chalkboard()
        CANVAS = Image.new("RGBA", (W, H), BLK + (255,))
        CANVAS.paste(frame_half(base, zoom_at(st, True)), (0, s(SPLIT_Y)))
        p = ease_out((st - SPLIT_IN) / 0.35)
        yoff = -(1 - p) * 300
        bd = BOARD.copy()
        if p < 1: bd.putalpha(int(255 * p))
        CANVAS.alpha_composite(bd, (0, s(yoff)))
        place(CANVAS, BTITLE, 540, 120 + yoff, alpha=p)
        draw_board(CANVAS, st, yoff)
        CANVAS.paste(Image.new("RGBA", (W, s(10)), YEL + (255,)), (0, s(SPLIT_Y - 5)))
        place(CANVAS, SERIES, 470, SPLIT_Y)
        ov(st, *P["follow_cta"], FOLLOW, 40, SPLIT_Y + 110, anchor="l")
        cap_y = P["cap_y_split"]
    else:
        CANVAS = frame_full(base, zoom_at(st, False)).convert("RGBA")
        cap_y = P["cap_y_full"]
        ov(st, *P["episod"]["lepas"], EP_LEPAS, 520, 400)
        ov(st, *P["episod"]["hari"], HARI_NI, 520, 400)
        ov(st, *P["name_label"], NAME, 60, 1130, anchor="l")
        c0, c1, c2, c3 = P["chips"][0]
        for a0, a1 in ((c0, c1), (c2, c3)):
            ov(st, a0, a1, CHIP_K, 330, 1150, rot=-3)
            ov(st, a0 + 0.46, a1, CHIP_P, 720, 1150, rot=3)
        n = P["note"]
        e = env(st, n["t0"], n["t1"])
        if e:
            on = tuple(l for l, t0 in n["lines"] if st >= t0)
            if on not in NOTES: NOTES[on] = masalah_note(on)
            place(CANVAS, NOTES[on], 520, 1190, e[0], e[1], rot=-2)
        ov(st, *P["minat"], MINAT, 520, 1150)
        ov(st, *P["lower_third"], LOWER3, 40, 1150, anchor="l")
        ov(st, *P["pill_2027"], PILL27, 520, 360)
        ov(st, *P["price"], PRICE, 520, 400, rot=-6)
        ov(st, *P["dm"], DM, 520, 1170)
    for c in CAPS:
        if c["s"] <= t < c["e"]:
            k = id(c)
            if k not in CAP_IMG: CAP_IMG[k] = caption_img(c["words"])
            p = min(1, (t - c["s"]) / 0.08)
            place(CANVAS, CAP_IMG[k], 500, cap_y, 0.92 + 0.08 * p, 1)
            break
    place(CANVAS, WATERMARK, 64, 250, anchor="l")
    return CANVAS

# ---------------- audio ----------------
def lufs(path):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); tp = float(re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", r)[-1])
    return I, tp

def build_audio(path):
    tmpd = path + "_stems"; os.makedirs(tmpd, exist_ok=True)
    vpath, mpath, pre = (os.path.join(tmpd, n) for n in ("voice.wav", "music.wav", "pre.wav"))
    keep = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[k{i}];" for i, (a, b) in enumerate(KEEP))
    cat = "".join(f"[k{i}]" for i in range(len(KEEP))) + f"concat=n={len(KEEP)}:v=0:a=1,"
    voice = "highpass=f=80,afftdn=nr=10:nf=-42,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(WD, "raw.mp4"), "-filter_complex", keep + cat + voice,
                    "-map", "[o]", "-ar", "48000", "-ac", "2", vpath], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(WD, "music.mp3"), "-t", f"{TOTAL + 0.5}",
                    "-ar", "48000", "-ac", "2", mpath], check=True)
    gv = -16 - lufs(vpath)[0]; gm = -16 - lufs(mpath)[0]
    a_up, a_dn = -12.0, -23.0   # music vs voice level (dB): open (thumbnail/end card) / under speech
    vol = (f"volume='pow(10,(if(lt(t,{LEAD}),{a_up},if(lt(t,{LEAD+0.4}),{a_up}+({a_dn}-({a_up}))*(t-{LEAD})/0.4,"
           f"if(lt(t,{T_VOICE_END}),{a_dn},{a_dn}+({a_up}-({a_dn}))*min(1,(t-{T_VOICE_END})/0.4)))))/20)':eval=frame")
    fc = (f"[0:a]volume={gv:.2f}dB,adelay={int(LEAD*1000)}:all=1,apad=whole_dur={TOTAL}[vo];"
          f"[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume={gm:.2f}dB,{vol},afade=t=in:d=0.3,afade=t=out:st={TOTAL-0.8}:d=0.8[mu];")
    inputs = ["-i", vpath, "-i", mpath]; labels = []
    for i, (t, name, g, base) in enumerate(P["sfx"]):
        if base == "s": t = src2out(t)
        inputs += ["-i", os.path.join(SFXD, name + ".wav")]
        fc += f"[{i+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={int(t*1000)}:all=1[s{i}];"
        labels.append(f"[s{i}]")
    fc += f"[vo][mu]{''.join(labels)}amix=inputs={2+len(labels)}:normalize=0:duration=first[mx]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[mx]", "-t", f"{TOTAL}", pre], check=True)
    # final: gain to -14 LUFS, brick-wall limiter keeps true peak <= -1 dBTP
    I, _ = lufs(pre)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af",
                    f"volume={-14 - I:.2f}dB,aresample=192000,alimiter=limit=0.85:attack=2:release=60:level=false,aresample=48000",
                    "-t", f"{TOTAL}", path], check=True)
    I2, tp2 = lufs(path)
    if abs(I2 + 14) > 0.3:   # limiter shaved loudness: nudge once more
        os.replace(path, pre)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af",
                        f"volume={-14 - I2:.2f}dB,aresample=192000,alimiter=limit=0.85:attack=2:release=60:level=false,aresample=48000",
                        "-t", f"{TOTAL}", path], check=True)
    print("audio", lufs(path), flush=True)
    for f in (vpath, mpath, pre):
        if os.path.exists(f): os.remove(f)
    os.rmdir(tmpd)

def stills(times):
    for t in times:
        base = None
        if LEAD <= t < TOTAL:
            st = out2src(min(t, T_VOICE_END - 0.01))
            base = grab_still(min(st, KEEP[-1][1] - 0.2))
        draw_frame(t, base).convert("RGB").save(f"{OUT}_{t:05.2f}.png")

def main():
    if os.environ.get("STILLS"):
        return stills([float(x) for x in os.environ["STILLS"].split(",")])
    apath = OUT + ".audio.wav"
    build_audio(apath)
    crf = "28" if SC < 1 else "18"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", apath, "-c:v", "libx264", "-preset", "medium", "-crf", crf, "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    base = base_reader(); cur = next(base); bi = 0
    for f in range(NF):
        t = f / FPS
        if LEAD <= t < T_VOICE_END:
            want = int(round((t - LEAD) * FPS))
            while bi < want: cur = next(base); bi += 1
        im = draw_frame(t, cur)
        enc.stdin.write(im.convert("RGB").tobytes())
        if f % 150 == 0: print(f"frame {f}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); os.remove(apath)
    THUMB.convert("RGB").resize((1080, 1920), Image.LANCZOS).save(OUT.replace(".mp4", "_THUMB.png"))
    json.dump(dict(total=TOTAL, voice_end=T_VOICE_END, captions=[dict(s=round(c["s"], 2), e=round(c["e"], 2), text=" ".join(w["w"] for w in c["words"])) for c in CAPS]),
              open(OUT.replace(".mp4", "_timeline.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
