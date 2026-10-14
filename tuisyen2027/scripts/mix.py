# Jana muzik latar (bebas hak cipta) + letak SFX + duck bawah suara.  python3 mix.py voice.wav sfxdir out.wav
import numpy as np, wave, sys
SR=48000; DUR=14.4; N=int(SR*DUR); rng=np.random.default_rng(3)
def rd(p):
    w=wave.open(p); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    a=a.reshape(-1,w.getnchannels()).mean(1)
    if sr!=SR: a=np.interp(np.arange(int(len(a)*SR/sr))*sr/SR,np.arange(len(a)),a)
    return a
voice=rd(sys.argv[1]); V=np.zeros(N); V[:len(voice)]=voice[:N]
# ---- muzik: 120bpm, C - G - Am - F ----
bpm=120; beat=60/bpm; t=np.arange(N)/SR; M=np.zeros(N)
def note(f,st,d,a=1,kind="pluck"):
    i=int(st*SR); n=min(int(d*SR),N-i)
    if n<=0: return
    tt=np.arange(n)/SR
    if kind=="pluck": x=(np.sin(2*np.pi*f*tt)+.3*np.sin(4*np.pi*f*tt)+.12*np.sin(6*np.pi*f*tt))*np.exp(-tt*7)
    elif kind=="bass": x=np.tanh(1.5*np.sin(2*np.pi*f*tt))*np.exp(-tt*2.2)
    elif kind=="pad": x=np.sin(2*np.pi*f*tt)*np.minimum(1,tt/.3)*np.minimum(1,(d-tt)/.3)
    M[i:i+n]+=a*x*np.minimum(1,np.arange(n)/48)
chords=[(261.63,329.63,392.0),(246.94,293.66,392.0),(220.0,261.63,329.63),(220.0,261.63,349.23)]
roots=[65.41,98.0,110.0,87.31]
bar=4*beat
for b in range(int(DUR/bar)+1):
    c=chords[b%4]; s0=b*bar
    for f in c: note(f/2,s0,bar,.10,"pad")
    for k in range(8):  # 8th-note arpeggio
        note(c[[0,1,2,1,0,2,1,2][k]]*2,s0+k*beat/2,beat/2*1.6,.16)
    for k in (0,1.5,2,3.5): note(roots[b%4],s0+k*beat,beat*1.2,.35,"bass")
    for k in range(4):  # kick + hat + clap
        i=int((s0+k*beat)*SR); n=min(int(.25*SR),N-i)
        if n>0:
            tt=np.arange(n)/SR; M[i:i+n]+=.55*np.sin(2*np.pi*np.cumsum(50+90*np.exp(-tt*30))/SR)*np.exp(-tt*9)
        i2=int((s0+k*beat+beat/2)*SR); n=min(int(.05*SR),N-i2)
        if n>0: M[i2:i2+n]+=.07*np.diff(np.r_[0,rng.standard_normal(n)])*np.exp(-np.arange(n)/SR*90)
        if k%2:
            n=min(int(.15*SR),N-i)
            if n>0: M[i:i+n]+=.14*rng.standard_normal(n)*np.exp(-np.arange(n)/SR*28)
M/=np.abs(M).max()
# ducking: envelope suara
env=np.convolve(np.abs(V),np.ones(int(.08*SR))/int(.08*SR),"same")
duck=np.clip(env/0.05,0,1); duck=np.convolve(duck,np.ones(int(.25*SR))/int(.25*SR),"same")
mg=10**(-21/20)*(1-.55*duck)
end=12.56; mg=np.where(t>end,mix:=10**(-12/20),mg); mg*=np.minimum(1,t/.4)*np.clip((DUR-t)/1.0,0,1)
mg=np.convolve(mg,np.ones(2400)/2400,"same")
out=V+M*mg
# ---- SFX ----
SFX=[(0.04,"pop",.5),(0.20,"impact",.75),(0.52,"whoosh",.5),(0.30,"pop",.4),
 (1.48,"whoosh",.6),(1.95,"pop",.45),(2.25,"pop",.45),(2.55,"pop",.4),(2.95,"click",.5),(3.50,"whoosh",.5),
 (4.02,"pop",.55),(4.66,"click",.45),(4.90,"click",.45),(5.28,"click",.45),(5.58,"click",.45),(5.94,"click",.45),
 (6.40,"whoosh",.6),(6.90,"chaching",.6),(8.88,"swoosh_down",.45),(9.20,"whoosh",.55),(9.90,"ding",.4),
 (11.00,"click",.6),(11.30,"pop",.35),(11.25,"riser",.35),(12.52,"impact",.6),(12.50,"whoosh",.5),
 (12.80,"pop",.3),(12.94,"pop",.3),(13.08,"pop",.3),(13.22,"pop",.3),(13.36,"pop",.3),(13.80,"ding",.35)]
for st,nm,g in SFX:
    x=rd(f"{sys.argv[2]}/{nm}.wav")*g*.8; i=int(st*SR); n=min(len(x),N-i); out[i:i+n]+=x[:n]
out=np.tanh(out*1.05)/np.tanh(1.05)*.95
with wave.open(sys.argv[3],"w") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.stack([out,out],1)*32767).astype(np.int16).tobytes())
print("ok",out.max())
