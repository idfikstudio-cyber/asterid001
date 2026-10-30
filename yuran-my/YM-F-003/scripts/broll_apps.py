# B-roll "Apps Yuran.my.MP4": senarai Payments + ketuk -> resit PDF, dalam bingkai telefon, data peribadi & jumlah diblur.
# python3 broll_apps.py apps.mp4 out.mp4   (keluaran 1080x1920, 30 fps, 3.0 s)
import subprocess, sys, tempfile, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
A = (43.6, 1.4)        # senarai Payments, jari ketuk muat turun resit (spinner ±44.5)
B = (46.5, 1.6)        # resit PDF dibuka
SW, SH, SX, SY = 536, 1160, 272, 330     # skrin telefon dalam frame 1080x1920
# kawasan blur (koordinat sumber 592x1280)
LIST = [(135, y, 225, 42) for y in (245, 359, 473, 587, 701, 815, 929, 1043, 1157)]       # Amount + key
RCPT = [(15, 326, 185, 34), (200, 326, 120, 34), (40, 393, 405, 25), (535, 393, 52, 88)]   # pembayar, penerima, item (nama+IC), jumlah
CARD = (0, 236, 592, 250)                                                                    # kad resit untuk zoom

tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
# latar biru + bezel telefon dengan lubang skrin bersudut bulat
bg = Image.new("RGBA", (1080, 1920))
d = ImageDraw.Draw(bg)
for y in range(1920):
    k = y / 1919
    d.line([(0, y), (1080, y)], fill=(int(42 - 14 * k), int(59 - 19 * k), int(143 - 42 * k), 255))
d.rounded_rectangle((SX - 20, SY - 20, SX + SW + 20, SY + SH + 20), 60, fill=(17, 17, 17, 255))
hole = Image.new("L", (1080, 1920), 0)
ImageDraw.Draw(hole).rounded_rectangle((SX, SY, SX + SW, SY + SH), 44, fill=255)
bg.putalpha(Image.eval(hole, lambda v: 255 - v))
bg.save(f"{tmp}/frame.png")
# bayang kad resit
sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((30, 760, 910, 1136), 26, fill=(10, 16, 50, 110))
sh.save(f"{tmp}/shadow.png")

def blur(lbl, rects, inp):
    f, cur = [], inp
    for i, (x, y, w, h) in enumerate(rects):
        f.append(f"[{cur}]split[{lbl}a{i}][{lbl}b{i}];[{lbl}b{i}]crop={w}:{h}:{x}:{y},boxblur=luma_radius=8:luma_power=2:chroma_radius=6:chroma_power=2[{lbl}c{i}];[{lbl}a{i}][{lbl}c{i}]overlay={x}:{y}[{lbl}o{i}]")
        cur = f"{lbl}o{i}"
    return f, cur
f = [f"[0:v]trim=start={A[0]}:duration={A[1]},setpts=PTS-STARTPTS,fps=30[la]",
     f"[0:v]trim=start={B[0]}:duration={B[1]},setpts=PTS-STARTPTS,fps=30[rb]"]
g, la = blur("L", LIST, "la"); f += g
g, rb = blur("R", RCPT, "rb"); f += g
f.append(f"[{la}][{rb}]concat=n=2:v=1:a=0,split[scr][scr2]")
f.append(f"[scr]scale={SW}:{SH}[ss]")
f.append(f"color=c=0x2A3B8F:s=1080x1920:r=30:d=3.0[bg]")
f.append(f"[bg][ss]overlay={SX}:{SY}[p1];[p1][1:v]overlay=0:0[ph]")
# kad resit zoom: muncul 0.25 s selepas resit dibuka
t1 = A[1] + 0.25
CW = 860; CH = round(CARD[3] * CW / CARD[2])
f.append(f"[scr2]crop={CARD[2]}:{CARD[3]}:{CARD[0]}:{CARD[1]},scale={CW}:{CH}:flags=lanczos,format=rgba,fade=in:st={t1}:d=0.2:alpha=1[card]")
f.append(f"[2:v]format=rgba,fade=in:st={t1}:d=0.2:alpha=1[shd]")
f.append(f"[ph][shd]overlay=0:0:enable='gte(t,{t1})'[p2];[p2][card]overlay=40:{948 - CH // 2}:enable='gte(t,{t1})',format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-i", f"{tmp}/frame.png", "-loop", "1", "-i", f"{tmp}/shadow.png",
                "-filter_complex", ";".join(f), "-map", "[v]", "-t", "3.0", "-r", "30", "-c:v", "libx264", "-crf", "14", "-preset", "fast", out], check=True)
