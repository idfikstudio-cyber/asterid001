# Render Yuran.my YM-F-006 (BOFU "JAIS mintak report KAFA").
# usage: python3 ym_f006_render.py <src.mp4> <brolldir: sistem.mp4 pantau.mp4 jais.png> <logo_white.png> <sfxdir> <outdir> <W> [crf]
# Avatar TikTok: env YM_TIKTOK atau <dir logo>/tiktok.jpg; muzik: env YM_MUSIC (281.mp3, 32.mp3)
# W=540 -> preview 540x960, W=1080 -> final 1080x1920.
import json, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, BROLL, LOGO, SFX, OUT = sys.argv[1:6]
W = int(sys.argv[6]); H = W * 16 // 9; CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
S = W / 1080  # skala reka bentuk (semua ukuran ditulis untuk 1080)
FPS = 30
ID = "YM-F-006_JAIS_Mintak_Report_KAFA"
TAG = "PREVIEW" if W < 1080 else "FINAL"
os.makedirs(OUT, exist_ok=True)

BLUE, ACC, BLACK, GREY, WHITE = "#2A3B8F", "#29ABE2", "#231F20", "#E7E8E9", "#FFFFFF"
FD = "/usr/share/fonts/opentype/inter/"
def F(w, px): return ImageFont.truetype(FD + {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], max(8, int(px * S)))

SRC_DUR = 41.21
THUMB = 1.0            # thumbnail statik
OFF = THUMB            # masa video asal + OFF = masa timeline
END = 1.5              # end card
BODY_END = OFF + SRC_DUR
TOTAL = BODY_END + END
NF = int(round(TOTAL * FPS))

# ---------- caption (masa video asal, ikut percakapan; ejaan istilah ikut DNA) ----------
CAP = [
 (0.00, 0.62, "Ini yang biasa"), (0.64, 1.28, "saya terima."), (1.30, 2.32, "Asyik bila nak hantar"), (2.34, 3.34, "*laporan* kat *JAIS* je,"),
 (3.36, 4.36, "banyak lah kena"), (4.38, 5.04, "bawa *report.*"),
 (5.06, 5.70, "*Hujung bulan,*"), (5.72, 6.48, "*laporan* nak kena"), (6.50, 7.30, "hantar kat *JAIS.*"),
 (7.32, 8.54, "Kumpullah semua *resit.*"), (8.56, 9.50, "Kalau *resit* tak buat,"), (9.52, 10.26, "buatlah *resit*"), (10.28, 11.14, "kejap-kejap tu."),
 (11.16, 12.06, "Besok nak hantar"), (12.08, 12.82, "kat *JAIS* ni."),
 (12.84, 13.66, "Type satu-satu"), (13.68, 14.88, "dalam *Excel.*"), (14.90, 15.70, "Semak semula,"), (15.72, 16.76, "*salah* lagi."),
 (16.78, 18.12, "*Berjam-jam hilang,*"), (18.14, 18.64, "betul tak?"),
 (18.66, 19.86, "Inilah keistimewaan"), (19.88, 20.66, "*Yuran.my.*"),
 (20.68, 21.66, "Kita dah siapkan"), (21.68, 22.80, "*template* yang khas"), (22.82, 23.46, "untuk hantar"), (23.48, 24.32, "kat *JAIS* dah."),
 (24.34, 25.30, "Data *kutipan*"), (25.32, 26.82, "tersusun *rapi.*"), (26.84, 27.84, "Tak perlu type semula."),
 (27.86, 29.26, "Masa yang kita luangkan"), (29.28, 30.40, "untuk buat *rekod* tu,"), (30.42, 31.50, "kita luangkan masa"), (31.52, 32.46, "dengan *pelajar.*"),
 (32.48, 33.32, "Habis cerita."),
 (33.34, 34.52, "Package kami, *Pro+,*"), (34.54, 35.32, "sesuai dengan"), (35.34, 36.28, "sekolah-sekolah *KAFA.*"), (36.30, 37.06, "Tak ada *kontrak.*"),
 (37.08, 37.62, "Cuba klik"), (37.64, 38.20, "*link in bio.*"), (38.22, 39.12, "Kita *demo* dulu."),
 (39.14, 39.78, "Kalau sesuai,"), (39.80, 40.46, "cikgu setuju."), (40.48, 41.21, "Let's go."),
]
ZOOM = [(0.00, 1.00), (5.04, 1.12), (7.30, 1.00), (11.14, 1.12), (12.82, 1.00), (18.64, 1.12), (20.66, 1.00),
        (27.84, 1.12), (32.46, 1.00), (33.32, 1.12), (37.06, 1.00)]
JAIS_IN, JAIS_OUT = 2.70, 4.95          # "laporan kat JAIS"
CAL = (5.04, 7.25)                      # "Hujung bulan, laporan nak kena hantar kat JAIS"
RCP = (7.30, 11.10)                     # "Kumpullah semua resit..."
SHEET = (12.82, 18.62)                  # Excel -> salah -> berjam-jam
SH_ERR, SH_CLOCK = 15.72, 16.78
LOGO_IN, LOGO_OUT = 19.80, 20.66        # "Yuran.my"
BA = (20.90, 23.90)                     # template laporan: B-Roll_SistemYuran.my.mp4 @1:56.6 (Invoice List Report -> Collection Report)
BB = (24.30, 27.30)                     # data kutipan: B-Roll Pantau Yuran.mp4 @1:41 (angka diblur)
MASA = (27.84, 32.46); MASA_R2 = 30.42
PKG = (33.30, 37.04); PKG_C1, PKG_C2 = 34.54, 36.30
CTA = (37.06, 41.21); CTA_TAP = 37.70
LABEL_IN, LABEL_OUT = 0.25, 2.60
THUMB_SRC_T = 11.5
LOW_WINS = [(JAIS_IN - 0.3, JAIS_OUT), CAL, RCP, SHEET, (LOGO_IN, LOGO_OUT), BA, BB, MASA, PKG, CTA]
def inwin(t, w): return w[0] <= t < w[1]

def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = min(1, max(0, x)); c = 1.6
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- frames sumber (grade ringan, kekal warna kulit) ----------
GRADE = "eq=contrast=1.04:brightness=0.012:saturation=1.05,unsharp=5:5:0.25"
def reader(t0=0):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", SRC, "-vf", GRADE + ",fps=30",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
SW, SH = 1080, 1920
CLOSE = []
CLOSE_Z = 1.65
def zoom_at(t):
    z = 1.0
    for a, v in ZOOM:
        if t >= a: z = v
    for a, b in CLOSE:
        if a <= t < b: z = z + (CLOSE_Z - z) * ease((t - a) / 0.22)
    return z
def place(fr, z):
    im = Image.fromarray(fr)
    if z != 1.0:
        cw, ch = SW / z, SH / z
        cx, cy = SW / 2, SH * (0.30 + 0.035 * min(1, max(0, z - 1.15) / 0.23))   # muka kekal di sepertiga atas; close-up ditarik ke muka
        x0 = cx - cw / 2; y0 = cy - ch * 0.30
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    return im.resize((W, H), Image.LANCZOS)

# ---------- teks ----------
def text_parts(s):
    out = []; hl = False
    for i, p in enumerate(s.split("*")):
        if p: out.append((p, i % 2 == 1))
    return out
def draw_rich(base, cx, cy, s, font, sc=1.0, stroke=None, colors=(WHITE, ACC), alpha=1.0, shadow=True):
    parts = text_parts(s)
    stroke = int((stroke if stroke is not None else 7) * S)
    tmp = ImageDraw.Draw(base)
    widths = [tmp.textlength(p, font=font) for p, _ in parts]
    tw = sum(widths); asc, desc = font.getmetrics()
    pad = stroke + int(30 * S)
    layer = Image.new("RGBA", (int(tw) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = pad
    for (p, h), w in zip(parts, widths):
        d.text((x, pad), p, font=font, fill=colors[1] if h else colors[0], stroke_width=stroke, stroke_fill=BLACK)
        x += w
    if shadow:
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        sh.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(10 * S)).point(lambda v: int(v * 0.55)))
        layer = Image.alpha_composite(sh, layer)
    if sc != 1.0:
        layer = layer.resize((max(1, int(layer.width * sc)), max(1, int(layer.height * sc))), Image.LANCZOS)
    if alpha < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))

CAP_FONT = F("xb", 78)
CX = W * 0.46          # elak jalur kanan 15%
def caption(base, t):
    cur = None
    for i, (a, b, s) in enumerate(CAP):
        nxt = CAP[i + 1][0] if i + 1 < len(CAP) else SRC_DUR
        if a - 0.02 <= t < min(nxt, b + 0.45) or (a <= t and i + 1 == len(CAP)): cur = (a, s)
    if not cur: return
    a, s = cur; k = ease((t - a) / 0.12)
    y = H * (0.755 if any(inwin(t, w) for w in LOW_WINS) else 0.64)
    tw = ImageDraw.Draw(base).textlength(s.replace("*", ""), font=CAP_FONT) + 30 * S
    fit = min(1.0, W * 0.80 / tw)          # caption panjang dikecilkan supaya kekal dalam safe zone
    draw_rich(base, CX, y + (1 - k) * 18 * S, s, CAP_FONT, sc=(0.9 + 0.1 * k) * fit, alpha=k)

# ---------- label nama ----------
def label(base, t):
    if not (LABEL_IN <= t < LABEL_OUT): return
    k = ease((t - LABEL_IN) / 0.3) * (1 - ease((t - (LABEL_OUT - 0.3)) / 0.3))
    f1, f2 = F("b", 34), F("m", 34)
    d = ImageDraw.Draw(base)
    t1, t2 = "Farhan", "  ·  Yuran.my"
    w = d.textlength(t1, font=f1) + d.textlength(t2, font=f2)
    pw, ph = int(w + 2 * 34 * S + 22 * S), int(66 * S)
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=ph // 2, fill=BLUE)
    ld.ellipse((int(24 * S), ph // 2 - int(8 * S), int(40 * S), ph // 2 + int(8 * S)), fill=ACC)
    x = int(52 * S); y = ph // 2
    ld.text((x, y), t1, font=f1, fill=WHITE, anchor="lm"); x += ld.textlength(t1, font=f1)
    ld.text((x, y), t2, font=f2, fill=GREY, anchor="lm")
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    base.alpha_composite(lay, (int(64 * S - (1 - k) * 40 * S), int(H * 0.135)))

# ---------- kad & B-roll ----------
def card_img(img, w, rad=24):
    h = int(img.height * w / img.width)
    c = img.resize((int(w), h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), radius=int(rad * S), fill=255)
    c.putalpha(m); return c
def shadowed(c, r=18, a=130):
    sh = Image.new("RGBA", (c.width + 100, c.height + 100), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((50, 62, c.width + 50, c.height + 62), radius=int(24 * S), fill=(0, 0, 0, a))
    sh = sh.filter(ImageFilter.GaussianBlur(r * S)); sh.alpha_composite(c, (50, 50)); return sh
def card_base(t, win, h):
    k = back((t - win[0]) / 0.35) if t < win[0] + 0.35 else 1
    ko = 1 - ease((t - (win[1] - 0.25)) / 0.25)
    cw = int(W * 0.74); ch = int(h)
    lay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(30 * S), fill=(255, 255, 255, 246))
    return lay, d, k, ko
def put_card(base, lay, k, ko, cy):
    sh = shadowed(lay, 16, 90)
    sc = max(0.01, 0.9 + 0.1 * min(k, 1.05))
    sh = sh.resize((max(1, int(sh.width * sc)), max(1, int(sh.height * sc))), Image.LANCZOS)
    sh.putalpha(sh.getchannel("A").point(lambda v: int(v * min(1, k) * ko)))
    base.alpha_composite(sh, (int(W * 0.47 - sh.width / 2), int(H * cy - sh.height / 2)))
def mark(d, cx, cy, r, ok):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACC if ok else "#C8435A")
    w = max(2, int(5 * S))
    if ok: d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)], fill=WHITE, width=w, joint="curve")
    else:
        d.line((cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38), fill=WHITE, width=w)
        d.line((cx - r * 0.38, cy + r * 0.38, cx + r * 0.38, cy - r * 0.38), fill=WHITE, width=w)
def fade_layer(lay, k):
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k))); return lay

# logo JAIS (B-ROLL/Logo JAIS.png), sama gaya YM-F-004
_j = Image.open(os.path.join(BROLL, "jais.png")).convert("RGBA")
def jais_card(cw):
    pad = int(16 * S)
    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, cw - 1, cw - 1), radius=int(36 * S), fill=WHITE, outline=ACC, width=max(2, int(6 * S)))
    card.alpha_composite(_j.resize((cw - 2 * pad, cw - 2 * pad), Image.LANCZOS), (pad, pad))
    return shadowed(card, 14, 110)
def jais(base, t):
    if not (JAIS_IN <= t < JAIS_OUT): return
    kin = back((t - JAIS_IN) / 0.32); kout = 1 - ease((t - (JAIS_OUT - 0.22)) / 0.22)
    sh = jais_card(int(300 * S)); sc = max(0.01, kin * (0.85 + 0.15 * kout))
    sh = sh.resize((max(1, int(sh.width * sc)), max(1, int(sh.height * sc))), Image.LANCZOS)
    fade_layer(sh, min(1, (t - JAIS_IN) / 0.12) * kout)
    base.alpha_composite(sh, (int(W * 0.47 - sh.width / 2), int(H * 0.57 - sh.height / 2)))

def calendar(d, x, y, s, top):
    d.rounded_rectangle((x, y, x + s, y + s), radius=int(s * 0.14), fill=WHITE, outline="#CBD0DA", width=max(2, int(3 * S)))
    d.rounded_rectangle((x, y, x + s, y + s * 0.3), radius=int(s * 0.14), fill=top)
    d.rectangle((x, y + s * 0.18, x + s, y + s * 0.3), fill=top)
    for r in range(3):
        for c in range(4):
            cx_ = x + s * (0.17 + c * 0.22); cy_ = y + s * (0.45 + r * 0.17)
            d.rectangle((cx_ - s * 0.05, cy_ - s * 0.04, cx_ + s * 0.05, cy_ + s * 0.04), fill="#C8435A" if (r, c) == (2, 3) else "#D5D9E2")
def docicon(d, x, y, s, col):
    d.rounded_rectangle((x, y, x + s * 0.78, y + s), radius=int(s * 0.08), fill=WHITE, outline=col, width=max(2, int(4 * S)))
    for i in range(4): d.line((x + s * 0.15, y + s * (0.28 + i * 0.17), x + s * 0.63, y + s * (0.28 + i * 0.17)), fill=col, width=max(2, int(4 * S)))
def cal_card(base, t):
    if not inwin(t, CAL): return
    ch = H * 0.15; lay, d, k, ko = card_base(t, CAL, ch); cw = lay.width
    s = int(ch * 0.62); calendar(d, int(36 * S), int((ch - s) / 2), s, "#C8435A")
    fb = F("xb", 50); fm = F("sb", 40)
    d.text((int(36 * S) + s + int(30 * S), ch * 0.34), "Hujung bulan", font=fb, fill=BLACK, anchor="lm")
    if t >= CAL[0] + 0.7:
        k2 = ease((t - CAL[0] - 0.7) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        x0 = int(36 * S) + s + int(30 * S)
        docicon(d2, x0, int(ch * 0.55), int(ch * 0.30), BLUE)
        d2.text((x0 + int(ch * 0.30), ch * 0.70), "Laporan ke JAIS", font=fm, fill=BLUE, anchor="lm")
        lay.alpha_composite(fade_layer(l2, k2))
    put_card(base, lay, k, ko, 0.595)

def receipt(w, h, rnd):
    r = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(r)
    d.rectangle((0, 0, w - 1, h - 1), fill="#FFFDF6", outline="#D8D2C2", width=max(1, int(2 * S)))
    d.text((w / 2, h * 0.16), "RESIT", font=F("b", 22), fill="#8A7F68", anchor="mm")
    for i in range(4):
        L = w * (0.45 + 0.35 * rnd[i]); d.line((w * 0.12, h * (0.36 + i * 0.14), w * 0.12 + L, h * (0.36 + i * 0.14)), fill="#CFC8B6", width=max(2, int(4 * S)))
    return r
_rr = np.random.default_rng(3)
RCP_ITEMS = [(RCP[0] + 0.15 + i * 0.42, _rr.uniform(-1, 1), _rr.uniform(-14, 14), _rr.random(4)) for i in range(8)]
def rcp_card(base, t):
    if not inwin(t, RCP): return
    ch = H * 0.17; lay, d, k, ko = card_base(t, RCP, ch); cw = lay.width
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(30 * S), fill="#EEF1F7")
    for t0, xo, rot, rnd in RCP_ITEMS:
        if t < t0: continue
        p = ease((t - t0) / 0.30)
        rc = receipt(150 * S, 190 * S, rnd).rotate(rot * (1.0 - 0.3 * p), resample=Image.BICUBIC, expand=True)
        x = cw / 2 + xo * cw * 0.30 - rc.width / 2; y = (ch * 0.52 - rc.height / 2) - (1 - p) * ch * 0.7
        lay.alpha_composite(fade_layer(rc, min(1, p * 1.6)), (int(x), int(y)))
    m = Image.new("L", lay.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(30 * S), fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.getchannel("A")), np.array(m))))
    put_card(base, lay, k, ko, 0.595)

def clock(d, cx, cy, r, t):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=BLUE, width=max(3, int(6 * S)))
    for i in range(12):
        a = i * math.pi / 6; d.line((cx + r * 0.8 * math.sin(a), cy - r * 0.8 * math.cos(a), cx + r * 0.9 * math.sin(a), cy - r * 0.9 * math.cos(a)), fill=BLUE, width=max(1, int(3 * S)))
    am = t * 2 * math.pi * 1.6; ah = am / 12
    d.line((cx, cy, cx + r * 0.75 * math.sin(am), cy - r * 0.75 * math.cos(am)), fill=BLACK, width=max(2, int(4 * S)))
    d.line((cx, cy, cx + r * 0.5 * math.sin(ah), cy - r * 0.5 * math.cos(ah)), fill="#C8435A", width=max(3, int(6 * S)))
def sheet_card(base, t):
    if not inwin(t, SHEET): return
    ch = H * 0.19; lay, d, k, ko = card_base(t, SHEET, ch); cw = lay.width
    x0, y0 = int(30 * S), int(30 * S); gw, gh = cw - 2 * x0, ch - 2 * y0
    cols, rows = 4, 5; cwid = [0.12, 0.40, 0.24, 0.24]
    rh = gh / rows
    d.rectangle((x0, y0, x0 + gw, y0 + rh), fill="#1F7A4D")
    hdr = ["No.", "Nama", "Resit", "Jumlah"]
    xs = [x0]
    for c in cwid: xs.append(xs[-1] + gw * c)
    for c in range(cols): d.text(((xs[c] + xs[c + 1]) / 2, y0 + rh / 2), hdr[c], font=F("b", 26), fill=WHITE, anchor="mm")
    for r in range(1, rows + 1):
        d.line((x0, y0 + r * rh, x0 + gw, y0 + r * rh), fill="#D5D9E2", width=1)
    for c in range(cols + 1): d.line((xs[c], y0, xs[c], y0 + gh), fill="#D5D9E2", width=1)
    # taip baris satu-satu
    tt = t - SHEET[0]
    for r in range(1, rows):
        for c in range(cols):
            st = 0.15 + (r - 1) * 0.42 + c * 0.09
            if tt < st: continue
            p = min(1, (tt - st) / 0.12)
            if c == 0: d.text(((xs[0] + xs[1]) / 2, y0 + r * rh + rh / 2), str(r), font=F("m", 26), fill="#6B6E75", anchor="mm")
            else:
                L = (xs[c + 1] - xs[c] - 24 * S) * (0.55 + 0.4 * ((r * 7 + c * 3) % 5) / 5) * p
                d.rounded_rectangle((xs[c] + 12 * S, y0 + r * rh + rh * 0.35, xs[c] + 12 * S + L, y0 + r * rh + rh * 0.65), radius=int(4 * S), fill="#B9BFCC")
    if t >= SH_ERR:   # "salah lagi"
        ke = ease((t - SH_ERR) / 0.2); r = 3; c = 3
        d.rectangle((xs[c] + 2, y0 + r * rh + 2, xs[c + 1] - 2, y0 + (r + 1) * rh - 2), outline="#C8435A", width=max(3, int(5 * S)))
        mark(d, int(xs[c + 1] - 4 * S), int(y0 + r * rh + 4 * S), int(20 * S * ke), False)
    if t >= SH_CLOCK:  # "berjam-jam hilang"
        kc = ease((t - SH_CLOCK) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        d2.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(30 * S), fill=(255, 255, 255, 215))
        clock(d2, int(cw * 0.28), int(ch * 0.5), int(ch * 0.33), t)
        d2.text((cw * 0.50, ch * 0.42), "Berjam-jam", font=F("xb", 54), fill="#C8435A", anchor="lm")
        d2.text((cw * 0.50, ch * 0.66), "hilang", font=F("b", 42), fill=BLACK, anchor="lm")
        lay.alpha_composite(fade_layer(l2, kc))
    put_card(base, lay, k, ko, 0.595)

_l2 = Image.open(LOGO).convert("RGBA")
def logo_pill(base, t):
    if not (LOGO_IN <= t < LOGO_OUT): return
    k = back((t - LOGO_IN) / 0.3); ko = 1 - ease((t - (LOGO_OUT - 0.18)) / 0.18)
    lw = int(330 * S); lh = int(_l2.height * lw / _l2.width)
    pw, ph = lw + int(80 * S), lh + int(40 * S)
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=ph // 2, fill=BLUE)
    lay.alpha_composite(_l2.resize((lw, lh), Image.LANCZOS), (int(40 * S), int(20 * S)))
    sc = max(0.01, 0.85 + 0.15 * min(k, 1.05))
    lay = lay.resize((max(1, int(pw * sc)), max(1, int(ph * sc))), Image.LANCZOS)
    fade_layer(lay, min(1, k) * ko)
    base.alpha_composite(lay, (int(W * 0.47 - lay.width / 2), int(H * 0.58 - lay.height / 2)))

# B-roll video: frame dibaca terus dari klip sumber
def clip_frames(path, t0, dur, crop, blur=()):
    x, y, w, h = crop
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", path, "-t", str(dur), "-vf", f"fps=30,crop={w}:{h}:{x}:{y}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3); out = []
    for i in range(n):
        im = Image.fromarray(np.frombuffer(raw[i * w * h * 3:(i + 1) * w * h * 3], np.uint8).reshape(h, w, 3))
        for bx in blur:
            reg = im.crop(bx).filter(ImageFilter.GaussianBlur(14)); im.paste(reg, bx[:2])
        out.append(im)
    return out
_clips = {}
def clips():
    if not _clips:
        _clips["ba"] = clip_frames(os.path.join(BROLL, "sistem.mp4"), 116.6, BA[1] - BA[0] + 0.1, (270, 100, 920, 420))
        # pantau: blur angka kutipan/peratus/pending (DNA: tiada statistik yang tidak disebut)
        _clips["bb"] = clip_frames(os.path.join(BROLL, "pantau.mp4"), 101.0, BB[1] - BB[0] + 0.1, (0, 0, 1080, 1900),
                                   [(380, 640, 1000, 790), (380, 1000, 1000, 1130), (380, 1340, 1000, 1490), (380, 1700, 1000, 1830)])
    return _clips
_bg = {}
def broll(base, t):
    for key, (a, b), w, cy in (("ba", BA, 0.96, 0.40), ("bb", BB, 0.66, 0.38)):
        if not (a <= t < b): continue
        fr_list = clips()[key]; i = min(len(fr_list) - 1, int((t - a) * 30)); img = fr_list[i]
        k = ease((t - a) / 0.22) * (1 - ease((t - (b - 0.22)) / 0.22)); p = (t - a) / (b - a)
        if key not in _bg:
            bgi = img.resize((W, int(img.height * W / img.width)) if img.width / img.height > W / H else (int(img.width * H / img.height), H), Image.LANCZOS)
            bgi = bgi.crop(((bgi.width - W) // 2, (bgi.height - H) // 2, (bgi.width - W) // 2 + W, (bgi.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(40 * S))
            _bg[key] = Image.blend(bgi.convert("RGBA"), Image.new("RGBA", (W, H), "#0D1122"), 0.62)
        fr = _bg[key].copy()
        c = shadowed(card_img(img, W * w * (1.0 + 0.035 * p)))
        fr.alpha_composite(c, (int(W * 0.50 - c.width / 2), int(H * cy - c.height / 2 + (1 - k) * 40 * S)))
        return Image.blend(base, fr, k)
    return base

def masa_card(base, t):
    if not inwin(t, MASA): return
    ch = H * 0.15; lay, d, k, ko = card_base(t, MASA, ch)
    f = F("b", 44); fb = F("xb", 48); y1, y2 = ch * 0.30, ch * 0.70
    mark(d, int(55 * S), y1, int(26 * S), False)
    d.text((int(100 * S), y1), "Masa untuk buat rekod", font=f, fill="#8D8F93", anchor="lm")
    if t >= MASA_R2:
        tw = d.textlength("Masa untuk buat rekod", font=f)
        d.line((int(100 * S), y1, int(100 * S) + tw * min(1, (t - MASA_R2) / 0.3), y1), fill="#8D8F93", width=max(2, int(4 * S)))
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        mark(d2, int(55 * S), y2, int(26 * S), True)
        d2.text((int(100 * S), y2), "Masa dengan ", font=fb, fill=BLACK, anchor="lm")
        d2.text((int(100 * S) + d2.textlength("Masa dengan ", font=fb), y2), "pelajar", font=fb, fill=ACC, anchor="lm")
        lay.alpha_composite(fade_layer(l2, ease((t - MASA_R2) / 0.25)))
    put_card(base, lay, k, ko, 0.595)

def pkg_card(base, t):
    if not inwin(t, PKG): return
    ch = H * 0.16; lay, d, k, ko = card_base(t, PKG, ch); cw = lay.width
    fb = F("xb", 56)
    d.text((int(40 * S), ch * 0.27), "Pakej ", font=fb, fill=BLACK, anchor="lm")
    x = int(40 * S) + d.textlength("Pakej ", font=fb)
    tw = d.textlength("Pro+", font=fb)
    d.rounded_rectangle((x - 10 * S, ch * 0.27 - 42 * S, x + tw + 14 * S, ch * 0.27 + 42 * S), radius=int(14 * S), fill=ACC)
    d.text((x + 2 * S, ch * 0.27), "Pro+", font=fb, fill=WHITE, anchor="lm")
    for i, (tc, lab) in enumerate(((PKG_C1, "Sesuai untuk KAFA"), (PKG_C2, "Tiada kontrak"))):
        if t < tc: continue
        x0 = int((28 + i * 392) * S); y0 = int(ch * 0.56); pw, ph = int(372 * S), int(ch * 0.32)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        d2.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=ph // 2, fill="#D8F0FB")
        mark(d2, x0 + int(36 * S), y0 + ph // 2, int(20 * S), True)
        d2.text((x0 + int(66 * S), y0 + ph // 2), lab, font=F("b", 30), fill=BLUE, anchor="lm")
        lay.alpha_composite(fade_layer(l2, ease((t - tc) / 0.25)))
    put_card(base, lay, k, ko, 0.595)

TIKTOK = os.environ.get("YM_TIKTOK", os.path.join(os.path.dirname(LOGO), "tiktok.jpg"))
_av = Image.open(TIKTOK).convert("RGBA").crop((37, 22, 202, 187))   # avatar dari BRAND/Yuran Tiktok.jpg
BIO_LINK = "yuran.my/daftar/?tiktok"                                  # dari BRAND/Yuran Tiktok.jpg
def profile_card(cw, ch, t, tap):
    lay = Image.new("RGBA", (int(cw), int(ch)), (0, 0, 0, 0)); od = ImageDraw.Draw(lay)
    od.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(34 * S), fill=WHITE)
    av = int(ch * 0.62); ax = int(30 * S); ay = int((ch - av) / 2)
    m = Image.new("L", (av, av), 0); ImageDraw.Draw(m).ellipse((0, 0, av - 1, av - 1), fill=255)
    a_ = _av.resize((av, av), Image.LANCZOS); a_.putalpha(m); lay.alpha_composite(a_, (ax, ay))
    tx = ax + av + int(26 * S)
    od.text((tx, ch * 0.22), "Yuran.My Street", font=F("b", 40), fill=BLACK, anchor="lm")
    od.text((tx, ch * 0.42), "CARA MUDAH KUTIP YURAN", font=F("m", 26), fill="#6B6E75", anchor="lm")
    fl = F("b", 34); lw_ = od.textlength(BIO_LINK, font=fl); ly = ch * 0.70
    hot = t >= tap
    if hot: od.rounded_rectangle((tx - 10 * S, ly - 30 * S, tx + lw_ + 48 * S, ly + 30 * S), radius=int(12 * S), fill="#FFE3E8")
    od.text((tx + 30 * S, ly), BIO_LINK, font=fl, fill="#E8304F", anchor="lm")
    od.ellipse((tx, ly - 9 * S, tx + 18 * S, ly + 9 * S), outline="#E8304F", width=max(2, int(4 * S)))
    if tap <= t < tap + 0.5:
        r = (t - tap) / 0.5; rr = 26 * S + 70 * S * r; bx = tx + lw_ / 2 + 30 * S
        od.ellipse((bx - rr, ly - rr, bx + rr, ly + rr), outline=(41, 171, 226, int(220 * (1 - r))), width=max(2, int(6 * S)))
    return lay
def cta_card(base, t):
    if not inwin(t, CTA): return
    k = back((t - CTA[0]) / 0.35) if t < CTA[0] + 0.35 else 1
    ko = 1 - ease((t - (CTA[1] - 0.2)) / 0.2)
    lay = shadowed(profile_card(W * 0.78, H * 0.15, t, CTA_TAP), 16, 90)
    sc = max(0.01, 0.9 + 0.1 * min(k, 1.05))
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    fade_layer(lay, min(1, k) * ko)
    base.alpha_composite(lay, (int(W * 0.47 - lay.width / 2), int(H * 0.595 - lay.height / 2)))

# ---------- thumbnail ----------
def thumbnail():
    fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(THUMB_SRC_T), "-i", SRC, "-vf", GRADE, "-frames:v", "1",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = place(np.frombuffer(fr, np.uint8).reshape(SH, SW, 3), 1.08).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(int(H * 0.40), H):
        gd.line((0, y, W, y), fill=(20, 24, 50, int(170 * min(1, (y - H * 0.40) / (H * 0.25)))))
    im.alpha_composite(g)
    f = F("xb", 132)
    draw_rich(im, CX, H * 0.52, "*JAIS*", f, stroke=9)
    draw_rich(im, CX, H * 0.605, "mintak", f, stroke=9)
    d = ImageDraw.Draw(im); fk = F("xb", 132)
    tw = d.textlength("REPORT?", font=fk); bw, bh = int(tw + 70 * S), int(172 * S)
    bx, by = int(CX - bw / 2), int(H * 0.695 - bh / 2)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(26 * S), fill=ACC)
    d.text((CX, H * 0.695), "REPORT?", font=fk, fill=WHITE, anchor="mm")
    sh = jais_card(int(270 * S))
    im.alpha_composite(sh, (int(W * 0.165 - sh.width / 2), int(H * 0.285 - sh.height / 2)))
    return im

# ---------- end card BOFU: link di bio untuk demo (tanpa emel, ikut YM-F-004/005) ----------
_l = Image.open(LOGO).convert("RGBA")
TAP = 0.75
def endcard(t):
    im = Image.new("RGBA", (W, H), BLUE); d = ImageDraw.Draw(im)
    x = W * 0.47; k = ease(t / 0.35)
    lw = int(380 * S); lh = int(_l.height * lw / _l.width)
    im.alpha_composite(_l.resize((lw, lh), Image.LANCZOS), (int(x - lw / 2), int(H * 0.20 - lh / 2 + (1 - k) * 20 * S)))
    f1 = F("xb", 58); y = H * 0.295
    p = [("Cara ", WHITE), ("MUDAH", ACC), (" Urus Yuran", WHITE)]
    tw = sum(d.textlength(s, font=f1) for s, _ in p); xx = x - tw / 2
    for s_, c in p: d.text((xx, y), s_, font=f1, fill=c, anchor="lm"); xx += d.textlength(s_, font=f1)
    k2 = ease((t - 0.15) / 0.35)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    pc = profile_card(W * 0.78, H * 0.15, t, TAP)
    ov.alpha_composite(pc, (int(x - pc.width / 2), int(H * 0.37 + (1 - k2) * 24 * S)))
    od.text((x, H * 0.60), "Klik link di bio", font=F("xb", 56), fill=WHITE, anchor="mm")
    od.text((x, H * 0.645), "untuk demo sistem Yuran.my", font=F("sb", 42), fill=GREY, anchor="mm")
    ov.putalpha(ov.getchannel("A").point(lambda v: int(v * k2)))
    im.alpha_composite(ov)
    return im

# ---------- render video ----------
def render():
    thumb = thumbnail()
    thumb.convert("RGB").save(os.path.join(OUT, f"{ID}_THUMB.png"))
    tmpv = os.path.join(OUT, "_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", CRF, "-pix_fmt", "yuv420p", tmpv],
                           stdin=subprocess.PIPE)
    rd = reader(); fb = SW * SH * 3; last = None
    for i in range(NF):
        T = i / FPS
        if T < THUMB:
            im = thumb
        elif T < BODY_END:
            t = T - OFF
            raw = rd.stdout.read(fb)
            if len(raw) == fb: last = np.frombuffer(raw, np.uint8).reshape(SH, SW, 3)
            im = place(last, zoom_at(t)).convert("RGBA")
            im = broll(im, t)
            label(im, t); jais(im, t); cal_card(im, t); rcp_card(im, t); sheet_card(im, t); logo_pill(im, t)
            masa_card(im, t); pkg_card(im, t); cta_card(im, t); caption(im, t)
            fade = ease((T - (BODY_END - 0.15)) / 0.15) if T > BODY_END - 0.15 else 0
            if fade: im = Image.blend(im, Image.new("RGBA", (W, H), BLUE), fade)
        else:
            im = endcard(T - BODY_END)
        enc.stdin.write(im.convert("RGB").tobytes())
        if i % 120 == 0: print(f"frame {i}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); rd.kill()
    return tmpv

# ---------- audio ----------
SFXL = [  # (masa timeline, fail, gain dB) — SFX lembut sahaja
    (OFF - 0.12, "whoosh.wav", -24), (OFF + JAIS_IN, "pop.wav", -16), (OFF + CAL[0], "pop.wav", -20),
    *[(OFF + t0, "tick.wav", -25) for t0, *_ in RCP_ITEMS],
    (OFF + SHEET[0], "whoosh.wav", -24), *[(OFF + SHEET[0] + 0.2 + i * 0.42, "tick.wav", -27) for i in range(4)],
    (OFF + SH_ERR, "bonk.wav", -26), *[(OFF + SH_CLOCK + 0.1 + i * 0.4, "tick.wav", -26) for i in range(4)],
    (OFF + LOGO_IN, "ding.wav", -22), (OFF + BA[0] - 0.05, "whoosh.wav", -22), (OFF + BB[0] - 0.05, "whoosh.wav", -22),
    (OFF + MASA[0], "pop.wav", -20), (OFF + MASA_R2, "ding.wav", -26),
    (OFF + PKG[0], "pop.wav", -18), (OFF + PKG_C1, "pop.wav", -22), (OFF + PKG_C2, "pop.wav", -22),
    (OFF + CTA[0], "whoosh.wav", -24), (OFF + CTA_TAP, "click.wav", -18),
    (BODY_END + 0.05, "ding.wav", -24), (BODY_END + TAP, "click.wav", -18),
]
def audio():
    vo = os.path.join(OUT, "_vo.wav")
    af = "highpass=f=70,afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120"
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", SRC, "-af", af + ",loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-af", f"{af},{ln},aresample=48000,adelay={int(OFF*1000)}:all=1,apad",
                    "-t", f"{TOTAL:.3f}", "-ac", "2", vo], check=True)
    # muzik berlesen (Mixkit Stock Music Free License), bertukar ikut babak
    MUS = os.environ.get("YM_MUSIC", os.path.join(os.path.dirname(SFX), "music"))
    X = OFF + 18.66                         # "Inilah keistimewaan Yuran.my": masalah -> penyelesaian
    bed = os.path.join(OUT, "_mus.wav")
    fc = (f"[0]atrim=start=24:duration={X + 0.8:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-33:TP=-6,"
          f"afade=t=in:d=0.6,afade=t=out:st={X - 0.4:.3f}:d=1.0[m1];"
          f"[1]atrim=duration={TOTAL - X + 0.4:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-32:TP=-6,"
          f"afade=t=in:d=0.9,afade=t=out:st={TOTAL - X - 0.3:.3f}:d=0.7,adelay={int((X - 0.4) * 1000)}:all=1[m2];"
          f"[m1][m2]amix=inputs=2:normalize=0:duration=longest,"
          f"volume='if(lt(t,{THUMB})+gt(t,{BODY_END}),2.5,1)':eval=frame,apad,atrim=duration={TOTAL:.3f}[mb];"
          f"[2]aresample=48000[vk];[mb][vk]sidechaincompress=threshold=0.04:ratio=3:attack=30:release=350[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MUS, "281.mp3"), "-i", os.path.join(MUS, "32.mp3"), "-i", vo,
                    "-filter_complex", fc, "-map", "[out]", "-ac", "2", bed], check=True)
    ins = ["-i", vo, "-i", bed]; fl = []
    for n, (t, f, g) in enumerate(SFXL):
        ins += ["-i", os.path.join(SFX, f)]
        fl.append(f"[{n+2}]aresample=48000,volume={g}dB,adelay={int(t*1000)}:all=1[s{n}]")
    mix = "".join(f"[s{n}]" for n in range(len(SFXL)))
    fl.append(f"[0][1]{mix}amix=inputs={len(SFXL)+2}:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]")
    out = os.path.join(OUT, "_a.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[a]", "-t", f"{TOTAL:.3f}", out], check=True)
    return out

if __name__ == "__main__":
    v = render(); a = audio()
    dst = os.path.join(OUT, f"{ID}_{TAG}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", dst], check=True)
    os.remove(v)
    print("OK", dst)
