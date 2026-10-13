# Inject plan.json and the raw-take list into the preview template.
# usage: build_preview.py plan.json template.html out.html
import json,sys
RAW=[(13,"Apa ni?",0,"Sebelum mula rakam"),(21,"Sembang 6, 3, 2, 1",0,"Kiraan mula"),
 (25.6,"Saya tak kisah anak tu belajar sejam, asalkan satu jam itu dia fokus.",1,"Ambilan 1 dari 4: paling lancar dan bertenaga"),
 (30.6,"Saya tak kisah anak tu belajar satu jam, asalkan satu jam itu. Dia fokus.",0,"Tersasul dan terhenti di tengah"),
 (37.4,"Saya tak kisah anak tu belajar sejam.",0,"Terhenti"),
 (40.8,"Saya tak kisah anak tu belajar sejam, asalkan satu jam itu dia betul-betul fokus.",0,"Jeda panjang di tengah ayat"),
 (48.3,"Saya tak kisah anak tu belajar sejam, asalkan satu jam itu dia fokus.",0,"Elok juga, tapi ambilan 1 lebih bertenaga"),
 (59.2,"Percaya atau tidak?",0,"Ambilan 1: suara masih perlahan"),
 (61.4,"Percaya atau tidak?",1,"Ambilan 2: jadi pembuka hook"),
 (64.6,"Sejam belajar tanpa gangguan lebih bernilai daripada 3 jam belajar sambil scroll-scroll handphone setiap 5 minit.",1,"Hook utama. Saat pertama ditutup grafik kerana penyampai menoleh"),
 (75.4,"Otak perlukan fokus, bukan perlukan masa yang panjang.",1,""),
 (82.4,"Sebab kalau panjang, otak mula merewang.",0,"Ambilan 1"),
 (88.5,"Sebab kalau panjang, otak ni mula merewang.",1,"Ambilan 2: pandang kamera dari awal"),
 (93.5,"Sebab kalau panjang, otak ni mula hilang fokus.",0,"Mula sambil menoleh ke tepi"),
 (100.2,"Kita tengok video panjang-panjang pun, boleh lah tu.",0,"Tersasul"),
 (106.3,"Kita tengok video panjang-panjang pun tak boleh kan? Boleh lah orang kata bebel lah, ceramah lah.",1,""),
 (113.9,"Boleh lah.",0,"Sisa ambilan"),
 (116.7,"Siapa rasa telefon zaman sekarang, siapa rasa telefon ini banyak mengganggu kehidupan kita?",0,"Ayat berulang dalam satu ambilan"),
 (125.7,"Siapa rasa, siapa rasa telefon ini, siapa rasa… paling banyak ganggu dalam waktu?",0,"Tersekat-sekat"),
 (135.6,"Siapa rasa telefon banyak ganggu kita?",0,"Pendek, versi 2:28 lebih lengkap"),
 (141.9,"Siapa rasa telefon banyak ganggu? Siapa rasa telefon banyak ganggu kita? Masa belajar? Masa belajar?",0,"Berulang"),
 (148.6,"Siapa rasa telefon banyak ganggu kita? Masa belajar, masa tidur, masa makan, semua ganggu.",1,"Versi paling lengkap"),
 (155.3,"Siapa rasa? Cuba komen.",1,"Ajakan komen"),
 (157.1,"Saya rasa.",0,"Gurauan selepas ambilan"),
 (161.4,"Saya Al-Farhan, pengusaha pusat tuisyen online.",0,"Ambilan 1: tiada julat umur"),
 (164.5,"Saya Al-Farhan, pengusaha pusat tuisyen untuk umur 14. Eh,",0,"Tersasul"),
 (168.3,"Saya Al-Farhan, pengusaha pusat tuisyen online untuk umur 10 tahun hingga 17 tahun.",1,"Ambilan 3: dipindah ke depan, terus selepas hook")]
raw=[{"t":t,"text":x,"use":u,"why":w} for t,x,u,w in RAW]
p=json.load(open(sys.argv[1]));h=open(sys.argv[2]).read()
h=h.replace("__PLAN__",json.dumps(p,ensure_ascii=False).replace("</","<\\/")).replace("__RAW__",json.dumps(raw,ensure_ascii=False))
open(sys.argv[3],"w").write(h);print(len(h),"bytes")
