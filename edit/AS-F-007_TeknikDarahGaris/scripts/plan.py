# Edit plan for AS-F-006_TeknikDarahGaris (TOFU). All times in SOURCE seconds unless noted.
import json, re, os
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(S, "work")

# --- cuts: silences > 0.3 s shortened to ~0.2 s (footage already trimmed by Farhan)
KEEP = [(0.0, 33.08), (33.25, 49.43), (49.58, 61.41), (61.69, 110.95)]
THUMB = 1.0
END = 1.5

def src2c(t):
    """source time -> content time (seconds after the 1 s thumbnail)"""
    acc = 0.0
    for a, b in KEEP:
        if t < a: return acc
        if t <= b: return acc + (t - a)
        acc += b - a
    return acc
CONTENT = sum(b - a for a, b in KEEP)
TOTAL = THUMB + CONTENT + END
def o(t):  # source -> output timeline
    return THUMB + src2c(t)

# --- split screen (B-roll top) ranges, source time
SPLIT = (20.10, 86.95)
# source time -> B-roll time keypoints (piecewise linear; equal src times = jump)
BMAP = [(20.10, 74.0), (25.6, 85.5), (30.0, 97.0), (32.9, 99.5), (32.91, 102.2), (35.2, 109.0), (38.1, 128.0),
        (40.8, 131.5), (45.4, 137.5), (50.0, 143.5), (52.6, 148.0),
        (52.65, 151.0), (56.2, 153.8), (56.21, 160.5), (56.25, 165.0), (62.3, 179.0), (65.9, 179.5),
        (65.91, 206.0), (67.5, 215.0), (69.8, 215.2), (69.81, 219.2), (71.4, 223.5), (76.2, 231.5), (78.4, 239.2),
        (82.4, 240.4), (86.0, 241.3), (87.0, 241.4)]
def broll_t(ts):
    for (a, x), (b, y) in zip(BMAP, BMAP[1:]):
        if a <= ts <= b and b > a:
            return x + (y - x) * (ts - a) / (b - a)
    return BMAP[-1][1]

# --- punch-in zoom (full-frame talking head), source ranges
ZOOM = [(0.0, 10.15, 1.18), (10.15, 20.10, 1.32), (86.95, 97.15, 1.18), (97.15, 106.72, 1.32), (106.72, 120, 1.18)]
SPLITZOOM = [(20.10, 52.65, 1.0), (52.65, 87.0, 1.1)]

# --- transcript -> captions
tr = json.load(open(os.path.join(W, "transcript.json")))
words = []
for s in tr:
    for w in s["words"]:
        t = w["w"].strip()
        if t.startswith("-") and words:  # anak -anak -> anak-anak
            words[-1]["w"] += t; words[-1]["e"] = w["e"]; continue
        words.append({"w": t, "s": w["s"], "e": w["e"]})
FIX = {"Ok": "OK", "Belisha": "Badli Shah"}
out = []
for w in words:
    if w["w"] in FIX:
        if FIX[w["w"]] is None: continue
        w["w"] = FIX[w["w"]]
    out.append(w)
words = out
HL = re.compile(r"^(\d+|RM\d+|SIFIR|SUSAH|LEMAH|MATH|MATEMATIK|SUBJEK|GARISAN|GARIS|MUDAH|DARJAH|TRIK|JAWAPAN|BERTEMU|25)$")
caps = []
cur = []
FORCE = {89.04, 0.98, 1.84, 3.44, 4.16, 11.42, 12.12, 13.94, 14.84, 15.82, 51.12, 54.54, 55.24, 103.32}
NOBREAK = {89.84, 90.14, 90.32, 2.62, 2.88, 3.12, 11.88, 12.06, 21.78, 51.58, 52.04, 54.86, 55.08, 57.46, 88.44, 103.62}
def flush():
    if cur:
        caps.append({"s": cur[0]["s"], "e": cur[-1]["e"], "words": [c["w"] for c in cur]})
    cur.clear()
for i, w in enumerate(words):
    starter = w["w"] in ("Jadi","So","Kalau","Kita","Nanti","Jadinya","Total","Cari","Contoh","Jangan","Anak-anak","DM","Ni","Macam","Ok","OK","sekarang")
    k = round(w["s"], 2)
    if cur and k in FORCE:
        flush()
    elif cur and k in NOBREAK:
        pass
    elif cur and (w["s"] - cur[-1]["e"] > 0.35 or len(cur) >= 4 or (starter and len(cur) >= 2)):
        flush()
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    end_p = w["w"][-1] in ".?"
    if nxt is not None and round(nxt["s"], 2) in NOBREAK:
        continue
    if end_p or (w["w"].endswith(",") and len(cur) >= 2 and not re.match(r"^\d", w["w"])):
        flush()
flush()
for i, c in enumerate(caps):
    nxt = caps[i + 1]["s"] if i + 1 < len(caps) else c["e"] + 0.5
    c["e2"] = min(nxt, c["e"] + 0.6)
    toks = []
    for t in c["words"]:
        t2 = t.rstrip(".,") if t != c["words"][-1] or not t.endswith("?") else t
        if t2.endswith(",") : pass
        toks.append(t2)
    # keep commas between counted digits, drop trailing punctuation on last word except '?'
    last = toks[-1]
    toks[-1] = last.rstrip(".,")
    if c["words"][-1].endswith("?"): toks[-1] = toks[-1].rstrip("?") + "?"
    # restore commas inside counting runs
    raw = c["words"]
    toks = [(r.rstrip(".") if j < len(raw) - 1 else toks[-1]) for j, r in enumerate(raw)]
    c["toks"] = [t.upper() for t in toks]
    c["hl"] = [bool(HL.match(re.sub(r"[^\w]", "", t.upper()))) for t in toks]
    c["text"] = " ".join(toks)

# --- overlay elements (source times; kind-specific params)
E = []
def el(s, e, kind, **kw): E.append(dict(s=s, e=e, kind=kind, **kw))
el(0.20, 3.20, "namepill", text="Cikgu AlFarhan")
el(11.40, 13.10, "bignum", text="321 × 3", y=1000)
el(13.18, 20.05, "note", head="MASALAH SEBENAR", lines=[(13.18, "Tak tahu sifir 3"), (15.80, "... susah nak jawab")])
# split-screen teaching
el(24.70, 30.05, "step", n=1, text="Buat garisan ikut digit")
el(30.08, 35.35, "step", n=2, text="Kali dengan 3: buat 3 garisan")
el(35.42, 50.10, "step", n=3, text="Kira garis yang bertemu")
el(40.60, 45.10, "counter", text="3", x=760)
el(45.20, 49.65, "counter", text="6", x=640)
el(49.70, 51.05, "counter", text="9", x=520)
el(51.10, 52.70, "answer", text="321 × 3 = 963")
el(54.50, 56.20, "bignum_panel", text="241 × 4")
el(56.22, 62.35, "step", n=1, text="Buat garisan ikut digit")
el(62.40, 67.50, "step", n=2, text="Kali dengan 4: buat 4 garis")
el(68.08, 83.90, "step", n=3, text="Cari garis yang bertemu")
el(70.60, 71.80, "counter", text="4", x=760)
el(75.98, 78.40, "counter", text="16", x=640)
el(76.36, 81.50, "carry", text="16: tulis 6, angka 1 naik ke atas")
el(81.60, 83.90, "counter", text="9", x=520)
el(83.94, 86.95, "answer", text="241 × 4 = 964")
el(52.80, 55.90, "follow", pos=(70, 640))
el(87.74, 94.45, "photo", name="Ustaz Badli Shah", role="Timbalan Mufti Pahang", quote="Kalau plan A tak jadi, masih ada 25 lagi alphabet untuk kita boleh guna", qt=88.90)
el(97.20, 106.70, "lowerthird", text="MATH TURBO 2027")
el(100.12, 101.55, "redpill", text="Pendaftaran 2027 dibuka")
el(101.58, 103.25, "price", text="RM20", sub="Pendaftaran serendah")
el(103.32, 106.70, "subjects", head="5 SUBJEK", items=[(104.18, "BM"), (104.74, "BI"), (105.18, "Math"), (105.58, "Science"), (106.14, "Sejarah")])
el(106.76, 110.95, "dmpill", text="DM saya untuk keterangan lanjut")

# --- SFX (OUTPUT timeline seconds, name, gain dB)
SFX = [(0.02, "pop", -6), (0.98, "whoosh", -8)]
def sx(src_t, name, g=-8): SFX.append((o(src_t), name, g))
sx(0.20, "pop", -10)
sx(11.40, "pop"); sx(13.18, "whoosh"); sx(15.80, "pop", -10)
sx(20.10, "whoosh", -6)
for t in (24.70, 30.08, 35.42, 56.22, 62.40, 68.08): sx(t, "click", -6)
for t in (40.60, 45.20, 49.70, 70.60, 75.98, 81.60): sx(t, "pop", -9)
sx(51.10, "ding", -8); sx(54.50, "whoosh", -8); sx(83.94, "ding", -8)
sx(52.80, "pop", -8); sx(76.36, "pop", -9)
sx(86.95, "swoosh_down", -8); sx(87.74, "whoosh", -8)
sx(88.90, "pop", -10); sx(94.45, "whoosh", -10)
sx(97.20, "whoosh", -9); sx(100.12, "pop", -9)
sx(101.58, "chaching", -9)
for t in (103.32, 104.18, 104.74, 105.18, 105.58, 106.14): sx(t, "pop", -11)
sx(106.76, "pop", -9)
SFX.append((THUMB + CONTENT, "whoosh", -8))

THUMB_SRC = 52.40
HOOK = ("TAK HAFAL SIFIR?", "GUNA GARISAN!")

if __name__ == "__main__":
    print("content", round(CONTENT, 2), "total", round(TOTAL, 2))
    for c in caps: print(f"{o(c['s']):6.2f} {c['text']}")
