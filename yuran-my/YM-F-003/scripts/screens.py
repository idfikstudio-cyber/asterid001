# Rakaman skrin B-ROLL -> imej pegun dengan data diblur (nama, no. IC, jumlah, statistik)
import sys
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]   # folder frame, folder aset
def blur(im, boxes, r=14):
    for b in boxes:
        reg = im.crop(b).filter(ImageFilter.GaussianBlur(r)); im.paste(reg, b)
    return im
# invois (sistem.mp4 @29s): blur No., item (nama + IC), jumlah
inv = Image.open(f"{src}/s29.png").convert("RGB")
inv = blur(inv, [(380, 480, 510, 970), (758, 480, 1505, 970), (1505, 480, 1575, 970)])
inv.crop((292, 87, 1890, 1000)).save(f"{out}/scr_invois.png")
# dashboard (sistem.mp4 @1s): blur semua angka statistik (tidak disebut spokesperson)
d = Image.open(f"{src}/s1.png").convert("RGB")
d = blur(d, [(372, 312, 470, 350), (908, 312, 1000, 350), (1446, 312, 1480, 350),
             (372, 503, 470, 541), (775, 503, 965, 541), (1178, 503, 1240, 541), (1580, 503, 1665, 541),
             (395, 728, 520, 764), (395, 834, 480, 868), (395, 938, 520, 974), (740, 800, 800, 1032)])
d.crop((292, 87, 1890, 1032)).save(f"{out}/scr_dashboard.png")
