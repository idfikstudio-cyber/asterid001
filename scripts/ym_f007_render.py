# Render Yuran.my YM-F-007 (TOFU+BOFU "Siapa belum bayar").
# usage: python3 ym_f007_render.py <src.mp4> <brolldir: sistem.mp4> <logo_white.png> <sfxdir> <outdir> <W> [crf]
# Avatar TikTok: env YM_TIKTOK atau <dir logo>/tiktok.jpg; muzik: env YM_MUSIC (188.mp3, 587.mp3)
# W=540 -> preview 540x960, W=1080 -> final 1080x1920.
import json, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, BROLL, LOGO, SFX, OUT = sys.argv[1:6]
W = int(sys.argv[6]); H = W * 16 // 9; CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
S = W / 1080  # skala reka bentuk (semua ukuran ditulis untuk 1080)
FPS = 30
ID = "YM-F-007_Siapa_belum_bayar"
TAG = "PREVIEW" if W < 1080 else "FINAL"
os.makedirs(OUT, exist_ok=True)

BLUE, ACC, BLACK, GREY, WHITE = "#2A3B8F", "#29ABE2", "#231F20", "#E7E8E9", "#FFFFFF"
FD = "/usr/share/fonts/opentype/inter/"
def F(w, px): return ImageFont.truetype(FD + {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], max(8, int(px * S)))

SRC_DUR = 34.71
THUMB = 1.0            # thumbnail statik
OFF = THUMB            # masa video asal + OFF = masa timeline
END = 1.5              # end card
BODY_END = OFF + SRC_DUR
TOTAL = BODY_END + END
NF = int(round(TOTAL * FPS))

# ---------- caption (masa video asal, ikut percakapan) ----------
CAP = [
 (0.00, 0.84, "Siapa *belum bayar*"), (0.86, 1.40, "bulan ni?"), (1.42, 2.54, "Cikgu pun buka"), (2.56, 3.62, "lah *buku.*"),
 (3.64, 4.32, "*Selak,*"), (4.34, 4.88, "*selak,*"), (4.90, 5.32, "*selak.*"),
 (5.34, 6.00, "Ada nama yang"), (6.02, 6.54, "*dah bayar*"), (6.56, 8.10, "tapi lupa nak *record.*"),
 (8.12, 9.40, "Ada yang *belum bayar*"), (9.42, 10.46, "tapi lupa nak"), (10.48, 11.38, "hantar *reminder.*"),
 (11.40, 12.16, "Nak follow up,"), (12.18, 12.94, "*segan-segan.*"), (12.96, 13.56, "Macam kita ni"), (13.58, 14.88, "collect hutang ke tak?"),
 (14.90, 15.98, "Sebabnya *takut*"), (16.00, 16.76, "bila follow up,"), (16.78, 17.90, "*tersalah* pula."),
 (17.92, 18.96, "Dia dah pernah bayar"), (18.98, 19.80, "tapi kita kata"), (19.82, 20.52, "*belum bayar.*"),
 (20.54, 21.46, "*Yuran.my*"), (21.48, 23.32, "tunjukkan *status* ni."), (23.34, 24.08, "Settle."),
 (24.10, 24.82, "*Dikemas kini*"), (24.84, 25.36, "setiap kali"), (25.38, 26.28, "*pembayaran* masuk."),
 (26.30, 27.44, "Follow up jadi *tepat.*"), (27.46, 27.96, "Confirm."), (27.98, 29.32, "Tak perlu teka-teka lagi."),
 (29.34, 30.28, "Klik saja *reminder*"), (30.30, 31.20, "terus *hantar.*"),
 (31.22, 31.94, "Klik link di bio"), (31.96, 32.86, "untuk *demo*"), (32.88, 34.71, "sistem *Yuran.my.*"),
]
ZOOM = [(0.00, 1.00), (1.40, 1.12), (5.32, 1.00), (11.38, 1.12), (14.88, 1.00), (17.90, 1.12), (20.52, 1.00),
        (26.28, 1.12), (29.32, 1.00), (31.20, 1.12)]
BOOK = (1.42, 5.32); FLIPS = [2.72, 3.64, 4.34, 4.90]      # buka buku, selak x3
LIST = (5.34, 11.38); L1, L1X, L2, L2X = 5.34, 7.64, 8.12, 10.74
CHAT = (11.40, 14.88); TYPE_A, TYPE_B, DEL_A, DEL_B = 11.50, 12.30, 12.50, 13.40
WRONG = (14.90, 20.52); W2 = 17.92
LOGO_IN, LOGO_OUT = 20.46, 21.46
BA = (21.46, 24.40)    # status: B-Roll_SistemYuran.my @0:30 (tapis Overdue)
BB = (24.40, 26.30)    # dikemas kini: B-Roll_SistemYuran.my @0:42.6 (tapis Paid)
TEPAT = (26.28, 29.32); T2 = 27.98
REM = (29.32, 31.20); REM_TAP = 30.30
CTA = (31.20, 34.71); CTA_TAP = 31.50
LABEL_IN, LABEL_OUT = 0.25, 1.40
THUMB_SRC_T = 0.9
LOW_WINS = [BOOK, LIST, CHAT, WRONG, (LOGO_IN, LOGO_OUT), BA, BB, TEPAT, REM, CTA]
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
# ---------- babak masalah ----------
def book_card(base, t):
    if not inwin(t, BOOK): return
    ch = H * 0.19; lay, d, k, ko = card_base(t, BOOK, ch); cw = lay.width
    bx0, by0, bw, bh = cw * 0.12, ch * 0.12, cw * 0.76, ch * 0.76
    mid_ = bx0 + bw / 2
    d.rectangle((bx0 - 8 * S, by0 + 6 * S, bx0 + bw + 8 * S, by0 + bh + 10 * S), fill="#8A5A3B")   # kulit buku
    def page(x0, x1, shade):
        d.rectangle((min(x0, x1), by0, max(x0, x1), by0 + bh), fill=shade, outline="#D6CDB8")
        if abs(x1 - x0) > 30 * S:
            for i in range(6):
                yy = by0 + bh * (0.15 + i * 0.13); a, b = sorted((x0, x1))
                d.line((a + 16 * S, yy, a + (b - a) * 0.8, yy), fill="#C9C0AA", width=max(1, int(3 * S)))
    page(bx0, mid_, "#FFFDF6"); page(mid_, bx0 + bw, "#FFFDF6")
    for ft in FLIPS:   # muka surat diselak dari kanan ke kiri
        if ft <= t < ft + 0.45:
            p = ease((t - ft) / 0.45); x = mid_ + (bw / 2) * math.cos(p * math.pi)
            page(mid_, x, "#F3EEDF" if p < 0.5 else "#FFFDF6")
    d.line((mid_, by0, mid_, by0 + bh), fill="#B8AE96", width=max(2, int(4 * S)))
    put_card(base, lay, k, ko, 0.585)

def chip(d, x, y, h, label, fg, bg, f):
    w = d.textlength(label, font=f) + 36 * S
    d.rounded_rectangle((x, y - h / 2, x + w, y + h / 2), radius=int(h / 2), fill=bg)
    d.text((x + 18 * S, y), label, font=f, fill=fg, anchor="lm"); return w
def list_card(base, t):
    if not inwin(t, LIST): return
    ch = H * 0.15; lay, d, k, ko = card_base(t, LIST, ch); cw = lay.width
    fc = F("b", 32)
    for i, (t0, tx, ok, lab, bad) in enumerate(((L1, L1X, True, "Dah bayar", "Tak direkod"), (L2, L2X, False, "Belum bayar", "Tiada reminder"))):
        if t < t0: continue
        y = ch * (0.30 + i * 0.42); ka = ease((t - t0) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        d2.ellipse((30 * S, y - 26 * S, 82 * S, y + 26 * S), fill=GREY)
        d2.rounded_rectangle((100 * S, y - 12 * S, 300 * S, y + 12 * S), radius=int(6 * S), fill="#C9CED8")
        x = 330 * S
        x += chip(d2, x, y, 56 * S, lab, "#1F7A4D" if ok else "#C8435A", "#DDF3E6" if ok else "#FBE3E7", fc) + 14 * S
        if t >= tx:
            kb = ease((t - tx) / 0.25)
            l3 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d3 = ImageDraw.Draw(l3)
            mark(d3, int(x + 22 * S), y, int(20 * S), False)
            d3.text((x + 52 * S, y), bad, font=F("xb", 32), fill="#C8435A", anchor="lm")
            l2.alpha_composite(fade_layer(l3, kb))
        lay.alpha_composite(fade_layer(l2, ka))
    put_card(base, lay, k, ko, 0.595)

def chat_card(base, t):
    if not inwin(t, CHAT): return
    ch = H * 0.15; lay, d, k, ko = card_base(t, CHAT, ch); cw = lay.width
    d.rounded_rectangle((0, 0, cw - 1, int(ch * 0.30)), radius=int(30 * S), fill="#E9F3EF")
    d.rectangle((0, int(ch * 0.15), cw - 1, int(ch * 0.30)), fill="#E9F3EF")
    d.ellipse((24 * S, ch * 0.15 - 20 * S, 64 * S, ch * 0.15 + 20 * S), fill="#B9C2CC")
    d.text((80 * S, ch * 0.15), "Ibu bapa", font=F("b", 30), fill=BLACK, anchor="lm")
    msg = "Assalamualaikum puan, yuran bulan ni..."
    if t < TYPE_B: n = int(len(msg) * max(0, (t - TYPE_A) / (TYPE_B - TYPE_A)))
    elif t < DEL_A: n = len(msg)
    else: n = int(len(msg) * (1 - min(1, (t - DEL_A) / (DEL_B - DEL_A))))   # dipadam semula (segan)
    by = ch * 0.66; bh = ch * 0.38
    d.rounded_rectangle((24 * S, by - bh / 2, cw - 120 * S, by + bh / 2), radius=int(bh / 2), fill=GREY)
    fm = F("m", 30); txt = msg[:n]
    while d.textlength(txt, font=fm) > cw - 190 * S and len(txt) > 1: txt = txt[1:]
    d.text((50 * S, by), txt if n else "Taip mesej...", font=fm, fill=BLACK if n else "#8D8F93", anchor="lm")
    cx = 50 * S + (d.textlength(txt, font=fm) if n else 0) + 4 * S
    if int(t * 4) % 2 == 0: d.line((cx, by - bh * 0.3, cx, by + bh * 0.3), fill=ACC, width=max(2, int(3 * S)))
    bx = cw - 66 * S; r = 34 * S
    d.ellipse((bx - r, by - r, bx + r, by + r), fill="#25A36F" if n else "#B9BBBF")
    a = 14 * S; d.polygon([(bx - a, by - a), (bx + a + 2, by), (bx - a, by + a), (bx - a * 0.45, by)], fill=WHITE)
    put_card(base, lay, k, ko, 0.595)

def wrong_card(base, t):
    if not inwin(t, WRONG): return
    ch = H * 0.15; lay, d, k, ko = card_base(t, WRONG, ch)
    f = F("b", 42); fb = F("xb", 46); y1, y2 = ch * 0.30, ch * 0.70
    mark(d, int(55 * S), y1, int(26 * S), False)
    d.text((int(100 * S), y1), "Kita kata: ", font=f, fill="#6B6E75", anchor="lm")
    d.text((int(100 * S) + d.textlength("Kita kata: ", font=f), y1), "Belum bayar", font=f, fill="#C8435A", anchor="lm")
    if t >= W2:
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        mark(d2, int(55 * S), y2, int(26 * S), True)
        d2.text((int(100 * S), y2), "Sebenarnya: ", font=fb, fill=BLACK, anchor="lm")
        d2.text((int(100 * S) + d2.textlength("Sebenarnya: ", font=fb), y2), "Dah bayar", font=fb, fill="#1F7A4D", anchor="lm")
        lay.alpha_composite(fade_layer(l2, ease((t - W2) / 0.25)))
    put_card(base, lay, k, ko, 0.595)

# ---------- babak penyelesaian ----------
_clips = {}
INV_CROP = (1100, 440, 820, 592)                              # bahagian kanan senarai invois: Items | Total | Status | Actions
INV_BLUR = [(0, 0, 442, 592), (440, 0, 528, 592)]           # lajur Items (nama pelajar) & Total RM individu
STATUS_COL = (530, 0, 612, 592)                               # lajur Status (callout)
def clips():
    if not _clips:
        _clips["ba"] = clip_frames(os.path.join(BROLL, "sistem.mp4"), 31.3, BA[1] - BA[0] + 0.1, INV_CROP, INV_BLUR)
        _clips["bb"] = clip_frames(os.path.join(BROLL, "sistem.mp4"), 44.3, BB[1] - BB[0] + 0.1, INV_CROP, INV_BLUR)
    return _clips
_bg = {}
def broll(base, t):
    for key, (a, b), w, cy in (("ba", BA, 0.98, 0.40), ("bb", BB, 0.98, 0.40)):
        if not (a <= t < b): continue
        fr_list = clips()[key]; i = min(len(fr_list) - 1, int((t - a) * 30)); img = fr_list[i]
        kin = ease((t - a) / 0.22) if key == "ba" else 1
        kout = (1 - ease((t - (b - 0.22)) / 0.22)) if key == "bb" else 1
        k = kin * kout; p = (t - a) / (b - a)
        if key not in _bg:
            bgi = img.resize((int(img.width * H / img.height), H), Image.LANCZOS)
            bgi = bgi.crop(((bgi.width - W) // 2, 0, (bgi.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40 * S))
            _bg[key] = Image.blend(bgi.convert("RGBA"), Image.new("RGBA", (W, H), "#0D1122"), 0.62)
        fr = _bg[key].copy()
        # zoom perlahan + callout pada lajur Status
        z = 1.0 + 0.08 * p; cwid = img.width / z; chgt = img.height / z
        x0 = (img.width - cwid) * 0.8; y0 = 0
        im2 = img.crop((int(x0), int(y0), int(x0 + cwid), int(y0 + chgt))).convert("RGBA")
        dd = ImageDraw.Draw(im2); sx0, _, sx1, _ = STATUS_COL
        pul = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.5)
        dd.rounded_rectangle((sx0 - x0, 4, sx1 - x0, chgt - 4), radius=10, outline=(41, 171, 226, int(150 + 100 * pul)), width=6)
        c = shadowed(card_img(im2, W * w))
        fr.alpha_composite(c, (int(W * 0.50 - c.width / 2), int(H * cy - c.height / 2 + (1 - kin) * 40 * S)))
        return Image.blend(base, fr, k)
    return base

def tepat_card(base, t):
    if not inwin(t, TEPAT): return
    ch = H * 0.15; lay, d, k, ko = card_base(t, TEPAT, ch)
    fb = F("xb", 46); y1, y2 = ch * 0.30, ch * 0.70
    mark(d, int(55 * S), y1, int(26 * S), True)
    d.text((int(100 * S), y1), "Follow up ", font=fb, fill=BLACK, anchor="lm")
    d.text((int(100 * S) + d.textlength("Follow up ", font=fb), y1), "tepat", font=fb, fill=ACC, anchor="lm")
    if t >= T2:
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        mark(d2, int(55 * S), y2, int(26 * S), True)
        d2.text((int(100 * S), y2), "Tak perlu teka-teka", font=fb, fill=BLACK, anchor="lm")
        lay.alpha_composite(fade_layer(l2, ease((t - T2) / 0.25)))
    put_card(base, lay, k, ko, 0.595)

def rem_card(base, t):
    if not inwin(t, REM): return
    ch = H * 0.13; lay, d, k, ko = card_base(t, REM, ch); cw = lay.width
    done = t >= REM_TAP + 0.1
    pr = 1 - 0.10 * math.sin(min(1, max(0, (t - REM_TAP) / 0.16)) * math.pi)
    bw, bh = cw * 0.80 * pr, ch * 0.56 * pr; bx, by = cw / 2, ch / 2
    d.rounded_rectangle((bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), radius=int(bh / 2), fill="#1F7A4D" if done else BLUE)
    lab = "Reminder dihantar" if done else "Hantar reminder"
    fb = F("xb", 44); tw = d.textlength(lab, font=fb)
    if done: mark(d, int(bx - tw / 2 - 30 * S), by, int(22 * S), True)
    d.text((bx + (14 * S if done else 0), by), lab, font=fb, fill=WHITE, anchor="mm")
    if REM_TAP <= t < REM_TAP + 0.45:
        r = (t - REM_TAP) / 0.45; rr = 30 * S + 70 * S * r
        d.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=(41, 171, 226, int(220 * (1 - r))), width=max(2, int(6 * S)))
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
    draw_rich(im, CX, H * 0.52, "Siapa", f, stroke=9)
    draw_rich(im, CX, H * 0.605, "*belum*", f, stroke=9)
    d = ImageDraw.Draw(im); fk = F("xb", 132)
    tw = d.textlength("BAYAR?", font=fk); bw, bh = int(tw + 70 * S), int(172 * S)
    bx, by = int(CX - bw / 2), int(H * 0.695 - bh / 2)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(26 * S), fill="#C8435A")
    d.text((CX, H * 0.695), "BAYAR?", font=fk, fill=WHITE, anchor="mm")
    # kad status kecil sebagai hook tambahan (kiri muka): dah bayar / ? / belum
    cw, chh = int(420 * S), int(300 * S)
    card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, cw - 1, chh - 1), radius=int(26 * S), fill=WHITE)
    for i, (lab, fg, bg) in enumerate((("Dah bayar", "#1F7A4D", "#DDF3E6"), ("?", "#6B6E75", GREY), ("Belum", "#C8435A", "#FBE3E7"))):
        y = chh * (0.2 + i * 0.3)
        cd.ellipse((22 * S, y - 24 * S, 70 * S, y + 24 * S), fill=GREY)
        cd.rounded_rectangle((86 * S, y - 12 * S, 186 * S, y + 12 * S), radius=int(6 * S), fill="#C9CED8")
        chip(cd, 196 * S, y, 56 * S, lab, fg, bg, F("b", 30))
    sh = shadowed(card, 14, 120).rotate(-4, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(sh, (int(W * 0.215 - sh.width / 2), int(H * 0.19 - sh.height / 2)))
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
            label(im, t); book_card(im, t); list_card(im, t); chat_card(im, t); wrong_card(im, t); logo_pill(im, t)
            tepat_card(im, t); rem_card(im, t); cta_card(im, t); caption(im, t)
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
    (OFF - 0.12, "whoosh.wav", -24), (OFF + BOOK[0], "pop.wav", -20), *[(OFF + ft, "whoosh.wav", -26) for ft in FLIPS],
    (OFF + L1, "pop.wav", -22), (OFF + L1X, "bonk.wav", -27), (OFF + L2, "pop.wav", -22), (OFF + L2X, "bonk.wav", -27),
    (OFF + CHAT[0], "pop.wav", -22), *[(OFF + TYPE_A + 0.1 + i * 0.2, "tick.wav", -28) for i in range(4)],
    (OFF + WRONG[0], "pop.wav", -20), (OFF + W2, "ding.wav", -26),
    (OFF + LOGO_IN, "ding.wav", -22), (OFF + BA[0] - 0.05, "whoosh.wav", -22), (OFF + BB[0], "click.wav", -24),
    (OFF + TEPAT[0], "pop.wav", -20), (OFF + T2, "pop.wav", -22),
    (OFF + REM[0], "pop.wav", -20), (OFF + REM_TAP, "click.wav", -18), (OFF + REM_TAP + 0.15, "ding.wav", -26),
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
    X = OFF + 20.54                         # "Yuran.my tunjukkan status ni": masalah -> penyelesaian
    bed = os.path.join(OUT, "_mus.wav")
    fc = (f"[0]atrim=start=18:duration={X + 0.8:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-33:TP=-6,"
          f"afade=t=in:d=0.6,afade=t=out:st={X - 0.4:.3f}:d=1.0[m1];"
          f"[1]atrim=start=30:duration={TOTAL - X + 0.4:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-32:TP=-6,"
          f"afade=t=in:d=0.9,afade=t=out:st={TOTAL - X - 0.3:.3f}:d=0.7,adelay={int((X - 0.4) * 1000)}:all=1[m2];"
          f"[m1][m2]amix=inputs=2:normalize=0:duration=longest,"
          f"volume='if(lt(t,{THUMB})+gt(t,{BODY_END}),2.5,1)':eval=frame,apad,atrim=duration={TOTAL:.3f}[mb];"
          f"[2]aresample=48000[vk];[mb][vk]sidechaincompress=threshold=0.04:ratio=3:attack=30:release=350[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MUS, "188.mp3"), "-i", os.path.join(MUS, "587.mp3"), "-i", vo,
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
