import cv2,sys,json
det=None
out={}
for f in sys.argv[2:]:
    im=cv2.imread(f);h,w=im.shape[:2]
    boxes=[]
    for sc in (1.0,2.0,3.0):
        img=cv2.resize(im,(int(w*sc),int(h*sc)))
        d=cv2.FaceDetectorYN.create(sys.argv[1],"",(img.shape[1],img.shape[0]),0.5,0.3,5000)
        _,r=d.detect(img)
        if r is not None:
            for x in r: boxes.append([float(x[0]/sc),float(x[1]/sc),float(x[2]/sc),float(x[3]/sc),float(x[14])])
    out[f]=boxes;print(f,len(boxes))
json.dump(out,open("faces.json","w"))
