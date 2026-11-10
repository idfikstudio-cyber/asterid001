# Muzik latar asal: ceria ringan, marimba + pad + bass + perkusi lembut, C major 100 BPM
import numpy as np,wave,sys
SR=48000;BPM=100;beat=60/BPM;DUR=30.0;N=int(SR*DUR);rng=np.random.default_rng(3)
out=np.zeros((N,2))
def mtof(m):return 440*2**((m-69)/12)
def add(x,t0,pan=0.5,g=1.0):
  i=int(t0*SR);x=x[:max(0,N-i)];out[i:i+len(x),0]+=x*g*(1-pan)*2**.5;out[i:i+len(x),1]+=x*g*pan*2**.5
def marimba(m,d=0.6):
  t=np.arange(int(SR*d))/SR;f=mtof(m)
  return (np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*4*f*t)*np.exp(-t*30))*np.exp(-t*7)*(1-np.exp(-t*800))
def pad(ms,d):
  t=np.arange(int(SR*d))/SR;x=sum(np.sin(2*np.pi*mtof(m)*t+0.3*np.sin(2*np.pi*0.3*t))+0.4*np.sin(2*np.pi*mtof(m)*1.003*t) for m in ms)
  env=np.minimum(1,t/0.4)*np.minimum(1,(d-t)/0.4);return x*env/len(ms)
def bass(m,d):
  t=np.arange(int(SR*d))/SR;f=mtof(m);return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*2.5)*(1-np.exp(-t*300))
def kick():
  t=np.arange(int(SR*0.3))/SR;f=55+90*np.exp(-t*30);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)
def shaker():
  t=np.arange(int(SR*0.08))/SR;x=rng.standard_normal(len(t));x=np.diff(x,prepend=0);return x*np.exp(-t*60)
def clap():
  t=np.arange(int(SR*0.2))/SR;x=rng.standard_normal(len(t));x=np.diff(x,prepend=0);return x*np.exp(-t*25)
# C G Am F (I V vi IV), 1 bar = 4 beats
CH=[(60,[48,60,64,67],[60,64,67,72]),(55,[43,59,62,67],[59,62,67,71]),(57,[45,57,60,64],[57,60,64,69]),(53,[41,57,60,65],[57,60,65,69])]
bar=4*beat;t=0;b=0
while t<DUR:
  root,pv,arp=CH[b%4]
  add(pad(pv[1:],bar),t,0.5,0.18)
  add(bass(pv[0],bar*0.5),t,0.5,0.35);add(bass(pv[0],bar*0.5),t+bar*0.5,0.5,0.28)
  pat=[0,1,2,3,2,1,3,2] if b%2==0 else [0,2,1,3,0,2,3,1]
  for k in range(8):
    add(marimba(arp[pat[k]]+12*(k==6)),t+k*beat/2,0.35+0.3*(k%2),0.22 if k%2==0 else 0.16)
  for k in range(4):
    add(kick(),t+k*beat,0.5,0.25 if k in(0,2) else 0.0)
    if k in(1,3): add(clap(),t+k*beat,0.55,0.06)
    for h in range(2): add(shaker(),t+k*beat+h*beat/2,0.65,0.05 if h else 0.03)
  t+=bar;b+=1
# light reverb (multi-tap)
rv=np.zeros_like(out)
for d,g in [(0.031,0.25),(0.047,0.2),(0.071,0.15),(0.113,0.1),(0.17,0.07)]:
  i=int(d*SR);rv[i:,0]+=out[:-i,1]*g;rv[i:,1]+=out[:-i,0]*g
out+=rv;out/=np.max(np.abs(out))*1.12
with wave.open(sys.argv[1],"w") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes())
