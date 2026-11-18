"""Jana overlay.html AS-F-015 (gaya HYBRID hitam+kuning; CSS/JS asas dari AS-F-012)."""
import re,json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import timeline as T
HERE=os.path.dirname(os.path.abspath(__file__));OUTD=sys.argv[1]
a12=open(f"{HERE}/../AS-F-012_Darjah6_ke_T1/overlay.html").read()
css=re.search(r"<style>(.*?)</style>",a12,re.S).group(1)
js=re.search(r"<script>(.*?)</script>",a12,re.S).group(1)
end=re.search(r'(<div id="end".*?)\n<div id="cap"',a12,re.S).group(1).replace('data-in="23.08"',f'data-in="{T.DUR-T.END:.2f}"')
o=lambda s:round(T.s2o(s),2)
# ---- caption dari transkrip (ikut sebutan) ----
tr=json.load(open(f"{HERE}/tr.json"))
W=[[w["w"].strip(),w["s"],w["e"]] for s in tr for w in s["words"]]
W=[w for w in W if not (21.0<=w[1]<21.85)]                 # "Prosesnya adalah," dibuang (EDL)
for w in W:
    if w[0]=="prosesnya" and 21.8<w[1]<22.1: w[0]="Prosesnya";w[1]=22.05
W=[w for w in W if w[0]!="mah"]
# 58.68-60.48: semakan kedua -> "Tapi tak semua anak mampu hafal."
W=[w for w in W if not (58.6<w[1]<60.5)]+[["Tapi",58.68,58.88],["tak",58.88,59.14],["semua",59.14,59.36],["anak",59.36,59.70],["mampu",59.70,60.2],["hafal.",60.2,60.48]]
W=[w for w in W if not (w[0]=="jadi" and 72<w[1]<72.5)]
# v2: "lima" kedua diganti "enam" (audio ditampal, diluluskan Farhan) + masa sebenar
for w in W:
    if w[0]=="5," and 45.5<w[1]<45.6: w[0],w[1],w[2]="6,",45.70,46.12
    elif w[0]=="12," and 45.9<w[1]<46.1: w[1],w[2]="46.17",46.55
W=[[a,float(b),c] for a,b,c in W]
FIX={"M":"DM","tuition":"tuisyen","trik":"trick","ibu":"ibu","-ibu":"-ibu"}
W.sort(key=lambda w:w[1])
# gabung "-anak" / "-ibu" / "-soalan" / "-jadual" ke perkataan sebelum
M=[]
for w in W:
    if w[0].startswith("-") and M: M[-1][0]+=w[0];M[-1][2]=w[2]
    else: M.append(list(w))
HL=set("12 6 1 2 3 4 5 7 8 9 10 15 20 25 30 35 40 45 50 18 24 36 42 48 54 60 sifir trick ibu-ibu tambah gandaan faham hafal DM teras selesai mampu jadual-jadual".split())
caps=[];cur=[]
def flush():
    global cur
    if cur: caps.append([cur[0][1],cur[-1][2],cur]);cur=[]
for w in M:
    t=FIX.get(re.sub(r"[.,?]","",w[0]),None)
    txt=w[0] if t is None else t+re.sub(r"[^.,?]","",w[0])
    glue=cur and re.sub(r"[.,?]","",cur[-1][0]).lower() in ("sifir","nombor","tengah","pukul")
    if cur and not glue and (len(cur)>=3 or w[1]-cur[-1][2]>0.25): flush()
    if cur and glue and len(cur)>=4: flush()
    cur.append([txt,w[1],w[2]])
    if re.search(r"[.,?]$",txt): flush()
flush()
CAPS=[]
for i,(s,e,ws) in enumerate(caps):
    nxt=caps[i+1][0] if i+1<len(caps) else e+0.4
    e2=min(max(e+0.15,s+0.35),nxt)
    words=[("*" if re.sub(r"[.,?]","",x[0]).lower() in {h.lower() for h in HL} else "")+re.sub(r"[.,]$","",x[0]) for x in ws]
    if words==["*Tingkatan"]: pass
    CAPS.append([o(s),o(e2),re.sub(r"(\*?sifir) (\*?6)",r"*sifir *6"," ".join(words))])
# ---- elemen grafik ----
TB=o(T.TEACH[0]);TE=o(T.TEACH[1]+T.TR)
def rowhl(words,col,x0,x1):
    h=""
    for r,(s,e) in enumerate(words):
        y=T.row_y(r)-34
        h+=f'<div class="el rowhl" data-in="{o(s-0.05)}" data-out="{o(e+0.35)}" data-a="fade" data-fo="0.2" style="left:{x0}px;top:{y:.0f}px;width:{x1-x0}px"></div>\n'
    return h
bx=lambda X:round(T.BPOS[0]+(X-T.BCROP[0])*T.BSCALE)
body=f"""
<div id="thumb" class="el" data-in="0" data-out="1.0" data-a="none">
  <div class="hw" style="position:absolute;left:0;width:920px;top:300px;text-align:center"><span style="color:#f2b33d">6 × 7</span> = <span style="color:#3d7bff">7 + 35</span> = <span style="color:#ffd21f">42</span></div>
  <div class="hook" style="top:1130px;left:60px;width:800px"><div class="h1">TRICK SIFIR 6</div><div class="h2" style="font-size:62px">UNTUK IBU AJAR ANAK</div></div>
</div>
<div id="name" class="el" data-in="1.3" data-out="4.3" data-a="slide" style="top:1135px"><div class="ring"><img src="face.png"></div><div class="txt">Cikgu AlFarhan</div></div>
<div class="el paper" data-in="{o(0.3)}" data-out="{o(3.4)}" data-a="pop" style="left:290px;top:292px;width:500px;display:flex;align-items:center;gap:20px">
  <svg viewBox="0 0 24 24" width="84" height="84"><path fill="#1d2b5a" d="M21 14.5A9 9 0 0 1 9.5 3a9 9 0 1 0 11.5 11.5z"/></svg>
  <div><small>Dah nak dekat</small><div style="font:900 56px/1.05 Poppins">12 tengah malam</div></div></div>
<div class="el" data-in="{o(5.5)}" data-out="{o(11.5)}" data-a="pop" style="left:0;width:1000px;top:272px;text-align:center"><div class="title"><small>Trick kuasai</small>SIFIR 6</div></div>
<div class="el" data-in="{o(7.92)}" data-out="{o(9.45)}" data-a="pop" style="left:0;width:1080px;top:1130px;text-align:center"><span class="pill">untuk <b>ibu-ibu</b> ajar anak</span></div>
<div class="el" data-in="{o(9.5)}" data-out="{o(11.55)}" data-a="pop" style="left:0;width:1080px;top:1130px;text-align:center"><span class="pill y">Cuba dengan anak ✓</span></div>
<div id="bframe" class="el" data-in="{o(T.TEACH[0]+0.2)}" data-out="{o(T.TEACH[1]+0.3)}" data-a="fade" data-fo="0.3"></div>
<div class="el step" data-in="{o(11.9)}" data-out="{o(22.0)}" data-a="slide"><span class="sl">SIFIR 6 · CIKGU ALFARHAN</span></div>
<div class="el step" data-in="{o(22.05)}" data-out="{o(29.95)}" data-a="slide"><b>LANGKAH 1</b>Tulis nombor 1 → 10</div>
<div class="el step" data-in="{o(30.0)}" data-out="{o(42.45)}" data-a="slide"><b>LANGKAH 2</b>Gandaan 5: 5 → 50</div>
<div class="el step" data-in="{o(42.52)}" data-out="{o(54.05)}" data-a="slide"><b>LANGKAH 3</b>Tambah = jawapan!</div>
{rowhl(T.NW,0,bx(400),bx(560))}{rowhl(T.KW,1,bx(560),bx(720))}{rowhl(T.RW,2,bx(80),bx(930))}
<div class="el" data-in="{o(54.1)}" data-out="{o(55.2)}" data-a="pop" style="left:0;width:1080px;top:640px;text-align:center"><span class="stamp">SIFIR 6 SELESAI ✓</span></div>
<div id="follow" class="el" data-in="{o(30.0)}" data-out="{o(34.0)}" data-a="pop" style="left:700px;top:1300px;width:210px;padding:12px"><b style="font-size:24px">Cikgu AlFarhan</b><span style="font-size:19px">@aster.edu_tpg</span><div class="btn" style="font-size:26px">Follow saya</div></div>
<div class="el paper" data-in="{o(55.04)}" data-out="{o(56.2)}" data-a="pop" style="left:0;right:0;margin:auto;top:296px;width:640px;text-align:center"><div style="font:900 60px/1.05 Poppins">Kenapa buat <span style="background:var(--yel);padding:0 10px;border-radius:10px">trick</span> ni? 🤔</div></div>
<div class="el" data-in="{o(56.26)}" data-out="{o(58.64)}" data-a="pop" style="left:0;width:1080px;top:290px;text-align:center"><span class="pill y" style="font-size:52px">Kena <b>FAHAM</b> ✓</span></div>
<div class="el" data-in="{o(58.68)}" data-out="{o(60.55)}" data-a="pop" style="left:0;width:1080px;top:276px;text-align:center"><div class="strike"><small>Tak semua anak mampu</small>HAFAL<span class="ln el" data-in="{o(60.25)}" data-out="{o(60.55)}" data-a="wipe" style="width:110%"></span></div></div>
<div class="el paper" data-in="{o(60.58)}" data-out="{o(68.05)}" data-a="pop" style="left:0;right:0;margin:auto;top:292px;width:700px;text-align:center"><small>Trick lain supaya anak</small><div style="font:900 52px/1.1 Poppins">masih <span style="color:#1f9d4c">MAMPU</span> jawab<br>soalan sifir ✓</div></div>
<div class="el" data-in="{o(68.1)}" data-out="{o(76.1)}" data-a="drop" style="left:0;width:1080px;top:268px;text-align:center"><span class="pill" style="background:#e0322b;border-color:#fff">Pendaftaran 2027 dibuka</span></div>
<div id="lt" class="el" data-in="{o(68.1)}" data-out="{o(70.9)}" data-a="slide" style="top:1120px"><div class="a">MATH TURBO 2027</div><div class="b">Tuisyen online bersama Cikgu AlFarhan</div></div>
<div class="el" data-in="{o(71.0)}" data-out="{o(72.3)}" data-a="pop" style="left:0;width:1080px;top:1130px;text-align:center"><span class="pill y">Subjek <b>teras</b></span></div>
<div class="el" data-in="{o(72.3)}" data-out="{o(72.95)}" data-a="pop" style="left:0;width:1080px;top:1130px;text-align:center"><span class="pill"><span class="ic"><svg viewBox="0 0 24 24" fill="#111"><path d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2z"/></svg></span>DM saya</span></div>
<div class="el" data-in="{o(72.95)}" data-out="{o(76.16)}" data-a="pop" style="left:0;width:1080px;top:1130px;text-align:center"><span class="pill"><span class="ic"><svg viewBox="0 0 24 24" fill="#111"><path d="M7 2v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2zm-2 8h14v10H5z"/></svg></span>Jadual kelas</span></div>
"""
css+=f"""
#wm{{top:232px}}
.hw{{font:700 92px/1 Caveat;color:#fff;letter-spacing:2px;text-shadow:0 4px 12px rgba(0,0,0,.6)}}
.title{{display:inline-block;font:900 128px/0.95 Poppins;color:var(--yel);-webkit-text-stroke:14px #111;paint-order:stroke fill;letter-spacing:-3px;text-shadow:0 10px 24px rgba(0,0,0,.6)}}
.title small{{display:block;font:900 44px Poppins;color:#fff;-webkit-text-stroke:8px #111;letter-spacing:1px;margin-bottom:6px}}
#bframe{{left:{T.BPOS[0]-14}px;top:{T.BPOS[1]-14}px;width:{round(840*T.BSCALE)+28-12}px;height:{round(1030*T.BSCALE)+28-12}px;border:6px solid var(--yel);border-radius:22px;box-shadow:0 0 0 3px rgba(0,0,0,.6)}}
.step{{left:{T.BPOS[0]-14}px;top:282px;display:flex;align-items:center;gap:14px;font:800 32px Poppins;color:#fff;white-space:nowrap}}
.step b{{background:var(--yel);color:#111;font:900 30px Poppins;padding:6px 16px;border-radius:10px;letter-spacing:1px}}
.step .sl{{font:900 30px Poppins;color:var(--yel);letter-spacing:2px}}
.rowhl{{height:68px;border-radius:14px;background:rgba(255,210,31,.16);border:4px solid var(--yel);box-sizing:border-box}}
.stamp{{display:inline-block;font:900 78px Poppins;color:#111;background:var(--yel);padding:10px 34px;border-radius:20px;border:6px solid #111;transform:rotate(-4deg);box-shadow:0 14px 34px rgba(0,0,0,.6)}}
"""
js=re.sub(r"const CAPS=.*?;\n","const CAPS="+json.dumps(CAPS,ensure_ascii=False)+";\n",js,count=1,flags=re.S)
js=re.sub(r"\{const q=document.getElementById\('eq'\).*?\}\}\n","",js,flags=re.S)
js=js.replace("cap.style.top=(t>=14.04&&t<16.3)?'1240px':'1290px';",f"cap.style.top=(t>={TB+0.3:.2f}&&t<{TE-0.2:.2f})?'1228px':'1290px';")
js=js.replace("document.querySelectorAll('.brimg').forEach(e=>{const a=+e.closest('.el').dataset.in;e.style.transform=`scale(${1+0.04*Math.max(0,t-a)})`});","")
assert "__" not in js
html=f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="fonts_local.css"><style>{css}</style></head>
<body><div id="stage">{body}
{end}
<div id="cap" class="el"></div>
<div id="wm" class="el">asteredu11.com.my</div>
</div><script>{js}</script></body></html>"""
open(f"{OUTD}/overlay.html","w").write(html)
json.dump(CAPS,open(f"{HERE}/caps.json","w"),ensure_ascii=False)
print(len(CAPS),"caption");[print(c) for c in CAPS]
