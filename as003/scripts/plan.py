# Build the edit plan (output timeline) for As003: captions, motion graphics, B-roll, SFX, zoom, music, end card.
# usage: plan.py cut.json edl.json out.json
import json,re,sys
words=[w for s in json.load(open(sys.argv[1])) for w in s["words"]]
edl=json.load(open(sys.argv[2]));SPEECH=edl["duration"]
FIX={"exam.":"SPM.","jaga":"jangka","Aya?":"ayah?","Ibu":"ibu","score":"skor"}
W=[]
for w in words:
    t=w["w"].strip();t=FIX.get(t,t)
    if t.startswith("-") and W: W[-1]["w"]+=t;W[-1]["e"]=w["e"];continue
    W.append({"w":t,"s":round(w["s"],2),"e":round(w["e"],2)})
# caption chunks: <=3 words, break on punctuation or gap
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.4:
        end=nxt["s"] if nxt and nxt["s"]-w["e"]<0.4 else w["e"]+0.15
        chunks.append({"s":cur[0]["s"],"e":round(end,2),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"]} for x in cur]});cur=[]
HOT={"berbuah","tanam","markah","SPM","skor","straight","A","proses","yakin","bertanya","konsisten","seronok","sikap","berlari-lari","masa","akar","penting","jangka","pendek","komen"}
for c in chunks:
    for x in c["words"]:
        if re.sub(r"[^\w-]","",x["w"]) in HOT: x["hot"]=1
END=round(SPEECH,2);DUR=round(END+5.0,2)
# B-roll cutaways (real footage, Mixkit Stock Video Free License). x = horizontal crop centre (0..1) for 9:16.
B=[
 {"s":1.15,"e":3.07,"id":47540,"src":24,"x":0.50,"d":"Benih bercambah (time-lapse)","why":"Visual terus untuk ayat hook 'pokok takkan terus berbuah'"},
 {"s":5.70,"e":7.05,"id":20468,"src":6,"x":0.36,"d":"Kertas jawapan peperiksaan","why":"'markah SPM'"},
 {"s":9.85,"e":12.00,"id":6101,"src":5,"x":0.56,"d":"Pelajar tertekan","why":"Tekanan nak skor straight A"},
 {"s":20.40,"e":22.70,"id":28319,"src":3,"x":0.62,"d":"Pelajar bertanya, dibantu rakan","why":"'banyak bertanya ke?'"},
 {"s":24.50,"e":26.17,"id":6264,"src":3,"x":0.40,"d":"Anak seronok belajar","why":"'lebih seronok nak belajar'"},
 {"s":29.19,"e":32.37,"id":48690,"src":2,"x":0.56,"d":"Ibu dan anak belajar online","why":"'markah datang berlari-lari' (hasil yang ibu bapa nak)"},
 {"s":32.37,"e":34.90,"id":33570,"src":4,"x":0.44,"d":"Siram anak pokok","why":"'kita perlukan masa' (sambung metafora pokok)"},
 {"s":36.89,"e":38.87,"id":46091,"src":1,"x":0.50,"d":"Anak pokok tumbuh rapat","why":"'mengukuhkan akar dia'"},
 {"s":END,"e":DUR,"id":48671,"src":1,"x":0.46,"d":"Ibu dan anak kelas online (latar end card)","why":"Latar CTA"},
]
G=[
 {"s":0.00,"e":3.60,"kind":"hook","text":["MARKAH ANAK","BELUM NAIK?"],"sub":"Ibu ayah, tengok ni dulu","note":"Tajuk hook: sakit utama ibu bapa, terus di saat pertama"},
 {"s":4.55,"e":7.05,"kind":"chip","text":"Fokus pada markah SPM","ic":"A+","note":"Kenal pasti fokus ibu bapa"},
 {"s":12.00,"e":13.90,"kind":"stamp","text":"STRAIGHT A","note":"Cop 'Straight A' (impian ibu bapa)"},
 {"s":15.10,"e":18.20,"kind":"swap","from":"MARKAH","to":"PROSES","note":"Pusing: dari markah ke proses (idea utama)"},
 {"s":18.27,"e":26.17,"kind":"checklist","items":[["Lebih yakin?",18.99],["Banyak bertanya?",21.69],["Lebih konsisten?",23.53],["Seronok belajar?",25.01]],"note":"Senarai semak ditanda satu-satu ikut suara"},
 {"s":26.60,"e":32.37,"kind":"steps","a":"Sikap berubah","b":"Markah naik","tb":29.20,"note":"Turutan: sikap dulu, baru markah"},
 {"s":33.44,"e":34.95,"kind":"masa","times":[33.44,33.94,34.60],"note":"'Masa' muncul 3 kali ikut sebutan"},
 {"s":35.30,"e":38.87,"kind":"roots","text":"Proses = akar","note":"Ilustrasi akar tumbuh di bawah anak pokok"},
 {"s":39.66,"e":42.58,"kind":"quote","a":"PROSES","b":"keputusan jangka pendek","note":"Kad petikan utama (boleh jadi thumbnail)"},
 {"s":42.58,"e":END,"kind":"comment","text":"Apa pandangan ibu ayah?","sub":"Komen di bawah","note":"Ajak komen (engagement, sesuai TOFU)"},
 {"s":END,"e":DUR,"kind":"endcard","note":"End card + CTA pendaftaran (maklumat dari asteredu11.com.my)",
  "brand":"Aster Edu","prog":"Math Turbo","lines":["Kelas LIVE di Zoom + rakaman 24/7","2 cikgu setiap kelas","Darjah 4 hingga Tingkatan 5"],
  "price":"RM99","per":"/bulan · 5 subjek","btn":"Daftar sekarang","url":"asteredu11.com.my","trust":"Dipercayai 50,000+ ibu bapa"},
]
SFX=[(0.00,"impact",0.75),(0.02,"whoosh",0.6),(1.15,"swoosh_down",0.45),(3.07,"whoosh",0.45),(4.58,"pop",0.55),(5.70,"whoosh",0.4),
 (9.85,"whoosh",0.4),(12.02,"impact",0.7),(15.12,"whoosh",0.55),(16.30,"bonk",0.45),(16.55,"ding",0.6),
 (18.99,"tick",0.6),(20.40,"whoosh",0.35),(21.69,"tick",0.6),(23.53,"tick",0.6),(24.50,"whoosh",0.35),(25.01,"tick",0.6),
 (26.62,"pop",0.5),(29.20,"riser",0.35),(29.25,"ding",0.5),(32.37,"whoosh",0.45),(33.44,"pop",0.5),(33.94,"pop",0.55),(34.60,"pop",0.6),
 (35.30,"swoosh_down",0.35),(36.89,"whoosh",0.35),(39.66,"impact",0.6),(42.60,"pop",0.55),(END,"whoosh",0.6),(END+1.2,"chaching",0.55),(END+2.6,"click",0.7)]
SFX=[{"t":round(t,2),"name":n,"gain":g} for t,n,g in SFX]
# zoom keyframes on the talking head (B-roll unaffected): (t, scale, originY%)
Z=[(0,1.10,42),(1.15,1.10,42),(3.07,1.0,42),(3.60,1.0,42),(3.83,1.0,42),(7.20,1.06,40),(9.85,1.06,40),(12.00,1.14,38),(13.9,1.14,38),(14.0,1.0,42),
   (14.75,1.0,42),(14.80,1.10,40),(18.2,1.10,40),(18.27,1.0,42),(26.17,1.0,42),(26.20,1.06,40),(29.19,1.06,40),(34.90,1.0,40),(36.89,1.0,40),
   (39.62,1.0,40),(39.66,1.16,38),(42.55,1.16,38),(42.58,1.04,40),(END,1.08,40)]
Z=[{"t":round(t,2),"scale":s,"oy":o} for t,s,o in Z]
json.dump({"duration":DUR,"speech_end":END,"parts":edl["parts"],"segments":edl["segments"],"captions":chunks,"broll":B,"graphics":G,"sfx":SFX,"zoom":Z,
  "music":{"file":"music.mp3","id":22,"note":"Piano tenang perlahan, Mixkit Stock Music Free License"}},open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
print(len(chunks),"caption chunks; duration",DUR)
