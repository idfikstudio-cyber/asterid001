# Muzik latar korporat ringan, dijana sendiri (bebas hak cipta).
# usage: python3 music.py out.wav duration_s [bpm] [seed]
# Rhodes-ish keys + pluck arpeggio + soft pad + bass + light kick/shaker. Intro (keys+pad), groove masuk bar 5.
import numpy as np, wave, sys
SR=44100
out=sys.argv[1]; DUR=float(sys.argv[2]); BPM=float(sys.argv[3]) if len(sys.argv)>3 else 100; rng=np.random.default_rng(int(sys.argv[4]) if len(sys.argv)>4 else 3)
beat=60/BPM; bar=4*beat; N=int(SR*(DUR+2)); L=np.zeros(N); R=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def add(x,t0,pan=0.0,g=1.0):
    i=int(t0*SR); x=x[:max(0,N-i)]
    L[i:i+len(x)]+=x*g*np.sqrt(0.5*(1-pan)); R[i:i+len(x)]+=x*g*np.sqrt(0.5*(1+pan))
def keys(m,d):
    t=np.arange(int(SR*(d+0.8)))/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t+0.6*np.exp(-t*3)*np.sin(2*np.pi*f*t))+0.25*np.sin(4*np.pi*f*t)*np.exp(-t*4)
    e=np.minimum(1,t/0.004)*np.exp(-t*1.6); rel=np.clip((d+0.8-t)/0.8,0,1)
    return x*e*rel*(1+0.15*np.sin(2*np.pi*4.5*t))
def pluck(m,d=0.45):
    t=np.arange(int(SR*d))/SR; f=hz(m)
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(6*np.pi*f*t)*np.exp(-t*20))*np.exp(-t*9)*np.minimum(1,t/0.002)
def pad(ms,d):
    t=np.arange(int(SR*d))/SR; x=0
    for m in ms:
        for det in (-0.08,0.08): x=x+np.sin(2*np.pi*hz(m+det)*t)+0.2*np.sin(4*np.pi*hz(m+det)*t)
    a=np.clip(t/0.9,0,1)*np.clip((d-t)/0.9,0,1); return x*a/len(ms)
def bass(m,d):
    t=np.arange(int(SR*d))/SR; f=hz(m)
    return (np.sin(2*np.pi*f*t)+0.15*np.sin(4*np.pi*f*t))*np.minimum(1,t/0.01)*np.exp(-t*1.2)*np.clip((d-t)/0.05,0,1)
def kick():
    t=np.arange(int(SR*0.35))/SR; f=48+70*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def shaker():
    n=int(SR*0.07); x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(6)/6,"same")
    return x*np.exp(-np.arange(n)/(SR*0.018))
# progression C - Am - F - G (add9 voicings), I-vi-IV-V: cerah, tenang, profesional
PROG=[(48,[60,64,67,74]),(45,[60,64,69,71]),(41,[60,65,69,72]),(43,[62,67,71,74])]
nb=int(np.ceil(DUR/bar))+1
K=kick(); S=shaker()
for b in range(nb):
    t0=b*bar; root,ch=PROG[b%4]
    add(pad([n-12 for n in ch[:3]],bar+0.9),t0,0,0.10)
    for k,hit in enumerate((0,1.5,2.5) if b>=2 else (0,)):
        for j,n in enumerate(ch[:3]): add(keys(n,beat*0.9),t0+hit*beat+j*0.012,(-0.25,0,0.25)[j],0.07)
    if b>=4:
        add(bass(root,beat*1.4),t0,0,0.30); add(bass(root,beat*0.9),t0+2*beat,0,0.22); add(bass(root+7 if b%2 else root+12,beat*0.9),t0+3*beat,0,0.18)
        for q in range(4): add(K,t0+q*beat,0,0.32 if q%2==0 else 0.18)
        for e in range(8): add(S,t0+e*beat/2,0.35,0.05 if e%2 else 0.025)
    if b>=8 and b%8 not in (7,):
        arp=[ch[0]+12,ch[2]+12,ch[1]+12,ch[3]+12,ch[2]+12,ch[1]+12,ch[3],ch[2]+12]
        for e,n in enumerate(arp): add(pluck(n),t0+e*beat/2,(-0.4,0.4)[e%2],0.045)
mix=np.stack([L,R],1)[:int(SR*DUR)]
# fade in 1.5 s, fade out 2.5 s
n=len(mix); fi=int(SR*1.5); fo=int(SR*2.5)
mix[:fi]*=np.linspace(0,1,fi)[:,None]; mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=mix/np.max(np.abs(mix))*0.8
with wave.open(out,"w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print("ok",DUR,"s",BPM,"bpm")
