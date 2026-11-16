"""Gambar statik -> klip B-roll 9:16 dengan Ken Burns (DNA Fi-k 7.7: gambar 1.5-2.5 s, zoom/pan perlahan).

python3 fk_imgclip.py <gambar> <out.mp4> <saat> [in|out]
- Gambar potret (lebar/tinggi < 0.8): skrin penuh, crop 9:16, zoom perlahan 100% -> 108% (atau sebaliknya).
- Gambar landskap / kecil: kad di tengah (sudut bulat, bayang lembut) atas latar gambar sama yang dikaburkan
  dan digelapkan sedikit, kad zoom perlahan 100% -> 106%. Tiada herot, tiada crop berat pada gambar kecil.
"""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance

src, dst, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
direction = sys.argv[4] if len(sys.argv) > 4 else "in"
W, H, FPS = 1080, 1920, 30
N = int(round(dur * FPS))
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
iw, ih = im.size

def ease(x): return x * x * (3 - 2 * x)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst],
                       stdin=subprocess.PIPE)
if iw / ih < 0.8:
    # skrin penuh: skala supaya 9:16 penuh pada zoom 1.08, kemudian crop bergerak
    base = max(W / iw, H / ih)
    big = im.resize((int(iw * base * 1.08) + 2, int(ih * base * 1.08) + 2), Image.LANCZOS)
    arr = np.array(big)
    for k in range(N):
        e = ease(k / max(1, N - 1))
        z = 1.0 + 0.08 * (e if direction == "in" else 1 - e)
        cw, ch = W * 1.08 / z, H * 1.08 / z
        x0 = (arr.shape[1] - cw) / 2; y0 = (arr.shape[0] - ch) / 2
        M = np.float32([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]])
        enc.stdin.write(cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_CUBIC).tobytes())
else:
    bgs = max(W / iw, H / ih)
    bg = im.resize((int(iw * bgs) + 2, int(ih * bgs) + 2), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.72)
    cw = 940; chh = int(ih * cw / iw)
    card = im.resize((cw * 2, chh * 2), Image.LANCZOS)   # 2x untuk zoom tanpa pecah
    mask = Image.new("L", card.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, *card.size), 56, fill=255)
    sh = Image.new("L", (W, H), 0)
    cx, cy = (W * 0.85) / 2 + 20, int(H * 0.42)          # tengah zon selamat, atas caption
    ImageDraw.Draw(sh).rounded_rectangle((cx - cw / 2, cy - chh / 2 + 18, cx + cw / 2, cy + chh / 2 + 18), 28, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), bg, sh)
    for k in range(N):
        e = ease(k / max(1, N - 1))
        z = 1.0 + 0.06 * (e if direction == "in" else 1 - e)
        w2, h2 = int(cw * z), int(chh * z)
        c = card.resize((w2, h2), Image.LANCZOS); m = mask.resize((w2, h2), Image.LANCZOS)
        fr = base.copy(); fr.paste(c, (int(cx - w2 / 2), int(cy - h2 / 2)), m)
        enc.stdin.write(np.array(fr).tobytes())
enc.stdin.close(); enc.wait()
print("ok", dst, N, "frames", "potret" if iw / ih < 0.8 else "kad")
