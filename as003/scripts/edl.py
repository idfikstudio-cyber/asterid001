# Build the cut list for As003. Source A = IMG_0573.MOV, B = IMG_0575.MOV.
# Each segment = best take of one line; pauses > MAXGAP inside a segment are squeezed to KEEP seconds.
# usage: edl.py A.sil B.sil out.json
import json,sys
MAXGAP,KEEP=0.30,0.10
SEG=[ # id, clip, in, out, text
 ("hook","B",30.92,34.90,"Pokok takkan terus berbuah selepas kita tanam. Betul tak?"),
 ("fokus","A",13.22,16.92,"Saya rasa ramai ibu ayah fokus pada markah SPM."),
 ("faham","A",23.12,30.30,"Saya faham, semua ibu ayah memang nak anak-anak score dan dapatkan straight A dalam SPM."),
 ("proses","A",31.82,36.00,"Tapi sebelum tengok markah, kita kena tengok proses dia."),
 ("yakin","A",39.62,41.56,"Adakah dia lebih yakin?"),
 ("tanya1","A",43.12,44.22,"Adakah dia"),
 ("tanya2","A",44.62,46.10,"banyak bertanya ke?"),
 ("seronok","A",48.42,51.92,"Lebih konsisten ke, lebih seronok nak belajar ke?"),
 ("sikap","A",60.58,63.56,"Kadang-kadang perubahan sikap ni datang dulu,"),
 ("berlari","A",76.15,79.55,"baru markah datang berlari-lari dekat dia."),
 ("masa","B",34.84,41.45,"Kita perlukan masa, masa, masa. Dan proses tu lah yang mengukuhkan akar dia."),
 ("penting","A",92.46,96.16,"Proses lebih penting daripada keputusan jangka pendek."),
 ("komen","A",110.40,115.20,"Apa pandangan ibu ayah? Cuba komen kat bawah. Saya nak tengok, saya nak baca."),
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
