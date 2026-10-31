# Render Yuran.my YM-F-004 (TOFU "Paling berat bagi guru KAFA").
# usage: python3 ym_render.py <src.mp4> <jais.png> <logo_white.png> <sfxdir> <outdir> <W> [crf]
# W=540 -> preview 540x960, W=1080 -> final 1080x1920.
import json, subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, JAIS, LOGO, SFX, OUT = sys.argv[1:6]
W = int(sys.argv[6]); H = W * 16 // 9; CRF = sys.argv[7] if len(sys.argv) > 7 else "20"
S = W / 1080  # skala reka bentuk (semua ukuran ditulis untuk 1080)
FPS = 30
ID = "YM-F-004_Paling_berat_bagi_guru_KAFA"
TAG = "PREVIEW" if W < 1080 else "FINAL"
os.makedirs(OUT, exist_ok=True)

BLUE, ACC, BLACK, GREY, WHITE = "#2A3B8F", "#29ABE2", "#231F20", "#E7E8E9", "#FFFFFF"
FD = "/usr/share/fonts/opentype/inter/"
def F(w, px): return ImageFont.truetype(FD + {"xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], max(8, int(px * S)))

SRC_DUR = 24.17
THUMB = 1.0            # thumbnail statik
OFF = THUMB            # masa video asal + OFF = masa timeline
END = 1.5              # end card
BODY_END = OFF + SRC_DUR
TOTAL = BODY_END + END
NF = int(round(TOTAL * FPS))

# ---------- caption (masa video asal, ikut percakapan) ----------
CAP = [
 (0.00, 0.92, "Paling *berat*"), (0.92, 2.26, "jadi cikgu KAFA ni"), (2.26, 3.54, "bukan mengajar."),
 (3.56, 4.94, "Bukan tanda buku"), (4.94, 6.22, "tapi nak"), (6.22, 7.30, "remind pasal *yuran.*"),
 (7.34, 8.22, "Depan ibu bapa,"), (8.34, 9.20, "*segan.*"),
 (9.26, 10.82, "Nak cakap dekat murid,"), (10.82, 11.46, "suruh cakap"), (11.46, 12.68, "dekat ibu ayah,"),
 (12.68, 13.86, "*takut* dia lupa"), (13.86, 14.74, "nak remindkan."),
 (14.88, 15.82, "Rasa *segan.*"), (15.98, 16.88, "Nak cakap pun"), (16.88, 18.02, "rasa tak sampai hati."),
 (18.04, 19.26, "Tapi duit sekolah ni"), (19.26, 19.72, "kena collect."),
 (19.90, 20.50, "Nanti *JAIS*"), (20.50, 20.90, "mintak *report.*"),
 (21.12, 21.50, "*Pernah* rasa"), (21.50, 22.10, "macam ni tak?"),
 (22.22, 22.74, "Komen *\"pernah\"*"), (22.74, 24.02, "kalau pernah alami."),
]
# punch-in ikut ayat (tiada potongan; footage sudah ditrim)
ZOOM = [(0.00, 1.00), (3.55, 1.12), (7.32, 1.15), (9.23, 1.00), (14.80, 1.12), (18.03, 1.00), (21.01, 1.12), (22.16, 1.00)]
JAIS_IN, JAIS_OUT = 20.12, 21.45          # "Nanti JAIS mintak report"
CMT_IN = 22.05                            # panel komen naik
TYPE_A, TYPE_B, SEND = 22.40, 22.95, 23.10
LABEL_IN, LABEL_OUT = 0.25, 3.25          # "Farhan · Yuran.my"
THUMB_SRC_T = 5.0

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
    y = H * (0.545 if t >= CMT_IN else 0.715 if JAIS_IN - 0.3 <= t < JAIS_OUT else 0.64)
    draw_rich(base, CX, y + (1 - k) * 18 * S, s, CAP_FONT, sc=0.9 + 0.1 * k, alpha=k)

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

# ---------- logo JAIS ----------
_j = Image.open(JAIS).convert("RGBA")
def jais(base, t):
    if not (JAIS_IN <= t < JAIS_OUT): return
    kin = back((t - JAIS_IN) / 0.32); kout = 1 - ease((t - (JAIS_OUT - 0.22)) / 0.22)
    sc = max(0.01, kin * (0.85 + 0.15 * kout)); a = min(1, (t - JAIS_IN) / 0.12) * kout
    cw = int(300 * S); pad = int(16 * S)
    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, cw - 1, cw - 1), radius=int(36 * S), fill=WHITE, outline=ACC, width=max(2, int(6 * S)))
    card.alpha_composite(_j.resize((cw - 2 * pad, cw - 2 * pad), Image.LANCZOS), (pad, pad))
    sh = Image.new("RGBA", (cw + 80, cw + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 48, cw + 40, cw + 48), radius=int(36 * S), fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(14 * S)); sh.alpha_composite(card, (40, 40))
    sh = sh.resize((max(1, int(sh.width * sc)), max(1, int(sh.height * sc))), Image.LANCZOS)
    sh.putalpha(sh.getchannel("A").point(lambda v: int(v * a)))
    base.alpha_composite(sh, (int(W * 0.46 - sh.width / 2), int(H * 0.57 - sh.height / 2)))

# ---------- motion komen (panel komen gaya TikTok) ----------
def heart(d, cx, cy, r, fill):
    d.ellipse((cx - r, cy - r * 0.9, cx, cy + r * 0.1), fill=fill); d.ellipse((cx, cy - r * 0.9, cx + r, cy + r * 0.1), fill=fill)
    d.polygon([(cx - r * 0.97, cy - r * 0.25), (cx + r * 0.97, cy - r * 0.25), (cx, cy + r)], fill=fill)
def comments(base, t):
    if t < CMT_IN: return
    k = ease((t - CMT_IN) / 0.35)
    pw, ph = int(W * 0.78), int(H * 0.21)
    x0 = int(W * 0.46 - pw / 2); y0 = int(H * 0.585 + (1 - k) * H * 0.12)
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = int(34 * S)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=r, fill=(255, 255, 255, 245))
    fh, fn, fu, fs = F("b", 34), F("m", 34), F("sb", 28), F("m", 24)
    d.text((pw // 2, int(44 * S)), "Komen", font=fh, fill=BLACK, anchor="mm")
    d.line((int(30 * S), int(84 * S), pw - int(30 * S), int(84 * S)), fill=GREY, width=max(1, int(2 * S)))
    # komen baru muncul selepas hantar
    if t >= SEND:
        kc = ease((t - SEND) / 0.25)
        cy = int(140 * S + (1 - kc) * 24 * S)
        av = int(64 * S); ax = int(36 * S)
        d.ellipse((ax, cy - av // 2, ax + av, cy + av // 2), fill=BLUE)
        d.text((ax + av // 2, cy), "A", font=F("b", 30), fill=WHITE, anchor="mm")
        tx = ax + av + int(22 * S)
        d.text((tx, cy - int(18 * S)), "anda  ·  baru sahaja", font=fs, fill="#7A7C80", anchor="lm")
        d.text((tx, cy + int(18 * S)), "Pernah", font=fn, fill=BLACK, anchor="lm")
        hp = 1 + 0.35 * math.sin(min(1, max(0, (t - SEND - 0.35) / 0.3)) * math.pi)
        hc = ACC if t >= SEND + 0.35 else "#B9BBBF"
        heart(d, pw - int(70 * S), cy, int(17 * S * hp), hc)
    # kotak tulis komen
    by = ph - int(96 * S); bh = int(70 * S)
    d.rounded_rectangle((int(30 * S), by, pw - int(120 * S), by + bh), radius=bh // 2, fill=GREY)
    n = int(len("pernah") * min(1, max(0, (t - TYPE_A) / (TYPE_B - TYPE_A)))) if t < SEND else 0
    typed = "pernah"[:n]
    if typed:
        d.text((int(60 * S), by + bh // 2), typed, font=fn, fill=BLACK, anchor="lm")
        cxp = int(60 * S) + d.textlength(typed, font=fn) + int(4 * S)
    else:
        d.text((int(60 * S), by + bh // 2), "Tambah komen...", font=fn, fill="#8D8F93", anchor="lm"); cxp = int(58 * S)
    if TYPE_A - 0.1 <= t < SEND and int(t * 4) % 2 == 0:
        d.line((cxp, by + int(18 * S), cxp, by + bh - int(18 * S)), fill=ACC, width=max(2, int(3 * S)))
    # butang hantar
    bx = pw - int(62 * S); bcy = by + bh // 2
    press = 1 - 0.18 * math.sin(min(1, max(0, (t - SEND + 0.08) / 0.18)) * math.pi)
    br = int(36 * S * press)
    d.ellipse((bx - br, bcy - br, bx + br, bcy + br), fill=ACC if n or t >= SEND else "#B9BBBF")
    a = int(15 * S * press)
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
    f = F("xb", 120)
    draw_rich(im, CX, H * 0.50, "Paling *berat*", f, stroke=9)
    draw_rich(im, CX, H * 0.585, "jadi cikgu", f, stroke=9)
    # KAFA dalam kotak biru aksen
    d = ImageDraw.Draw(im); fk = F("xb", 132)
    tw = d.textlength("KAFA", font=fk); bw, bh = int(tw + 70 * S), int(170 * S)
    bx, by = int(CX - bw / 2), int(H * 0.675 - bh / 2)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(26 * S), fill=ACC)
    d.text((CX, H * 0.675), "KAFA", font=fk, fill=WHITE, anchor="mm")
    return im

# ---------- end card ----------
_l = Image.open(LOGO).convert("RGBA")
def endcard(t):
    im = Image.new("RGBA", (W, H), BLUE); d = ImageDraw.Draw(im)
    lw = int(440 * S); lh = int(_l.height * lw / _l.width)
    k = ease(t / 0.35)
    im.alpha_composite(_l.resize((lw, lh), Image.LANCZOS), (int(W / 2 - lw / 2), int(H * 0.30 - lh / 2 + (1 - k) * 20 * S)))
    f1 = F("xb", 64); x = W / 2; y = H * 0.43
    p = [("Cara ", WHITE), ("MUDAH", ACC), (" Urus Yuran", WHITE)]
    tw = sum(d.textlength(s, font=f1) for s, _ in p); xx = x - tw / 2
    for s, c in p: d.text((xx, y), s, font=f1, fill=c, anchor="lm"); xx += d.textlength(s, font=f1)
    k2 = ease((t - 0.2) / 0.35)
    cta = "Follow untuk tips urus yuran sekolah"; f2 = F("sb", 40)
    cw = d.textlength(cta, font=f2) + 70 * S; chh = 84 * S; cy = H * 0.545 + (1 - k2) * 16 * S
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle((x - cw / 2, cy - chh / 2, x + cw / 2, cy + chh / 2), radius=int(chh / 2), fill=WHITE)
    od.text((x, cy), cta, font=f2, fill=BLUE, anchor="mm")
    od.text((x, H * 0.64), "hello@yuran.my", font=F("m", 40), fill=GREY, anchor="mm")
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
            label(im, t); jais(im, t); comments(im, t); caption(im, t)
            fade = ease((T - (BODY_END - 0.15)) / 0.15) if T > BODY_END - 0.15 else 0
            if fade: im = Image.blend(im, Image.new("RGBA", (W, H), BLUE), fade)
        else:
            im = endcard(T - BODY_END)
        enc.stdin.write(im.convert("RGB").tobytes())
        if i % 60 == 0: print(f"frame {i}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); rd.kill()
    return tmpv

# ---------- audio ----------
SFXL = [  # (masa timeline, fail, gain dB) — SFX lembut sahaja
    (OFF - 0.12, "whoosh.wav", -24), (OFF + JAIS_IN, "pop.wav", -16), (OFF + CMT_IN, "whoosh.wav", -24),
    (OFF + 22.48, "tick.wav", -26), (OFF + 22.66, "tick.wav", -26), (OFF + 22.84, "tick.wav", -26),
    (OFF + SEND - 0.04, "click.wav", -18), (OFF + SEND + 0.35, "pop.wav", -22), (BODY_END + 0.05, "ding.wav", -24),
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
    ins = ["-i", vo]; fl = []
    for n, (t, f, g) in enumerate(SFXL):
        ins += ["-i", os.path.join(SFX, f)]
        fl.append(f"[{n+1}]aresample=48000,volume={g}dB,adelay={int(t*1000)}:all=1[s{n}]")
    mix = "".join(f"[s{n}]" for n in range(len(SFXL)))
    fl.append(f"[0]{mix}amix=inputs={len(SFXL)+1}:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]")
    out = os.path.join(OUT, "_a.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[a]", "-t", f"{TOTAL:.3f}", out], check=True)
    return out

if __name__ == "__main__":
    v = render(); a = audio()
    dst = os.path.join(OUT, f"{ID}_{TAG}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", dst], check=True)
    os.remove(v)
    print("OK", dst)
