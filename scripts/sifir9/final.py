# Final render: base composite (comp.py at 1080) + punch-in zoom + graphics frames
# (render_overlay.js) + mixed audio (mix.py), H.264/AAC 1080x1920 30fps.
# usage: final.py <base_1080.mp4> <overlay dir> <audio dir> <out.mp4>
import json, os, subprocess, sys
import numpy as np
from PIL import Image
base, ovdir, audir, out = sys.argv[1:5]
W, H, FPS = 1080, 1920, 30
zoom = json.load(open(os.path.join(ovdir, "zoom.json")))
n = len(zoom)

def frames(cmd, ch):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); sz = W * H * ch
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz: return
        yield np.frombuffer(b, np.uint8).reshape(H, W, ch)

bf = frames(["ffmpeg", "-v", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], 3)
of = frames(["ffmpeg", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(ovdir, "o_%05d.png"),
             "-f", "rawvideo", "-pix_fmt", "rgba", "-"], 4)

mix = os.path.join(audir, "final_mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(audir, "voice_clean.wav"), "-i", os.path.join(audir, "sfx.wav"),
                "-i", os.path.join(audir, "music.wav"), "-filter_complex",
                "amix=inputs=3:normalize=0,alimiter=limit=0.9:attack=3:release=50,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000",
                "-ar", "48000", mix], check=True)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                        "-profile:v", "high", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for i in range(n):
    b = next(bf, None); o = next(of, None)
    if b is None or o is None: break
    z = zoom[i]
    if z > 1.0005:  # CSS scale with transform-origin 50% 40%
        w, h = W / z, H / z; x0, y0 = (W - w) * 0.5, (H - h) * 0.4
        b = np.asarray(Image.fromarray(b).resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h)))
    a = o[..., 3:4].astype(np.float32) / 255
    if a.max() > 0:
        b = (b.astype(np.float32) * (1 - a) + o[..., :3].astype(np.float32) * a + 0.5).astype(np.uint8)
    enc.stdin.write(np.ascontiguousarray(b).tobytes())
    if i % 300 == 0: print(f"{i}/{n}", flush=True)
enc.stdin.close(); enc.wait()
print("wrote", out)
