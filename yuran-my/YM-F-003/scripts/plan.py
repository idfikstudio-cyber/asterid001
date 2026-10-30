# transcript.json (masa sumber) -> plan.json (masa output). Output = 1.0 s thumbnail + sumber penuh + 1.5 s end card
import json, re, sys
T0 = 1.0                      # thumbnail statik di depan
SRC_DUR = 48.646
END = T0 + SRC_DUR            # mula end card
DUR = END + 1.5
d = json.load(open(sys.argv[1]))

# ejaan ikut skrip/DNA; perkataan ragu ditanda PERLU SEMAK
FIX = {(7.94, "Hari"): "Dari", (42.50, "yang"): "tanya"}
W = []
for s in d:
    for w in s["words"]:
        txt = w["w"].strip()
        txt = FIX.get((round(w["s"], 2), txt), txt)
        if txt.startswith("-") and W: W[-1]["w"] += txt; W[-1]["e"] = w["e"]; continue
        if txt.startswith(".my") and W: W[-1]["w"] = "Yuran.my" + txt[3:]; W[-1]["e"] = w["e"]; continue
        W.append({"w": txt, "s": w["s"], "e": w["e"]})

chunks, cur = [], []
for i, w in enumerate(W):
    cur.append(w)
    nxt = W[i + 1] if i + 1 < len(W) else None
    tail = nxt and len(cur) == 3 and re.search(r"[.,?!]$", nxt["w"]) and nxt["s"] - w["e"] < 0.4  # elak serpihan 1 perkataan
    if (len(cur) >= 3 and not tail) or re.search(r"[.,?!]$", w["w"]) or not nxt or nxt["s"] - w["e"] > 0.4:
        e = nxt["s"] if nxt and nxt["s"] - w["e"] < 0.4 else w["e"] + 0.2
        chunks.append({"s": round(cur[0]["s"] + T0, 3), "e": round(e + T0, 3),
                       "words": [{"w": re.sub(r"[.,]$", "", x["w"]), "s": round(x["s"] + T0, 3)} for x in cur]})
        cur = []
HOT = {"resit", "rekod", "direkod", "automatik", "Yuran.my", "dashboard", "tegang", "tertuduh", "manual", "salah?", "dipersalahkan"}
for c in chunks:
    for x in c["words"]:
        if x["w"].strip(",.") in HOT: x["hot"] = 1

def o(t): return round(t + T0, 3)   # masa sumber -> output
G = [
    {"s": 0, "e": T0, "kind": "thumb", "lines": ["DAH BAYAR,", "TAPI TIADA", "REKOD?"], "note": "Thumbnail 1 s + hook"},
    {"s": o(0.2), "e": o(3.2), "kind": "label", "text": "Farhan · Yuran.my", "note": "Label pembentang"},
    {"s": o(0.75), "e": o(5.2), "kind": "versus", "a": ["Ibu bapa", "Dah bayar", o(0.75)], "b": ["Cikgu", "Belum bayar", o(2.70)], "q": o(3.62), "note": "Dua pihak bercanggah, '?' pada 'Siapa betul?'"},
    {"s": o(5.32), "e": o(6.86), "kind": "chip", "icon": "book", "text": "Buku resit", "note": "Ikon buku resit"},
    {"s": o(6.86), "e": o(9.86), "kind": "broll-book", "note": "B-roll motion (buatan sendiri): buku resit diselak helai demi helai, Jan → Okt"},
    {"s": o(11.64), "e": o(13.9), "kind": "notfound", "text": "TAK JUMPA", "note": "Kanta pembesar + pangkah lembut"},
    {"s": o(24.9), "e": o(26.8), "kind": "chip", "icon": "receipt-x", "text": "Resit tak dibuat", "note": "Punca sebenar"},
    {"s": o(27.72), "e": o(30.72), "kind": "broll-ledger", "note": "B-roll motion (buatan sendiri): buku rekod manual ditulis tangan"},
    {"s": o(31.94), "e": o(33.1), "kind": "logo", "note": "Logo putih atas pil biru #2A3B8F (tiada shadow)"},
    {"s": o(33.1), "e": o(36.1), "kind": "broll-screen", "img": "scr_invois.png", "focus": [1330, 413], "callout": "Status bayaran direkod", "note": "B-ROLL/B-Roll_SistemYuran.my.mp4 @0:29 (invois); nama, IC, no. & jumlah diblur; zoom ke status PAID"},
    {"s": o(36.6), "e": o(39.6), "kind": "broll-receipt", "ding": o(39.04), "note": "B-roll motion (buatan sendiri): resit automatik terbang ke telefon ibu bapa"},
    {"s": o(39.68), "e": o(42.95), "kind": "chip", "icon": "phone", "text": "Ibu bapa semak dalam app", "note": "Ikon telefon"},
    {"s": o(43.1), "e": o(44.6), "kind": "broll-screen", "img": "scr_dashboard.png", "focus": [990, 790], "callout": "Dashboard cikgu", "note": "B-ROLL/B-Roll_SistemYuran.my.mp4 @0:01 (dashboard); semua angka statistik diblur"},
    {"s": o(44.8), "e": o(46.9), "kind": "versus-ok", "a": ["Ibu bapa", "Lega", o(45.0)], "b": ["Cikgu", "Lega", o(45.2)], "note": "Ulang motif awal: kedua-dua pihak ✓"},
    {"s": o(46.96), "e": END, "kind": "cta-bio", "tap": o(47.6), "note": "Cara klik link di bio TikTok (gambar BRAND/Yuran Tiktok.jpg)"},
    {"s": END, "e": DUR, "kind": "endcard", "note": "Logo putih + Cara MUDAH Urus Yuran + Klik link di bio + hello@yuran.my"},
]
SFX = [(T0 - 0.05, "whoosh", 0.35), (o(0.75), "pop", 0.3), (o(2.70), "pop", 0.3), (o(3.62), "tick", 0.3),
       (o(5.32), "pop", 0.25), (o(6.86), "whoosh", 0.3), (o(7.6), "tick", 0.12), (o(8.2), "tick", 0.12), (o(8.8), "tick", 0.12), (o(9.4), "tick", 0.12),
       (o(11.64), "pop", 0.3), (o(24.9), "pop", 0.25), (o(27.72), "whoosh", 0.3), (o(31.94), "riser", 0.2), (o(32.2), "ding", 0.3),
       (o(33.1), "whoosh", 0.3), (o(36.6), "whoosh", 0.3), (o(39.04), "ding", 0.4), (o(39.68), "pop", 0.25), (o(43.1), "whoosh", 0.25),
       (o(45.0), "pop", 0.3), (o(45.2), "pop", 0.3), (o(46.96), "whoosh", 0.3), (o(47.6), "click", 0.5), (END, "whoosh", 0.3)]
SFX = [{"t": round(t, 3), "name": n, "gain": g} for t, n, g in SFX]
# punch-in: (mula sumber, skala). Asas 1.05, punch 1.15 — mata di sepertiga atas
ZS = [(0, 1.05), (3.62, 1.15), (5.32, 1.05), (11.64, 1.15), (14.04, 1.05), (16.34, 1.15), (18.54, 1.05), (21.48, 1.15),
      (24.9, 1.05), (30.72, 1.15), (31.94, 1.05), (39.6, 1.15), (41.6, 1.05), (44.6, 1.15), (46.96, 1.05)]
json.dump({"t0": T0, "end": END, "ctaAt": o(46.96), "duration": round(DUR, 3), "thumb_src": 5.25, "captions": chunks, "graphics": G, "sfx": SFX,
           "zoom": [{"src": s, "scale": z} for s, z in ZS],
           "music": [{"file": "Minimal Emotion — Alejandro Magaña (Mixkit, 160)", "from": 0, "to": o(31.94), "offset": 0},
                     {"file": "Motivating Mornings — Ahjay Stelino (Mixkit, 33)", "from": o(31.94) - 0.6, "to": DUR, "offset": 10.4}]},
          open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(chunks), "caption", DUR)
for c in chunks: print(c["s"], c["e"], " ".join(x["w"] + ("*" if x.get("hot") else "") for x in c["words"]))
