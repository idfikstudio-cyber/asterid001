import re,json
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad/a11"
css=open(f"{S}/work/a9_css.css").read(); js=open(f"{S}/work/a9_js.js").read(); star=open(f"{S}/work/star.txt").read()
CAPS=[[1.0,1.94,"*RM99 dengan"],[1.94,2.76,"*5 *subjek"],[2.76,3.52,"*BM, *BI, *Math"],[3.52,4.6,"*Sains, *Sejarah"],
[4.6,5.48,"Setiap minggu"],[5.48,6.3,"*seminggu *sekali"],[6.3,7.04,"melalui *Zoom"],[7.04,8.06,"di rumah sahaja"],
[8.12,9.2,"*Rakaman *percuma"],[9.2,10.26,"*modul *percuma"],[10.26,11.32,"guru ada *2 orang"],[11.32,12.22,"dalam satu kelas"],[12.22,13.5,"nota dan modul"],
[13.56,14.14,"Lepas tu"],[14.18,15.6,"*ujian *bulanan kita akan buat"],[15.6,16.86,"setiap hujung bulan"],[16.86,17.98,"supaya anak-anak tahu"],[17.98,19.74,"tahap dia dalam bulan tersebut"],
[19.8,21.02,"Pendaftaran *RM20 sahaja"],[21.04,21.7,"*DM saya"],[21.7,22.5,"untuk keterangan lanjut"]]
js=re.sub(r"const CAPS=\[.*?\]\];","const CAPS="+json.dumps(CAPS,ensure_ascii=False)+";",js,count=1,flags=re.S)
js=js.replace("cap.style.top=(t>=6.08&&t<12.0)?'1420px':'1290px';","cap.style.top=(t>=9.1&&t<14.5)?'1420px':'1290px';")
css+="""
#check{left:66px;top:930px;width:620px;background:#fff;border-radius:26px;padding:18px 26px 14px;color:#1b1b1b;box-shadow:0 14px 34px rgba(0,0,0,.45);border-top:14px solid var(--red)}
#check .it{display:flex;align-items:center;gap:14px;font:800 38px Poppins;padding:6px 0;border-top:2px dashed #eee}
#check .it:first-child{border-top:0}
#check .it i{font-style:normal;width:50px;height:50px;border-radius:50%;background:#1f9d4c;color:#fff;display:grid;place-items:center;font:900 30px Poppins;flex:none}
#check .it b{color:var(--red)}
#cal{left:540px;top:262px;width:370px;background:#fff;border-radius:22px;overflow:hidden;color:#1b1b1b;box-shadow:0 12px 30px rgba(0,0,0,.45);text-align:center}
#cal .top{background:var(--red);color:#fff;font:900 38px Poppins;padding:10px 0;letter-spacing:1px}
#cal .bd{padding:12px 10px 16px;font:900 46px/1.05 Poppins}
#cal .bd small{display:block;font:800 32px Poppins;color:#666;margin-top:6px}
.chips{left:70px;top:1150px;display:flex;gap:12px}
.chip{font-size:36px;padding:4px 20px 4px 8px}
.chip i{width:40px;height:40px;line-height:40px;font-size:22px}
#bars{display:inline-flex;align-items:flex-end;gap:5px;height:40px}
#bars s{display:block;width:10px;background:#1f9d4c;border-radius:3px}
"""
body=f"""
<div id="thumb" class="el" data-in="0" data-out="1.0" data-a="none">
  <div class="top"><span class="pillY"><svg viewBox="0 0 24 24" fill="#ffd21f"><path d="M3 10v4h3l5 4V6L6 10H3zm13.5 2A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/></svg>IBU AYAH, PERHATIAN!</span></div>
  <div class="hook"><div class="h1">5 SUBJEK</div><div class="h2">RM99</div><br><div class="sub">BM · BI · <span>MATH</span> · SAINS · SEJARAH</div></div>
</div>
<div id="banner" class="el" data-in="1.0" data-out="9.0" data-a="drop" data-fo="0.6">
  <span class="pillY"><svg viewBox="0 0 24 24" fill="#ffd21f"><path d="M3 10v4h3l5 4V6L6 10H3zm13.5 2A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/></svg>IBU AYAH, PERHATIAN!</span>
  <div class="redbar">RM99 · 5 SUBJEK</div>
  <div class="yelline el" data-in="5.48" data-out="9.0" data-a="pop" data-fo="0.6" style="position:relative">SEMINGGU SEKALI!</div>
</div>
<div id="name" class="el shadow" data-in="1.3" data-out="4.3" data-a="slide"><div class="ring"><img src="face.png"></div><div class="txt">Cikgu AlFarhan</div></div>
<div id="star" class="el" data-in="1.0" data-out="2.76" data-a="pop" style="left:560px;top:820px;width:360px;height:360px">
  <svg viewBox="0 0 400 400" width="360" height="360" style="position:absolute;inset:0">{star}</svg>
  <div class="in"><div class="s2" style="font-size:100px">RM99</div></div>
</div>
<div id="subj5" class="el" data-in="1.94" data-out="5.9" data-a="pop" style="top:600px"><b>5</b><span>SUBJEK</span></div>
<div class="chips el" data-in="2.76" data-out="5.9" data-a="none" style="opacity:1">
  <span class="chip el" data-in="2.76" data-out="5.9" data-a="pop" style="position:relative"><i>B</i>BM</span>
  <span class="chip el" data-in="3.22" data-out="5.9" data-a="pop" style="position:relative"><i>B</i>BI</span>
  <span class="chip el" data-in="3.52" data-out="5.9" data-a="pop" style="position:relative"><i>÷</i>Math</span>
  <span class="chip el" data-in="3.90" data-out="5.9" data-a="pop" style="position:relative"><i>S</i>Sains</span>
  <span class="chip el" data-in="4.12" data-out="5.9" data-a="pop" style="position:relative"><i>S</i>Sejarah</span>
</div>
<div class="el" data-in="6.3" data-out="8.1" data-a="pop" style="left:110px;top:1010px"><span class="pill"><span class="ic" style="background:#2d8cff"><svg viewBox="0 0 24 24" fill="#fff"><path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5l4 4v-11z"/></svg></span>Melalui Zoom</span></div>
<div class="el" data-in="7.04" data-out="8.1" data-a="pop" style="left:150px;top:1130px"><span class="pill red"><span class="ic" style="background:#fff"><svg viewBox="0 0 24 24" fill="#e31b23"><path d="M12 3 2 12h3v8h5v-5h4v5h5v-8h3z"/></svg></span>Di rumah sahaja</span></div>
<div id="check" class="el" data-in="8.12" data-out="13.5" data-a="pop">
  <div class="it el" data-in="8.12" data-out="13.5" data-a="slide" style="position:relative"><i>✓</i>Rakaman <b>percuma</b></div>
  <div class="it el" data-in="9.2" data-out="13.5" data-a="slide" style="position:relative"><i>✓</i>Modul <b>percuma</b></div>
  <div class="it el" data-in="10.26" data-out="13.5" data-a="slide" style="position:relative"><i>✓</i><b>2 guru</b> dalam 1 kelas</div>
  <div class="it el" data-in="12.22" data-out="13.5" data-a="slide" style="position:relative"><i>✓</i>Nota dan modul</div>
</div>
<div id="cal" class="el" data-in="13.56" data-out="19.74" data-a="pop"><div class="top">UJIAN BULANAN</div><div class="bd"><svg viewBox="0 0 24 24" width="96" height="96" fill="#e31b23"><path d="M7 2v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2zM5 9h14v11H5zm9 7h4v3h-4z"/></svg><small class="el" data-in="15.6" data-out="19.74" data-a="pop" style="position:relative">setiap hujung bulan</small></div></div>
<div class="el" data-in="16.86" data-out="19.74" data-a="pop" style="left:110px;top:1110px"><span class="pill"><span class="ic" style="background:#eafbf0"><span id="bars"><s style="height:14px"></s><s style="height:24px"></s><s style="height:36px"></s></span></span>Anak tahu tahap dia</span></div>
<div id="ticket" class="el" data-in="19.8" data-out="22.5" data-a="pop" data-rot="-4" style="left:60px;top:300px;width:760px;height:230px">
  <div class="stub"><svg viewBox="0 0 24 24" fill="#fff"><path d="M12 2l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17l-6.1 3.4 1.5-6.8L2.2 9l6.9-.7z"/></svg></div>
  <div class="body"><div class="t0">PENDAFTARAN</div><div class="t1">RM20</div><div class="t2" style="position:relative">SAHAJA</div></div>
</div>
<div id="phone" class="el" data-in="21.04" data-out="22.5" data-a="slide">
  <div class="scr"><div class="url"><svg viewBox="0 0 24 24" width="18" height="18" fill="#1f9d4c"><path d="M12 1a5 5 0 0 0-5 5v4H5v13h14V10h-2V6a5 5 0 0 0-5-5zm-3 9V6a3 3 0 0 1 6 0v4z"/></svg>asteredu11.com.my</div>
  <div class="hero"><div class="ring"><img src="face.png"></div><b>Cikgu AlFarhan</b></div>
  <div class="btn">Daftar Sekarang</div><div class="ln"></div><div class="ln s"></div></div>
</div>
<div class="el" data-in="21.04" data-out="22.5" data-a="pop" style="left:420px;top:1120px"><span class="pill"><span class="ic" style="background:var(--red)"><svg viewBox="0 0 24 24" fill="#fff"><path d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2z"/></svg></span>DM saya</span></div>
"""
# end card + caption + watermark from a9
a9=open(f"{S}/../ov/overlay.html").read()
end=re.search(r'(<div id="end".*?)\n<div id="cap"',a9,re.S).group(1).replace('data-in="26.95"','data-in="22.5"')
html=f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="fonts_local.css"><style>{css}</style></head>
<body><div id="stage">{body}
{end}
<div id="cap" class="el"></div>
<div id="wm" class="el">asteredu11.com.my</div>
</div><script>{js}</script></body></html>"""
html=html.replace("if(e.classList.contains('it'))e.style.display=t<a?'none':'flex';","if(e.classList.contains('it'))e.style.display=t<a?'none':'flex';\n    if(e.classList.contains('chips')){e.style.opacity=(t>=a&&t<b)?1:0;continue}")
open(f"{S}/ov/overlay.html","w").write(html)
json.dump(CAPS,open(f"{S}/work/caps.json","w"),ensure_ascii=False)
