import re,json
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad"
a10=open(f"{S}/a10/ov/overlay.html").read()
css=re.search(r"<style>(.*?)</style>",a10,re.S).group(1)
js=re.search(r"<script>(.*?)</script>",a10,re.S).group(1)
end=re.search(r'(<div id="end".*?)\n<div id="cap"',a10,re.S).group(1).replace('data-in="44.82"','data-in="23.08"')
fol=re.search(r'(<div id="follow".*?</div></div>)',a10,re.S).group(1).replace('data-in="23.0" data-out="26.2"','data-in="6.6" data-out="8.95"')
lt=re.search(r'(<div class="el" data-in="26.3" data-out="31.6".*?</div>\n<div id="lt".*?</div></div>)',a10,re.S).group(1)
lt=lt.replace('data-in="26.3" data-out="31.6"','data-in="16.42" data-out="19.8"').replace('data-in="26.3" data-out="28.0"','data-in="16.42" data-out="17.6"')
CAPS=[[1.0,2.08,"Siapa yang ada anak"],[2.08,2.96,"*Tingkatan *1?"],[2.96,4.64,"*Algebra menunggu"],[4.64,5.18,"*pecahan"],[5.18,5.8,"*perpuluhan"],[5.8,6.38,"*peratus"],
[6.38,7.14,"Kalau asas"],[7.14,8.0,"*Darjah *6 ni *lemah lagi"],[9.0,9.8,"Tingkatan 1"],[9.8,11.06,"merupakan step"],[11.06,12.24,"yang paling *ngeri"],[12.24,12.82,"untuk anak-anak"],
[12.82,14.04,"Sekarang masa yang *terbaik"],[14.04,15.0,"Kami nak bantu"],[15.0,16.28,"anak-anak *sekolah *menengah ni"],
[16.42,17.26,"Kelas hari *Sabtu"],[17.26,18.14,"*percuma sahaja"],[18.14,19.8,"untuk pelajar-pelajar *sekolah *menengah"],[19.82,20.82,"untuk kuatkan *algebra"],
[21.18,21.7,"*DM saya"],[21.7,23.08,"untuk keterangan lanjut"]]
js=re.sub(r"const CAPS=__CAPS__;","const CAPS="+json.dumps(CAPS,ensure_ascii=False)+";",js)
js=js.replace("cap.style.top=((t>=28.08&&t<34.9)||(t>=37.06&&t<43.25))?'1400px':'1290px';","cap.style.top=(t>=14.04&&t<16.3)?'1240px':'1290px';")
js=js.replace("const mh=document.getElementById('mh');mh.style.transform=`rotate(${(t-1)*40}deg)`;","")
js=js.replace("const d=[...document.querySelectorAll('#dots span')];d.forEach((s,j)=>s.style.opacity=(Math.floor(t*5)%3===j)?1:.3);","document.querySelectorAll('.brimg').forEach(e=>{const a=+e.closest('.el').dataset.in;e.style.transform=`scale(${1+0.04*Math.max(0,t-a)})`});")
css+="""
#board{left:70px;top:262px;width:620px;background:#1e2a22;border:10px solid #6b4a2b;border-radius:16px;padding:14px 26px;box-shadow:0 12px 30px rgba(0,0,0,.5);color:#f4f1e6}
#board .t{font:900 46px Poppins;color:var(--yel);letter-spacing:1px}
#board .eq{font:700 82px/1 Caveat;margin-top:4px}
#board .eq span{opacity:0}
.brwrap{left:80px;top:300px;width:820px;height:820px;border-radius:26px;overflow:hidden;border:8px solid var(--yel);box-shadow:0 20px 50px rgba(0,0,0,.6);background:#fff}
.brimg{width:100%;height:100%;object-fit:cover;display:block;transform-origin:50% 40%}
#brbg{left:0;top:0;width:1080px;height:1920px;background:radial-gradient(circle at 50% 35%,#2a2a2a,#0b0b0b)}
#brlab{left:80px;top:1140px;width:820px;text-align:center}
.chiprow{left:90px;top:1110px;display:flex;gap:14px}
.warn{font:900 92px/1 Poppins;color:#fff;-webkit-text-stroke:12px #111;paint-order:stroke fill;letter-spacing:-2px}
.warn b{color:#ff4d3d}
.warn small{display:block;font:900 40px Poppins;color:var(--yel);-webkit-text-stroke:8px #111;letter-spacing:1px;margin-bottom:6px}
"""
body="""
<div id="thumb" class="el" data-in="0" data-out="1.0" data-a="none">
  <div class="hook"><div class="h1">TINGKATAN 1</div><div class="h2">ALGEBRA MENUNGGU!</div>
  <div class="sub"><span class="pill">Kelas Sabtu <b>PERCUMA</b></span></div></div>
</div>
<div id="name" class="el" data-in="1.3" data-out="4.3" data-a="slide"><div class="ring"><img src="face.png"></div><div class="txt">Cikgu AlFarhan</div></div>
<div class="el paper" data-in="1.0" data-out="2.9" data-a="pop" style="left:540px;top:270px;width:370px"><small>Siapa ada anak</small><div style="font:900 56px/1.05 Poppins">Tingkatan 1?</div></div>
<div id="board" class="el" data-in="2.96" data-out="6.36" data-a="pop"><div class="t">ALGEBRA</div><div class="eq" id="eq">x + 5 = 12</div></div>
<div class="chiprow el" data-in="4.64" data-out="6.36" data-a="none">
  <span class="pill el" data-in="4.64" data-out="6.36" data-a="pop" style="position:relative;font-size:36px;padding:8px 24px">Pecahan</span>
  <span class="pill el" data-in="5.18" data-out="6.36" data-a="pop" style="position:relative;font-size:36px;padding:8px 24px">Perpuluhan</span>
  <span class="pill el" data-in="5.8" data-out="6.36" data-a="pop" style="position:relative;font-size:36px;padding:8px 24px">Peratus</span>
</div>
<div id="note" class="el paper" data-in="6.38" data-out="8.95" data-a="pop"><div class="h">Kalau asas...</div>
  <div class="r el" data-in="7.6" data-out="8.95" data-a="slide" style="position:relative"><i>✗</i>Darjah 6 lemah lagi</div></div>
__FOLLOW__
<div class="el" data-in="9.0" data-out="12.8" data-a="pop" style="left:80px;top:262px"><div class="warn"><small>TINGKATAN 1</small>step paling <b class="el" data-in="11.76" data-out="12.8" data-a="pop" style="position:relative;display:inline-block">NGERI</b></div></div>
<div class="el" data-in="12.82" data-out="14.0" data-a="pop" style="left:110px;top:280px"><span class="pill y">Sekarang masa <b>terbaik</b> ✓</span></div>
<div id="brbg" class="el" data-in="14.04" data-out="16.3" data-a="fade" data-fo="0.15"></div>
<div class="brwrap el" data-in="14.04" data-out="14.8" data-a="pop" data-fo="0.08"><img class="brimg" src="br1.jpg"></div>
<div class="brwrap el" data-in="14.8" data-out="15.55" data-a="pop" data-fo="0.08"><img class="brimg" src="br2.jpg"></div>
<div class="brwrap el" data-in="15.55" data-out="16.3" data-a="pop" data-fo="0.15"><img class="brimg" src="br3.jpg"></div>
__LT__
<div class="el" data-in="17.26" data-out="19.8" data-a="pop" style="left:90px;top:1010px"><div class="paper" style="border-left:14px solid var(--yel)"><small>Kelas hari Sabtu</small><div style="font:900 64px/1 Poppins;color:#e0322b">PERCUMA</div>
  <div class="el" data-in="18.42" data-out="19.8" data-a="pop" style="position:relative;font:800 32px Poppins;margin-top:6px">untuk pelajar <b style="background:#ffd21f;padding:0 8px;border-radius:8px">sekolah menengah</b></div></div></div>
<div class="el" data-in="19.82" data-out="21.1" data-a="pop" style="left:110px;top:1110px"><span class="pill y">Kuatkan <b>ALGEBRA</b> ✓</span></div>
<div class="el" data-in="21.18" data-out="23.08" data-a="pop" style="left:110px;top:1110px"><span class="pill"><span class="ic"><svg viewBox="0 0 24 24" fill="#111"><path d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2z"/></svg></span>DM saya</span></div>
""".replace("__FOLLOW__",fol).replace("__LT__",lt)
js=js.replace("if(e.classList.contains('r')||e.classList.contains('m'))e.style.display=t<a?'none':'flex';","if(e.classList.contains('r')||e.classList.contains('m'))e.style.display=t<a?'none':'flex';\n    if(e.classList.contains('chiprow')){e.style.opacity=(t>=a&&t<b)?1:0;continue}")
js=js.replace("window.render=function(t){","window.render=function(t){\n  {const q=document.getElementById('eq');if(q){const n=Math.max(0,Math.min(10,Math.floor((t-3.1)*8)));q.innerHTML='x + 5 = 12'.split('').map((c,i)=>`<span style=\"opacity:${i<n?1:0}\">${c===' '?'&nbsp;':c}</span>`).join('')}}")
html=f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="fonts_local.css"><style>{css}</style></head>
<body><div id="stage">{body}
{end}
<div id="cap" class="el"></div>
<div id="wm" class="el">asteredu11.com.my</div>
</div><script>{js}</script></body></html>"""
open(f"{S}/a12/ov/overlay.html","w").write(html)
json.dump(CAPS,open(f"{S}/a12/work/caps.json","w"),ensure_ascii=False)
print("ok", "__CAPS__" in html, html.count('id="follow"'), html.count('id="lt"'))
