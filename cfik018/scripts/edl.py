# Build the cut list for CFik018. Source A = IMG_1472.MOV (B unused; pass the same .sil twice).
# Each segment = best take of one line; pauses > MAXGAP inside a segment are squeezed to KEEP seconds.
# usage: edl.py A.sil B.sil out.json
import json,sys
MAXGAP,KEEP=0.30,0.10
SEG=[ # id, clip, in, out, text (single source IMG_1472.MOV = clip "A")
 ("hook","A",8.52,13.45,"Ramai hampir rugi berbelas ribu sebabkan satu gambar dekat Pinterest."),
 ("situasi","A",20.60,26.78,"Situasi yang biasa kita jumpa adalah klien datang kat kita. Dia nak buat macam dia jumpa dekat Pinterest."),
 ("masalah","A",36.95,44.20,"Masalahnya, dapur dekat gambar Pinterest tu 15 kaki. Tapi rumah korang tu 9 kaki je."),
 ("muat","A",55.62,63.92,"Peti ais tak muat, laluan jadi sempit, pintu kabinet berlaga-laga."),
 ("lukis","A",73.38,85.85,"Bila kami lukis ikut 3D dan ukuran sebenar rumah korang, masalah ni akan dapat kita detect sebelum papan tu mula melekat dekat dinding."),
 ("murah","A",91.20,94.62,"Nak ubah 3D ni tak susah, tak mahal."),
 ("mahal","A",96.15,96.47,"Nak"),
 ("mahal2","A",97.95,101.30,"ubah time renovation, beribu hilang."),
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
