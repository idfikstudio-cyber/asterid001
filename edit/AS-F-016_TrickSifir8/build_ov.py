"""Jana overlay.html AS-F-016 (HYBRID hitam+kuning; CSS/JS asas AS-F-012). python3 build_ov.py <out_dir>"""
import re,json,os,sys
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import timeline as T
OUTD=sys.argv[1]
a12=open(f"{HERE}/../AS-F-012_Darjah6_ke_T1/overlay.html").read()
css=re.search(r"<style>(.*?)</style>",a12,re.S).group(1)
js=re.search(r"<script>(.*?)</script>",a12,re.S).group(1)
end=re.search(r'(<div id="end".*?)\n<div id="cap"',a12,re.S).group(1).replace('data-in="23.08"',f'data-in="{T.DUR-T.END:.2f}"')
o=lambda s:round(T.s2o(s),2)
tr=json.load(open(f"{HERE}/tr.json"))
W=[[w["w"].strip(),w["s"],w["e"]] for s in tr for w in s["words"]]
W=[w for w in W if w[0]!="Eh,"]
for w in W:
    if w[0]=="Dan" and w[1]>52: w[0]="DM"
    if w[0]=="kami" and w[1]>52: pass
M=[]
for w in W:
    if w[0].startswith("-") and M: M[-1][0]+=w[0];M[-1][2]=w[2]
    else: M.append(list(w))
FIX={"trik":"trick"}
HL=set("kosong 0 1 2 3 4 5 6 7 8 sifir trick gandaan tambah kali selesai mudah menghafal mampu lemah dm sukses peperiksaan".split())
caps=[];cur=[]
def flush():
    global cur
    if cur: caps.append([cur[0][1],cur[-1][2],cur]);cur=[]
for w in M:
    b=re.sub(r"[.,?]","",w[0]);txt=FIX.get(b,b)+re.sub(r"[^.,?]","",w[0])
    glue=cur and re.sub(r"[.,?]","",cur[-1][0]).lower() in ("sifir","kali","gandaan")
    if cur and not glue and (len(cur)>=3 or w[1]-cur[-1][2]>0.25): flush()
    if cur and glue and len(cur)>=4: flush()
    cur.append([txt,w[1],w[2]])
    if re.search(r"[.,?]$",txt): flush()
flush()
CAPS=[]
for i,(s,e,ws) in enumerate(caps):
    nxt=caps[i+1][0] if i+1<len(caps) else e+0.4
    e2=min(max(e+0.15,s+0.35),nxt)
    words=[("*" if re.sub(r"[.,?]","",x[0]).lower() in HL else "")+re.sub(r"[.,]$","",x[0]) for x in ws]
    CAPS.append([o(s),o(e2)," ".join(words)])
bx=lambda X:round(T.bx(X))
def hl(grp,cols,rows,cls="rowhl"):
    h=""
    for ((s,e),_),r in zip(grp,rows):
        y=T.row_y(r)-36
        h+=f'<div class="el {cls}" data-in="{o(s-0.05)}" data-out="{o(e+0.35)}" data-a="fade" data-fo="0.2" style="left:{bx(cols[0])}px;top:{y:.0f}px;width:{bx(cols[1])-bx(cols[0])}px"></div>\n'
    return h
labels="".join(f'<div class="el lab" data-in="{o(s)}" data-out="{o(32.3)}" data-a="slide" style="top:{T.row_y(r)-26:.0f}px">{r+1} × 8 =</div>\n' for r,((s,e),_) in enumerate(T.RL[:4]))
labels+=f'<div class="el lab" data-in="{o(30.6)}" data-out="{o(32.3)}" data-a="slide" style="top:{T.row_y(4)-26:.0f}px">5 × 8 =</div>\n'
labels+=f'<div class="el lab" data-in="{o(30.9)}" data-out="{o(32.3)}" data-a="slide" style="top:{T.row_y(0)-26:.0f}px;left:{bx(640)+6}px;text-align:left;width:auto">← 6 × 8</div>\n'
body=f"""
<div id="thumb" class="el" data-in="0" data-out="1.0" data-a="none">
  <div class="hw" style="position:absolute;left:0;width:920px;top:300px;text-align:center">8 × 7 = <span style="color:#f2b33d">56</span></div>
  <div class="hook" style="top:1130px;left:60px;width:800px"><div class="h1">TRICK SIFIR 8</div><div class="h2" style="font-size:58px">UNTUK ANAK LEMAH SIFIR</div></div>
</div>
<div id="name" class="el" data-in="1.3" data-out="{o(3.2)}" data-a="slide" style="top:1135px"><div class="ring"><img src="face.png"></div><div class="txt">Cikgu AlFarhan</div></div>
<div class="el" data-in="{o(0.3)}" data-out="{o(3.25)}" data-a="pop" style="left:0;width:1000px;top:272px;text-align:center"><div class="title"><small>Anak masih lemah</small>SIFIR 8?</div></div>
<div id="divbar" class="el" data-in="{o(T.TEACH[0]+0.15)}" data-out="{o(T.TEACH[1]+0.3)}" data-a="fade" data-fo="0.3"><span>SIFIR 8 · CIKGU ALFARHAN</span></div>
<div class="el step" data-in="{o(3.28)}" data-out="{o(8.1)}" data-a="slide"><b>LANGKAH 1</b>Tulis 0 → 4</div>
<div class="el step" data-in="{o(8.18)}" data-out="{o(12.2)}" data-a="slide"><b>LANGKAH 2</b>Sambung 4 → 8 di sebelah</div>
<div class="el step" data-in="{o(12.26)}" data-out="{o(20.1)}" data-a="slide"><b>LANGKAH 3</b>Gandaan 2 dari bawah: 0, 2, 4, 6, 8</div>
<div class="el step" data-in="{o(20.16)}" data-out="{o(26.45)}" data-a="slide"><b>LANGKAH 4</b>Sebelah pun gandaan 2</div>
<div class="el step" data-in="{o(26.5)}" data-out="{o(32.3)}" data-a="slide"><b>SIAP!</b>Baca setiap baris = jawapan</div>
{hl(T.T1,(180,300),range(5))}{hl(T.T2,(420,520),range(5))}{hl(T.U1,(300,420),[4,3,2,1,0])}{hl(T.U2,(520,640),[4,3,2,1,0])}{hl(T.RL[:4],(170,650),range(4))}
{labels}
<div class="el" data-in="{o(16.1)}" data-out="{o(20.1)}" data-a="pop" style="left:{bx(300)-10}px;top:{T.row_y(4)+44:.0f}px"><span class="up">↑ mula dari bawah</span></div>
<div class="el" data-in="{o(26.5)}" data-out="{o(27.3)}" data-a="pop" style="left:0;width:1080px;top:560px;text-align:center"><span class="stamp">SIFIR 8 SIAP ✓</span></div>
<div id="follow" class="el" data-in="{o(20.16)}" data-out="{o(22.2)}" data-a="pop" style="left:700px;top:1300px;width:210px;padding:12px"><b style="font-size:24px">Cikgu AlFarhan</b><span style="font-size:19px">@aster.edu_tpg</span><div class="btn" style="font-size:26px">Follow saya</div></div>
<div class="el" data-in="{o(32.64)}" data-out="{o(33.5)}" data-a="pop" style="left:0;width:1000px;top:290px;text-align:center"><span class="pill y" style="font-size:52px">Mudah kan? ✓</span></div>
<div class="el paper" data-in="{o(33.54)}" data-out="{o(37.0)}" data-a="pop" style="left:0;right:80px;margin:auto;top:292px;width:640px;text-align:center"><small>Sebenarnya</small><div style="font:900 52px/1.1 Poppins">banyak cara &amp; <span style="background:var(--yel);padding:0 10px;border-radius:10px">trick</span> kuasai sifir</div></div>
<div class="el" data-in="{o(37.06)}" data-out="{o(40.95)}" data-a="pop" style="left:0;width:1000px;top:276px;text-align:center"><div class="strike"><small class="el" data-in="{o(37.06)}" data-out="{o(38.55)}" data-a="none" style="position:absolute;left:0;right:0;top:-46px">Salah satunya: memang</small><small class="el" data-in="{o(38.6)}" data-out="{o(40.95)}" data-a="none" style="position:absolute;left:0;right:0;top:-46px">Tak semua anak mampu</small>MENGHAFAL<span class="ln el" data-in="{o(40.3)}" data-out="{o(40.95)}" data-a="wipe" style="width:106%"></span></div></div>
<div class="el paper" data-in="{o(41.0)}" data-out="{o(44.95)}" data-a="pop" style="left:0;right:80px;margin:auto;top:292px;width:660px;text-align:center"><small>Jadi kami datangkan</small><div style="font:900 52px/1.1 Poppins"><span style="color:#1f9d4c">PELBAGAI CARA</span><br>untuk anak kuasai sifir ✓</div></div>
<div class="el" data-in="{o(45.1)}" data-out="{o(53.76)}" data-a="drop" style="left:0;width:1000px;top:268px;text-align:center"><span class="pill" style="background:#e0322b;border-color:#fff">Pendaftaran 2027 dibuka</span></div>
<div class="el paper" data-in="{o(45.1)}" data-out="{o(47.6)}" data-a="pop" style="left:0;right:80px;margin:auto;top:370px;width:600px;text-align:center"><small>Ibu ayah</small><div style="font:900 50px/1.1 Poppins">jangan berputus asa 💪</div></div>
<div id="lt" class="el" data-in="{o(47.7)}" data-out="{o(50.4)}" data-a="slide" style="top:1120px"><div class="a">MATH TURBO 2027</div><div class="b">Tuisyen online bersama Cikgu AlFarhan</div></div>
<div class="el" data-in="{o(50.4)}" data-out="{o(52.1)}" data-a="pop" style="left:0;width:1000px;top:1130px;text-align:center"><span class="pill y"><b>SUKSES</b> dalam peperiksaan ✓</span></div>
<div class="el" data-in="{o(52.12)}" data-out="{o(53.76)}" data-a="pop" style="left:0;width:1000px;top:1130px;text-align:center"><span class="pill"><span class="ic"><svg viewBox="0 0 24 24" fill="#111"><path d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2z"/></svg></span>DM kami</span></div>
"""
css+=f"""
#wm{{top:232px}}
.hw{{font:700 104px/1 Caveat;color:#fff;letter-spacing:2px;text-shadow:0 4px 14px rgba(0,0,0,.7)}}
.title{{display:inline-block;font:900 128px/0.95 Poppins;color:var(--yel);-webkit-text-stroke:14px #111;paint-order:stroke fill;letter-spacing:-3px;text-shadow:0 10px 24px rgba(0,0,0,.6)}}
.title small{{display:block;font:900 44px Poppins;color:#fff;-webkit-text-stroke:8px #111;letter-spacing:1px;margin-bottom:6px}}
#divbar{{left:0;top:{T.DIV-8}px;width:1080px;height:12px;background:var(--yel)}}
#divbar span{{position:absolute;right:190px;top:-38px;background:var(--yel);color:#111;font:900 24px Poppins;letter-spacing:2px;padding:6px 14px;border-radius:10px 10px 0 0}}
.step{{left:{T.BPOS[0]-60}px;top:282px;display:flex;align-items:center;gap:14px;font:800 32px Poppins;color:#fff;white-space:nowrap}}
.step b{{background:var(--yel);color:#111;font:900 30px Poppins;padding:6px 16px;border-radius:10px;letter-spacing:1px}}
.rowhl{{height:72px;border-radius:14px;background:rgba(255,210,31,.16);border:4px solid var(--yel);box-sizing:border-box}}
.lab{{left:60px;width:{bx(180)-70}px;text-align:right;font:800 36px Poppins;color:var(--yel);white-space:nowrap}}
.up{{display:inline-block;background:#111;color:var(--yel);border:3px solid var(--yel);border-radius:999px;font:800 26px Poppins;padding:4px 16px}}
.stamp{{display:inline-block;font:900 78px Poppins;color:#111;background:var(--yel);padding:10px 34px;border-radius:20px;border:6px solid #111;transform:rotate(-4deg);box-shadow:0 14px 34px rgba(0,0,0,.6)}}
#cap .w{{margin:0 7px}}
"""
TB,TE=o(T.TEACH[0]),o(T.TEACH[1])
js=re.sub(r"const CAPS=.*?;\n","const CAPS="+json.dumps(CAPS,ensure_ascii=False)+";\n",js,count=1,flags=re.S)
js=re.sub(r"\{const q=document.getElementById\('eq'\).*?\}\}\n","",js,flags=re.S)
js=js.replace("cap.style.top=(t>=14.04&&t<16.3)?'1240px':'1290px';",f"cap.style.top=(t>={TB+0.3:.2f}&&t<{TE+0.2:.2f})?'1062px':'1290px';")
js=js.replace("document.querySelectorAll('.brimg').forEach(e=>{const a=+e.closest('.el').dataset.in;e.style.transform=`scale(${1+0.04*Math.max(0,t-a)})`});","")
html=f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="fonts_local.css"><style>{css}</style></head>
<body><div id="stage">{body}
{end}
<div id="cap" class="el"></div>
<div id="wm" class="el">asteredu11.com.my</div>
</div><script>{js}</script></body></html>"""
open(f"{OUTD}/overlay.html","w").write(html)
json.dump(CAPS,open(f"{HERE}/caps.json","w"),ensure_ascii=False)
print(len(CAPS));[print(c) for c in CAPS]
