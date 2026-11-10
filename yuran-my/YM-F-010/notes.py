# Teks status, perkara PERLU SEMAK dan caption TikTok untuk YM-F-010 (digunakan oleh build_page.py & RINGKASAN)
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "plan.json")))
def o(src):  # masa sumber -> masa video siap
    t = src - (P["cuts"][0][1] - P["cuts"][0][0] if src >= P["cuts"][0][1] else 0)
    return round(P["thumb"] + t, 2)

HOOK = "ANDA PERLUKAN / SISTEM / MACAM MANA?  (MACAM MANA? dalam kotak biru aksen #29ABE2)"
CTA = ("Sebutan Farhan: “Anda perlukan sistem macam mana? Cuba ceritakan di ruangan komen. Klik link di bawah untuk sesi demo.” "
       "→ grafik gelembung komen + butang “Sesi demo Yuran.my” dengan anak panah ke bawah. "
       "End card (TOFU, ikut DNA): logo Yuran.my putih + Cara MUDAH Urus Yuran + “Follow untuk tips urus yuran sekolah” + hello@yuran.my")
TT = ("Anda perlukan sistem macam mana? Dengan Yuran.my, pantau siapa dah bayar, belum bayar dan overdue dalam satu skrin handphone. "
      "Resit dihantar secara automatik, kehadiran tinggal tik je, dan ahli boleh download dokumen terus dalam apps. "
      "Cuba ceritakan di ruangan komen 👇")
HS = "#yuranmy #sistemyuran #kutipanyuran #sekolahkafa #adminsekolah"

TODO = [
 ("“E-sijil” (transkrip awal: “Isi jil”)", "Whisper pertama dengar “Isi jil”; 3 kali dengar semula semuanya “E-sijil”. Caption tulis “E-sijil”. Sahkan.", o(34.34)),
 ("“Semua yang saya cerita dengan ni”", "Caption ikut transkrip. Mungkin “cerita tadi ni”. Sahkan perkataan sebenar.", o(45.86)),
 ("CTA: sebutan vs DNA", "Farhan sebut “Klik link di bawah untuk sesi demo” (gaya BOFU), tetapi skrip bertag TOFU, jadi end card guna CTA TOFU DNA “Follow untuk tips urus yuran sekolah”. Di TikTok link ada di bio, bukan “di bawah”. Pilih: kekal, atau tukar end card ke CTA demo / link di bio seperti YM-F-002/003.", o(51.66)),
 ("Tiada muzik latar", "Folder Yuran.my tiada MUSIC/ (peraturan: muzik dari MUSIC/ sahaja). Video tanpa muzik. Jika mahu muzik, letak fail dalam MUSIC/ atau luluskan muzik luar (YM-F-002/003 guna Mixkit)."),
 ("Durasi 56.0 s melebihi TOFU 20–45 s", "Video Farhan 53.7 s sudah ditrim; isi tidak dipotong (hanya satu senyap 0.22 s dibuang). Thumbnail 1 s + end card 1.5 s."),
 ("Angka dalam B-roll dashboard", "B-roll Pantau Yuran (akaun demo) papar 43 Overdue Invoices, RM 6,450 Overdue Amount, 4 Average Days Overdue. Angka ini tidak disebut Farhan (DNA §7). Callout hanya pada kad, tiada teks angka ditambah. Sahkan boleh papar atau perlu blur.", o(8.40)),
 ("Nama fail B-roll dokumen terbalik dengan isi", "DownloadDocument.mp4 sebenarnya admin MUAT NAIK dokumen (Add New Document → Upload), UploadDocument.mp4 ialah app ahli lihat/MUAT TURUN. Dipadankan ikut isi: DownloadDocument pada “kita boleh hantar dokumen”, UploadDocument pada “Ahli download sahaja” dan “Semua kita boleh download”.", o(26.30)),
 ("Laporan Prestasi dalam B-roll", "Markah subjek kelihatan. Nama sekolah (SMK … SRI AMAN) dan nama pelajar di ruang tandatangan diblur; nama murid & guru dalam dokumen sudah XXX. Sahkan contoh laporan ini boleh dipapar.", o(41.62)),
 ("Preview MP4 belum di Drive", "Alat Drive hadkan 4.2 MB setiap muat naik; preview 7.2 MB. MP4 ada di halaman ini. THUMB.png dan RINGKASAN sudah di 02_EDITED/_PREVIEW/."),
 ("edit-log.csv belum dikemas kini", "Alat Drive tidak boleh menulis isi fail sedia ada. Baris log ada dalam RINGKASAN (bahagian 7); tambah manual ke 03_LOG/edit-log.csv."),
 ("Tiada video rujukan gaya", "BRAND/ Yuran.my tiada rujukan-gaya-*.mp4. Farhan setuju teruskan ikut DNA sahaja."),
]
DONE = [
 ("Video sudah ditrim", "TOFU_SistemMacamMana.mp4 (53.7 s, 1080×1920). Isi tidak dipotong. Satu senyap 0.42 s (selepas “lain-lain”) dipendekkan 0.22 s, disorok oleh B-roll.", o(3.27)),
 ("Thumbnail 1 saat", "ANDA PERLUKAN / SISTEM / MACAM MANA? atas frame Farhan senyum memegang telefon (sumber 0:47.0). Dari tajuk skrip & ayat Farhan. Tiada logo di awal. THUMB.png dieksport.", 0.3),
 ("B-roll dokumen (permintaan Farhan)", "DownloadDocument (paparan admin: Add New Document → Upload → dokumen Exam masuk senarai) pada “kita boleh hantar dokumen”. UploadDocument (app ahli: tab Documents, butang muat turun, Laporan Prestasi dibuka) pada “Ahli download sahaja dokumen…” dan “Semua kita boleh download…”. Nama & no. pelajar diblur.", o(26.30)),
 ("B-roll sistem lain", "Pantau Yuran: dashboard di skrin telefon (“satu skrin handphone”) dan kad Overdue dengan callout pada “berapa lama overdue”. Apps Yuran.my: senarai resit (jumlah RM individu & key diblur) pada “resit dihantar secara automatik”. Setiap sisipan ≤3 s, suara terus berjalan.", o(3.27)),
 ("Motion ringkas", "Status Bayar / Belum bayar / Overdue ikut sebutan; Resit manual dipangkah; kad Kehadiran dengan ✓ tepat pada “tik-tik-tik” dan ✗ pada “tak hadir”; kad Dokumen (E-sijil, Reminder, Prestasi anak, Prestasi ahli, Surat jemputan) muncul ikut sebutan; logo Yuran.my; gelembung komen; butang Sesi demo. Semua di paras dada, muka Farhan tidak ditutup.", o(20.2)),
 ("Caption & ejaan", "1–3 perkataan, Inter ExtraBold (ganti Acumin Pro), outline gelap, dalam safe zone (atas 80%, kiri 85%). “automatik” (transkrip: otomatik), “Yuran.my”. Kata kunci biru: penting, skrin, handphone, bayar, belum, overdue, lama, resit, automatik, manual, kehadiran, hadir, laporan, dokumen, download, E-sijil, reminder, prestasi, surat jemputan, Yuran.my, komen, demo.", 2.0),
 ("Label & punch-in", "Pil “Farhan · Yuran.my” 0:01.2–0:04.0. Punch-in 100% ↔ 112% pada permulaan ayat (14 kali), mata kekal di sepertiga atas.", 1.2),
 ("Audio", "High-pass 70 Hz, denoise ringan (afftdn 8 dB), kompresor lembut 2.5:1, normalize −14.0 LUFS (peak −1.5 dBFS). SFX lembut dijana sendiri."),
 ("End card", "1.5 s latar biru #2A3B8F, logo putih (tiada shadow/lutsinar), Cara MUDAH Urus Yuran, CTA TOFU, hello@yuran.my.", o(53.73)),
]
LOG = ("YM-F-010,SistemMacamMana,FARHAN,TOFU,56.0,PREVIEW,\"Preview v1 10/11/2026 (540x960). Video trim Farhan 53.7s, isi tidak dipotong (senyap 0.22s dibuang). "
       "Durasi 56.0s melebihi TOFU 45s. B-roll DownloadDocument (admin hantar dokumen) & UploadDocument (app ahli download) atas permintaan Farhan + Pantau Yuran + Apps Yuran.my; nama/no. pelajar, nama sekolah, jumlah RM individu diblur. "
       "Tiada muzik (MUSIC/ tiada). Tiada rujukan-gaya (Farhan setuju). Font Inter ganti Acumin Pro. PERLU SEMAK: E-sijil, 'cerita dengan ni', CTA end card TOFU vs sebutan demo, angka dashboard demo.\"")
