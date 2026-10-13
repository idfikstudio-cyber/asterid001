# Edit decision list for CFik016.MOV (source seconds). Order = output order.
# One best take per sentence; retakes, false starts and long pauses removed.
SEG=[
 ("hook","Klien memang tahu apa yang dia nak, tapi susah nak cerita kat contractor",37.70,41.68),
 ("A","Tak semua orang nak interior design uruskan A sampai Z, daripada design sampai renovation",0.22,5.00),
 ("B","Ada klien yang memang nak design sahaja ... uruskan renovation sendiri",22.80,28.05),
 ("D1","Fikir",71.44,71.86),
 ("D2","studio boleh bantu dengan layout 3D",72.26,74.72),
 ("D3","dan drawing untuk mulakan kerja renovation ini",79.06,81.58),
 ("E1","Kalau nak design rumah dulu, dapatkan visual akhir ... kontraktor cari sendiri",143.42,149.04),
 ("E2","Boleh DM kami, kita akan bagikan suggestion yang terbaik untuk rumah anda",160.72,164.52),
 ("F2","kita akan bincang macam mana nak cantikkan rumah sebelum hantarkan design tu kepada kontraktor untuk buat kerja",170.66,176.28),
 ("F3","DM kami ya",176.58,177.55),
]
def table():
    o=0;out=[]
    for n,txt,s,e in SEG: out.append({"id":n,"text":txt,"src_in":s,"src_out":e,"out_in":round(o,3)}); o+=e-s
    return out,round(o,3)
if __name__=="__main__":
    import json,sys
    t,d=table(); json.dump({"segments":t,"duration":d},open(sys.argv[1],"w"),ensure_ascii=False,indent=1); print(d)
