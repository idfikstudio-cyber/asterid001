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

TREE_X0, TREE_W = 300, 710

def node_boxes(lv):
    n = len(lv["items"]); gap = 22
    w = (TREE_W - gap * (n - 1)) / n
    y = lv["y"] + 40
    return [(TREE_X0 + i * (w + gap), y, TREE_X0 + i * (w + gap) + w, y + NODE_H) for i in range(n)]

def parent_of(li, bi):
    pb = node_boxes(LEVELS[li - 1]); n = len(LEVELS[li]["items"])
    return min(len(pb) - 1, int(bi * len(pb) / n))

def bg_blue(W, H):
    im = Image.new("RGB", (W, H), B1); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = y / H; c = tuple(int(B1[i] * (1 - 0.25 * k) + B1D[i] * 0.25 * k) for i in range(3)); d.rectangle((0, y, W, y + 4), fill=c)
    # hiasan grid titik halus
    for y in range(S(60), H, S(60)):
        for x in range(S(60), W, S(60)): d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(70, 88, 170))
    return im

def tree(img, t, reveal, names=None, path=None, path_t=None, title_a=1.0, items=None):
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
        # label aras: lajur kiri (x 70-280), berpusat pada baris kotak
        cy = lv["y"] + 40 + NODE_H / 2
        d.ellipse((S(70), S(cy - 52), S(118), S(cy - 4)), fill=B2 + (int(255 * a),))
        d.text((S(94), S(cy - 28)), str(lv["n"]), font=F(FX, 30), fill=WH + (int(255 * a),), anchor="mm")
        d.text((S(70), S(cy + 24)), lv["name"], font=F(FX, 30), fill=WH + (int(255 * a),), anchor="lm")
        boxes = node_boxes(lv)
        # penyambung dari aras atas
        if li > 0 and reveal[li - 1] is not None:
            pb = node_boxes(LEVELS[li - 1])
            for bi, (x0, y0, x1, y1) in enumerate(boxes):
                it0 = items[li][bi] if items and li in items else t0 + bi * 0.12
                ta = ramp(t, it0 - 0.15, 0.35)
                if ta <= 0: continue
                src = pb[parent_of(li, bi)]
                if path is not None and path_t is not None and li < len(path) and path[li] == bi and t >= path_t[li]:
                    src = pb[path[li - 1]]
                # gaya bas: turun dari induk ke garis bas tepat atas aras anak, mendatar, turun ke anak
                sx, sy = (src[0] + src[2]) / 2, src[3]; ex, ey = (x0 + x1) / 2, y0
                my = ey - 40
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
            it0 = items[li][bi] if items and li in items else t0 + bi * 0.12
            ba = ramp(t, it0, 0.3)
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
    for row in rows:
        if len(row) == 3: title, tt0, items = row
        else: (title, items), tt0 = row, row[1][0][1] - 0.2
        if t < tt0: yy += 250; continue
        ta = min(ramp(t, tt0, 0.3), ae)
        tc = card(title, fill=B1, ink=WH, fs=36); paste_a(img, tc, S(70), S(yy), ta)
        x = 70
        for txt, t0 in items:
            if t < t0: continue
            a = min(ramp(t, t0, 0.3), ae)
            c = card(txt, fs=42); paste_a(img, c, S(x), S(yy + 96) + (1 - a) * S(20), a); x += c.width / SC + 18
        yy += 250
    return img

# ---------- simulasi Abu: langkah demi langkah ----------
ABU_STEPS = [("PELAJAR", "Abu"), ("PROGRAM", "Bahasa Arab"), ("KATEGORI", "Sesi Petang"), ("MODUL", "Peringkat 2"), ("KELAS", "Kelas 1")]
ABU_Y0, ABU_DY, ABU_H = 400, 200, 132

def _chev(d, cx, cy, s, col, w=6):
    d.line((S(cx - s), S(cy - s / 2), S(cx), S(cy + s / 2), S(cx + s), S(cy - s / 2)), fill=col, width=S(w), joint="curve")

def abu_flow(img, t, times, glow_t=None, t_in=None):
    """times: masa Abu tiba di setiap langkah [abu, program, kategori, modul, kelas]."""
    o = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    a0 = ramp(t, t_in if t_in is not None else times[0] - 0.6, 0.35)
    d.text((S(70), S(200)), "Simulasi pelajar", font=F(FX, 54), fill=WH + (int(255 * a0),))
    d.text((S(70), S(268)), "Abu → Program → Kategori → Modul → Kelas", font=F(FS, 30), fill=GR + (int(210 * a0),))
    x0, x1 = 230, 1010
    reached = [t >= tt for tt in times]
    k = max([i for i, r in enumerate(reached) if r], default=-1)
    # rel kiri
    rx = 140
    y_top = ABU_Y0 + ABU_H / 2; y_bot = ABU_Y0 + 4 * ABU_DY + ABU_H / 2
    d.line((S(rx), S(y_top), S(rx), S(y_bot)), fill=(90, 108, 190, int(255 * a0)), width=S(6))
    if k >= 1:
        # bahagian rel yang sudah dilalui
        prog = k + (ramp(t, times[k + 1] - 0.5, 0.5) if k + 1 < len(times) and t >= times[k + 1] - 0.5 else 0)
        d.line((S(rx), S(y_top), S(rx), S(y_top + ABU_DY * min(prog, 4))), fill=B2 + (255,), width=S(10))
    for i, (lab, val) in enumerate(ABU_STEPS):
        y = ABU_Y0 + i * ABU_DY
        on = reached[i]
        ka = ramp(t, times[i], 0.3) if on else 0
        glow = glow_t is not None and t >= glow_t
        # kad
        if on:
            fill = (B2 if i > 0 else WH) + (255,)
        else:
            fill = (55, 72, 160, int(255 * a0))
        d.rounded_rectangle((S(x0), S(y), S(x1), S(y + ABU_H)), S(26), fill=fill,
                            outline=(WH + (255,)) if (glow and on) else (110, 128, 205, int(255 * a0)), width=S(5 if glow and on else 3))
        # titik pada rel
        d.ellipse((S(rx - 16), S(y + ABU_H / 2 - 16), S(rx + 16), S(y + ABU_H / 2 + 16)), fill=(B2 if on else (90, 108, 190)) + (int(255 * a0),))
        if i == 0:
            d.text((S(x0 + 40), S(y + 40)), lab, font=F(FX, 26), fill=(B2 if on else GR) + (int(255 * a0),), anchor="lm")
            d.text((S(x0 + 40), S(y + 88)), val if on else "?", font=F(FX, 46), fill=(B1 if on else GR) + (int(255 * a0),), anchor="lm")
        else:
            d.text((S(x0 + 40), S(y + 40)), f"{i}  {lab}", font=F(FX, 26), fill=(WH if on else GR) + (int(255 * a0),), anchor="lm")
            if on:
                d.text((S(x0 + 40), S(y + 88) + (1 - ka) * S(16)), val, font=F(FX, 46), fill=WH + (int(255 * ka),), anchor="lm")
            else:
                d.text((S(x0 + 40), S(y + 88)), "…", font=F(FX, 46), fill=(150, 165, 225, int(255 * a0)), anchor="lm")
        if i < 4:
            _chev(d, (x0 + x1) / 2, y + ABU_H + (ABU_DY - ABU_H) / 2, 16, (B2 if reached[i + 1] else (120, 138, 210)) + (int(255 * a0),))
    # token Abu bergerak di rel
    if k >= 0:
        if k + 1 < len(times) and t >= times[k + 1] - 0.5:
            f = ramp(t, times[k + 1] - 0.5, 0.5)
        else:
            f = 0
        cy = ABU_Y0 + ABU_H / 2 + ABU_DY * (k + f)
        r = 40
        ta = ramp(t, times[0], 0.3)
        d.ellipse((S(rx - r), S(cy - r), S(rx + r), S(cy + r)), fill=WH + (int(255 * ta),), outline=B2 + (int(255 * ta),), width=S(7))
        d.text((S(rx), S(cy)), "A", font=F(FX, 40), fill=B1 + (int(255 * ta),), anchor="mm")
    img.alpha_composite(o)
    return img

# ---------- jenis institusi ----------
INST = ["Pusat Tuisyen", "Sekolah Asrama", "Sekolah Harian", "Persatuan Penduduk", "Kelab Sukan", "Dan lain-lain"]

def inst_list(img, t, t0, item_t):
    o = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    a = ramp(t, t0, 0.35)
    d.text((S(90), S(330)), "Jenis Institusi", font=F(FX, 84), fill=WH + (int(255 * a),))
    d.rounded_rectangle((S(90), S(450), S(90) + S(150) * a, S(460)), S(5), fill=B2 + (int(255 * a),))
    for i, (txt, ti) in enumerate(zip(INST, item_t)):
        if t < ti: continue
        k = ramp(t, ti, 0.3); y = 540 + i * 128; dx = (1 - k) * 40
        for cx in (112, 142):   # ">>"
            d.line((S(cx + dx - 9), S(y + 30), S(cx + dx + 9), S(y + 46), S(cx + dx - 9), S(y + 62)), fill=B2 + (int(255 * k),), width=S(8), joint="curve")
        d.text((S(186 + dx), S(y + 46)), txt, font=F(FX, 56), fill=(WH if i < 5 else GR) + (int(255 * k),), anchor="lm")
    img.alpha_composite(o)
    return img
