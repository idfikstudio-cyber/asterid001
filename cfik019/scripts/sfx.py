# Soft, studio-style sound effects and an ambient music bed, synthesised here so they are royalty free.
# Deliberately quiet and airy: no cartoon pops or boings.
import numpy as np, wave, sys, os, json
SR=44100; out=sys.argv[1]; rng=np.random.default_rng(19)
def t(d): return np.arange(int(SR*d))/SR
def lp(x,c):
    c=np.broadcast_to(np.asarray(c,float),x.shape); y=np.zeros_like(x); s=0.0; k=1-np.exp(-2*np.pi*c/SR)
    for i in range(len(x)): s+=k[i]*(x[i]-s); y[i]=s
    return y
def hp(x,c): return x-lp(x,c)
def save(name,x,g=0.8,stereo=None):
    x=np.stack([x,x],1) if stereo is None else stereo
    x=x/(np.max(np.abs(x))+1e-9)*g
    with wave.open(os.path.join(out,name+".wav"),"w") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
# whoosh: soft band-passed air, swell and release
d=0.7;tt=t(d);sw=500+2600*np.sin(np.pi*tt/d)**2
save("whoosh",hp(lp(rng.standard_normal(len(tt)),sw),sw*.4)*np.sin(np.pi*tt/d)**2,0.6)
# air: long filtered breath for the hook open
d=1.6;tt=t(d);save("air",hp(lp(rng.standard_normal(len(tt)),900+1500*tt/d),300)*(tt/d)**1.5*np.exp(-np.maximum(0,tt-1.3)*12),0.4)
# thud: low felt-mallet hit, no click
d=0.8;tt=t(d);f=70*np.exp(-tt*5)+48
save("thud",np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*6)*(1-np.exp(-tt*400)),0.8)
# tick: wooden tap (list items, dimension marks)
d=0.12;tt=t(d);x=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for a,f,k in [(1,1850,70),(.5,3100,110),(.3,620,45)])
save("tick",x*(1-np.exp(-tt*3000)),0.55)
# pen: pencil on paper, short scratchy stroke
d=0.55;tt=t(d);n=hp(rng.standard_normal(len(tt)),2500)*(0.6+0.4*np.sin(2*np.pi*9*tt))
save("pen",lp(n,7000)*np.sin(np.pi*tt/d)**.8,0.35)
# chime: soft glass bell
d=2.2;tt=t(d);x=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for a,f,k in [(1,1046.5,2.2),(.6,1568,2.8),(.35,2093,3.5),(.15,3136,5)])
save("chime",x*(1-np.exp(-tt*200)),0.5)
# shimmer: rising airy sparkle for "3D to real"
d=1.0;tt=t(d);x=sum(np.sin(2*np.pi*f*(1+.5*tt/d)*tt)*np.exp(-((tt-.25-k*.12)/.18)**2) for k,f in enumerate([1760,2217,2637,3520]))
save("shimmer",x+0.3*hp(rng.standard_normal(len(tt)),6000)*np.sin(np.pi*tt/d)**3,0.35)
# swipe: quick page/photo slide
d=0.32;tt=t(d);sw=5000*np.exp(-tt*8)+800
save("swipe",hp(lp(rng.standard_normal(len(tt)),sw),400)*np.sin(np.pi*tt/d)**1.2,0.5)
# music bed: warm ambient pad, Fmaj9 - Am7 - Dm9 - Bbmaj7, 78 bpm feel, gentle plucks
dur=float(sys.argv[2]) if len(sys.argv)>2 else 32.3
N=int(SR*dur);tt=np.arange(N)/SR;L=np.zeros(N);R=np.zeros(N)
midi=lambda m:440*2**((m-69)/12)
chords=[[41,53,57,60,64,67],[45,52,55,60,64],[38,50,57,60,64],[46,53,57,62,65]];bar=60/78*4
for b in range(int(dur/bar)+1):
    s=int(b*bar*SR);e=min(N,int((b+1)*bar*SR+SR*1.5))
    if s>=N: break
    seg=tt[s:e]-tt[s];env=(1-np.exp(-seg/0.9))*np.exp(-np.maximum(0,seg-bar)/0.6)
    for j,m in enumerate(chords[b%4]):
        f=midi(m);ph=rng.random()*6.28
        v=(np.sin(2*np.pi*f*seg+ph)+.25*np.sin(2*np.pi*2*f*seg+ph))*env*(1.3 if j==0 else .55)
        L[s:e]+=v*(.6+.08*j);R[s:e]+=v*(1.0-.08*j)
    for k,m in enumerate([chords[b%4][-1]+12,chords[b%4][-2]+12,chords[b%4][-3]+12]):  # soft pluck arpeggio
        ps=s+int((k*bar/4+bar/8)*SR);pe=min(N,ps+int(SR*1.2))
        if ps>=N: continue
        sg=tt[ps:pe]-tt[ps];v=np.sin(2*np.pi*midi(m)*sg)*np.exp(-sg*4)*(1-np.exp(-sg*300))*.35
        (L if k%2 else R)[ps:pe]+=v
fade=np.minimum(1,tt/1.2)*np.minimum(1,(dur-tt)/1.8).clip(0,1)
L=lp(L,2200)*fade;R=lp(R,2200)*fade
save("music",None,0.5,np.stack([L,R],1))
print(sorted(os.listdir(out)))
