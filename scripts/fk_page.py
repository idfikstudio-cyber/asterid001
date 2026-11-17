"""Jana halaman preview Artifact + RINGKASAN untuk satu video Fi-k Studio.

python3 fk_page.py <edit_dir> <out_index.html> <out_ringkasan.txt>

<edit_dir> (contoh edit/FK-F-008) mesti ada:
  transcript.json, plan.json (dari fk_plan.py), config.json (fix/fix_at/key/hook_lines/thumb_t),
  page.json: id, topik, tag, ver, status, tarikh, edit_intro, seg [[s,e,nama,isi]...] (masa OUTPUT),
             done [[tajuk,isi,(masa)]...], todo [[tajuk,isi,(masa)]...], tt, hs
Templat: scripts/fk_preview_tpl.html
"""
import json, sys, re, os

ED, OUT_HTML, OUT_TXT = sys.argv[1:4]
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fk_preview_tpl.html")
p = json.load(open(f"{ED}/plan.json")); O = p['offset']; D = round(p['total'], 2)
t = json.load(open(f"{ED}/transcript.json"))
C = json.load(open(f"{ED}/config.json"))
G = json.load(open(f"{ED}/page.json"))
FIX = C.get("fix", {})
FIX_AT = {round(float(k), 2): v for k, v in C.get("fix_at", {}).items()}
KEY = {k.lower() for k in C["key"]}

caps = []
for s in t:
    ws = []
    for w in s['words']:
        raw = w['w'].strip()
        if raw.startswith('-') and ws:
            ws[-1]['t'] += raw; continue
        core = re.sub(r"[^\w\-]", "", raw)
        if round(w['s'], 2) in FIX_AT:
            ws.append({"t": raw.replace(core, FIX_AT[round(w['s'], 2)]), "hl": False, "fix": core})
        elif core in FIX:
            ws.append({"t": raw.replace(core, FIX[core]), "hl": False, "fix": core})
        else:
            ws.append({"t": raw, "hl": False, "fix": None})
    for w in ws:
        if not w['fix'] and re.sub(r"[^\w\-]", "", w['t']).lower() in KEY:
            w['hl'] = True
    caps.append({"s": round(s['start'] + O, 2), "e": round(s['end'] + O, 2), "w": ws})

hook = " / ".join(h["text"] for h in C["hook_lines"])
def tsm(x): return f"{int(x // 60)}:{x % 60:04.1f}"
mg = [[0, 1.0, "Thumbnail", f"Hook “{hook}” atas frame Farhan (sumber {tsm(C['thumb_t'])}), latar bokeh"],
      [p['label']['s'] + O, p['label']['e'] + O, "Label", f"Pil hijau “{p['label']['text']}”"]]
for n in p['nums']: mg.append([n['s'] + O, n['e'] + O, "Teks besar", f"“{n['text'].replace(chr(92) + 'N', ' ')}” (hijau #304945, stroke putih)"])
for q in p['points']: mg.append([q['s'] + O, q['e'] + O, "Tajuk poin", f"Kotak hijau atas: “{q['text'].replace('  ', ' ')}”"])
for b in p['broll']:
    kind = "gambar, Ken Burns" if b.get("type") == "image" else "video"
    mg.append([b['s'] + O, b['e'] + O, "B-roll", f"{b['src']} ({kind}, {b['e'] - b['s']:.1f} s) pada {b['why']}"])
mg.append([D - p["end_card"], D, "Outro", f"BRAND/Outro Potrait.mp4 (animasi logo, 4.0 s) + “{p['tagline']}” + kotak hijau “{p['cta']}” muncul selepas logo statik"])
mg = sorted([[round(a, 2), round(b, 2), c, d] for a, b, c, d in mg])
sfx = sorted([[round(s['t'] + O, 2), "pop lembut" if s['f'] == "softpop" else "whoosh lembut"] for s in p['sfx']])
zoom = [{"t": round(z['s'] + O, 2), "m": f"{'zoom in' if z['z1'] > z['z0'] else 'zoom out'} perlahan {int(z['z0']*100)}% → {int(z['z1']*100)}%"} for z in p['zoom']]
SEG = [[round(a, 2), round(b, 2), c, d] for a, b, c, d in G["seg"]]
DONE, TODO, TT, HS = G["done"], G["todo"], G["tt"], G["hs"]

js = ("const DATA=" + json.dumps(dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=D), ensure_ascii=False)
      + ";\nconst SEG=" + json.dumps(SEG, ensure_ascii=False) + ";\nconst DONE=" + json.dumps(DONE, ensure_ascii=False)
      + ";\nconst TODO=" + json.dumps(TODO, ensure_ascii=False) + ";\nconst TT=" + json.dumps(TT, ensure_ascii=False)
      + ";\nconst HS=" + json.dumps(HS) + ";")
meta = f"{G['tag']} · Farhan · {G['tarikh']} · 540×960 · {D:.1f} saat"
html = open(TPL).read().replace("/*DATA*/", js)
for k, v in {"ID": G["id"], "TOPIK": G["topik"], "STATUS": G["status"], "META": meta, "DUR": f"{D:.1f}",
             "EDIT_INTRO": G["edit_intro"]}.items():
    html = html.replace("{{" + k + "}}", v)
open(OUT_HTML, "w").write(html)

def ts(x): return f"{int(x // 60)}:{x % 60:05.2f}"
L = [f"RINGKASAN EDIT — {G['id']}_Farhan_{G['topik']} (preview {G['ver']})",
     f"Brand: Fi-k Studio | Spokesperson: Farhan (Founder) | Tag skrip: {G['tag']}",
     f"Durasi: {D:.1f} s (1 s thumbnail + {p['src_dur']:.1f} s isi + 4.0 s outro)",
     "DNA: fik-studio/CLAUDE.md v3.3", "",
     "1) TEKS HOOK / THUMBNAIL", f"   \"{hook}\" atas frame Farhan (sumber {tsm(C['thumb_t'])}).", "",
     "2) CAPTION PENUH (ikut percakapan; masa ikut video preview)"]
for c in caps:
    L.append(f"   [{ts(c['s'])}] " + " ".join(w['t'] for w in c['w']))
L += ["", "3) SFX, ANIMASI, B-ROLL, ZOOM (masa ikut video preview)",
      "   Bokeh halus berperingkat sepanjang video; subjek dijernihkan sedikit."]
for m in mg: L.append(f"   {ts(m[0])}–{ts(m[1])}  {m[2]}: {m[3]}")
for x in sfx: L.append(f"   {ts(x[0])}  SFX {x[1]}")
L.append("   Motion zoom: " + "; ".join(f"{ts(z['t'])} {z['m']}" for z in zoom))
L += ["", "   Senarai B-roll: [baris skrip] → [folder / nama fail] → [sebab]"]
for b in p['broll']: L.append(f"   {ts(b['s'] + O)}  {b['why'].split(' (')[0]} → {b['src']} → {b['why']}")
L += ["", "4) CTA", f"   Outro: \"{p['tagline']}\" + \"{p['cta']}\".", "",
      "5) PERLU SEMAK"] + [f"   - {a}: {b}" for a, b, *_ in TODO] + ["",
      "6) CAPTION TIKTOK", "   " + TT, "   " + HS]
if G.get("changes"):
    L += ["", "Perubahan (ikut komen Farhan):"] + [f"   - {x}" for x in G["changes"]]
open(OUT_TXT, "w").write("\n".join(L) + "\n")
print("ok", len(html))
