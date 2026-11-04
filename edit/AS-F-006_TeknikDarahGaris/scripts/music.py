# Gentle, positive family-friendly bed: soft pluck arpeggio + warm pad + light shaker. 96 BPM, C major.
import numpy as np, wave, sys
SR=44100; dur=float(sys.argv[2]); out=sys.argv[1]; rng=np.random.default_rng(3)
N=int(SR*dur); L=np.zeros(N); R=np.zeros(N)
bpm=96; beat=60/bpm; e8=beat/2
def note(f): return 440*2**((f-69)/12)
prog=[[60,64,67,72],[57,60,64,69],[53,57,60,65],[55,59,62,67]]  # C Am F G
bass=[36,33,29,31]
def add(buf,start,sig):
    i=int(start*SR); j=min(N,i+len(sig))
    if i<N: buf[i:j]+=sig[:j-i]
def pluck(f,d=0.9,a=0.18):
    t=np.arange(int(SR*d))/SR
    s=(np.sin(2*np.pi*f*t)+0.35*np.sin(4*np.pi*f*t)+0.12*np.sin(6*np.pi*f*t))*np.exp(-t*5.5)
    s[:200]*=np.linspace(0,1,200); return a*s
def pad(fs,d):
    t=np.arange(int(SR*d))/SR; s=np.zeros_like(t)
    for f in fs:
        for det in (-0.12,0.12): s+=np.sin(2*np.pi*note(f+det)*t)
    env=np.minimum(1,np.minimum(t/0.6,(d-t)/0.6)).clip(0,1)
    return 0.035*s*env
bar=4*beat; t0=0; k=0
patt=[0,2,1,3,2,1,3,2]
while t0<dur:
    ch=prog[k%4]
    p=pad(ch,bar+0.3); add(L,t0,p); add(R,t0,p)
    tb=np.arange(int(SR*bar))/SR; bs=0.10*np.sin(2*np.pi*note(bass[k%4])*tb)*np.exp(-tb*1.2); add(L,t0,bs); add(R,t0,bs)
    for i,pi in enumerate(patt):
        s=pluck(note(ch[pi]+12),a=0.11); pan=0.35 if i%2 else -0.35
        add(L,t0+i*e8,s*(1-pan)); add(R,t0+i*e8,s*(1+pan))
    for i in range(8):
        n=int(SR*0.06); sh=rng.standard_normal(n)*np.exp(-np.arange(n)/(SR*0.012))*(0.018 if i%2 else 0.01)
        sh=np.diff(sh,prepend=0); add(L,t0+i*e8,sh); add(R,t0+i*e8,sh)
    t0+=bar; k+=1
x=np.stack([L,R],1); fade=int(SR*2); x[-fade:]*=np.linspace(1,0,fade)[:,None]; x[:int(SR*0.5)]*=np.linspace(0,1,int(SR*0.5))[:,None]
x/=np.max(np.abs(x))+1e-9; x*=0.8
with wave.open(out,"w") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
