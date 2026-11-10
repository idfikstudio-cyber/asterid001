# source-time captions -> video time
import json
def V(t):
  if t<2.52: return t+1.0
  if t<17.36: return t+0.63
  return t+0.22
C=[(0.00,"Pukul *9 *malam"),(1.00,"anak-anak akan buat"),(1.74,"*ulang *kaji"),
(2.89,"Kadang-kadang kita tengok"),(3.88,"anak tu *termenung"),(4.80,"tengok buku tu"),
(5.84,"Bukan kadang-kadang menung"),(7.12,"Kadang-kadang ada yang"),(8.14,"*menangis"),
(8.74,"Ibu ayah *menekan-tekan"),(9.92,"Kau ni kenapa"),(10.54,"tak *faham lagi ni?"),
(11.74,"Kau ni kenapa"),(12.30,"tak buat *ulang *kaji lagi ni?"),
(13.84,"Esok babak *yang *sama"),(15.28,"Kadang-kadang ada"),(15.92,"satu *peel anak"),(16.82,"esok *sakit"),
(17.80,"tak nak pergi sekolah"),(19.14,"Anak ni bukan *malas"),(20.22,"sebenarnya"),(20.80,"Dan ibu pun"),(21.60,"bukannya *garang"),
(22.42,"Cuma dia pergi sekolah tu"),(23.80,"dalam keadaan"),(24.44,"*asas dia"),(25.20,"tak *kukuh lagi"),
(26.08,"Tuisyen bersama dengan kami"),(27.14,"kita akan sediakan"),(27.86,"*2 *guru"),(28.52,"dalam *1 *kelas"),
(29.60,"Satu orang guru"),(30.76,"*mengajar"),(31.30,"dan seorang lagi guru"),(32.26,"akan *menjawab soalan-soalan"),(33.62,"yang anak-anak *confused"),
(34.94,"Anak tak perlu *takut"),(35.84,"nak *bertanya"),(36.36,"sebab *kamera"),(37.20,"tak payah buka pun"),
(38.48,"*Mikrofon pun"),(39.22,"tak payah buka"),(40.04,"*Taip sahaja"),(41.04,"nanti *cikgu *kedua"),(42.28,"akan jawab soalan"),
(43.08,"*DM kami"),(43.50,"untuk keterangan lanjut")]
END=44.60
out=[]
for i,(s,t) in enumerate(C):
  e=C[i+1][0] if i+1<len(C) else END
  vs,ve=V(s),V(e)
  if i+1<len(C) and C[i+1][0]>=17.36 and s<17.36: ve=V(17.36)
  out.append([round(vs,2),round(ve,2),t])
json.dump(out,open("work/caps.json","w"),ensure_ascii=False);print(out[:3],out[-1],"dur",round(1+ (END-0.37-0.41),2)+1.5)
