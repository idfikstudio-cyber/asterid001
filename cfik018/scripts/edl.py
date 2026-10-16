# Build the cut list for CFik018. Source A = IMG_1472.MOV (B unused; pass the same .sil twice).
# v2: cuts requested after preview 1 (start on 'Ramai', false start before 'Masalahnya', pauses at 0:28, 0:34, 0:37).
# Each segment = best take of one line; pauses > MAXGAP inside a segment are squeezed to KEEP seconds.
# usage: edl.py A.sil B.sil out.json
import json,sys
MAXGAP,KEEP=0.30,0.10
SEG=[ # id, clip, in, out, text (single source IMG_1472.MOV = clip "A")
 ("hook","A",9.22,13.45,"Ramai hampir rugi berbelas ribu sebabkan satu gambar dekat Pinterest."),
 ("situasi","A",20.60,26.78,"Situasi yang biasa kita jumpa adalah klien datang kat kita. Dia nak buat macam dia jumpa dekat Pinterest."),
 ("masalah","A",37.90,44.20,"Masalahnya, dapur dekat gambar Pinterest tu 15 kaki. Tapi rumah korang tu 9 kaki je."),
 ("muat","A",55.62,63.92,"Peti ais tak muat, laluan jadi sempit, pintu kabinet berlaga-laga."),
 ("lukis","A",73.38,77.45,"Bila kami lukis ikut 3D dan ukuran sebenar rumah korang,"),
 ("lukis2","A",80.08,85.36,"masalah ni akan dapat kita detect sebelum papan tu mula melekat dekat dinding."),
 ("murah","A",91.86,94.62,"Ubah 3D tak susah, tak mahal."),
 ("mahal2","A",97.95,101.30,"Ubah time renovation, beribu hilang."),
 ("follow","A",108.85,110.75,"Follow dan share."),
]
def sil(path):
    out=[]
    for line in open(path):
        line=line.strip().lstrip("[")
        if "-" in line:
            a,b=line.split("-");out.append((float(a),float(b)))
    return out
S={"A":sil(sys.argv[1]),"B":sil(sys.argv[2])}
parts=[];t=0
for sid,c,i,o,txt in SEG:
    keep=[(i,o)]
    for a,b in S[c]:
        if b-a>MAXGAP and a>i+0.05 and b<o-0.05:
            nk=[]
            for x,y in keep:
                if a>x and b<y: nk+= [(x,a+KEEP/2),(b-KEEP/2,y)]
                else: nk.append((x,y))
            keep=nk
    for x,y in keep:
        parts.append({"seg":sid,"clip":c,"in":round(x,3),"out":round(y,3),"t":round(t,3)});t+=y-x
json.dump({"segments":[{"id":s,"clip":c,"in":i,"out":o,"text":x} for s,c,i,o,x in SEG],"parts":parts,"duration":round(t,3)},open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
print("parts",len(parts),"duration",round(t,2))
