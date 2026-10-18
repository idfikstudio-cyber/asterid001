# Extra synthesized SFX for Sifir 9 (pencil, marker, quiz). Same helpers as scripts/sfx.py.
import numpy as np, wave, sys, os
SR=44100; out=sys.argv[1]; rng=np.random.default_rng(9)
def t(d): return np.arange(int(SR*d))/SR
def lp(x,c):
    c=np.broadcast_to(np.asarray(c,float),x.shape); y=np.zeros_like(x); s=0.0
    k=1-np.exp(-2*np.pi*c/SR)
    for i in range(len(x)): s+=k[i]*(x[i]-s); y[i]=s
    return y
def hp(x,c): return x-lp(x,c)
def save(name,x,g=0.9):
    x=x/(np.max(np.abs(x))+1e-9)*g; x=np.stack([x,x],1)
    with wave.open(os.path.join(out,name),"w") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
def strokes(d,n,seed):  # pencil on glass/paper: grainy noise in short strokes
    r=np.random.default_rng(seed); tt=t(d); x=np.zeros(len(tt))
    for k in range(n):
        st=r.uniform(0,d*0.8); ln=r.uniform(0.05,0.16); i=int(st*SR); m=min(int(ln*SR),len(x)-i)
        g=hp(lp(r.standard_normal(m),r.uniform(3500,6500)),1500)
        g*=np.sin(np.pi*np.arange(m)/m)**0.6*(0.6+0.4*np.abs(np.sin(np.arange(m)/SR*2*np.pi*r.uniform(9,16))))
        x[i:i+m]+=g
    return x
save("scribble.wav",strokes(1.6,9,1),0.5)
save("scribble_s.wav",strokes(0.4,2,2),0.5)
# marker: one long squeaky swipe
d=0.5;tt=t(d);sw=np.sin(np.pi*tt/d)
x=hp(lp(rng.standard_normal(len(tt)),2500+1500*tt/d),700)*sw+0.15*np.sin(2*np.pi*(1800+600*tt/d)*tt)*sw
save("marker.wav",x,0.6)
# swoosh up (mirror of swoosh_down)
d=0.55;tt=t(d);sweep=300+3800*(tt/d)**2
x=hp(lp(rng.standard_normal(len(tt)),sweep),200)*np.sin(np.pi*tt/d)
save("swoosh_up.wav",x,0.6)
# single countdown tick (woodblock)
d=0.18;tt=t(d);x=np.sin(2*np.pi*1100*tt)*np.exp(-tt*45)+0.5*np.sin(2*np.pi*1750*tt)*np.exp(-tt*60)
save("tick1.wav",x,0.7)
# correct answer: rising major arpeggio chime
d=0.9;tt=t(d);x=np.zeros(len(tt))
for k,f in enumerate([1046.5,1318.5,1568,2093]):
    i=int(k*0.07*SR);tb=tt[:len(tt)-i];x[i:]+=np.sin(2*np.pi*f*tb)*np.exp(-tb*5)*(0.8 if k<3 else 1)
save("correct.wav",x,0.7)
print(sorted(os.listdir(out)))
