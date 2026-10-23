# Build edit plan for AS-F-001_pendaftaran-2027 (Aster, BOFU) from the Whisper transcript.
# All times in "pops", "boards", "zoom", "captions" are SOURCE seconds; output = source + intro (1 s thumbnail).
# usage: python3 aster_plan.py <transcript.json> <plan.json> <audio.wav>
import json, re, sys
d = json.load(open(sys.argv[1]))

# spelling per script / brand DNA / rujukan-aster.txt (caption follows what was SAID)
FIX = {"tuition": "tuisyen", "sipir": "sifir", "Dr.": "Dr", "Syukri": "Shukri", "paket": "pakej", "4,": "4,"}
W = []
for s in d:
    for w in s["words"]:
        t = w["w"].strip(); t = FIX.get(t, t)
        if t.startswith("-") and W: W[-1]["w"] += t; W[-1]["e"] = w["e"]; continue
        W.append({"w": t, "s": w["s"], "e": w["e"]})

KEEP = [("Dr", "Shukri"), ("Shukri", "Abdullah."), ("RM99", "sahaja."), ("RM20", "sahaja"), ("tahun", "2027."), ("penyelesaian", "masalah.")]
BREAK = [("dan", "penyelesaian"), ("rendah", "tahun")]
chunks, cur = [], []
for i, w in enumerate(W):
    cur.append(w); nxt = W[i + 1] if i + 1 < len(W) else None
    glue = nxt and (w["w"], nxt["w"]) in KEEP
    if nxt and (w["w"], nxt["w"]) in BREAK:
        chunks.append({"s": cur[0]["s"], "words": [re.sub(r"[.,]$", "", x["w"]) for x in cur], "end_word": w["e"]}); cur = []; continue
    long_ = sum(len(x["w"]) + 1 for x in cur) >= 15
    if not nxt or (not glue and (len(cur) >= 3 or long_ or re.search(r"[.,]$", w["w"]) or nxt["s"] - w["e"] > 0.4)):
        chunks.append({"s": cur[0]["s"], "words": [re.sub(r"[.,]$", "", x["w"]) for x in cur], "end_word": w["e"]}); cur = []
for a, b in zip(chunks, chunks[1:]): a["e"] = b["s"] if b["s"] - a["end_word"] < 0.6 else a["end_word"] + 0.2
chunks[-1]["e"] = chunks[-1]["end_word"] + 0.35
for c in chunks: c.pop("end_word")

HIGHLIGHT = ["RM99", "RM20", "BM", "BI", "Math", "Science", "Sejarah", "sifir", "4P", "problem", "2027"]

pops = [
    {"kind": "big", "s": 2.14, "e": 3.62, "text": "TAHUN 4, 5 & 6", "sub": "SEKOLAH RENDAH", "size": 112},
    {"kind": "big", "s": 5.10, "e": 6.30, "text": "2027", "size": 160, "y": 1235},
    {"kind": "big", "s": 6.60, "e": 8.45, "text": "7 PROGRAM", "sub": "SATU PAKEJ", "sub_top": False, "y": 1165, "size": 130},
    {"kind": "big", "s": 8.50, "e": 9.84, "text": "RM99", "size": 180, "y": 1235},
    {"kind": "big", "s": 14.36, "e": 16.25, "text": "2 PROGRAM", "sub": "TAMBAHAN", "sub_top": False, "y": 1165, "size": 130},
    {"kind": "chips", "s": 16.32, "e": 18.50, "chips": [{"t": 16.32, "text": "Pengukuhan Sifir"}, {"t": 17.68, "text": "4P"}]},
    {"kind": "warn", "s": 22.95, "e": 23.85, "x": 790, "y": 690},
    {"kind": "person", "s": 26.96, "e": 30.20, "name": "Dr Shukri Abdullah", "sub": "Pakar Motivasi Pendidikan"},
    {"kind": "big", "s": 30.36, "e": 32.15, "text": "RM20", "sub": "PENDAFTARAN", "size": 190},
    {"kind": "dm", "s": 32.20, "e": 33.62},
    {"kind": "big", "s": 34.62, "e": 35.95, "text": "2027", "sub": "JUMPA", "size": 160},
]
boards = [
    {"s": 9.84, "e": 12.84, "title": "Subjek", "cols": 3, "items": [
        {"t": 9.86, "text": "BM"}, {"t": 10.22, "text": "BI"}, {"t": 10.70, "text": "Math"},
        {"t": 11.06, "text": "Science"}, {"t": 11.50, "text": "Sejarah"}]},
    {"s": 18.55, "e": 21.55, "title": "4P", "cols": 2, "big_first": True, "items": [
        {"t": 18.68, "text": "Perpuluhan"}, {"t": 19.38, "text": "Pecahan"},
        {"t": 20.00, "text": "Peratus", "pos": [1, 0]}, {"t": 20.72, "text": "Penyelesaian Masalah", "pos": [2, 0]}]},
]
# punch-in: alternate 100 % / 113 % at sentence boundaries; 113 % (anchored at the bottom) lifts the face for boards
zoom = [{"s": a, "e": b, "scale": s} for a, b, s in [
    (0, 6.0, 1.0), (6.0, 9.83, 1.0), (9.83, 13.63, 1.13), (13.63, 18.5, 1.0), (18.5, 21.86, 1.13), (21.86, 23.84, 1.0),
    (23.84, 28.4, 1.13), (28.4, 30.21, 1.0), (30.21, 32.13, 1.13), (32.13, 33.62, 1.0), (33.62, 99, 1.13)]]

INTRO = 1.0
sfx = [(-0.08, "whoosh", .30), (0.25, "swoosh_down", .22),
       (2.14, "pop", .40), (5.10, "pop", .32), (6.60, "pop", .40), (8.50, "chaching", .32),
       (9.84, "whoosh", .28), (9.95, "click", .45), (10.31, "click", .45), (10.79, "click", .45), (11.15, "click", .45), (11.59, "ding", .22),
       (14.36, "pop", .40), (16.32, "pop", .35), (17.68, "pop", .35),
       (18.55, "whoosh", .28), (18.83, "click", .45), (19.53, "click", .45), (20.15, "click", .45), (20.87, "ding", .22),
       (22.95, "bonk", .28), (26.96, "swoosh_down", .28), (30.36, "chaching", .32), (32.20, "pop", .40), (34.62, "ding", .25)]
sfx = [{"t": round(t + INTRO, 3), "name": n, "gain": g} for t, n, g in sfx] + [{"t": INTRO + 36.01, "name": "whoosh", "gain": .28}, {"t": INTRO + 36.15, "name": "ding", "gain": .22}]

plan = {
    "id": "AS-F-001", "topik": "pendaftaran-2027", "jenis": "BOFU",
    "intro": INTRO, "outro": 1.5, "src_duration": 36.0,
    "watermark": "asteredu11.com.my", "wm_xy": [72, 236], "whatsapp": "011-5596 9070",
    "label": ["Cikgu AlFarhan", " · Aster Edu"], "label_t": [1.25, 4.3], "label_y": 300,
    "cta": ["WhatsApp Cikgu AlFarhan", "untuk daftar / cuba kelas"],
    "caption_y": 1420, "pop_y": 1200, "board_y": 1000,
    "zoom_anchor": [410, 1920], "zoom": zoom,
    "thumb": {"src_t": 31.15, "zoom": 1.13, "y": 1060, "lines": [{"text": "TUISYEN 2027", "size": 132}, {"text": "RM99 SAHAJA", "size": 150, "hot": True}]},
    "highlight": HIGHLIGHT, "captions": chunks, "pops": pops, "boards": boards, "sfx": sfx,
    "audio_path": sys.argv[3],
}
json.dump(plan, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for c in chunks: print(f'{c["s"]:6.2f}-{c["e"]:6.2f}  {" ".join(c["words"])}')
