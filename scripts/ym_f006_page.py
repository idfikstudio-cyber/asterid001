# Bina halaman preview Artifact YM-F-006 (susun atur sama seperti YM-F-001..005).
# usage: python3 ym_f006_page.py <out.html> [lufs-text]
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
full = open(os.path.join(HERE, "ym_f006_render.py")).read()
src = full.split("# ---------- frames sumber")[0]
src = src.replace("SRC, AS, SFX, MUS, OUT = sys.argv[1:6]", "SRC=AS=SFX=MUS=OUT=''").replace("W = int(sys.argv[6])", "W = 1080")
src = src.replace("CRF = sys.argv[7] if len(sys.argv) > 7 else \"20\"", "CRF='20'").replace("os.makedirs(OUT, exist_ok=True)", "")
src += "\nTAP = 0.80\n" + full[full.index("SFXL = ["):full.index("def audio")]
R = {}; exec(src, R)
O = R["OFF"]; D = round(R["TOTAL"], 3); BE = R["BODY_END"]
LUFS = sys.argv[2] if len(sys.argv) > 2 else "−14.0 LUFS, peak −1.4 dBFS."

caps = []
for a, b, s in R["CAP"]:
    w = []
    for i, p in enumerate(s.split("*")):
        for t in p.split():
            key = t.strip(".,?")
            fx = None
            if key == "Tekan": fx = "Kan"
            elif key == "blast": fx = "belas"
            elif key == "invois": fx = "invoice (ejaan DNA: invois)"
            elif key == "reminder" and a < 1: fx = "‘reminder’ kurang jelas (keyakinan rendah); cubaan lain dengar ‘mana’"
            w.append({"t": t, "hl": i % 2 == 1, "fix": fx})
    caps.append({"s": round(a + O, 2), "e": round(b + O, 2), "w": w})

g = lambda k: (O + R[k][0], O + R[k][1])
mg = [
 [0, 1.0, "Thumbnail", "Thumbnail 1 s: HANTAR / REMINDER (kotak biru aksen) / yuran guna / WhatsApp? + potongan sebenar butang WhatsApp hijau dari B-roll sistem (ditanda bulatan biru), atas frame Farhan senyum ke kamera (sumber 0:03.0)"],
 [O + R["LABEL_IN"], O + R["LABEL_OUT"], "Label nama", "Pil biru #2A3B8F “Farhan · Yuran.my”, atas-kiri"],
 [*g("BR_DASH"), "B-roll sistem", "B-Roll_SistemYuran.my (0:02): dashboard, zoom perlahan ke kad “Overdue Invoice Alerts” + callout biru, pada “beberapa cara untuk follow up bayaran”"],
 [*g("BR_INV"), "B-roll sistem", "B-Roll_SistemYuran.my (0:24.5): skrin Invoice, callout pada butang “Auto Generate Billing”, pada “generate invois ni”"],
 [*g("BR_APP"), "B-roll apps", "Apps Yuran.my.MP4 (0:07–0:10): app telefon dengan senarai “Unpaid Invoices”, dalam bingkai telefon, pada “invois tu dah terpapar dalam apps”"],
 [*g("CARD_CH"), "Kad grafik", "Invois dihantar ke… → [Apps] → [Email] → ✓ Pelanggan dapat automatik"],
 [*g("BR_OVD"), "B-roll sistem", "B-Roll_SistemYuran.my (0:33): senarai invois ditapis OVERDUE (baris merah), callout pada lajur status, pada “tak buka apps ataupun tak buka email”"],
 [*g("CARD_WA"), "Kad grafik", "“Reminder bayaran” → [WhatsApp] (hijau) → [SMS]"],
 [*g("NUM"), "Angka", "“5 orang” teks besar (Farhan sebut “lima orang”)"],
 [*g("BR_WA"), "B-roll WhatsApp", "B-Roll_SistemYuran.my (0:24.5): skrin Invoice zoom ke lajur Action → bulatan biru + label “Button WhatsApp” pada butang hijau (" + f"{O + R['WA_RING']:.1f}" + " s) → kursor bergerak dan tekan butang, riak hijau (" + f"{O + R['WA_TAP']:.1f}" + " s, tepat pada “button WhatsApp tu”). Data demo, tidak diblur (arahan Farhan)"],
 [*g("CARD_COST"), "Kad grafik", "Button WhatsApp → pil FREE (pada “free je”) | WhatsApp/SMS pukal → pil Kredit top up (pada “kredit”)"],
 [*g("CARD_OFF"), "Kad grafik", "WhatsApp official (perisai hijau) → ✓ Berdaftar secara rasmi → ✓ Kena bayar → “Bukan kita yang ambil, WhatsApp yang ambil”"],
 [*g("CARD_BAN"), "Kad amaran", "✗ WhatsApp tak rasmi → ⚠ Risiko kena BAN (merah) + close-up muka 145% pada “kena ban pun ada”"],
 [O + R["CMT_IN"], BE, "Motion komen", "Panel komen naik: “Nak tengok cara on WhatsApp pukal?” → “Nak” ditaip pada “Comment nak” → butang hantar berdenyut. Tiada komen palsu"],
 [BE, D, "End card", "Logo putih + Cara MUDAH Urus Yuran + kad profil TikTok Yuran.My Street @yuran.my, + Follow ditekan jadi Following ✓ + Follow TikTok Yuran.my untuk tips urus yuran sekolah"],
]
sfx = [[round(t, 2), f.replace(".wav", "")] for t, f, gn in R["SFXL"]]
zoom = [{"t": round(t + O, 2), "m": "100% (asas)" if z == 1 else f"{round(z*100)}% punch-in"} for t, z in R["ZOOM"]]
zoom.append({"t": round(62.70 + O, 2), "m": "145% close-up muka pada “kena ban pun ada” (hingga " + f"{63.75 + O:.1f}" + " s)"})
zoom.sort(key=lambda x: x["t"])
SEG = [
 [0, 1.0, "Thumbnail", "Hook HANTAR REMINDER YURAN GUNA WHATSAPP? + butang WhatsApp sebenar"],
 [1.0, O + 8.16, "Soalan", "Boleh hantar reminder? Boleh je. Beberapa cara follow up bayaran (B-roll dashboard)"],
 [O + 8.16, O + 23.86, "Apps & email", "Invois terpapar dalam apps (B-roll invois + apps), atau email, pelanggan dapat automatik"],
 [O + 23.86, O + 32.08, "Tak buka?", "Pelanggan tak buka apps/email (B-roll overdue) → reminder guna WhatsApp atau SMS"],
 [O + 32.08, O + 42.34, "Button WhatsApp", "5 orang → button WhatsApp (B-roll butang hijau ditekan) → reminder pembayaran → free"],
 [O + 42.34, O + 57.58, "Pukal & official", "WhatsApp/SMS pukal guna kredit top up; WhatsApp official berdaftar, bayaran diambil WhatsApp"],
 [O + 57.58, O + 65.96, "Tak rasmi = risiko", "WhatsApp tak rasmi boleh kena ban. Tak caya? Cuba chat"],
 [O + 65.96, BE, "Comment nak", "Ajak comment “nak” untuk tutorial on WhatsApp pukal"],
 [BE, D, "End card", "CTA TOFU Follow TikTok @yuran.my"],
]
DONE = [
 ["B-roll butang WhatsApp (arahan Farhan)", "Pada “kita sediakan button WhatsApp je. Tekan je button WhatsApp tu” skrin Invoice dari B-Roll_SistemYuran.my zoom ke lajur Action: bulatan biru + label “Button WhatsApp” pada butang hijau, kursor tekan butang tepat pada perkataan “button WhatsApp tu”, dengan bunyi click lembut. Data demo dipaparkan tanpa blur (arahan Farhan).", O + R["BR_WA"][0]],
 ["B-roll sistem lain ikut apa disebut", "Dashboard (Overdue Invoice Alerts) pada “follow up bayaran”, skrin Invoice (Auto Generate Billing) pada “generate invois”, app telefon Unpaid Invoices (Apps Yuran.my.MP4) pada “terpapar dalam apps”, senarai invois OVERDUE pada “tak buka apps ataupun email”. Setiap sisipan ≤ 3 s, suara terus berjalan.", O + R["BR_DASH"][0]],
 ["Guna video trim Farhan", "TOFU_Boleh hantar reminder yuran ke.mp4 (74.6 s, 1080×1920). Tiada take ulangan dan tiada senyap lebih 0.3 s, jadi isi tidak dipotong.", 1.0],
 ["Thumbnail 1 saat", "HANTAR REMINDER yuran guna WhatsApp? (5 perkataan, dari tajuk skrip & apa yang disebut) + potongan butang WhatsApp sebenar. Tiada logo di awal. PNG 1080×1920 berasingan dieksport.", 0.3],
 ["Kad grafik ikut ayat", "Apps/Email → automatik; WhatsApp/SMS; 5 orang; Button WhatsApp FREE vs pukal Kredit top up; WhatsApp official; amaran tak rasmi → risiko ban. Semua teks dari apa yang disebut. Tiada harga atau statistik ditambah.", O + R["CARD_CH"][0]],
 ["Caption", "Sepanjang video, 1–4 perkataan, Inter ExtraBold putih + outline gelap. Kata kunci biru #29ABE2: reminder, invois, apps, email, automatik, WhatsApp, SMS, button, lima, free, pukal, kredit, top up, berdaftar, official, rasmi, ban, comment nak. Ejaan DNA: invois, Yuran.my.", 3.0],
 ["End card TOFU", "CTA Follow TikTok @yuran.my, gaya YM-F-004/005 yang diluluskan.", BE + 0.3],
 ["Audio", "High-pass 70 Hz, denoise ringan, kompresor lembut, normalize −14 LUFS; muzik ~24 dB di bawah suara dengan ducking.", None],
]
TODO = [
 ["Durasi 77.1 s melebihi TOFU (20–45 s)", "Isi tidak dipotong (peraturan). Jika mahu lebih pendek, Farhan boleh pilih bahagian untuk dibuang, contohnya “Tak caya? Cuba chat. Kami tak tipu.” (1:04.8–1:06.9) atau ayat berulang tentang apps.", None],
 ["“reminder bayaran” pada ayat pertama", "Whisper kurang yakin pada perkataan ‘reminder’ (0:00.6); satu cubaan dengar ‘hantar mana bayaran’. Caption tulis “Boleh hantar reminder bayaran ke” (sama dengan tajuk skrip). Sila dengar dan sahkan.", 1.6],
 ["“Tekan je button WhatsApp tu”", "Transkrip dengar ‘Kan dia button’; cubaan lain dengar ‘Tekan je’. Caption tulis “Tekan je”. Sila sahkan.", O + 36.24],
 ["“blast” dan “Cuba chat”", "Transkrip dengar ‘belas’; caption tulis ‘blast’. ‘Tak caya? Cuba chat.’ ditulis seperti didengar (mungkin maksud ‘check’?).", O + 57.76],
 ["Dakwaan bayaran WhatsApp & ban", "Kad memaparkan “Kena bayar”, “Bukan kita yang ambil, WhatsApp yang ambil” dan “Risiko kena BAN”, semuanya seperti disebut Farhan. Tiada angka harga kredit ditambah. Pastikan selesa dengan fakta ini untuk akaun syarikat.", O + R["CARD_OFF"][0]],
 ["Tiada B-roll top up / WhatsApp pukal", "B-ROLL tiada rakaman skrin top up kredit atau tetapan WhatsApp official, jadi bahagian ini guna kad grafik. Jika ada rakaman, boleh ganti.", O + R["COST_KR"]],
 ["Data demo dalam B-roll", "Nama pelajar, IC dan jumlah dalam Sek Integrasi Demo (demo.yuran.vip) dan app telefon dipaparkan tanpa blur, ikut arahan Farhan (data demo).", O + R["BR_WA"][0]],
 ["Muzik dari luar folder MUSIC/", "MUSIC/ Yuran.my kosong. Guna “Dreaming Big” (Ahjay Stelino), Mixkit Stock Music Free License, sama seperti YM-F-005.", None],
 ["Tiada video rujukan gaya", "BRAND/ tiada rujukan-gaya-*.mp4 (Farhan setuju ikut DNA untuk YM-F-003 hingga 005).", None],
 ["Preview MP4 belum di Drive", "Alat Drive tidak dapat muat naik fail video besar. RINGKASAN dimuat naik ke 02_EDITED/_PREVIEW; MP4 preview dan thumbnail ada di halaman ini.", None],
]
TT = "Boleh hantar reminder yuran guna Yuran.my? Boleh je! Invois terus masuk apps & email secara automatik. Nak follow up? Tekan je button WhatsApp, free. Nak hantar pukal? Guna WhatsApp official dengan kredit top up, tak risau kena ban. Nak tengok cara on WhatsApp pukal? Comment “nak” 👇"
HS = "#yuranmy #yuransekolah #sekolahkafa #reminderyuran #whatsappbusiness"

data = {"caps": caps, "mg": [[round(a, 2), round(b, 2), k, d] for a, b, k, d in mg], "sfx": sfx, "zoom": zoom, "dur": D}
tpl = open(os.path.join(HERE, "ym_f006_template.html")).read()
r2 = lambda L: [[a, b] + ([round(c, 2)] if c is not None else []) for a, b, c in L]
js = (f"const DATA={json.dumps(data, ensure_ascii=False)};\nconst SEG={json.dumps([[round(a,2),round(b,2),k,d] for a,b,k,d in SEG], ensure_ascii=False)};\n"
      f"const DONE={json.dumps(r2(DONE), ensure_ascii=False)};\nconst TODO={json.dumps(r2(TODO), ensure_ascii=False)};\n"
      f"const TT={json.dumps(TT, ensure_ascii=False)};\nconst HS={json.dumps(HS)};\n")
out = tpl.replace("/*DATA*/", js).replace("{{DUR}}", f"{D:.1f}").replace("{{NQ}}", str(len(TODO))).replace("{{LUFS}}", LUFS)
open(sys.argv[1], "w").write(out)
json.dump({"data": data, "SEG": SEG, "DONE": DONE, "TODO": TODO, "TT": TT, "HS": HS}, open(sys.argv[1] + ".json", "w"), ensure_ascii=False, indent=1)
print("OK", D, len(caps))
