# Render AS-F-002 (Aster TOFU): base cut/zoom/grade (ffmpeg) + overlay graphics (Pillow, piped) + audio mix.
# usage: asf002_render.py plan.json raw.mov logo.png fonts_dir sfx_dir out.mp4 WIDTH [crf] [abitrate]
import json,sys,os,subprocess,math,wave,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
plan_p,raw,logo_p,FD,SFXD,out=sys.argv[1:7];W=int(sys.argv[7]);CRF=sys.argv[8] if len(sys.argv)>8 else "23";AB=sys.argv[9] if len(sys.argv)>9 else "128k"
H=W*16//9;S=W/1080;FPS=30
P=json.load(open(plan_p));DUR=P["duration"];C0=P["thumb"];C1=round(C0+P["content"],3)
tmp=os.path.splitext(out)[0]+"_tmp";os.makedirs(tmp,exist_ok=True)
NAVY=(19,36,94);NAVY2=(10,22,64);YEL=(255,200,61);RED=(226,35,45);INK=(11,20,48);WHITE=(255,255,255);PEN=(31,63,168)
GRADE="eq=brightness=0.02:contrast=1.06:saturation=1.08:gamma=1.02,colorbalance=rs=-0.01:bs=0.01:rm=-0.005"
THUMB_SRC=46.6
SW,SH=720,1280;EYE=(338,500)
def crop(z):
    cw,ch=SW/z,SH/z
    x0=min(max(EYE[0]-cw/2,0),SW-cw);y0=min(max(EYE[1]-(0.33 if z>1 else 0.39)*ch,0),SH-ch)
    return f"crop={int(cw)//2*2}:{int(ch)//2*2}:{int(x0)}:{int(y0)},scale={W}:{H}:flags=lanczos,setsar=1"
def run(cmd): subprocess.run(cmd,check=True)
# ---------- base video + voice ----------
segs=P["segments"];fc=[]
for i,(sg,z) in enumerate(zip(segs,P["zoom"])):
    d=sg["src_out"]-sg["src_in"]
    fc.append(f"[0:v]trim={sg['src_in']}:{sg['src_out']},setpts=PTS-STARTPTS,{crop(z)}[v{i}]")
    fc.append(f"[0:a]atrim={sg['src_in']}:{sg['src_out']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
n=len(segs)
fc.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[cv][ca]")
fc.append(f"[cv]fps={FPS},{GRADE},tpad=start_duration={C0}:stop_duration={P['end']}:color=black,format=yuv420p[vout]")
fc.append(f"[ca]highpass=f=80,afftdn=nr=8:nf=-50,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,adelay={int(C0*1000)}:all=1,apad=whole_dur={DUR},aresample=48000[aout]")
base=f"{tmp}/base.mp4";voice=f"{tmp}/voice.wav"
run(["ffmpeg","-v","error","-y","-i",raw,"-filter_complex",";".join(fc),"-map","[vout]","-c:v","libx264","-crf","14","-preset","veryfast","-t",str(DUR),base,
     "-map","[aout]","-ac","2","-t",str(DUR),voice])
run(["ffmpeg","-v","error","-y","-ss",str(THUMB_SRC),"-i",raw,"-frames:v","1","-vf",crop(1.13)+","+GRADE,f"{tmp}/thumb_bg.png"])
# ---------- audio: voice + sfx, then loudness -14 LUFS / -1 dBTP ----------
def readwav(p):
    w=wave.open(p);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,w.getnchannels()).astype(np.float32)/32768
    return a,w.getframerate()
v,sr=readwav(voice);mix=v.copy()
for s in P["sfx"]:
    x,xsr=readwav(os.path.join(SFXD,s["name"]+".wav"))
    if xsr!=sr: idx=np.arange(0,len(x),xsr/sr);x=np.stack([np.interp(idx,np.arange(len(x)),x[:,c]) for c in range(2)],1)
    i=int(s["t"]*sr);j=min(len(mix),i+len(x));mix[i:j]+=x[:j-i]*s["gain"]*0.32
mixp=f"{tmp}/mix.wav"
with wave.open(mixp,"w") as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes())
m=subprocess.run(["ffmpeg","-hide_banner","-i",mixp,"-af","loudnorm=I=-14:TP=-1:LRA=11:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
j=json.loads(m[m.rindex("{"):m.rindex("}")+1])
ln=f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
final_a=f"{tmp}/final.wav";run(["ffmpeg","-v","error","-y","-i",mixp,"-af",ln+",aresample=48000",final_a])
# ---------- overlay graphics ----------
FC={}
def F(name,size):
    k=(name,int(size*S))
    if k not in FC:
        f=ImageFont.truetype(os.path.join(FD,name+".ttf"),max(6,int(size*S)))
        if name=="Caveat": f.set_variation_by_axes([700])
        FC[k]=f
    return FC[k]
def px(v): return int(round(v*S))
def ease_back(x): c=1.7;x=min(max(x,0),1);return 1+(c+1)*(x-1)**3+c*(x-1)**2
def ease(x): x=min(max(x,0),1);return 1-(1-x)**3
def shadow(img,r=6,off=(0,4),a=150):
    sh=Image.new("RGBA",img.size,(0,0,0,0));al=img.split()[3].point(lambda p:p*a//255)
    sh.putalpha(al);sh=sh.filter(ImageFilter.GaussianBlur(px(r)))
    out=Image.new("RGBA",(img.width+px(abs(off[0])),img.height+px(abs(off[1]))),(0,0,0,0))
    out.alpha_composite(sh,(px(off[0]),px(off[1])));out.alpha_composite(img);return out
def pad(img,p):
    o=Image.new("RGBA",(img.width+2*p,img.height+2*p),(0,0,0,0));o.alpha_composite(img,(p,p));return o
def text_img(t,font,fill,stroke=0,sfill=INK):
    b=font.getbbox(t,stroke_width=stroke);im=Image.new("RGBA",(b[2]-b[0],b[3]-b[1]),(0,0,0,0))
    ImageDraw.Draw(im).text((-b[0],-b[1]),t,font=font,fill=fill,stroke_width=stroke,stroke_fill=sfill);return im
def rrect(w,h,r,fill,outline=None,ow=0):
    im=Image.new("RGBA",(w,h),(0,0,0,0));ImageDraw.Draw(im).rounded_rectangle((0,0,w-1,h-1),r,fill=fill,outline=outline,width=ow);return im
LOGO=Image.open(logo_p).convert("RGBA")
def face(d,ring=None):
    ring=ring or max(2,d//22);im=Image.new("RGBA",(d,d),(0,0,0,0));dr=ImageDraw.Draw(im)
    dr.ellipse((0,0,d-1,d-1),fill=YEL);inner=d-2*ring
    lg=LOGO.resize((inner,inner),Image.LANCZOS);mask=Image.new("L",(inner,inner),0);ImageDraw.Draw(mask).ellipse((0,0,inner-1,inner-1),fill=255)
    a=np.minimum(np.array(lg.split()[3]),np.array(mask));lg.putalpha(Image.fromarray(a))
    bg=Image.new("RGBA",(inner,inner),(0,0,0,0));ImageDraw.Draw(bg).ellipse((0,0,inner-1,inner-1),fill=NAVY);bg.alpha_composite(lg)
    im.alpha_composite(bg,(ring,ring));return im
def tiktok(s,base=(0,0,0)):
    # TikTok note glyph: cyan + red offsets under the main note
    im=Image.new("RGBA",(s,s),(0,0,0,0))
    def note(dr,dx,dy,col):
        u=s/24
        dr.rectangle((dx+11*u,dy+3*u,dx+14*u,dy+16*u),fill=col)
        dr.ellipse((dx+4*u,dy+12*u,dx+13*u,dy+21*u),outline=col,width=max(2,int(3*u)))
        dr.arc((dx+11*u,dy-3*u,dx+21*u,dy+9*u),180,270,fill=col,width=max(2,int(3*u)))
        dr.pieslice((dx+11*u,dy+0*u,dx+21*u,dy+9*u),180,270,fill=col)
    dr=ImageDraw.Draw(im);u=s/24
    note(dr,-u,-u,(37,244,238));note(dr,u,u,(254,44,85));note(dr,0,0,base);return im
def check_mark(s,col=(34,170,90),w=None):
    im=Image.new("RGBA",(s,s),(0,0,0,0));ImageDraw.Draw(im).line([(s*.12,s*.55),(s*.4,s*.82),(s*.9,s*.15)],fill=col,width=w or max(3,s//7),joint="curve");return im
def star(s,col=YEL,outline=INK):
    im=Image.new("RGBA",(s,s),(0,0,0,0));c=s/2;pts=[]
    for k in range(10):
        r=(s*.48 if k%2==0 else s*.2);a=-math.pi/2+k*math.pi/5;pts.append((c+r*math.cos(a),c+r*math.sin(a)))
    ImageDraw.Draw(im).polygon(pts,fill=col,outline=outline,width=max(1,s//18));return im
def heart(s,col=RED):
    im=Image.new("RGBA",(s,s),(0,0,0,0));d=ImageDraw.Draw(im)
    d.ellipse((0,s*.05,s*.55,s*.6),fill=col);d.ellipse((s*.45,s*.05,s,s*.6),fill=col);d.polygon([(s*.04,s*.42),(s*.96,s*.42),(s*.5,s*.95)],fill=col);return im
CX=0.455*W  # content centre: keeps text out of the right 15 % strip
def at_center(img,cy): return (int(CX-img.width/2),int(cy))
# ---- sprites ----
def wm():
    t=text_img("asteredu11.com.my",F("Poppins-SemiBold",32),(255,255,255,int(255*0.68)))
    return shadow(shadow(pad(t,px(4)),r=2,off=(1,1),a=200),r=6,off=(0,1),a=110)
def topbox():
    a=text_img("CALON SPM",F("Poppins-Black",64),YEL,px(3),NAVY2)
    b=text_img("SPM 2026 · CIKGU ALFARHAN",F("Poppins-Bold",26),WHITE)
    w=max(a.width,b.width)+px(56);h=a.height+b.height+px(44)
    box=rrect(w,h,px(18),NAVY,YEL,px(4));box.alpha_composite(a,((w-a.width)//2,px(16)));box.alpha_composite(b,((w-b.width)//2,px(26)+a.height))
    return shadow(box)
def label():
    f=face(px(92));t=text_img("Cikgu AlFarhan",F("Poppins-ExtraBold",40),WHITE)
    w=f.width+t.width+px(46);h=px(104);p=rrect(w,h,h//2,NAVY+(235,),YEL,px(3));p.alpha_composite(f,(px(6),px(6)));p.alpha_composite(t,(f.width+px(22),(h-t.height)//2))
    return shadow(p)
def sticker(txt):
    t=text_img(txt,F("Poppins-Black",48),WHITE);w,h=t.width+px(44),t.height+px(34)
    p=rrect(w,h,px(14),RED,WHITE,px(5));p.alpha_composite(t,(px(22),px(17)))
    return shadow(pad(p,px(10)).rotate(5,resample=Image.BICUBIC,expand=True))
def pill(txt,icon):
    t=text_img(txt,F("Poppins-ExtraBold",40),INK);ic=heart(px(46)) if icon=="heart" else star(px(52))
    w=t.width+ic.width+px(60);h=max(t.height,ic.height)+px(30);p=rrect(w,h,h//2,YEL,WHITE,px(4))
    p.alpha_composite(ic,(px(20),(h-ic.height)//2));p.alpha_composite(t,(px(34)+ic.width,(h-t.height)//2));return shadow(p)
CARD_W=int(0.80*W)
def paper_card(h,title=None):
    c=rrect(CARD_W,h,px(18),(255,253,247));d=ImageDraw.Draw(c)
    for y in range(px(108),h-px(4),px(66)): d.line((px(14),y,CARD_W-px(14),y),fill=(205,220,240),width=max(1,px(2)))
    if title: d.text((px(26),px(14)),title,font=F("Poppins-Bold",24),fill=RED)
    # pencil
    x0,y0=CARD_W-px(70),px(14);d.polygon([(x0,y0+px(36)),(x0+px(8),y0+px(44)),(x0+px(44),y0+px(8)),(x0+px(36),y0)],fill=(255,190,40),outline=INK)
    d.polygon([(x0,y0+px(36)),(x0+px(8),y0+px(44)),(x0-px(4),y0+px(48))],fill=(60,60,60));return c
def hand(txt,size=62,col=PEN): return text_img(txt,F("Caveat",size),col)
def follow_card(followed):
    w,h=CARD_W,px(160);c=rrect(w,h,px(22),WHITE);f=face(px(116),px(5));c.alpha_composite(f,(px(20),(h-f.height)//2))
    n=text_img("Cikgu AlFarhan",F("Poppins-ExtraBold",36),INK);c.alpha_composite(n,(px(152),px(34)))
    tk=tiktok(px(36));c.alpha_composite(tk,(px(150),px(86)))
    hd=text_img("@aster.edu_tpg",F("Poppins-SemiBold",28),(90,90,100));c.alpha_composite(hd,(px(192),px(90)))
    bw,bh=px(190),px(62)
    if followed:
        b=rrect(bw,bh,px(12),(233,233,238));t=text_img("Followed",F("Poppins-Bold",28),INK);ck=check_mark(px(26),INK,px(4))
        b.alpha_composite(ck,(px(16),(bh-ck.height)//2));b.alpha_composite(t,(px(48),(bh-t.height)//2))
    else:
        b=rrect(bw,bh,px(12),(254,44,85));t=text_img("+ Follow",F("Poppins-Bold",30),WHITE);b.alpha_composite(t,((bw-t.width)//2,(bh-t.height)//2))
    c.alpha_composite(b,(w-bw-px(22),(h-bh)//2));return shadow(c)
def stamp(txt):
    t=text_img(txt,F("Poppins-Black",58),RED);w,h=t.width+px(50),t.height+px(40)
    p=rrect(w,h,px(10),(255,255,255,225),RED,px(8));p.alpha_composite(t,(px(25),px(20)))
    return shadow(pad(p,px(10)).rotate(-6,resample=Image.BICUBIC,expand=True))
def goodluck(sub):
    g=text_img("GOOD LUCK!",F("Poppins-Black",112),YEL,px(7),NAVY2);w=g.width+px(120);h=g.height+px(100)
    im=Image.new("RGBA",(w,h),(0,0,0,0));im.alpha_composite(g,(px(60),px(6)))
    for x,y,s in ((0,px(4),px(58)),(w-px(56),px(0),px(50)),(w-px(40),g.height-px(10),px(34))): im.alpha_composite(star(s),(x,y))
    if sub:
        t=text_img("SUKSES SELALU",F("Poppins-ExtraBold",38),WHITE);p=rrect(t.width+px(48),t.height+px(26),px(30),NAVY,YEL,px(3))
        p.alpha_composite(t,(px(24),px(13)));im.alpha_composite(p,((w-p.width)//2,g.height+px(14)))
    return shadow(im)
CAPF=F("Poppins-ExtraBold",62)
def caption(words):
    sp=CAPF.getlength(" ");parts=[];x=0
    for w in words:
        t=w["w"].upper();parts.append((t,YEL if w["hot"] else WHITE,x));x+=CAPF.getlength(t)+sp
    width=int(x-sp)+px(16);asc,desc=CAPF.getmetrics();im=Image.new("RGBA",(width,asc+desc+px(16)),(0,0,0,0));d=ImageDraw.Draw(im)
    for t,col,xx in parts: d.text((xx+px(8),px(8)),t,font=CAPF,fill=col,stroke_width=px(6),stroke_fill=INK)
    if im.width>0.8*W: im=im.resize((int(0.8*W),int(im.height*0.8*W/im.width)),Image.LANCZOS)
    return shadow(im,r=5,off=(0,4),a=170)
def endcard():
    im=Image.new("RGBA",(W,H));g=np.linspace(0,1,H)[:,None,None]
    a=np.array(NAVY2)[None,None,:]*(1-g)+np.array((29,60,154))[None,None,:]*g
    im=Image.fromarray(np.concatenate([np.repeat(a,W,1),np.full((H,W,1),255)],2).astype(np.uint8),"RGBA")
    f=face(px(340),px(12));im.alpha_composite(f,at_center(f,0.19*H))
    y=0.19*H+f.height+px(30)
    n=text_img("Cikgu AlFarhan",F("Poppins-Black",76),WHITE);im.alpha_composite(n,at_center(n,y));y+=n.height+px(30)
    tk=tiktok(px(56),WHITE);hd=text_img("@aster.edu_tpg",F("Poppins-Bold",46),YEL);rw=tk.width+px(14)+hd.width
    x0=int(CX-rw/2);im.alpha_composite(tk,(x0,int(y+(hd.height-tk.height)/2)));im.alpha_composite(hd,(x0+tk.width+px(14),int(y)));y+=hd.height+px(44)
    t=text_img("Follow untuk tips belajar anak seterusnya",F("Poppins-ExtraBold",36),INK);p=rrect(t.width+px(56),t.height+px(34),px(40),YEL)
    p.alpha_composite(t,(px(28),px(17)));im.alpha_composite(p,at_center(p,y));y+=p.height+px(56)
    s=text_img("asteredu11.com.my",F("Poppins-Black",66),WHITE);im.alpha_composite(s,at_center(s,y))
    return im
def thumb():
    im=Image.open(f"{tmp}/thumb_bg.png").convert("RGBA").resize((W,H))
    g=np.clip((np.linspace(0,1,H)-0.42)/0.35,0,1)**1.2*200;ov=np.zeros((H,W,4),np.uint8);ov[...,:3]=np.array(NAVY2);ov[...,3]=g[:,None].astype(np.uint8)
    im.alpha_composite(Image.fromarray(ov,"RGBA"))
    y=0.505*H
    a=text_img("SPM ESOK?",F("Poppins-Black",124),WHITE,px(8),NAVY2);a=shadow(a);im.alpha_composite(a,at_center(a,y));y+=a.height+px(14)
    for txt,bg,fg in (("JANGAN",YEL,NAVY2),("GABRA!",RED,WHITE)):
        t=text_img(txt,F("Poppins-Black",132),fg);b=rrect(t.width+px(60),t.height+px(40),px(18),bg);b.alpha_composite(t,(px(30),px(20)))
        b=shadow(b.rotate(-3 if bg==RED else 2,resample=Image.BICUBIC,expand=True));im.alpha_composite(b,at_center(b,y));y+=b.height-px(6)
    return im
def paper_full(t,lines):
    im=Image.new("RGBA",(W,H),(251,248,240,255));d=ImageDraw.Draw(im)
    for y in range(px(420),H,px(96)): d.line((0,y,W,y),fill=(196,214,238),width=max(1,px(3)))
    d.line((px(120),0,px(120),H),fill=(232,120,120),width=max(1,px(3)))
    d.text((px(150),px(330)),"KERTAS JAWAPAN",font=F("Poppins-Bold",34),fill=RED)
    nm=hand("Nama: Calon SPM",60);im.alpha_composite(nm,(int(0.84*W)-nm.width,px(300)))
    for k,lt in enumerate(lines):
        if t<lt: continue
        y=px(420)+px(96)*(2*k+1)-px(80);txt=hand(f"Soalan {k+1}:  dijawab",80)
        rev=ease((t-lt)/0.45);cw=int(txt.width*rev)
        if cw>0: im.alpha_composite(txt.crop((0,0,cw,txt.height)),(px(160),y))
        if t-lt>0.45:
            ck=check_mark(px(90));im.alpha_composite(ck,(px(160)+txt.width+px(30),y))
    return im
# ---------- cache + per-frame compose ----------
SP={}
def sp(key,fn):
    if key not in SP: SP[key]=fn()
    return SP[key]
def put(canvas,img,xy,alpha=1.0,scale=1.0,anchor=(0.5,0.5)):
    if alpha<=0.01: return
    if abs(scale-1)>0.01:
        nw,nh=max(1,int(img.width*scale)),max(1,int(img.height*scale));ax,ay=xy[0]+img.width*anchor[0],xy[1]+img.height*anchor[1]
        img=img.resize((nw,nh),Image.BILINEAR);xy=(int(ax-nw*anchor[0]),int(ay-nh*anchor[1]))
    if alpha<0.99:
        img=img.copy();img.putalpha(img.split()[3].point(lambda p:int(p*alpha)))
    canvas.alpha_composite(img,(int(xy[0]),int(xy[1]))) if xy[0]>=0 and xy[1]>=0 else canvas.paste(img,(int(xy[0]),int(xy[1])),img)
def env(t,s,e,din=0.22,dout=0.18):
    if t<s or t>=e: return 0,1
    a=min(1,(t-s)/din if din else 1,(e-t)/dout if dout else 1);sc=0.75+0.25*ease_back((t-s)/din) if din else 1
    return max(0,a),sc
TOP_Y=int(0.015*H)
def draw(t):
    cv=Image.new("RGBA",(W,H),(0,0,0,0))
    for g in P["graphics"]:
        k=g["kind"];s,e=g["s"],g["e"]
        if not(s<=t<e): continue
        if k=="thumb": cv.alpha_composite(sp("thumb",thumb))
        elif k=="endcard":
            a=min(1,(t-s)/0.25);put(cv,sp("end",endcard),(0,0),a)
        elif k=="paper":
            a=min(1,(t-s)/0.15,(e-t)/0.15);im=paper_full(t,P["paper_lines"])
            put(cv,im,(0,0),a)
        elif k=="topbox":
            a,sc=env(t,s,e,0.25,0.2);b=sp("top",topbox);put(cv,b,at_center(b,TOP_Y),a,sc,(0.5,0))
        elif k=="label":
            a=min(1,(t-s)/0.25,(e-t)/0.25);b=sp("label",label);x=px(50)-int((1-ease((t-s)/0.35))*px(120));put(cv,b,(max(0,x),int(0.665*H)),a)
        elif k=="sticker":
            a,sc=env(t,s,e,0.25);b=sp("st"+g["text"],lambda:sticker(g["text"]));put(cv,b,(px(40),int(0.165*H)),a,sc)
        elif k=="pill":
            a,sc=env(t,s,e,0.25);b=sp("pl"+g["text"],lambda:pill(g["text"],g.get("icon","heart")));put(cv,b,(px(46),int(0.17*H)),a,sc)
        elif k=="note":
            a,sc=env(t,s,e,0.25,0.2);c=paper_card(px(196),g["title"]).copy()
            l1=" , ".join(x[0] for x in g["lines"][:2] if t>=x[1]).replace(" ,",",")
            if l1:
                im=hand(l1);c.alpha_composite(im,(px(30),px(44)))
            ln=g["lines"][2]
            if t>=ln[1]:
                im=hand(ln[0]);cw=int(im.width*ease((t-ln[1])/0.4));
                if cw>0: c.alpha_composite(im.crop((0,0,cw,im.height)),(px(30),px(110)))
                if t-ln[1]>0.4: ImageDraw.Draw(c).line((px(30),px(180),px(30)+im.width,px(180)),fill=YEL,width=px(8))
            put(cv,shadow(c),at_center(c,TOP_Y),a,sc,(0.5,0))
        elif k=="check":
            a,sc=env(t,s,e,0.25,0.2);rows=[x for x in P["check"] if t>=x["in"]]
            if not rows: continue
            h=px(30)+px(64)*3;c=rrect(CARD_W,h,px(18),(255,253,247));d=ImageDraw.Draw(c)
            for i,x in enumerate(P["check"]):
                if t<x["in"]: continue
                y=px(16)+px(64)*i;hl=any(0<=t-hh<1.6 for hh in x["hl"]) or 0<=t-x["tick"]<0.6
                if hl: d.rounded_rectangle((px(12),y-px(2),CARD_W-px(12),y+px(62)),px(10),fill=(255,232,160))
                d.rounded_rectangle((px(26),y+px(12),px(68),y+px(54)),px(6),outline=INK,width=px(4))
                if t>=x["tick"]: c.alpha_composite(check_mark(px(56)),(px(22),y))
                im=hand(x["text"],64);cw=int(im.width*ease((t-x["in"])/0.45))
                if cw>0: c.alpha_composite(im.crop((0,0,cw,im.height)),(px(90),y))
            put(cv,shadow(c),at_center(c,TOP_Y),a,sc,(0.5,0))
        elif k=="follow":
            a,sc=env(t,s,e,0.25,0.2);fl=t>=P["follow_tap"];b=sp("fol%d"%fl,lambda:follow_card(fl))
            put(cv,b,at_center(b,TOP_Y),a,sc,(0.5,0))
            dt=t-P["follow_tap"]+0.25
            if 0<=dt<0.6:  # tap ripple on the button
                d=ImageDraw.Draw(cv);cx=int(CX+CARD_W/2-px(117));cy=TOP_Y+px(80);r=px(18)+int(dt*px(90))
                d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(255,255,255,int(255*(1-dt/0.6))),width=px(5))
        elif k=="stamp":
            a=min(1,(t-s)/0.08,(e-t)/0.2);sc=1+0.6*(1-ease((t-s)/0.18));b=sp("stamp",lambda:stamp(g["text"]));put(cv,b,at_center(b,TOP_Y+px(10)),a,sc)
        elif k=="goodluck":
            subt=next(w["s"] for c in P["captions"] for w in c["words"] if w["w"].lower()=="sukses")
            a,sc=env(t,s,e,0.3,0.2);b=sp("gl%d"%(t>=subt),lambda:goodluck(t>=subt));put(cv,b,at_center(b,TOP_Y),a,sc,(0.5,0))
    if C0<=t<C1:
        for c in P["captions"]:
            if c["s"]<=t<c["e"]:
                b=sp(("cap",c["s"]),lambda:caption(c["words"]));sc=0.88+0.12*ease((t-c["s"])/0.12)
                put(cv,b,at_center(b,0.585*H),1,sc);break
    b=sp("wm",wm);cv.alpha_composite(b,(int(0.06*W),int(0.14*H)))
    return cv
if __name__=="__main__":
    mode=os.environ.get("MODE","video")
    if mode=="stills":
        for tt in [float(x) for x in os.environ["TIMES"].split(",")]:
            fr=subprocess.run(["ffmpeg","-v","error","-ss",str(tt),"-i",base,"-frames:v","1","-f","rawvideo","-pix_fmt","rgba","-"],capture_output=True).stdout
            im=Image.frombytes("RGBA",(W,H),fr) if fr else Image.new("RGBA",(W,H),(0,0,0,255))
            im.alpha_composite(draw(tt));im.convert("RGB").save(f"{tmp}/still_{tt:05.2f}.png")
        sys.exit()
    nf=int(round(DUR*FPS))
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-i",base,"-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",final_a,
        "-filter_complex","[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]","-map","[v]","-map","2:a","-c:v","libx264","-preset","medium","-crf",CRF,
        "-profile:v","high","-r",str(FPS),"-c:a","aac","-b:a",AB,"-ar","48000","-movflags","+faststart","-t",str(DUR),out],stdin=subprocess.PIPE)
    for i in range(nf):
        enc.stdin.write(draw(i/FPS).tobytes())
        if i%150==0: print("frame",i,"/",nf,flush=True)
    enc.stdin.close();enc.wait()
    subprocess.run(["ffmpeg","-v","error","-ss","0.5","-i",out,"-frames:v","1",os.path.splitext(out)[0]+"_THUMB.png","-y"])
    print("done",out)
