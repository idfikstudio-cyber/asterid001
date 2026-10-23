# Render Aster talking-head video: grade + punch-in + captions + pop-ups + whiteboard + watermark + end card.
# usage: python3 aster_render.py <plan.json> <src.mp4> <logo.png> <fonts_dir> <sfx_dir> <out.mp4> [preview|final] [thumb.png]
import json, math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

plan_p, src, logo_p, FD, SFXD, out = sys.argv[1:7]
mode = sys.argv[7] if len(sys.argv) > 7 else "preview"
thumb_out = sys.argv[8] if len(sys.argv) > 8 else None
P = json.load(open(plan_p))
W, H, FPS = 1080, 1920, 30
DARK, WHITE, ACC = (43, 51, 50), (255, 255, 255), (255, 200, 61)
SAFE_CX = 486                      # centre of area left of TikTok right-hand 15% strip
GRADE = open(os.path.join(os.path.dirname(__file__), "grade.sh")).read().split('GRADE_BASE="')[1].split('"')[0]
INTRO, OUTRO = P["intro"], P["outro"]
VDUR = P["src_duration"]
TOTAL = INTRO + VDUR + OUTRO
NF = int(round(TOTAL * FPS))

_fc = {}
def F(w, s):
    k = (w, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(os.path.join(FD, f"Poppins-{w}.ttf"), s)
    return _fc[k]

def ease_back(x):
    x = min(max(x, 0), 1); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

def shadowed(img, r=10, op=150, off=(0, 6)):
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(r)).point(lambda v: v * op // 255)
    pad = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh = Image.new("RGBA", img.size, (0, 0, 0, 255)); sh.putalpha(a)
    pad.alpha_composite(sh, off); pad.alpha_composite(img); return pad

def text_runs(runs, size, weight="ExtraBold", stroke=7, pad=40):
    """runs: [(text, colour)] on one line -> RGBA with dark outline + soft shadow"""
    f = F(weight, size); d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    ws = [d.textlength(t, font=f) for t, _ in runs]
    asc, desc = f.getmetrics()
    im = Image.new("RGBA", (int(sum(ws)) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    x = pad
    for (t, c), w in zip(runs, ws):
        dr.text((x, pad), t, font=f, fill=c, stroke_width=stroke, stroke_fill=(20, 22, 22)); x += w
    return shadowed(im)

def rrect(size, fill, r=34, outline=None, ow=0):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=fill, outline=outline, width=ow)
    return im

def tick_icon(sz, col=ACC):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, sz - 1, sz - 1], fill=col)
    d.line([(sz * .27, sz * .52), (sz * .44, sz * .69), (sz * .74, sz * .34)], fill=DARK, width=max(4, sz // 9), joint="curve")
    return im

def with_alpha(im, op):
    if op >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * op))); return im

def place(base, im, cx, cy, scale=1.0, op=1.0):
    if op <= 0.01 or scale <= 0.02: return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    im = with_alpha(im, op)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    base.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))

def pop_env(u, dur, inn=0.25, out_=0.18):
    """scale/opacity envelope for a pop-up living for dur seconds, u = local time"""
    if u < 0 or u > dur: return 0, 0
    sc = ease_back(u / inn) if u < inn else 1.0
    op = min(1, u / 0.08) * (1 if u < dur - out_ else max(0, (dur - u) / out_))
    return sc, op

# ---------- static assets ----------
HL = set(P["highlight"])
def is_hot(w):
    import re
    k = re.sub(r"[^\w&]", "", w)
    return k in HL or any(ch.isdigit() for ch in k)

cap_cache = {}
def caption_img(i):
    if i not in cap_cache:
        c = P["captions"][i]; runs = []
        for j, w in enumerate(c["words"]):
            runs.append((("" if j == 0 else " ") + w, ACC if is_hot(w) else WHITE))
        im = text_runs(runs, 74)
        if im.width > 840: im = im.resize((840, int(im.height * 840 / im.width)), Image.LANCZOS)
        cap_cache[i] = im
    return cap_cache[i]

def card_big(text, sub=None, sub_top=True, col=ACC, size=150):
    main = text_runs([(text, col)], size, "Black", stroke=9)
    if not sub: return main
    s = text_runs([(sub, WHITE)], 54, "ExtraBold", stroke=6)
    im = Image.new("RGBA", (max(main.width, s.width), main.height + s.height - 70), (0, 0, 0, 0))
    a, b = (s, main) if sub_top else (main, s)
    im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height - 70))
    return im

def chip(text, w=None):
    f = F("ExtraBold", 50); tw = int(ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f))
    t = tick_icon(62); w = w or tw + 150
    im = rrect((w, 96), DARK + (240,), 48, outline=ACC, ow=4); d = ImageDraw.Draw(im)
    im.alpha_composite(t, (20, 17)); d.text((98, 14), text, font=f, fill=WHITE)
    return shadowed(im, 12, 120)

wm = text_runs([(P["watermark"], WHITE)], 36, "SemiBold", stroke=2, pad=16)
wm = with_alpha(wm, 0.66)

def label_img():
    f1, f2 = F("Bold", 38), F("SemiBold", 38); d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    a, b = P["label"]; w1, w2 = d.textlength(a, font=f1), d.textlength(b, font=f2)
    im = rrect((int(w1 + w2) + 70, 74), DARK + (225,), 37); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, 10, 73], 5, fill=ACC)
    dr.text((34, 12), a, font=f1, fill=WHITE); dr.text((34 + w1, 12), b, font=f2, fill=ACC)
    return shadowed(im, 10, 110)
LABEL = label_img()

# whiteboard panel: dark board, yellow title, chalk-style items written in with a wipe
BW, BH = 840, 350
def board_base(title):
    im = rrect((BW, BH), DARK + (245,), 36, outline=(255, 255, 255, 60), ow=3); d = ImageDraw.Draw(im)
    d.text((40, 22), title, font=F("Black", 56), fill=ACC)
    d.line([(40, 98), (BW - 40, 98)], fill=(255, 255, 255, 70), width=3)
    return im
def board_item(text, big_first=False):
    f = F("Bold", 50); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    if big_first:
        fb = F("Black", 58); w0 = d0.textlength(text[0], font=fb); w = int(w0 + d0.textlength(text[1:], font=f)) + 10
        im = Image.new("RGBA", (w, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((0, 0), text[0], font=fb, fill=ACC); d.text((w0 + 2, 6), text[1:], font=f, fill=WHITE)
    else:
        w = int(d0.textlength(text, font=f)) + 10
        im = Image.new("RGBA", (w, 80), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 6), text, font=f, fill=WHITE)
    return im

BOARDS = []
for b in P["boards"]:
    items = [(it["t"], board_item(it["text"], b.get("big_first", False))) for it in b["items"]]
    BOARDS.append(dict(b, base=board_base(b["title"]), imgs=items))

def draw_board(base, b, u, dur, cy):
    sc, op = pop_env(u, dur, 0.22, 0.2)
    if op <= 0: return
    im = b["base"].copy(); cols = b.get("cols", 2); tk = tick_icon(48)
    for k, (t, it) in enumerate(b["imgs"]):
        lu = u - (t - b["s"])
        if lu < 0: continue
        r, c = b["items"][k].get("pos") or divmod(k, cols); x = 40 + c * ((BW - 60) // cols); y = 122 + r * 70
        p = ease_out(lu / 0.35); wv = int(it.width * p)
        if wv > 0: im.alpha_composite(it.crop((0, 0, wv, it.height)), (x + 62, y))
        if wv > 0 and p < 1:  # chalk/pen dot leading the stroke
            ImageDraw.Draw(im).ellipse([x + 62 + wv - 6, y + 36, x + 62 + wv + 6, y + 48], fill=ACC)
        ts = ease_back((lu - 0.15) / 0.2) if lu > 0.15 else 0
        if ts > 0: place(im, tk, x + 26, y + 42, ts)
    place(base, shadowed(im, 14, 140), SAFE_CX, cy + BH // 2 + 4, 0.92 + 0.08 * sc, op)

def warn_icon(sz=150):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, sz - 1, sz - 1], 30, fill=ACC)
    f = F("Black", int(sz * .72)); d.text((sz / 2, sz / 2 + 4), "!", font=f, fill=DARK, anchor="mm")
    return shadowed(im.rotate(8, resample=Image.BICUBIC, expand=True), 10, 120)

def dm_bubble():
    im = Image.new("RGBA", (330, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 329, 150], 40, fill=WHITE); d.polygon([(60, 140), (120, 140), (54, 188)], fill=WHITE)
    d.text((165, 76), "DM", font=F("Black", 84), fill=DARK, anchor="mm")
    return shadowed(im, 12, 120)

def person_card(name, sub):
    s = F("SemiBold", 40); n = F("Black", 60); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(max(d0.textlength(name, font=n), d0.textlength(sub, font=s))) + 90
    im = rrect((w, 180), DARK + (240,), 30); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 12, 179], 6, fill=ACC)
    d.text((44, 20), sub, font=s, fill=ACC); d.text((44, 74), name, font=n, fill=WHITE)
    return shadowed(im, 12, 130), w

# ---------- pop-ups ----------
POPS = []
for p in P["pops"]:
    k = p["kind"]
    if k == "big": img = card_big(p["text"], p.get("sub"), p.get("sub_top", True), ACC if p.get("hot", True) else WHITE, p.get("size", 150))
    elif k == "chips": img = None; p["imgs"] = [(c["t"], chip(c["text"])) for c in p["chips"]]
    elif k == "warn": img = warn_icon()
    elif k == "dm": img = dm_bubble()
    elif k == "person": img, _ = person_card(p["name"], p["sub"])
    p["img"] = img; POPS.append(p)

# ---------- end card ----------
def end_card():
    im = Image.new("RGBA", (W, H), DARK + (255,))
    yy, xx = np.mgrid[0:H, 0:W]; g = np.clip(1 - np.hypot(xx - SAFE_CX, yy - 640) / 900, 0, 1) ** 2 * 60  # soft glow behind logo
    glow = np.zeros((H, W, 4), np.uint8); glow[..., :3] = ACC; glow[..., 3] = g.astype(np.uint8)
    im.alpha_composite(Image.fromarray(glow, "RGBA")); d = ImageDraw.Draw(im)
    lg = Image.open(logo_p).convert("RGBA"); lg = lg.crop(lg.getbbox()); lh = 330
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    card = rrect((lg.width + 90, lh + 70), (255, 255, 255, 255), 40); card.alpha_composite(lg, (45, 35))
    im.alpha_composite(shadowed(card, 18, 140), (SAFE_CX - card.width // 2, 430))
    y = 900
    url = text_runs([(P["watermark"], WHITE)], 78, "Black", stroke=0, pad=10)
    im.alpha_composite(url, (SAFE_CX - url.width // 2, y)); d.rounded_rectangle([SAFE_CX - 200, y + url.height + 2, SAFE_CX + 200, y + url.height + 12], 5, fill=ACC)
    y += url.height + 50
    wa = text_runs([("WhatsApp  ", WHITE), (P["whatsapp"], ACC)], 56, "ExtraBold", stroke=0, pad=10)
    im.alpha_composite(wa, (SAFE_CX - wa.width // 2, y)); y += wa.height + 46
    lines = P["cta"]; fh = F("ExtraBold", 46); bw = int(max(d.textlength(l, font=fh) for l in lines)) + 90
    pill = rrect((bw, 70 * len(lines) + 50), ACC + (255,), 36); pd = ImageDraw.Draw(pill)
    for i, l in enumerate(lines): pd.text((bw // 2, 25 + 70 * i + 33), l, font=fh, fill=DARK, anchor="mm")
    im.alpha_composite(pill, (SAFE_CX - bw // 2, y))
    return im
END = end_card()

# ---------- timeline helpers ----------
def zoom_at(ts):
    for z in P["zoom"]:
        if z["s"] <= ts < z["e"]: return z["scale"]
    return 1.0
AX, AY = P["zoom_anchor"]
def zoomed(fr, s):
    if s == 1.0: return fr
    w, h = W / s, H / s; l, t = AX - AX / s, AY - AY / s
    return fr.resize((W, H), Image.BILINEAR, box=(l, t, l + w, t + h))

def grab(t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf", GRADE, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return Image.frombytes("RGB", (W, H), r.stdout[:W * H * 3])

def overlays(base, T):
    ts = T - INTRO
    for b in BOARDS:
        if b["s"] <= ts <= b["e"]: draw_board(base, b, ts - b["s"], b["e"] - b["s"], P["board_y"])
    for p in POPS:
        u, dur = ts - p["s"], p["e"] - p["s"]
        if not (0 <= u <= dur): continue
        cx, cy = p.get("x", SAFE_CX), p.get("y", P["pop_y"])
        if p["kind"] == "chips":
            n = len(p["imgs"]); gap = 18; tot = sum(i.height for _, i in p["imgs"]) + gap * (n - 1) - 40 * (n - 1); y0 = cy - tot / 2
            for t, im in p["imgs"]:
                sc, op = pop_env(ts - t, p["e"] - t)
                place(base, im, cx, y0 + im.height / 2, sc, op); y0 += im.height + gap - 40
        elif p["kind"] == "person":
            sc, op = pop_env(u, dur, 0.3, 0.2); dx = (1 - ease_out(u / 0.3)) * -120
            place(base, p["img"], cx + dx, cy, 1, op)
        else:
            sc, op = pop_env(u, dur)
            if p["kind"] == "warn": sc *= 1 + 0.06 * math.sin(u * 9)
            place(base, p["img"], cx, cy, sc, op)
    # captions
    for i, c in enumerate(P["captions"]):
        if c["s"] <= ts < c["e"]:
            u = ts - c["s"]; sc = 0.86 + 0.14 * ease_back(u / 0.14)
            place(base, caption_img(i), SAFE_CX, P["caption_y"], sc, min(1, u / 0.05)); break
    # name label once, ~3 s after the thumbnail
    ls, le = P["label_t"]
    if ls <= T <= le:
        u = T - ls; op = min(1, u / 0.2) * min(1, (le - T) / 0.25); dx = (1 - ease_out(u / 0.35)) * -80
        lx = P["wm_xy"][0] - 6 + dx
        base.alpha_composite(with_alpha(LABEL, op), (int(max(lx, 0)), P["label_y"]))

def thumb_frame(fr):
    base = zoomed(fr, P["thumb"]["zoom"]).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)  # darken lower half slightly for legibility
    for y in range(1000, H): gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(150 * min(1, (y - 1000) / 450))))
    base.alpha_composite(g)
    y = P["thumb"]["y"]
    for ln in P["thumb"]["lines"]:
        im = text_runs([(ln["text"], ACC if ln.get("hot") else WHITE)], ln["size"], "Black", stroke=11, pad=30)
        if im.width > 860: im = im.resize((860, int(im.height * 860 / im.width)), Image.LANCZOS)
        base.alpha_composite(im, (SAFE_CX - im.width // 2, y)); y += im.height - 80
    base.alpha_composite(wm, tuple(P["wm_xy"]))
    return base

# ---------- render ----------
vf = GRADE
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", vf, "-r", str(FPS), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=W * H * 3 * 4)
if mode == "preview": venc = ["-vf", "scale=540:960:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "22"]
else: venc = ["-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high"]
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", P["audio_path"], *venc, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
thumb = thumb_frame(grab(P["thumb"]["src_t"]))
if thumb_out: thumb.convert("RGB").save(thumb_out)
last = None; n_in = int(round(INTRO * FPS)); n_v = int(math.floor(VDUR * FPS)); end_first = n_in + n_v
for i in range(NF):
    T = i / FPS
    if i < n_in: fr = thumb.copy()
    elif i < end_first:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) == W * H * 3: last = Image.frombytes("RGB", (W, H), raw)
        fr = zoomed(last, zoom_at(T - INTRO)).convert("RGBA")
        overlays(fr, T)
        fr.alpha_composite(wm, tuple(P["wm_xy"]))
    else:
        u = (i - end_first) / FPS
        fr = zoomed(last, zoom_at(VDUR - 0.01)).convert("RGBA")
        fr = Image.blend(fr, END, min(1, u / 0.2))
        fr.alpha_composite(wm, tuple(P["wm_xy"]))
    enc.stdin.write(fr.convert("RGB").tobytes())
    if i % 150 == 0: print(f"frame {i}/{NF}", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
print("done", out)
