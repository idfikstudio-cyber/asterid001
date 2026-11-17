# Mockup tambahan storyboard YM: thumbnail, intro + label, cip kedai aplikasi, PIP Farhan atas tutorial, end card.
# python3 ym_sb_extra.py <hi_dir> <brand_dir> <sb_out_dir>
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HI, BR, OUT = sys.argv[1:4]
B1, B2, WH, INK = (42, 59, 143), (41, 171, 226), (255, 255, 255), (20, 24, 50)
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
W, H = 1080, 1920
def F(p, s): return ImageFont.truetype(p, s)
def save(im, n): im.convert("RGB").resize((540, 960), Image.LANCZOS).save(f"{OUT}/{n}.jpg", quality=86); print(n)
def grad(im, y0, a=200):
    g = Image.new("L", (1, H), 0)
    for y in range(y0, H): g.putpixel((0, y), int(a * (y - y0) / (H - y0)))
    im.paste(Image.new("RGB", (W, H), INK), (0, 0), g.resize((W, H)))

# 1. Thumbnail (frame 150s)
im = Image.open(f"{HI}/raw_150.png").convert("RGB"); grad(im, 900, 235); d = ImageDraw.Draw(im)
d.rounded_rectangle((80, 1020, 560, 1100), 40, fill=B2); d.text((320, 1060), "TUTORIAL", font=F(FX, 50), fill=WH, anchor="mm")
for i, (t, c) in enumerate([("CARA BAYAR", WH), ("YURAN DALAM", WH), ("APP", B2)]):
    d.text((80, 1130 + i * 108), t, font=F(FX, 96), fill=c, stroke_width=4, stroke_fill=INK)
save(im, "s0_thumb")

# 2. Intro + label "Farhan · Yuran.my"
im = Image.open(f"{HI}/raw_3.png").convert("RGB").resize((int(W * 1.1), int(H * 1.1))).crop((54, 40, 54 + W, 40 + H)); d = ImageDraw.Draw(im)
lab = "Farhan · Yuran.my"; lw = d.textlength(lab, font=F(FB, 40))
d.rounded_rectangle((70, 300, 70 + lw + 60, 376), 38, fill=B1); d.text((100, 338), lab, font=F(FB, 40), fill=WH, anchor="lm")
cap = "install aplikasi"; cw = d.textlength(cap, font=F(FX, 70))
d.text((W / 2, 1380), "install", font=F(FX, 76), fill=WH, anchor="rm", stroke_width=8, stroke_fill=INK)
d.text((W / 2 + 20, 1380), "Yuran.my", font=F(FX, 76), fill=B2, anchor="lm", stroke_width=8, stroke_fill=INK)
save(im, "s1_intro")

# 3. Cip kedai aplikasi (teks sahaja, tiada logo pihak ketiga)
im = Image.open(f"{HI}/raw_30.png").convert("RGB"); d = ImageDraw.Draw(im)
for i, (dev, st) in enumerate([("Android", "Play Store"), ("iOS", "App Store"), ("Huawei", "AppGallery")]):
    y = 980 + i * 150
    d.rounded_rectangle((120, y, 880, y + 120), 30, fill=WH)
    d.rounded_rectangle((120, y, 400, y + 120), 30, fill=B1)
    d.text((260, y + 60), dev, font=F(FX, 44), fill=WH, anchor="mm")
    d.text((640, y + 60), st, font=F(FB, 48), fill=B1, anchor="mm")
save(im, "s1b_stores")

# 4. PIP Farhan atas rakaman skrin (pakai mockup langkah 7)
base = Image.open(f"{OUT}/s8_home.jpg").resize((W, H)).convert("RGB")
face = Image.open(f"{HI}/raw_45.png").convert("RGB").crop((280, 450, 820, 990)).resize((250, 250))
m = Image.new("L", (250, 250), 0); ImageDraw.Draw(m).ellipse((0, 0, 249, 249), fill=255)
d = ImageDraw.Draw(base); d.ellipse((44, 1256, 306, 1518), fill=WH)
base.paste(face, (50, 1262), m)
save(base, "s8b_pip")

# 5. End card
im = Image.new("RGB", (W, H), B1); d = ImageDraw.Draw(im)
logo = Image.open(f"{BR}/logo_white.png").convert("RGBA"); logo = logo.resize((560, int(560 * logo.height / logo.width)), Image.LANCZOS)
im.paste(logo, ((W - logo.width) // 2, 640), logo)
d.text((W / 2, 1060), "Cara MUDAH Urus Yuran", font=F(FX, 64), fill=WH, anchor="mm")
d.rounded_rectangle((110, 1180, 970, 1290), 55, fill=B2)
d.text((W / 2, 1235), "Follow untuk tips urus yuran sekolah", font=F(FB, 40), fill=WH, anchor="mm")
d.text((W / 2, 1380), "hello@yuran.my", font=F(FB, 46), fill=(231, 232, 233), anchor="mm")
save(im, "s12_end")
