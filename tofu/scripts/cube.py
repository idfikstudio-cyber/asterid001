"""Sample krpano cubemap faces (f,b,l,r,u,d) into perspective or equirect views."""
import cv2
import numpy as np

FACES = "fblrud"


def load_atlas(scene_dir):
    imgs = [cv2.imread(f"{scene_dir}/{f}.jpg") for f in FACES]
    n = imgs[0].shape[0]
    # 1px border per face (replicated) so bilinear sampling never bleeds across faces
    pad = [cv2.copyMakeBorder(im, 1, 1, 1, 1, cv2.BORDER_REPLICATE) for im in imgs]
    return np.hstack(pad), n


def dirs_to_map(x, y, z, n):
    """x right, y up, z forward -> remap coords into the atlas."""
    ax, ay, az = np.abs(x), np.abs(y), np.abs(z)
    face = np.select(
        [(az >= ax) & (az >= ay) & (z > 0), (az >= ax) & (az >= ay),
         (ax >= ay) & (x < 0), ax >= ay, y > 0],
        [0, 1, 2, 3, 4], 5)
    u = np.select([face == 0, face == 1, face == 2, face == 3, face == 4],
                  [x / az, -x / az, z / ax, -z / ax, x / ay], x / ay)
    v = np.select([face == 0, face == 1, face == 2, face == 3, face == 4],
                  [-y / az, -y / az, -y / ax, -y / ax, z / ay], -z / ay)
    px = (u + 1) * 0.5 * (n - 1) + 1 + face * (n + 2)
    py = (v + 1) * 0.5 * (n - 1) + 1
    return px.astype(np.float32), py.astype(np.float32)


def perspective(atlas, n, yaw, pitch, hfov, w, h):
    """yaw/pitch in degrees, krpano style (pitch positive = look down)."""
    f = (w / 2) / np.tan(np.radians(hfov) / 2)
    xs = (np.arange(w) - (w - 1) / 2)[None, :].repeat(h, 0)
    ys = -(np.arange(h) - (h - 1) / 2)[:, None].repeat(w, 1)
    zs = np.full((h, w), f)
    p, yw = np.radians(-pitch), np.radians(yaw)
    y2 = ys * np.cos(p) + zs * np.sin(p)
    z2 = -ys * np.sin(p) + zs * np.cos(p)
    x3 = xs * np.cos(yw) + z2 * np.sin(yw)
    z3 = -xs * np.sin(yw) + z2 * np.cos(yw)
    mx, my = dirs_to_map(x3, y2, z3, n)
    return cv2.remap(atlas, mx, my, cv2.INTER_LINEAR)


def equirect(atlas, n, w=4096):
    h = w // 2
    lon = (np.arange(w) / w - 0.5) * 2 * np.pi
    lat = (0.5 - np.arange(h) / h) * np.pi
    lon, lat = np.meshgrid(lon, lat)
    mx, my = dirs_to_map(np.cos(lat) * np.sin(lon), np.sin(lat), np.cos(lat) * np.cos(lon), n)
    return cv2.remap(atlas, mx, my, cv2.INTER_LINEAR)
