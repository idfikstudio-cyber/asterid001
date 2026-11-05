# Render Yuran.my YM-F-006 (TOFU "Boleh hantar reminder yuran ke").
# usage: python3 ym_f006_render.py <src.mp4> <assetdir> <sfxdir> <musicdir> <outdir> <W> [crf]
# assetdir: scr_dashboard.png scr_invois.png scr_overdue.png apps_unpaid.mp4 logo_white.png tiktok.jpg
# W=540 -> preview 540x960, W=1080 -> final 1080x1920.
import json, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, AS, SFX, MUS, OUT = sys.argv[1:6]
W = int(sys.argv[6]); H = W * 16 // 9; CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
S = W / 1080
FPS = 30
ID = "YM-F-006_Boleh_hantar_reminder_yuran_ke"
TAG = "PREVIEW" if W < 1080 else "FINAL"
os.makedirs(OUT, exist_ok=True)

BLUE, ACC, BLACK, GREY, WHITE = "#2A3B8F", "#29ABE2", "#231F20", "#E7E8E9", "#FFFFFF"
RED = "#C8435A"
WAG = "#25D366"   # hijau butang WhatsApp dalam sistem (warna UI, bukan aset brand lain)
FD = "/usr/share/fonts/opentype/inter/"
def F(w, px): return ImageFont.truetype(FD + {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], max(8, int(px * S)))

SRC_DUR = 74.63
THUMB = 1.0
OFF = THUMB
END = 1.5
BODY_END = OFF + SRC_DUR
TOTAL = BODY_END + END
NF = int(round(TOTAL * FPS))

# ---------- caption (masa video asal, ikut percakapan; ejaan istilah ikut DNA) ----------
CAPS = [
 (0.00, "Boleh hantar"), (0.60, "*reminder* bayaran ke"), (1.58, "guna Yuran.my ni?"), (2.86, "Boleh je."),
 (3.68, "Dalam sistem Yuran.my ni,"), (5.04, "kita dah siapkan"), (5.78, "beberapa cara"), (6.56, "untuk *follow up* bayaran."),
 (8.16, "Sebenarnya bila kita"), (8.92, "dah generate *invois* ni,"), (10.30, "*invois* tu dah terpapar"), (11.76, "dalam *apps*"), (12.32, "yang kita sediakan."),
 (13.44, "Sebab memang"), (14.08, "dalam Yuran.my ni"), (15.24, "kita sediakan *apps.*"),
 (16.38, "Kalau tak nak"), (16.88, "dalam *apps,*"), (17.64, "kita hantar dekat *email.*"),
 (19.04, "Jadi kedua-duanya"), (19.96, "pelanggan akan dapat"), (20.82, "secara *automatik.*"),
 (21.98, "Tinggal dia nak bayar"), (23.10, "tak bayar je."),
 (23.86, "Tapi kalau pelanggan kita"), (25.00, "tak buka *apps*"), (25.94, "ataupun tak buka *email,*"), (27.72, "macam mana?"),
 (28.14, "Kita boleh hantar"), (29.04, "*reminder* bayaran"), (29.80, "menggunakan *WhatsApp*"), (30.88, "ataupun *SMS.*"),
 (32.08, "Kalau hantar *reminder*"), (32.82, "dalam *lima* orang"), (33.82, "ke apa,"), (34.36, "kita sediakan"), (35.04, "*button WhatsApp* je."),
 (36.24, "Tekan je"), (36.58, "*button WhatsApp* tu,"), (37.46, "kita akan hantar"), (38.52, "*WhatsApp reminder*"), (39.32, "pembayaran"), (40.10, "kepada pelanggan kita."),
 (41.34, "Yang ni *free* je."),
 (42.34, "Tapi kalau nak hantar"), (43.48, "WhatsApp ataupun SMS"), (44.68, "secara *pukal,*"), (45.82, "yang ni ada"), (46.38, "bayaran *kredit*"),
 (47.24, "yang kita kena *top up*"), (48.30, "dalam sistem"), (48.92, "yang kita sediakan."),
 (49.88, "Sebab WhatsApp kita ni"), (51.06, "adalah WhatsApp"), (51.70, "yang *berdaftar*"), (52.50, "secara *official.*"),
 (53.38, "*WhatsApp rasmi* ni"), (54.38, "kena bayar."), (55.14, "Bukan kita yang ambil,"), (56.52, "*WhatsApp* yang ambil."),
 (57.58, "Kalau kita blast"), (58.40, "pada pelanggan kita"), (59.14, "gunakan WhatsApp"), (59.94, "yang *tak rasmi,*"),
 (60.82, "possible WhatsApp kita tu"), (62.72, "kena *ban* pun ada."),
 (63.84, "Tak caya?"), (64.42, "Cuba chat."), (65.14, "Kami tak tipu."),
 (65.96, "Nak tak saya tunjukkan"), (66.92, "cara on *WhatsApp*"), (67.84, "secara *pukal* ni"), (69.00, "dalam sistem kita?"),
 (70.22, "*Comment nak,*"), (70.70, "nanti saya akan tunjukkan"), (71.70, "cara on *WhatsApp official*"), (72.90, "dalam *apps* kita."),
]
CAP = [(a, (CAPS[i + 1][0] if i + 1 < len(CAPS) else SRC_DUR) - 0.02, s) for i, (a, s) in enumerate(CAPS)]
# punch-in ikut ayat (footage sudah ditrim; tiada potongan isi)
ZOOM = [(0.00, 1.00), (2.86, 1.12), (3.68, 1.00), (8.16, 1.12), (13.44, 1.00), (16.38, 1.12), (19.04, 1.00), (21.98, 1.12),
        (23.86, 1.00), (28.14, 1.12), (32.08, 1.00), (37.46, 1.12), (42.34, 1.00), (49.88, 1.12), (53.38, 1.00), (57.58, 1.12),
        (63.84, 1.00), (65.96, 1.12), (70.22, 1.00)]
CLOSE = [(62.70, 63.75)]   # close-up muka pada "kena ban pun ada"
CLOSE_Z = 1.45

# B-roll sistem (maks 3 s setiap sisipan; suara terus berjalan). Data demo: tidak diblur (arahan Farhan).
BR_DASH = (4.00, 7.00)    # "beberapa cara untuk follow up bayaran" -> dashboard, callout Overdue Invoice Alerts
BR_INV = (8.40, 10.30)    # "generate invois ni" -> skrin Invoice, callout Auto Generate Billing
BR_APP = (10.30, 13.30)   # "invois tu dah terpapar dalam apps" -> Apps Yuran.my: Unpaid Invoices
BR_OVD = (24.30, 27.30)   # "tak buka apps ataupun tak buka email" -> senarai invois overdue
BR_WA = (34.55, 37.55)    # "button WhatsApp je. Tekan je button WhatsApp tu" -> butang WhatsApp hijau
WA_RING, WA_TAP = 35.30, 36.86
CARD_CH = (13.44, 23.80)  # apps + email -> automatik
CH_A, CH_E, CH_AUTO = 15.82, 18.50, 21.30
CARD_WA = (28.40, 32.90)  # WhatsApp / SMS
WA_A, WA_S = 30.40, 31.50
NUM = (33.20, 34.50)      # "lima orang" -> 5 orang
CARD_COST = (37.70, 49.75)
COST_FREE, COST_R2, COST_KR = 41.70, 43.10, 46.85
CARD_OFF = (49.90, 57.50)
OFF_R1, OFF_R2, OFF_R3 = 51.90, 54.38, 56.50
CARD_BAN = (59.40, 63.80)
BAN_B = 62.90
CMT_IN = 65.96
TYPE_A, TYPE_B = 70.22, 70.62
LABEL_IN, LABEL_OUT = 0.25, 3.60
THUMB_SRC_T = 3.0
def inwin(t, w): return w[0] <= t < w[1]

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
LOWWIN = (BR_DASH, BR_INV, BR_APP, BR_OVD, BR_WA, CARD_CH, CARD_WA, CARD_COST, CARD_OFF, CARD_BAN)
def caption(base, t):
    cur = None
    for i, (a, b, s) in enumerate(CAP):
        if a - 0.02 <= t < b + 0.02: cur = (a, s)
    if not cur: return
    a, s = cur; k = ease((t - a) / 0.12)
    y = H * (0.545 if t >= CMT_IN else 0.755 if any(inwin(t, w) for w in LOWWIN) else 0.64)
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

# ---------- B-roll skrin sistem: zoom perlahan ke bahagian yang diterangkan + callout ----------
_SCR = {k: Image.open(os.path.join(AS, f)).convert("RGB") for k, f in
        (("dash", "scr_dashboard.png"), ("inv", "scr_invois.png"), ("ovd", "scr_overdue.png"))}
CARD_W, CARD_AR = 0.92, 0.80   # kad skrin: lebar 92% frame, nisbah tinggi/lebar
# (cx, cy, lebar) kotak potongan dalam piksel rakaman 1920x1032: mula -> akhir
SHOTS = {
    "dash": ((960, 516, 1290), (800, 470, 1060)),     # zoom ke "Overdue Invoice Alerts"
    "inv": ((960, 516, 1290), (760, 420, 1000)),      # zoom ke butang New Invoice / Auto Generate Billing
    "ovd": ((960, 516, 1290), (1300, 640, 1100)),     # senarai invois OVERDUE
    "wa": ((960, 516, 1290), (1700, 600, 560)),       # zoom ke lajur Action, butang WhatsApp hijau
}
RINGS = {"dash": (294, 405, 620, 475), "inv": (433, 292, 596, 323), "ovd": (1650, 445, 1730, 960)}
def crop_at(key, p):
    (ax, ay, aw), (bx, by, bw) = SHOTS[key]
    e = ease(p)
    cx, cy, cw = ax + (bx - ax) * e, ay + (by - ay) * e, aw + (bw - aw) * e
    ch = cw * CARD_AR
    cx = min(max(cx, cw / 2), 1920 - cw / 2); cy = min(max(cy, ch / 2), 1032 - ch / 2)
    return (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
def screen_card(key, t, win, extra=None):
    a, b = win
    k = ease((t - a) / 0.22) * (1 - ease((t - (b - 0.22)) / 0.22))
    p = min(1, (t - a) / 1.3)            # zoom masuk dalam 1.3 s, kemudian kekal
    img = _SCR["inv" if key == "wa" else key]
    box = crop_at(key, p)
    cw = int(W * CARD_W); ch = int(cw * CARD_AR)
    c = img.crop(tuple(int(v) for v in box)).resize((cw, ch), Image.LANCZOS).convert("RGBA")
    sx = cw / (box[2] - box[0])
    def mp(x, y): return ((x - box[0]) * sx, (y - box[1]) * sx)
    d = ImageDraw.Draw(c)
    if key in RINGS and t >= a + 1.0:
        kr = ease((t - a - 1.0) / 0.3)
        x0, y0, x1, y1 = RINGS[key]
        (px0, py0), (px1, py1) = mp(x0 - 8, y0 - 8), mp(x1 + 8, y1 + 8)
        lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((px0, py0, px1, py1), radius=int(14 * S), outline=ACC, width=max(3, int(7 * S)))
        c.alpha_composite(fade_layer(lay, kr))
    if extra: extra(c, d, mp, t)
    c.putalpha(round_mask(c.size, int(26 * S)))
    fr = bg_of(key, img)
    sc = shadowed(c)
    fr.alpha_composite(sc, (int(W * 0.47 - sc.width / 2), int(H * 0.40 - sc.height / 2 + (1 - k) * 40 * S)))
    return fr, k

WA_BTN = (1844, 551)       # butang WhatsApp baris ke-2 (UNPAID) dalam scr_invois
def wa_extra(c, d, mp, t):
    bx, by = mp(*WA_BTN)
    r0 = 34 * (c.width / 560)  # jejari kira-kira butang pada skala akhir
    if t >= WA_RING:
        kr = ease((t - WA_RING) / 0.3)
        pulse = 1 + 0.08 * math.sin((t - WA_RING) * 2 * math.pi * 1.6)
        rr = r0 * 1.15 * pulse
        lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=ACC, width=max(3, int(8 * S)))
        # label kecil "Button WhatsApp" di kiri butang
        f = F("xb", 40); txt = "Button WhatsApp"
        tw = ld.textlength(txt, font=f); pw, ph = tw + 44 * S, 70 * S
        lx1 = bx - rr - 22 * S; lx0 = lx1 - pw; ly0 = by - ph / 2
        ld.rounded_rectangle((lx0, ly0, lx1, ly0 + ph), radius=int(ph / 2), fill=BLUE)
        ld.text(((lx0 + lx1) / 2, by), txt, font=f, fill=WHITE, anchor="mm")
        c.alpha_composite(fade_layer(lay, kr))
    # kursor bergerak ke butang dan tekan
    m0 = WA_TAP - 0.9
    if t >= m0:
        q = ease((t - m0) / 0.75)
        sx_, sy_ = bx - 220 * S, by + 260 * S
        px, py = sx_ + (bx + 6 * S - sx_) * q, sy_ + (by + 8 * S - sy_) * q
        press = 0.85 if WA_TAP <= t < WA_TAP + 0.15 else 1.0
        u = 46 * S * press
        pts = [(0, 0), (0, 1.0), (0.27, 0.76), (0.45, 1.13), (0.6, 1.06), (0.42, 0.7), (0.75, 0.7)]
        poly = [(px + x * u, py + y * u) for x, y in pts]
        d.polygon(poly, fill=WHITE, outline=BLACK, width=max(2, int(3 * S)))
        if WA_TAP <= t < WA_TAP + 0.5:
            r = (t - WA_TAP) / 0.5; rr = 20 * S + 70 * S * r
            lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=(37, 211, 102, int(230 * (1 - r))), width=max(3, int(7 * S)))
            c.alpha_composite(lay)

# Apps Yuran.my (rakaman telefon): klip "Unpaid Invoices"
_APPF = None
def app_frames():
    global _APPF
    if _APPF is None:
        aw = int(W * 0.50); ah = int(aw * 1280 / 592)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(AS, "apps_unpaid.mp4"), "-vf", f"fps=30,scale={aw}:{ah}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(raw) // (aw * ah * 3)
        _APPF = [Image.frombuffer("RGB", (aw, ah), raw[i * aw * ah * 3:(i + 1) * aw * ah * 3]) for i in range(n)]
    return _APPF
def app_broll(t):
    a, b = BR_APP
    k = ease((t - a) / 0.22) * (1 - ease((t - (b - 0.22)) / 0.22))
    fr_ = app_frames(); i = min(len(fr_) - 1, int((t - a) * 30) + 3)
    ph = fr_[i].convert("RGBA")
    # bingkai telefon ringkas
    bz = int(16 * S)
    body = Image.new("RGBA", (ph.width + 2 * bz, ph.height + 2 * bz), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle((0, 0, body.width - 1, body.height - 1), radius=int(56 * S), fill="#14172A")
    ph.putalpha(round_mask(ph.size, int(42 * S))); body.alpha_composite(ph, (bz, bz))
    sc = 1.0 + 0.03 * (t - a) / (b - a)
    body = body.resize((int(body.width * sc), int(body.height * sc)), Image.LANCZOS)
    fr = bg_of("app", Image.open(os.path.join(AS, "scr_invois.png")).convert("RGB"))
    s2 = shadowed(body)
    fr.alpha_composite(s2, (int(W * 0.47 - s2.width / 2), int(H * 0.40 - s2.height / 2 + (1 - k) * 40 * S)))
    return fr, k

def broll(base, t):
    if inwin(t, BR_DASH): fr, k = screen_card("dash", t, BR_DASH)
    elif inwin(t, BR_INV): fr, k = screen_card("inv", t, BR_INV)
    elif inwin(t, BR_APP): fr, k = app_broll(t)
    elif inwin(t, BR_OVD): fr, k = screen_card("ovd", t, BR_OVD)
    elif inwin(t, BR_WA): fr, k = screen_card("wa", t, BR_WA, wa_extra)
    else: return base
    # B-roll bersambung (invois -> apps): tiada fade ke muka di antara
    if inwin(t, BR_INV) and t > BR_INV[1] - 0.22: k = 1
    if inwin(t, BR_APP) and t < BR_APP[0] + 0.22: k = 1
    return Image.blend(base, fr, k)

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

def card_ch(base, t):
    if not inwin(t, CARD_CH): return
    ch = H * 0.15
    lay, d, k, ko = card_base(t, CARD_CH, ch); cw = lay.width
    f = F("b", 44)
    y0 = int(ch * 0.12)
    if t >= CH_A: pill(lay, int(36 * S), y0, "Apps", f, BLUE, "#D8F0FB", ease((t - CH_A) / 0.25), lambda d_, x, y, r: ic_phone(d_, x, y, r, BLUE))
    if t >= CH_E: pill(lay, int(cw * 0.50), y0, "Email", f, BLUE, "#D8F0FB", ease((t - CH_E) / 0.25), lambda d_, x, y, r: ic_mail(d_, x, y, r, BLUE))
    if t >= CH_AUTO:
        ka = ease((t - CH_AUTO) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        yy = ch * 0.74
        mark(d2, int(70 * S), yy, int(28 * S), True)
        fb = F("xb", 50)
        d2.text((int(116 * S), yy), "Pelanggan dapat ", font=F("b", 44), fill=BLACK, anchor="lm")
        d2.text((int(116 * S) + d2.textlength("Pelanggan dapat ", font=F("b", 44)), yy), "automatik", font=fb, fill=ACC, anchor="lm")
        lay.alpha_composite(fade_layer(l2, ka))
    elif t < CH_A:
        d.text((cw // 2, ch * 0.5), "Invois dihantar ke…", font=F("sb", 40), fill="#7A7C80", anchor="mm")
    put_card(base, lay, k, ko, 0.595)

def card_wa(base, t):
    if not inwin(t, CARD_WA): return
    ch = H * 0.15
    lay, d, k, ko = card_base(t, CARD_WA, ch); cw = lay.width
    d.text((cw // 2, ch * 0.27), "Reminder bayaran", font=F("xb", 50), fill=BLUE, anchor="mm")
    f = F("b", 44)
    if t >= WA_A: pill(lay, int(cw * 0.08), int(ch * 0.52), "WhatsApp", f, WHITE, WAG, ease((t - WA_A) / 0.25), lambda d_, x, y, r: ic_chat(d_, x, y, r, WHITE))
    if t >= WA_S: pill(lay, int(cw * 0.60), int(ch * 0.52), "SMS", f, BLUE, "#D8F0FB", ease((t - WA_S) / 0.25), lambda d_, x, y, r: ic_chat(d_, x, y, r, BLUE))
    put_card(base, lay, k, ko, 0.595)

def num(base, t):
    if not inwin(t, NUM): return
    k = back((t - NUM[0]) / 0.3) * (1 - ease((t - (NUM[1] - 0.2)) / 0.2))
    f = F("xb", 210)
    draw_rich(base, CX, H * 0.47, "*5* orang", f, sc=max(0.01, k), stroke=10)

def card_cost(base, t):
    if not inwin(t, CARD_COST): return
    ch = H * 0.19
    lay, d, k, ko = card_base(t, CARD_COST, ch, 0.84); cw = lay.width
    f = F("b", 40); fp = F("xb", 36)
    rows = [(0.27, "Button WhatsApp", CARD_COST[0], COST_FREE, "FREE", "#1F9D57"),
            (0.73, "WhatsApp/SMS pukal", COST_R2, COST_KR, "Kredit top up", BLUE)]
    for yy, txt, t0, t1, pt, pc in rows:
        if t < t0: continue
        kr = ease((t - t0) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        y = ch * yy
        ic_wa(d2, int(64 * S), y, int(30 * S))
        d2.text((int(112 * S), y), txt, font=f, fill=BLACK, anchor="lm")
        lay.alpha_composite(fade_layer(l2, kr))
        if t >= t1:
            kp = back((t - t1) / 0.3)
            l3 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d3 = ImageDraw.Draw(l3)
            tw = d3.textlength(pt, font=fp); pw, ph = tw + 40 * S, 70 * S
            x1 = cw - 30 * S; x0 = x1 - pw
            d3.rounded_rectangle((x0, y - ph / 2, x1, y + ph / 2), radius=int(ph / 2), fill=pc)
            d3.text(((x0 + x1) / 2, y), pt, font=fp, fill=WHITE, anchor="mm")
            lay.alpha_composite(fade_layer(l3, min(1, kp)))
    d.line((int(36 * S), ch * 0.5, cw - int(36 * S), ch * 0.5), fill=GREY, width=max(1, int(3 * S)))
    put_card(base, lay, k, ko, 0.58)

def shield(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r * 0.85, cy - r * 0.6), (cx + r * 0.75, cy + r * 0.25), (cx, cy + r), (cx - r * 0.75, cy + r * 0.25), (cx - r * 0.85, cy - r * 0.6)], fill=fill)
    w = max(2, int(4 * S))
    d.line([(cx - r * 0.35, cy), (cx - r * 0.05, cy + r * 0.3), (cx + r * 0.4, cy - r * 0.3)], fill=WHITE, width=w, joint="curve")
def card_off(base, t):
    if not inwin(t, CARD_OFF): return
    ch = H * 0.20
    lay, d, k, ko = card_base(t, CARD_OFF, ch); cw = lay.width
    shield(d, int(66 * S), ch * 0.17, int(32 * S), WAG)
    fb = F("xb", 50)
    d.text((int(116 * S), ch * 0.17), "WhatsApp ", font=fb, fill=BLACK, anchor="lm")
    d.text((int(116 * S) + d.textlength("WhatsApp ", font=fb), ch * 0.17), "official", font=fb, fill=ACC, anchor="lm")
    f = F("b", 40)
    for yy, t0, txt, ok in ((0.43, OFF_R1, "Berdaftar secara rasmi", True), (0.63, OFF_R2, "Kena bayar", True), (0.83, OFF_R3, "Bukan kita yang ambil, WhatsApp yang ambil", None)):
        if t < t0: continue
        kr = ease((t - t0) / 0.25)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        y = ch * yy
        if ok: mark(d2, int(66 * S), y, int(22 * S), True)
        else: d2.ellipse((int(56 * S), y - 10 * S, int(76 * S), y + 10 * S), fill=BLUE)
        ff = f if d2.textlength(txt, font=f) < cw - 140 * S else F("b", 34)
        d2.text((int(106 * S), y), txt, font=ff, fill=BLACK if ok else BLUE, anchor="lm")
        lay.alpha_composite(fade_layer(l2, kr))
    put_card(base, lay, k, ko, 0.585)

def card_ban(base, t):
    if not inwin(t, CARD_BAN): return
    ch = H * 0.15
    lay, d, k, ko = card_base(t, CARD_BAN, ch); cw = lay.width
    y1 = ch * 0.30
    mark(d, int(62 * S), y1, int(26 * S), False)
    d.text((int(108 * S), y1), "WhatsApp tak rasmi", font=F("b", 46), fill="#5A5D66", anchor="lm")
    if t >= BAN_B:
        kb = back((t - BAN_B) / 0.3)
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        y2 = ch * 0.70; r = 30 * S
        d2.polygon([(62 * S, y2 - r), (62 * S + r * 1.1, y2 + r * 0.8), (62 * S - r * 1.1, y2 + r * 0.8)], fill=RED)
        d2.text((62 * S, y2 + r * 0.22), "!", font=F("xb", 36), fill=WHITE, anchor="mm")
        fb = F("xb", 56)
        d2.text((int(108 * S), y2), "Risiko kena ", font=F("b", 48), fill=BLACK, anchor="lm")
        d2.text((int(108 * S) + d2.textlength("Risiko kena ", font=F("b", 48)), y2), "BAN", font=fb, fill=RED, anchor="lm")
        lay.alpha_composite(fade_layer(l2, min(1, kb)))
    put_card(base, lay, k, ko, 0.595)

# ---------- motion komen: "Comment nak" ----------
def comments(base, t):
    if t < CMT_IN: return
    k = ease((t - CMT_IN) / 0.35)
    pw, ph = int(W * 0.78), int(H * 0.21)
    x0 = int(W * 0.46 - pw / 2); y0 = int(H * 0.585 + (1 - k) * H * 0.12)
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = int(34 * S)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=r, fill=(255, 255, 255, 245))
    fh, fn = F("b", 34), F("m", 36)
    d.text((pw // 2, int(44 * S)), "Komen", font=fh, fill=BLACK, anchor="mm")
    d.line((int(30 * S), int(84 * S), pw - int(30 * S), int(84 * S)), fill=GREY, width=max(1, int(2 * S)))
    d.text((pw // 2, int(150 * S)), "Nak tengok cara on WhatsApp pukal?", font=F("sb", 30), fill="#7A7C80", anchor="mm")
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
    draw_rich(im, CX, H * 0.505, "Hantar", F("xb", 120), stroke=9)
    d = ImageDraw.Draw(im); fk = F("xb", 124)
    tw = d.textlength("REMINDER", font=fk); bw, bh = int(tw + 70 * S), int(162 * S)
    bx, by = int(CX - bw / 2), int(H * 0.585 - bh / 2)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(26 * S), fill=ACC)
    d.text((CX, H * 0.585), "REMINDER", font=fk, fill=WHITE, anchor="mm")
    draw_rich(im, CX, H * 0.668, "yuran guna", F("xb", 104), stroke=9)
    draw_rich(im, CX, H * 0.735, "*WhatsApp?*", F("xb", 118), stroke=9, colors=(WHITE, "#3BE07A"))
    # potongan sebenar butang WhatsApp dari B-roll sistem (sebelah muka)
    src = _SCR["inv"].crop((1680, 480, 1870, 575))
    c = src.resize((int(src.width * 2.2 * S), int(src.height * 2.2 * S)), Image.LANCZOS).convert("RGBA")
    c.putalpha(round_mask(c.size, int(20 * S)))
    frm = Image.new("RGBA", (c.width + int(16 * S), c.height + int(16 * S)), (0, 0, 0, 0))
    ImageDraw.Draw(frm).rounded_rectangle((0, 0, frm.width - 1, frm.height - 1), radius=int(26 * S), fill=WHITE)
    frm.alpha_composite(c, (int(8 * S), int(8 * S)))
    dd = ImageDraw.Draw(frm); bx_, by_ = (1844 - 1680) * 2.2 * S + 8 * S, (551 - 480) * 2.2 * S + 8 * S
    rr = 38 * S
    dd.ellipse((bx_ - rr, by_ - rr, bx_ + rr, by_ + rr), outline=ACC, width=max(3, int(7 * S)))
    rot = shadowed(frm, 14, 120).rotate(-4, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(rot, (int(W * 0.26 - rot.width / 2), int(H * 0.165 - rot.height / 2)))
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
    label(im, t); card_ch(im, t); card_wa(im, t); num(im, t); card_cost(im, t); card_off(im, t); card_ban(im, t)
    comments(im, t); caption(im, t)
    return im

# ---------- audio ----------
SFXL = [  # (masa timeline, fail, gain dB) — SFX lembut sahaja
    (OFF - 0.12, "whoosh.wav", -24),
    (OFF + BR_DASH[0] - 0.05, "whoosh.wav", -22), (OFF + BR_INV[0] - 0.05, "whoosh.wav", -22),
    (OFF + BR_OVD[0] - 0.05, "whoosh.wav", -22), (OFF + BR_WA[0] - 0.05, "whoosh.wav", -22),
    (OFF + BR_DASH[0] + 1.0, "pop.wav", -24), (OFF + BR_INV[0] + 1.0, "pop.wav", -24), (OFF + BR_OVD[0] + 1.0, "pop.wav", -24),
    (OFF + WA_RING, "pop.wav", -21), (OFF + WA_TAP, "click.wav", -17),
    (OFF + CARD_CH[0], "pop.wav", -20), (OFF + CH_A, "pop.wav", -23), (OFF + CH_E, "pop.wav", -23), (OFF + CH_AUTO, "ding.wav", -25),
    (OFF + CARD_WA[0], "pop.wav", -20), (OFF + WA_A, "pop.wav", -23), (OFF + WA_S, "pop.wav", -23),
    (OFF + NUM[0], "pop.wav", -19),
    (OFF + CARD_COST[0], "pop.wav", -20), (OFF + COST_FREE, "ding.wav", -24), (OFF + COST_R2, "pop.wav", -23), (OFF + COST_KR, "pop.wav", -22),
    (OFF + CARD_OFF[0], "pop.wav", -20), (OFF + OFF_R1, "pop.wav", -24), (OFF + OFF_R2, "pop.wav", -24), (OFF + OFF_R3, "pop.wav", -24),
    (OFF + CARD_BAN[0], "pop.wav", -21), (OFF + BAN_B, "bonk.wav", -24),
    (OFF + CMT_IN, "whoosh.wav", -24), (OFF + TYPE_A + 0.05, "tick.wav", -27), (OFF + TYPE_A + 0.25, "tick.wav", -27), (OFF + TYPE_B + 0.05, "tick.wav", -27),
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
