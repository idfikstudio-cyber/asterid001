# Timeline for the CFik017 handover video. All times are seconds on the output timeline.
import json,sys
tr=json.load(open(sys.argv[1])); out=sys.argv[2]
DUR=66.0
# VO takes picked from CFik016.MOV (retakes removed): (timeline_start, src_in, src_out)
VO=[(3.0,0.00,4.98),(8.3,22.28,27.85),(14.2,37.28,41.50),(18.9,45.50,48.78),
    (22.6,110.00,113.26),(25.9,114.94,116.80),(55.2,160.36,166.62),(61.7,176.28,177.20)]
FIX={"fikir":"Fi-K","studio":"Studio","studio,":"Studio,","apatkan":"dapatkan","consert":"consult","contractor":"kontraktor","contractor.":"kontraktor.","3d":"3D","3d,":"3D,"}
words=[]
for t0,a,b in VO:
    for s in tr:
        for w in s["words"]:
            if w["s"]>=a-0.05 and w["e"]<=b+0.05:
                txt=w["w"].strip(); txt=FIX.get(txt.lower(),txt)
                words.append({"w":txt,"s":round(t0+w["s"]-a,2),"e":round(t0+w["e"]-a,2)})
# group into caption chunks (<=4 words, break on punctuation or gaps)
caps=[];cur=[]
for w in words:
    if cur and (len(cur)>=4 or w["s"]-cur[-1]["e"]>0.35 or cur[-1]["w"][-1] in ".,"):
        caps.append(cur);cur=[]
    cur.append(w)
if cur: caps.append(cur)
caps=[{"s":c[0]["s"],"e":max(c[-1]["e"],c[0]["s"]+0.6),"words":c} for c in caps]
# founder on camera: (timeline_start, src_in, dur)
FOUNDER=[(3.0,0.0,5.2),(14.0,37.08,4.6),(55.0,160.16,6.6)]
CLIENT=[(49.6,1.0,5.6)]  # client walk-through clip
I=lambda n:"img/"+n+".jpg"
scenes=[
 {"id":"hook","t0":0,"t1":3.0,"type":"ba","chapter":"Hook","before":I("b_living"),"after":I("client"),"wipe":[0.9,1.9],"title":"Rumah lama → rumah impian","caps":False},
 {"id":"f1","t0":3.0,"t1":8.2,"type":"founder","chapter":"Pengenalan","lower":["Fi-K Studio","Interior Design · 3D · Renovation"]},
 {"id":"before","t0":8.2,"t1":14.0,"type":"photos","chapter":"Sebelum","stamp":"SEBELUM","imgs":[I("b_dining"),I("b_rest"),I("b_wetkitchen"),I("b_toilet2"),I("b_dining2")]},
 {"id":"f2","t0":14.0,"t1":18.6,"type":"founder","chapter":"Masalah klien"},
 {"id":"logo","t0":18.6,"t1":22.2,"type":"logo","chapter":"Fi-K Studio","tag":"Inilah fungsi kami"},
 {"id":"pano","t0":22.2,"t1":29.0,"type":"pano","chapter":"Rekaan 3D","yaw":[-55,38],
  "chips":[{"t":24.26,"txt":"Layout"},{"t":24.9,"txt":"3D"},{"t":25.44,"txt":"Drawing"}]},
 {"id":"morph","t0":29.0,"t1":31.5,"type":"morph","chapter":"3D → Realiti","after":I("client")},
 {"id":"dining","t0":31.5,"t1":36.5,"type":"ba","chapter":"Ruang Makan","room":"Ruang Makan","before":I("b_dining"),"after":I("a_dining1"),"extra":[I("a_dining2"),I("a_dining3")],"wipe":[0.6,1.6],
  "callouts":[{"t":2.0,"x":62,"y":16,"txt":"Chandelier moden"},{"t":2.4,"x":20,"y":62,"txt":"Kerusi tufted 8 tempat"}]},
 {"id":"toilet","t0":36.5,"t1":40.5,"type":"ba","chapter":"Bilik Air","room":"Bilik Air","before":I("b_toilet"),"after":I("a_toilet"),"wipe":[0.5,1.4],
  "callouts":[{"t":1.8,"x":20,"y":22,"txt":"Shower kaca"},{"t":2.2,"x":58,"y":70,"txt":"Jubin corak klasik"}]},
 {"id":"kitchen","t0":40.5,"t1":44.5,"type":"ba","chapter":"Dapur Kering","room":"Dapur Kering","before":I("b_drykitchen"),"after":I("a_drykitchen"),"wipe":[0.5,1.4],
  "callouts":[{"t":1.8,"x":52,"y":56,"txt":"Island top marble"},{"t":2.2,"x":55,"y":24,"txt":"Kabinet built-in"}]},
 {"id":"family","t0":44.5,"t1":49.6,"type":"ba","chapter":"Ruang Keluarga","room":"Ruang Keluarga","before":I("b_rest"),"after":I("a_family1"),"extra":[I("a_family2")],"wipe":[0.5,1.4],
  "callouts":[{"t":1.8,"x":8,"y":30,"txt":"Feature wall kayu"},{"t":2.2,"x":50,"y":66,"txt":"Sofa & rug baharu"}]},
 {"id":"client","t0":49.6,"t1":55.0,"type":"client","chapter":"Reaksi klien","bg":I("a_family2"),"handover":I("client"),"handoverAt":3.7},
 {"id":"f3","t0":55.0,"t1":61.6,"type":"founder","chapter":"DM kami","lower":["DM kami","Konsultasi design rumah anda"]},
 {"id":"end","t0":61.6,"t1":DUR,"type":"end","chapter":"Penutup"},
]
S=lambda t,n,g=1.0:{"t":t,"n":n,"g":g}
sfx=[S(0.15,"whoosh",.7),S(0.9,"swipe"),S(1.95,"shimmer",.8),S(2.85,"impact",.8),S(3.25,"thud",.7),
     S(8.2,"whoosh",.6),S(8.35,"thud"),*[S(8.4+i*1.16,"shutter",.7) for i in range(5)],
     S(13.9,"swipe",.7),S(18.15,"riser",.6),S(18.6,"impact",.7),S(19.0,"ding",.5),
     S(22.2,"whoosh",.7),S(24.26,"pop"),S(24.9,"pop"),S(25.44,"pop"),S(29.0,"shimmer",.8)]
for sc in scenes:
    if sc["type"]=="ba" and sc["id"]!="hook":
        sfx+= [S(sc["t0"],"whoosh",.6),S(sc["t0"]+0.1,"thud",.7),S(sc["t0"]+sc["wipe"][0],"swipe"),S(sc["t0"]+sc["wipe"][1],"shimmer",.6)]
        sfx+= [S(sc["t0"]+c["t"],"pop",.8) for c in sc["callouts"]]
        if sc.get("extra"): sfx+=[S(sc["t0"]+3.0+i*0.9,"click",.5) for i in range(len(sc["extra"]))]
sfx+=[S(49.6,"whoosh",.6),S(50.0,"pop",.7),S(53.3,"ding",.6),S(55.0,"swipe",.6),S(55.3,"thud",.7),S(61.6,"impact",.8),S(62.6,"shimmer",.6),S(63.4,"pop",.7)]
json.dump({"dur":DUR,"vo":VO,"founder":FOUNDER,"client":CLIENT,"captions":caps,"scenes":scenes,"sfx":sorted(sfx,key=lambda x:x["t"])},open(out,"w"),ensure_ascii=False,indent=1)
print(len(caps),"captions;",len(sfx),"sfx")
for c in caps: print(f'{c["s"]:5.2f} '+" ".join(w["w"] for w in c["words"]))
