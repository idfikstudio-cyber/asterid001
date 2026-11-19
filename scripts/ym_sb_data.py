# Mockup storyboard YM "Macam mana nak susun data": frame raw + grafik dari ym_datatree.
# python3 ym_sb_data.py <hi_dir> <brand_dir> <out_dir>
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ym_datatree as T
from PIL import Image, ImageDraw

HI, BR, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
F, S = T.F, T.S
def raw(t): return Image.open(f"{HI}/r_{t}.png").convert("RGBA").resize((W, H))
def cap(im, words, mode="talk"):
    d = ImageDraw.Draw(im); f = F(T.FX, 66 if mode == "talk" else 56); sp = d.textlength(" ", font=f)
    tw = sum(d.textlength(w, font=f) for w, _ in words) + sp * (len(words) - 1)
    cx, cy = (W / 2, 1340) if mode == "talk" else (650, 1390)
    if mode != "talk": d.rounded_rectangle((cx - tw / 2 - 26, cy - 46, cx + tw / 2 + 26, cy + 46), 22, fill=T.INK)
    x = cx - tw / 2
    for w, hl in words:
        d.text((x, cy), w, font=f, fill=T.B2 if hl else T.WH, anchor="lm", stroke_width=7 if mode == "talk" else 0, stroke_fill=T.INK); x += d.textlength(w, font=f) + sp
def pip(im, t):
    fr = Image.open(f"{HI}/r_{t}.png").convert("RGB").resize((W, H))
    f = fr.crop((525 - 280, 525 - 280, 525 + 280, 525 + 280)).resize((230, 230))
    m = Image.new("L", (230, 230), 0); ImageDraw.Draw(m).ellipse((0, 0, 229, 229), fill=255)
    d = ImageDraw.Draw(im); d.ellipse((34, 1324, 276, 1566), fill=T.WH); im.paste(f, (40, 1330), m)
def save(im, n): im.convert("RGB").resize((540, 960), Image.LANCZOS).save(f"{OUT}/{n}.jpg", quality=86); print(n)

# 0 thumbnail
im = raw(123.5); g = Image.new("L", (1, H), 0)
for y in range(900, H): g.putpixel((0, y), int(235 * (y - 900) / (H - 900)))
im.paste(Image.new("RGBA", (W, H), T.INK + (255,)), (0, 0), g.resize((W, H))); d = ImageDraw.Draw(im)
d.rounded_rectangle((80, 1020, 470, 1100), 40, fill=T.B2); d.text((275, 1060), "TUTORIAL", font=F(T.FX, 50), fill=T.WH, anchor="mm")
for i, (t, c) in enumerate([("SUSUN DATA", T.WH), ("DULU, BARU", T.WH), ("GUNA SISTEM", T.B2)]):
    d.text((80, 1130 + i * 108), t, font=F(T.FX, 96), fill=c, stroke_width=4, stroke_fill=T.INK)
save(im, "a0_thumb")
# 1 intro + label
im = raw(1); d = ImageDraw.Draw(im)
lb = T.card("Farhan · Yuran.my", fill=T.B1, ink=T.WH, fs=36); T.paste_a(im, lb, 70, 300)
cap(im, [("sistem", False), ("Yuran.my", True)]); save(im, "a1_intro")
# 2 bersepah -> tersusun
im = raw(12); T.messy_to_tidy(im, 12.0, 11.1, 99, 15.2); cap(im, [("Tanpa", False), ("data", True), ("yang", False), ("tersusun", False)]); save(im, "a2_messy")
im = raw(12); T.messy_to_tidy(im, 14.5, 11.1, 13.5, 15.2); save(im, "a2b_tidy")
# 3 senarai 4 komponen
im = raw(24); T.list4(im, 28.0, [22.1, 23.7, 25.3, 27.0], 33.2); cap(im, [("kena", False), ("ada", False), ("kelas", True)]); save(im, "a3_list")
im = raw(30); T.list4(im, 31.5, [22.1, 23.7, 25.3, 27.0], 33.2, chain_t=29.6); cap(im, [("berkait", True), ("rapat", False)]); save(im, "a4_chain")
# 5 pokok penuh — berperingkat
R = [40.6, 42.0, 48.3, 57.5]
for n, t, c in [("b1_program", 41.5, [("Program", True), ("tu", False), ("bahasa", False), ("Arab", False)]),
                ("b2_kategori", 47.0, [("sesi", False), ("petang", True), ("ataupun", False), ("sesi", False), ("pagi", True)]),
                ("b3_modul", 54.0, [("Peringkat", False), ("2", True)]),
                ("b4_kelas", 63.0, [("kelas", False), ("3,", True), ("kelas", False), ("4", True)])]:
    im = T.bg_blue(W, H).convert("RGBA")
    rv = [r if r <= t else None for r in R]
    T.tree(im, t, rv); pip(im, 40); cap(im, c, "tut"); save(im, n)
im = T.bg_blue(W, H).convert("RGBA"); T.tree(im, 67.5, R, names={0: ("Adiwira", 65.6), 1: ("Wira", 66.3), 2: ("Satria", 67.0)})
pip(im, 40); cap(im, [("kelas", False), ("satria", True)], "tut"); save(im, "b5_rename")
# 6 simulasi Abu langkah demi langkah
AT = [70.9, 72.2, 74.6, 77.2, 80.1]
for n, t, c in [("c1_abu_start", 71.5, [("nama", False), ("dia", False), ("Abu", True)]),
                ("c2_abu_kat", 75.3, [("masuk", False), ("sesi", True), ("petang", True)]),
                ("c3_abu_kelas", 81.6, [("Nampak", False), ("tak", False), ("kaitan", True), ("dia?", False)])]:
    im = T.bg_blue(W, H).convert("RGBA"); T.abu_flow(im, t, AT, glow_t=81.3); pip(im, 70); cap(im, c, "tut"); save(im, n)
# 6b jenis institusi
IT = [86.6, 87.7, 88.8, 89.8, 90.8, 91.8]
for n, t, c in [("c4_inst_mid", 88.9, [("institusi", True)]), ("c5_inst_full", 92.5, [("operasi", False), ("dia", False), ("macam", False), ("mana", False)])]:
    im = T.bg_blue(W, H).convert("RGBA"); T.inst_list(im, t, 85.9, IT); pip(im, 83); cap(im, c, "tut"); save(im, n)
# 7 banyak program & sesi
im = raw(96); T.chips_rows(im, 106.0, [("Program Bahasa Arab", [("Intensif", 95.1), ("Mingguan", 98.0), ("Bulanan", 100.0)]), ("Sesi", [("Pagi", 103.4), ("Petang", 104.4), ("Malam", 105.4)])], 107.4)
cap(im, [("sesi", False), ("malam", True)]); save(im, "d1_many")
# 8 callback tersusun
im = raw(119); T.messy_to_tidy(im, 120.8, 118.5, 119.0, 122.1, label_b="Sedia guna sistem"); cap(im, [("barulah", False), ("guna", False), ("sistem", True)]); save(im, "d2_ready")
# 9 end card
im = Image.new("RGB", (W, H), T.B1); d = ImageDraw.Draw(im)
lg = Image.open(f"{BR}/logo_white.png").convert("RGBA"); lg = lg.resize((560, int(560 * lg.height / lg.width)), Image.LANCZOS); im.paste(lg, ((W - 560) // 2, 640), lg)
d.text((W / 2, 1060), "Cara MUDAH Urus Yuran", font=F(T.FX, 64), fill=T.WH, anchor="mm")
d.rounded_rectangle((110, 1180, 970, 1290), 55, fill=T.B2); d.text((W / 2, 1235), "Follow untuk tips urus yuran sekolah", font=F(T.FB, 40), fill=T.WH, anchor="mm")
d.text((W / 2, 1380), "hello@yuran.my", font=F(T.FB, 46), fill=T.GR, anchor="mm"); save(im, "e_end")
# talking head biasa
for n, t, c in [("a5_depend", 83, [("bergantung", False), ("kepada", False)]), ("a6_share", 108, [("kongsikan", False), ("dengan", False), ("kami", False)])]:
    im = raw(t).resize((int(W * 1.12), int(H * 1.12))).crop((60, 40, 60 + W, 40 + H)) if n == "a5_depend" else raw(t)
    cap(im, c); save(im, n)
