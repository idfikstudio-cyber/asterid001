# usage: blur.py faces.json extra.json outdir   -> heavy elliptical blur over every face box (+ manual boxes)
import cv2,json,sys,os,numpy as np
F=json.load(open(sys.argv[1]));X=json.load(open(sys.argv[2])) if os.path.exists(sys.argv[2]) else {}
for f,b in F.items():
    name=os.path.basename(f);im=cv2.imread(f);h,w=im.shape[:2]
    e=X.get(name,{});boxes=[x[:4] for x in b if x[4]>=0.55 and x[2]<=e.get("maxw",9999)]+e.get("faces",[])
    blur=cv2.GaussianBlur(cv2.resize(im,(w//8,h//8)),(0,0),3);blur=cv2.resize(blur,(w,h))
    m=np.zeros((h,w),np.float32);dbg=im.copy()
    for x,y,bw,bh in boxes:
        cx,cy=x+bw/2,y+bh/2;ax,ay=bw*0.75,bh*0.85
        cv2.ellipse(m,(int(cx),int(cy)),(int(ax),int(ay)),0,0,360,1,-1)
        cv2.rectangle(dbg,(int(x),int(y)),(int(x+bw),int(y+bh)),(0,0,255),2)
    for x,y,bw,bh in e.get("regions",[]):
        r=np.zeros((h,w),np.float32);r[y:y+bh,x:x+bw]=1;m=np.maximum(m,cv2.GaussianBlur(r,(0,0),12))
    m=cv2.GaussianBlur(m,(0,0),3)[...,None]
    o=(im*(1-m)+blur*m).astype(np.uint8)
    cv2.imwrite(os.path.join(sys.argv[3],name),o,[cv2.IMWRITE_JPEG_QUALITY,93]);cv2.imwrite(os.path.join(sys.argv[3],"dbg_"+name),dbg)
    print(name,len(boxes))
