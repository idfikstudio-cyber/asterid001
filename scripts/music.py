# Muzik latar asal (dijana sendiri, bebas hak cipta): hangat, bersyukur, sesuai keluarga.
# Felt piano + petikan Karplus-Strong + pad lembut + bass + perkusi ringan. D major, I-V-vi-IV.
# usage: python3 music.py out.wav seconds [bpm]
import numpy as np, wave, sys
SR=44100; rng=np.random.default_rng(11)
dur=float(sys.argv[2]); bpm=float(sys.argv[3]) if len(sys.argv)>3 else 84
beat=60/bpm; bar=4*beat; N=int(SR*(dur+3)); L=np.zeros(N); R=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def add(x,t,pan=0.0,g=1.0):
    i=int(t*SR); x=x[:max(0,N-i)]
    L[i:i+len(x)]+=x*g*np.sqrt(0.5*(1-pan)); R[i:i+len(x)]+=x*g*np.sqrt(0.5*(1+pan))
def tt(d): return np.arange(int(SR*d))/SR
def piano(m,d=2.6,v=1.0):
    t=tt(d); f=hz(m)
    x=sum(a*np.sin(2*np.pi*f*k*t*(1+0.0004*k*k))*np.exp(-t*(1.6+1.1*k)) for k,a in [(1,1),(2,.42),(3,.18),(4,.08),(5,.04)])
    a=int(SR*0.006); x[:a]*=np.linspace(0,1,a); return x*v
def pluck(m,d=1.6,v=1.0):
    p=int(SR/hz(m)); buf=rng.uniform(-1,1,p); n=int(SR*d); y=np.zeros(n)
    for i in range(n):
        y[i]=buf[i%p]; buf[i%p]=0.996*0.5*(buf[i%p]+buf[(i+1)%p])
    return y*v
def pad(ms,d):
    t=tt(d); x=sum(np.sin(2*np.pi*hz(m)*t+0.3*np.sin(2*np.pi*0.21*t+j))+0.5*np.sin(2*np.pi*hz(m)*1.003*t) for j,m in enumerate(ms))
    e=np.minimum(1,np.minimum(t/0.9,(d-t)/0.9)).clip(0); return x*e/len(ms)
def bass(m,d):
    t=tt(d); x=np.sin(2*np.pi*hz(m)*t)+0.25*np.sin(4*np.pi*hz(m)*t)
    return x*np.exp(-t*1.3)*np.minimum(1,t/0.01)
def kick():
    t=tt(0.35); f=48+110*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def shaker():
    t=tt(0.09); x=rng.standard_normal(len(t)); x=np.diff(x,prepend=0); return x*np.exp(-t*55)*0.5
def snap():
    t=tt(0.18); x=rng.standard_normal(len(t)); x=x-np.convolve(x,np.ones(8)/8,"same"); return x*np.exp(-t*30)*0.6
# D major: I(D) V(A) vi(Bm) IV(G); root midi + chord tones
PROG=[(50,[62,66,69,74]),(45,[61,64,69,73]),(47,[62,66,71,74]),(43,[62,67,71,74])]
MEL=[[78,76,74,76],[76,73,69,73],[74,78,79,78],[74,71,74,76]]  # gentle top-line, from bar 9
nb=int(np.ceil(dur/bar))+1
for b in range(nb):
    t0=b*bar; root,ch=PROG[b%4]; sec=b//4   # section 0 = intro (lighter)
    add(pad([m-12 for m in ch[:3]],bar+0.9),t0,0,0.09)
    for k,m in enumerate(ch): add(piano(m,3.0,0.55 if k else 0.7),t0+0.012*k,(k-1.5)*0.25,0.33)
    add(piano(ch[1],1.6,0.45),t0+2*beat,0.2,0.22)
    if sec>=1:
        add(bass(root-12,bar*0.9),t0,0,0.42); add(bass(root-12,beat*1.8),t0+2.5*beat,0,0.22)
        for s in range(8):                      # pluck arpeggio, eighth notes
            m=ch[[0,2,1,3,2,1,3,2][s]]+12; add(pluck(m,1.2,0.5),t0+s*beat/2,0.45 if s%2 else -0.35,0.17)
        for k in (0,2): add(kick(),t0+k*beat,0,0.35)
        for k in (1,3): add(snap(),t0+k*beat,0.1,0.16)
        for s in range(8): add(shaker(),t0+s*beat/2+0.01,0.5,0.10 if s%2 else 0.06)
    if sec>=2:
        for k,m in enumerate(MEL[b%4]): add(piano(m,1.8,0.6),t0+k*beat,-0.15,0.2)
x=np.stack([L,R],1)[:int(SR*dur)]
# simple stereo room: two short delays
for d,g in [(0.031,0.22),(0.047,0.18),(0.083,0.12)]:
    k=int(SR*d); x[k:,0]+=x[:-k,1]*g; x[k:,1]+=x[:-k,0]*g
fi,fo=int(SR*1.5),int(SR*2.5); x[:fi]*=np.linspace(0,1,fi)[:,None]; x[-fo:]*=np.linspace(1,0,fo)[:,None]
x=x/np.max(np.abs(x))*0.89
with wave.open(sys.argv[1],"w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes())
