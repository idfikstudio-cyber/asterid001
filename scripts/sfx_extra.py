# extra sound effects for AT001 (pen writing, lock, tick-mark, sparkle); same synth helpers as sfx.py
import numpy as np,os,sys
sys.argv=[sys.argv[0],sys.argv[1]]
exec(open(os.path.join(os.path.dirname(__file__),"sfx.py")).read().split("# whoosh:")[0])
# scribble: pen on paper, bandpassed noise with stroke rhythm
d=0.7;tt=t(d);nz=rng.standard_normal(len(tt))
strokes=np.clip(np.sin(2*np.pi*7.5*tt+2*np.sin(2*np.pi*1.3*tt)),0,1)**.6
x=hp(lp(nz,5200),1800)*strokes*np.sin(np.pi*tt/d)**.5
save("scribble.wav",x,0.5)
# lock: two metallic clacks
d=0.35;tt=t(d);x=np.zeros(len(tt))
for st,f in ((0.0,2600),(0.11,1900)):
    i=int(st*SR);m=int(0.06*SR);tm=tt[:m]
    x[i:i+m]+=(np.sin(2*np.pi*f*tm)+.6*np.sin(2*np.pi*f*2.3*tm))*np.exp(-tm*90)+.5*hp(rng.standard_normal(m),3000)*np.exp(-tm*200)
save("lock.wav",x,0.65)
# check: quick rising two-note chime
d=0.45;tt=t(d);x=np.zeros(len(tt))
for st,f in ((0.0,1046),(0.08,1568)):
    i=int(st*SR);tb=tt[:len(tt)-i];x[i:]+=np.sin(2*np.pi*f*tb)*np.exp(-tb*9)*env(len(tb),0.002,1)
save("check.wav",x,0.55)
# sparkle: random high pings
d=1.0;tt=t(d);x=np.zeros(len(tt))
for k in range(9):
    st=k*0.07+rng.uniform(0,.03);f=rng.uniform(2500,5200);i=int(st*SR);tb=tt[:len(tt)-i]
    x[i:]+=np.sin(2*np.pi*f*tb)*np.exp(-tb*14)*(1-k/12)
save("sparkle.wav",x,0.5)
print(sorted(os.listdir(out)))
