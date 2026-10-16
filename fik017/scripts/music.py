# Original royalty-free music bed: warm lo-fi house, 96 BPM, Fmaj7-Em7-Dm7-Cmaj7.
import numpy as np, wave, sys
SR=44100; BPM=96; beat=60/BPM; bar=4*beat; DUR=float(sys.argv[2]) if len(sys.argv)>2 else 64
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(3)
def add(x,t0,g=1.0,pan=0.0):
    i=int(t0*SR); 
    if i>=N: return
    x=x[:N-i]; L[i:i+len(x)]+=x*g*(1-pan)/1; R[i:i+len(x)]+=x*g*(1+pan)/1
def mt(d): return np.arange(int(SR*d))/SR
def hz(m): return 440*2**((m-69)/12)
def ep(m,d,vel=1):  # electric-piano: FM sine, bell attack, soft decay
    t=mt(d); f=hz(m); mod=np.sin(2*np.pi*f*t)*1.2*np.exp(-t*3)
    x=np.sin(2*np.pi*f*t+mod)*np.exp(-t*1.1)*np.minimum(1,t/0.004)
    x*=np.minimum(1,(d-t)/0.08); return x*vel
def pad(m,d):
    t=mt(d); f=hz(m); x=sum(np.sin(2*np.pi*f*dt*t+ph) for dt,ph in ((1,0),(1.004,1),(0.996,2)))/3
    a=np.minimum(1,t/0.6)*np.minimum(1,(d-t)/0.6); return x*a
def kick():
    t=mt(0.45); f=50+90*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
def hat(d=0.05):
    t=mt(d); n=rng.standard_normal(len(t)); n=np.diff(np.concatenate([[0],n])); return n*np.exp(-t*90)
def rim():
    t=mt(0.18); n=rng.standard_normal(len(t)); n=n-np.convolve(n,np.ones(8)/8,'same')
    return (0.6*n*np.exp(-t*40)+0.5*np.sin(2*np.pi*1800*t)*np.exp(-t*60))
def bass(m,d):
    t=mt(d); f=hz(m); x=np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t)
    return x*np.minimum(1,t/0.01)*np.minimum(1,(d-t)/0.05)*np.exp(-t*0.8)
chords=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]  # Fmaj7 Em7 Dm7 Cmaj7
roots=[41,40,38,36]
nbars=int(DUR/bar)+1
for b in range(nbars):
    t0=b*bar; c=chords[b%4]; r=roots[b%4]
    for m in c: add(pad(m+12,bar+0.3),t0,0.05,0.0)
    full = b>=2                       # bars 0-1: intro (pads + keys only)
    # keys: syncopated stabs
    for st in (0,1.5,2.5,3.5) if full else (0,2):
        for k,m in enumerate(c): add(ep(m+12,beat*1.2,0.9),t0+st*beat+k*0.006,0.085,(k-1.5)*0.15)
    if full:
        for q in range(4): add(kick(),t0+q*beat,0.55)
        for q in (1,3): add(rim(),t0+q*beat,0.18,0.2)
        for e in range(8): add(hat(0.04 if e%2 else 0.07),t0+e*beat/2+(0.018 if e%2 else 0),0.07 if e%2 else 0.045,-0.3)
        for st,dd in ((0,1.4),(1.5,0.9),(2.5,0.4),(3,0.9)): add(bass(r if st!=3 else r+7,beat*dd),t0+st*beat,0.32)
    # simple melodic hook every 2nd bar after bar 4
    if b>=4 and b%2==0:
        mel=[c[3]+24,c[2]+24,c[3]+24,c[1]+24+2]
        for k,m in enumerate(mel): add(ep(m,beat*0.9,0.7),t0+(0.5+k*0.75)*beat,0.05,0.25)
# gentle tape-ish lowpass (moving average) + glue
def smooth(x,k=3): return np.convolve(x,np.ones(k)/k,'same')
L=smooth(L);R=smooth(R)
fo=int(SR*2.5); env=np.ones(N); env[-fo:]=np.linspace(1,0,fo); env[:int(SR*0.3)]=np.linspace(0,1,int(SR*0.3))
L*=env;R*=env
pk=max(np.abs(L).max(),np.abs(R).max()); L=np.tanh(L/pk*1.3)/np.tanh(1.3)*0.8; R=np.tanh(R/pk*1.3)/np.tanh(1.3)*0.8
x=np.stack([L,R],1)
with wave.open(sys.argv[1],"w") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
print("bar",bar,"s; bars",nbars)
