"""AS-F-016 Trick Sifir 8: garis masa (satu take, tiada potongan), fasa skrin terbelah, pemetaan papan B-roll."""
import numpy as np
THUMB=1.0; END=1.5
EDL=[(0.00,53.76)]
THUMB_SRC=1.5
CONTENT=sum(b-a for a,b in EDL); DUR=THUMB+CONTENT+END
def o2s(t):
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
TEACH=(3.20,32.30); TR=0.40          # skrin terbelah: papan atas, Cikgu bawah
def phase(src):
    if src is None: return 0.0
    a,b=TEACH
    def ss(x): x=min(max(x,0),1); return x*x*(3-2*x)
    return ss((src-a)/TR)*(1-ss((src-b)/TR))
SENT=[0,3.28,8.18,12.26,14.86,20.16,22.12,26.5,32.64,33.54,37.06,38.6,41.0,45.1,52.12]
def zoom(src):
    if src is None: return 1.08
    i=max(k for k,s in enumerate(SENT) if src>=s-0.05); return 1.12 if i%2 else 1.0
# papan: (mula, tamat sebutan) -> masa B-roll siap ditulis
T1=[((4.16,4.74),2.9),((4.74,5.26),3.9),((5.48,6.02),5.1),((6.44,6.86),6.4),((7.24,7.88),7.5)]
T2=[((9.16,9.46),10.7),((9.68,10.10),12.3),((10.36,11.00),12.8),((11.20,11.64),14.0),((11.72,11.96),14.8)]
U1=[((15.94,16.76),17.3),((16.78,17.22),18.3),((17.42,18.32),19.4),((18.54,19.20),20.3),((19.40,19.92),21.3)]   # ditulis dari bawah
U2=[((22.40,23.18),24.4),((23.18,23.56),25.4),((23.92,24.70),26.4),((24.88,25.54),27.2),((25.72,26.22),28.0)]
RL=[((27.14,27.88),31.9),((28.20,28.74),32.8),((28.94,29.56),33.6),((29.74,30.32),34.5),((30.32,31.6),37.6)]
LAG=0.25   # masa perkataan Whisper ±0.25 s awal berbanding sebutan sebenar
T1,T2,U1,U2,RL=[[((s+LAG,e+LAG),d) for (s,e),d in g] for g in (T1,T2,U1,U2,RL)]
KP=[(0,1.0),(3.9,1.0)]
for grp,off in [(T1,0.5),(T2,0.6),(U1,0.6),(U2,0.6),(RL,0.6)]:
    for (s,e),d in grp: KP+=[(s,d-off),(e,d)]
KP+=[(40,40.5),(80,40.5)]
for i in range(1,len(KP)): KP[i]=(max(KP[i][0],KP[i-1][0]+0.02),max(KP[i][1],KP[i-1][1]))
_kx=np.array([k[0] for k in KP]);_ky=np.array([k[1] for k in KP])
assert (np.diff(_kx)>0).all()
def board(src): return float(np.interp(src if src is not None else 80,_kx,_ky))
# susun atur
BCROP=(60,320,620,540); BSCALE=1.25; BPOS=(152,340)       # potongan B-roll 1080x1440 -> panel atas
DIV=1040                                                    # garis pembahagi skrin terbelah
ROWS=[(362,419),(452,513),(534,601),(635,701),(740,800)]
def row_y(r): return BPOS[1]+((ROWS[r][0]+ROWS[r][1])/2-BCROP[1])*BSCALE
def bx(X): return BPOS[0]+(X-BCROP[0])*BSCALE
if __name__=="__main__": print("durasi",round(DUR,2)); print([round(row_y(r)) for r in range(5)],round(bx(180)),round(bx(650)))
