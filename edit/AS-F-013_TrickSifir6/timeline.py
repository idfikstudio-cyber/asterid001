"""AS-F-013 Trick Sifir 6: garis masa bersama (EDL, fasa bulatan, pemetaan papan B-roll)."""
import numpy as np
THUMB=1.0; END=1.5
EDL=[(0.00,19.56),(19.80,21.04),(22.02,76.16)]   # buang "Prosesnya adalah," (tersilap mula) + senyap 0.24 s
THUMB_SRC=62.2
CONTENT=sum(b-a for a,b in EDL); DUR=THUMB+CONTENT+END
def o2s(t):
    """masa video -> masa sumber (None = thumbnail/end card)"""
    if t<THUMB: return None
    x=t-THUMB
    for a,b in EDL:
        if x<b-a: return a+x
        x-=b-a
    return None
def s2o(s):
    acc=THUMB
    for a,b in EDL:
        if s<a: return acc
        if s<=b: return acc+s-a
        acc+=b-a
    return acc
# fasa: 0 = bulatan besar, 1 = papan + bulatan kecil
TEACH=(11.60,55.00); TR=0.45
def phase(src):
    if src is None: return 0.0
    a,b=TEACH
    def ss(x): x=min(max(x,0),1); return x*x*(3-2*x)
    return ss((src-a)/TR)*(1-ss((src-b)/TR))
BIG=(540,770,640); SMALL=(540,1432,280)
def circle(src):
    p=phase(src); return tuple(BIG[i]+(SMALL[i]-BIG[i])*p for i in range(3))
# punch-in ikut ayat (selang-seli 100% / 113%)
SENT=[0,3.48,9.5,11.68,15.86,19.9,22.02,30.0,34.18,42.52,44.58,54.1,55.04,56.26,58.68,60.58,68.1,72.92]
def zoom(src):
    if src is None: return 1.0
    i=max(k for k,s in enumerate(SENT) if src>=s-0.05); return 1.13 if i%2 else 1.0
# papan B-roll: masa sumber -> masa B-roll (tulisan ikut nombor yang disebut)
NW=[(23.32,23.58),(23.74,24.30),(24.52,24.94),(25.24,25.90),(26.18,26.64),(26.88,27.12),(27.24,27.78),(27.90,28.36),(28.56,28.96),(29.14,29.60)]
ND=[2.2,3.1,3.9,4.9,5.8,6.3,7.2,7.9,8.7,9.6]
KW=[(34.18,34.38),(34.60,34.90),(35.32,35.64),(36.10,36.46),(36.90,37.54),(37.94,38.62),(39.04,39.74),(40.16,40.68),(40.98,41.58),(41.78,42.18)]
KD=[26.3,27.5,28.4,29.8,31.0,32.2,33.3,34.6,35.6,37.5]
RW=[(45.54,45.88),(45.98,46.26),(46.94,47.34),(47.92,48.32),(48.88,49.08),(49.62,50.12),(50.48,50.88),(51.22,52.06),(52.34,53.06),(53.14,53.86)]
RD=[43.2,45.3,48.4,51.1,54.1,55.7,59.2,62.6,67.1,72.5]
KP=[(0,1.0),(23.0,1.0)]
for (s,e),d in zip(NW,ND): KP+=[(s,d-0.45),(e,d)]
KP+=[(34.0,9.6),(34.01,25.0)]
for (s,e),d in zip(KW,KD): KP+=[(s,d-0.8),(e,d)]
KP+=[(45.3,37.5),(45.31,42.5)]
for (s,e),d in zip(RW,RD): KP+=[(s,d-1.0),(e,d)]
KP+=[(54.2,74.0),(80,74.0)]
for i in range(1,len(KP)): KP[i]=(KP[i][0],max(KP[i][1],KP[i-1][1]))
_kx=np.array([k[0] for k in KP]);_ky=np.array([k[1] for k in KP])
assert (np.diff(_kx)>0).all() and (np.diff(_ky)>=0).all()
def board(src): return float(np.interp(src if src is not None else 80,_kx,_ky))
# kawasan papan: potong B-roll (1080x1440) dan letak dalam frame 1080x1920
BCROP=(90,210,840,1030); BSCALE=0.83; BPOS=(int((1080-840*BSCALE)/2),355)
ROWS=[290,380,470,580,660,750,860,960,1060,1160]
def row_y(r): return BPOS[1]+(ROWS[r]-BCROP[1])*BSCALE
if __name__=="__main__":
    print("durasi",round(DUR,2),"isi",round(CONTENT,2))
    for s in [11.6,23.32,34.18,45.54,53.14,55.0,68.1,72.38,76.16]: print(s,"->",round(s2o(s),2))
