# Timeline for the CFik017 handover video. All times are seconds on the output timeline.
import json,sys
tr=json.load(open(sys.argv[1])); out=sys.argv[2]
DUR=49.5
# No voiceover (CFik016 is a different piece of content). The story is told with on-screen text.
TEXT=[(6.7,9.3,"Ini keadaan asal rumah klien"),(9.5,12.1,"Ruang lama, susun atur kurang efisien"),
      (12.6,15.4,"Semua bermula dengan rekaan 3D"),(15.6,18.9,"Klien nampak hasilnya sebelum kerja bermula")]
caps=[]
for s0,e0,txt in TEXT:
    ws=txt.split(); step=min(0.22,(e0-s0-0.6)/len(ws))
    caps.append({"s":s0,"e":e0,"words":[{"w":w,"s":round(s0+i*step,2),"e":round(e0,2)} for i,w in enumerate(ws)]})
VO=[]; FOUNDER=[]
CLIENT=[(39.7,1.0,5.4)]  # client walk-through clip
I=lambda n:"img/"+n+".jpg"
scenes=[
 {"id":"hook","t0":0,"t1":3.0,"type":"ba","chapter":"Hook","before":I("b_living"),"after":I("client"),"wipe":[0.9,1.9],"title":"Rumah lama → rumah impian"},
 {"id":"logo","t0":3.0,"t1":6.5,"type":"logo","chapter":"Fi-K Studio","tag":"Interior Design · 3D · Renovation"},
 {"id":"before","t0":6.5,"t1":12.3,"type":"photos","chapter":"Sebelum","stamp":"SEBELUM","imgs":[I("b_dining"),I("b_rest"),I("b_wetkitchen"),I("b_toilet2"),I("b_dining2")]},
 {"id":"pano","t0":12.3,"t1":19.1,"type":"pano","chapter":"Rekaan 3D","yaw":[-55,38],
  "chips":[{"t":14.0,"txt":"Layout"},{"t":14.6,"txt":"3D"},{"t":15.2,"txt":"Drawing"}]},
 {"id":"morph","t0":19.1,"t1":21.6,"type":"morph","chapter":"3D → Realiti","after":I("client")},
 {"id":"dining","t0":21.6,"t1":26.6,"type":"ba","chapter":"Ruang Makan","room":"Ruang Makan","before":I("b_dining"),"after":I("a_dining1"),"extra":[I("a_dining2"),I("a_dining3")],"wipe":[0.6,1.6],
  "callouts":[{"t":2.0,"x":62,"y":16,"txt":"Chandelier moden"},{"t":2.4,"x":20,"y":62,"txt":"Kerusi tufted 8 tempat"}]},
 {"id":"toilet","t0":26.6,"t1":30.6,"type":"ba","chapter":"Bilik Air","room":"Bilik Air","before":I("b_toilet"),"after":I("a_toilet"),"wipe":[0.5,1.4],
  "callouts":[{"t":1.8,"x":20,"y":22,"txt":"Shower kaca"},{"t":2.2,"x":58,"y":70,"txt":"Jubin corak klasik"}]},
 {"id":"kitchen","t0":30.6,"t1":34.6,"type":"ba","chapter":"Dapur Kering","room":"Dapur Kering","before":I("b_drykitchen"),"after":I("a_drykitchen"),"wipe":[0.5,1.4],
  "callouts":[{"t":1.8,"x":52,"y":56,"txt":"Island top marble"},{"t":2.2,"x":55,"y":24,"txt":"Kabinet built-in"}]},
 {"id":"family","t0":34.6,"t1":39.7,"type":"ba","chapter":"Ruang Keluarga","room":"Ruang Keluarga","before":I("b_rest"),"after":I("a_family1"),"extra":[I("a_family2")],"wipe":[0.5,1.4],
  "callouts":[{"t":1.8,"x":8,"y":30,"txt":"Feature wall kayu"},{"t":2.2,"x":50,"y":66,"txt":"Sofa & rug baharu"}]},
 {"id":"client","t0":39.7,"t1":45.1,"type":"client","chapter":"Reaksi klien","bg":I("a_family2"),"handover":I("client"),"handoverAt":3.7},
 {"id":"end","t0":45.1,"t1":DUR,"type":"end","chapter":"Penutup"},
]
S=lambda t,n,g=1.0:{"t":t,"n":n,"g":g}
sfx=[S(0.15,"whoosh",.7),S(0.9,"swipe"),S(1.95,"shimmer",.8),S(2.85,"riser",.5),S(3.0,"impact",.7),S(3.5,"ding",.5),
     S(6.5,"whoosh",.6),S(6.65,"thud"),*[S(6.7+i*1.16,"shutter",.7) for i in range(5)],
     S(12.3,"whoosh",.7),S(14.0,"pop"),S(14.6,"pop"),S(15.2,"pop"),S(19.1,"swipe",.7),S(19.6,"shimmer",.8)]
for sc in scenes:
    if sc["type"]=="ba" and sc["id"]!="hook":
        sfx+= [S(sc["t0"],"whoosh",.6),S(sc["t0"]+0.1,"thud",.7),S(sc["t0"]+sc["wipe"][0],"swipe"),S(sc["t0"]+sc["wipe"][1],"shimmer",.6)]
        sfx+= [S(sc["t0"]+c["t"],"pop",.8) for c in sc["callouts"]]
        if sc.get("extra"): sfx+=[S(sc["t0"]+3.0+i*0.9,"click",.5) for i in range(len(sc["extra"]))]
sfx+=[S(39.7,"whoosh",.6),S(40.1,"pop",.7),S(43.4,"ding",.6),S(45.1,"impact",.7),S(46.1,"shimmer",.6),S(46.9,"pop",.7)]
# 1 s thumbnail + hook frame in front of everything: shift the whole edit by TH
TH=1.0
for sc in scenes:
    sc["t0"]=round(sc["t0"]+TH,2); sc["t1"]=round(sc["t1"]+TH,2)
    for c in sc.get("chips",[]): c["t"]=round(c["t"]+TH,2)
for c in caps:
    c["s"]+=TH; c["e"]+=TH
    for w in c["words"]: w["s"]=round(w["s"]+TH,2); w["e"]=round(w["e"]+TH,2)
for x in sfx: x["t"]=round(x["t"]+TH,2)
CLIENT=[(t0+TH,a,d) for t0,a,d in CLIENT]
DUR=round(DUR+TH,2)
THUMBS=[
 {"id":"A","name":"Sebelum vs Selepas","top":I("b_dining2"),"bottom":I("a_dining2"),"hook":["Rumah lama","jadi macam ni?"]},
 {"id":"B","name":"Hasil dulu, lama kemudian","main":I("a_dining1"),"inset":I("b_dining"),"hook":["Ruang makan ni","dulu macam ni"]},
 {"id":"C","name":"3D vs Hasil sebenar","left":"img/pano_still.jpg","right":I("a_family1"),"hook":["Design 3D vs","hasil sebenar"],"sub":"Sama tak?"},
]
scenes.insert(0,{"id":"thumb","t0":0,"t1":TH,"type":"thumb","chapter":"Thumbnail"})
sfx=[S(0.0,"impact",.8),S(0.05,"shimmer",.5),S(0.82,"whoosh",.6)]+sfx
json.dump({"dur":DUR,"vo":VO,"founder":FOUNDER,"client":CLIENT,"captions":caps,"thumbs":THUMBS,"thumb":"B","scenes":scenes,"sfx":sorted(sfx,key=lambda x:x["t"])},open(out,"w"),ensure_ascii=False,indent=1)
print(len(caps),"captions;",len(sfx),"sfx")

