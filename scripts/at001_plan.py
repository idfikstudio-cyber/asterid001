# AT001: cut list + captions + motion/b-roll/sfx/zoom plan on the OUTPUT timeline.
# usage: python3 at001_plan.py at001/edit/transcript.json at001/edit/plan.json
import json,re,sys
# only 2 pauses long enough to remove (energy < -44 dB for >0.2s); the rest is already jump-cut tight
SEG=[("A",0.00,14.90),("B",15.04,23.68),("C",23.82,28.421)]
END_CARD=1.5
def off(i): return sum(e-s for _,s,e in SEG[:i])
def to_out(t):
    for i,(_,s,e) in enumerate(SEG):
        if t<e: return off(i)+max(0,t-s)
    return off(len(SEG))
DUR=round(off(len(SEG)),3)
t=json.load(open(sys.argv[1]))
FIX={"CP":"sifir","block":"blok","mic":"minda"}   # confirmed by 2nd whisper pass with context ("sifir", "blok mind")
W=[]
for s in t:
    for w in s["words"]:
        txt=w["w"].strip();txt=FIX.get(txt,txt)
        W.append({"w":txt,"s":round(to_out(w["s"]),3),"e":round(to_out(w["e"]),3)})
# word onsets that fall inside a removed pause snap to the real speech start
for w in W:
    if w["w"]=="Selalunya": w["s"]=round(to_out(15.08),3)
    if w["w"]=="untuk" and 23.3<w["s"]<23.7: w["s"]=round(to_out(23.88),3)
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.45:
        chunks.append({"s":cur[0]["s"],"e":(nxt["s"] if nxt and nxt["s"]-w["e"]<0.45 else w["e"]+0.12),
                       "words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"]} for x in cur]});cur=[]
EMPH={"sifir","pandai","jari","marah","takut","bencikan","blok","minda","susah","salah","teknik","betul","konsisten","kuasai","Follow","tips","4","5"}
for c in chunks:
    for x in c["words"]:
        if re.sub(r"\W","",x["w"]) in EMPH: x["hot"]=1
FIXED=sorted(set(FIX.values()))
# ---- graphics: kind decides the look in the preview page; "full" = full-screen b-roll
G=[
 {"s":0.00,"e":7.06,"kind":"hook","l1":"ANAK LEMAH","hl":"SIFIR?","l2":"BUKAN SEBAB DIA","l3":"TAK PANDAI","dock":2.08,
  "note":"Tajuk utama 7 saat: besar 0–2s, kemudian melekat di atas sampai 0:07"},
 {"s":3.98,"e":7.06,"kind":"fingers","text":"7 × 8 = ?","tag":"Tahun 4 & 5","count":[5.94,6.10,6.26,6.42,6.58],
  "note":"B-roll tulisan tangan '7 × 8 = ?' + jari mengira 1–5 ikut 'kira gunakan jari'"},
 {"s":7.18,"e":8.52,"kind":"angry","text":"KENAPA TAK BOLEH LAGI?!","note":"Belon marah bergegar (watak ibu bapa)"},
 {"s":8.55,"e":11.18,"kind":"full-exam","marks":[8.95,9.35,9.75],"score":10.45,"note":"B-roll penuh: kertas ujian, pen merah tulis ✗ ✗ ✗ dan bulatkan markah 32"},
 {"s":12.30,"e":14.86,"kind":"brain","text":"BLOK MINDA","stamp":"SUSAH!","stamp_at":14.38,"note":"Otak + mangga kunci jatuh, cop 'SUSAH!'"},
 {"s":14.94,"e":18.46,"kind":"insight","head":"MASALAH SEBENAR","text":"salah teknik belajar","write":16.30,"note":"Animasi menulis: punca sebenar (bukan anak tak pandai)"},
 {"s":18.54,"e":20.88,"kind":"checklist","items":[["Teknik betul",19.82],["Konsisten",20.30]],"note":"Senarai semak, tanda ✓ dilukis ikut sebutan"},
 {"s":20.90,"e":22.70,"kind":"full-solve","text":"7 × 8 = 56","sub":"Tanpa kira jari","note":"B-roll penuh: jawapan soalan hook ditulis laju + ✓ + bintang (callback hook)"},
 {"s":22.72,"e":24.64,"kind":"path","text":"KUASAI MATEMATIK","goal":23.72,"note":"Jalan berliku dilukis naik ke trofi"},
 {"s":24.68,"e":28.14,"kind":"follow","name":"Aster Edu","sub":"Tips bantu anak kuasai matematik","tap":25.10,"note":"Kad profil + butang Follow ditekan; anak panah ke butang Follow TikTok"},
 {"s":25.90,"e":28.14,"kind":"comment","text":"Anak kira guna jari juga?","ask":"Komen “YA” 👇","note":"Ajak komen (interaktif, naikkan engagement)"},
 {"s":DUR,"e":DUR+END_CARD,"kind":"endcard","text":"ASTER EDU","sub":"Tuisyen Online · Darjah 4 – Tingkatan 5","note":"Kad penutup jenama (1.5s, video dibekukan)"},
]
for g in G:
    for k in ("s","e","dock","score","stamp_at","write","goal","tap"):
        if k in g: g[k]=round(g[k],3)
SFX=[(0.00,"impact",.85),(0.60,"pop",.7),(0.78,"whoosh",.55),(2.08,"swoosh_down",.45),(4.00,"scribble",.55),
 (5.94,"pop",.45),(6.10,"pop",.45),(6.26,"pop",.45),(6.42,"pop",.45),(6.58,"pop",.5),
 (7.20,"bonk",.7),(8.55,"whoosh",.7),(8.95,"scribble",.45),(9.35,"scribble",.45),(9.75,"scribble",.45),(10.45,"bonk",.6),
 (11.15,"whoosh",.6),(12.40,"lock",.7),(14.38,"impact",.7),(14.94,"whoosh",.55),(16.30,"scribble",.6),(18.54,"pop",.5),
 (19.82,"check",.6),(20.30,"check",.65),(20.90,"whoosh",.6),(21.00,"scribble",.55),(21.95,"ding",.6),(22.70,"whoosh",.5),
 (22.80,"riser",.35),(23.72,"sparkle",.6),(24.68,"pop",.6),(25.10,"click",.8),(25.92,"pop",.5),
 (DUR,"whoosh",.7),(DUR+.25,"ding",.55)]
SFX=[{"t":round(t,3),"name":n,"gain":g} for t,n,g in SFX]
Z=[(0,1.08,40),(2.04,1.14,40),(2.08,1.0,42),(7.14,1.0,42),(7.18,1.10,36),(8.50,1.10,36),(8.55,1.0,42),(11.70,1.0,42),(11.76,1.06,38),
   (14.86,1.06,38),(14.94,1.0,42),(16.26,1.0,42),(16.32,1.14,37),(18.46,1.14,37),(18.54,1.0,42),(22.66,1.0,42),(22.72,1.06,40),
   (24.64,1.06,40),(24.68,1.0,42),(DUR,1.05,40)]
Z=[{"t":round(t,3),"scale":s,"oy":o} for t,s,o in Z]
json.dump({"duration":DUR,"total":round(DUR+END_CARD,3),"cuts":[{"id":n,"src_in":s,"src_out":e,"out":round(off(i),3)} for i,(n,s,e) in enumerate(SEG)],
  "captions":chunks,"fixed":FIXED,"no_caption":[[0,2.08]],"graphics":G,"sfx":SFX,"zoom":Z},open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print("dur",DUR,"chunks",len(chunks))
for c in chunks: print(f'{c["s"]:6.2f}-{c["e"]:6.2f}',' '.join(x["w"] for x in c["words"]))
