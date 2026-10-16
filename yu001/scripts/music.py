# Original music bed for YU001 (generated, no third-party samples). Two sections:
# A 0-16.2s "masalah": muted pad + soft keys (Am F C G); dropout at 16.2 for "JAIS nak tengok";
# B 17.38s->end "penyelesaian": brighter keys, kick + shaker (F G Em Am .. F C).
import numpy as np,wave,sys
SR=44100;T=29.0;N=int(SR*T);L=np.zeros(N);Rr=np.zeros(N);rng=np.random.default_rng(3)
def mtof(m):return 440*2**((m-69)/12)
def add(x,t0,pan=0.0,g=1.0):
    i=int(t0*SR);x=x[:max(0,N-i)];L[i:i+len(x)]+=x*g*(1-pan)/1.0;Rr[i:i+len(x)]+=x*g*(1+pan)/1.0
def keys(m,d,v=1.0,bright=1.0):  # soft electric-piano-ish tone
    t=np.arange(int(SR*(d+1.2)))/SR;f=mtof(m)
    mod=np.sin(2*np.pi*f*t)*1.2*bright*np.exp(-t*3)
    x=np.sin(2*np.pi*f*t+mod)*np.exp(-t*1.6)+0.25*np.sin(4*np.pi*f*t)*np.exp(-t*4)
    a=np.minimum(1,t/0.006);rel=np.where(t>d,np.exp(-(t-d)*6),1)
    return x*a*rel*v
def pad(ms,d,cut):
    t=np.arange(int(SR*d))/SR;x=0
    for m in ms:
        for det in (-0.08,0.08):
            ph=np.cumsum(np.full(len(t),mtof(m)*2**(det/12)))/SR
            x=x+sum(np.sin(2*np.pi*k*ph)/k*np.exp(-k*900/cut) for k in range(1,6))
    env=np.minimum(1,t/0.6)*np.minimum(1,(d-t)/0.6)
    return x*env/len(ms)/2
def kick():
    t=np.arange(int(SR*0.35))/SR;f=110*np.exp(-t*25)+48
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def shaker():
    t=np.arange(int(SR*0.08))/SR;n=rng.standard_normal(len(t));n=n-np.convolve(n,np.ones(8)/8,'same')
    return n*np.exp(-t*60)*np.minimum(1,t/0.01)
CH={"Am":[57,60,64,67],"F":[53,57,60,64],"C":[48,55,60,64],"G":[55,59,62,67],"Em":[52,55,59,62],"Fmaj7":[53,57,60,64],"Dm":[50,57,60,65]}
BASS={"Am":45,"F":41,"C":48,"G":43,"Em":40,"Fmaj7":41,"Dm":38}
bpm=92;b=60/bpm;bar=4*b
# Section A
t=0.0
for c in ["Am","F","C","G","Am","F","C"]:
    if t>=16.2:break
    d=min(bar,16.2-t)
    add(pad(CH[c],d+0.4,1400),t,0,0.10)
    for k,m in enumerate([CH[c][0]+12,CH[c][2]+12,CH[c][1]+12,CH[c][3]+12,CH[c][2]+12,CH[c][1]+12,CH[c][2]+12,CH[c][3]+12]):
        if t+k*b/2<16.0:add(keys(m,b/2,0.11,0.6),t+k*b/2,(-0.3 if k%2 else 0.3))
    add(keys(BASS[c],d,0.18,0.2),t);t+=bar
# small reverse swell into B
sw=np.linspace(0,1,int(SR*0.9))**3*pad([60,64,67],0.9,3000)[:int(SR*0.9)];add(sw,17.38-0.9,0,0.25)
# Section B
t=17.38
prog=["F","G","Em","Am","F","C"]
for i,c in enumerate(prog):
    if t>=T:break
    d=bar if i<len(prog)-1 else T-t
    add(pad(CH[c],d+0.4,2600),t,0,0.11)
    for k in range(8):
        tk=t+k*b/2
        if tk>=27.95:break
        m=CH[c][[0,2,1,3,2,1,3,2][k]]+12
        add(keys(m,b/2,0.13,1.0),tk,(-0.35 if k%2 else 0.35))
    add(keys(BASS[c],d,0.22,0.3),t)
    for k in range(4):
        tk=t+k*b
        if tk>=27.95:break
        if k in (0,2):add(kick(),tk,0,0.35)
        add(shaker(),tk+b/2,0.2,0.08);add(shaker(),tk+b*0.75,-0.2,0.04)
    t+=bar
# final chord ring-out on "sistematik"
add(keys(60,1.5,0.12)+keys(64,1.5,0.1)+keys(67,1.5,0.1),27.0)
x=np.stack([L,Rr],1);x=np.tanh(x*1.3)/1.3
# simple reverb: few diffused delays
for dl,g in ((0.031,.25),(0.047,.2),(0.071,.15),(0.113,.1)):
    k=int(dl*SR);x[k:]+=g*x[:-k]
fade=np.ones(N);fo=int(SR*1.2);fade[-fo:]=np.linspace(1,0,fo);x*=fade[:,None]
x=x/np.abs(x).max()*0.8
with wave.open(sys.argv[1],"w") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
