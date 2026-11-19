# Jana halaman Artifact storyboard daripada spesifikasi JSON (generik untuk video Yuran.my).
# python3 ym_sb_page.py <spec.json> <mockup_dir> <music_mp3> <out_html>
import sys, base64, json, html, os

SPEC, SB, MUS, OUT = sys.argv[1:5]
P = json.load(open(SPEC))
def b64(p, mime): return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
def fmt(t): return f"{int(t // 60)}:{int(t % 60):02d}"
esc = html.escape

rows, strip = [], []
for sc in P["scenes"]:
    a, b = sc.get("s"), sc.get("e")
    kind = sc["kind"]
    tm = sc.get("time") or f"{fmt(a)}–{fmt(b)} · {b - a:.0f} s"
    img = b64(f"{SB}/{sc['img']}.jpg", "image/jpeg")
    rows.append(f"""<article class="scene" id="{sc['img']}" data-kind="{kind}">
  <figure><img src="{img}" alt="Mockup {esc(sc['label'])}: {esc(sc['title'])}" loading="lazy" width="540" height="960"></figure>
  <div class="sbody">
    <div class="shead"><span class="tag t-{kind}">{esc(sc['label'])}</span><span class="time">{tm}</span></div>
    <h3>{esc(sc['title'])}</h3>
    <dl>
      <dt>Ucapan</dt><dd class="say">{esc(sc['say'])}</dd>
      <dt>Visual</dt><dd>{esc(sc['vis'])}</dd>
      <dt>Animasi & SFX</dt><dd>{esc(sc['anim'])}</dd>
      <dt>Sumber</dt><dd class="src">{esc(sc['src'])}</dd>
    </dl>
  </div>
</article>""")
    w = sc.get("w", (b - a) if a is not None else 1.0)
    strip.append(f'<a href="#{sc["img"]}" class="seg k-{kind}" style="flex:{w:.1f}" title="{esc(sc["label"])}: {esc(sc["title"])}"><span>{esc(sc.get("short", sc["label"]))}</span></a>')

tx = "".join(f'<li><span class="ts">{esc(t)}</span><span>{esc(l).replace("[", "<mark>").replace("]", "</mark>")}</span></li>' for t, l in P["tx"])
ask = "".join(f'<li><h4>{esc(h)}</h4><p>{esc(p)}</p></li>' for h, p in P["ask"])
style = "".join(f'<div><h4>{esc(h)}</h4><p>{esc(p)}</p></div>' for h, p in P["style"])
pills = "".join(f'<span class="pill{" warn" if i == 0 else ""}">{esc(x)}</span>' for i, x in enumerate(P["pills"]))
axis = "".join(f"<span>{esc(x)}</span>" for x in P["axis"])
cap = (f'  <p><strong>Caption:</strong> {esc(P["tt"])}</p>\n  <p>' + " ".join(f"<code>{esc(h)}</code>" for h in P["hs"]) + "</p>\n"
       + f'  <p class="small">{esc(P["hook_note"])}</p>')
page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ym_sb_tpl2.html")).read()
for k, v in {"TITLE": esc(P["title"]), "EYEBROW": esc(P["eyebrow"]), "H1": esc(P["h1"]), "PILLS": pills, "TUTLABEL": esc(P["tutlabel"]),
             "STRIP": "".join(strip), "AXIS": axis, "ROWS": "\n".join(rows), "NASK": str(len(P["ask"])), "ASK": ask,
             "MUSTITLE": esc(P["mus_title"]), "MUS": b64(MUS, "audio/mpeg"), "MUSNOTE": esc(P["mus_note"]), "TX": tx,
             "STYLE": style, "CAPTION": cap}.items():
    page = page.replace("{{" + k + "}}", v)
open(OUT, "w").write(page)
print(OUT, len(page) // 1024, "KB")
