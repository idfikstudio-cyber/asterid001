"""Jejak muka (MediaPipe BlazeFace) setiap 3 frame -> face.json untuk motion zoom fk_render.py.

python3 fk_face.py <in.mp4> <face.json> <blaze_face_short_range.tflite>
Format: {"n": jumlah frame, "pts": [[frame, x_pusat, y_pusat, lebar], ...]} (px @1080x1920)
"""
import sys, json, cv2, numpy as np, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, dst, model = sys.argv[1:4]
det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), min_detection_confidence=0.5))
cap = cv2.VideoCapture(src); n = 0; pts = []
while True:
    ok, f = cap.read()
    if not ok: break
    if n % 3 == 0:
        sx = 1080 / f.shape[1]
        small = cv2.resize(f, (f.shape[1] // 3, f.shape[0] // 3))
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))))
        if r.detections:
            b = max(r.detections, key=lambda d: d.bounding_box.width).bounding_box
            pts.append([n, round((b.origin_x + b.width / 2) * 3 * sx, 1), round((b.origin_y + b.height / 2) * 3 * sx, 1), round(b.width * 3 * sx)])
    n += 1
json.dump({"n": n, "pts": pts}, open(dst, "w"))
print("face", n, len(pts))
