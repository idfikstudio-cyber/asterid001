# extra SFX for the Adudu edits (same synth helpers as sfx.py)
import numpy as np,os,sys
sys.argv=[sys.argv[0],sys.argv[1]];exec(open(os.path.join(os.path.dirname(__file__),"sfx.py")).read().split("# whoosh")[0])
# scribble: marker on whiteboard, band-passed noise with stroke rhythm
d=1.2;tt=t(d);nz=rng.standard_normal(len(tt))
strokes=0.55+0.45*np.sin(2*np.pi*7.5*tt+np.sin(2*np.pi*1.3*tt)*2)**2
x=hp(lp(nz,3200),900)*strokes*np.minimum(1,tt/0.03)*np.minimum(1,(d-tt)/0.08)
save("scribble.wav",x,0.45)
# balloon pop: sharp broadband burst + low thump
d=0.35;tt=t(d);x=hp(rng.standard_normal(len(tt)),1200)*np.exp(-tt*55)+0.6*np.sin(2*np.pi*(110*np.exp(-tt*12)+50)*tt)*np.exp(-tt*18)
save("balloonpop.wav",x,0.9)
# correct: rising two-note chime (E6 -> B6)
d=0.9;tt=t(d);x=np.zeros(len(tt))
for st,f in ((0,1318.5),(0.11,1975.5)):
    i=int(st*SR);tb=tt[:len(tt)-i];x[i:]+=sum(a*np.sin(2*np.pi*f*r*tb)*np.exp(-tb*k) for a,r,k in [(1,1,5),(0.3,2,8),(0.12,3,12)])
save("correct.wav",x,0.55)
# zap: playful laser for "serang"
d=0.45;tt=t(d);f=1800*np.exp(-tt*9)+180
x=(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*0.5+np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-tt*6)
x=lp(x,5000)
save("zap.wav",x,0.5)
# boop: soft UI blip for checklist items
d=0.18;tt=t(d);x=np.sin(2*np.pi*(660+440*np.minimum(1,tt/0.05))*tt)*env(len(tt),0.003,0.05)
save("boop.wav",x,0.55)
print(sorted(os.listdir(out)))
