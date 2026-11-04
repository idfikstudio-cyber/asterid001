# Compositor: python3 render.py <scale 0.5|1.0> <out_video_noaudio.mp4> [thumb.png]
import sys, os, subprocess, math, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan as P

SC = float(sys.argv[1]); OUT = sys.argv[2]; THUMB_OUT = sys.argv[3] if len(sys.argv) > 3 else None
ROOT = P.S; WK = P.W; FD = os.path.join(ROOT, "fonts"); DL = os.path.join(ROOT, "dl")
FW, FH = 1080, 1920
W, H = int(FW * SC), int(FH * SC)
FPS = 30
NAVY = (18, 32, 74); NAVY2 = (10, 20, 52); YEL = (255, 200, 61); WHITE = (255, 255, 255); INK = (22, 28, 48); RED = (214, 48, 49)
GRADE = "colorbalance=rs=-0.02:bs=0.03:rm=-0.01:bm=0.005:rh=0.01:bh=-0.01,curves=all='0/0.035 0.18/0.16 0.5/0.54 0.82/0.87 1/0.985',eq=brightness=0.025:contrast=1.05:saturation=1.08:gamma=1.04"

def s(v): return int(round(v * SC))
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        path = os.path.join(FD, name + ".ttf")
        f = ImageFont.truetype(path, max(8, s(size)))
        if name == "Caveat":
            try: f.set_variation_by_name("Bold")
            except Exception: pass
        _fc[k] = f
    return _fc[k]

# ---------- face asset
face_src = Image.open(os.path.join(DL, "face.png")).convert("RGBA").crop((337, 337, 3038, 3038))
def face_circle(d, ring=10):
    d = s(d); r = max(2, s(ring))
    im = face_src.resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new("RGBA", (d + 2 * r, d + 2 * r), (0, 0, 0, 0))
    dr = ImageDraw.Draw(out); dr.ellipse((0, 0, d + 2 * r - 1, d + 2 * r - 1), fill=(232, 178, 40, 255))
    dr.ellipse((r // 3, r // 3, d + 2 * r - 1 - r // 3, d + 2 * r - 1 - r // 3), fill=(255, 214, 90, 255))
    out.paste(im, (r, r), Image.composite(im, Image.new("RGBA", (d, d), (0, 0, 0, 0)), m).split()[3])
    return out

# ---------- drawing helpers (return RGBA images)
def shadowed(img, blur=8, off=(0, 4), alpha=150):
    pad = s(blur * 3) + 4
    base = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((0, 0, 0, 255), (pad + s(off[0]), pad + s(off[1])), a)
    sh = sh.filter(ImageFilter.GaussianBlur(max(1, s(blur))))
    base.alpha_composite(sh); base.alpha_composite(img, (pad, pad))
    return base

def text_img(text, font, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0)):
    f = font; bb = f.getbbox(text, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-bb[0] + 2, -bb[1] + 2), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def rich_line(toks, hls, size, gap=16):
    f = F("Poppins-ExtraBold", size); st = max(2, s(7))
    parts = [text_img(t, f, YEL if h else WHITE, st, (8, 10, 20)) for t, h in zip(toks, hls)]
    asc = f.getbbox("ÀgHy", stroke_width=st)
    hgt = asc[3] - asc[1] + 4
    wid = sum(p.width for p in parts) + s(gap) * (len(parts) - 1)
    im = Image.new("RGBA", (wid, hgt), (0, 0, 0, 0)); x = 0
    for t, p in zip(toks, parts):
        bb = f.getbbox(t, stroke_width=st)
        im.alpha_composite(p, (x, max(0, bb[1] - asc[1])))
        x += p.width + s(gap)
    return im

def rbox(size, radius, fill, outline=None, width=0):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), s(radius), fill=fill, outline=outline, width=width)
    return im

def pill(text, size, bg, fg, padx=28, pady=14, font="Poppins-Bold", radius=40):
    t = text_img(text, F(font, size), fg)
    b = rbox((t.width + s(2 * padx), t.height + s(2 * pady)), radius, bg)
    b.alpha_composite(t, (s(padx), s(pady))); return b

def paper(w, h):
    im = rbox((s(w), s(h)), 22, (252, 249, 238, 255))
    d = ImageDraw.Draw(im)
    for y in range(s(70), s(h), s(46)): d.line((s(18), y, s(w) - s(18), y), fill=(205, 220, 240), width=max(1, s(2)))
    d.line((s(56), 0, s(56), s(h)), fill=(240, 140, 140), width=max(1, s(3)))
    return im

# ---------- element renderers: (img, (x, y) top-left in 1080 coords, anchor) given local time lt
cache = {}
def C(key, fn):
    if key not in cache: cache[key] = fn()
    return cache[key]

def render_el(e, st):
    k = e["kind"]; lt = st - e["s"]
    if k == "namepill":
        def mk():
            dot = Image.new("RGBA", (s(22), s(22)), (0, 0, 0, 0)); ImageDraw.Draw(dot).ellipse((0, 0, s(21), s(21)), fill=NAVY)
            p = pill(e["text"], 40, YEL + (255,), NAVY, padx=30, pady=12)
            return shadowed(p, 10, (0, 4), 120)
        return C(id(e), mk), (60, 1110), "tl"
    if k == "bignum":
        return C(id(e), lambda: shadowed(text_img(e["text"], F("Poppins-Black", 150), YEL, s(12), NAVY2), 14, (0, 8), 170)), (470, e["y"]), "c"
    if k == "bignum_panel":
        def mk():
            t = text_img(e["text"], F("Poppins-Black", 120), YEL, s(10), NAVY2)
            return shadowed(t, 12, (0, 6), 170)
        return C(id(e), mk), (480, 470), "c"
    if k == "note":
        shown = [txt for (t0, txt) in e["lines"] if st >= t0 - 0.02]
        key = (id(e), len(shown))
        def mk():
            w, h = 780, 110 + 66 * len(e["lines"])
            im = paper(w, h); d = ImageDraw.Draw(im)
            d.text((s(80), s(22)), e["head"], font=F("Poppins-Bold", 26), fill=RED)
            d.text((s(w - 80), s(14)), "✎", font=F("Poppins-Bold", 34), fill=(230, 150, 40)) if False else None
            for i, txt in enumerate(shown):
                hl = ("25" in txt) or ("sifir" in txt)
                d.text((s(80), s(62 + 66 * i)), txt, font=F("Caveat", 58), fill=(28, 52, 140))
            return shadowed(im, 14, (0, 6), 110)
        return C(key, mk), (60, 270), "tl"
    if k == "step":
        def mk():
            tag = pill(f"LANGKAH {e['n']}", 26, YEL + (255,), NAVY, padx=16, pady=8, radius=12)
            t = text_img(e["text"], F("Poppins-Bold", 32), WHITE)
            b = rbox((tag.width + t.width + s(60), max(tag.height, t.height) + s(24)), 18, NAVY + (235,))
            b.alpha_composite(tag, (s(12), (b.height - tag.height) // 2))
            b.alpha_composite(t, (tag.width + s(32), (b.height - t.height) // 2))
            return shadowed(b, 8, (0, 3), 120)
        return C(id(e), mk), (50, 790), "tl"
    if k == "counter":
        def mk():
            d = 150; im = Image.new("RGBA", (s(d), s(d)), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse((0, 0, s(d) - 1, s(d) - 1), fill=YEL + (255,), outline=WHITE, width=max(1, s(6)))
            t = text_img(e["text"], F("Poppins-Black", 76 if len(e["text"]) < 2 else 64), NAVY)
            im.alpha_composite(t, ((im.width - t.width) // 2, (im.height - t.height) // 2 - s(4)))
            return shadowed(im, 10, (0, 5), 140)
        return C(id(e), mk), (850, 150), "c"
    if k == "answer":
        def mk():
            t = text_img(e["text"], F("Poppins-Black", 88), NAVY)
            b = rbox((t.width + s(70), t.height + s(46)), 26, YEL + (255,), outline=WHITE, width=max(1, s(6)))
            b.alpha_composite(t, (s(35), s(20)))
            return shadowed(b, 14, (0, 8), 160)
        return C(id(e), mk), (480, 800), "c"
    if k == "follow":
        def mk():
            fc = face_circle(190, 9)
            t1 = text_img("Follow saya", F("Poppins-ExtraBold", 52), WHITE, s(6), NAVY2)
            t2 = pill("@aster.edu_tpg", 34, YEL + (255,), NAVY, padx=22, pady=8)
            w = fc.width + s(24) + max(t1.width, t2.width); h = max(fc.height, t1.height + t2.height + s(14))
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); im.alpha_composite(fc, (0, (h - fc.height) // 2))
            x = fc.width + s(24); y0 = (h - t1.height - t2.height - s(14)) // 2
            im.alpha_composite(t1, (x, y0)); im.alpha_composite(t2, (x, y0 + t1.height + s(14)))
            return shadowed(im, 12, (0, 5), 130)
        return C(id(e), mk), (60, 300), "tl"
    if k == "price":
        def mk():
            d = 380; im = Image.new("RGBA", (s(d), s(d)), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
            cx = cy = s(d) / 2; pts = []
            for i in range(32):
                r = s(d) / 2 - 1 if i % 2 == 0 else s(d) / 2 * 0.84
                a = math.pi * 2 * i / 32; pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            dr.polygon(pts, fill=YEL + (255,))
            dr.ellipse((s(26), s(26), s(d) - s(26), s(d) - s(26)), outline=NAVY, width=max(1, s(4)))
            t1 = text_img(e["sub"], F("Poppins-Bold", 24), NAVY)
            t2 = text_img(e["text"], F("Poppins-Black", 104), NAVY)
            im.alpha_composite(t1, ((im.width - t1.width) // 2, s(112)))
            im.alpha_composite(t2, ((im.width - t2.width) // 2, s(146)))
            return shadowed(im.rotate(-8, resample=Image.BICUBIC, expand=True), 14, (0, 8), 150)
        return C(id(e), mk), (680, 430), "c"
    if k == "subjects":
        shown = [txt for (t0, txt) in e["items"] if st >= t0 - 0.02]
        def mk():
            head = pill(e["head"], 54, YEL + (255,), NAVY, font="Poppins-Black", padx=30, pady=10, radius=20)
            chips = [pill(x, 36, NAVY + (240,), WHITE, padx=22, pady=10, radius=30) for x in shown]
            rows, row, rw = [], [], 0
            for c in chips:
                if row and rw + c.width > s(800): rows.append(row); row, rw = [], 0
                row.append(c); rw += c.width + s(12)
            if row: rows.append(row)
            hh = head.height + s(18) + sum(max(c.height for c in r) + s(12) for r in rows)
            ww = max([head.width] + [sum(c.width + s(12) for c in r) for r in rows])
            im = Image.new("RGBA", (ww + 4, hh + 4), (0, 0, 0, 0)); im.alpha_composite(head, (0, 0)); y = head.height + s(18)
            for r in rows:
                x = 0
                for c in r: im.alpha_composite(c, (x, y)); x += c.width + s(12)
                y += max(c.height for c in r) + s(12)
            return shadowed(im, 10, (0, 5), 130)
        return C((id(e), len(shown)), mk), (60, 290), "tl"
    if k == "dmpill":
        return C(id(e), lambda: shadowed(pill("💬 " if False else e["text"], 40, YEL + (255,), NAVY, padx=30, pady=14, font="Poppins-ExtraBold"), 10, (0, 5), 140)), (60, 300), "tl"
    return None

def anim(lt, dur):
    """returns (scale, alpha) for pop-in / fade-out"""
    if lt < 0.10: sc = 0.7 + 3.6 * lt
    elif lt < 0.20: sc = 1.06 - 0.6 * (lt - 0.10)
    else: sc = 1.0
    a = min(1.0, lt / 0.08)
    rem = dur - lt
    if rem < 0.15: a = min(a, max(0.0, rem / 0.15))
    return sc, a

def paste(frame, img, pos, anchor, sc=1.0, a=1.0):
    if a <= 0: return
    if abs(sc - 1) > 0.01:
        img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
    if a < 0.999:
        img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * a)))
    x, y = s(pos[0]), s(pos[1])
    if anchor == "c": x -= img.width // 2; y -= img.height // 2
    elif anchor == "tl" and abs(sc - 1) > 0.01:
        pass
    if x >= 0 and y >= 0: frame.alpha_composite(img, (x, y))
    else: frame.paste(img, (x, y), img)

# ---------- watermark
WM = shadowed(text_img("asteredu11.com.my", F("Poppins-SemiBold", 30), (255, 255, 255, 172)), 4, (0, 2), 140)

# ---------- caption images
def cap_img(c):
    def mk():
        one = rich_line(c["toks"], c["hl"], 64)
        if one.width <= s(860) or len(c["toks"]) < 2:
            return shadowed(one, 8, (0, 4), 150)
        best = None
        for k in range(1, len(c["toks"])):
            a = rich_line(c["toks"][:k], c["hl"][:k], 64); b = rich_line(c["toks"][k:], c["hl"][k:], 64)
            m = max(a.width, b.width)
            if best is None or m < best[0]: best = (m, a, b)
        _, a, b = best
        im = Image.new("RGBA", (max(a.width, b.width), a.height + b.height - s(6)), (0, 0, 0, 0))
        im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height - s(6)))
        return shadowed(im, 8, (0, 4), 150)
    return C(("cap", id(c)), mk)

# ---------- source frames
FACE = (500, 930)   # face centre in source frame (1080 coords)
SHIFT = 280         # lift full-frame shot so eyes sit in upper third

def src_reader():
    filt = []
    for i, (a, b) in enumerate(P.KEEP):
        filt.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
    filt.append("".join(f"[v{i}]" for i in range(len(P.KEEP))) + f"concat=n={len(P.KEEP)}:v=1:a=0,fps={FPS},{GRADE},scale={W}:{H}:flags=lanczos,format=rgb24[o]")
    cmd = ["ffmpeg", "-v", "error", "-i", os.path.join(DL, "main.mp4"), "-filter_complex", ";".join(filt), "-map", "[o]", "-f", "rawvideo", "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 4)

def grab_still(t):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", os.path.join(DL, "main.mp4"), "-frames:v", "1", "-vf", f"{GRADE},scale={W}:{H}:flags=lanczos,format=rgb24", "-f", "rawvideo", "-"]
    return Image.frombytes("RGB", (W, H), subprocess.run(cmd, capture_output=True).stdout)

def full_frame(src, z):
    # lift + desk extension
    top = src.crop((0, s(SHIFT), W, H))
    desk = src.crop((0, H - s(160), W, H)).resize((W, s(SHIFT)), Image.BILINEAR)
    fr = Image.new("RGB", (W, H)); fr.paste(top, (0, 0)); fr.paste(desk, (0, H - s(SHIFT)))
    if z > 1.001:
        fx, fy = s(FACE[0]), s(FACE[1] - SHIFT)
        x0 = fx - fx / z; y0 = fy - fy / z
        fr = fr.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + W / z, y0 + H / z))
    return fr

PANEL_H = 900; DIV_H = 60
def bottom_panel(src, z):
    top = FACE[1] - 320
    bh = FH - PANEL_H - DIV_H
    x0, y0, w, h = 0, top, FW, bh
    if z > 1.001:
        cx, cy = FACE[0], FACE[1]
        w, h = FW / z, bh / z; x0 = cx - (cx - 0) / z; y0 = cy - (cy - top) / z
    return src.resize((W, s(bh)), Image.BICUBIC, box=(s(x0), s(y0), s(x0 + w), s(y0 + h)))

# B-roll frames
BR = os.path.join(WK, f"broll_{SC}")
IN_W, IN_H = 1020, 850
def prep_broll():
    if os.path.isdir(BR) and len(glob.glob(BR + "/*.jpg")) > 5000: return
    os.makedirs(BR, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "70", "-to", "247", "-i", os.path.join(DL, "broll.mp4"),
                    "-vf", f"fps=30,crop=1320:1100:0:190,scale={s(IN_W)}:{s(IN_H)}:flags=lanczos", "-q:v", "3",
                    os.path.join(BR, "%05d.jpg")], check=True)
def broll_frame(bt):
    i = int(round((bt - 70.0) * 30)) + 1
    i = max(1, min(i, len(os.listdir(BR))))
    return Image.open(os.path.join(BR, f"{i:05d}.jpg")).convert("RGB")

def panel_bg():
    im = Image.new("RGB", (W, s(PANEL_H)), NAVY)
    g = np.linspace(0, 1, s(PANEL_H))[:, None, None]
    arr = (np.array(NAVY2)[None, None, :] * g + np.array(NAVY)[None, None, :] * (1 - g)).astype(np.uint8)
    arr = np.repeat(arr, W, axis=1); im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s(30) - s(6), s(28) - s(6), s(30 + IN_W) + s(6), s(28 + IN_H) + s(6)), s(26), fill=YEL)
    return im
_mask = None
def inset_mask():
    global _mask
    if _mask is None:
        _mask = Image.new("L", (s(IN_W), s(IN_H)), 0)
        ImageDraw.Draw(_mask).rounded_rectangle((0, 0, s(IN_W) - 1, s(IN_H) - 1), s(22), fill=255)
    return _mask
DIV = None
def divider():
    global DIV
    if DIV is None:
        DIV = Image.new("RGBA", (W, s(DIV_H)), YEL + (255,))
        t = text_img("DARAB GARIS · CIKGU ALFARHAN", F("Poppins-ExtraBold", 30), NAVY)
        DIV.alpha_composite(t, (s(40), (DIV.height - t.height) // 2))
    return DIV

def zoom_at(ts, table):
    for a, b, z in table:
        if a <= ts < b: return z
    return 1.0

# ---------- thumbnail
def fit_text(text, font, size, maxw, **kw):
    while True:
        im = text_img(text, F(font, size), **kw)
        if im.width <= s(maxw) or size < 30: return im
        size -= 4

def make_thumb():
    src = grab_still(P.THUMB_SRC)
    fr = full_frame(src, 1.0).convert("RGBA")
    # darken lower-middle for legibility
    g = Image.new("L", (1, H));
    for y in range(H):
        v = y / H; a = 0 if v < 0.42 else min(170, int((v - 0.42) / 0.2 * 170))
        g.putpixel((0, y), a)
    shade = Image.new("RGBA", (W, H), NAVY2 + (0,)); shade.putalpha(g.resize((W, H)))
    fr.alpha_composite(shade)
    l1 = shadowed(fit_text(P.HOOK[0], "Poppins-Black", 100, 860, fill=WHITE, stroke=s(10), stroke_fill=NAVY2), 14, (0, 8), 170)
    t2 = fit_text(P.HOOK[1], "Poppins-Black", 110, 780, fill=NAVY)
    b2 = rbox((t2.width + s(60), t2.height + s(40)), 24, YEL + (255,)); b2.alpha_composite(t2, (s(30), s(18)))
    b2 = shadowed(b2.rotate(-2, resample=Image.BICUBIC, expand=True), 14, (0, 8), 170)
    pl = shadowed(pill("Darjah 4, 5 & 6", 44, WHITE + (255,), NAVY, padx=30, pady=12, font="Poppins-ExtraBold"), 10, (0, 4), 150)
    cx = 470
    fr.alpha_composite(pl, (s(cx) - pl.width // 2, s(1000)))
    fr.alpha_composite(l1, (s(cx) - l1.width // 2, s(1100)))
    fr.alpha_composite(b2, (s(cx) - b2.width // 2, s(1250)))
    # sticky note sample question
    note = paper(300, 150); d = ImageDraw.Draw(note)
    d.text((s(72), s(30)), "321 × 3 = ?", font=F("Caveat", 60), fill=(28, 52, 140))
    note = shadowed(note.rotate(6, resample=Image.BICUBIC, expand=True), 12, (0, 6), 140)
    fr.alpha_composite(note, (s(590), s(300)))
    fr.alpha_composite(WM, (s(60), s(250)))
    return fr

def make_endcard():
    im = Image.new("RGBA", (W, H), NAVY + (255,))
    arr = np.zeros((H, W, 3), np.uint8); g = np.linspace(0, 1, H)[:, None]
    for c in range(3): arr[:, :, c] = (NAVY[c] * (1 - g) + NAVY2[c] * g).astype(np.uint8)
    im = Image.fromarray(arr).convert("RGBA")
    cx = 470
    fc = shadowed(face_circle(400, 14), 16, (0, 8), 150)
    im.alpha_composite(fc, (s(cx) - fc.width // 2, s(300)))
    def ctr(img, y): im.alpha_composite(img, (s(cx) - img.width // 2, s(y)))
    ctr(text_img("Cikgu AlFarhan", F("Poppins-ExtraBold", 64), WHITE), 800)
    ctr(text_img("@aster.edu_tpg", F("Poppins-Bold", 42), YEL), 890)
    cta1 = text_img("Follow untuk tips belajar", F("Poppins-ExtraBold", 44), NAVY)
    cta2 = text_img("anak seterusnya", F("Poppins-ExtraBold", 44), NAVY)
    b = rbox((max(cta1.width, cta2.width) + s(70), cta1.height + cta2.height + s(56)), 30, YEL + (255,))
    b.alpha_composite(cta1, ((b.width - cta1.width) // 2, s(20))); b.alpha_composite(cta2, ((b.width - cta2.width) // 2, s(30) + cta1.height))
    ctr(b, 1010)
    ctr(text_img("asteredu11.com.my", F("Poppins-Black", 76), WHITE), 1230)
    ctr(text_img("WhatsApp 011-5596 9070", F("Poppins-Bold", 42), (220, 228, 255)), 1345)
    return im

def main():
    prep_broll()
    thumb = make_thumb()
    if THUMB_OUT:
        make_thumb_full = thumb.convert("RGB"); make_thumb_full.save(THUMB_OUT)
    end = make_endcard()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18" if SC == 1 else "20", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    nT = int(round(P.THUMB * FPS)); nE = int(round(P.END * FPS))
    tb = thumb.convert("RGB").tobytes()
    for i in range(nT): enc.stdin.write(tb)
    rd = src_reader(); fsz = W * H * 3
    inv = []  # content time -> source time
    acc = 0
    for a, b in P.KEEP: inv.append((acc, a, b)); acc += b - a
    def c2src(ct):
        for c0, a, b in inv:
            if ct < c0 + (b - a) + 1e-6: return a + (ct - c0)
        return P.KEEP[-1][1]
    bg = panel_bg(); n = 0
    while True:
        buf = rd.stdout.read(fsz)
        if len(buf) < fsz: break
        ct = n / FPS; st = c2src(ct); n += 1
        src = Image.frombytes("RGB", (W, H), buf)
        fr = compose(src, st, bg)
        enc.stdin.write(fr.convert("RGB").tobytes())
        if n % 300 == 0: print("frame", n, flush=True)
    eb = end.convert("RGB").tobytes()
    for i in range(nE): enc.stdin.write(eb)
    enc.stdin.close(); enc.wait()
    print("content frames", n, "expected", int(P.CONTENT * FPS))

def compose(src, st, bg):
        if P.SPLIT[0] <= st < P.SPLIT[1]:
            fr = Image.new("RGB", (W, H)); fr.paste(bg, (0, 0))
            fr.paste(broll_frame(P.broll_t(st)), (s(30), s(28)), inset_mask())
            fr.paste(bottom_panel(src, zoom_at(st, P.SPLITZOOM)), (0, s(PANEL_H + DIV_H)))
            fr = fr.convert("RGBA"); fr.alpha_composite(divider(), (0, s(PANEL_H)))
            capy = 1470
        else:
            fr = full_frame(src, zoom_at(st, P.ZOOM)).convert("RGBA"); capy = 1330
        fr.alpha_composite(WM, (s(60), s(250)))
        for e in P.E:
            if e["s"] <= st < e["e"]:
                r = render_el(e, st)
                if r:
                    img, pos, anc = r; sc, a = anim(st - e["s"], e["e"] - e["s"])
                    if anc == "tl" and sc != 1.0:
                        pos = (pos[0] + (1 - sc) * img.width / SC / 2, pos[1] + (1 - sc) * img.height / SC / 2)
                    paste(fr, img, pos, anc, sc, a)
        for c in P.caps:
            if c["s"] - 0.05 <= st < c["e2"]:
                img = cap_img(c); sc, a = anim(st - c["s"] + 0.05, c["e2"] - c["s"] + 0.05)
                sc = 1 + (sc - 1) * 0.5
                paste(fr, img, (470, capy), "c", sc, 1.0)
                break
        return fr

if __name__ == "__main__":
    main()
