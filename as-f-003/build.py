# AS-F-003 SoalanMath: bina timeline (EDL, caption, grafik, SFX, zoom, peta b-roll) dari transkrip.
# usage: python3 build.py transcript.json timeline.json
import json, re, sys

tr = json.load(open(sys.argv[1]))
SRC_END = 94.18  # hujung rakaman: harga disebut sampai habis
THUMB, OUTRO = 1.0, 1.5

# ---- EDL: footage sudah ditrim oleh Farhan; hanya senyap >0.3 s dibuang (silencedetect -32 dB), padding 0.1 s
SIL = [(4.383, 4.766), (14.227, 14.691), (16.349, 16.722), (24.062, 24.519), (25.970, 26.318),
       (31.245, 31.586), (38.333, 38.671), (45.587, 45.888), (70.809, 71.323), (72.824, 75.040)]
PAD = 0.1
keep, t = [], 0.0
for a, b in SIL:
    if b - a - 2 * PAD > 0.1:
        keep.append((t, a + PAD)); t = b - PAD
keep.append((t, SRC_END))
# jump cut asal dalam footage (sudah ditrim) – digunakan untuk punch-in
JUMPS = [8.23, 10.73, 21.67, 27.27, 42.80, 47.30, 48.47, 57.10, 64.33, 78.53, 81.80, 85.73, 87.17, 90.97]

def s2o(s):
    """masa sumber -> masa output (termasuk thumbnail 1 s)"""
    o = THUMB
    for a, b in keep:
        if s < a: return o
        if s <= b: return o + s - a
        o += b - a
    return o
CONTENT = sum(b - a for a, b in keep)
DUR = THUMB + CONTENT + OUTRO

# ---- perkataan + pembetulan ejaan
FIX = {"RM69": "RM99", "belajar": "Darjah",  # RM99 disahkan Farhan
       "rumah": "rendah", "tuition": "tuisyen", "syllabus": "silibus", "So": "So,"}
W = []
for sg in tr:
    for w in sg["words"]:
        x = w["w"].strip()
        if w["s"] >= SRC_END: continue
        if x.startswith("-") and W: W[-1]["w"] += x; W[-1]["e"] = w["e"]; continue
        base = re.sub(r"[.,?!]$", "", x)
        if base in FIX: x = FIX[base] + x[len(base):] if FIX[base][-1] not in ",." else FIX[base]
        if base in ("x", "X"):  # Farhan sebut "kali dengan" (disahkan transkrip berasingan)
            m = (w["s"] + w["e"]) / 2
            W.append({"w": "kali", "s": w["s"], "e": m, "orig": "x"}); W.append({"w": "dengan" + x[1:], "s": m, "e": w["e"], "orig": "x"}); continue
        d = {"w": x, "s": w["s"], "e": w["e"]}
        if base in FIX: d["orig"] = base
        W.append(d)
    if W: W[-1]["end"] = True  # hujung segmen Whisper = hujung ayat
# "2, 6, 4" / "5 2 8" disebut digit demi digit -> caption satu nombor
def merge_digits(ws, i, n, txt):
    ws[i:i + n] = [{"w": txt, "s": ws[i]["s"], "e": ws[i + n - 1]["e"], "end": True, "orig": " ".join(x["w"] for x in ws[i:i + n])}]
for k in range(len(W) - 2):
    trio = [re.sub(r"[.,]", "", W[k + j]["w"]) for j in range(3)] if k + 2 < len(W) else []
    if trio == ["2", "6", "4"]: merge_digits(W, k, 3, "2, 6, 4.");
    if trio == ["5", "2", "8"]: merge_digits(W, k, 3, "5, 2, 8.")

HOT = {"Darjah", "masalah", "darab", "mudah", "tambah", "jawapan", "Senang", "DM", "RM20", "RM69", "RM99", "percuma", "jadual", "silibus",
       "4", "5", "6", "2", "8", "12", "22", "24", "32", "264", "528", "2, 6, 4", "5, 2, 8", "kedua", "pertama", "Sama", "1"}
# caption: 1–4 perkataan, pecah ikut tanda baca / jeda > 0.35 s
caps, cur = [], []
for i, w in enumerate(W):
    cur.append(w); nx = W[i + 1] if i + 1 < len(W) else None
    if len(cur) >= 3 or w.get("end") or re.search(r"[.,?!]$", w["w"]) or not nx or nx["s"] - w["e"] > 0.35:
        caps.append(cur); cur = []
# gabung caption satu perkataan pendek dengan seterusnya jika rapat (maks 4)
C = []
for c in caps:
    if C and len(C[-1]) == 1 and len(C[-1] + c) <= 4 and c[0]["s"] - C[-1][-1]["e"] < 0.25 and not C[-1][-1].get("end") and not re.search(r"[.?!]$", C[-1][-1]["w"]):
        C[-1] = C[-1] + c
    else: C.append(c)
captions = []
for i, c in enumerate(C):
    s = s2o(c[0]["s"]); e = s2o(C[i + 1][0]["s"]) if i + 1 < len(C) and s2o(C[i + 1][0]["s"]) - s2o(c[-1]["e"]) < 0.4 else s2o(c[-1]["e"]) + 0.15
    captions.append({"s": round(s, 3), "e": round(THUMB + CONTENT if i == len(C) - 1 else min(e, THUMB + CONTENT), 3), "src": round(c[0]["s"], 2),
                     "w": [{"t": re.sub(r"(?<=\D)[.,]$|^(.*\d)[.]$", lambda m: m.group(1) or "", x["w"]).rstrip(","), "hl": re.sub(r"[.,?!]", "", x["w"]) in HOT or x["w"].rstrip(".") in HOT,
                            **({"fix": x["orig"]} if "orig" in x else {})} for x in c]})

# ---- layout: talking head penuh / skrin terbelah (papan iPad atas, Cikgu bawah)
SPLIT = (10.64, 81.76)
# ---- peta b-roll (masa sumber cakap -> masa rakaman iPad), dipadan ikut setiap coretan
BMAP = [(10.64, 0.5), (14.08, 3.9), (17.6, 8.6), (18.9, 9.8), (20.0, 10.6), (25.5, 15.8), (26.62, 16.6), (27.3, 27.0), (28.88, 28.1),
        (37.9, 31.4), (39.9, 33.4), (41.0, 35.4), (43.9, 40.4), (46.0, 42.9), (47.2, 44.1), (48.6, 46.3), (50.6, 49.4), (51.3, 51.7),
        (52.6, 58.3), (54.0, 60.2), (55.3, 66.3), (56.6, 68.2), (58.2, 75.8), (61.8, 76.8), (63.6, 78.2), (65.0, 83.7), (66.9, 87.3),
        (68.6, 91.2), (70.4, 92.6), (70.85, 93.0), (75.0, 95.6), (76.6, 96.4), (78.1, 97.6), (81.76, 101.0)]

def S(a, b): return [round(s2o(a), 3), round(s2o(b), 3)]
G = []
def g(t0, t1, kind, **kw): G.append({"s": round(s2o(t0), 3), "e": round(s2o(t1), 3), "kind": kind, **kw})
# Intro
g(0.15, 3.3, "label", text="Cikgu AlFarhan")
g(2.70, 6.9, "pill", text="Darjah 4 · 5 · 6", icon="school")
g(4.70, 8.2, "note", title="Masalah sebenar", lines=["Jawab soalan", "darab 2 nombor"])
g(8.18, 10.64, "today", head="Hari ni", text="Cara MUDAH jawab darab 2 nombor")
# Skrin terbelah
g(*SPLIT, "split", bar="DARAB 2 NOMBOR · CIKGU ALFARHAN")
g(10.64, 46.6, "qtag", text="SOALAN 1")
g(48.34, 70.85, "qtag", text="SOALAN 2")
g(75.04, 81.76, "qtag", text="CUBA SENDIRI!")
for a, b, n, t in [(13.62, 26.80, 1, "Digit pertama × setiap digit"), (26.88, 35.24, 2, "Digit kedua × setiap digit"), (35.24, 46.6, 3, "Tambah ke bawah = jawapan"),
                   (51.44, 56.88, 1, "Digit pertama × setiap digit"), (56.88, 61.78, 2, "Digit kedua × setiap digit"), (61.78, 70.85, 3, "Tambah ke bawah = jawapan")]:
    g(a, b, "step", n=n, text=t)
for a, b, t, col in [(15.4, 17.7, "2 × 1", "g"), (19.2, 20.5, "2 × 1", "g"), (24.08, 26.75, "2 × 2 = 4", "g"),
                     (28.88, 31.0, "2 × 1", "r"), (31.0, 31.9, "Sama", "r"), (33.9, 35.3, "2 × 2 = 4", "r"),
                     (38.14, 38.6, "4", "y"), (38.8, 40.5, "4 + 2 = 6", "y"), (40.9, 41.5, "2", "y"),
                     (52.56, 54.48, "2 × 2 = 4", "g"), (55.3, 56.88, "2 × 2 = 4", "g"),
                     (58.24, 60.08, "4 × 2 = 8", "r"), (60.08, 61.78, "4 × 2 = 8", "r"),
                     (63.62, 63.95, "8", "y"), (63.95, 65.3, "4 + 8 = 12", "y"), (65.3, 67.15, "4 + 1 = 5", "y")]:
    g(a, b, "calc", text=t, col=col)
g(42.70, 46.6, "answer", q="22 × 12", ans="264")
g(68.30, 70.85, "answer", q="24 × 22", ans="528")
g(69.42, 70.85, "sticker", text="Senang kan?")
g(78.08, 81.76, "comment", text="Komen jawapan 32 × 24 👇")
# Jualan
g(81.80, 85.6, "lower", title="MATH TURBO 2027", sub="Tuisyen sekolah rendah · tahun depan")
g(82.0, SRC_END, "reg", text="Pendaftaran 2027 dibuka")
g(85.64, 87.12, "dm", text="DM saya", sub="untuk keterangan lanjut")
g(87.46, 90.70, "chips", items=["Jadual kelas", "Silibus"])
g(90.84, SRC_END, "price1", label="Pendaftaran serendah", price="RM20")
g(92.20, SRC_END, "price2", top="5", mid="subjek", price="RM99")

SFX = []
def sfx(src, name, gain=0.6, out=None): SFX.append({"t": round(out if out is not None else s2o(src), 3), "name": name, "gain": gain})
sfx(0, "impact", 0.8, out=0.0); sfx(0, "whoosh", 0.6, out=0.92)
sfx(0.15, "pop", 0.55); sfx(2.7, "pop", 0.55); sfx(4.7, "whoosh", 0.5); sfx(4.75, "click", 0.6); sfx(8.18, "ding", 0.45)
sfx(10.6, "whoosh", 0.7)
for x in G:
    if x["kind"] == "calc": SFX.append({"t": x["s"], "name": "pop", "gain": 0.45})
    if x["kind"] == "step": SFX.append({"t": x["s"], "name": "click", "gain": 0.6})
    if x["kind"] == "answer": SFX.append({"t": x["s"], "name": "chaching", "gain": 0.55}); SFX.append({"t": round(x["s"] - 1.0, 3), "name": "riser", "gain": 0.3})
    if x["kind"] == "qtag" and x["s"] > 2: SFX.append({"t": x["s"], "name": "whoosh", "gain": 0.55})
sfx(69.42, "ding", 0.5); sfx(78.08, "pop", 0.6); sfx(81.80, "whoosh", 0.7); sfx(82.0, "pop", 0.5); sfx(85.64, "pop", 0.6)
sfx(87.46, "click", 0.6); sfx(88.6, "click", 0.6); sfx(90.84, "chaching", 0.6); sfx(92.2, "impact", 0.55)
SFX.append({"t": round(THUMB + CONTENT - 0.05, 3), "name": "whoosh", "gain": 0.6}); SFX.append({"t": round(THUMB + CONTENT + 0.25, 3), "name": "ding", "gain": 0.5})
SFX.sort(key=lambda x: x["t"])

# ---- punch-in: talking head berselang 100% / 112% setiap 2–3 potongan (potongan = jump cut asal + senyap dibuang)
bounds = sorted(set([round(a, 3) for a, _ in keep] + JUMPS))
Z, pat = [], [1.0, 1.0, 1.12, 1.12, 1.12, 1.0, 1.0, 1.12, 1.12]
for i, b in enumerate(bounds):
    Z.append({"src": b, "t": round(s2o(b), 3), "z": pat[i % len(pat)]})

CLARITY = [round(s2o(92.95), 3), round(s2o(SRC_END), 3)]  # "5 subjek RM99": suara perlahan, dijernihkan
json.dump({"dur": round(DUR, 3), "clarity": CLARITY, "thumb": THUMB, "content": round(CONTENT, 3), "outro": OUTRO, "keep": keep,
           "split": S(*SPLIT), "bmap": [[round(s2o(a), 3), b] for a, b in BMAP], "captions": captions, "graphics": G,
           "sfx": SFX, "zoom": Z}, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print("durasi", round(DUR, 2), "isi", round(CONTENT, 2), "caption", len(captions), "grafik", len(G), "sfx", len(SFX))
for c in captions: print(f'{c["s"]:6.2f} ' + " ".join(("*" + w["t"] + "*") if w["hl"] else w["t"] for w in c["w"]))
