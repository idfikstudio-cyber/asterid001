# Mockup storyboard YM "Cara Isi Data didalam Template Migration".
# python3 ym_sb_sheet.py <hi_dir> <shot_dir> <brand_dir> <out_dir>
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ym_datatree as T, ym_sheet as SH
from PIL import Image, ImageDraw

HI, SHOT, BR, OUT = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920; F = T.F
FACE = (530, 450)
def tab(n): return f"{SHOT}/tab_{n}.png"
def raw(t): return Image.open(f"{HI}/r_{t}.png").convert("RGBA").resize((W, H))
def cap(im, words, mode="talk"):
    d = ImageDraw.Draw(im); f = F(T.FX, 66 if mode == "talk" else 56); sp = d.textlength(" ", font=f)
    tw = sum(d.textlength(w, font=f) for w, _ in words) + sp * (len(words) - 1)
    cy = 1340 if mode == "talk" else 1440
    if mode != "talk": d.rounded_rectangle((540 - tw / 2 - 26, cy - 46, 540 + tw / 2 + 26, cy + 46), 22, fill=T.INK)
    x = 540 - tw / 2
    for w, hl in words:
        d.text((x, cy), w, font=f, fill=T.B2 if hl else T.WH, anchor="lm", stroke_width=7 if mode == "talk" else 0, stroke_fill=T.INK); x += d.textlength(w, font=f) + sp
def pip(im, t=40):
    fr = Image.open(f"{HI}/r_{t}.png").convert("RGB").resize((W, H))
    f = fr.crop((FACE[0] - 280, FACE[1] - 280, FACE[0] + 280, FACE[1] + 280)).resize((210, 210))
    m = Image.new("L", (210, 210), 0); ImageDraw.Draw(m).ellipse((0, 0, 209, 209), fill=255)
    d = ImageDraw.Draw(im); d.ellipse((814, 134, 1036, 356), fill=T.WH); im.paste(f, (820, 140), m)
def screen(title, sub, path, cam, hl=(), notes=(), words=None, warn=None, t=40):
    im = T.bg_blue(W, H).convert("RGBA"); SH.header(im, title, sub)
    SH.sheet(im, path, cam, hl, notes)
    if warn: SH.warn_card(im, warn[0], warn[1], 1.0, y=warn[2] if len(warn) > 2 else 1320)
    pip(im, t)
    if words: cap(im, words, "tut")
    return im
def save(im, n): im.convert("RGB").resize((540, 960), Image.LANCZOS).save(f"{OUT}/{n}.jpg", quality=86); print(n)
c = SH.cell

# 0 thumbnail — tajuk sama dengan nama fail video
im = raw(2); g = Image.new("L", (1, H), 0)
for y in range(860, H): g.putpixel((0, y), int(235 * (y - 860) / (H - 860)))
im.paste(Image.new("RGBA", (W, H), T.INK + (255,)), (0, 0), g.resize((W, H))); d = ImageDraw.Draw(im)
d.rounded_rectangle((70, 960, 460, 1040), 40, fill=T.B2); d.text((265, 1000), "TUTORIAL", font=F(T.FX, 50), fill=T.WH, anchor="mm")
for i, (txt, col) in enumerate([("CARA ISI DATA", T.WH), ("DIDALAM", T.WH), ("TEMPLATE", T.B2), ("MIGRATION", T.B2)]):
    d.text((70, 1066 + i * 104), txt, font=F(T.FX, 92), fill=col, stroke_width=4, stroke_fill=T.INK)
save(im, "a0_thumb")
# 1 intro
im = raw(2); T.paste_a(im, T.card("Farhan · Yuran.my", fill=T.B1, ink=T.WH, fs=36), 70, 300); cap(im, [("template", True), ("migration", True)]); save(im, "a1_intro")
# 2 tiga bahagian
im = raw(12)
for i, (nm, tt) in enumerate([("Programs", 1), ("Students", 2), ("Staffs", 3)]):
    T.paste_a(im, T.card(nm, w=420, num=tt, fs=40), 70, 760 + i * 120)
cap(im, [("yang", False), ("ketiga", False), ("adalah", False), ("staff", True)]); save(im, "a2_three")
# 3 tab programs: 4 kumpulan
P = tab("Programs")
groups = [(c("Programs", "A", "F", 3, 3), "Program"), (c("Programs", "G", "H", 3, 3), "Kategori"), (c("Programs", "I", "J", 3, 3), "Modul"), (c("Programs", "K", "L", 3, 3), "Class")]
cam = SH.cam_for((92, 432, 3026, 588), pad=40)
save(screen("Tab Programs", "4 perkara wajib diisi", P, cam, [(b, l, 1.0, "blue") for b, l in groups], words=[("dan", False), ("yang", False), ("keempat", False), ("class", True)]), "b1_groups")
# 4 program
b1, b2 = c("Programs", "A", "A", 4, 5), c("Programs", "B", "B", 4, 5)
save(screen("1 · Program", "Kod program + nama program", P, SH.cam_for((92, 432, 540, 588)), [(b1, "Kod program", 1, "blue"), (b2, "Nama program", 1, "blue")],
            notes=[("AR1 → Bahasa Arab", 1.0)], words=[("kod", False), ("program", True), ("AR1", True)]), "b2_program")
# 5 kategori
save(screen("2 · Kategori", "Kod kategori + nama kategori", P, SH.cam_for((1616, 432, 2084, 588)), [(c("Programs", "G", "G", 4, 5), "Kod kategori", 1, "blue"), (c("Programs", "H", "H", 4, 5), "Nama kategori", 1, "blue")],
            notes=[("PAGI → Sesi Pagi", 1.0)], words=[("nama", False), ("kategori", True), ("sesi", False), ("pagi", False)]), "b3_kategori")
# 6 modul
save(screen("3 · Modul", "Kod modul + nama modul", P, SH.cam_for((2084, 432, 2632, 588)), [(c("Programs", "I", "I", 4, 5), "Kod modul", 1, "blue"), (c("Programs", "J", "J", 4, 5), "Nama modul", 1, "blue")],
            notes=[("L1 → Level 1", 1.0)], words=[("kod", False), ("modul", True), ("L1", True)]), "b4_modul")
# 7 class
save(screen("4 · Class", "Kod class + nama class", P, SH.cam_for((2632, 432, 3026, 588)), [(c("Programs", "K", "K", 4, 5), "Kod class", 1, "blue"), (c("Programs", "L", "L", 4, 5), "Nama class", 1, "blue")],
            notes=[("AR1A → Kelas 1A", 1.0)], words=[("kod", False), ("class", True), ("AR1A", True)]), "b5_class")
# 8 konsisten — kod dihubungkan
im = raw(90)
for i, (k, v) in enumerate([("AR1", "Program"), ("PAGI", "Kategori"), ("L1", "Modul"), ("AR1A", "Class")]):
    T.paste_a(im, T.card(f"{k}  ·  {v}", w=470, num=i + 1, fs=38), 70, 740 + i * 118)
T.paste_a(im, T.card("Kod mesti konsisten", fill=T.B2, ink=T.WH, fs=34), 580, 920)
cap(im, [("pastikan", False), ("konsisten", True)]); save(im, "b6_konsisten")
# 9 fees
fees = c("Programs", "M", "V", 3, 5)
save(screen("Class Fees (RM)", "Masukkan semua yuran yang dikenakan", P, SH.cam_for((3026, 432, 3674, 588), pad=30), [(c("Programs", "M", "M", 4, 5), "Pendaftaran", 1, "blue"), (c("Programs", "N", "N", 4, 5), "Material", 1, "blue"), (c("Programs", "O", "O", 4, 5), "Course", 1, "blue")],
            words=[("fee", True), ("pendaftaran", False)]), "b7_fees")
# 10 trainer (pilihan)
save(screen("Trainer & Assistant", "Pilihan: tak ada pun tak apa", P, SH.cam_for((5078, 432, 6580, 548), pad=30), [(c("Programs", "W", "Z", 3, 4), "Trainer details", 1, "blue"), (c("Programs", "AA", "AD", 3, 4), "Assistant details", 1, "blue")],
            notes=[("Kalau ada, bonus", 1.0)], words=[("tak", False), ("ada", False), ("pun", False), ("tak", False), ("apa", False)]), "b8_trainer")
# 11 tab students — klik tab
ST = tab("Students")
im = T.bg_blue(W, H).convert("RGBA"); SH.header(im, "Tab Students", "Bahagian kedua")
SH.sheet(im, P, (100, 1080, 600, 190), [((420, 1222, 590, 1268), "Klik tab Students", 1, "blue")]); pip(im); cap(im, [("bahagian", False), ("student", True)], "tut"); save(im, "c1_tab_students")
# 12 students: name + class code
save(screen("Tab Students", "Nama pelajar + kod class", ST, SH.cam_for((92, 432, 554, 644)), [(c("Students", "A", "A", 4, 5), "Class Code", 1, "warn"), (c("Students", "B", "B", 4, 5), "Nama pelajar", 1, "blue")],
            words=[("nak", False), ("masuk", False), ("kelas", True), ("mana", False)]), "c2_students")
# 13 PERINGATAN class code
im = T.bg_blue(W, H).convert("RGBA"); SH.header(im, "Penting: Class Code", "Students mesti sama dengan Programs")
# dua panel kecil: Programs K5 dan Students A5
SH.CARD = (40, 380, 1040, 740); SH.sheet(im, P, SH.cam_for((2632, 472, 3026, 588), pad=24, ar=0.36), [(c("Programs", "K", "K", 4, 5), None, 1, "warn")])
SH.CARD = (40, 800, 1040, 1160); SH.sheet(im, ST, SH.cam_for((92, 472, 554, 644), pad=24, ar=0.36), [(c("Students", "A", "A", 4, 5), None, 1, "warn")])
SH.CARD = (40, 380, 1040, 1180)
d = ImageDraw.Draw(im); d.ellipse((495, 725, 585, 815), fill=T.B2); d.text((540, 770), "=", font=F(T.FX, 64), fill=T.WH, anchor="mm")
SH.warn_card(im, "Kod class mesti sama", ["Class Code di tab Students mesti sama", "dengan kod di tab Programs."], 1.0, y=1170)
pip(im); cap(im, [("sama", True), ("dengan", False), ("bahagian", False), ("program", True)], "tut"); save(im, "c3_warning")
# 14 parents
save(screen("Maklumat ibu bapa", "Nama, nombor telefon, email", ST, SH.cam_for((2886, 432, 3564, 644), pad=30), [(c("Students", "M", "M", 4, 5), "Nama", 1, "blue"), (c("Students", "N", "N", 4, 5), "No. telefon", 1, "blue"), (c("Students", "O", "O", 4, 5), "Email", 1, "blue")],
            notes=[("Tiada email? Kami masukkan email dummy", 1.0)], words=[("nama", False), ("nombor", False), ("telefon", False)]), "c4_parents")
# 15 staff access (talking head)
im = raw(168)
T.paste_a(im, T.card("Jangan kongsi ID", fill=T.B1, ink=T.WH, fs=40), 70, 780)
T.paste_a(im, T.card("Activity log untuk setiap ID", fs=36), 70, 900)
cap(im, [("activity", True), ("log", True)]); save(im, "d1_noshare")
# 16 staffs fields + roles
TF = tab("Staffs")
save(screen("Tab Staffs", "Nama, telefon, email dan level", TF, SH.cam_for((92, 480, 1292, 760), pad=30), [(c("Staffs", "A", "A", 4, 5), "Nama", 1, "blue"), (c("Staffs", "C", "C", 4, 5), "Email", 1, "blue"), (c("Staffs", "D", "D", 4, 5), "Telefon", 1, "blue"), ((1100, 480, 1292, 760), "Level", 1, "warn")],
            notes=[("admin · supervisor · clerk", 1.0), ("class-assistant · class-admin", 1.0)], words=[("supervisor", True), ("clerk", True)]), "d2_staffs")
# 17 penutup
im = raw(190); T.paste_a(im, T.card("Data sedia untuk migrasi", fill=T.B2, ink=T.WH, fs=40), 70, 900)
cap(im, [("data", True), ("dah", False), ("ready", False)]); save(im, "d3_ready")
# end card
im = Image.new("RGB", (W, H), T.B1); d = ImageDraw.Draw(im)
lg = Image.open(f"{BR}/logo_white.png").convert("RGBA"); lg = lg.resize((560, int(560 * lg.height / lg.width)), Image.LANCZOS); im.paste(lg, ((W - 560) // 2, 640), lg)
d.text((W / 2, 1060), "Cara MUDAH Urus Yuran", font=F(T.FX, 64), fill=T.WH, anchor="mm")
d.rounded_rectangle((110, 1180, 970, 1290), 55, fill=T.B2); d.text((W / 2, 1235), "Follow untuk tips urus yuran sekolah", font=F(T.FB, 40), fill=T.WH, anchor="mm")
d.text((W / 2, 1380), "hello@yuran.my", font=F(T.FB, 46), fill=T.GR, anchor="mm"); save(im, "e_end")
# klik tab Staffs
im = T.bg_blue(W, H).convert("RGBA"); SH.header(im, "Tab Staffs", "Bahagian ketiga")
SH.sheet(im, ST, (100, 1080, 760, 190), [((636, 1222, 740, 1268), "Klik tab Staffs", 1, "blue")]); pip(im); cap(im, [("bahagian", False), ("staff", True), ("pula", False)], "tut"); save(im, "d0_tab_staffs")
