# Bina halaman preview Artifact dari meta render + edit/<ID>/page.json.
# usage: python3 ym_page.py <workdir> <page.json> <tpl.html>   -> <workdir>/art/index.html + ringkasan.json
import json, sys
S, PG, TPL = sys.argv[1:4]; m = json.load(open(S + "/edit/tmp540/meta.json")); pg = json.load(open(PG))
FIXES = pg.get("fix_shown", {}); CTX = set(pg.get("fix_ctx", []))  # caption -> ejaan transkrip asal (hover)
caps = [{"s": round(c["s"], 2), "e": round(c["e"], 2),
         "w": [{"t": w, "hl": h, "fix": FIXES.get(w.rstrip("?")) if not CTX or any(x[0] in CTX for x in c["w"]) else None} for w, h in c["w"]]}
        for c in m["caps"]]
E0, DUR = round(m["end0"], 2), round(m["dur"], 2)
T = lambda x: E0 if x == "END" else DUR if x == "DUR" else x
mg = [[0, 1.0, "Thumbnail", pg["thumb"]]]
for i, (t0, t1, k) in enumerate(m["gfx"]):
    d = pg["gfx_desc"][i] if "gfx_desc" in pg else (pg["rows_desc"].get(str(round(t0, 2))) if k == "rows" else pg["desc"][k])
    mg.append([round(t0, 2), round(t1, 2), pg["labels"][k], d])
mg.append([E0, DUR, "End card", pg["end"]]); mg.sort(key=lambda x: x[0])
cuts = [1.0]; [cuts.append(cuts[-1] + b - a) for a, b in m["edl"]]
zoom = [{"t": round(cuts[i], 2), "m": ("130% punch-in" if z > 1.2 else "115% (asas)")} for i, z in enumerate(m["zoom"])]
data = {"caps": caps, "mg": mg, "sfx": [[round(t, 2), n] for t, n, g in m["sfx"]], "zoom": zoom, "dur": DUR}
SEG = [[T(a), T(b), n, d] for a, b, n, d in pg["seg"]]
out = open(TPL).read()
for k, v in {"__DATA__": data, "__SEG__": SEG, "__DONE__": pg["done"], "__TODO__": pg["todo"], "__TT__": pg["tt"], "__HS__": pg["hs"]}.items():
    out = out.replace(k, json.dumps(v, ensure_ascii=False))
for k, v in pg.get("html", {}).items(): out = out.replace(k, v)
out = out.replace("__DUR__", str(DUR))
open(S + "/art/index.html", "w").write(out)
json.dump({"caps": caps, "mg": mg, "sfx": data["sfx"], "todo": pg["todo"], "tt": pg["tt"], "hs": pg["hs"]}, open(S + "/art/ringkasan.json", "w"), ensure_ascii=False)
print("ok")
