# Render Yuran.my YM-F-007 (TOFU "Pantau Yuran").
# usage: python3 ym_f007_render.py <src.mp4> <assetdir> <sfxdir> <musicdir> <outdir> <W> [crf]
# assetdir: pantau_{dash,ovd,oct,jun,jul,aug,sep}.png (frame dari B-ROLL/B-Roll Pantau Yuran.mp4) logo_white.png tiktok.jpg
# W=540 -> preview 540x960, W=1080 -> final 1080x1920.
# Dibina daripada ym_f006_render.py (helper sama); bahagian khusus YM-F-007 di bawah.
import json, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, AS, SFX, MUS, OUT = sys.argv[1:6]
W = int(sys.argv[6]); H = W * 16 // 9; CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
S = W / 1080
FPS = 30
ID = "YM-F-007_Pantau_Yuran"
TAG = "PREVIEW" if W < 1080 else "FINAL"
os.makedirs(OUT, exist_ok=True)

BLUE, ACC, BLACK, GREY, WHITE = "#2A3B8F", "#29ABE2", "#231F20", "#E7E8E9", "#FFFFFF"
RED = "#C8435A"
GREEN = "#1F9D57"
FD = "/usr/share/fonts/opentype/inter/"
def F(w, px): return ImageFont.truetype(FD + {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], max(8, int(px * S)))

SRC_DUR = 90.70
THUMB = 1.0
OFF = THUMB
END = 1.5
BODY_END = OFF + SRC_DUR
TOTAL = BODY_END + END
NF = int(round(TOTAL * FPS))

# ---------- caption (masa video asal, ikut percakapan) ----------
CAPS = [
 (0.00, "*Pantau yuran* dalam masa"), (1.10, "*2 minit* sahaja."),
 (2.04, "Tak payah tunggu admin,"), (3.16, "tak payah tunggu kerani,"), (4.26, "tak payah tunggu siapa-siapa."),
 (5.56, "Kita boleh check sendiri"), (6.38, "gunakan *handphone,*"), (7.64, "*tablet,*"), (8.26, "*komputer,*"),
 (8.88, "apa sahaja device"), (9.72, "yang boleh connect"), (10.54, "dengan internet."),
 (11.26, "Nak pantau prestasi *yuran*"), (13.04, "yang masuk,"), (13.74, "kita sediakan *dashboard*"), (14.64, "untuk anda pantau"),
 (16.28, "dan semak"), (17.10, "secara konsisten."),
 (18.16, "Berapa yang *unpaid,*"), (19.84, "berapa yang *overdue,*"), (21.36, "berapa lama dah *overdue.*"),
 (23.26, "Semuanya dalam sistem"), (24.36, "kita sediakan."),
 (25.02, "Jom saya tunjukkan *dashboard,*"), (26.72, "pantau yuran"), (27.68, "guna *handphone* sahaja."),
 (28.94, "Bila kita dah login,"), (29.94, "kita akan tengok semua"), (30.98, "prestasi-prestasi"), (32.24, "tentang yuran"), (33.18, "yang kita kenakan."),
 (34.02, "Yang ini sekarang ni"), (34.98, "ada *200.*"), (36.30, "*200* ni maksudnya"), (37.50, "*200 pelanggan.*"),
 (39.40, "Kita ada satu sahaja"), (40.36, "program."), (41.06, "Boleh kita tengok view dah,"), (42.26, "berapa yang *overdue.*"),
 (43.58, "Ini saya nak tekankan"), (44.70, "dekat sini adalah"), (45.58, "*bulanan collection.*"),
 (47.22, "Contoh,"), (47.54, "kita semak pada bulan *Jun.*"), (48.84, "Bila kita semak"), (49.44, "pada bulan *Jun,*"),
 (50.22, "waktu ni dia tak"), (50.94, "guna sistem lagi."), (51.88, "Jadinya tak ada *record,*"), (53.02, "tak ada *data.*"),
 (53.44, "Jadi, kalau kita nak tengok"), (54.74, "bulan *Julai.*"), (55.40, "Pada bulan *Julai,*"), (56.16, "kita dah tahu dah"),
 (56.94, "berapa peratus"), (57.82, "yang belum collect,"), (58.72, "berapa peratus"), (59.48, "yang dah collect."),
 (60.10, "Kat sini, bulan *Julai,*"), (61.34, "*100%* collection."),
 (62.52, "Jom kita tengok"), (63.10, "pada bulan *Ogos.*"), (64.06, "Pada bulan *Ogos,*"), (64.94, "*peningkatan* berlaku."),
 (65.96, "Dan kita tengok kat sini,"), (67.32, "*100%* juga collection."),
 (69.26, "Pada bulan *September,*"), (70.26, "berlaku lagi *peningkatan*"), (71.62, "dengan prestasi"), (72.32, "kutipan yuran *100%.*"),
 (74.00, "Tak ada *overdue* tau."), (75.06, "Dan *Oktober* pula"), (75.70, "macam mana?"), (76.28, "*Oktober* ni baru lagi kan."),
 (77.60, "Untuk bulan *Oktober* ni"), (78.58, "kita tengok hampir *70%*"), (80.22, "kutipan yang telah"), (81.00, "berjaya dikutip."),
 (81.98, "Tinggal lagi *30%* sahaja."),
 (83.44, "Nak saya tunjuk tak?"), (84.60, "Macam mana nak *follow up?*"), (85.82, "Sebab tengah sakit perut ni."),
 (86.92, "Nak membuang jap."), (88.02, "Saya *follow up*"), (88.64, "dalam toilet lah eh."), (89.94, "Sakit ni."),
]
CAP = [(a, (CAPS[i + 1][0] if i + 1 < len(CAPS) else SRC_DUR) - 0.02, s) for i, (a, s) in enumerate(CAPS)]
ZOOM = [(0.00, 1.00), (2.04, 1.12), (5.56, 1.00), (11.26, 1.12), (18.16, 1.00), (25.02, 1.12), (28.94, 1.00), (34.02, 1.12),
        (39.40, 1.00), (43.58, 1.12), (47.22, 1.00), (51.88, 1.12), (53.44, 1.00), (59.48, 1.12), (62.52, 1.00), (65.96, 1.12),
        (69.26, 1.00), (74.00, 1.12), (75.06, 1.00), (81.98, 1.12), (83.44, 1.00), (85.82, 1.12), (88.02, 1.00)]
CLOSE = []
CLOSE_Z = 1.4

# B-roll dari B-ROLL/B-Roll Pantau Yuran.mp4 (rakaman skrin telefon). Maks 3 s setiap sisipan; suara terus berjalan.
# (mula, tamat, frame, [(masa_ring, kotak_ring, label_pil)])
BR = [
 (13.74, 16.74, "dash", [(14.40, (30, 150, 1050, 1000), None)]),                                   # "kita sediakan dashboard"
 (18.16, 21.16, "ovd", [(18.70, (40, 1020, 1050, 1320), None), (20.30, (40, 1020, 1050, 1320), None)]),  # unpaid / overdue -> 43 overdue invoices
 (21.30, 24.30, "ovd", [(21.70, (40, 1715, 1050, 2010), None)]),                                    # "berapa lama dah overdue" -> 4 average days overdue
 (34.40, 37.40, "dash", [(35.10, (40, 690, 1050, 995), "200 pelanggan")]),                          # "ada 200 ... 200 pelanggan"
 (39.40, 42.40, "dash", [(39.70, (40, 1040, 1050, 1340), "1 program"), (41.30, (40, 1740, 1050, 2050), None)]),  # satu program -> view overdue
 (45.40, 48.40, "oct", [(45.70, (110, 395, 770, 545), None)]),                                     # "bulanan collection" -> pilih bulan
 (48.60, 51.60, "jun", [(48.90, (110, 400, 440, 545), None), (49.90, (40, 665, 1050, 1310), None)]),     # Jun: RM 0, 0.00%
 (59.50, 62.50, "jul", [(59.80, (110, 340, 440, 470), None), (60.70, (40, 955, 1050, 1250), "100%")]),  # Julai 100%
 (63.60, 66.60, "aug", [(63.90, (110, 340, 440, 470), None), (64.90, (40, 600, 1050, 905), "Peningkatan")]),  # Ogos peningkatan
 (69.40, 72.40, "sep", [(69.70, (110, 340, 440, 470), None), (70.80, (40, 600, 1050, 905), "Peningkatan")]),  # September peningkatan
 (77.60, 80.60, "oct2", [(77.90, (110, 340, 440, 470), None), (79.50, (40, 955, 1050, 1250), "hampir 70%")]),  # Oktober hampir 70%
]
# angka besar ikut apa disebut (1-2 s)
NUMS = [
 (1.10, 2.30, "*2* minit", None),
 (67.20, 68.95, "*100%*", "juga collection"),
 (72.95, 74.95, "*100%*", "Tak ada overdue"),
 (82.30, 83.40, "*30%*", "tinggal lagi"),
]
CARD_TP = (2.10, 5.50)      # Tak payah tunggu: admin / kerani / siapa-siapa
TP_T = (2.80, 3.84, 5.00)
CARD_DEV = (5.60, 11.20)    # handphone / tablet / komputer / internet
DEV_T = (6.94, 7.64, 8.26, 10.30)
CMT_IN = 83.44
TYPE_A, TYPE_B = 84.00, 84.45
CMT_OUT = 85.80
LABEL_IN, LABEL_OUT = 2.40, 5.40   # label nama selepas angka "2 minit"
THUMB_SRC_T = 25.3
def inwin(t, w): return w[0] <= t < w[1]
BRWIN = [(a, b) for a, b, _, _ in BR]

def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = min(1, max(0, x)); c = 1.6
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def fade_layer(lay, k):
    if k < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    return lay

# ---------- frames sumber (grade ringan, kekal warna kulit) ----------
GRADE = "eq=contrast=1.04:brightness=0.012:saturation=1.04,unsharp=5:5:0.25"
def reader(t0=0):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", SRC, "-vf", GRADE + ",fps=30",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
SW, SH = 1080, 1920
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
        cx, cy = SW / 2, SH * (0.30 + 0.03 * min(1, max(0, z - 1.15) / 0.3))
        x0 = cx - cw / 2; y0 = cy - ch * 0.30
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    return im.resize((W, H), Image.LANCZOS)

# ---------- teks ----------
def text_parts(s):
    return [(p, i % 2 == 1) for i, p in enumerate(s.split("*")) if p]
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
LOWWIN = tuple(BRWIN) + (CARD_TP, CARD_DEV)
def caption(base, t):
    cur = None
    for i, (a, b, s) in enumerate(CAP):
        if a - 0.02 <= t < b + 0.02: cur = (a, s)
    if not cur: return
    a, s = cur; k = ease((t - a) / 0.12)
    y = H * (0.545 if inwin(t, (CMT_IN, CMT_OUT)) else 0.755 if any(inwin(t, w) for w in LOWWIN) else 0.64)
    tw = ImageDraw.Draw(base).textlength(s.replace("*", ""), font=CAP_FONT) + 30 * S
    fit = min(1.0, W * 0.80 / tw)
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
    base.alpha_composite(fade_layer(lay, k), (int(64 * S - (1 - k) * 40 * S), int(H * 0.135)))

# ---------- helper kad ----------
def round_mask(size, rad):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=rad, fill=255); return m
def shadowed(c, r=18, a=130):
    sh = Image.new("RGBA", (c.width + 100, c.height + 100), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((50, 62, c.width + 50, c.height + 62), radius=int(24 * S), fill=(0, 0, 0, a))
    sh = sh.filter(ImageFilter.GaussianBlur(r * S)); sh.alpha_composite(c, (50, 50)); return sh
_bgcache = {}
def bg_of(key, img):
    if key not in _bgcache:
        b = img.resize((int(img.width * H / img.height), H), Image.LANCZOS) if img.width / img.height < W / H else img.resize((int(img.width * H / img.height), H), Image.LANCZOS)
        b = b.crop(((b.width - W) // 2, 0, (b.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40 * S))
        _bgcache[key] = Image.blend(b.convert("RGBA"), Image.new("RGBA", (W, H), "#0D1122"), 0.62)
    return _bgcache[key].copy()

# ---------- B-roll Pantau Yuran: skrin telefon, zoom perlahan ke kad yang disebut + callout ----------
_PS = {k: Image.open(os.path.join(AS, f"pantau_{k}.png")).convert("RGB") for k in ("dash", "ovd", "oct", "jun", "jul", "aug", "sep", "oct2")}
PH_Y1 = 2130            # bawah kandungan skrin (atas bar navigasi)
PH_AR = PH_Y1 / 1080
CARD_H = 0.60           # tinggi kad telefon (nisbah H)
def phone_crop(p, ring):
    e = ease(p)
    x0, y0, x1, y1 = ring
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w = 1080 - (1080 - 860) * e          # zoom masuk hingga ~126%
    h = w * PH_AR
    cx = 540 + (cx - 540) * e; cy = PH_Y1 / 2 + (cy - PH_Y1 / 2) * e
    cx = min(max(cx, w / 2), 1080 - w / 2); cy = min(max(cy, h / 2), PH_Y1 - h / 2)
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
def pantau_broll(t, a, b, key, rings):
    k = ease((t - a) / 0.22) * (1 - ease((t - (b - 0.22)) / 0.22))
    img = _PS[key]
    # ring aktif = yang terakhir sudah bermula
    act = [r for r in rings if t >= r[0]]
    tgt = (act[-1] if act else rings[0])[1]
    p = min(1, (t - a) / 1.2)
    box = phone_crop(p, tgt)
    ch = int(H * CARD_H); cw = int(ch / PH_AR)
    c = img.crop(tuple(int(v) for v in box)).resize((cw, ch), Image.LANCZOS).convert("RGBA")
    sx = cw / (box[2] - box[0])
    def mp(x, y): return ((x - box[0]) * sx, (y - box[1]) * sx)
    for i, (rt, rb, lab) in enumerate(rings):
        if t < rt: continue
        if i + 1 < len(rings) and t >= rings[i + 1][0]: continue   # satu callout pada satu masa
        kr = ease((t - rt) / 0.3)
        (px0, py0), (px1, py1) = mp(rb[0] - 6, rb[1] - 6), mp(rb[2] + 6, rb[3] + 6)
        lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((px0, py0, px1, py1), radius=int(18 * S), outline=ACC, width=max(3, int(7 * S)))
        c.alpha_composite(fade_layer(lay, kr))
    c.putalpha(round_mask(c.size, int(34 * S)))
    bz = int(14 * S)
    body = Image.new("RGBA", (cw + 2 * bz, ch + 2 * bz), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle((0, 0, body.width - 1, body.height - 1), radius=int(46 * S), fill="#14172A")
    body.alpha_composite(c, (bz, bz))
    fr = bg_of("pantau", _PS["dash"])
    sb = shadowed(body)
    bx, by = int(W * 0.46 - sb.width / 2), int(H * 0.385 - sb.height / 2 + (1 - k) * 40 * S)
    fr.alpha_composite(sb, (bx, by))
    # pil label di sebelah kiri callout (ikut apa disebut)
    for i, (rt, rb, lab) in enumerate(rings):
        if lab is None or t < rt + 0.15: continue
        kl = back((t - rt - 0.15) / 0.3)
        (px0, py0), (px1, py1) = mp(rb[0], rb[1]), mp(rb[2], rb[3])
        f = F("xb", 46); d = ImageDraw.Draw(fr)
        tw = d.textlength(lab, font=f); pw, ph = tw + 50 * S, 84 * S
        cx_ = bx + 50 + bz + (px0 + px1) / 2; cy_ = by + 50 + bz + py1 + ph * 0.2
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((cx_ - pw / 2, cy_, cx_ + pw / 2, cy_ + ph), radius=int(ph / 2), fill=BLUE)
        ld.text((cx_, cy_ + ph / 2), lab, font=f, fill=WHITE, anchor="mm")
        fr.alpha_composite(fade_layer(lay, min(1, max(0, kl))))
    return fr, k

def broll(base, t):
    for a, b, key, rings in BR:
        if a <= t < b:
            fr, k = pantau_broll(t, a, b, key, rings)
            # sisipan bersambung (<0.3 s jarak): tiada fade ke muka di antara
            for a2, b2, _, _ in BR:
                if abs(a2 - b) < 0.3 and t > b - 0.22: k = 1
                if abs(b2 - a) < 0.3 and t < a + 0.22: k = 1
            return Image.blend(base, fr, k)
    return base

# ---------- kad grafik (putih, di dada; muka tidak ditutup) ----------
def card_base(t, win, h, wf=0.76):
    k = back((t - win[0]) / 0.35) if t < win[0] + 0.35 else 1
    ko = 1 - ease((t - (win[1] - 0.25)) / 0.25)
    cw = int(W * wf); ch = int(h)
    lay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(30 * S), fill=(255, 255, 255, 246))
    return lay, d, k, ko
def put_card(base, lay, k, ko, cy):
    sh = shadowed(lay, 16, 90)
    sc = max(0.01, 0.9 + 0.1 * min(k, 1.05))
    sh = sh.resize((max(1, int(sh.width * sc)), max(1, int(sh.height * sc))), Image.LANCZOS)
    base.alpha_composite(fade_layer(sh, min(1, k) * ko), (int(W * 0.47 - sh.width / 2), int(H * cy - sh.height / 2)))
def mark(d, cx, cy, r, ok, col=None):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col or (ACC if ok else RED))
    w = max(2, int(5 * S))
    if ok: d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)], fill=WHITE, width=w, joint="curve")
    else:
        d.line((cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38), fill=WHITE, width=w)
        d.line((cx - r * 0.38, cy + r * 0.38, cx + r * 0.38, cy - r * 0.38), fill=WHITE, width=w)
def ic_phone(d, cx, cy, r, col):
    d.rounded_rectangle((cx - r * 0.55, cy - r, cx + r * 0.55, cy + r), radius=int(r * 0.25), outline=col, width=max(2, int(5 * S)))
    d.line((cx - r * 0.18, cy + r * 0.72, cx + r * 0.18, cy + r * 0.72), fill=col, width=max(2, int(4 * S)))
def ic_mail(d, cx, cy, r, col):
    d.rounded_rectangle((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), radius=int(r * 0.15), outline=col, width=max(2, int(5 * S)))
    d.line([(cx - r, cy - r * 0.6), (cx, cy + r * 0.1), (cx + r, cy - r * 0.6)], fill=col, width=max(2, int(5 * S)), joint="curve")
def ic_chat(d, cx, cy, r, col, fill=False):
    w = max(2, int(5 * S))
    if fill:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.polygon([(cx - r * 0.75, cy + r * 0.5), (cx - r * 1.0, cy + r * 1.05), (cx - r * 0.25, cy + r * 0.88)], fill=col)
    else:
        d.rounded_rectangle((cx - r, cy - r * 0.75, cx + r, cy + r * 0.55), radius=int(r * 0.35), outline=col, width=w)
        d.polygon([(cx - r * 0.5, cy + r * 0.5), (cx - r * 0.6, cy + r * 0.95), (cx - r * 0.1, cy + r * 0.5)], fill=col)
def ic_wa(d, cx, cy, r):
    ic_chat(d, cx, cy, r, WAG, True)
    # gagang telefon ringkas (putih)
    d.arc((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), 100, 260, fill=WHITE, width=max(2, int(6 * S)))
def pill(lay, x0, y0, txt, f, fg, bg, k, icon=None):
    pl = Image.new("RGBA", lay.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    tw = pd.textlength(txt, font=f); ih = int(f.size * 1.75)
    iw = int(ih * 0.9) if icon else 0
    pw = int(tw + iw + 46 * S)
    pd.rounded_rectangle((x0, y0, x0 + pw, y0 + ih), radius=ih // 2, fill=bg)
    if icon: icon(pd, x0 + int(22 * S) + iw // 2, y0 + ih // 2, ih * 0.27)
    pd.text((x0 + int(23 * S) + iw, y0 + ih // 2), txt, font=f, fill=fg, anchor="lm")
    lay.alpha_composite(fade_layer(pl, k))
    return pw

def ic_x(d, cx, cy, r): mark(d, cx, cy, r, False)
def ic_monitor(d, cx, cy, r, col):
    d.rounded_rectangle((cx - r, cy - r * 0.7, cx + r, cy + r * 0.45), radius=int(r * 0.15), outline=col, width=max(2, int(5 * S)))
    d.line((cx - r * 0.4, cy + r * 0.8, cx + r * 0.4, cy + r * 0.8), fill=col, width=max(2, int(5 * S)))
def ic_tablet(d, cx, cy, r, col):
    d.rounded_rectangle((cx - r * 0.8, cy - r, cx + r * 0.8, cy + r), radius=int(r * 0.2), outline=col, width=max(2, int(5 * S)))
def card_tp(base, t):
    if not inwin(t, CARD_TP): return
    ch = H * 0.15
    lay, d, k, ko = card_base(t, CARD_TP, ch, 0.80); cw = lay.width
    d.text((cw // 2, ch * 0.27), "Tak payah tunggu", font=F("xb", 50), fill=BLUE, anchor="mm")
    f = F("b", 40); x = int(26 * S)
    for tt, lab in zip(TP_T, ("Admin", "Kerani", "Siapa-siapa")):
        if t < tt: break
        w = pill(lay, x, int(ch * 0.53), lab, f, RED, "#FBE3E7", ease((t - tt) / 0.25), lambda d_, cx, cy, r: ic_x(d_, cx, cy, r * 0.9))
        x += w + int(14 * S)
    put_card(base, lay, k, ko, 0.595)
def card_dev(base, t):
    if not inwin(t, CARD_DEV): return
    ch = H * 0.17
    lay, d, k, ko = card_base(t, CARD_DEV, ch, 0.80); cw = lay.width
    d.text((cw // 2, ch * 0.20), "Check sendiri guna", font=F("xb", 48), fill=BLUE, anchor="mm")
    f = F("b", 38); x = int(24 * S)
    icons = (lambda d_, cx, cy, r: ic_phone(d_, cx, cy, r, BLUE), lambda d_, cx, cy, r: ic_tablet(d_, cx, cy, r, BLUE),
             lambda d_, cx, cy, r: ic_monitor(d_, cx, cy, r, BLUE))
    for tt, lab, ic in zip(DEV_T[:3], ("Handphone", "Tablet", "Komputer"), icons):
        if t < tt: break
        w = pill(lay, x, int(ch * 0.36), lab, f, BLUE, "#D8F0FB", ease((t - tt) / 0.25), ic)
        x += w + int(12 * S)
    if t >= DEV_T[3]:
        ka = ease((t - DEV_T[3]) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        yy = ch * 0.82
        mark(d2, int(56 * S), yy, int(24 * S), True)
        d2.text((int(96 * S), yy), "Apa sahaja device + internet", font=F("b", 40), fill=BLACK, anchor="lm")
        lay.alpha_composite(fade_layer(l2, ka))
    put_card(base, lay, k, ko, 0.595)
def nums(base, t):
    for a, b, txt, sub in NUMS:
        if not (a <= t < b): continue
        k = back((t - a) / 0.3) * (1 - ease((t - (b - 0.2)) / 0.2))
        draw_rich(base, CX, H * 0.46, txt, F("xb", 210), sc=max(0.01, k), stroke=10)
        if sub: draw_rich(base, CX, H * 0.545, sub, F("xb", 64), sc=max(0.01, k), stroke=7)

# ---------- motion komen: "Nak saya tunjuk tak?" ----------
def comments(base, t):
    if not inwin(t, (CMT_IN, CMT_OUT)): return
    k = ease((t - CMT_IN) / 0.35) * (1 - ease((t - (CMT_OUT - 0.25)) / 0.25))
    pw, ph = int(W * 0.78), int(H * 0.21)
    x0 = int(W * 0.46 - pw / 2); y0 = int(H * 0.585 + (1 - k) * H * 0.12)
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = int(34 * S)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=r, fill=(255, 255, 255, 245))
    fh, fn = F("b", 34), F("m", 36)
    d.text((pw // 2, int(44 * S)), "Komen", font=fh, fill=BLACK, anchor="mm")
    d.line((int(30 * S), int(84 * S), pw - int(30 * S), int(84 * S)), fill=GREY, width=max(1, int(2 * S)))
    d.text((pw // 2, int(150 * S)), "Nak tengok cara follow up?", font=F("sb", 30), fill="#7A7C80", anchor="mm")
    by = ph - int(96 * S); bh = int(70 * S)
    d.rounded_rectangle((int(30 * S), by, pw - int(120 * S), by + bh), radius=bh // 2, fill=GREY)
    msg = "Nak"
    n = int(len(msg) * min(1, max(0, (t - TYPE_A) / (TYPE_B - TYPE_A))))
    typed = msg[:n]
    d.text((int(60 * S), by + bh // 2), typed, font=fn, fill=BLACK, anchor="lm")
    cxp = int(60 * S) + d.textlength(typed, font=fn) + int(4 * S)
    if int(t * 4) % 2 == 0:
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
    base.alpha_composite(fade_layer(sh, min(1, k * 1.5)), (x0 - 40, y0 - 40))

# ---------- thumbnail ----------
def thumbnail():
    fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(THUMB_SRC_T), "-i", SRC, "-vf", GRADE, "-frames:v", "1",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = place(np.frombuffer(fr, np.uint8).reshape(SH, SW, 3), 1.08).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(int(H * 0.40), H):
        gd.line((0, y, W, y), fill=(20, 24, 50, int(170 * min(1, (y - H * 0.40) / (H * 0.25)))))
    im.alpha_composite(g)
    draw_rich(im, CX, H * 0.505, "*Pantau* yuran", F("xb", 118), stroke=9)
    draw_rich(im, CX, H * 0.585, "dalam", F("xb", 104), stroke=9)
    d = ImageDraw.Draw(im); fk = F("xb", 136)
    tw = d.textlength("2 MINIT", font=fk); bw, bh = int(tw + 70 * S), int(176 * S)
    bx, by = int(CX - bw / 2), int(H * 0.675 - bh / 2)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(26 * S), fill=ACC)
    d.text((CX, H * 0.675), "2 MINIT", font=fk, fill=WHITE, anchor="mm")
    # potongan sebenar dashboard telefon (kutipan September 100%)
    src = _PS["sep"].crop((20, 580, 1060, 1270))
    c = src.resize((int(460 * S), int(460 * S * src.height / src.width)), Image.LANCZOS).convert("RGBA")
    c.putalpha(round_mask(c.size, int(20 * S)))
    frm = Image.new("RGBA", (c.width + int(16 * S), c.height + int(16 * S)), (0, 0, 0, 0))
    ImageDraw.Draw(frm).rounded_rectangle((0, 0, frm.width - 1, frm.height - 1), radius=int(26 * S), fill=WHITE)
    frm.alpha_composite(c, (int(8 * S), int(8 * S)))
    rot = shadowed(frm, 14, 120).rotate(-4, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(rot, (int(W * 0.27 - rot.width / 2), int(H * 0.135 - rot.height / 2)))
    return im

# ---------- end card: TOFU follow TikTok (gaya YM-F-004/005 yang diluluskan) ----------
_l = Image.open(os.path.join(AS, "logo_white.png")).convert("RGBA")
_av = Image.open(os.path.join(AS, "tiktok.jpg")).convert("RGBA").crop((37, 22, 202, 187))
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
    done = t >= TAP + 0.08
    pr = 1 - 0.12 * math.sin(min(1, max(0, (t - TAP) / 0.16)) * math.pi)
    pulse = 1 + 0.05 * math.sin(max(0, t - 0.35) * 2 * math.pi * 2.2) if t < TAP else 1
    bw, bh = 300 * S * pr * pulse, 74 * S * pr * pulse; bx = tx + 150 * S; by = cy0 + ch * 0.74
    lab = "Following ✓" if done else "+ Follow"
    od.rounded_rectangle((bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), radius=int(14 * S), fill="#E7E8E9" if done else "#FE2C55")
    od.text((bx, by), lab, font=F("b", 34), fill=BLACK if done else WHITE, anchor="mm")
    if TAP <= t < TAP + 0.45:
        r = (t - TAP) / 0.45; rr = 30 * S + 60 * S * r
        od.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=(41, 171, 226, int(200 * (1 - r))), width=max(2, int(6 * S)))
    od.text((x, H * 0.60), "Follow TikTok Yuran.my", font=F("xb", 54), fill=WHITE, anchor="mm")
    od.text((x, H * 0.645), "untuk tips urus yuran sekolah", font=F("sb", 42), fill=GREY, anchor="mm")
    im.alpha_composite(fade_layer(ov, k2))
    return im

# ---------- render video ----------
def render(only=None):
    thumb = thumbnail()
    thumb.convert("RGB").save(os.path.join(OUT, f"{ID}_THUMB.png"))
    if only is not None:   # semakan frame: senarai masa timeline
        rd = None
        for T in only:
            if T < THUMB: im = thumb
            elif T < BODY_END:
                t = T - OFF
                fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", SRC, "-vf", GRADE, "-frames:v", "1",
                                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
                im = place(np.frombuffer(fr, np.uint8).reshape(SH, SW, 3), zoom_at(t)).convert("RGBA")
                im = compose(im, t)
            else: im = endcard(T - BODY_END)
            im.convert("RGB").save(os.path.join(OUT, f"chk_{T:06.2f}.jpg"), quality=85)
        return None
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
            im = compose(place(last, zoom_at(t)).convert("RGBA"), t)
            fade = ease((T - (BODY_END - 0.15)) / 0.15) if T > BODY_END - 0.15 else 0
            if fade: im = Image.blend(im, Image.new("RGBA", (W, H), BLUE), fade)
        else:
            im = endcard(T - BODY_END)
        enc.stdin.write(im.convert("RGB").tobytes())
        if i % 150 == 0: print(f"frame {i}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); rd.kill()
    return tmpv
def compose(im, t):
    im = broll(im, t)
    label(im, t); card_tp(im, t); card_dev(im, t); nums(im, t)
    comments(im, t); caption(im, t)
    return im

# ---------- audio ----------
SFXL = [(OFF - 0.12, "whoosh.wav", -24)]
for a, b, key, rings in BR:
    if not any(abs(b2 - a) < 0.3 for _, b2, _, _ in BR): SFXL.append((OFF + a - 0.05, "whoosh.wav", -22))
    for rt, rb, lab in rings: SFXL.append((OFF + rt, "pop.wav", -24 if lab is None else -21))
for a, b, txt, sub in NUMS: SFXL.append((OFF + a, "pop.wav", -19))
SFXL += [(OFF + CARD_TP[0], "pop.wav", -20)] + [(OFF + x, "pop.wav", -23) for x in TP_T]
SFXL += [(OFF + CARD_DEV[0], "pop.wav", -20)] + [(OFF + x, "pop.wav", -23) for x in DEV_T[:3]] + [(OFF + DEV_T[3], "ding.wav", -25)]
SFXL += [(OFF + CMT_IN, "whoosh.wav", -24), (OFF + TYPE_A + 0.05, "tick.wav", -27), (OFF + TYPE_A + 0.25, "tick.wav", -27), (OFF + TYPE_B + 0.05, "tick.wav", -27)]
SFXL += [(BODY_END + 0.05, "ding.wav", -24), (BODY_END + TAP, "click.wav", -18)]
SFXL.sort()

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
    # muzik berlesen: Mixkit "Dreaming Big" (Ahjay Stelino), Mixkit Stock Music Free License (MUSIC/ kosong)
    bed = os.path.join(OUT, "_mus.wav")
    fc = (f"[0]atrim=duration={TOTAL + 0.2:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-32:TP=-6,"
          f"afade=t=in:d=0.6,afade=t=out:st={TOTAL - 0.8:.3f}:d=0.8,"
          f"volume='if(lt(t,{THUMB})+gt(t,{BODY_END}),2.5,1)':eval=frame,apad,atrim=duration={TOTAL:.3f}[mb];"
          f"[1]aresample=48000[vk];[mb][vk]sidechaincompress=threshold=0.04:ratio=3:attack=30:release=350[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MUS, "31.mp3"), "-i", vo,
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
    if os.environ.get("YM_CHECK"):
        render([float(x) for x in os.environ["YM_CHECK"].split(",")]); print("check OK"); sys.exit()
    v = render(); a = audio()
    dst = os.path.join(OUT, f"{ID}_{TAG}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", dst], check=True)
    os.remove(v)
    print("OK", dst)
