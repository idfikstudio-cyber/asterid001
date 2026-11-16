"""Pelan edit FK-F-007 (Fi-k Studio, Farhan): caption, overlay, B-roll, zoom, SFX.

python3 fk_plan.py <transcript.json> <out_dir>
Tulis: plan.json + captions.ass (masa ikut video OUTPUT: thumbnail 1s di depan).
"""
import json, sys, re
from PIL import ImageFont

TR, OUT = sys.argv[1], sys.argv[2]
OFF = 1.0            # thumbnail 1 saat
SRC_DUR = 67.87
END = 1.5            # end card
GREEN_ASS = "&H00454930"   # #304945 (BGR)
FONT_BLACK = "/root/.fonts/Montserrat-Black.ttf"
fnt = ImageFont.truetype(FONT_BLACK, 100)

t = json.load(open(TR))
words = [dict(w=w["w"].strip(), s=w["s"], e=w["e"]) for s in t for w in s["words"]]
sents = [(s["start"], s["end"], s["text"].strip()) for s in t]

# ---- pembetulan ejaan / dengar (caption ikut apa yang disebut) ----
FIX = {"Ryan": "Raya", "adekat": "dah dekat", "time": "tambah"}
PERLU_SEMAK = []
for w in words:
    core = re.sub(r"[^\w\-]", "", w["w"])
    if core in FIX:
        PERLU_SEMAK.append(f'{w["s"]+OFF:.2f}s: transkrip dengar "{core}", caption tulis "{FIX[core]}"')
        w["w"] = w["w"].replace(core, FIX[core])
# gabung "-kadang", "-ubah", "-kerja", "-apa" dengan perkataan sebelum
merged = []
for w in words:
    if w["w"].startswith("-") and merged:
        merged[-1]["w"] += w["w"]; merged[-1]["e"] = w["e"]
    else:
        merged.append(dict(w))
words = merged

KEY = {"3", "TIGA", "LAMBAT", "DELAY", "JANGAN", "SEMINGGU", "MINGGU", "PENTING", "SALAHKAN",
       "PERTAMA", "KEDUA", "KETIGA", "KABINET", "TAK TEPAT", "BERUBAH-UBAH", "AGREEMENT", "SETTLE", "DESIGN"}

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

# ---- overlay teks (masa sumber) ----
LABEL = dict(s=0.15, e=3.3, text="Farhan · Founder Fi-k Studio")
POINTS = [  # tajuk poin, atas frame
    dict(s=18.56, e=22.82, text="#1  DESIGN BERUBAH-UBAH"),
    dict(s=28.12, e=34.74, text="#2  UKURAN TAK TEPAT"),
    dict(s=38.20, e=41.90, text="#3  TAK ADA AGREEMENT"),
    dict(s=48.86, e=53.70, text="PALING PENTING"),
]
NUMS = [  # angka besar 1-2 saat, tepat seperti disebut
    dict(s=8.30, e=9.80, text="3 PERKARA"),
    dict(s=17.14, e=18.50, text="3 BENDA"),
    dict(s=35.82, e=37.20, text="SEMINGGU DUA"),
    dict(s=37.28, e=38.80, text="3 MINGGU"),
]
BROLL = [
    dict(s=22.82, e=25.62, clip="b1", src="B-ROLL/Video Onprogress/IMG_9301.MOV",
         why="'Projek tengah ongoing, nak tukar situ, nak tukar sini'"),
    dict(s=30.76, e=33.30, clip="b2", src="B-ROLL/Video Onprogress/IMG_9321.MOV",
         why="'kabinet yang kita rancang tu kita kena buat balik'"),
    dict(s=39.24, e=41.62, clip="b3", src="B-ROLL/Video Onprogress/IMG_9290.MOV",
         why="'agreement yang tulus dan ikhlas' (klien pegang dokumen)"),
    dict(s=59.36, e=62.26, clip="b4", src="B-ROLL/Video Projek Dah Siap/IMG_0535.MOV",
         why="'semua kerja-kerja tu akan smooth sahaja' (projek siap)"),
]
# punch-in: selang-seli ikut ayat (DNA Farhan: setiap 2 potongan)
ZOOM = []
for k, (s, e, _) in enumerate(sents):
    ZOOM.append(dict(s=s, e=e, z=1.0 if k % 2 == 0 else 1.12))
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
    fs = fit(n["text"], 150, 820)
    ev.append(f"Dialogue: 4,{ts(n['s']+OFF)},{ts(n['e']+OFF)},Num,,0,0,0,,{{\\an5\\pos(480,1020)\\fs{fs}\\fad(80,150)\\fscx70\\fscy70\\t(0,120,\\fscx100\\fscy100)}}{n['text']}")
# Hook pada thumbnail (0–1s)
h2 = fit("RENO LAMBAT SIAP", 170, 820)
ev.append(f"Dialogue: 5,{ts(0)},{ts(1.0)},Hook,,0,0,0,,{{\\an2\\pos(470,1400)\\fs250}}3 PUNCA")
ev.append(f"Dialogue: 5,{ts(0)},{ts(1.0)},Hook,,0,0,0,,{{\\an2\\pos(470,1530)\\fs112}}RENO LAMBAT SIAP")
open(f"{OUT}/captions.ass", "w").write(hdr + "\n".join(ev) + "\n")

plan = dict(offset=OFF, thumb_t=17.6, src_dur=SRC_DUR, end_card=END, total=OFF + SRC_DUR + END,
            hook="3 PUNCA RENO LAMBAT SIAP", label=LABEL, points=POINTS, nums=NUMS, broll=BROLL,
            zoom=ZOOM, sfx=SFX, chunks=chunks, perlu_semak=PERLU_SEMAK,
            cta="DM / WhatsApp kami untuk 3D design rumah anda")
json.dump(plan, open(f"{OUT}/plan.json", "w"), ensure_ascii=False, indent=1)
print(len(chunks), "chunks;", "total", plan["total"])
for p in PERLU_SEMAK: print("SEMAK", p)
