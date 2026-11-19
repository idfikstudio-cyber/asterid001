"""Paparan tutorial Google Sheet: tangkapan skrin sebenar (2x) dalam kad, kamera zoom/pan, highlight sel, nota.

Koordinat sel dalam piksel tangkapan skrin (deviceScaleFactor 2). Koordinat output dalam ruang 1080x1920, didarab SC (ym_datatree.SC).
"""
from PIL import Image, ImageDraw, ImageFilter
import ym_datatree as T

CARD = (40, 380, 1040, 1180)          # kotak paparan sheet dalam frame 1080x1920
TOP_CROP = 282                         # buang bar tajuk/menu/avatar (nama fail) di atas lajur huruf

# sempadan lajur (x kanan setiap lajur bermula dari tepi kiri lajur A) dan baris, dikesan dari tangkapan skrin
COLS = {
 "Programs": [92, 292, 540, 726, 912, 1428, 1616, 1826, 2084, 2280, 2632, 2788, 3026, 3242, 3458, 3674, 3890, 4106, 4322, 4494, 4646, 4862, 5078, 5320, 5516, 5730, 5928, 6152, 6366, 6580, 6600],
 "Students": [92, 222, 554, 752, 1042, 1254, 1442, 1634, 1864, 2448, 2572, 2730, 2886, 3138, 3348, 3564, 3778, 3984, 4180, 4348, 4518, 4696, 4852, 5080, 5288, 5484],
 "Staffs": [92, 380, 576, 866, 1100, 1292, 1408, 1582, 1756, 1944, 2060, 2220, 2846, 2974, 3106, 3234],
}
ROWS = {  # (atas, bawah) baris 3 (kumpulan), 4 (tajuk lajur), 5 (contoh)
 "Programs": {3: (432, 472), 4: (472, 548), 5: (548, 588)},
 "Students": {3: (432, 472), 4: (472, 600), 5: (600, 644)},
 "Staffs": {4: (480, 560), 5: (560, 600), 9: (560, 760)},
}
def L2i(letter):
    n = 0
    for ch in letter: n = n * 26 + (ord(ch) - 64)
    return n - 1
def cell(tab, c0, c1=None, r0=4, r1=None):
    """Kotak sumber untuk lajur c0..c1 (huruf) dan baris r0..r1."""
    c1 = c1 or c0; r1 = r1 or r0; X = COLS[tab]; R = ROWS[tab]
    return (X[L2i(c0)], R[r0][0], X[L2i(c1) + 1], R[r1][1])

_img = {}
def tab_img(path):
    if path not in _img: _img[path] = Image.open(path).convert("RGB")
    return _img[path]

AVAIL_H = 1270 - TOP_CROP

def cam_for(box, pad=60, min_w=520, ar=0.9):
    """Kamera (x0, y0, w, h) yang memuatkan kotak sumber. Kad menjadi lebih rendah untuk kawasan lebar."""
    x0, y0, x1, y1 = box
    w = max(min_w, x1 - x0 + 2 * pad)
    h = min(w * ar, AVAIL_H); h = max(h, min(AVAIL_H, y1 - y0 + 2 * pad))
    cx = (x0 + x1) / 2; x = max(0, cx - w / 2)
    y = max(TOP_CROP, min(y0 - pad * 1.5, 1270 - h))
    return (x, y, w, h)

def lerp_cam(a, b, k):
    k = T.ease(k); return tuple(a[i] + (b[i] - a[i]) * k for i in range(4))

def sheet(img, path, cam, hl=(), notes=(), card_a=1.0):
    """hl: senarai (kotak_sumber, label, alpha, gaya) gaya 'blue'|'warn'. notes: (teks, alpha, y) kad nota di bawah kad."""
    S = T.S
    x, y, w, h = cam
    cx0, cy0, cx1, _ = CARD; cw = cx1 - cx0; ch = min(CARD[3] - CARD[1], cw * h / w); cy1 = cy0 + ch
    w = cw * h / ch
    src = tab_img(path)
    crop = src.crop((int(x), int(y), int(x + w), int(y + h))).resize((S(cw), S(ch)), Image.LANCZOS)
    # bayang + kad
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((S(cx0), S(cy0 + 14), S(cx1), S(cy1 + 14)), S(30), fill=(0, 0, 0, int(110 * card_a)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S(18))))
    m = Image.new("L", (S(cw), S(ch)), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, S(cw) - 1, S(ch) - 1), S(30), fill=int(255 * card_a))
    img.paste(crop, (S(cx0), S(cy0)), m)
    sc = cw / w
    def P(px, py): return S(cx0 + (px - x) * sc), S(cy0 + (py - y) * sc)
    o = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    labels = []
    for box, label, a, style in hl:
        if a <= 0: continue
        col = T.B2 if style == "blue" else (245, 166, 35)
        x0, y0 = P(box[0], box[1]); x1, y1 = P(box[2], box[3])
        x0 = max(x0, S(cx0) + S(6)); x1 = min(x1, S(cx1) - S(6))
        y0 = max(y0, S(cy0) + S(6)); y1 = min(y1, S(cy1) - S(6))
        if x1 - x0 < S(20) or y1 - y0 < S(10): continue
        d.rounded_rectangle((x0 - S(6), y0 - S(6), x1 + S(6), y1 + S(6)), S(12), fill=col + (int(40 * a),), outline=col + (int(255 * a),), width=S(7))
        if label: labels.append((label, (x0 + x1) / 2, y1 + S(18), a, style))
    # gelapkan luar kad sedikit bila ada highlight? tidak — kekal kemas
    img.alpha_composite(o)
    for label, lx, ly, a, style in labels:
        c = T.card(label, fill=(T.B2 if style == "blue" else (245, 166, 35)), ink=T.WH, fs=34)
        lx = min(max(lx - c.width / 2, S(cx0 + 10)), S(cx1 - 10) - c.width)
        ly = min(ly, S(cy1) - c.height - S(8))
        T.paste_a(img, c, lx, ly, a)
    ny = cy1 + 34
    for text, a in notes:
        if a <= 0: continue
        c = T.card(text, fill=T.WH, ink=T.B1, fs=38)
        T.paste_a(img, c, S(540) - c.width / 2, S(ny) + (1 - a) * S(20), a); ny += c.height / T.SC + 16
    return img

def warn_card(img, title, body, a, y=1320):
    """Kad amaran: ikon ! dalam bulatan oren, tajuk tebal, badan teks."""
    S = T.S
    if a <= 0: return img
    w, h = 1000, 220
    c = Image.new("RGBA", (S(w), S(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, S(w) - 1, S(h) - 1), S(28), fill=T.WH, outline=(245, 166, 35), width=S(6))
    d.ellipse((S(30), S(36), S(110), S(116)), fill=(245, 166, 35))
    d.text((S(70), S(76)), "!", font=T.F(T.FX, 56), fill=T.WH, anchor="mm")
    d.text((S(136), S(46)), title, font=T.F(T.FX, 40), fill=T.B1)
    yy = 104
    for line in body:
        d.text((S(136), S(yy)), line, font=T.F(T.FS, 34), fill=T.INK); yy += 46
    T.paste_a(img, c, S(40), S(y) + (1 - a) * S(24), a)
    return img

def header(img, title, sub=None, a=1.0):
    S = T.S
    d = ImageDraw.Draw(img)
    d.text((S(60), S(190)), title, font=T.F(T.FX, 58), fill=T.WH + (int(255 * a),))
    if sub: d.text((S(60), S(266)), sub, font=T.F(T.FS, 34), fill=T.GR + (int(220 * a),))
    return img
