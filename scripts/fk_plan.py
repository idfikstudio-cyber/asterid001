"""Pelan edit video Fi-k Studio (talking head): caption, overlay, B-roll, motion zoom, SFX.

python3 fk_plan.py <transcript.json> <out_dir> <config.json>
Tulis: plan.json + captions.ass (masa ikut video OUTPUT: thumbnail 1s di depan).
Semua masa dalam config ialah masa SUMBER (video asal). Contoh config: edit/FK-F-007/config.json.
"""
import json, sys, re
from PIL import ImageFont

TR, OUT, CFG = sys.argv[1], sys.argv[2], sys.argv[3]
C = json.load(open(CFG))
OFF = 1.0            # thumbnail 1 saat
SRC_DUR = C["src_dur"]
END = 121 / 30       # outro BRAND/Outro Potrait.mp4, frame 0-120 (selepas itu skrin putih kosong)
GREEN_ASS = "&H00454930"   # #304945 (BGR)
FONT_BLACK = "/root/.fonts/Montserrat-Black.ttf"
fnt = ImageFont.truetype(FONT_BLACK, 100)

t = json.load(open(TR))
words = [dict(w=w["w"].strip(), s=w["s"], e=w["e"]) for s in t for w in s["words"]]
sents = [(s["start"], s["end"], s["text"].strip()) for s in t]

# ---- pembetulan ejaan / dengar (caption ikut apa yang disebut) ----
FIX = C.get("fix", {})                                         # perkataan -> ganti (semua tempat)
FIX_AT = {round(float(k), 2): v for k, v in C.get("fix_at", {}).items()}   # masa mula perkataan -> ganti
PERLU_SEMAK = C.get("perlu_semak", [])
for w in words:
    core = re.sub(r"[^\w\-]", "", w["w"])
    if round(w["s"], 2) in FIX_AT:
        w["w"] = w["w"].replace(core, FIX_AT[round(w["s"], 2)])
    elif core in FIX:
        w["w"] = w["w"].replace(core, FIX[core])
# gabung "-kadang", "-ubah", "-kerja", "-apa" dengan perkataan sebelum
merged = []
for w in words:
    if w["w"].startswith("-") and merged:
        merged[-1]["w"] += w["w"]; merged[-1]["e"] = w["e"]
    else:
        merged.append(dict(w))
words = merged

KEY = set(C["key"])

def clean(s):
    return re.sub(r"[,.?!]", "", s).upper()

# ---- chunk: 1 perkataan (gaya rujukan); perkataan pendek (<=3 huruf) digabung dengan seterusnya ----
chunks = []
i = 0
while i < len(words):
    grp = [words[i]]
    while len(grp) < 3 and len(re.sub(r"\W", "", grp[-1]["w"])) <= 3 and i + 1 < len(words) \
            and words[i + 1]["s"] - grp[-1]["e"] < 0.25 and not re.search(r"[.,?!]$", grp[-1]["w"]):
        i += 1; grp.append(words[i])
    chunks.append(dict(text=clean(" ".join(g["w"] for g in grp)), s=grp[0]["s"], e=grp[-1]["e"]))
    i += 1
for k, c in enumerate(chunks):
    nxt = chunks[k + 1]["s"] if k + 1 < len(chunks) else c["e"] + 0.3
    c["e"] = min(max(c["e"], c["s"] + 0.18), nxt) if nxt - c["e"] < 0.35 else c["e"] + 0.1

# ---- overlay teks, B-roll (masa sumber, dari config) ----
LABEL = C.get("label", dict(s=0.15, e=3.3, text="Farhan · Founder Fi-k Studio"))
POINTS = C.get("points", [])      # tajuk poin, atas frame
NUMS = C.get("nums", [])          # angka / teks besar 1-2 saat, tepat seperti disebut
BROLL = C["broll"]                # ±setiap 8 s, sepadan ayat, BUKAN pada poin penting; type: video | image
# motion zoom lembut pada muka -- zoom in perlahan satu ayat, zoom out ayat seterusnya
ZOOM = []
for k, (s, e, _) in enumerate(sents):
    ZOOM.append(dict(s=s, e=e, z0=1.0 if k % 2 == 0 else 1.14, z1=1.14 if k % 2 == 0 else 1.0))
SFX = [dict(t=n["s"], f="softpop") for n in NUMS] + [dict(t=b["s"] - 0.12, f="softwhoosh") for b in BROLL]

# ---- ASS ----
def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def fit(text, base, maxw):
    w = fnt.getlength(text) * base / 100
    w *= 0.8   # libass render ~0.8x saiz PIL
    return int(base if w <= maxw else base * maxw / w)

hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CapOut,Montserrat Black,120,&H00FFFFFF,&H00FFFFFF,{GREEN_ASS},&H00000000,0,0,0,0,100,100,1,0,1,17,0,2,60,200,500,1
Style: CapIn,Montserrat Black,120,&H00FFFFFF,&H00FFFFFF,&H00151515,&H00000000,0,0,0,0,100,100,1,0,1,6,0,2,60,200,500,1
Style: CapKey,Montserrat Black,120,&H00FFFFFF,&H00FFFFFF,{GREEN_ASS},&H00000000,0,0,0,0,100,100,1,0,3,16,0,2,60,200,500,1
Style: Label,Montserrat SemiBold,46,&H00FFFFFF,&H00FFFFFF,{GREEN_ASS},&H00000000,0,0,0,0,100,100,0.5,0,3,12,0,7,70,200,250,1
Style: Point,Montserrat ExtraBold,58,&H00FFFFFF,&H00FFFFFF,{GREEN_ASS},&H00000000,0,0,0,0,100,100,1,0,3,18,0,7,70,200,230,1
Style: Num,Montserrat Black,150,{GREEN_ASS},&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,14,0,5,60,200,0,1
Style: Hook,Montserrat Black,150,{GREEN_ASS},&H00FFFFFF,&H00FFFFFF,&H80000000,0,0,0,0,100,100,0,0,1,18,6,7,70,190,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
POP = r"{\fscx86\fscy86\t(0,90,\fscx100\fscy100)}"
def in_num(c):
    return any(n["s"] - 0.1 <= c["s"] < n["e"] and c["text"] in n["text"] for n in NUMS)
for c in chunks:
    if in_num(c):
        continue   # angka besar sudah papar perkataan ini
    s, e = c["s"] + OFF, c["e"] + OFF
    fs = fit(c["text"], 120, 800)
    key = any(k in c["text"].split() or k == c["text"] for k in KEY)
    if key:
        ev.append(f"Dialogue: 2,{ts(s)},{ts(e)},CapKey,,0,0,0,,{POP}{{\\fs{fs}}}{c['text']}")
    else:
        ev.append(f"Dialogue: 1,{ts(s)},{ts(e)},CapOut,,0,0,0,,{POP}{{\\fs{fs}}}{c['text']}")
        ev.append(f"Dialogue: 2,{ts(s)},{ts(e)},CapIn,,0,0,0,,{POP}{{\\fs{fs}}}{c['text']}")
ev.append(f"Dialogue: 3,{ts(LABEL['s']+OFF)},{ts(LABEL['e']+OFF)},Label,,0,0,0,,{{\\fad(200,250)}}{LABEL['text']}")
for p in POINTS:
    ev.append(f"Dialogue: 3,{ts(p['s']+OFF)},{ts(p['e']+OFF)},Point,,0,0,0,,{{\\fad(180,200)\\move(40,230,70,230,0,220)}}{p['text']}")
for n in NUMS:
    fs = min(fit(line, 150, 820) for line in n["text"].split("\\N"))   # teks panjang: pecah dengan \N
    ev.append(f"Dialogue: 4,{ts(n['s']+OFF)},{ts(n['e']+OFF)},Num,,0,0,0,,{{\\an5\\pos(480,1020)\\fs{fs}\\fad(80,150)\\fscx70\\fscy70\\t(0,120,\\fscx100\\fscy100)}}{n['text']}")
# Hook pada thumbnail (0–1s): baris dari config [{text, fs, y}] (fs None = auto muat lebar)
for hl in C["hook_lines"]:
    fs = hl.get("fs") or fit(hl["text"], 170, 820)
    ev.append(f"Dialogue: 5,{ts(0)},{ts(1.0)},Hook,,0,0,0,,{{\\an2\\pos(470,{hl['y']})\\fs{fs}}}{hl['text']}")
open(f"{OUT}/captions.ass", "w").write(hdr + "\n".join(ev) + "\n")

plan = dict(offset=OFF, thumb_t=C["thumb_t"], src_dur=SRC_DUR, end_card=END, total=OFF + SRC_DUR + END,
            hook=" ".join(h["text"] for h in C["hook_lines"]), label=LABEL, points=POINTS, nums=NUMS, broll=BROLL,
            zoom=ZOOM, sfx=SFX, chunks=chunks, perlu_semak=PERLU_SEMAK,
            cta=C.get("cta", "DM untuk keterangan lanjut"), tagline=C.get("tagline", "Design Dulu, Baru Bina"))
json.dump(plan, open(f"{OUT}/plan.json", "w"), ensure_ascii=False, indent=1)
print(len(chunks), "chunks;", "total", plan["total"])
for p in PERLU_SEMAK: print("SEMAK", p)
