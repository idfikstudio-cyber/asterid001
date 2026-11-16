"""Bokeh latar + subjek jernih untuk talking head.

python3 bokeh.py <in.mp4> <out.mp4> <selfie_multiclass.tflite> [scale]

- Segmentasi orang (MediaPipe selfie multiclass), topeng dilicinkan antara frame.
- Latar: blur bertumpu (normalized convolution) supaya warna badan tidak meleleh ke latar,
  kernel cakera (rasa lensa) + highlight sedikit kembang.
- Subjek: denoise ringan + unsharp mask (jernih) tanpa ubah warna kulit.
Output video sahaja (tanpa audio), yuv420p, CRF 16 (perantaraan).
"""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0

cap = cv2.VideoCapture(src)
W0, H0 = int(cap.get(3)), int(cap.get(4))
W, H = int(W0 * scale) // 2 * 2, int(H0 * scale) // 2 * 2
fps = cap.get(5) or 30

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), output_confidence_masks=True))

# Kernel cakera untuk bokeh (dikira pada 1/4 resolusi)
DS = 4
R = max(3, int(round(26 * W / 1080 / DS)))
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
disc = ((xx ** 2 + yy ** 2) <= R * R).astype(np.float32)
disc = cv2.GaussianBlur(disc, (0, 0), 0.8)
disc /= disc.sum()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                        "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", dst],
                       stdin=subprocess.PIPE)
prev = None
n = 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    if (W, H) != (W0, H0):
        f = cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    m = 1.0 - r.confidence_masks[0].numpy_view()[..., 0]  # 0 = background
    m = cv2.resize(m, (W, H))
    # licin temporal (kurangkan kelip pada tepi)
    m = m if prev is None else 0.6 * m + 0.4 * prev
    prev = m
    m = np.clip((m - 0.5) / 0.3, 0, 1)
    m = cv2.erode(m, np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 1.5 * W / 1080)

    ff = f.astype(np.float32) / 255
    # --- latar bokeh (normalized convolution pada 1/4 res) ---
    bgw = cv2.resize(1 - m, (W // DS, H // DS), interpolation=cv2.INTER_AREA)
    small = cv2.resize(ff, (W // DS, H // DS), interpolation=cv2.INTER_AREA)
    lin = small ** 2.2
    lum = lin.mean(axis=2, keepdims=True)
    lin = lin * (1 + 1.5 * np.clip(lum - 0.55, 0, 1))  # highlight kembang
    num = cv2.filter2D(lin * bgw[..., None], -1, disc)
    den = cv2.filter2D(bgw, -1, disc)[..., None]
    bg = np.clip(num / np.maximum(den, 1e-3), 0, 1) ** (1 / 2.2)
    bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_CUBIC)
    # sedikit grain supaya latar tak nampak 'plastik'
    bg += np.random.normal(0, 0.006, bg.shape).astype(np.float32)

    # --- subjek jernih ---
    den_f = cv2.bilateralFilter(f, 5, 18, 5).astype(np.float32) / 255
    blur = cv2.GaussianBlur(den_f, (0, 0), 1.4 * W / 1080)
    sharp = np.clip(den_f + 0.65 * (den_f - blur), 0, 1)
    out = sharp * m[..., None] + bg * (1 - m[..., None])
    enc.stdin.write((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    n += 1
    if n % 150 == 0:
        print(n, flush=True)
enc.stdin.close()
enc.wait()
print("done", n)
