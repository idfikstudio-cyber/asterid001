"""Render the Fi-k Studio TOFU reel (1080x1920) from the AIHouse 720 cubemaps.

usage: python3 render.py <scenes_dir> <out.mp4> [--preview]
<scenes_dir> holds one folder per scene (01_guest1 ...) with f,b,l,r,u,d.jpg.
Writes video only; audio is mixed by mix.py.
"""
import math
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import cube

W, H, FPS = 1080, 1920, 30
SCN = sys.argv[1]
PREVIEW = "--preview" in sys.argv
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-%s.otf"
CREAM, INK, GOLD = (250, 246, 238), (34, 30, 27), (212, 165, 116)
XF = 0.3  # crossfade between shots (s)

# ---------------------------------------------------------------- timeline
# kind, start, end, scene, yaw0, yaw1, pitch, hfov0, hfov1
SHOTS = [
    ("pan", 0.0, 3.4, "01_guest1", -8, 8, 4, 80, 56),
    ("pan", 3.4, 7.8, "02_guest2", -62, 30, 3, 64, 64),
    ("pan", 7.8, 12.2, "04_living2", -18, 112, 8, 64, 62),
    ("poll", 12.2, 16.8, None, 0, 0, 0, 0, 0),
    ("pan", 16.8, 21.0, "05_dining", -42, 18, 12, 64, 60),
    ("pan", 21.0, 24.6, "07_drykitchen", -168, -105, 16, 64, 62),
    ("pan", 24.6, 28.2, "09_wetkitchen", -30, 40, 10, 64, 62),
    ("pan", 28.2, 31.4, "10_bathroom", -68, 2, 6, 68, 62),
    ("pan", 31.4, 35.0, "03_living1", -40, 30, 5, 70, 60),
    ("cta", 35.0, 41.0, "01_guest1", 0, 6, 4, 64, 60),
]
DUR = SHOTS[-1][2]

# room chip + caption + hotspot (yaw, pitch, label) per shot start
ROOMS = {
    3.4: ("01", "GUEST AREA", "Ruang tamu tetamu", (-56, 2, "Partition kayu slat", "privasi tanpa dinding batu")),
    7.8: ("02", "LIVING", "Ruang keluarga", (21, 1, "Feature wall TV", "dengan lampu LED tersembunyi")),
    16.8: ("03", "DINING", "Ruang makan", (21, -18, "Kabinet tinggi siling", "storan maksimum")),
    21.0: ("04", "DRY KITCHEN", "Dapur kering", (-122, 26, "Meja island", "sarapan + ruang kerja")),
    24.6: ("05", "WET KITCHEN", "Dapur basah", (2, 24, "Kabinet kayu + top putih", "senang lap, nampak luas")),
    28.2: ("06", "BATHROOM", "Bilik air", (-66, 4, "Mozek hitam-putih", "+ skrin kaca shower")),
}
N_ROOMS = 6


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def out_back(t):
    t = min(max(t, 0.0), 1.0) - 1
    return 1 + 2.2 * t ** 3 + 1.2 * t ** 2


@lru_cache(maxsize=4)
def atlas(name):
    return cube.load_atlas(f"{SCN}/{name}")


@lru_cache(maxsize=None)
def font(weight, size):
    return ImageFont.truetype(FONT % weight, size)


def cam(shot, t):
    _, s, e, _, y0, y1, p, f0, f1 = shot
    k = ease((t - s) / (e - s))
    return y0 + (y1 - y0) * k, p, f0 + (f1 - f0) * k


def view(scene, yaw, pitch, hfov, w=W, h=H):
    a, n = atlas(scene)
    return Image.fromarray(cube.perspective(a, n, yaw, pitch, hfov, w, h)[:, :, ::-1])


def project(yaw, pitch, hfov, ty, tp, w=W, h=H):
    """Screen position of world direction (ty, tp) for a camera (yaw, pitch, hfov)."""
    def vec(yw, pt):
        yw, pt = math.radians(yw), math.radians(-pt)
        return np.array([math.cos(pt) * math.sin(yw), math.sin(pt), math.cos(pt) * math.cos(yw)])
    d = vec(ty, tp)
    fwd, right = vec(yaw, pitch), vec(yaw + 90, 0)
    up = np.cross(fwd, right)
    z = d @ fwd
    if z <= 0.05:
        return None
    f = (w / 2) / math.tan(math.radians(hfov) / 2)
    return w / 2 + f * (d @ right) / z, h / 2 - f * (d @ up) / z


def shot_frame(shot, t):
    kind, s, e, scene = shot[:4]
    if kind == "poll":
        return poll_bg(t - s)
    yaw, pitch, hfov = cam(shot, t)
    img = view(scene, yaw, pitch, hfov)
    if kind == "cta":
        img = img.filter(ImageFilter.GaussianBlur(14))
    return img


def poll_bg(lt):
    drift = lt * 4
    top = view("05_dining", -4 + drift, 12, 78, W, H // 2)
    bot = view("07_drykitchen", -150 + drift, 10, 78, W, H // 2)
    img = Image.new("RGB", (W, H))
    img.paste(top, (0, 0))
    img.paste(bot, (0, H // 2))
    return img


# ---------------------------------------------------------------- overlay helpers
def shadow_text(d, xy, text, f, fill=CREAM, anchor="mm", a=255, sh=150):
    x, y = xy
    d.text((x + 3, y + 4), text, font=f, fill=(0, 0, 0, int(sh * a / 255)), anchor=anchor)
    d.text((x, y), text, font=f, fill=fill + (a,), anchor=anchor)


def pill(d, cx, cy, text, f, bg, fg, a=255, pad=(34, 18)):
    l, t, r, b = d.textbbox((0, 0), text, font=f, anchor="lt")
    w, h = r - l + pad[0] * 2, b - t + pad[1] * 2
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=bg + (a,))
    d.text((cx, cy), text, font=f, fill=fg + (a,), anchor="mm")
    return w, h


def top_bar(d, t, active):
    # "360° 3D TOUR" badge + room progress dots
    d.rounded_rectangle((48, 120, 330, 186), radius=33, fill=(20, 18, 16, 150))
    d.ellipse((72, 141, 96, 165), fill=(235, 72, 60, 255) if int(t * 2) % 2 == 0 else (235, 72, 60, 120))
    d.text((112, 153), "360° 3D TOUR", font=font("Bold", 30), fill=CREAM + (255,), anchor="lm")
    x0 = W - 48 - N_ROOMS * 44
    for i in range(N_ROOMS):
        on = i < active
        d.rounded_rectangle((x0 + i * 44, 147, x0 + i * 44 + 34, 159), radius=6,
                            fill=GOLD + (255,) if on else (255, 255, 255, 90))


def hotspot(d, layer, xy, label, sub, a, lt):
    x, y = xy
    r = 18 + 6 * math.sin(lt * 6)
    ring = 34 + (lt * 40) % 40
    d.ellipse((x - ring, y - ring, x + ring, y + ring), outline=CREAM + (int(a * (1 - (ring - 34) / 40) * 0.9),), width=4)
    d.ellipse((x - r, y - r, x + r, y + r), fill=CREAM + (int(a * 0.95),))
    d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=GOLD + (a,))
    # label card to the side that has room
    f1, f2 = font("Bold", 40), font("Medium", 32)
    w = max(d.textlength(label, font=f1), d.textlength(sub, font=f2)) + 56
    left = x > W * 0.55
    cx0 = x - 60 - w if left else x + 60
    cx0 = min(max(cx0, 40), W - 40 - w)
    cy0 = y - 62
    d.line((x + (-r if left else r), y, cx0 + (w if left else 0), y), fill=CREAM + (a,), width=4)
    d.rounded_rectangle((cx0, cy0, cx0 + w, cy0 + 124), radius=22, fill=(250, 246, 238, int(a * 0.94)))
    d.text((cx0 + 28, cy0 + 24), label, font=f1, fill=INK + (a,), anchor="lt")
    d.text((cx0 + 28, cy0 + 76), sub, font=f2, fill=(110, 96, 84, a), anchor="lt")


def room_chip(d, num, name, sub, a, lt):
    dy = (1 - out_back(lt / 0.45)) * 60
    y = 1480 + dy
    d.text((64, y), num, font=font("Black", 120), fill=GOLD + (int(a * 0.95),), anchor="ls")
    shadow_text(d, (64, y + 70), name, font("Black", 72), anchor="ls", a=a)
    shadow_text(d, (66, y + 126), sub, font("Medium", 42), fill=(235, 226, 212), anchor="ls", a=a)


def swipe_hint(d, lt, a):
    # hand-drag gesture: a dot sliding left-right with trailing arrows
    cx, cy = W / 2 + 150 * math.sin(lt * 2.4), 1500
    d.line((W / 2 - 200, cy, W / 2 + 200, cy), fill=(255, 255, 255, int(a * 0.5)), width=4)
    for sx in (-1, 1):
        ax = W / 2 + sx * 220
        d.polygon([(ax, cy), (ax - sx * 26, cy - 18), (ax - sx * 26, cy + 18)], fill=(255, 255, 255, int(a * 0.7)))
    d.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), fill=CREAM + (a,))
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=GOLD + (a,))
    shadow_text(d, (W / 2, cy + 90), "drag & pusing 360° — macam berada di dalam rumah", font("SemiBold", 34), a=a)


def fade(lt, ln, i=0.25, o=0.25):
    return int(255 * min(1, max(0, lt / i), max(0, (ln - lt) / o)))


def vignette():
    y = np.linspace(-1, 1, H)[:, None]
    g = np.clip((np.abs(y) - 0.35) / 0.65, 0, 1) ** 1.6 * 170
    a = np.repeat(g, W, 1).astype(np.uint8)
    return Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [Image.fromarray(a)])


VIG = None
BAND = None


def band(y, half):
    """Soft dark band behind headline text."""
    yy = np.arange(H)[:, None]
    a = (np.clip(1 - np.abs(yy - y) / half, 0, 1) ** 0.8 * 165).astype(np.uint8)
    a = np.repeat(a, W, 1)
    return Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [Image.fromarray(a)])


# ---------------------------------------------------------------- overlays per segment
def overlay(t, img):
    global VIG, BAND
    if VIG is None:
        VIG, BAND = vignette(), band(600, 380)
    img = img.convert("RGBA")
    img.alpha_composite(VIG)
    if t < 3.4 or 31.4 <= t < 35.0:
        img = Image.blend(img, Image.alpha_composite(img, BAND), min(1, (t if t < 3.4 else t - 31.4) / 0.2))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shot = next(s for s in SHOTS if s[1] <= t < s[2] or s is SHOTS[-1])
    kind, s, e = shot[:3]
    lt = t - s

    active = sum(1 for k in ROOMS if k <= t)
    if kind != "cta":
        top_bar(d, t, active)

    if s == 0.0:  # HOOK
        a1 = fade(lt, 3.4, 0.15, 0.3)
        k = out_back(lt / 0.35)
        pill(d, W / 2, 420 - (1 - k) * 40, "SEBELUM RENOVATE...", font("Black", 46), (235, 72, 60), (255, 255, 255), a1)
        shadow_text(d, (W / 2, 560), "Tengok dulu rumah", font("Black", 86), a=fade(lt - 0.35, 3.0, 0.2, 0.3))
        shadow_text(d, (W / 2, 660), "anda siap — dalam 3D", font("Black", 86), fill=GOLD, a=fade(lt - 0.6, 2.75, 0.2, 0.3))
        swipe_hint(d, lt, fade(lt - 1.0, 2.4, 0.3, 0.3))

    elif s in ROOMS:
        num, name, sub, (hy, hp, lab, lsub) = ROOMS[s]
        ln = e - s
        room_chip(d, num, name, sub, fade(lt, ln, 0.2, 0.3), lt)
        yaw, pitch, hfov = cam(shot, t)
        p = project(yaw, pitch, hfov, hy, hp)
        ha = fade(lt - 0.9, ln - 0.9, 0.25, 0.3)
        if p and ha and 80 < p[0] < W - 80:
            hotspot(d, layer, p, lab, lsub, ha, lt)

    elif kind == "poll":
        ln = e - s
        a = fade(lt, ln, 0.2, 0.3)
        d.rectangle((0, H / 2 - 4, W, H / 2 + 4), fill=CREAM + (a,))
        for label, name, cy in (("A", "RUANG MAKAN", H * 0.25), ("B", "DAPUR ISLAND", H * 0.75)):
            k = out_back((lt - (0.3 if label == "A" else 0.5)) / 0.35)
            r = 82 * k
            if r > 1:
                d.ellipse((W / 2 - r, cy - r, W / 2 + r, cy + r), fill=CREAM + (a,))
                d.text((W / 2, cy + 4), label, font=font("Black", int(110 * k) + 1), fill=INK + (a,), anchor="mm")
            shadow_text(d, (W / 2, cy + 150), name, font("Black", 56), a=fade(lt - 0.6, ln - 0.6))
        # center question bar
        qa = fade(lt - 0.1, ln - 0.1)
        d.rounded_rectangle((70, H / 2 - 110, W - 70, H / 2 + 110), radius=34, fill=(250, 246, 238, int(qa * 0.97)))
        d.text((W / 2, H / 2 - 38), "Kalau rumah anda, mana nak", font=font("Bold", 46), fill=INK + (qa,), anchor="mm")
        d.text((W / 2, H / 2 + 30), "reno dulu? KOMEN A atau B", font=font("Black", 50), fill=(190, 120, 70, qa), anchor="mm")
        # timer bar = "answer before it ends"
        tb = 1 - lt / ln
        d.rounded_rectangle((110, H / 2 + 78, 110 + (W - 220) * tb, H / 2 + 90), radius=6, fill=GOLD + (qa,))

    elif s == 31.4:  # bridge line
        ln = e - s
        shadow_text(d, (W / 2, 640), "Semua ini dirancang dalam 3D", font("Black", 66), a=fade(lt, ln))
        shadow_text(d, (W / 2, 730), "SEBELUM satu bata pun diubah.", font("Black", 66), fill=GOLD, a=fade(lt - 0.6, ln - 0.6))
        shadow_text(d, (W / 2, 1430), "Nampak hasil dulu. Bajet & keputusan lebih yakin.",
                    font("SemiBold", 40), a=fade(lt - 1.3, ln - 1.3))

    elif kind == "cta":
        ln = e - s
        a = fade(lt, ln + 1, 0.3, 0.1)
        d.rectangle((0, 0, W, H), fill=(26, 22, 19, int(a * 0.55)))
        cy = 560 - (1 - out_back(lt / 0.5)) * 50
        d.text((W / 2, cy), "FI-K STUDIO", font=font("Black", 110), fill=CREAM + (a,), anchor="mm")
        d.text((W / 2, cy + 90), "INTERIOR DESIGN & BUILD", font=font("SemiBold", 40), fill=GOLD + (a,), anchor="mm")
        b = fade(lt - 0.5, ln, 0.3, 0.1)
        d.text((W / 2, 880), "Nak tengok tour 360° penuh", font=font("Bold", 54), fill=CREAM + (b,), anchor="mm")
        d.text((W / 2, 950), "projek ni sendiri?", font=font("Bold", 54), fill=CREAM + (b,), anchor="mm")
        c = fade(lt - 1.0, ln, 0.3, 0.1)
        pulse = 1 + 0.04 * math.sin(lt * 7)
        bw, bh = 640 * pulse, 170 * pulse
        d.rounded_rectangle((W / 2 - bw / 2, 1130 - bh / 2, W / 2 + bw / 2, 1130 + bh / 2), radius=bh / 2, fill=GOLD + (c,))
        d.text((W / 2, 1130), "KOMEN “360”", font=font("Black", 76), fill=INK + (c,), anchor="mm")
        d.text((W / 2, 1270), "kami DM link terus kepada anda", font=font("SemiBold", 40), fill=CREAM + (c,), anchor="mm")
        g = fade(lt - 1.8, ln, 0.3, 0.1)
        d.text((W / 2, 1480), "Simpan video ni untuk idea reno rumah anda", font=font("Medium", 36),
               fill=(235, 226, 212, g), anchor="mm")
        d.text((W / 2, 1540), "Projek: PT22 · Lembah Keramat", font=font("Medium", 32),
               fill=(200, 188, 172, g), anchor="mm")

    img.alpha_composite(layer)
    return img.convert("RGB")


def frame(i):
    t = i / FPS
    cur = next(s for s in SHOTS if s[1] <= t < s[2] or s is SHOTS[-1])
    img = shot_frame(cur, t)
    idx = SHOTS.index(cur)
    if idx and t - cur[1] < XF:  # blend in from previous shot (with a quick zoom-whip feel)
        prev = shot_frame(SHOTS[idx - 1], min(t, SHOTS[idx - 1][2] - 1e-3))
        img = Image.blend(prev, img, ease((t - cur[1]) / XF))
    return overlay(t, img).tobytes()


def main():
    out = sys.argv[2]
    n = int(DUR * FPS)
    frames = range(0, n, 15) if PREVIEW else range(n)
    if PREVIEW:
        with Pool(4) as p:
            for i, b in zip(frames, p.imap(frame, frames, chunksize=2)):
                Image.frombytes("RGB", (W, H), b).resize((W // 3, H // 3)).save(f"{out}/f{i:04d}.jpg")
        return
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for k, b in enumerate(p.imap(frame, frames, chunksize=4)):
            ff.stdin.write(b)
            if k % 150 == 0:
                print(f"{k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
