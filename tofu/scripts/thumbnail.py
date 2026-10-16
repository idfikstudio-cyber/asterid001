"""Cover/thumbnail variants for the TOFU reel (1080x1920, text kept inside the 4:5 grid crop).

usage: python3 thumbnail.py <scenes_dir> <out_dir>
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from render import CREAM, GOLD, H, INK, W, font, view

OUT = sys.argv[2]
RED = (235, 72, 60)
GRID = (285, 1635)  # IG profile grid shows the centre 1080x1350


def shade(img, y, half, strength=185):
    yy = np.arange(H)[:, None]
    a = (np.clip(1 - np.abs(yy - y) / half, 0, 1) ** 0.7 * strength).astype(np.uint8)
    over = Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [Image.fromarray(np.repeat(a, W, 1))])
    return Image.alpha_composite(img.convert("RGBA"), over)


def text(d, xy, s, f, fill=CREAM, anchor="mm", stroke=0):
    x, y = xy
    d.text((x + 4, y + 6), s, font=f, fill=(0, 0, 0, 140), anchor=anchor)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK)


def pill(d, cx, cy, s, f, bg, fg, pad=(36, 20)):
    l, t, r, b = d.textbbox((0, 0), s, font=f, anchor="lt")
    w, h = r - l + 2 * pad[0], b - t + 2 * pad[1]
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=bg)
    d.text((cx, cy), s, font=f, fill=fg, anchor="mm")


def badge360(d, x, y):
    d.rounded_rectangle((x, y, x + 300, y + 70), radius=35, fill=(20, 18, 16, 170))
    d.ellipse((x + 24, y + 23, x + 48, y + 47), fill=RED)
    d.text((x + 64, y + 35), "360° 3D TOUR", font=font("Bold", 32), fill=CREAM, anchor="lm")


def drag_hint(d, cy):
    d.line((W / 2 - 190, cy, W / 2 + 190, cy), fill=(255, 255, 255, 170), width=5)
    for sx in (-1, 1):
        ax = W / 2 + sx * 210
        d.polygon([(ax, cy), (ax - sx * 28, cy - 20), (ax - sx * 28, cy + 20)], fill=(255, 255, 255, 220))
    d.ellipse((W / 2 + 60 - 40, cy - 40, W / 2 + 60 + 40, cy + 40), fill=CREAM)
    d.ellipse((W / 2 + 60 - 15, cy - 15, W / 2 + 60 + 15, cy + 15), fill=GOLD)


def cover_a():
    """Main cover, same promise as the video hook."""
    img = shade(view("01_guest1", 0, 6, 60), 760, 520)
    d = ImageDraw.Draw(img)
    badge360(d, 390, 330)
    pill(d, W / 2, 500, "SEBELUM RENOVATE", font("Black", 54), RED, (255, 255, 255))
    text(d, (W / 2, 660), "TENGOK DULU", font("Black", 118))
    text(d, (W / 2, 790), "RUMAH ANDA", font("Black", 118))
    text(d, (W / 2, 925), "SIAP DALAM 3D", font("Black", 118), fill=GOLD)
    img = shade(img, 1510, 170, 160)
    d = ImageDraw.Draw(img)
    drag_hint(d, 1480)
    text(d, (W / 2, 1565), "pusing 360° dalam setiap bilik", font("SemiBold", 40))
    return img


def cover_b():
    """Poll cover: curiosity + comment bait."""
    top = view("05_dining", -4, 12, 78, W, H // 2)
    bot = view("07_drykitchen", -150, 10, 78, W, H // 2)
    img = Image.new("RGB", (W, H))
    img.paste(top, (0, 0))
    img.paste(bot, (0, H // 2))
    img = shade(img, H / 2, 420, 150)
    d = ImageDraw.Draw(img)
    d.rectangle((0, H / 2 - 5, W, H / 2 + 5), fill=CREAM)
    for lab, cy in (("A", 560), ("B", 1360)):
        d.ellipse((W / 2 - 95, cy - 95, W / 2 + 95, cy + 95), fill=CREAM)
        d.text((W / 2, cy + 6), lab, font=font("Black", 130), fill=INK, anchor="mm")
    d.rounded_rectangle((60, H / 2 - 150, W - 60, H / 2 + 150), radius=40, fill=(250, 246, 238, 245))
    d.text((W / 2, H / 2 - 62), "RUMAH ANDA,", font=font("Black", 74), fill=INK, anchor="mm")
    d.text((W / 2, H / 2 + 22), "MANA NAK RENO DULU?", font=font("Black", 66), fill=INK, anchor="mm")
    d.text((W / 2, H / 2 + 100), "komen A atau B", font=font("Bold", 46), fill=(190, 120, 70), anchor="mm")
    return img


def cover_c():
    """Reveal cover: the most 'wow' room + project label."""
    img = view("05_dining", 4, 10, 66)
    img = shade(img, 620, 400)
    d = ImageDraw.Draw(img)
    badge360(d, 390, 330)
    text(d, (W / 2, 560), "RUMAH NI BELUM", font("Black", 104))
    text(d, (W / 2, 680), "SIAP DIBINA", font("Black", 104), fill=GOLD)
    pill(d, W / 2, 830, "ini render 3D 360°", font("Bold", 48), CREAM, INK)
    img = shade(img, 1560, 160, 150)
    d = ImageDraw.Draw(img)
    text(d, (W / 2, 1560), "PT22 · LEMBAH KERAMAT · FI-K STUDIO", font("Bold", 38))
    return img


def main():
    for name, fn in (("A_tengok_dulu", cover_a), ("B_poll_AB", cover_b), ("C_belum_siap", cover_c)):
        img = fn().convert("RGB")
        img.save(f"{OUT}/cover_{name}.jpg", quality=92)
        # 4:5 grid crop, to check what shows on the profile grid
        img.crop((0, GRID[0], W, GRID[1])).save(f"{OUT}/cover_{name}_4x5.jpg", quality=92)


if __name__ == "__main__":
    main()
