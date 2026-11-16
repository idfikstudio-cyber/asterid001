"""Panorama AIHouse 720 (cubemap krpano) -> klip B-roll 9:16 dengan pan kamera perlahan.

python3 fk_pano.py <cube_dir> <out.mp4> <saat> <yaw0> <yaw1> [pitch] [fov] [--equi preview.jpg]
- cube_dir: show_f/b/l/r/u/d.jpg (dari https://3vj-render.3vjia.com/.../DesignSchemeRenderCutFile/.../show_%s.jpg)
- yaw dalam darjah (0 = muka depan 'f', +90 = kanan 'r'), pitch + = pandang bawah, fov = sudut mendatar.
Rakaman terus dari imej panorama: tiada UI viewer, tiada nama projek/client dalam frame.
DNA Fi-k 7.6: pan perlahan, 9:16.
"""
import sys, subprocess, numpy as np, cv2

EQUI = sys.argv[sys.argv.index("--equi") + 1] if "--equi" in sys.argv else None
A = sys.argv[1:sys.argv.index("--equi")] if EQUI else sys.argv[1:]
d, dst, dur, y0, y1 = A[0], A[1], float(A[2]), float(A[3]), float(A[4])
pitch = float(A[5]) if len(A) > 5 else 8.0
fov = float(A[6]) if len(A) > 6 else 62.0
W, H, FPS = 1080, 1920, 30
F = {k: cv2.imread(f"{d}/show_{k}.jpg") for k in "fbrlud"}
S = F["f"].shape[0]

# --- cubemap -> equirect (sekali) ---
EW, EH = 6000, 3000
lon = (np.arange(EW) + 0.5) / EW * 2 * np.pi - np.pi
lat = np.pi / 2 - (np.arange(EH) + 0.5) / EH * np.pi
lon, lat = np.meshgrid(lon, lat)
x = np.cos(lat) * np.sin(lon); y = np.sin(lat); z = np.cos(lat) * np.cos(lon)
ax, ay, az = np.abs(x), np.abs(y), np.abs(z)
eq = np.zeros((EH, EW, 3), np.uint8)
def put(mask, face, u, v):
    mx = ((u + 1) / 2 * S - 0.5).astype(np.float32); my = ((v + 1) / 2 * S - 0.5).astype(np.float32)
    r = cv2.remap(F[face], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    eq[mask] = r[mask]
with np.errstate(divide="ignore", invalid="ignore"):
    m = (az >= ax) & (az >= ay) & (z > 0); put(m, "f", x / az, -y / az)
    m = (az >= ax) & (az >= ay) & (z <= 0); put(m, "b", -x / az, -y / az)
    m = (ax > az) & (ax >= ay) & (x > 0); put(m, "r", -z / ax, -y / ax)
    m = (ax > az) & (ax >= ay) & (x <= 0); put(m, "l", z / ax, -y / ax)
    m = (ay > az) & (ay > ax) & (y > 0); put(m, "u", x / ay, z / ay)
    m = (ay > az) & (ay > ax) & (y <= 0); put(m, "d", x / ay, -z / ay)
if EQUI:
    cv2.imwrite(EQUI, cv2.resize(eq, (2000, 1000)))
    sys.exit(0)

# --- perspektif 9:16 bergerak ---
f = (W / 2) / np.tan(np.radians(fov) / 2)
px, py = np.meshgrid(np.arange(W) - W / 2 + 0.5, np.arange(H) - H / 2 + 0.5)
rays = np.stack([px / f, -py / f, np.ones_like(px)], -1)
rays /= np.linalg.norm(rays, axis=-1, keepdims=True)
def ease(t): return t * t * (3 - 2 * t)
N = int(round(dur * FPS))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
for k in range(N):
    e = ease(k / max(1, N - 1))
    yaw, pt = np.radians(y0 + (y1 - y0) * e), np.radians(pitch)
    cp, sp, cy, sy = np.cos(pt), np.sin(pt), np.cos(yaw), np.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])     # pitch + = pandang bawah
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    v = rays @ (Ry @ Rx).T
    lo = np.arctan2(v[..., 0], v[..., 2]); la = np.arcsin(np.clip(v[..., 1], -1, 1))
    mx = ((lo + np.pi) / (2 * np.pi) * EW - 0.5).astype(np.float32)
    my = ((np.pi / 2 - la) / np.pi * EH - 0.5).astype(np.float32)
    enc.stdin.write(cv2.remap(eq, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP).tobytes())
enc.stdin.close(); enc.wait()
print("ok", dst, N)
