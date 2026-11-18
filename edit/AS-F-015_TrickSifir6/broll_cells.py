import cv2,json,numpy as np,sys
cap=cv2.VideoCapture(sys.argv[1])
R=[290,380,470,580,660,750,860,960,1060,1160]
C={"n":(420,530),"k":(570,710),"r":(700,900)}
fr=[];i=0
while True:
    ok,f=cap.read()
    if not ok:break
    if i%3==0:
        h=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        blue=((h[...,0]>95)&(h[...,0]<135)&(h[...,1]>120)&(h[...,2]>120))
        row=[]
        for y in R:
            row.append([int(blue[y-45:y+45,a:b].sum()) for a,b in C.values()])
        fr.append([i/30,row])
    i+=1
json.dump(fr,open(sys.argv[2],"w"))
