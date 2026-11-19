"""Halaman preview Artifact + RINGKASAN (generik). Cue grafik datang dari page.json["mg"] (masa raw).

python3 ym_page2.py <edit_dir> <out_index.html> <out_ringkasan.txt>
"""
import json, sys, os, html, re

ED, OUT_HTML, OUT_TXT = sys.argv[1:4]
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ym_preview_tpl.html")
C = json.load(open(f"{ED}/config.json")); P = json.load(open(f"{ED}/plan.json")); G = json.load(open(f"{ED}/page.json"))
O = P["thumb"]; D = P["total"]
caps = []
for g in P["groups"]:
    ws = []
    for t, hl, orig in g["w"]:
        o = orig.strip(",.?…"); fixed = not re.sub(r"[,.?…]", "", t).lower().startswith(re.sub(r"[,.?…]", "", o).lower())
        ws.append({"t": t, "hl": hl and not fixed, "fix": o if fixed else None})
    caps.append({"s": g["s"], "e": g["e"], "w": ws})
def r2o(r): return round(r + O, 2)
mg = [[0, 1.0, "Thumbnail", "Hook “" + " ".join(h[0] for h in C["hook"]) + "” atas frame Farhan, gradien gelap bawah"]]
mg += [[r2o(a), r2o(b), k, d] for a, b, k, d in G["mg"]]
mg.append([round(D - C["end_card"], 2), D, "End card", f"Latar biru #2A3B8F, logo putih, “{C['tagline']}”, CTA “{C['cta']}”, {C['email']}"])
mg.sort()
names = {"pop.wav": "pop lembut", "tick.wav": "tick lembut", "click.wav": "klik lembut", "whoosh.wav": "whoosh lembut", "swoosh_down.wav": "swoosh lembut", "ding.wav": "ding lembut"}
sfx = sorted([[r2o(a), names.get(f, f)] for a, f, _ in C["sfx"]])
zoom = [{"t": r2o(z), "m": "punch-in 112%" if i % 2 else "skala 100%"} for i, z in enumerate(C["zoom_cuts"])]
SEG = [[round(a, 2), round(b, 2), c, d] for a, b, c, d in G["seg"]]
js = ("const DATA=" + json.dumps(dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=D), ensure_ascii=False)
      + ";\nconst SEG=" + json.dumps(SEG, ensure_ascii=False) + ";\nconst DONE=" + json.dumps(G["done"], ensure_ascii=False)
      + ";\nconst TODO=" + json.dumps(G["todo"], ensure_ascii=False) + ";\nconst TT=" + json.dumps(G["tt"], ensure_ascii=False)
      + ";\nconst HS=" + json.dumps(G["hs"]) + ";")
ga = ""
for sec, rows in G["ga"]:
    ga += f"        <h3>{html.escape(sec)}</h3>\n        <div class=\"tbl\"><table><thead><tr><th>Langkah</th><th>Nilai</th><th>Kesan</th></tr></thead><tbody>"
    ga += "".join(f"<tr><td>{html.escape(a)}</td><td class=\"n\">{html.escape(b)}</td><td>{html.escape(c)}</td></tr>" for a, b, c in rows) + "</tbody></table></div>\n"
meta = f"{G['tag']} · Farhan · {G['tarikh']} · 540×960 · {D:.1f} saat"
page = open(TPL).read().replace("/*DATA*/", js)
for k, v in {"ID": G["id"], "TOPIK": G["topik"], "STATUS": G["status"], "META": meta, "DUR": f"{D:.1f}", "EDIT_INTRO": G["edit_intro"], "GA": ga}.items():
    page = page.replace("{{" + k + "}}", v)
page = page.replace("ymf011-tab", G["id"].lower() + "-tab")
open(OUT_HTML, "w").write(page)

def ts(x): return f"{int(x // 60)}:{x % 60:05.2f}"
L = [f"RINGKASAN EDIT — {G['id']}_{G['topik']} (preview {G['ver']})",
     f"Brand: Yuran.my | Spokesperson: Farhan | Tag skrip: {G['tag']}",
     f"Durasi: {D:.1f} s (1 s thumbnail + {D - 1 - C['end_card']:.1f} s isi + {C['end_card']} s end card)", "DNA: yuran-my/CLAUDE.md v2", "",
     "1) TEKS HOOK / THUMBNAIL", "   \"" + " ".join(h[0] for h in C["hook"]) + "\" atas frame Farhan.", "",
     "2) CAPTION PENUH (ikut percakapan; masa ikut video preview)"]
for c in caps: L.append(f"   [{ts(c['s'])}] " + " ".join(w["t"] for w in c["w"]))
L += ["", "3) SFX, ANIMASI, GRAFIK (masa ikut video preview)"]
for m in mg: L.append(f"   {ts(m[0])}–{ts(m[1])}  {m[2]}: {m[3]}")
for x in sfx: L.append(f"   {ts(x[0])}  SFX {x[1]}")
L += ["", "4) CTA", f"   End card: \"{C['tagline']}\" + \"{C['cta']}\" + {C['email']} ({C['tag']}).", "",
      "5) PERLU SEMAK"] + ([f"   - {a}: {b}" for a, b, *_ in G["todo"]] or ["   (tiada)"]) + ["", "6) CAPTION TIKTOK", "   " + G["tt"], "   " + G["hs"]]
if G.get("changes"): L += ["", "Perubahan (ikut komen Farhan):"] + [f"   - {x}" for x in G["changes"]]
open(OUT_TXT, "w").write("\n".join(L) + "\n")
print("ok", len(page))
