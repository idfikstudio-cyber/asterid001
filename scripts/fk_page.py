"""Jana halaman preview Artifact + RINGKASAN untuk FK-F-007.

python3 fk_page.py <template.html> <out_index.html> <out_ringkasan.txt>
"""
import json, sys, re

TPL, OUT_HTML, OUT_TXT = sys.argv[1:4]
p = json.load(open('edit/FK-F-007/plan.json')); O = p['offset']; D = round(p['total'], 2)
t = json.load(open('edit/FK-F-007/transcript.json'))
VER = "v2"
FIX = {"Ryan": "Raya", "adekat": "dah dekat"}
FIX_AT = {25.94: "tu"}
KEY = {"3", "tiga", "lambat", "delay", "jangan", "seminggu", "minggu", "penting", "salahkan", "pertama", "kedua",
       "ketiga", "kabinet", "tepat", "berubah-ubah", "agreement", "settle", "design"}
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

mg = [[0, 1.0, "Thumbnail", "Hook “3 PUNCA / RENO LAMBAT SIAP” atas frame Farhan tunjuk 3 jari (sumber 0:17.6)"],
      [p['label']['s'] + O, p['label']['e'] + O, "Label", "Pil hijau “Farhan · Founder Fi-k Studio”"]]
for n in p['nums']: mg.append([n['s'] + O, n['e'] + O, "Angka", f"Teks besar “{n['text']}” (hijau #304945, stroke putih)"])
for q in p['points']: mg.append([q['s'] + O, q['e'] + O, "Tajuk poin", f"Kotak hijau atas: “{q['text'].replace('  ', ' ')}”"])
for b in p['broll']: mg.append([b['s'] + O, b['e'] + O, "B-roll", f"{b['src']} ({b['e'] - b['s']:.1f} s) pada {b['why']}"])
mg.append([D - 1.5, D, "End card", "Putih: Logo Green + “We Design, You Build.” + “Follow untuk tips reno seterusnya” + “DM / WhatsApp kami untuk 3D design rumah anda”"])
mg = sorted([[round(a, 2), round(b, 2), c, d] for a, b, c, d in mg])
sfx = sorted([[round(s['t'] + O, 2), "pop lembut" if s['f'] == "softpop" else "whoosh lembut"] for s in p['sfx']])
zoom = [{"t": round(z['s'] + O, 2), "m": f"{'zoom in' if z['z1'] > z['z0'] else 'zoom out'} perlahan {int(z['z0']*100)}% → {int(z['z1']*100)}%"} for z in p['zoom']]
SEG = [[0, 1.0, "Thumbnail", "Hook 3 PUNCA / RENO LAMBAT SIAP"],
       [1.0, 18.6, "Hook & masalah", "Jangan reno sebelum raya tanpa dengar penjelasan; label Farhan; B-roll 0:05.6 & 0:14.6; angka 3 PERKARA, 3 BENDA"],
       [18.6, 29.1, "#1 Design berubah", "Tajuk poin #1 (muka Farhan) + B-roll projek ongoing (tukar situ, tukar sini)"],
       [29.1, 38.9, "#2 Ukuran tak tepat", "Tajuk poin #2 (muka Farhan) + B-roll sinki/kabinet + angka SEMINGGU DUA / 3 MINGGU"],
       [38.9, 48.8, "#3 Tiada agreement", "Tajuk poin #3 (muka Farhan) + B-roll klien pegang dokumen pada 'siapa yang bertanggungjawab'"],
       [48.8, 64.98, "Paling penting", "PALING PENTING (muka Farhan, tiada B-roll) → B-roll 'design dulu' + projek siap"],
       [64.98, D - 1.5, "CTA", "Raya dah dekat ni, DM kami"], [D - 1.5, D, "End card", "Logo + We Design, You Build. + CTA TOFU & BOFU"]]
SEG = [[round(a, 2), round(b, 2), c, d] for a, b, c, d in SEG]
DONE = [
    ["v2: bokeh lebih halus", "Blur dikurangkan (jejari 8 px, sebelum ini 26 px) dan berperingkat ikut jarak dari badan: dekat badan kurang kabur, jauh lebih kabur, macam lensa sebenar. Latar (rak, panel kayu, pokok) masih jelas nampak. Tepi badan dilembutkan supaya tak nampak 'cut-out'; sharpen dikurangkan.", 2.0],
    ["v2: B-roll ±setiap 8 saat", "7 sisipan (0:05.6, 0:14.6, 0:23.8, 0:31.8, 0:42.9, 0:54.8, 1:00.4), semua ≤3 s. Tiada B-roll pada hook, angka, tajuk poin #1/#2/#3, “paling penting” dan CTA, jadi muka Farhan nampak pada poin penting.", 5.6],
    ["v2: motion zoom pada muka", "Zoom in perlahan sepanjang satu ayat, zoom out pada ayat seterusnya (100% ↔ 114%, ease in/out). Zoom berpusat pada muka (dijejak setiap frame, dilicinkan 1 s), mata kekal di sepertiga atas.", 18.72],
    ["v2: caption disahkan", "“RAYA DAH DEKAT NI” (1:05.0) dan “TIME TU” (0:26.7) ikut Farhan.", 26.7],
    ["v2: CTA TOFU + BOFU", "End card: “Follow untuk tips reno seterusnya” + “DM / WhatsApp kami untuk 3D design rumah anda”.", 68.9],
    ["v2: tiada muzik", "Dikekalkan tanpa muzik, ikut Farhan."],
    ["Footage sudah ditrim", "Tiada isi dipotong; tiada senyap >0.3 s dalam rakaman."],
    ["Gaya ikut rujukan", "Caption 1 perkataan, huruf besar tebal, outline + stroke berwarna (hijau #304945 ikut DNA brand); hook besar; B-roll skrin penuh; end card putih dengan logo."],
    ["Thumbnail 1 saat", "Frame Farhan tunjuk 3 jari + “3 PUNCA / RENO LAMBAT SIAP”.", 0.3],
    ["Angka tepat seperti disebut", "3 PERKARA, 3 BENDA, SEMINGGU DUA, 3 MINGGU.", 9.3],
    ["Audio", "High-pass, denoise ringan, −14.3 LUFS, peak −1.4 dBFS. SFX lembut dijana sendiri."]]
TODO = [
    ["Durasi 70.3 s", "Melebihi sasaran BOFU 30–60 s; footage sudah ditrim jadi isi tidak dipotong."],
    ["B-roll IMG_0535 resolusi rendah", "Klip projek siap hanya 352×640, jadi nampak lembut dalam 1080p.", 60.36],
    ["Preview MP4 & log belum di Drive", "Alat Drive hadkan ±3 MB setiap muat naik dan tidak boleh tulis ganti fail sedia ada. THUMB & RINGKASAN v2 dimuat naik sebagai fail baru di _PREVIEW; video preview ada di halaman ini; baris log perlu ditambah manual."]]
TT = "Nak reno rumah sebelum raya? Elakkan 3 punca ni dulu supaya projek tak lambat siap. Follow untuk tips reno seterusnya & DM kami untuk 3D design rumah anda."
HS = "#renovaterumah #interiordesign #fikstudio #renorumah #tipsrenovate"

js = ("const DATA=" + json.dumps(dict(caps=caps, mg=mg, sfx=sfx, zoom=zoom, dur=D), ensure_ascii=False)
      + ";\nconst SEG=" + json.dumps(SEG, ensure_ascii=False) + ";\nconst DONE=" + json.dumps(DONE, ensure_ascii=False)
      + ";\nconst TODO=" + json.dumps(TODO, ensure_ascii=False) + ";\nconst TT=" + json.dumps(TT, ensure_ascii=False)
      + ";\nconst HS=" + json.dumps(HS) + ";")
html = open(TPL).read().replace("/*DATA*/", js)
open(OUT_HTML, "w").write(html)

def ts(x): return f"{int(x // 60)}:{x % 60:05.2f}"
L = ["RINGKASAN EDIT — FK-F-007_Farhan_Punca Renovate Lambat Siap (preview " + VER + ")",
     "Brand: Fi-k Studio | Spokesperson: Farhan (Founder) | Tag skrip: TOFU+BOFU",
     "Footage: SUDAH DITRIM (tiada isi dipotong) | Durasi: 70.3 s (1 s thumbnail + 67.9 s isi + 1.5 s end card)",
     "Rujukan gaya: BRAND/rujukan video/Apa beza Kontraktor, Arkitek dan Interior Design.mp4", "",
     "1) TEKS HOOK / THUMBNAIL", "   \"3 PUNCA / RENO LAMBAT SIAP\" atas frame Farhan tunjuk 3 jari (sumber 17.6 s).", "",
     "2) CAPTION PENUH (ikut percakapan; masa ikut video preview)"]
for c in caps:
    L.append(f"   [{ts(c['s'])}] " + " ".join(w['t'] for w in c['w']))
L += ["", "3) SFX, ANIMASI, B-ROLL, ZOOM (masa ikut video preview)",
      "   Bokeh halus berperingkat sepanjang video; subjek dijernihkan sedikit."]
for m in mg: L.append(f"   {ts(m[0])}–{ts(m[1])}  {m[2]}: {m[3]}")
for x in sfx: L.append(f"   {ts(x[0])}  SFX {x[1]}")
L.append("   Motion zoom: " + "; ".join(f"{ts(z['t'])} {z['m']}" for z in zoom))
L += ["", "4) CTA", "   End card: \"Follow untuk tips reno seterusnya\" + \"DM / WhatsApp kami untuk 3D design rumah anda\" (TOFU + BOFU).", "",
      "5) PERLU SEMAK"] + [f"   - {a}: {b}" for a, b, *_ in TODO] + ["",
      "6) CAPTION TIKTOK", "   " + TT, "   " + HS, "",
      "Perubahan v2 (ikut komen Farhan):"] + [f"   - {a}: {b}" for a, b, *_ in DONE[:6]]
open(OUT_TXT, "w").write("\n".join(L) + "\n")
print("ok", len(html))
