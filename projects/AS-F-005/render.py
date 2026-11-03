#!/usr/bin/env python3
"""AS-F-005_TeknikDarab Part 1 (Aster, TOFU) — render preview/final.

usage: render.py <workdir> <scale> <out.mp4>
  workdir: has raw.mp4, broll.mp4, logo.png, music.mp3, fonts/, raw_tr.json
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

NAVY = (16, 34, 74); NAVY_D = (9, 20, 46); YEL = (255, 200, 61); WHITE = (255, 255, 255); INK = (12, 18, 34)

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

def card_darjah():
    a = text_img("DARJAH", "P800.ttf", 46, fill=WHITE)
    b = text_img("4, 5 & 6", "P900.ttf", 96, fill=YEL)
    w = max(a.width, b.width) + s(80); h = a.height + b.height + s(40)
    im = rrect(w, h, s(34), NAVY + (240,), outline=YEL, ow=s(5))
    im.alpha_composite(a, ((w - a.width) // 2, s(16))); im.alpha_composite(b, ((w - b.width) // 2, s(16) + a.height))
    return shadowed(im)

def langkah_pill(n, eq, res=None):
    tag = pill_label(f"LANGKAH {n}", 24, padx=16, pady=7)
    e = text_img(eq, "P800.ttf", 52, fill=WHITE)
    parts = [tag, e]
    if res is not None:
        parts += [text_img("=", "P800.ttf", 52, fill=WHITE), text_img(res, "P900.ttf", 62, fill=YEL)]
    inner = hstack(parts, s(16))
    im = rrect(inner.width + s(44), inner.height + s(12), s(24), NAVY_D + (235,), outline=YEL, ow=s(4))
    im.alpha_composite(inner, (s(22), s(6)))
    return im

def follow_cta():
    fc = face_circle(104, 7)
    a = text_img("Follow saya", "P800.ttf", 40, fill=NAVY)
    b = text_img("@aster.edu_tpg", "P600.ttf", 30, fill=(70, 80, 100))
    tw = max(a.width, b.width)
    im = rrect(fc.width + tw + s(70), fc.height + s(24), s(999), (255, 255, 255, 245), outline=YEL, ow=s(5))
    im.alpha_composite(fc, (s(12), s(12)))
    im.alpha_composite(a, (fc.width + s(30), s(16))); im.alpha_composite(b, (fc.width + s(32), s(16) + a.height))
    return shadowed(im)

def syarat_note():
    w, h = s(720), s(230)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), s(14), fill=(255, 250, 232, 255))
    for y in range(s(70), h, s(44)): d.line((s(20), y, w - s(20), y), fill=(160, 190, 230), width=max(1, s(2)))
    d.line((s(70), 0, s(70), h), fill=(235, 120, 120), width=max(1, s(3)))
    tape = rrect(s(140), s(36), s(4), (255, 200, 61, 200)); im.alpha_composite(tape, ((w - tape.width) // 2, 0))
    a = text_img("Teknik ni ada", "Caveat.ttf", 64, fill=NAVY)
    b = text_img("SYARAT!", "P900.ttf", 92, fill=(214, 40, 40))
    im.alpha_composite(a, (s(95), s(34))); im.alpha_composite(b, (s(95), s(34) + a.height - s(10)))
    # warning triangle icon
    tri = Image.new("RGBA", (s(110), s(100)), (0, 0, 0, 0)); td = ImageDraw.Draw(tri)
    td.polygon([(s(55), s(4)), (s(106), s(96)), (s(4), s(96))], fill=YEL, outline=NAVY)
    ex = text_img("!", "P900.ttf", 64, fill=NAVY); tri.alpha_composite(ex, ((tri.width - ex.width) // 2, s(24)))
    im.alpha_composite(tri, (w - s(135), s(70)))
    return shadowed(im)

def comment_bubble():
    fc = face_circle(84, 5)
    a = text_img("@aster.edu_tpg", "P600.ttf", 28, fill=(110, 115, 125))
    b = hstack([text_img("Comment", "P800.ttf", 50, fill=INK), text_img("“GOOD”", "P900.ttf", 56, fill=(230, 160, 0))], s(12))
    c = text_img("di ruangan komen", "P600.ttf", 32, fill=(60, 66, 80))
    tw = max(a.width, b.width, c.width)
    w, h = fc.width + tw + s(70), a.height + b.height + c.height + s(36)
    im = rrect(w, h, s(30), (255, 255, 255, 250))
    im.alpha_composite(fc, (s(18), (h - fc.height) // 2))
    x = fc.width + s(40); y = s(14)
    for t in (a, b, c): im.alpha_composite(t, (x, y)); y += t.height
    # tail
    tl = Image.new("RGBA", (s(40), s(30)), (0, 0, 0, 0)); ImageDraw.Draw(tl).polygon([(0, 0), (s(40), 0), (s(8), s(30))], fill=(255, 255, 255, 250))
    out = Image.new("RGBA", (w, h + s(28)), (0, 0, 0, 0)); out.alpha_composite(im); out.alpha_composite(tl, (s(70), h - 1))
    return shadowed(out)

def part2_card():
    a = text_img("NANTI", "P800.ttf", 40, fill=NAVY)
    b = text_img("PART 2", "P900.ttf", 110, fill=NAVY)
    w = max(a.width, b.width) + s(140); h = a.height + b.height + s(36)
    im = rrect(w, h, s(30), YEL + (255,), outline=NAVY, ow=s(6))
    im.alpha_composite(a, ((w - s(100) - a.width) // 2, s(14))); im.alpha_composite(b, ((w - s(100) - b.width) // 2, s(10) + a.height))
    ar = Image.new("RGBA", (s(70), s(80)), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon([(0, s(10)), (s(60), s(40)), (0, s(70))], fill=NAVY)
    im.alpha_composite(ar, (w - s(90), (h - ar.height) // 2))
    return shadowed(im)

def board_title():
    t = text_img("Teknik Darab", "Caveat.ttf", 120, fill=WHITE)
    im = Image.new("RGBA", (t.width + s(20), t.height + s(40)), (0, 0, 0, 0)); im.alpha_composite(t, (s(10), 0))
    d = ImageDraw.Draw(im); y = t.height + s(4)
    pts = [(s(30) + i * s(12), y + int(math.sin(i * 0.9) * s(5))) for i in range((t.width - s(40)) // s(12))]
    d.line(pts, fill=YEL, width=s(7), joint="curve")
    return im

def series_label():
    return pill_label("TEKNIK DARAB · CIKGU ALFARHAN", 28, padx=22, pady=8)

def name_label():
    a = text_img("Cikgu AlFarhan", "P800.ttf", 44, fill=NAVY)
    im = rrect(a.width + s(60), a.height + s(26), s(14), YEL + (255,))
    bar = rrect(s(10), a.height + s(26), s(4), NAVY + (255,)); im.alpha_composite(bar, (0, 0))
    im.alpha_composite(a, (s(34), s(13)))
    return shadowed(im, 8, 4, 100)

def thumb_overlay():
    l1 = text_img("TEKNIK DARAB", "P900.ttf", 100, fill=WHITE, stroke=11, sfill=NAVY, shadow=5)
    l2 = text_img("PANTAS!", "P900.ttf", 176, fill=YEL, stroke=13, sfill=NAVY, shadow=7)
    return l1, l2

def endcard():
    im = Image.new("RGBA", (W, H), NAVY_D + (255,))
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(NAVY_D)[None, None, :] * (1 - g[..., None] * 0) * (1 - 0.0)).astype(np.float32)
    top = np.array(NAVY, np.float32); bot = np.array(NAVY_D, np.float32)
    grad = (top[None, :] * (1 - g) + bot[None, :] * g)
    arr = np.repeat(grad[:, None, :], W, axis=1).astype(np.uint8)
    im = Image.fromarray(arr, "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((s(520 - 250), s(470 - 250), s(520 + 250), s(470 + 250)), fill=(255, 200, 61, 70))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s(60))))
    place(im, face_circle(360, 12), 520, 470)
    place(im, text_img("Cikgu AlFarhan", "P800.ttf", 66, fill=WHITE), 520, 715)
    place(im, text_img("@aster.edu_tpg", "P600.ttf", 42, fill=YEL), 520, 790)
    cta1 = text_img("Follow untuk tips belajar", "P800.ttf", 44, fill=NAVY)
    cta2 = text_img("anak seterusnya", "P800.ttf", 44, fill=NAVY)
    cw = max(cta1.width, cta2.width) + s(70); ch = cta1.height + cta2.height + s(34)
    box = rrect(cw, ch, s(999) if False else s(36), YEL + (255,))
    box.alpha_composite(cta1, ((cw - cta1.width) // 2, s(16))); box.alpha_composite(cta2, ((cw - cta2.width) // 2, s(16) + cta1.height))
    place(im, shadowed(box), 520, 950)
    place(im, text_img("asteredu11.com.my", "P900.ttf", 80, fill=WHITE, shadow=3), 520, 1140)
    place(im, text_img("WhatsApp 011-5596 9070", "P700.ttf", 46, fill=YEL), 520, 1240)
    return im

# ---------------- captions ----------------
def build_captions():
    tr = json.load(open(os.path.join(WD, "raw_tr.json")))
    words = [dict(w=w["w"].strip(), s=w["s"], e=w["e"]) for seg in tr for w in seg["words"]]
    out = []
    for w in words:
        if w["w"].startswith("-") and out: out[-1]["w"] += w["w"]; out[-1]["e"] = w["e"]; continue
        out.append(w)
    fix = P["caption_fix"]; hot = set(P["caption_hot"])
    for w in out:
        w["w"] = fix.get(w["w"], w["w"]).replace(" x ", " × ")
        if w["w"] == "x": w["w"] = "×"
        bare = re.sub(r"[.,?!]", "", w["w"]).lower()
        if bare in hot or re.fullmatch(r"\d+", bare): w["hot"] = 1
    chunks, cur = [], []
    for i, w in enumerate(out):
        cur.append(w); nxt = out[i + 1] if i + 1 < len(out) else None
        brk = len(cur) >= 3 or re.search(r"[.,?!]$", w["w"]) or not nxt or nxt["s"] - w["e"] > 0.35
        if nxt and (nxt["w"] == "×" or w["w"] == "×"): brk = False   # keep "99 × 2" together
        if len(cur) >= 5 or (len(cur) >= 4 and w["w"] != "×" and not (nxt and nxt["w"] == "×")): brk = True
        if not nxt: brk = True
        if brk:
            e = nxt["s"] if nxt and nxt["s"] - w["e"] < 0.6 else w["e"] + 0.15
            chunks.append(dict(s=src2out(cur[0]["s"]), e=src2out(min(e, KEEP[-1][1])),
                               words=[dict(x) for x in cur]))
            cur = []
    # fold 1-word fragments ("lah", "2", "9") into a neighbour so captions follow speech rhythm
    merged = []
    for c in chunks:
        if merged:
            p = merged[-1]
            short = len(c["words"]) == 1 or len(p["words"]) == 1
            if short and len(p["words"]) + len(c["words"]) <= 4 and c["s"] - p["e"] < 0.3 and not re.search(r"[.?!]$", p["words"][-1]["w"]):
                p["words"] = p["words"] + c["words"]; p["e"] = c["e"]; continue
        merged.append(c)
    for c in merged:   # keep inner commas ("dapat 1, 8"), drop trailing . and ,
        c["words"] = [dict(x, w=re.sub(r"[.]$", "", x["w"]) if i < len(c["words"]) - 1 else re.sub(r"[.,]$", "", x["w"])) for i, x in enumerate(c["words"])]
    return merged
CAPS = build_captions()

# ---------------- b-roll board ----------------
BX, BY, BW, BH = P["broll_crop"]           # crop in b-roll source px
BSC = P["broll_scale"]                     # design scale of the crop
BOARD_POS = P["board_pos"]                 # design top-left of crop on canvas
def broll_time(src_t):
    hold = P["broll_map"][0]["b0"]
    for m in P["broll_map"]:
        if src_t < m["s0"]: return hold
        if src_t <= m["s1"]:
            return m["b0"] + (m["b1"] - m["b0"]) * (src_t - m["s0"]) / max(1e-6, m["s1"] - m["s0"])
        hold = m["b1"]
    return hold
BR_T0, BR_T1 = 29.0, 84.0
bw, bh = s(BW * BSC), s(BH * BSC)
def load_broll():
    cmd = ["ffmpeg", "-v", "error", "-ss", str(BR_T0), "-to", str(BR_T1), "-i", os.path.join(WD, "broll.mp4"),
           "-vf", f"fps={FPS},crop={BW}:{BH}:{BX}:{BY},scale={bw}:{bh}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, bh, bw, 3)
    # screen-blend with navy so the iPad's black page becomes the TOFU dark-blue board
    nv = np.array(NAVY, np.float32) / 255
    out = (1 - (1 - fr.astype(np.float32) / 255) * (1 - nv)) * 255
    return out.astype(np.uint8)
BROLL = load_broll()
def broll_frame(src_t):
    i = int(round((broll_time(src_t) - BR_T0) * FPS)); i = min(max(i, 0), len(BROLL) - 1)
    return Image.fromarray(BROLL[i], "RGB")

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

GRADE = ("colorbalance=rs=-0.02:bs=0.03:rm=-0.01:bm=0.005:rh=0.01:bh=-0.01,"
         "curves=all='0/0.035 0.18/0.16 0.5/0.54 0.82/0.87 1/0.985',eq=brightness=0.02:contrast=1.05:saturation=1.10:gamma=1.03")
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
L1, L2 = thumb_overlay()
DARJAH = card_darjah(); FOLLOW = follow_cta(); SYARAT = syarat_note(); BUBBLE = comment_bubble(); PART2 = part2_card()
TITLE = board_title(); SERIES = series_label(); NAME = name_label(); ENDC = endcard()
THUMB_CHIP = pill_label("DARJAH 4, 5 & 6", 54, fg=YEL, bg=NAVY + (255,), padx=34, pady=14)
CAP_IMG = {}
def thumbnail():
    im = frame_full(grab_still(P["thumb_src_t"]), "1.0").convert("RGBA")
    place(im, L1, 490, 370); place(im, L2, 490, 520, rot=4)
    place(im, THUMB_CHIP, 520, 1250)
    place(im, WATERMARK, 64, 250, anchor="l")
    return im
THUMB = thumbnail()

SPLIT_IN, SPLIT_OUT = P["split_src"]
def ov(t, t0, t1, im, cx, cy, **kw):
    e = env(t, t0, t1)
    if e: place(CANVAS, im, cx, cy, e[0], e[1], **kw)

def draw_frame(t, base):
    global CANVAS
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
        CANVAS = Image.new("RGBA", (W, H), NAVY + (255,))
        CANVAS.paste(frame_half(base, zoom_at(st, True)), (0, s(SPLIT_Y)))
        p = ease_out((st - SPLIT_IN) / 0.35)
        yoff = -(1 - p) * 300
        bd = broll_frame(st).convert("RGBA")
        if p < 1: bd.putalpha(int(255 * p))
        CANVAS.alpha_composite(bd, (s(BOARD_POS[0]), s(BOARD_POS[1] + yoff)))
        place(CANVAS, TITLE, 540, 135 + yoff, alpha=p)
        # row highlight while reading the three questions
        for r in P["row_flash"]:
            if r["t0"] <= st <= r["t1"]:
                y0, y1 = P["rows"][r["row"]]
                q = ease_out((st - r["t0"]) / 0.15)
                box = Image.new("RGBA", (s(640), s(y1 - y0 + 30)), (0, 0, 0, 0))
                ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), s(20), outline=YEL + (int(255 * q),), width=s(6))
                CANVAS.alpha_composite(box, (s(190), s(y0 - 15)))
        # active-row marker
        for r in P["active_row"]:
            if r["t0"] <= st < r["t1"]:
                y0, y1 = P["rows"][r["row"]]; cy = (y0 + y1) / 2
                bob = math.sin(st * 8) * 6
                tri = Image.new("RGBA", (s(46), s(52)), (0, 0, 0, 0))
                ImageDraw.Draw(tri).polygon([(0, 0), (s(46), s(26)), (0, s(52))], fill=YEL)
                place(CANVAS, tri, 150 + bob, cy)
        for L in P["langkah"]:
            e = env(st, L["t0"], L["t1"])
            if e:
                res = L["res"] if st >= L["tres"] else None
                k = (L["n"], L["eq"], res)
                if k not in CAP_IMG: CAP_IMG[k] = langkah_pill(L["n"], L["eq"], res)
                pop = 1.0
                if res is not None: pop = 1 + 0.12 * max(0, 1 - (st - L["tres"]) / 0.2)
                place(CANVAS, CAP_IMG[k], 530, L["y"], e[0] * pop, e[1])
        # divider + series label
        CANVAS.paste(Image.new("RGBA", (W, s(10)), YEL + (255,)), (0, s(SPLIT_Y - 5)))
        place(CANVAS, SERIES, 470, SPLIT_Y)
        cap_y = P["cap_y_split"]
    else:
        CANVAS = frame_full(base, zoom_at(st, False)).convert("RGBA")
        cap_y = P["cap_y_full"]
    # full-frame / global overlays (source time)
    ov(st, *P["name_label"], NAME, 60, 1130, anchor="l")
    ov(st, *P["darjah_card"], DARJAH, 520, 400)
    ov(st, *P["follow_cta"], FOLLOW, 40, 1150, anchor="l")
    ov(st, *P["syarat_note"], SYARAT, 520, 410, rot=-3)
    ov(st, *P["comment_bubble"], BUBBLE, 500, 400)
    ov(st, *P["part2_card"], PART2, 520, 400)
    # captions
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
            base = grab_still(st)
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
