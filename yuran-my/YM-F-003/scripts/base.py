# Video asas: thumbnail pegun 1 s + talking head (grade + punch-in ikut plan) + latar end card. python3 base.py plan.json raw.mp4 out.mp4 W H
import json, subprocess, sys
plan, raw, out, OW, OH = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
P = json.load(open(plan))
SRC = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", raw]))
# grade lembut: cerah & jelas, kekal warna kulit (saturasi rendah sahaja)
GRADE = "eq=brightness=0.02:contrast=1.05:saturation=1.06:gamma=1.03,curves=all='0/0.02 0.5/0.52 1/0.98',unsharp=5:5:0.4"
EYE = 750   # paras mata dalam frame sumber (px, 1920 tinggi)
def crop(z):
    w, h = round(1080 / z / 2) * 2, round(1920 / z / 2) * 2
    top = min(1920 - h, max(0, round(EYE - 640 / z)))   # mata ke ±1/3 atas
    return f"crop={w}:{h}:{(1080 - w) // 2}:{top},scale={OW}:{OH}:flags=lanczos,setsar=1"
Z = P["zoom"] + [{"src": SRC, "scale": None}]
parts, f = [], []
f.append(f"[0:v]{GRADE},split={len(Z)}" + "".join(f"[v{i}]" for i in range(len(Z))))
# thumbnail: frame pilihan, punch 1.15
f.append(f"[v{len(Z)-1}]trim=start={P['thumb_src']}:duration=0.04,setpts=PTS-STARTPTS,{crop(1.15)},loop=loop={int(P['t0']*30)-1}:size=1,setpts=N/30/TB,fps=30[th]")
for i in range(len(Z) - 1):
    a, b = Z[i]["src"], Z[i + 1]["src"]
    f.append(f"[v{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,{crop(Z[i]['scale'])}[z{i}]")
endn = round((P["duration"] - P["end"]) * 30)
f.append(f"color=c=0x2A3B8F:s={OW}x{OH}:r=30:d={endn/30:.4f},setsar=1[ec]")
f.append("[th]" + "".join(f"[z{i}]" for i in range(len(Z) - 1)) + f"[ec]concat=n={len(Z)+1}:v=1:a=0,fps=30,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-filter_complex", ";".join(f), "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out], check=True)
