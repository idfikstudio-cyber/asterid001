# Render Yuran.my YM-F-005 (TOFU "Duit yuran dalam laci").
# usage: python3 ym_f005_render.py <src.mp4> <brolldir: a1.jpg a2.jpg a3.png a4.jpg> <logo_white.png> <sfxdir> <outdir> <W> [crf]
# Avatar TikTok: env YM_TIKTOK atau <dir logo>/tiktok.jpg
# W=540 -> preview 540x960, W=1080 -> final 1080x1920.
import json, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, BROLL, LOGO, SFX, OUT = sys.argv[1:6]
W = int(sys.argv[6]); H = W * 16 // 9; CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
S = W / 1080  # skala reka bentuk (semua ukuran ditulis untuk 1080)
FPS = 30
ID = "YM-F-005_Duit_yuran_dalam_laci"
TAG = "PREVIEW" if W < 1080 else "FINAL"
os.makedirs(OUT, exist_ok=True)

BLUE, ACC, BLACK, GREY, WHITE = "#2A3B8F", "#29ABE2", "#231F20", "#E7E8E9", "#FFFFFF"
FD = "/usr/share/fonts/opentype/inter/"
def F(w, px): return ImageFont.truetype(FD + {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], max(8, int(px * S)))

SRC_DUR = 39.87
THUMB = 1.0            # thumbnail statik
OFF = THUMB            # masa video asal + OFF = masa timeline
END = 1.5              # end card
BODY_END = OFF + SRC_DUR
TOTAL = BODY_END + END
NF = int(round(TOTAL * FPS))

# ---------- caption (masa video asal, ikut percakapan) ----------
CAP = [
 (0.00, 1.06, "Duit *yuran* dalam *laci,*"), (1.08, 2.08, "pagi tadi kutip,"), (2.10, 2.94, "petang nanti baru"), (2.96, 3.70, "nak pergi bank-in."),
 (3.72, 4.32, "Kalau *hilang,*"), (4.34, 5.10, "siapa yang *tanggung?*"),
 (5.18, 6.06, "Pernah kan jadi kes"), (6.08, 7.26, "sekolah kena *pecah masuk*"), (7.26, 8.36, "dan lastnya"), (8.38, 9.50, "duit tu *hilang.*"),
 (9.82, 11.04, "Siapa yang akan *tanggung?*"), (11.06, 12.56, "Siapa yang akan *dipersalahkan?*"), (12.58, 13.80, "Siapa yang akan *rugi?*"),
 (13.92, 15.10, "Itu belum cerita lagi"), (15.12, 16.12, "kalau duit *kurang,*"), (16.14, 17.12, "siapa yang akan"), (17.14, 17.88, "*dipersalahkan?*"),
 (17.90, 18.56, "Dan siapa yang"), (18.58, 19.30, "akan *ganti?*"),
 (19.32, 20.00, "Ini bukan soal"), (20.02, 20.66, "*amanah* ya."), (20.68, 21.90, "Guru KAFA saya jamin,"), (21.92, 22.60, "mesti *amanah.*"),
 (22.62, 24.60, "Ini adalah soal *sistem.*"),
 (24.64, 25.46, "*Sistem* yang akan"), (25.48, 26.20, "*lindungi* cikgu."), (26.22, 27.26, "*Sistem* juga yang akan"), (27.28, 28.10, "*lindungi* ibu bapa."),
 (28.12, 29.62, "So sekolah cikgu,"), (29.64, 30.42, "ketua guru,"), (30.44, 31.34, "masih gunakan"), (31.36, 32.44, "*tunai* cash ke?"),
 (32.46, 33.74, "Kongsikan pengalaman."),
 (33.76, 35.06, "Ada tak sekolah anda"), (35.08, 36.44, "ataupun sekolah"), (36.46, 37.64, "ketua guru yang lain"), (37.66, 39.14, "kena *pecah masuk?*"),
 (39.16, 39.87, "Cuba *komen.*"),
]
# punch-in ikut ayat (tiada potongan; footage sudah ditrim)
ZOOM = [(0.00, 1.00), (3.70, 1.12), (5.15, 1.00), (13.90, 1.12), (17.88, 1.00), (20.66, 1.12), (22.60, 1.00),
        (24.62, 1.12), (28.10, 1.00), (32.44, 1.12), (33.74, 1.00)]
# B-roll artikel (maks 3 s setiap satu; suara terus berjalan)
B1 = (5.40, 8.40)      # hantaran "SEKOLAH KAFAI AS SYARIFF BANTING KENA PECAH MASUK"
B2 = (9.75, 12.75)     # artikel "Polis buru suspek pecah masuk sekolah agama curi duit" + tajuk Media Selangor
B2_STRIP = 11.10
B3 = (33.70, 36.70)    # gambar pejabat sekolah selepas pecah masuk
CARD1 = (19.30, 28.10)  # amanah -> sistem -> lindungi
CARD1_R2, CARD1_B, CARD1_C1, CARD1_C2 = 22.60, 24.62, 25.45, 27.25
POLL = (28.40, 32.40)   # "masih gunakan tunai?"
CMT_IN = 36.80
TYPE_A, TYPE_B = 37.05, 38.70
LABEL_IN, LABEL_OUT = 0.25, 3.25          # "Farhan · Yuran.my"
THUMB_SRC_T = 2.4
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
def zoom_at(t):
    z = 1.0
    for a, v in ZOOM:
        if t >= a: z = v
    return z
def place(fr, z):
    im = Image.fromarray(fr)
    if z != 1.0:
        cw, ch = SW / z, SH / z
        cx, cy = SW / 2, SH * 0.30          # muka kekal di sepertiga atas
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
    y = H * (0.545 if t >= CMT_IN else 0.755 if (inwin(t, B1) or inwin(t, B2) or inwin(t, B3) or inwin(t, CARD1) or inwin(t, POLL)) else 0.64)
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

# ---------- bahan B-roll artikel ----------
def blur_boxes(im, boxes, r=16):
    im = im.copy()
    for bx in boxes:
        reg = im.crop(bx).filter(ImageFilter.GaussianBlur(r)); im.paste(reg, bx[:2])
    return im
_A1 = Image.open(os.path.join(BROLL, "a1.jpg")).convert("RGB").crop((0, 0, 1224, 1420))   # nama sekolah tidak diblur (arahan Farhan: berita awam)
_A2 = Image.open(os.path.join(BROLL, "a2.jpg")).convert("RGB")
_A3 = Image.open(os.path.join(BROLL, "a3.png")).convert("RGB")
_A4H = Image.open(os.path.join(BROLL, "a4.jpg")).convert("RGB").crop((0, 0, 830, 78))
_bgcache = {}
def card_img(img, w, rad=24):
    h = int(img.height * w / img.width)
    c = img.resize((int(w), h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), radius=int(rad * S), fill=255)
    c.putalpha(m); return c
def shadowed(c, r=18, a=130):
    sh = Image.new("RGBA", (c.width + 100, c.height + 100), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((50, 62, c.width + 50, c.height + 62), radius=int(24 * S), fill=(0, 0, 0, a))
    sh = sh.filter(ImageFilter.GaussianBlur(r * S)); sh.alpha_composite(c, (50, 50)); return sh
def bg_of(key, img):
    if key not in _bgcache:
        b = img.resize((W, int(img.height * W / img.width)) if img.width / img.height > W / H else (int(img.width * H / img.height), H), Image.LANCZOS)
        b = b.crop(((b.width - W) // 2, (b.height - H) // 2, (b.width - W) // 2 + W, (b.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(40 * S))
        b = Image.blend(b.convert("RGBA"), Image.new("RGBA", (W, H), "#0D1122"), 0.62)
        _bgcache[key] = b
    return _bgcache[key].copy()
def broll(base, t):
    for key, (a, b), img, w, cy in (("a1", B1, _A1, 0.84, 0.40), ("a3", B2, _A3, 0.80, 0.37), ("a2", B3, _A2, 1.10, 0.40)):
        if not (a <= t < b): continue
        k = ease((t - a) / 0.22) * (1 - ease((t - (b - 0.22)) / 0.22))
        p = (t - a) / (b - a)
        fr = bg_of(key, img)
        c = shadowed(card_img(img, W * w * (1.0 + 0.035 * p)))
        fr.alpha_composite(c, (int(W * 0.47 - c.width / 2), int(H * cy - c.height / 2 + (1 - k) * 40 * S)))
        if key == "a3" and t >= B2_STRIP:
            ks = ease((t - B2_STRIP) / 0.3)
            s2 = shadowed(card_img(_A4H, W * 0.80, 14), 12, 110)
            s2.putalpha(s2.getchannel("A").point(lambda v: int(v * ks)))
            fr.alpha_composite(s2, (int(W * 0.47 - s2.width / 2 + (1 - ks) * 60 * S), int(H * 0.675 - s2.height / 2)))
        return Image.blend(base, fr, k)
    return base

# ---------- kad grafik (putih, di dada; muka tidak ditutup) ----------
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
def shield(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r * 0.85, cy - r * 0.6), (cx + r * 0.75, cy + r * 0.25), (cx, cy + r), (cx - r * 0.75, cy + r * 0.25), (cx - r * 0.85, cy - r * 0.6)], fill=fill)
    w = max(2, int(4 * S))
    d.line([(cx - r * 0.35, cy), (cx - r * 0.05, cy + r * 0.3), (cx + r * 0.4, cy - r * 0.3)], fill=WHITE, width=w, joint="curve")
def card1(base, t):
    if not inwin(t, CARD1): return
    ch = H * 0.15
    lay, d, k, ko = card_base(t, CARD1, ch); cw = lay.width
    f = F("b", 46); fb = F("xb", 50)
    if t < CARD1_B:
        y1, y2 = ch * 0.30, ch * 0.70
        d.text((int(100 * S), y1), "Bukan soal amanah", font=f, fill="#8D8F93", anchor="lm")
        tw = d.textlength("Bukan soal amanah", font=f)
        mark(d, int(55 * S), y1, int(26 * S), False)
        if t >= CARD1_R2:
            d.line((int(100 * S), y1, int(100 * S) + tw * min(1, (t - CARD1_R2) / 0.3), y1), fill="#8D8F93", width=max(2, int(4 * S)))
            k2 = ease((t - CARD1_R2) / 0.25)
            lay2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
            mark(d2, int(55 * S), y2, int(26 * S), True)
            d2.text((int(100 * S), y2), "Soal ", font=fb, fill=BLACK, anchor="lm")
            d2.text((int(100 * S) + d2.textlength("Soal ", font=fb), y2), "SISTEM", font=fb, fill=ACC, anchor="lm")
            lay2.putalpha(lay2.getchannel("A").point(lambda v: int(v * k2))); lay.alpha_composite(lay2)
    else:
        kb = ease((t - CARD1_B) / 0.25)
        lay2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
        shield(d2, int(60 * S), ch * 0.30, int(30 * S), BLUE)
        d2.text((int(110 * S), ch * 0.30), "Sistem melindungi", font=fb, fill=BLUE, anchor="lm")
        for i, (tc, lab) in enumerate(((CARD1_C1, "Cikgu"), (CARD1_C2, "Ibu bapa"))):
            if t < tc: continue
            kc = ease((t - tc) / 0.25)
            x0 = int((40 + i * 330) * S); y0 = int(ch * 0.55); pw, ph = int(300 * S), int(ch * 0.33)
            pl = Image.new("RGBA", lay.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
            pd.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=ph // 2, fill="#D8F0FB")
            mark(pd, x0 + int(38 * S), y0 + ph // 2, int(20 * S), True)
            pd.text((x0 + int(72 * S), y0 + ph // 2), lab, font=F("b", 40), fill=BLUE, anchor="lm")
            pl.putalpha(pl.getchannel("A").point(lambda v: int(v * kc))); lay2.alpha_composite(pl)
        lay2.putalpha(lay2.getchannel("A").point(lambda v: int(v * kb))); lay.alpha_composite(lay2)
    put_card(base, lay, k, ko, 0.595)
def poll(base, t):
    if not inwin(t, POLL): return
    ch = H * 0.15
    lay, d, k, ko = card_base(t, POLL, ch); cw = lay.width
    d.text((cw // 2, ch * 0.28), "Masih guna tunai?", font=F("xb", 52), fill=BLACK, anchor="mm")
    for i, lab in enumerate(("Ya", "Tak")):
        pw, ph = int(cw * 0.40), int(ch * 0.36); x0 = int(cw * (0.06 + i * 0.48)); y0 = int(ch * 0.52)
        hot = t >= POLL[0] + 0.6 and int((t - POLL[0]) * 2.2) % 2 == i
        d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=int(18 * S), fill="#D8F0FB" if hot else GREY, outline=ACC if hot else None, width=max(2, int(4 * S)))
        d.text((x0 + pw // 2, y0 + ph // 2), lab, font=F("b", 44), fill=BLUE, anchor="mm")
    put_card(base, lay, k, ko, 0.595)

# ---------- motion komen: ajak kongsi pengalaman ----------
def comments(base, t):
    if t < CMT_IN: return
    k = ease((t - CMT_IN) / 0.35)
    pw, ph = int(W * 0.78), int(H * 0.21)
    x0 = int(W * 0.46 - pw / 2); y0 = int(H * 0.585 + (1 - k) * H * 0.12)
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = int(34 * S)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=r, fill=(255, 255, 255, 245))
    fh, fn = F("b", 34), F("m", 34)
    d.text((pw // 2, int(44 * S)), "Komen", font=fh, fill=BLACK, anchor="mm")
    d.line((int(30 * S), int(84 * S), pw - int(30 * S), int(84 * S)), fill=GREY, width=max(1, int(2 * S)))
    d.text((pw // 2, int(150 * S)), "Ada sekolah kena pecah masuk?", font=F("sb", 32), fill="#7A7C80", anchor="mm")
    by = ph - int(96 * S); bh = int(70 * S)
    d.rounded_rectangle((int(30 * S), by, pw - int(120 * S), by + bh), radius=bh // 2, fill=GREY)
    msg = "Kongsikan pengalaman..."
    n = int(len(msg) * min(1, max(0, (t - TYPE_A) / (TYPE_B - TYPE_A))))
    typed = msg[:n]
    d.text((int(60 * S), by + bh // 2), typed, font=fn, fill=BLACK, anchor="lm")
    cxp = int(60 * S) + d.textlength(typed, font=fn) + int(4 * S)
    if t >= TYPE_A - 0.1 and int(t * 4) % 2 == 0:
        d.line((cxp, by + int(18 * S), cxp, by + bh - int(18 * S)), fill=ACC, width=max(2, int(3 * S)))
    bx = pw - int(62 * S); bcy = by + bh // 2
    pulse = 1 + 0.10 * math.sin(max(0, t - TYPE_B) * 2 * math.pi * 1.8) if t >= TYPE_B else 1
    br = int(36 * S * pulse)
    d.ellipse((bx - br, bcy - br, bx + br, bcy + br), fill=ACC if n else "#B9BBBF")
    a = int(15 * S * pulse)
    d.polygon([(bx - a, bcy - a), (bx + a + 2, bcy), (bx - a, bcy + a), (bx - a * 0.45, bcy)], fill=WHITE)
    sh = Image.new("RGBA", (pw + 80, ph + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, pw + 40, ph + 50), radius=r, fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(16 * S)); sh.alpha_composite(lay, (40, 40))
    sh.putalpha(sh.getchannel("A").point(lambda v: int(v * min(1, k * 1.5))))
    base.alpha_composite(sh, (x0 - 40, y0 - 40))

# ---------- thumbnail ----------
def thumbnail():
    fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(THUMB_SRC_T), "-i", SRC, "-vf", GRADE, "-frames:v", "1",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = place(np.frombuffer(fr, np.uint8).reshape(SH, SW, 3), 1.08).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(int(H * 0.40), H):
        gd.line((0, y, W, y), fill=(20, 24, 50, int(170 * min(1, (y - H * 0.40) / (H * 0.25)))))
    im.alpha_composite(g)
    f = F("xb", 128)
    draw_rich(im, CX, H * 0.52, "Duit *yuran*", f, stroke=9)
    draw_rich(im, CX, H * 0.605, "dalam", f, stroke=9)
    d = ImageDraw.Draw(im); fk = F("xb", 140)
    tw = d.textlength("LACI?", font=fk); bw, bh = int(tw + 70 * S), int(178 * S)
    bx, by = int(CX - bw / 2), int(H * 0.70 - bh / 2)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(26 * S), fill=ACC)
    d.text((CX, H * 0.70), "LACI?", font=fk, fill=WHITE, anchor="mm")
    # gambar kes pecah masuk sebagai hook tambahan (kiri muka)
    ph = Image.open(os.path.join(BROLL, "a1.jpg")).convert("RGB").crop((384, 300, 838, 932))
    c = card_img(ph, 250 * S, 18)
    fr_ = Image.new("RGBA", (c.width + int(16 * S), c.height + int(16 * S)), (0, 0, 0, 0))
    ImageDraw.Draw(fr_).rounded_rectangle((0, 0, fr_.width - 1, fr_.height - 1), radius=int(24 * S), fill=WHITE)
    fr_.alpha_composite(c, (int(8 * S), int(8 * S)))
    tg = F("xb", 34); dd = ImageDraw.Draw(fr_)
    tw2 = dd.textlength("PECAH MASUK", font=tg); tx0 = (fr_.width - tw2) / 2 - 14 * S; ty0 = fr_.height - 70 * S
    dd.rounded_rectangle((tx0, ty0, tx0 + tw2 + 28 * S, ty0 + 52 * S), radius=int(10 * S), fill="#C8435A")
    dd.text((fr_.width / 2, ty0 + 26 * S), "PECAH MASUK", font=tg, fill=WHITE, anchor="mm")
    rot = shadowed(fr_, 14, 120).rotate(5, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(rot, (int(W * 0.17 - rot.width / 2), int(H * 0.265 - rot.height / 2)))
    return im

# ---------- end card: follow TikTok (arahan Farhan, tanpa emel) ----------
_l = Image.open(LOGO).convert("RGBA")
TIKTOK = os.environ.get("YM_TIKTOK", os.path.join(os.path.dirname(LOGO), "tiktok.jpg"))
_av = Image.open(TIKTOK).convert("RGBA").crop((37, 22, 202, 187))   # avatar dari BRAND/Yuran Tiktok.jpg
TAP = 0.80
def endcard(t):
    im = Image.new("RGBA", (W, H), BLUE); d = ImageDraw.Draw(im)
    x = W * 0.47; k = ease(t / 0.35)
    lw = int(380 * S); lh = int(_l.height * lw / _l.width)
    im.alpha_composite(_l.resize((lw, lh), Image.LANCZOS), (int(x - lw / 2), int(H * 0.20 - lh / 2 + (1 - k) * 20 * S)))
    f1 = F("xb", 58); y = H * 0.295
    p = [("Cara ", WHITE), ("MUDAH", ACC), (" Urus Yuran", WHITE)]
    tw = sum(d.textlength(s, font=f1) for s, _ in p); xx = x - tw / 2
    for s_, c in p: d.text((xx, y), s_, font=f1, fill=c, anchor="lm"); xx += d.textlength(s_, font=f1)
    # kad profil TikTok
    k2 = ease((t - 0.15) / 0.35)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    cw, ch = W * 0.74, H * 0.16; cx0 = x - cw / 2; cy0 = H * 0.37 + (1 - k2) * 24 * S
    od.rounded_rectangle((cx0, cy0, cx0 + cw, cy0 + ch), radius=int(36 * S), fill=WHITE)
    av = int(ch * 0.70); ax = int(cx0 + 34 * S); ay = int(cy0 + (ch - av) / 2)
    m = Image.new("L", (av, av), 0); ImageDraw.Draw(m).ellipse((0, 0, av - 1, av - 1), fill=255)
    a_ = _av.resize((av, av), Image.LANCZOS); a_.putalpha(m); ov.alpha_composite(a_, (ax, ay))
    tx = ax + av + int(30 * S)
    od.text((tx, cy0 + ch * 0.22), "Yuran.My Street", font=F("b", 44), fill=BLACK, anchor="lm")
    od.text((tx, cy0 + ch * 0.44), "@yuran.my", font=F("m", 34), fill="#6B6E75", anchor="lm")
    # butang Follow: berdenyut, ditekan, jadi Following
    done = t >= TAP + 0.08
    pr = 1 - 0.12 * math.sin(min(1, max(0, (t - TAP) / 0.16)) * math.pi)
    pulse = 1 + 0.05 * math.sin(max(0, t - 0.35) * 2 * math.pi * 2.2) if t < TAP else 1
    bw, bh = 300 * S * pr * pulse, 74 * S * pr * pulse; bx = tx + 150 * S; by = cy0 + ch * 0.74
    lab = "Following ✓" if done else "+ Follow"
    od.rounded_rectangle((bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), radius=int(14 * S), fill="#E7E8E9" if done else "#FE2C55")
    od.text((bx, by), lab, font=F("b", 34), fill=BLACK if done else WHITE, anchor="mm")
    if TAP <= t < TAP + 0.45:   # riak sentuhan
        r = (t - TAP) / 0.45; rr = 30 * S + 60 * S * r
        od.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=(41, 171, 226, int(200 * (1 - r))), width=max(2, int(6 * S)))
    od.text((x, H * 0.60), "Follow TikTok Yuran.my", font=F("xb", 54), fill=WHITE, anchor="mm")
    od.text((x, H * 0.645), "untuk tips urus yuran sekolah", font=F("sb", 42), fill=GREY, anchor="mm")
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
            label(im, t); card1(im, t); poll(im, t); comments(im, t); caption(im, t)
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
    (OFF - 0.12, "whoosh.wav", -24),
    (OFF + B1[0] - 0.05, "whoosh.wav", -22), (OFF + B2[0] - 0.05, "whoosh.wav", -22), (OFF + B2_STRIP, "pop.wav", -22),
    (OFF + B3[0] - 0.05, "whoosh.wav", -22),
    (OFF + CARD1[0], "pop.wav", -18), (OFF + CARD1_R2, "ding.wav", -26), (OFF + CARD1_B, "pop.wav", -20),
    (OFF + CARD1_C1, "pop.wav", -22), (OFF + CARD1_C2, "pop.wav", -22),
    (OFF + POLL[0], "pop.wav", -18), (OFF + CMT_IN, "whoosh.wav", -24),
    (OFF + 37.25, "tick.wav", -27), (OFF + 37.65, "tick.wav", -27), (OFF + 38.05, "tick.wav", -27), (OFF + 38.45, "tick.wav", -27),
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
    X = OFF + CARD1[0]                      # "Ini bukan soal amanah": masalah -> sistem
    bed = os.path.join(OUT, "_mus.wav")
    fc = (f"[0]atrim=start=18:duration={X + 0.8:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-33:TP=-6,"
          f"afade=t=in:d=0.6,afade=t=out:st={X - 0.4:.3f}:d=1.0[m1];"
          f"[1]atrim=duration={TOTAL - X + 0.4:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-32:TP=-6,"
          f"afade=t=in:d=0.9,afade=t=out:st={TOTAL - X - 0.3:.3f}:d=0.7,adelay={int((X - 0.4) * 1000)}:all=1[m2];"
          f"[m1][m2]amix=inputs=2:normalize=0:duration=longest,"
          f"volume='if(lt(t,{THUMB})+gt(t,{BODY_END}),2.5,1)':eval=frame,apad,atrim=duration={TOTAL:.3f}[mb];"
          f"[2]aresample=48000[vk];[mb][vk]sidechaincompress=threshold=0.04:ratio=3:attack=30:release=350[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MUS, "188.mp3"), "-i", os.path.join(MUS, "31.mp3"), "-i", vo,
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
