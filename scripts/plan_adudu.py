# usage: plan_adudu.py edit/adudu1|edit/adudu2   -> writes <dir>/plan.json (output timeline, seconds)
import json,re,sys,os
D=sys.argv[1];N=os.path.basename(D.rstrip("/"))
E=json.load(open(f"{D}/edl.json"))
# ---- captions: merge reduplication tokens, <=3 words, break on punctuation or gap
W=[]
for w in E["words"]:
    if w["w"].startswith("-") and W: W[-1]["w"]+=w["w"];W[-1]["e"]=w["e"];continue
    W.append(dict(w))
for w in W:
    if w["w"].startswith("Adu-du"): w["w"]="Adudu"+w["w"][6:]
    w["w"]=w["w"].replace("balon","belon")
# spoken digit runs ("6, 9, 6, 5") -> one token "6965" (needs >=3 single digits in a row, gap < 0.8s)
M=[]
i=0
while i<len(W):
    j=i
    while j<len(W) and re.fullmatch(r"\d[.,]?",W[j]["w"]) and (j==i or W[j]["s"]-W[j-1]["e"]<0.8): j+=1
    if j-i>=3:
        M.append(dict(W[i],w="".join(x["w"][0] for x in W[i:j])+re.sub(r"^\d","",W[j-1]["w"]),e=W[j-1]["e"],seg=W[j-1]["seg"]));i=j
    else: M.append(W[i]);i+=1
W=M
HOT={"tambah","tolak","operasi","Belon","Adudu","UASA","direct","jawab","tak","serang","jelas","dua","2","kotak","boleh","6965","6608","atas","ikat","terbang"}
chunks=[];cur=[]
for i,w in enumerate(W):
    cur.append(w);nxt=W[i+1] if i+1<len(W) else None
    if len(cur)>=3 or re.search(r"[.,?!]$",w["w"]) or not nxt or nxt["s"]-w["e"]>0.45 or nxt["seg"]!=w["seg"]:
        end=nxt["s"] if nxt and nxt["s"]-w["e"]<0.45 else w["e"]+0.2
        chunks.append({"s":cur[0]["s"],"e":round(end,3),"words":[{"w":re.sub(r"[.,]$","",x["w"]),"s":x["s"]} for x in cur]});cur=[]
for c in chunks:
    for x in c["words"]:
        if re.sub(r"[^\w]","",x["w"]) in HOT or re.fullmatch(r"\d{3,}",x["w"]): x["hot"]=1
EMOJI={}
if N=="adudu1":
    G=[
     {"s":0.00,"e":7.00,"kind":"hook","lines":["ANAK TAHU","TAMBAH & TOLAK…","TAPI TAK BOLEH JAWAB?"],"at":[0.0,0.35,0.96],"badge":"Teknik Belon Adudu","badge_at":3.18,"note":"Hook 7 saat: tajuk utama untuk ibu ayah. Ayat 'Mostly anak kita tak boleh jawab' dipindah dari 0:34 ke depan"},
     {"s":4.13,"e":34.24,"kind":"board","note":"B-roll papan putih: soalan UASA + 3 belon dilukis (animasi menulis)"},
     {"s":11.44,"e":13.90,"kind":"chip","icon":"?","tone":"red","text":"Operasi apa nak pakai?","note":"Masalah sebenar anak"},
     {"s":16.66,"e":17.95,"kind":"chip","icon":"✕","tone":"red","text":"Bukan problem solving","note":"Senarai cepat"},
     {"s":18.00,"e":19.85,"kind":"chip","icon":"✕","tone":"red","text":"Bukan soalan ayat panjang"},
     {"s":19.90,"e":20.80,"kind":"chip","icon":"✓","tone":"green","text":"Soalan terus (direct)"},
     {"s":21.89,"e":24.95,"kind":"chip","icon":"📘","tone":"navy","text":"Darjah 4 · 5 · 6"},
     {"s":24.99,"e":28.20,"kind":"chip","icon":"📝","tone":"gold","text":"UASA · Bahagian A · S1–7","note":"Konteks peperiksaan: ibu ayah kenal 'UASA'"},
     {"s":29.61,"e":31.85,"kind":"chip","icon":"✓","tone":"green","text":"Tahu tambah, tahu tolak"},
     {"s":31.90,"e":34.24,"kind":"chip","icon":"?","tone":"red","text":"Tapi operasi apa?!","note":"Klimaks masalah: punch-in"},
     {"s":34.24,"e":38.44,"kind":"end1","note":"Kad penutup: soalan kuiz A/B untuk komen + 'Jawapan di Part 2'"},
    ]
    B=[{"t":4.13,"a":"q"},{"t":4.40,"a":"b"},{"t":6.80,"e":11.40,"a":"ops"},{"t":9.42,"e":11.40,"a":"opA"},{"t":10.60,"e":11.40,"a":"opB"},
       {"t":11.44,"e":14.20,"a":"qq"},{"t":14.28,"e":16.60,"a":"qglow"},{"t":28.27,"e":29.55,"a":"qglow"},{"t":31.90,"a":"qq"},{"t":31.90,"a":"ops"}]
    SFX=[(0.00,"impact",0.85),(0.05,"whoosh",0.6),(0.35,"pop",0.5),(0.96,"pop",0.6),(3.18,"ding",0.55),(4.13,"whoosh",0.5),(4.45,"scribble",0.55),
         (6.80,"pop",0.45),(9.42,"boop",0.6),(10.60,"boop",0.6),(11.44,"bonk",0.7),(14.28,"tick",0.5),(16.66,"bonk",0.5),(18.00,"bonk",0.5),(19.90,"correct",0.6),
         (21.89,"pop",0.45),(24.99,"ding",0.5),(28.27,"whoosh",0.5),(29.61,"boop",0.5),(31.90,"impact",0.7),(34.24,"riser",0.4),(35.30,"pop",0.6),(35.55,"pop",0.6),(36.10,"ding",0.5)]
    Z=[(0,1.16,30),(1.70,1.0,30),(8.04,1.0,30),(8.08,1.08,28),(11.40,1.08,28),(11.44,1.14,26),(13.90,1.14,26),(13.95,1.0,30),(28.20,1.0,30),(28.27,1.08,28),(29.55,1.08,28),(29.61,1.0,30),
       (31.85,1.0,30),(31.90,1.16,26),(34.20,1.16,26),(34.24,1.0,30),(38.44,1.06,30)]
else:
    G=[
     {"s":0.00,"e":7.00,"kind":"hook","lines":["ANAK KELIRU","TAMBAH","ATAU TOLAK?"],"at":[0.0,0.3,0.6],"badge":"Teknik Belon Adudu · 3 langkah","badge_at":1.78,"note":"Hook 7 saat: tajuk utama untuk ibu ayah"},
     {"s":0.00,"e":104.10,"kind":"board","note":"B-roll papan putih mengikut setiap langkah (animasi menulis)"},
     {"s":0.00,"e":3.10,"kind":"step","n":1,"text":"Lukis 3 belon, ikat","hidden_during_hook":True},
     {"s":5.57,"e":11.20,"kind":"step","n":2,"text":"Tulis − , − , +","note":"Label langkah"},
     {"s":13.65,"e":21.30,"kind":"step","n":3,"text":"Isi nombor dari soalan"},
     {"s":31.30,"e":32.60,"kind":"chip","icon":"2","tone":"gold","text":"Ada 2 tolak!"},
     {"s":41.61,"e":46.10,"kind":"chip","icon":"🙋","tone":"navy","text":"Soalan murid: letak kanan boleh?"},
     {"s":46.14,"e":49.10,"kind":"chip","icon":"✓","tone":"green","text":"Boleh! Dua-dua sisi tolak"},
     {"s":56.85,"e":61.20,"kind":"chip","icon":"?","tone":"red","text":"Tinggal satu belon kosong"},
     {"s":67.83,"e":81.25,"kind":"step","n":4,"text":"Serang belon Adudu!","note":"Momen seronok: zap + belon pecah"},
     {"s":81.32,"e":101.11,"kind":"step","n":5,"text":"Baca operasi yang tinggal"},
     {"s":99.35,"e":101.11,"kind":"stamp","text":"OPERASI: TOLAK","note":"Kesimpulan"},
     {"s":101.11,"e":104.10,"kind":"answer","note":"Tambahan: jawapan 357 + semak guna sisi '+' (cikgu tak sebut jawapan dalam video)"},
     {"s":104.10,"e":108.71,"kind":"cta","note":"CTA lembut ikut landing page: Sesi 2027, kelas live, 5 subjek RM99"},
    ]
    B=[{"t":0.00,"a":"q"},{"t":1.30,"a":"b"},{"t":2.84,"a":"tie"},{"t":3.92,"e":5.18,"a":"fly"},
       {"t":7.05,"a":"m1"},{"t":8.45,"a":"m2"},{"t":10.29,"a":"pl"},
       {"t":13.65,"e":15.40,"a":"qglow"},{"t":15.51,"e":17.30,"a":"hiA"},{"t":19.85,"a":"n1"},
       {"t":22.96,"e":25.50,"a":"hiA"},{"t":24.60,"e":25.50,"a":"hiB"},{"t":27.78,"e":31.80,"a":"gL"},{"t":28.62,"e":31.80,"a":"gR"},
       {"t":32.70,"e":37.60,"a":"where"},{"t":39.05,"a":"boxL"},{"t":43.52,"e":49.10,"a":"ghostR"},{"t":47.74,"e":49.10,"a":"gR"},
       {"t":53.79,"a":"c1"},{"t":54.90,"a":"c2"},{"t":56.11,"a":"c3"},{"t":56.85,"e":62.90,"a":"askR"},{"t":62.95,"a":"n2"},{"t":66.05,"a":"c4"},
       {"t":66.31,"a":"face"},{"t":71.09,"e":71.60,"a":"zap"},{"t":76.11,"e":76.60,"a":"zap"},{"t":76.87,"e":77.20,"a":"zap"},{"t":77.29,"e":77.60,"a":"zap"},{"t":77.73,"e":78.20,"a":"zap"},
       {"t":78.71,"e":79.30,"a":"zap"},{"t":80.36,"a":"popL"},{"t":84.09,"e":87.30,"a":"askTR"},{"t":87.33,"a":"gTR"},
       {"t":90.39,"a":"col"},{"t":91.33,"a":"k1"},{"t":93.53,"a":"k2"},{"t":96.20,"a":"kl"},{"t":101.11,"a":"k3"},{"t":101.60,"a":"fillq"},{"t":102.50,"a":"verify"}]
    SFX=[(0.00,"impact",0.85),(0.05,"whoosh",0.55),(0.30,"pop",0.5),(0.60,"pop",0.55),(1.30,"scribble",0.5),(1.78,"ding",0.45),(2.84,"scribble",0.4),(3.92,"riser",0.25),(5.18,"pop",0.6),
         (5.57,"whoosh",0.4),(7.05,"pop",0.55),(8.45,"pop",0.55),(10.29,"pop",0.6),(13.65,"whoosh",0.4),(15.51,"tick",0.45),(19.85,"scribble",0.5),(21.10,"ding",0.4),
         (24.60,"pop",0.4),(27.78,"boop",0.5),(28.62,"boop",0.5),(31.30,"pop",0.55),(32.70,"bonk",0.45),(37.60,"whoosh",0.35),(39.05,"pop",0.55),
         (41.61,"click",0.6),(43.52,"whoosh",0.35),(46.14,"correct",0.6),(49.15,"whoosh",0.35),(53.79,"boop",0.6),(54.90,"boop",0.6),(56.11,"boop",0.6),(56.85,"bonk",0.45),
         (62.95,"scribble",0.5),(66.05,"correct",0.55),(66.31,"pop",0.5),(67.83,"whoosh",0.4),(71.09,"zap",0.55),(76.11,"zap",0.55),(76.87,"zap",0.5),(77.29,"zap",0.5),(77.73,"zap",0.55),
         (78.71,"zap",0.55),(80.36,"balloonpop",0.85),(80.40,"impact",0.5),(81.32,"whoosh",0.35),(84.09,"riser",0.35),(87.33,"impact",0.7),(87.40,"correct",0.5),
         (90.39,"whoosh",0.45),(91.33,"scribble",0.45),(93.53,"scribble",0.45),(96.20,"tick",0.4),(99.35,"impact",0.75),(101.11,"scribble",0.5),(101.40,"ding",0.6),
         (101.60,"pop",0.5),(102.50,"correct",0.6),(104.10,"whoosh",0.6),(104.60,"chaching",0.55),(106.30,"click",0.6)]
    Z=[(0,1.14,30),(1.30,1.0,30),(41.55,1.0,30),(41.61,1.08,28),(46.10,1.08,28),(46.14,1.0,30),(71.05,1.0,30),(71.09,1.10,28),(72.70,1.10,28),(72.75,1.0,30),
       (76.05,1.0,30),(76.11,1.06,28),(77.70,1.06,28),(77.73,1.14,26),(79.40,1.14,26),(79.52,1.0,30),(84.05,1.0,30),(84.09,1.08,28),(87.30,1.08,28),(87.33,1.16,26),(88.80,1.16,26),
       (88.90,1.0,30),(99.30,1.0,30),(99.35,1.12,28),(101.05,1.12,28),(101.11,1.0,30),(108.71,1.06,30)]
SFX=[{"t":t,"name":n,"gain":g} for t,n,g in SFX]
Z=[{"t":t,"scale":s,"oy":o} for t,s,o in Z]
json.dump({"id":N,"duration":E["duration"],"speech_end":E["speech_end"],"cuts":[{"out":s["out_in"],"src_in":s["src_in"],"src_out":s["src_out"],"id":s["id"]} for s in E["segments"]],
           "captions":chunks,"graphics":G,"board":B,"sfx":SFX,"zoom":Z},open(f"{D}/plan.json","w"),ensure_ascii=False,indent=1)
print(N,len(chunks),"captions",len(G),"graphics",len(B),"board acts",len(SFX),"sfx")
