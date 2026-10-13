# Build the cut list for IMG_0571 (raw take with retakes) and map words to the output timeline.
# usage: edl.py transcript.json chunks0.json edl.json
import json,sys
# (id, src_in, src_out, note) – best take of each line, in story order
SEG=[("P",61.30,62.62,"Percaya atau tidak? (ambilan ke-2)"),
     ("S",64.62,71.95,"Sejam belajar tanpa gangguan … setiap 5 minit"),
     ("I",168.24,173.90,"Pengenalan (ambilan ke-3, tanpa 'Eh')"),
     ("F",25.50,29.93,"Saya tak kisah … dia fokus (ambilan ke-1 dari 4)"),
     ("O",75.30,78.62,"Otak perlukan fokus …"),
     ("R",88.48,91.38,"Sebab kalau panjang … merewang (ambilan ke-2 dari 3)"),
     ("V",106.26,111.70,"Kita tengok video panjang-panjang … ceramah lah (ambilan ke-2)"),
     ("T",148.52,154.86,"Siapa rasa telefon banyak ganggu kita? … semua ganggu"),
     ("K",155.22,156.74,"Siapa rasa? Cuba komen.")]
FPS=30000/1001
snap=lambda t:round(round(t*FPS)/FPS,4)  # cut on frame boundaries so audio, video and captions stay in sync
SEG=[(n,snap(a),snap(b),note) for n,a,b,note in SEG]
END=round(135/FPS,4)  # 4.5 s  # end card (blurred freeze of last frame + CTA)
FIX={"tuition":"tuisyen"}
def out_off(i): return sum(e-s for _,s,e,_ in SEG[:i])
if __name__=="__main__":
    t=json.load(open(sys.argv[1]));c=json.load(open(sys.argv[2]))
    src=[w for s in t for w in s["words"] if w["s"]>=60]
    src+=[{"w":w["w"],"s":w["s"],"e":w["e"]} for ch in c if ch["chunk"][0]==25.3 for w in ch["words"]]
    src[[i for i,w in enumerate(src) if w["s"]==25.3][0]]["s"]=25.58  # chunk-start clamp
    src.sort(key=lambda w:w["s"])
    words=[]
    for i,(n,s,e,_) in enumerate(SEG):
        o=out_off(i)
        for w in src:
            if min(w["e"],e)-max(w["s"],s)>0.04 and w["s"]<e-0.15:  # overlap test: whisper word starts include the leading pause
                txt=w["w"].strip()
                if txt.startswith("-") and words and words[-1]["seg"]==n: words[-1]["w"]+=txt;words[-1]["e"]=round(o+min(w["e"],e)-s,3);continue
                txt=txt[0].upper()+txt[1:] if not words or words[-1]["seg"]!=n else txt
                txt=FIX.get(txt.rstrip(".,?"),None) and FIX[txt.rstrip(".,?")]+txt[len(txt.rstrip(".,?")):] or txt
                words.append({"w":txt,"seg":n,"s":round(o+max(w["s"],s,w["e"]-0.6)-s,3),"e":round(o+min(w["e"],e)-s,3),"src":round(w["s"],2)})
    D=out_off(len(SEG))
    json.dump({"segments":[{"id":n,"src_in":s,"src_out":e,"out_in":round(out_off(i),3),"note":note} for i,(n,s,e,note) in enumerate(SEG)],
               "end_card":{"out_in":round(D,3),"dur":END,"freeze_src":SEG[-1][2]-0.04},
               "duration":round(D+END,3),"words":words},open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
    print("duration",round(D+END,2))
    for w in words: print(f'{w["s"]:6.2f} {w["seg"]} {w["w"]}')
