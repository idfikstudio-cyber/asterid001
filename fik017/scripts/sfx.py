import numpy as np, wave, sys, os
SR=44100; out=sys.argv[1]; rng=np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def env(n,a,r):
    e=np.ones(n); A=int(SR*a); e[:A]=np.linspace(0,1,A) if A else 1
    e[A:]=np.exp(-np.arange(n-A)/(SR*r)); return e
def lp(x,c):  # one-pole lowpass, c can be array (Hz)
    c=np.broadcast_to(np.asarray(c,float),x.shape); y=np.zeros_like(x); s=0.0
    k=1-np.exp(-2*np.pi*c/SR)
    for i in range(len(x)): s+=k[i]*(x[i]-s); y[i]=s
    return y
def hp(x,c): return x-lp(x,c)
def save(name,x,g=0.9):
    x=x/ (np.max(np.abs(x))+1e-9)*g; x=np.stack([x,x],1)
    with wave.open(os.path.join(out,name),"w") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
# whoosh: band-swept noise, swell then fade
d=0.5;n=int(SR*d);tt=t(d);nz=rng.standard_normal(n)
sweep=300+3200*np.sin(np.pi*tt/d)**2
x=hp(lp(nz,sweep),sweep*0.35)*np.sin(np.pi*tt/d)**1.5
save("whoosh.wav",x,0.7)
# pop: pitch-dropping sine blip
d=0.14;tt=t(d);f=900*np.exp(-tt*28)+260
x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(tt),0.002,0.035)
save("pop.wav",x,0.8)
# ding: bell partials
d=1.4;tt=t(d);x=sum(a*np.sin(2*np.pi*1320*r*tt)*np.exp(-tt*k) for a,r,k in [(1,1,3.2),(0.5,2.76,5),(0.25,5.4,8),(0.15,8.9,12)])
x*=env(len(tt),0.002,10)
save("ding.wav",x,0.6)
# chaching: two metallic clicks then bright bell
d=1.3;tt=t(d);x=np.zeros(len(tt))
for st in (0.0,0.07):
    i=int(st*SR);k=int(0.03*SR);x[i:i+k]+=hp(rng.standard_normal(k),3000)*np.exp(-np.arange(k)/(SR*0.006))
i=int(0.14*SR);tb=tt[:len(tt)-i]
bell=sum(a*np.sin(2*np.pi*f*tb)*np.exp(-tb*k) for a,f,k in [(1,2093,3.5),(0.7,2637,4),(0.5,3136,4.5),(0.2,6272,9)])
x[i:]+=0.55*bell
save("chaching.wav",x,0.75)
# riser: noise + rising tone, ends abruptly
d=1.6;tt=t(d);f=180*2**(tt/d*3)
x=0.5*np.sin(2*np.pi*np.cumsum(f)/SR)+0.6*hp(lp(rng.standard_normal(len(tt)),400+5000*(tt/d)**2),200)
x*=(tt/d)**2
save("riser.wav",x,0.55)
# impact: sub boom + noise crack
d=0.9;tt=t(d);f=90*np.exp(-tt*6)+42
x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*4.5)+0.35*lp(rng.standard_normal(len(tt)),1800)*np.exp(-tt*30)
save("impact.wav",x,0.9)
# click: UI tap
d=0.06;tt=t(d);x=np.sin(2*np.pi*2400*tt)*np.exp(-tt*120)+0.4*hp(rng.standard_normal(len(tt)),4000)*np.exp(-tt*300)
save("click.wav",x,0.6)
# tick: clock tick x3
d=0.9;tt=t(d);x=np.zeros(len(tt))
for k in range(3):
    i=int(k*0.3*SR);m=int(0.025*SR);x[i:i+m]+=np.sin(2*np.pi*3200*tt[:m])*np.exp(-tt[:m]*250)
save("tick.wav",x,0.5)
# bonk: soft "wrong" thud
d=0.35;tt=t(d);f=220*np.exp(-tt*5)+120
x=(np.sin(2*np.pi*np.cumsum(f)/SR)+0.3*np.sin(4*np.pi*np.cumsum(f)/SR))*env(len(tt),0.003,0.09)
save("bonk.wav",x,0.7)
# swoosh down (for "risiko turun")
d=0.55;tt=t(d);sweep=4000*np.exp(-tt*6)+300
x=hp(lp(rng.standard_normal(len(tt)),sweep),200)*np.sin(np.pi*tt/d)
save("swoosh_down.wav",x,0.6)
print(sorted(os.listdir(out)))
# --- interior set ---
# shimmer: sparkle arpeggio for "after" reveals
d=1.6;tt=t(d);x=np.zeros(len(tt))
for k,f in enumerate([1568,1976,2349,2637,3136,3951]):
    i=int(k*0.055*SR);tb=tt[:len(tt)-i]
    x[i:]+=np.sin(2*np.pi*f*tb)*np.exp(-tb*5)*(0.9-k*0.08)
x+=0.15*hp(rng.standard_normal(len(tt)),6000)*np.exp(-tt*4)
save("shimmer.wav",x,0.55)
# shutter: camera click-clack
d=0.25;tt=t(d);x=np.zeros(len(tt))
for st,g in ((0,1),(0.07,0.7)):
    i=int(st*SR);k=int(0.04*SR);x[i:i+k]+=g*hp(rng.standard_normal(k),1500)*np.exp(-np.arange(k)/(SR*0.008))
save("shutter.wav",x,0.7)
# swipe: short airy pass for slider/transition
d=0.32;tt=t(d);sweep=800+5000*(tt/d)
x=hp(lp(rng.standard_normal(len(tt)),sweep),600)*np.sin(np.pi*tt/d)**2
save("swipe.wav",x,0.55)
# thud: soft wooden knock for labels
d=0.25;tt=t(d);f=160*np.exp(-tt*12)+90
x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*18)+0.2*lp(rng.standard_normal(len(tt)),900)*np.exp(-tt*60)
save("thud.wav",x,0.8)
print("interior set ok")
