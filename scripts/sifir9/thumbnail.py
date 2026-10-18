# TikTok cover 1080x1920 for Sifir 9. Key text sits inside the centre 3:4 crop
# (y 240-1680) that the profile grid shows.
# usage: thumbnail.py <graded_face.png> <board_final.png> <aster_logo.png> <tiktok_avatar.png> <fonts_dir> <out.png>
import sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
face_p, board_p, logo_p, avatar_p, fdir, out = sys.argv[1:7]
W, H = 1080, 1920
Y, K, R, WH = (255, 216, 0), (11, 11, 11), (235, 10, 30), (255, 255, 255)
F = lambda name, size: ImageFont.truetype(os.path.join(fdir, name), size)

img = Image.open(face_p).convert("RGB").resize((W, H))
# push the face a little lower and larger so the title has room above the cap
img = img.resize((int(W * 1.08), int(H * 1.08)), Image.LANCZOS).crop((int(W * .04), 20, int(W * .04) + W, 20 + H))
# top shade for the title, bottom shade for the brand strip
shade = Image.new("L", (W, H), 0); d = ImageDraw.Draw(shade)
for y in range(H):
    a = max(0, 1 - y / 760) ** 1.4 * 235 + max(0, (y - 1560) / 360) ** 1.2 * 235
    d.line([(0, y), (W, y)], fill=int(min(235, a)))
img = Image.composite(Image.new("RGB", (W, H), K), img, shade)
draw = ImageDraw.Draw(img)

def text(xy, s, font, fill, stroke=0, sfill=K, anchor="la", shadow=True):
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + 8, xy[1] + 12), s, font=font, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170), anchor=anchor)
        img.paste(sh.filter(ImageFilter.GaussianBlur(10)), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)

# title block
text((W // 2, 300), "TAK PERLU HAFAL!", F("Poppins-Black.ttf", 92), WH, 10, anchor="mm")
text((W // 2 - 10, 500), "SIFIR 9", F("Poppins-BlackItalic.ttf", 300), Y, 18, anchor="mm")
# "cuma tulis je" yellow highlighter strip, handwriting
pill = F("Poppins-ExtraBold.ttf", 64); label = "Cuma TULIS je"
bx = draw.textbbox((0, 0), label, font=pill); pw, ph = bx[2] - bx[0] + 70, 104
strip = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); ImageDraw.Draw(strip).rounded_rectangle((0, 0, pw, ph), 22, fill=K + (255,))
ImageDraw.Draw(strip).text((pw // 2, ph // 2 + 2), label, font=pill, fill=Y, anchor="mm")
strip = strip.rotate(-3, expand=True, resample=Image.BICUBIC)
img.paste(strip, ((W - strip.width) // 2, 640), strip)

# board card: the finished trick (0 9 / 1 8 / ... / 9 0 with red lines)
b = Image.open(board_p).convert("RGB").crop((250, 80, 740, 1275))  # SIFIR 9 title to the 9 0 row
b = b.resize((int(b.width * 0.54), int(b.height * 0.54)), Image.LANCZOS)
pad = 16; card = Image.new("RGBA", (b.width + pad * 2, b.height + pad * 2), Y + (255,))
card.paste(b, (pad, pad))
card = ImageOps.expand(card, border=0)
cs = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0)); cs.paste((0, 0, 0, 150), (40, 50, 40 + card.width, 50 + card.height))
cs = cs.filter(ImageFilter.GaussianBlur(18)); cs.paste(card, (40, 40), card)
cs = cs.rotate(5, expand=True, resample=Image.BICUBIC)
cx, cy = W - cs.width + 40, 960
img.paste(cs, (cx, cy), cs)

# "< 3 MINIT" sticker on the card corner
st = 250; sticker = Image.new("RGBA", (st, st), (0, 0, 0, 0)); sd = ImageDraw.Draw(sticker)
sd.ellipse((6, 6, st - 6, st - 6), fill=R + (255,), outline=WH + (255,), width=10)
sd.text((st // 2, st // 2 - 34), "< 3", font=F("Poppins-Black.ttf", 92), fill=WH, anchor="mm")
sd.text((st // 2, st // 2 + 52), "MINIT", font=F("Poppins-Black.ttf", 52), fill=WH, anchor="mm")
sticker = sticker.rotate(-12, expand=True, resample=Image.BICUBIC)
img.paste(sticker, (18, 860), sticker)

# brand strip
logo = Image.open(logo_p).convert("RGBA"); logo = logo.resize((170, 170), Image.LANCZOS)
img.paste(logo, (40, 1715), logo)
text((215, 1760), "Tuisyen Online Aster", F("Poppins-ExtraBold.ttf", 50), WH, shadow=False)
av = Image.open(avatar_p).convert("RGBA").resize((64, 64), Image.LANCZOS)
m = Image.new("L", (64, 64), 0); ImageDraw.Draw(m).ellipse((0, 0, 63, 63), fill=255)
img.paste(av, (217, 1832), m)
text((296, 1864), "@aster.edu_tpg", F("Poppins-ExtraBold.ttf", 40), Y, shadow=False, anchor="lm")
img.save(out, quality=95)
print("saved", out)
