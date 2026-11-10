# YM-F-010 Sistem Macam Mana: pelan edit (caption, B-roll, grafik, SFX, zoom) atas garis masa video siap.
# Masa sumber (src) = masa dalam TOFU_SistemMacamMana.mp4. Masa video siap = 1.0 (thumbnail) + masa body.
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
THUMB = 1.0
END = 1.5
CUTS = [(3.05, 3.27)]          # senyap 0.42 s selepas "lain-lain" (padding 0.10 kekal di kedua-dua belah)
SRC_DUR = 53.73

def body(src):
    t = src
    for a, b in CUTS:
        if src >= b: t -= (b - a)
        elif src > a: t -= (src - a)
    return t

def out(src): return round(THUMB + body(src), 3)

BODY_DUR = body(SRC_DUR)
DUR = round(THUMB + BODY_DUR + END, 3)

# ---------- caption ----------
FIX = {"otomatik.": "automatik.", "Isi": "E-sijil", "jil": None, ".my.": None}
HOT = {"penting", "skrin", "handphone", "bayar", "belum", "overdue", "resit", "automatik", "manual",
       "kehadiran", "hadir", "tak", "laporan", "dokumen", "download", "E-sijil", "reminder", "prestasi",
       "surat", "jemputan", "Yuran.my", "komen", "demo", "lama"}
# "tak" hanya hot pada "tak hadir"

def words():
    t = json.load(open(os.path.join(HERE, "transcript.json")))
    W = []
    for s in t:
        for w in s["words"]:
            txt = w["w"].strip()
            orig = txt
            if txt in FIX:
                txt = FIX[txt]
                if txt is None:  # gabung ke perkataan sebelum
                    W[-1]["e"] = w["e"]
                    if orig == ".my.": W[-1]["w"] = "Yuran.my."
                    continue
            if txt.startswith("-") and W:
                W[-1]["w"] += txt; W[-1]["e"] = w["e"]; continue
            W.append({"w": txt, "s": w["s"], "e": w["e"], "orig": orig if orig != txt else None})
    # pembetulan khas
    for w in W:
        if w["w"] == "E-sijil": w["orig"] = "Isi jil"
        if w["w"] == "Yuran.my.": w["orig"] = "yuran .my"
        if w["w"] == "automatik.": w["orig"] = "otomatik"
    return W

def chunks(W):
    C, cur = [], []
    for i, w in enumerate(W):
        cur.append(w)
        nxt = W[i + 1] if i + 1 < len(W) else None
        n = len(cur)
        brk = (n >= 3 or re.search(r"[.,?!]$", w["w"]) or not nxt or nxt["s"] - w["e"] > 0.35
               or (n >= 2 and len(" ".join(x["w"] for x in cur)) > 16))
        if brk:
            C.append(cur); cur = []
    res = []
    for i, c in enumerate(C):
        s = c[0]["s"]; e = C[i + 1][0]["s"] if i + 1 < len(C) else c[-1]["e"] + 0.2
        e = min(e, c[-1]["e"] + 0.5)
        ws = []
        for j, x in enumerate(c):
            k = re.sub(r"[^\w\-\.]", "", x["w"]).strip(".").lower()
            hot = k in {h.lower() for h in HOT} and k != "tak"
            if k == "tak" and j + 1 < len(c) and "hadir" in c[j + 1]["w"]: hot = True
            if k == "lama" : hot = True
            if k == "belum": hot = True
            ws.append({"t": re.sub(r"[,.]$", "", x["w"]) if not x["w"].endswith("?") else x["w"],
                       "hl": hot, "fix": x["orig"], "s": out(x["s"])})
        res.append({"s": out(s), "e": out(e), "w": ws})
    return res

# ---------- B-roll (masa sumber body) ----------
# crop: (x,y,w,h) dalam piksel sumber (nisbah 9:16). blur: [(x0,y0,x1,y1, dari_masa_klip, hingga_masa_klip)]
# callout: [(t0,t1, rect_awal, rect_akhir)] masa klip
BR = [
 dict(id="B1", src=(3.27, 5.10), file="pantau.mp4", at=0.6, crop=(0, 60, 1080, 1920), kb=(1.0, 1.06),
      label=None, note="B-ROLL/B-Roll Pantau Yuran.mp4 @0:00.6: dashboard Yuran.my di skrin telefon (Good Morning, Overdue Invoice Alerts)",
      blur=[], callout=[]),
 dict(id="B2", src=(8.40, 11.20), file="pantau.mp4", at=55.0, crop=(0, 180, 1080, 1920), kb=(1.0, 1.04),
      label=None, note="B-ROLL/B-Roll Pantau Yuran.mp4 @0:55.0: kad 43 Overdue Invoices → callout Average Days Overdue pada “berapa lama overdue”",
      blur=[], callout=[(55.0, 55.76, (50, 1020, 1030, 1310), (50, 1000, 1030, 1290)),
                        (55.76, 57.8, (50, 1715, 1030, 2015), (50, 1665, 1030, 1955))]),
 dict(id="B3", src=(15.40, 18.30), file="apps.mp4", at=40.6, crop=(0, 95, 592, 1052), kb=(1.0, 1.05),
      label="App ahli", note="B-ROLL/Apps Yuran.my.MP4 @0:40.6: senarai resit (Payments) dengan butang muat turun; callout resit pertama pada “resit”. Jumlah RM individu & key diblur",
      blur=[(130, y0, 545, y1, 0, 99) for y0, y1 in [(243, 291), (357, 405), (471, 519), (585, 633), (699, 747), (813, 863), (927, 977), (1041, 1091), (1155, 1205)]],
      callout=[(41.3, 43.6, (8, 200, 585, 300), (8, 200, 585, 300))]),
 dict(id="B4", src=(26.30, 29.08), file="DownloadDocument.mp4", at=19.0, crop=(0, 150, 576, 1024), kb=(1.0, 1.05),
      label="Paparan admin", note="B-ROLL/DownloadDocument.mp4 @0:19.0: admin isi “Add New Document” (Exam, Untitled design.pdf) → Upload → dokumen masuk senarai pelajar. Nama & no. pelajar diblur",
      blur=[(40, 465, 545, 630, 20.38, 99)],
      callout=[(19.0, 20.3, (62, 735, 515, 828), (62, 735, 515, 828)), (20.6, 21.8, (25, 1025, 555, 1095), (25, 1025, 555, 1095))]),
 dict(id="B5", src=(29.08, 32.08), file="UploadDocument.mp4", at=7.7, crop=(0, 40, 592, 1052), kb=(1.0, 1.05),
      label="App ahli", note="B-ROLL/UploadDocument.mp4 @0:07.7: app ahli, tab Documents (Laporan Prestasi, Exam) dengan butang muat turun; callout butang muat turun. Nama & no. pelajar diblur",
      blur=[(25, 285, 567, 445, 0, 99)],
      callout=[(8.45, 10.7, (510, 548, 585, 715), (510, 548, 585, 715))]),
 dict(id="B6", src=(41.62, 44.40), file="UploadDocument.mp4", at=11.3, crop=(0, 40, 592, 1052), kb=(1.0, 1.06),
      label="App ahli", note="B-ROLL/UploadDocument.mp4 @0:11.3: Laporan Prestasi Pelajar dibuka dalam app ahli. Nama sekolah & nama pelajar diblur",
      blur=[(150, 285, 450, 330, 0, 99), (35, 988, 130, 1020, 0, 99), (25, 285, 567, 445, 0, 11.45)],
      callout=[]),
]

# ---------- grafik (masa sumber) ----------
G = [
 dict(k="label", s=0.15, e=3.05, note="Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"),
 dict(k="status", s=5.95, e=8.40, note="Kad 3 status muncul ikut sebutan: Bayar ✓ (6.3) → Belum bayar (7.3) → Overdue (8.2)"),
 dict(k="manual", s=18.30, e=19.70, note="Kad “Resit manual” dipangkah ✗"),
 dict(k="attend", s=20.20, e=26.20, note="Kad Kehadiran: 4 baris (nama sebagai bar kelabu), ✓ ditanda tepat pada “tik-tik-tik”, ✗ pada “tak hadir”"),
 dict(k="docs", s=34.30, e=41.55, note="Kad Dokumen: E-sijil, Reminder, Prestasi anak, Prestasi ahli, Surat jemputan muncul satu-satu ikut sebutan, ikon muat turun"),
 dict(k="logo", s=47.45, e=48.40, note="Logo Yuran.my putih atas pil biru #2A3B8F (tiada shadow) pada “apps Yuran.my”"),
 dict(k="comment", s=49.80, e=51.55, note="Ikon gelembung komen dengan titik menaip pada “Cuba ceritakan di ruangan komen”"),
 dict(k="cta", s=51.62, e=53.73, note="Butang “Sesi demo Yuran.my” + anak panah ke bawah pada “Klik link di bawah”"),
]
DOCS = [("E-sijil", 34.34), ("Reminder", 35.70), ("Prestasi anak", 37.04), ("Prestasi ahli", 38.34), ("Surat jemputan", 40.36)]
STATUS = [("Bayar", 6.26, "ok"), ("Belum bayar", 7.30, "warn"), ("Overdue", 8.15, "bad")]
TICKS = [23.28, 23.56, 23.78]
CROSS = 25.84

SFX = [(0.85, "whoosh", -20)]
def sfx(src, n, db=-22): SFX.append((out(src), n, db))
for b in BR: sfx(b["src"][0] - 0.12, "whoosh", -24)
for _, t, _ in STATUS: sfx(t, "pop", -22)
sfx(18.32, "pop", -22); sfx(18.85, "bonk", -26)
sfx(20.38, "pop", -22)
for t in TICKS: sfx(t, "click", -16)
sfx(CROSS, "bonk", -26)
for _, t in DOCS: sfx(t, "pop", -23)
sfx(47.58, "ding", -22); sfx(49.86, "pop", -22); sfx(51.66, "click", -16)
SFX.append((round(THUMB + BODY_DUR + 0.05, 3), "ding", -22))
# callout B2/B3/B4/B5
sfx(9.16, "click", -18); sfx(16.12, "click", -18); sfx(29.84, "click", -18)

# punch-in zoom: tukar pada permulaan ayat (src)
ZPTS = [0.0, 5.14, 11.44, 14.66, 19.84, 22.56, 24.34, 26.28, 32.20, 34.34, 41.62, 45.46, 48.42, 51.66]
ZOOM = [(out(t), 1.0 if i % 2 == 0 else 1.12) for i, t in enumerate(ZPTS)]

SEG = [
 (0, 1.0, "Thumbnail", "Hook ANDA PERLUKAN SISTEM MACAM MANA? atas frame Farhan (sumber 0:47.0)"),
 (1.0, out(14.62), "Pantau dalam telefon", "Pantau yuran dalam satu skrin telefon: siapa bayar, belum bayar, overdue, berapa lama overdue"),
 (out(14.62), out(19.80), "Resit automatik", "Resit dihantar automatik lepas bayaran; tak perlu resit manual"),
 (out(19.80), out(26.24), "Kehadiran", "Catat kehadiran dalam sistem, tik-tik-tik, siapa hadir / tak hadir"),
 (out(26.24), out(45.42), "Dokumen", "Hantar dokumen (B-roll DownloadDocument / UploadDocument), ahli download dalam apps, senarai jenis dokumen"),
 (out(45.42), out(SRC_DUR), "Penutup & CTA", "Semua dalam apps Yuran.my; ceritakan di komen; klik link di bawah untuk sesi demo"),
 (out(SRC_DUR), DUR, "End card", "Logo putih + Cara MUDAH Urus Yuran + hello@yuran.my + CTA TOFU"),
]

if __name__ == "__main__":
    W = words()
    caps = chunks(W)
    plan = dict(dur=DUR, thumb=THUMB, end=END, body_dur=round(BODY_DUR, 3), cuts=CUTS, caps=caps,
                br=[dict(b, s=out(b["src"][0]), e=out(b["src"][1])) for b in BR],
                g=[dict(x, s=out(x["s"]), e=out(x["e"])) for x in G],
                docs=[(n, out(t)) for n, t in DOCS], status=[(n, out(t), c) for n, t, c in STATUS],
                ticks=[out(t) for t in TICKS], cross=out(CROSS), sfx=sorted(SFX), zoom=ZOOM, seg=SEG,
                thumb_src=47.0)
    json.dump(plan, open(os.path.join(HERE, "plan.json"), "w"), ensure_ascii=False, indent=1)
    print("dur", DUR, "caps", len(caps))
    for c in caps: print(f"{c['s']:6.2f} {' '.join(('*' if w['hl'] else '') + w['t'] for w in c['w'])}")
