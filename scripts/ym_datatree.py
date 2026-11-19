"""Grafik gerak 'Struktur data Yuran.my' (Program > Kategori > Modul > Kelas) dalam warna brand.

Fungsi utama menerima masa relatif / progres supaya boleh dipakai untuk mockup storyboard dan render frame.
Semua koordinat dalam ruang 1080x1920, didarab SC.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

B1, B2, WH, INK, GR = (42, 59, 143), (41, 171, 226), (255, 255, 255), (20, 24, 50), (231, 232, 233)
B1D = (30, 42, 108)
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SC = 1.0
def S(v): return int(round(v * SC))
_fc = {}
def F(p, s):
    k = (p, int(s * SC))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, max(8, int(s * SC)))
    return _fc[k]
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ramp(t, t0, d=0.35): return ease((t - t0) / d) if t >= t0 else 0.0

LEVELS = [
    {"n": 1, "name": "PROGRAM", "items": ["Bahasa Arab"], "y": 340},
    {"n": 2, "name": "KATEGORI", "items": ["Sesi Pagi", "Sesi Petang"], "y": 610},
    {"n": 3, "name": "MODUL", "items": ["Peringkat 1", "Peringkat 2", "Peringkat 3"], "y": 880},
    {"n": 4, "name": "KELAS", "items": ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4"], "y": 1150},
]
NODE_H = 124

def node_boxes(lv):
    n = len(lv["items"]); gap = 22; total = 940
    w = (total - gap * (n - 1)) / n
    x0 = (1080 - total) / 2; y = lv["y"] + 52
    return [(x0 + i * (w + gap), y, x0 + i * (w + gap) + w, y + NODE_H) for i in range(n)]

def bg_blue(W, H):
    im = Image.new("RGB", (W, H), B1); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = y / H; c = tuple(int(B1[i] * (1 - 0.25 * k) + B1D[i] * 0.25 * k) for i in range(3)); d.rectangle((0, y, W, y + 4), fill=c)
    # hiasan grid titik halus
    for y in range(S(60), H, S(60)):
        for x in range(S(60), W, S(60)): d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(70, 88, 170))
    return im

def tree(img, t, reveal, names=None, path=None, path_t=None, title_a=1.0):
    """reveal: senarai masa mula setiap aras [t1,t2,t3,t4]; item dalam aras muncul berperingkat.
    names: gantian nama kelas {indeks: (nama_baru, t_mula)}. path: indeks nod terpilih setiap aras, path_t masa setiap langkah."""
    o = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    if title_a > 0:
        d.text((S(70), S(200)), "Struktur data Yuran.my", font=F(FX, 54), fill=WH + (int(255 * title_a),))
        d.text((S(70), S(268)), "Sebagai contoh", font=F(FS, 32), fill=GR + (int(200 * title_a),))
    for li, lv in enumerate(LEVELS):
        t0 = reveal[li]
        if t is None or t0 is None or t < t0: continue
        a = ramp(t, t0, 0.3)
        # label aras
        lab = f"{lv['n']}  {lv['name']}"
        d.rounded_rectangle((S(70), S(lv["y"]) - S(4), S(70) + S(40), S(lv["y"]) + S(36)), S(10), fill=B2 + (int(255 * a),))
        d.text((S(90), S(lv["y"]) + S(16)), str(lv["n"]), font=F(FX, 28), fill=WH + (int(255 * a),), anchor="mm")
        d.text((S(126), S(lv["y"]) + S(16)), lv["name"], font=F(FX, 34), fill=WH + (int(255 * a),), anchor="lm")
        boxes = node_boxes(lv)
        # penyambung dari aras atas
        if li > 0 and reveal[li - 1] is not None:
            pb = node_boxes(LEVELS[li - 1])
            for bi, (x0, y0, x1, y1) in enumerate(boxes):
                ta = ramp(t, t0 + bi * 0.12, 0.35)
                if ta <= 0: continue
                src = pb[min(len(pb) - 1, int(bi * len(pb) / len(boxes)))] if len(pb) > 1 else pb[0]
                if path is not None and path_t is not None and li < len(path) and path[li] == bi and t >= path_t[li]:
                    src = pb[path[li - 1]]
                sx, sy = (src[0] + src[2]) / 2, src[3]; ex, ey = (x0 + x1) / 2, y0
                my = (sy + ey) / 2
                pts = [(sx, sy), (sx, my), (ex, my), (ex, ey)]
                L = [abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]) for i in range(3)]; tot = sum(L) * ta
                cur = [pts[0]]
                for i in range(3):
                    if tot <= 0: break
                    seg = min(L[i], tot); f = seg / L[i] if L[i] else 1
                    cur.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)); tot -= seg
                on_path = path is not None and path_t is not None and li < len(path) and path[li] == bi and path[li - 1] == pb.index(src) and t >= path_t[li]
                col = B2 + (255,) if on_path else (150, 165, 225, int(200 * ta))
                d.line([(S(x), S(y)) for x, y in cur], fill=col, width=S(8 if on_path else 4), joint="curve")
        for bi, (x0, y0, x1, y1) in enumerate(boxes):
            ba = ramp(t, t0 + bi * 0.12, 0.3)
            if ba <= 0: continue
            dy = (1 - ba) * 24
            sel = path is not None and path_t is not None and li < len(path) and path[li] == bi and t >= path_t[li]
            dim = path is not None and path_t is not None and t >= path_t[0] and not sel
            fill = (B2 if sel else (WH if not dim else (190, 198, 230))) + (int(255 * ba),)
            d.rounded_rectangle((S(x0), S(y0 + dy), S(x1), S(y1 + dy)), S(22), fill=fill)
            txt = lv["items"][bi]
            if names and li == 3 and bi in names and t >= names[bi][1]:
                k = ramp(t, names[bi][1], 0.3); txt = names[bi][0]
            fs = 46 if len(lv["items"]) <= 2 else (40 if len(lv["items"]) == 3 else 36)
            tw = d.textlength(txt, font=F(FX, fs))
            if tw > S(x1 - x0 - 24): fs = fs * (x1 - x0 - 24) * SC / tw
            d.text((S((x0 + x1) / 2), S((y0 + y1) / 2 + dy)), txt, font=F(FX, fs), fill=(WH if sel else B1) + (int(255 * ba),), anchor="mm")
    # token pelajar
    if path is not None and path_t is not None and t >= path_t[0]:
        k = max(i for i in range(len(path_t)) if t >= path_t[i])
        b = node_boxes(LEVELS[k])[path[k]]
        if k + 1 < len(path_t):
            nb = node_boxes(LEVELS[k + 1])[path[k + 1]]; f = ramp(t, path_t[k + 1] - 0.45, 0.45) if t >= path_t[k + 1] - 0.45 else 0
        else:
            nb, f = b, 0
        cx = b[2] - 6 + (nb[2] - b[2]) * f; cy = b[1] - 6 + (nb[1] - b[1]) * f
        r = 34
        d.ellipse((S(cx - r), S(cy - r), S(cx + r), S(cy + r)), fill=WH, outline=B2, width=S(6))
        d.text((S(cx), S(cy)), "A", font=F(FX, 34), fill=B1, anchor="mm")
        d.rounded_rectangle((S(cx - r - 112), S(cy - 22), S(cx - r - 8), S(cy + 22)), S(20), fill=INK)
        d.text((S(cx - r - 60), S(cy)), "Abu", font=F(FX, 28), fill=WH, anchor="mm")
    img.alpha_composite(o)
    return img

# ---------- grafik kecil atas talking head ----------
def card(text, sub=None, w=None, fill=WH, ink=B1, num=None, fs=40):
    f = F(FX, fs); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1))); tw = d0.textlength(text, font=f)
    pad = S(84) if num is not None else S(34)
    w = int(w * SC) if w else int(tw + pad + S(34)); h = S(fs * 2.1)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), S(22), fill=fill)
    if num is not None:
        d.ellipse((S(14), (h - S(52)) // 2, S(66), (h + S(52)) // 2), fill=B2)
        d.text((S(40), h // 2), str(num), font=F(FX, 30), fill=WH, anchor="mm")
    d.text((pad, h // 2), text, font=f, fill=ink, anchor="lm")
    return im

def paste_a(img, ov, x, y, a=1.0):
    if a <= 0: return
    if a < 1:
        ov = ov.copy(); ov.putalpha(ov.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(ov, (int(x), int(y)))

def messy_to_tidy(img, t, t0, t_snap, t_end, label_a="Data bersepah", label_b="Data tersusun"):
    """Kad-kad data bertaburan kemudian tersusun rapi. Kawasan y 760-1240."""
    import math
    if t < t0 or t > t_end: return img
    a = min(ramp(t, t0, 0.3), ease((t_end - t) / 0.3))
    k = ramp(t, t_snap, 0.6)
    names = ["Program", "Kategori", "Modul", "Kelas"]
    messy = [(-150, 40, -18), (140, -30, 14), (-60, 170, 9), (170, 150, -12)]
    for i, nm in enumerate(names):
        c = card(nm, w=360, num=i + 1, fs=36)
        mx, my, rot = messy[i]
        tx, ty = 0, (i - 1.5) * S(96) / SC
        x = mx + (tx - mx) * k; y = my + (ty - my) * k; r = rot * (1 - k)
        cr = c.rotate(r, expand=True, resample=Image.BICUBIC)
        paste_a(img, cr, S(540 + x) - cr.width / 2, S(1000 + y) - cr.height / 2, a)
    lab = card(label_b if k > 0.5 else label_a, fill=(B2 if k > 0.5 else INK), ink=WH, fs=32)
    paste_a(img, lab, S(540) - lab.width / 2, S(740), a)
    return img

def list4(img, t, ts, t_end, chain_t=None):
    """Senarai 4 komponen bernombor di kiri; chain_t: masa garis penyambung muncul."""
    if t < ts[0] or t > t_end: return img
    names = ["Program", "Kategori", "Modul", "Kelas"]
    ae = ease((t_end - t) / 0.3)
    d = ImageDraw.Draw(img)
    if chain_t is not None and t >= chain_t:
        k = ramp(t, chain_t, 0.8)
        y0, y1 = S(800 + 48), S(800 + 48 + 3 * 120)
        d.line((S(103), y0, S(103), y0 + (y1 - y0) * k), fill=B2 + (int(255 * ae),), width=S(10))
    for i, nm in enumerate(names):
        if t < ts[i]: continue
        a = min(ramp(t, ts[i], 0.3), ae)
        c = card(nm, w=420, num=i + 1, fs=40)
        paste_a(img, c, S(70) - (1 - a) * S(50), S(800 + i * 120), a)
    if chain_t is not None and t >= chain_t + 0.4:
        a = min(ramp(t, chain_t + 0.4, 0.3), ae)
        c = card("Berkait rapat", fill=B2, ink=WH, fs=34)
        paste_a(img, c, S(520), S(800 + 1.5 * 120 + 10), a)
    return img

def chips_rows(img, t, rows, t_end, y=820):
    """rows: [(tajuk, [(teks, t_mula), ...]), ...] cip tersusun di bawah tajuk."""
    ae = ease((t_end - t) / 0.3)
    if t > t_end: return img
    yy = y
    for title, items in rows:
        if t < items[0][1] - 0.2: yy += 250; continue
        ta = min(ramp(t, items[0][1] - 0.2, 0.3), ae)
        tc = card(title, fill=B1, ink=WH, fs=36); paste_a(img, tc, S(70), S(yy), ta)
        x = 70
        for txt, t0 in items:
            if t < t0: continue
            a = min(ramp(t, t0, 0.3), ae)
            c = card(txt, fs=42); paste_a(img, c, S(x), S(yy + 96) + (1 - a) * S(20), a); x += c.width / SC + 18
        yy += 250
    return img
