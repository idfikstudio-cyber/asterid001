# YM-F-010 versi melintang 16:9: python3 render_169.py <dl_dir> <out.mp4> [OW]   (OW=960 preview, 1920 final)
# Susunan: Farhan (video 9:16) di kiri, panel kanan untuk B-roll (bingkai telefon), kad grafik dan caption.
import sys, os, math, subprocess
DL, OUT = sys.argv[1], sys.argv[2]
OW = int(sys.argv[3]) if len(sys.argv) > 3 else 960
OH = OW * 9 // 16
S = OW / 1920
sys.argv = ["render.py", DL, OUT, "1080" if OW >= 1920 else "540"]
import render as R
from PIL import Image, ImageDraw, ImageFilter
R.body.close()
P, FPS, DUR, TH, BODY = R.P, R.FPS, R.DUR, R.TH, R.BODY
NAVY, ACC, WHITE, INK = R.NAVY, R.ACC, R.WHITE, R.INK
font, text_w, rr, ease, pop = R.font, R.text_w, R.rr, R.ease, R.pop
s = lambda v: v * S

# geometri (dalam piksel 1920x1080, darab S)
FX, FY, FW, FH = s(84), s(24), round(s(582)), round(s(1032))   # panel Farhan 9:16
PX0, PX1 = s(760), s(1860); PCX = (PX0 + PX1) / 2                # panel kanan
PH_W, PH_H = round(s(450)), round(s(800)); PH_Y = s(48)          # skrin telefon B-roll
GV_W, GV_H = round(s(1080)), round(s(1920))                      # kanvas maya grafik potret
BAND = (0.04, 0.36, 0.88, 0.76)                                  # jalur grafik (x0,y0,x1,y1) dari kanvas maya                                              # jalur grafik yang diambil dari kanvas maya

def size(w, h): R.W, R.H = w, h

def background():
    im = Image.new("RGBA", (OW, OH), NAVY + (255,))
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((s(1500), s(-420), s(2300), s(380)), fill=ACC + (34,))
    d.ellipse((s(620), s(760), s(1180), s(1320)), fill=ACC + (22,))
    im.alpha_composite(lay)
    return im
BG = background()

MASK = Image.new("L", (FW, FH), 0); ImageDraw.Draw(MASK).rounded_rectangle((0, 0, FW - 1, FH - 1), radius=round(s(30)), fill=255)
SHADOW = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW).rounded_rectangle((FX + s(6), FY + s(14), FX + FW + s(6), FY + FH + s(14)), radius=round(s(30)), fill=(5, 10, 40, 110))
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(s(14)))

def paste_farhan(cv, fr):
    cv.alpha_composite(SHADOW)
    cv.paste(fr.resize((FW, FH), Image.LANCZOS) if fr.size != (FW, FH) else fr, (round(FX), round(FY)), MASK)

def phone(cv, scr, a):
    if a <= 0: return
    sc = 0.94 + 0.06 * a
    w, h = round(PH_W * sc), round(PH_H * sc); b = s(14)
    x = PCX - w / 2; y = PH_Y + (PH_H - h) / 2
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rr(d, (x - b + s(6), y - b + s(16), x + w + b + s(6), y + h + b + s(16)), s(46), fill=(5, 10, 40, int(110 * a)))
    lay = lay.filter(ImageFilter.GaussianBlur(s(12))); d = ImageDraw.Draw(lay)
    rr(d, (x - b, y - b, x + w + b, y + h + b), s(46), fill=(16, 18, 28, int(255 * a)))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=round(s(32)), fill=int(255 * a))
    lay.paste(scr.resize((w, h), Image.LANCZOS).convert("RGBA"), (round(x), round(y)), m)
    cv.alpha_composite(lay)

def graphics_band(t):
    """Lukis kad grafik (kecuali label) pada kanvas potret maya, pulangkan jalur tengahnya."""
    act = [g for g in P["g"] if g["s"] <= t < g["e"] and g["k"] != "label"]
    if not act: return None
    size(GV_W, GV_H); R.NAVY = ACC   # kepala kad biru aksen supaya timbul atas latar navy
    lay = Image.new("RGBA", (GV_W, GV_H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for g in act: R.GF[g["k"]](d, lay, g, t)
    R.NAVY = NAVY
    return lay.crop((round(GV_W * BAND[0]), round(GV_H * BAND[1]), round(GV_W * BAND[2]), round(GV_H * BAND[3])))

def label(cv, t, g):
    a = ease((t - g["s"]) / 0.25) * (1 - ease((t - (g["e"] - 0.25)) / 0.25))
    if a <= 0: return
    d = ImageDraw.Draw(cv); f = font("SemiBold", s(30)); txt = "Farhan · Yuran.my"; tw = text_w(f, txt)
    x, y = FX + s(28), FY + FH - s(96) + s(10) * (1 - a)
    rr(d, (x, y, x + tw + s(52), y + s(62)), s(31), fill=NAVY + (int(240 * a),))
    d.text((x + s(26), y + s(31)), txt, font=f, fill=WHITE + (int(255 * a),), anchor="lm")

def tag(cv, txt, a):
    d = ImageDraw.Draw(cv); f = font("SemiBold", s(26)); tw = text_w(f, txt)
    x = PCX + PH_W / 2 + s(34); y = PH_Y + s(30)
    rr(d, (x, y, x + tw + s(44), y + s(54)), s(27), fill=ACC + (int(255 * a),))
    d.text((x + s(22), y + s(27)), txt, font=f, fill=WHITE + (int(255 * a),), anchor="lm")

def wrap(f, words, maxw):
    lines, cur = [], []
    for w in words:
        test = cur + [w]
        if cur and text_w(f, " ".join(x["t"] for x in test)) > maxw: lines.append(cur); cur = [w]
        else: cur = test
    if cur: lines.append(cur)
    return lines

def caption(cv, t, busy):
    c = next((c for c in P["caps"] if c["s"] <= t < c["e"]), None)
    if not c: return
    d = ImageDraw.Draw(cv)
    size_px = s(62) + (s(104) - s(62)) * (1 - busy)
    cy = s(985) + (s(520) - s(985)) * (1 - busy)
    f = font("ExtraBold", size_px)
    lines = wrap(f, c["w"], PX1 - PX0 - s(60))
    lh = size_px * 1.15; y0 = cy - lh * (len(lines) - 1) / 2
    sc = min(1.0, pop(t, c["s"], 0.12)); dy = (1 - sc) * s(14)
    for i, ln in enumerate(lines):
        tw = sum(text_w(f, w["t"]) for w in ln) + text_w(f, " ") * (len(ln) - 1)
        x = PCX - tw / 2; y = y0 + i * lh + dy
        for w in ln:
            col = ACC if w["hl"] else WHITE
            d.text((x + s(3), y + s(4)), w["t"], font=f, fill=(8, 12, 40, 150), anchor="lm")
            d.text((x, y), w["t"], font=f, fill=col + (255,), anchor="lm")
            x += text_w(f, w["t"] + " ")

def busy_at(t):
    a = 0.0
    for b in P["br"]: a = max(a, min(1, (t - b["s"] + 0.25) / 0.25, (b["e"] + 0.25 - t) / 0.25))
    for g in P["g"]:
        if g["k"] == "label": continue
        a = max(a, min(1, (t - g["s"] + 0.25) / 0.25, (g["e"] + 0.25 - t) / 0.25))
    return max(0.0, min(1.0, a))

def make_thumb(face):
    cv = BG.copy(); paste_farhan(cv, face); d = ImageDraw.Draw(cv)
    x = PX0 + s(40); y = s(250)
    for txt, sz, box in [("ANDA PERLUKAN", 92, None), ("SISTEM", 190, None), ("MACAM MANA?", 118, ACC)]:
        f = font("Black", s(sz)); asc, _ = f.getmetrics(); hh = asc * 0.78
        if box:
            tw = text_w(f, txt)
            rr(d, (x, y, x + tw + s(56), y + hh + s(56)), s(22), fill=box + (255,))
            d.text((x + s(28), y + s(28) + hh), txt, font=f, fill=WHITE, anchor="ls"); y += hh + s(76)
        else:
            d.text((x, y + hh), txt, font=f, fill=WHITE, anchor="ls"); y += hh + s(34)
    return cv.convert("RGB")

def make_end():
    cv = BG.copy(); d = ImageDraw.Draw(cv)
    R.paste_logo(cv, OW / 2, s(330), s(520), 1.0)
    f = font("ExtraBold", s(76)); parts = [("Cara ", WHITE), ("MUDAH", ACC), (" Urus Yuran", WHITE)]
    tw = sum(text_w(f, p) for p, _ in parts); x = OW / 2 - tw / 2
    for p, c in parts: d.text((x, s(560)), p, font=f, fill=c, anchor="lm"); x += text_w(f, p)
    f2 = font("SemiBold", s(42)); txt = "Follow untuk tips urus yuran sekolah"; tw = text_w(f2, txt)
    rr(d, (OW / 2 - tw / 2 - s(48), s(660), OW / 2 + tw / 2 + s(48), s(760)), s(50), outline=WHITE, width=max(2, round(s(4))))
    d.text((OW / 2, s(710)), txt, font=f2, fill=WHITE, anchor="mm")
    d.text((OW / 2, s(850)), "hello@yuran.my", font=font("Medium", s(44)), fill=(210, 220, 245), anchor="mm")
    return cv.convert("RGB")

def main():
    RAW = R.RAW
    face = R.Reader(["-ss", str(P["thumb_src"]), "-i", RAW, "-frames:v", "1", "-vf", f"{R.GRADE},scale={FW}:{FH}:flags=lanczos"], FW, FH)
    thumb = make_thumb(R.zoom_img(face.read(), 1.04, 0.5, 0.22)); face.close(); end = make_end()
    thumb.save(OUT.replace(".mp4", "_THUMB.png"))
    body = R.Reader(["-i", RAW, "-vf", f"select='not(between(t,{R.C0},{R.C1}))',setpts=N/{FPS}/TB,fps={FPS},{R.GRADE},scale={FW}:{FH}:flags=lanczos"], FW, FH)
    tmpv = OUT + ".v.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19" if OW >= 1920 else "22", "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    N = round(DUR * FPS); nb = round(BODY * FPS); bi = 0; act = {}; prev = None
    lab = next(g for g in P["g"] if g["k"] == "label")
    for i in range(N):
        t = i / FPS
        if t < TH: fr = thumb
        elif bi < nb:
            bf = body.read(); bi += 1
            cv = BG.copy(); paste_farhan(cv, R.zoom_img(bf, R.zoom_at(t)))
            label(cv, t, lab)
            band = graphics_band(t)
            if band is not None:
                bw = PX1 - PX0; sc = min(bw / band.width, s(880) / band.height)
                bb = band.resize((round(band.width * sc), round(band.height * sc)), Image.LANCZOS)
                cv.alpha_composite(bb, (round(PCX - bb.width / 2), round(s(470) - bb.height / 2)))
            for b in P["br"]:
                if b["s"] <= t < b["e"]:
                    if b["id"] not in act:
                        size(PH_W, PH_H); act[b["id"]] = R.Broll(dict(b, label=None))
                    size(PH_W, PH_H); scr = act[b["id"]].frame(t)
                    a = ease(min(1, (t - b["s"]) / 0.2, (b["e"] - t) / 0.2))
                    phone(cv, scr, a)
                    if b.get("label"): tag(cv, b["label"], a)
                elif b["id"] in act and t >= b["e"]:
                    act.pop(b["id"]).r.close()
            caption(cv, t, busy_at(t))
            fr = cv.convert("RGB"); prev = fr
        else:
            lt = t - (TH + BODY)
            fr = Image.blend(prev, end, ease(lt / 0.25)) if lt < 0.25 and prev else end
        enc.stdin.write(fr.tobytes())
        if i % 150 == 0: print(f"{t:5.1f}/{DUR}", flush=True)
    enc.stdin.close(); enc.wait(); body.close()
    R.audio(OUT + ".a.m4a")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", OUT + ".a.m4a", "-c", "copy", "-movflags", "+faststart", "-shortest", OUT], check=True)
    os.remove(tmpv); os.remove(OUT + ".a.m4a")

if __name__ == "__main__":
    main()
