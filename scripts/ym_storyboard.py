# Mockup frame storyboard YM tutorial: rakaman skrin dalam kad telefon atas latar biru brand,
# pil langkah di atas, bulatan "klik" (#29ABE2) + label, kotak blur untuk data peribadi.
# python3 ym_storyboard.py <dir_png_1080x1920> <out_dir> <spec.json>
import json, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT, SPEC = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
B1, B2, WH = (42, 59, 143), (41, 171, 226), (255, 255, 255)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
W, H = 1080, 1920
SC = 0.80                      # skala skrin
PW, PH = int(W * SC), int(H * SC)
PX, PY = (W - PW) // 2, 250    # kedudukan kad skrin

def rr(d, box, r, **k): d.rounded_rectangle(box, r, **k)

for it in json.load(open(SPEC)):
    scr = Image.open(f"{SRC}/{it['t']}.png").convert("RGB").resize((W, H))
    for bx in it.get("blur", []):                       # blur data peribadi (koordinat 1080x1920)
        reg = scr.crop(bx).filter(ImageFilter.GaussianBlur(18)); scr.paste(reg, bx)
    bg = scr.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H))
    bg = Image.blend(bg, Image.new("RGB", (W, H), B1), 0.82)
    card = scr.resize((PW, PH))
    m = Image.new("L", (PW, PH), 0); rr(ImageDraw.Draw(m), (0, 0, PW, PH), 44, fill=255)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rr(ImageDraw.Draw(sh), (PX, PY + 14, PX + PW, PY + PH + 14), 44, fill=(0, 0, 0, 110))
    bg = Image.alpha_composite(bg.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(20)))
    bg.paste(card, (PX, PY), m)
    d = ImageDraw.Draw(bg)
    # pil langkah
    f1 = ImageFont.truetype(FX, 46); f2 = ImageFont.truetype(FB, 40)
    if it.get("step"):
        n = f"{it['step']}"; tx = it["title"]
        nw = d.textlength(n, font=f1); tw = d.textlength(tx, font=f2)
        x0 = (W - (nw + tw + 150)) // 2
        rr(d, (x0, 110, x0 + nw + tw + 150, 200), 45, fill=WH)
        d.ellipse((x0 + 10, 118, x0 + 84, 192), fill=B2)
        d.text((x0 + 47, 155), n, font=f1, fill=WH, anchor="mm")
        d.text((x0 + 104, 155), tx, font=f2, fill=B1, anchor="lm")
    # bulatan klik
    for c in it.get("tap", []):
        cx, cy = PX + c[0] * SC, PY + c[1] * SC; r = c[2] if len(c) > 2 else 70
        for k, a in ((r + 34, 60), (r + 16, 120)):
            o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(o).ellipse((cx - k, cy - k, cx + k, cy + k), outline=B2 + (a,), width=8)
            bg = Image.alpha_composite(bg, o)
        d = ImageDraw.Draw(bg)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(o).ellipse((cx - r, cy - r, cx + r, cy + r), fill=B2 + (45,))
        bg = Image.alpha_composite(bg, o); d = ImageDraw.Draw(bg)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=B2, width=10)
        if len(c) > 3 and c[3]:
            fl = ImageFont.truetype(FX, 40); lw = d.textlength(c[3], font=fl)
            lx = min(max(cx - lw / 2 - 30, 40), W - lw - 100); ly = cy + r + 30
            rr(d, (lx, ly, lx + lw + 60, ly + 76), 38, fill=B2)
            d.text((lx + 30 + lw / 2, ly + 38), c[3], font=fl, fill=WH, anchor="mm")
    # caption contoh
    if it.get("cap"):
        fc = ImageFont.truetype(FX, 62); cw = d.textlength(it["cap"], font=fc)
        rr(d, (W / 2 - cw / 2 - 36, 1372, W / 2 + cw / 2 + 36, 1470), 24, fill=(20, 24, 50))
        d.text((W / 2, 1421), it["cap"], font=fc, fill=WH, anchor="mm")
    bg.convert("RGB").resize((540, 960), Image.LANCZOS).save(f"{OUT}/{it['id']}.jpg", quality=86)
    print(it["id"])
