# Builds edit/sifir9/plan.json: the edited timeline ("E" time), board retime anchors,
# corrected word captions, motion-graphic cues and SFX cues. Everything else reads this.
import json, os, re
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
raw = json.load(open(os.path.join(ROOT, "edit/sifir9/transcript_raw.json")))

# ---- timeline: talk video is kept whole (quiz insert removed at the client's request, so E = talk time)
Q0, QD = 41.70, 0.0          # end of the board lesson (gap before "Nak kuasai sifir")
TALK_END = 56.10
END_CARD = 3.4
def e(t):                     # talk time -> edited time
    return t if t < Q0 else t + QD
DUR = round(e(TALK_END) + END_CARD, 2)
SPLIT = (9.20, Q0)            # board + face split screen
segments = [
    {"id": "intro", "t0": 0, "t1": SPLIT[0], "layout": "face", "label": "Hook + intro"},
    {"id": "lesson", "t0": SPLIT[0], "t1": Q0, "layout": "split", "label": "Ajar di papan"},
    {"id": "message", "t0": Q0 + QD, "t1": e(47.80), "layout": "face", "label": "Mesej: tak perlu hafal"},
    {"id": "cta", "t0": e(47.80), "t1": e(TALK_END), "layout": "face", "label": "CTA daftar 2027"},
    {"id": "end", "t0": e(TALK_END), "t1": DUR, "layout": "end", "label": "End card + TikTok"},
]
edl = [  # source pieces laid on E timeline (talk video)
    {"src": "talk", "s0": 0, "s1": TALK_END, "e0": 0},
    {"src": "hold", "frame": TALK_END - 0.05, "e0": e(TALK_END), "dur": END_CARD},
]

# ---- captions: fix Whisper mistakes, then shift to E time
FIX = {(21.90, "bintang"): "panah", (40.12, "20."): "27.", (35.24, "adalah"): "adalah"}
words = []
for s in raw:
    for w in s["words"]:
        txt = w["w"].strip()
        txt = FIX.get((round(w["s"], 2), txt), txt)
        txt = txt.replace(" x", " ×") if txt != "x" else "×"
        if txt.startswith("-") and words:  # "stres -stres" -> "stres-stres"
            words[-1]["w"] += txt; words[-1]["e"] = round(e(w["e"]), 2); continue
        words.append({"w": txt, "s": round(e(w["s"]), 2), "e": round(e(w["e"]), 2)})
for i, w in enumerate(words):  # make words contiguous within a phrase for karaoke
    if i + 1 < len(words) and words[i + 1]["s"] - w["e"] < 0.35:
        w["e"] = words[i + 1]["s"]
# phrases for caption lines (split on sentence end, max 4 words)
lines, cur = [], []
for w in words:
    cur.append(w)
    if w["w"].endswith((".", "?")) or (w["w"].endswith(",") and len(cur) >= 2) or len(cur) == 4:
        lines.append(cur); cur = []
if cur: lines.append(cur)
merged = []
for l in lines:  # a lone trailing word ("kan.", "18.") joins the line before it
    if merged and len(l) == 1 and l[0]["s"] - merged[-1][-1]["e"] < 0.6:
        merged[-1] += l
    else:
        merged.append(l)
lines = merged
captions = [{"s": l[0]["s"], "e": l[-1]["e"], "words": l} for l in lines]
# during counting the board + big numbers do the talking; no captions
NO_CAP = [(11.9, 21.2), (24.2, 31.05)]
captions = [c for c in captions if not any(a <= c["s"] < b for a, b in NO_CAP)]

# ---- board retime anchors (E time -> board source time). Board is a silent iPad
# screen recording; each anchor puts a stroke on the word that names it.
right = [(11.86, 9.05), (12.46, 10.15), (13.48, 11.25), (14.56, 12.45), (15.76, 13.35),
         (16.82, 14.65), (17.94, 15.45), (18.80, 16.25), (19.64, 17.10), (20.48, 19.40)]
left = [(24.22, 26.95), (24.90, 28.05), (25.78, 29.15), (26.42, 30.25), (27.12, 31.25),
        (27.60, 32.35), (28.24, 33.25), (29.20, 34.25), (29.72, 35.25), (30.46, 36.05)]
board_map = ([(SPLIT[0], 1.30), (10.90, 5.80)] + right + [(21.00, 19.95), (21.80, 22.75), (22.95, 24.35)]
             + left + [(31.00, 36.60), (31.45, 38.25), (32.45, 39.45), (35.70, 39.95),
                       "cut",  # board toolbar pops up at 40.0-43.8 (colour picker); jump over it
                       (35.71, 43.82), (37.00, 44.70), (37.55, 45.12), (38.30, 45.85),
                       (39.10, 46.50), (39.90, 47.20), (40.40, 48.35), (41.65, 51.70), (DUR, 51.75)])
BOARD = {"src_crop": [0, 60, 960, 1220], "dest": [0, 0, 1080, 1180], "mask_x_from": 800, "mask_top": 30,
         # digit-row centres in board source pixels (after the zoom at 17.9s)
         "rows_y": [320, 414, 511, 603, 690, 794, 904, 993, 1110, 1215],
         "col_x": {"up_arrow": 306, "left": 459, "right": 544, "down_arrow": 681}}
def board_xy(x, y):  # board source px -> output 1080x1920 px
    sx, sy, sw, sh = BOARD["src_crop"]; k = 1180 / sh; ox = (1080 - sw * k) / 2
    return round(ox + (x - sx) * k, 1), round((y - sy) * k, 1)
rows_out = [board_xy(0, y)[1] for y in BOARD["rows_y"]]

# ---- motion graphics (rendered by preview/sifir9/index.html, keyed by "kind")
mg = [
    {"kind": "hook", "s": 0.00, "e": 1.50, "text": ["NAK KUASAI", "SIFIR 9?"], "note": "Hook besar + punch-in"},
    {"kind": "bug", "s": 0.00, "e": e(TALK_END), "note": "Logo Aster Edu kecil, atas kiri"},
    {"kind": "fingers", "s": 1.54, "e": 4.00, "text": "Episod lepas: guna JARI", "note": "B-roll: animasi 10 jari, jari ke-4 dilipat = 36"},
    {"kind": "pencil", "s": 4.04, "e": 7.05, "text": "Hari ni: MENULIS je!", "note": "B-roll: pensel tulis '9 × ?'"},
    {"kind": "timer", "s": 7.10, "e": 9.20, "text": "< 3 MINIT", "note": "Jam randik berpusing"},
    {"kind": "split_in", "s": SPLIT[0], "e": SPLIT[0] + 0.5, "note": "Transisi ke papan"},
    {"kind": "step", "s": 9.30, "e": 21.20, "n": 1, "text": "Tulis 9 → 0 ke BAWAH"},
    {"kind": "count", "s": 11.86, "e": 21.10, "col": "right", "times": [a for a, _ in right], "note": "Nombor besar pop ikut sebutan"},
    {"kind": "arrow_hint", "s": 21.80, "e": 23.10, "dir": "down"},
    {"kind": "step", "s": 23.10, "e": 31.40, "n": 2, "text": "Tulis 9 → 0 NAIK ke atas"},
    {"kind": "count", "s": 24.22, "e": 31.00, "col": "left", "times": [a for a, _ in left]},
    {"kind": "arrow_hint", "s": 31.40, "e": 32.50, "dir": "up"},
    {"kind": "step", "s": 32.60, "e": Q0, "n": 3, "text": "Baca setiap baris = jawapan!"},
    {"kind": "eq", "s": 35.84, "e": Q0, "rows": [[0, 35.84], [1, 37.62], [2, 39.16]] + [[i, round(40.45 + (i - 3) * 0.17, 2)] for i in range(3, 10)],
     "rows_y_out": rows_out, "note": "Label '1 × 9 =' muncul di sebelah setiap baris"},
    {"kind": "strike", "s": e(43.95), "e": e(46.10), "hit": e(44.78), "text": "MENGHAFAL", "note": "'Tak semestinya MENGHAFAL' dipangkah"},
    {"kind": "chill", "s": e(46.10), "e": e(47.80), "text": "Jangan stres! 😌"},
    {"kind": "lower", "s": e(47.88), "e": e(50.60), "title": "MATH TURBO 2027", "sub": "Pelbagai teknik kuasai Matematik"},
    {"kind": "badge", "s": e(50.62), "e": e(53.90), "hit": e(52.50), "text": "Pendaftaran 2027 dibuka 🔥"},
    {"kind": "price", "s": e(53.95), "e": e(TALK_END), "text": "RM20", "sub": "booking sahaja"},
    {"kind": "dm", "s": e(54.94), "e": e(TALK_END), "note": "Kad profil TikTok + butang DM/Follow ditekan"},
    {"kind": "end", "s": e(TALK_END), "e": DUR},
    {"kind": "comment", "s": e(46.55), "e": e(50.40), "text": "Komen jawapan 8 × 9 👇", "note": "Ajak komen (interaktif)"},
]

# ---- sound effects (files in edit/sifir9/sfx, gain in dB)
sfx = [("whoosh", 0.00, -4), ("impact", 0.30, -6), ("pop", 1.60, -6), ("click", 2.70, -8), ("click", 3.05, -8),
       ("whoosh", 4.04, -8), ("scribble", 4.40, -10), ("tick", 7.15, -6), ("ding", 8.40, -10),
       ("swoosh_up", SPLIT[0] - 0.15, -6), ("scribble", 9.40, -12)]
for t, _ in right + left:
    sfx += [("scribble_s", round(t + 0.02, 2), -13), ("pop", round(t + 0.05, 2), -15)]
sfx += [("swoosh_down", 21.85, -7), ("swoosh_up", 31.45, -7)]
for _, t in [(0, 35.84), (1, 37.62), (2, 39.16)]:
    sfx += [("marker", round(t - 0.08, 2), -10), ("ding", round(t + 0.9, 2), -16)]
sfx += [("marker", 40.40, -12)] + [("pop", round(40.45 + i * 0.17, 2), -14) for i in range(7)]
sfx += [("whoosh", Q0 - 0.05, -8),
        ("bonk", e(44.78), -6), ("pop", e(46.15), -10), ("pop", e(46.60), -12),
        ("whoosh", e(47.85), -8), ("impact", e(52.50), -10), ("chaching", e(54.00), -6),
        ("click", e(55.25), -6), ("pop", e(55.40), -10), ("riser", e(TALK_END) - 1.2, -12), ("impact", e(TALK_END) + 0.05, -8)]
sfx = [{"f": f, "t": round(t, 2), "db": db} for f, t, db in sorted(sfx, key=lambda x: x[1])]

plan = {"dur": DUR, "quiz": {"t0": Q0, "dur": QD}, "segments": segments, "edl": edl,
        "board": {**BOARD, "map": board_map, "rows_y_out": rows_out,
                  "up_arrow_x_out": board_xy(BOARD["col_x"]["up_arrow"], 0)[0]},
        "captions": captions, "mg": mg, "sfx": sfx,
        "music": {"bpm": 100, "duck_db": -9, "base_db": -15}}
json.dump(plan, open(os.path.join(ROOT, "edit/sifir9/plan.json"), "w"), ensure_ascii=False, indent=1)
print("dur", DUR, "captions", len(captions), "sfx", len(sfx), "rows_out", rows_out, "upx", plan["board"]["up_arrow_x_out"])
