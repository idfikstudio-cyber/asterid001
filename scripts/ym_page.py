"""Jana halaman preview Artifact + RINGKASAN untuk video tutorial Yuran.my.

python3 ym_page.py <edit_dir> <out_index.html> <out_ringkasan.txt>
<edit_dir> mesti ada config.json, plan.json (dari ym_render.py) dan page.json.
"""
import json, sys, os, html

ED, OUT_HTML, OUT_TXT = sys.argv[1:4]
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ym_preview_tpl.html")
C = json.load(open(f"{ED}/config.json")); P = json.load(open(f"{ED}/plan.json")); G = json.load(open(f"{ED}/page.json"))
O = P["thumb"]; D = P["total"]
FIXT = {round(float(k), 2): v for k, v in G["fix_marks"].items()}   # masa raw -> perkataan asal

caps = []
for g in P["groups"]:
    ws = []
    for t, hl in g["w"]:
        ws.append({"t": t, "hl": hl, "fix": None})
    caps.append({"s": g["s"], "e": g["e"], "w": ws})
# tanda perkataan yang dibetulkan (ikut masa raw dalam page.json)
for rt, orig in FIXT.items():
    ot = rt + O
    for c in caps:
        if c["s"] - 0.05 <= ot < c["e"]:
            for w in c["w"]:
                if w["t"].lower().startswith(orig[1].lower()) and not w["fix"]:
                    w["fix"] = orig[0]; w["hl"] = False; break
            break

def r2o(r): return round(r + O, 2)
mg = [[0, 1.0, "Thumbnail", "Hook “" + " ".join(h[0] for h in C["hook"]) + "” atas frame Farhan (sumber 2:30), gradien gelap bawah"],
      [r2o(C["label"]["s"]), r2o(C["label"]["e"]), "Label", f"Pil biru “{C['label']['text']}”"]]
for ic in C["icons"]: mg.append([r2o(ic["r"]), r2o(C["icons_end"]), "Ikon", f"Kad putih + tanda ✓ biru: “{ic['text']}”"])
for ch in C["chips"]: mg.append([r2o(ch["r"]), r2o(C["chips_end"]), "Cip peranti", f"{ch['dev']} → {ch['store']}"])
for st in C["steps"]:
    mg.append([r2o(st["r0"]), r2o(st["r1"]), "Tutorial", f"Langkah {st['n']}: {st['title']} · B-roll paparan apps yuran.my {st['map'][0][1]:.1f}–{st['map'][-1][1]:.1f} s"])
for tp in C["taps"]: mg.append([r2o(tp["r"] - 0.25), r2o(tp["r"] + 1.1), "Klik", f"Bulatan berdenyut + label “{tp['label']}”"])
pc = C["pic"]; mg.append([r2o(pc["r"]), r2o(pc["e"]), "PIC", f"Bingkai biru berkelip pada nombor telefon (hanya 4 digit akhir kelihatan) + label “{pc['label']}”"])
nt = C["note"]; mg.append([r2o(nt["r"]), r2o(nt["e"]), "Kad nota", f"“{nt['text']}”"])
for k in ("resit_card", "anywhere_card"): mg.append([r2o(C[k]["r"]), r2o(C[k]["e"]), "Kad", f"“{C[k]['text']}”"])
mg.append([round(D - C["end_card"], 2), D, "End card", f"Latar biru #2A3B8F, logo putih, “{C['tagline']}”, CTA “{C['cta']}”, {C['email']}"])
mg = sorted([[round(a, 2), round(b, 2), c, d] for a, b, c, d in mg])
sfx = [[r2o(tp["r"] - 0.05), "klik lembut"] for tp in C["taps"]]
sfx += [[r2o(ic["r"]), "pop lembut"] for ic in C["icons"]] + [[r2o(c["r"]), "tick lembut"] for c in C["chips"]]
sfx += [[r2o(C["note"]["r"]), "pop lembut"], [r2o(C["resit_card"]["r"]), "pop lembut"], [r2o(140.4), "ding lembut"]]
sfx.sort()
zc = C["zoom_cuts"]; zoom = [{"t": r2o(z), "m": "punch-in 112%" if i % 2 else "skala 100%"} for i, z in enumerate(zc)]
SEG = [[round(a, 2), round(b, 2), c, d] for a, b, c, d in G["seg"]]
js = ("const DATA=" + json.dumps(dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=D), ensure_ascii=False)
      + ";\nconst SEG=" + json.dumps(SEG, ensure_ascii=False) + ";\nconst DONE=" + json.dumps(G["done"], ensure_ascii=False)
      + ";\nconst TODO=" + json.dumps(G["todo"], ensure_ascii=False) + ";\nconst TT=" + json.dumps(G["tt"], ensure_ascii=False)
      + ";\nconst HS=" + json.dumps(G["hs"]) + ";")
ga = ""
for sec, rows in G["ga"]:
    ga += f"        <h3>{html.escape(sec)}</h3>\n        <div class=\"tbl\"><table><thead><tr><th>Langkah</th><th>Nilai</th><th>Kesan</th></tr></thead><tbody>"
    ga += "".join(f"<tr><td>{html.escape(a)}</td><td class=\"n\">{html.escape(b)}</td><td>{html.escape(c)}</td></tr>" for a, b, c in rows)
    ga += "</tbody></table></div>\n"
meta = f"{G['tag']} · Farhan · {G['tarikh']} · 540×960 · {D:.1f} saat"
page = open(TPL).read().replace("/*DATA*/", js)
for k, v in {"ID": G["id"], "TOPIK": G["topik"], "STATUS": G["status"], "META": meta, "DUR": f"{D:.1f}", "EDIT_INTRO": G["edit_intro"], "GA": ga}.items():
    page = page.replace("{{" + k + "}}", v)
open(OUT_HTML, "w").write(page)

def ts(x): return f"{int(x // 60)}:{x % 60:05.2f}"
L = [f"RINGKASAN EDIT — {G['id']}_{G['topik']} (preview {G['ver']})",
     f"Brand: Yuran.my | Spokesperson: Farhan | Tag skrip: {G['tag']} (tutorial evergreen)",
     f"Durasi: {D:.1f} s (1 s thumbnail + {D - 1 - C['end_card']:.1f} s isi + {C['end_card']} s end card)",
     "DNA: yuran-my/CLAUDE.md v2", "",
     "1) TEKS HOOK / THUMBNAIL", "   \"" + " ".join(h[0] for h in C["hook"]) + "\" atas frame Farhan (sumber 2:30).", "",
     "2) CAPTION PENUH (ikut percakapan; masa ikut video preview)"]
for c in caps: L.append(f"   [{ts(c['s'])}] " + " ".join(w["t"] for w in c["w"]))
L += ["", "3) SFX, ANIMASI, B-ROLL (masa ikut video preview)"]
for m in mg: L.append(f"   {ts(m[0])}–{ts(m[1])}  {m[2]}: {m[3]}")
for x in sfx: L.append(f"   {ts(x[0])}  SFX {x[1]}")
L += ["", "4) CTA", f"   End card: \"{C['tagline']}\" + \"{C['cta']}\" + {C['email']} (TOFU).", "",
      "5) PERLU SEMAK"] + [f"   - {a}: {b}" for a, b, *_ in G["todo"]] + ["",
      "6) CAPTION TIKTOK", "   " + G["tt"], "   " + G["hs"]]
if G.get("changes"): L += ["", "Perubahan (ikut komen Farhan):"] + [f"   - {x}" for x in G["changes"]]
open(OUT_TXT, "w").write("\n".join(L) + "\n")
print("ok", len(page))
