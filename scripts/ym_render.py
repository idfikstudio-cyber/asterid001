# Render Yuran.my talking-head video: thumbnail 1 s + isi (EDL) + B-roll + grafik + caption + end card.
# usage: python3 ym_render.py <workdir> <W> <out.mp4>
#   workdir: raw/<src>, edit/edl.json (konfigurasi video), edit/transcript_cut.json, broll/integrasi.mp4,
#            brand/logo_white.png, audio/*.wav (sfx + music.wav)
#   edl.json: src, segments [[in, out, zoom], ...] (segmen bersambung = tiada potongan), face_y, thumb_t,
#             fix {transkrip: caption}, gfx [[t0, t1, jenis, data]], sfx [[t, nama, gain]]; "END" = mula end card
import json, os, re, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD, W, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
H = W * 16 // 9; u = W / 1080; FPS = 30
P = lambda *a: os.path.join(WD, *a)
CFG = json.load(open(P("edit/edl.json")))
EDL = [s[:2] for s in CFG["segments"]]
SRC = P("raw", CFG["src"])
TH = 1.0                                   # thumbnail
CONTENT = sum(b - a for a, b in EDL)
END0 = TH + CONTENT; DUR = END0 + 1.5      # end card 1.5 s
NAVY, ACC, INK, GREY, WHITE = (42, 59, 143), (41, 171, 226), (35, 31, 32), (231, 232, 233), (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/Inter-%s.otf"   # Acumin Pro tiada: guna Inter (catat dalam log)
font = lambda w, s: ImageFont.truetype(F % w, max(8, int(s * u)))

# ---------------- zoom per segment (punch-in tiap 2-3 potongan), muka di sepertiga atas ----------------
BASE, PUNCH = 1.15, 1.30
ZOOM = [PUNCH if s[2] == "P" else BASE for s in CFG["segments"]]
FACE_Y = CFG["face_y"]                             # paras mata dalam frame asal
def y0(z, target=0.29): return max(0.0, min(1 - 1 / z, FACE_Y - target / z))
GRADE = ("eq=brightness=0.02:contrast=1.05:saturation=1.06:gamma=1.03,"
         "colorbalance=bs=-0.01:bm=-0.01,curves=all='0/0.02 0.5/0.52 1/0.99',unsharp=5:5:0.4")

def run(cmd): subprocess.run(cmd, check=True)

def build_content(path):
    fc = ""
    for i, (a, b) in enumerate(EDL):
        z = ZOOM[i]
        fc += (f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:ih*{y0(z):.4f},"
               f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS}[v{i}];")
    fc += "".join(f"[v{i}]" for i in range(len(EDL))) + f"concat=n={len(EDL)}:v=1:a=0,{GRADE}[o]"
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[o]",
         "-c:v", "libx264", "-crf", "14", "-preset", "fast", path])

def build_broll(path, dur):
    # Rakaman sistem Yuran.my: senarai invois. Lajur nama/item & jumlah individu diblur (privasi).
    # crop 9:16 dari x=1390 (Items hujung, Total, Status, Action), zoom perlahan ke lajur Status.
    blur = "[c]split[c1][c2];[c2]crop=200:520:0:200,boxblur=14:3[bl];[c1][bl]overlay=0:200[cb]"
    fc = (f"[0:v]trim=12.4:{12.4 + dur},setpts=PTS-STARTPTS,fps={FPS},crop=500:889:1390:250[c];{blur};"
          f"[cb]scale={W}:{H}:flags=lanczos,setsar=1,"
          f"zoompan=z='1+0.10*on/{int(dur * FPS)}':x='iw*0.46-iw/zoom*0.46':y='ih*0.5-ih/zoom*0.5':d=1:s={W}x{H}:fps={FPS},"
          f"eq=saturation=1.05[o]")
    run(["ffmpeg", "-v", "error", "-y", "-i", P("broll/integrasi.mp4"), "-filter_complex", fc, "-map", "[o]",
         "-t", str(dur), "-c:v", "libx264", "-crf", "14", "-preset", "fast", path])

def grab(t, z, path):
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", SRC, "-frames:v", "1", "-vf",
         f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:ih*{y0(z, 0.27):.4f},scale={W}:{H}:flags=lanczos,{GRADE}", path])

# ---------------- drawing helpers ----------------
def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def text_w(d, s, f): return d.textlength(s, font=f)
def rrect(im, box, r, fill, shadow=True):
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle(
            (box[0], box[1] + 6 * u, box[2], box[3] + 6 * u), r, fill=(10, 16, 50, 70))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * u)))
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=fill)

def paste(dst, src, x, y, a=1.0):
    if a <= 0: return
    if a < 1:
        src = src.copy(); al = src.split()[3].point(lambda p: int(p * a)); src.putalpha(al)
    dst.alpha_composite(src, (int(x), int(y)))

def icon_check(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)], fill=WHITE, width=max(2, int(r * .28)), joint="curve")
def icon_cross(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col); k = r * .38; w = max(2, int(r * .28))
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=WHITE, width=w); d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=WHITE, width=w)
def icon_clock(d, cx, cy, r, col, ang=0.0, w=None):
    w = w or max(2, int(r * .16)); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=w)
    d.line([(cx, cy), (cx + r * .55 * math.sin(ang), cy - r * .55 * math.cos(ang))], fill=col, width=w)
    d.line([(cx, cy), (cx + r * .75 * math.sin(ang * 12), cy - r * .75 * math.cos(ang * 12))], fill=col, width=max(2, w * 2 // 3))

# ---------------- captions ----------------
FIX = CFG["fix"]
HOT = {"KAFA", "kerani", "yuran", "resit", "tally", "fokus", "berkualiti", "senyap-senyap", "curi", "mendidik", "komen", "admin", "collection"}
def captions():
    W_ = []
    for s in json.load(open(P("edit/transcript_cut.json"))):
        for w in s["words"]:
            t = w["w"].strip(); core = re.sub(r"[.,?!]", "", t); punct = t[len(core):] if t.startswith(core) else ""
            if t.startswith("-") and W_: W_[-1]["w"] += t.rstrip(".,"); W_[-1]["e"] = w["e"] + TH; continue
            if core in FIX:
                if FIX[core] is None: W_[-1]["p"] = punct or W_[-1].get("p", ""); continue
                core = FIX[core]
            W_.append({"w": core, "p": punct, "s": w["s"] + TH, "e": min(w["e"], w["s"] + 0.8) + TH})
    ch, cur = [], []
    for i, w in enumerate(W_):
        cur.append(w); nxt = W_[i + 1] if i + 1 < len(W_) else None
        if len(cur) >= 3 or w["p"] or not nxt or nxt["s"] - w["e"] > 0.4:
            e = nxt["s"] if nxt and nxt["s"] - w["e"] < 0.4 else w["e"] + 0.2
            ch.append({"s": cur[0]["s"], "e": min(e, END0), "w": [(x["w"] + ("?" if x["p"] == "?" else ""), x["w"] in HOT) for x in cur]}); cur = []
    return ch
CAPS = captions()
CF = font("ExtraBold", 66)
def draw_caption(im, t):
    c = next((c for c in CAPS if c["s"] <= t < c["e"]), None)
    if not c: return
    d = ImageDraw.Draw(im); sp = 18 * u
    words = c["w"]; ws = [text_w(d, w, CF) for w, _ in words]; tw = sum(ws) + sp * (len(words) - 1)
    k = ease((t - c["s"]) / 0.12); x = 0.46 * W - tw / 2; y = 0.665 * H + (1 - k) * 14 * u
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    if any(g[2] == "broll" and g[0] <= t < g[1] for g in GFX):  # latar cerah: pil gelap di belakang caption
        rrect(layer, (x - 26 * u, y - 14 * u, x + tw + 26 * u, y + 92 * u), 24 * u, (*NAVY, 235), shadow=False)
    for (w, hot), wd in zip(words, ws):
        ld.text((x, y), w, font=CF, fill=ACC if hot else WHITE, stroke_width=int(7 * u), stroke_fill=(20, 24, 50))
        x += wd + sp
    sh = layer.split()[3].filter(ImageFilter.GaussianBlur(8 * u)).point(lambda p: int(p * .45))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); shadow.putalpha(sh)
    im.alpha_composite(shadow, (0, int(4 * u))); paste(im, layer, 0, 0, k)

# ---------------- graphics ----------------
def card_rows(title, rows, t, t0, t1, kinds=None):
    """Kad senarai di kiri (atas bahu), baris muncul ikut masa disebut."""
    a = ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25))
    if a <= 0: return None
    fT, fL, fR = font("Bold", 30), font("SemiBold", 26), font("Bold", 44)
    cw = 0.62 * W; rh = 96 * u; n = sum(1 for r in rows if t >= r[0])
    chh = 80 * u + max(1, n) * rh + 14 * u
    im = Image.new("RGBA", (int(cw + 40 * u), int(chh + 40 * u)), (0, 0, 0, 0))
    rrect(im, (10 * u, 10 * u, 10 * u + cw, 10 * u + chh), 28 * u, (255, 255, 255, 246))
    d = ImageDraw.Draw(im); d.text((36 * u, 30 * u), title, font=fT, fill=NAVY)
    for i, r in enumerate([r for r in rows if t >= r[0]]):
        k = ease((t - r[0]) / .22); y = 86 * u + i * rh + (1 - k) * 10 * u
        row = Image.new("RGBA", im.size, (0, 0, 0, 0)); rd = ImageDraw.Draw(row)
        kind = r[3] if len(r) > 3 else "check"
        if kind == "check": icon_check(rd, 52 * u, y + 30 * u, 19 * u, ACC)
        elif kind == "cross": icon_cross(rd, 52 * u, y + 30 * u, 19 * u, (200, 60, 60))
        elif kind == "q": rd.ellipse((33 * u, y + 11 * u, 71 * u, y + 49 * u), fill=NAVY); rd.text((52 * u, y + 30 * u), "?", font=font("Bold", 26), fill=WHITE, anchor="mm")
        if r[1]: rd.text((86 * u, y + 2 * u), r[1], font=fL, fill=(110, 116, 140))
        rd.text((86 * u, y + (28 if r[1] else 14) * u), r[2], font=fR, fill=INK)
        if kind == "cross":
            tw = text_w(rd, r[2], fR); yy = y + (28 if r[1] else 14) * u + 28 * u
            rd.line([(86 * u, yy), (86 * u + tw * min(1, (t - r[0]) / .35), yy)], fill=(200, 60, 60), width=int(5 * u))
        if i < n - 1: rd.line([(36 * u, y + rh - 6 * u), (cw - 16 * u, y + rh - 6 * u)], fill=GREY, width=max(1, int(2 * u)))
        paste(im, row, 0, 0, k)
    return im, a

def _t(x): return END0 + float(x[3:] or 0) if isinstance(x, str) else x  # "END", "END+0.2"
GFX = [(_t(a), _t(b), k, d) for a, b, k, d in CFG["gfx"]]  # masa output
SFX = [(_t(t), n, g) for t, n, g in CFG["sfx"]]

def draw_label(im, t, t0, t1, s):
    a = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    if a <= 0: return
    f = font("SemiBold", 30); d = ImageDraw.Draw(im); tw = text_w(d, s, f)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); x = 0.06 * W - (1 - ease((t - t0) / .3)) * 30 * u; y = 0.115 * H
    rrect(lay, (x, y, x + tw + 64 * u, y + 58 * u), 29 * u, (*NAVY, 235))
    ld = ImageDraw.Draw(lay); ld.ellipse((x + 20 * u, y + 22 * u, x + 34 * u, y + 36 * u), fill=ACC)
    ld.text((x + 44 * u, y + 29 * u), s, font=f, fill=WHITE, anchor="lm"); paste(im, lay, 0, 0, a)

def draw_chip(im, t, t0, t1, s):
    a = ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25))
    if a <= 0: return
    f = font("Bold", 38); d = ImageDraw.Draw(im); tw = text_w(d, s, f)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); x = 0.06 * W; y = 0.44 * H + (1 - ease((t - t0) / .25)) * 16 * u
    rrect(lay, (x, y, x + tw + 120 * u, y + 84 * u), 42 * u, (255, 255, 255, 246)); ld = ImageDraw.Draw(lay)
    # ikon ulang (anak panah bulat)
    cx, cy, r = x + 50 * u, y + 42 * u, 20 * u; ang = (t - t0) * 2.5
    ld.arc((cx - r, cy - r, cx + r, cy + r), math.degrees(ang) % 360, (math.degrees(ang) + 290) % 360, fill=ACC, width=int(6 * u))
    ex = cx + r * math.cos(ang + math.radians(290)); ey = cy + r * math.sin(ang + math.radians(290))
    ld.ellipse((ex - 7 * u, ey - 7 * u, ex + 7 * u, ey + 7 * u), fill=ACC)
    ld.text((x + 88 * u, y + 42 * u), s, font=f, fill=NAVY, anchor="lm"); paste(im, lay, 0, 0, a)

def draw_callout(im, t, t0, t1, s):
    a = ease((t - t0) / .25) * (1 - ease((t - t1 + .2) / .2))
    if a <= 0: return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    # bulatan sorotan pada lajur Status (anggaran kedudukan dalam B-roll)
    k = ease((t - t0) / .45); cx, cy = 0.465 * W, 0.50 * H; rx, ry = 105 * u * k, 520 * u * k
    ld.rounded_rectangle((cx - rx, cy - ry, cx + rx, cy + ry), 40 * u, outline=ACC, width=int(7 * u))
    f = font("ExtraBold", 54); tw = text_w(ld, s, f); x = 0.06 * W; y = 0.10 * H
    rrect(lay, (x, y, x + tw + 60 * u, y + 96 * u), 24 * u, (*NAVY, 245)); ld = ImageDraw.Draw(lay)
    ld.text((x + 30 * u, y + 48 * u), s, font=f, fill=WHITE, anchor="lm"); paste(im, lay, 0, 0, a)

def draw_timebar(im, t, t0, t1):
    a = ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25))
    if a <= 0: return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); x, y, cw, chh = 0.06 * W, 0.40 * H, 0.70 * W, 200 * u
    rrect(lay, (x, y, x + cw, y + chh), 28 * u, (255, 255, 255, 246)); ld = ImageDraw.Draw(lay)
    icon_clock(ld, x + 58 * u, y + 56 * u, 24 * u, NAVY, ang=(t - t0) * 1.2)
    ld.text((x + 98 * u, y + 56 * u), "Waktu mengajar", font=font("Bold", 36), fill=INK, anchor="lm")
    bx0, bx1, by = x + 34 * u, x + cw - 34 * u, y + 112 * u
    ld.rounded_rectangle((bx0, by, bx1, by + 40 * u), 20 * u, fill=GREY)
    k = ease((t - t0 - .3) / 1.6); split = bx1 - (bx1 - bx0) * 0.62 * k
    ld.rounded_rectangle((bx0, by, max(bx0 + 40 * u, split), by + 40 * u), 20 * u, fill=NAVY)
    if k > .05:
        ld.rounded_rectangle((split - 20 * u, by, bx1, by + 40 * u), 20 * u, fill=ACC)
        ld.text((bx1, by + 62 * u), "dicuri kerja admin", font=font("SemiBold", 26), fill=(0, 120, 170), anchor="rm")
    paste(im, lay, 0, 0, a)

def draw_comment(im, t, t0, t1):
    a = ease((t - t0) / .25) * (1 - ease((t - t1 + .2) / .2))
    if a <= 0: return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); x, y = 0.06 * W, 0.42 * H + (1 - ease((t - t0) / .3)) * 18 * u
    f1, f2 = font("Bold", 40), font("SemiBold", 28); cw = 0.62 * W
    rrect(lay, (x, y, x + cw, y + 150 * u), 30 * u, (255, 255, 255, 248)); ld = ImageDraw.Draw(lay)
    ld.polygon([(x + 60 * u, y + 148 * u), (x + 110 * u, y + 148 * u), (x + 56 * u, y + 196 * u)], fill=(255, 255, 255, 248))
    ld.text((x + 34 * u, y + 30 * u), "Setuju atau tak setuju?", font=f1, fill=NAVY)
    ld.text((x + 34 * u, y + 92 * u), "Kongsi pendapat di ruang komen", font=f2, fill=(90, 96, 120))
    paste(im, lay, 0, 0, a)

def pile_frame(t, t0, dur):
    """B-roll animasi sendiri (berlesen, dijana skrip ini): resit & rekod bertimbun, jam berpusing laju."""
    tt = t - t0
    im = Image.new("RGBA", (W, H), (*NAVY, 255)); d = ImageDraw.Draw(im)
    for i in range(0, H, max(1, int(8 * u))):  # gradien lembut
        c = int(18 * i / H); d.rectangle((0, i, W, i + 8 * u), fill=(NAVY[0] - c // 2, NAVY[1] - c // 2, NAVY[2] - c, 255))
    d.rounded_rectangle((W * .12, H * .585, W * .88, H * .600), 8 * u, fill=(255, 255, 255, 90))  # meja
    labels = ["RESIT", "REKOD YURAN", "RESIT", "SENARAI BAYARAN", "RESIT", "REKOD YURAN", "INVOIS", "RESIT"]
    rng = np.random.default_rng(5)
    for i, lab in enumerate(labels):
        st = 0.08 + i * 0.27
        if tt < st: break
        k = ease((tt - st) / .35); rot = rng.uniform(-9, 9); dx = rng.uniform(-60, 60) * u
        pw, ph = 420 * u, 140 * u
        card = Image.new("RGBA", (int(pw), int(ph)), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, pw - 1, ph - 1), 14 * u, fill=(255, 255, 255, 255))
        cd.rectangle((0, 0, 14 * u, ph), fill=ACC if i % 2 == 0 else NAVY)
        cd.text((34 * u, 22 * u), lab, font=font("Bold", 34), fill=NAVY)
        for j in range(2): cd.rounded_rectangle((34 * u, (76 + j * 28) * u, (330 - j * 90) * u, (88 + j * 28) * u), 6 * u, fill=GREY)
        card = card.rotate(rot, expand=True, resample=Image.BICUBIC)
        yy = H * .585 - (i + 1) * 58 * u - card.size[1] * .45
        yy = yy - (1 - k) * H * .35
        paste(im, card, W * .5 - card.size[0] / 2 + dx, yy, min(1, k * 1.6))
    d = ImageDraw.Draw(im); cy = H * .17  # jam di atas timbunan, berpusing laju
    d.ellipse((W * .5 - 118 * u, cy - 118 * u, W * .5 + 118 * u, cy + 118 * u), fill=(*NAVY, 255))
    icon_clock(d, W * .5, cy, 105 * u, WHITE, ang=tt * 2.4, w=int(12 * u))
    for k in range(12):  # tanda jam
        a_ = k * math.pi / 6; d.line([(W * .5 + 82 * u * math.sin(a_), cy - 82 * u * math.cos(a_)),
                                      (W * .5 + 94 * u * math.sin(a_), cy - 94 * u * math.cos(a_))], fill=ACC, width=int(5 * u))
    a = ease(tt / .2) * (1 - ease((tt - dur + .2) / .2))
    return im, a

def end_card(t):
    tt = t - END0
    im = Image.new("RGBA", (W, H), (*NAVY, 255)); d = ImageDraw.Draw(im)
    logo = Image.open(P("brand/logo_white.png")).convert("RGBA"); logo = logo.crop(logo.getbbox())
    lw = int(470 * u); logo = logo.resize((lw, int(logo.size[1] * lw / logo.size[0])), Image.LANCZOS)
    k = ease(tt / .35)
    paste(im, logo, W * .46 - lw / 2, H * .28 + (1 - k) * 20 * u, k)
    f = font("ExtraBold", 64); y = H * .28 + logo.size[1] + 90 * u; parts = [("Cara ", WHITE), ("MUDAH", ACC), (" Urus Yuran", WHITE)]
    tw = sum(text_w(d, s, f) for s, _ in parts); x = W * .46 - tw / 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for s, c in parts: ld.text((x, y), s, font=f, fill=c); x += text_w(ld, s, f)
    f2 = font("Bold", 38); s2 = "Follow untuk tips urus yuran sekolah"; tw2 = text_w(ld, s2, f2)
    y2 = y + 150 * u; ld.rounded_rectangle((W * .46 - tw2 / 2 - 40 * u, y2, W * .46 + tw2 / 2 + 40 * u, y2 + 92 * u), 46 * u, fill=WHITE)
    ld.text((W * .46, y2 + 46 * u), s2, font=f2, fill=NAVY, anchor="mm")
    ld.text((W * .46, y2 + 190 * u), "hello@yuran.my", font=font("SemiBold", 44), fill=WHITE, anchor="mm")
    paste(im, lay, 0, 0, ease((tt - .15) / .35))
    return im

def thumb_overlay(base):
    im = base.copy(); g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(int(H * .40), H):
        a = min(1, (i - H * .40) / (H * .22)); gd.line([(0, i), (W, i)], fill=(20, 28, 80, int(215 * a)))
    im.alpha_composite(g); d = ImageDraw.Draw(im); cx = W * .46
    f1, f2, f3 = font("ExtraBold", 132), font("Bold", 64), font("ExtraBold", 160)
    st = dict(stroke_width=int(6 * u), stroke_fill=(15, 20, 55))
    d.text((cx, H * .535), "CIKGU KAFA", font=f1, fill=WHITE, anchor="mm", **st)
    d.text((cx, H * .615), "atau", font=f2, fill=WHITE, anchor="mm", **st)
    d.text((cx, H * .700), "KERANI?", font=f3, fill=ACC, anchor="mm", **st)
    return im

# ---------------- render ----------------
if __name__ == "__main__":
    tmp = P("edit", f"tmp{W}"); os.makedirs(tmp, exist_ok=True)
    build_content(f"{tmp}/content.mp4")
    BR = [g for g in GFX if g[2] == "broll"][0]; build_broll(f"{tmp}/broll.mp4", BR[1] - BR[0] + .1)
    grab(CFG["thumb_t"], PUNCH, f"{tmp}/thumbsrc.png")
    thumb = thumb_overlay(Image.open(f"{tmp}/thumbsrc.png").convert("RGBA"))
    thumb.convert("RGB").save(f"{tmp}/thumb.png")
    rd = lambda p: subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    cv, bv = rd(f"{tmp}/content.mp4"), rd(f"{tmp}/broll.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", f"{tmp}/video.mp4"], stdin=subprocess.PIPE)
    fb = W * H * 3; last = None; bframe = None
    for n in range(int(round(DUR * FPS))):
        t = n / FPS
        if t < TH: enc.stdin.write(thumb.convert("RGB").tobytes()); continue
        if t >= END0: enc.stdin.write(end_card(t).convert("RGB").tobytes()); continue
        raw = cv.stdout.read(fb); last = raw if len(raw) == fb else last
        im = Image.frombytes("RGB", (W, H), last).convert("RGBA")
        for t0, t1, kind, data in GFX:
            if kind == "broll" and t0 <= t < t1:
                raw = bv.stdout.read(fb); bframe = raw if len(raw) == fb else bframe
                a = ease((t - t0) / .15) * (1 - ease((t - t1 + .15) / .15))
                paste(im, Image.frombytes("RGB", (W, H), bframe).convert("RGBA"), 0, 0, a)
            elif kind == "pile" and t0 <= t < t1:
                p, a = pile_frame(t, t0, t1 - t0); paste(im, p, 0, 0, a)
        for t0, t1, kind, data in GFX:
            if not (t0 <= t < t1): continue
            if kind == "label": draw_label(im, t, t0, t1, data)
            elif kind == "rows":
                r = card_rows(data[0], data[1], t, t0, t1)
                if r: paste(im, r[0], 0.06 * W - 10 * u, 0.385 * H, r[1])
            elif kind == "chip": draw_chip(im, t, t0, t1, data)
            elif kind == "callout": draw_callout(im, t, t0, t1, data)
            elif kind == "timebar": draw_timebar(im, t, t0, t1)
            elif kind == "comment": draw_comment(im, t, t0, t1)
        draw_caption(im, t)
        enc.stdin.write(im.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait(); cv.kill(); bv.kill()
    json.dump({"dur": DUR, "end0": END0, "caps": CAPS, "gfx": [list(g[:3]) for g in GFX], "sfx": SFX,
               "zoom": ZOOM, "edl": EDL}, open(f"{tmp}/meta.json", "w"), ensure_ascii=False, indent=1)
    # ---------------- audio ----------------
    # fade 10 ms hanya pada potongan sebenar; segmen bersambung (tukar zoom sahaja) tidak di-fade
    cut_in = lambda i: i == 0 or abs(EDL[i - 1][1] - EDL[i][0]) > 1e-3
    cut_out = lambda i: i == len(EDL) - 1 or abs(EDL[i + 1][0] - EDL[i][1]) > 1e-3
    fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS" + (",afade=t=in:d=0.01" if cut_in(i) else "")
                 + (f",afade=t=out:st={b - a - 0.012}:d=0.012" if cut_out(i) else "") + f"[a{i}];" for i, (a, b) in enumerate(EDL))
    fc += "".join(f"[a{i}]" for i in range(len(EDL))) + f"concat=n={len(EDL)}:v=0:a=1,aresample=48000,pan=stereo|c0=c0|c1=c0,"
    fc += "highpass=f=80,afftdn=nr=8:nf=-42,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=160:makeup=2," \
          f"adelay={int(TH * 1000)}:all=1,apad=pad_dur=4[voice];[voice]asplit[v1][vsc];"
    fc += f"[1:a]aresample=48000,volume=-23dB,atrim=0:{DUR}[mu];[mu][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[mud];"
    ins = ["-i", SRC, "-i", P("audio/music.wav")]; mix = ["[v1]", "[mud]"]
    for j, (t, name, g) in enumerate(SFX):
        ins += ["-i", P("audio", name + ".wav")]
        fc += f"[{j + 2}:a]aresample=48000,volume={g * 0.5:.3f},adelay={int(t * 1000)}:all=1[s{j}];"; mix.append(f"[s{j}]")
    fc += "".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,asetpts=N/SR/TB,apad[mx]"
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[mx]", "-t", f"{DUR:.3f}", "-c:a", "pcm_s16le", f"{tmp}/mix.wav"])
    st = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{tmp}/mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                         "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(st[st.rfind("{"):])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/video.mp4", "-i", f"{tmp}/mix.wav", "-af", ln + ",aresample=48000",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT])
    print("ok", OUT, round(DUR, 2), "s")
