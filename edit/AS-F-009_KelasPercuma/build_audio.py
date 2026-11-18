import subprocess,json,re,sys
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad"
SFX=[(0.0,"pop",.6),(0.95,"whoosh",.55),(1.02,"pop",.45),(1.3,"pop",.35),(4.48,"pop",.4),(5.82,"pop",.35),(6.08,"whoosh",.5),(7.2,"ding",.4),
(8.68,"pop",.35),(9.9,"pop",.35),(10.78,"pop",.35),(11.48,"pop",.35),(12.06,"whoosh",.5),(12.12,"click",.5),(12.76,"pop",.35),
(14.9,"pop",.4),(16.68,"pop",.5),(17.5,"chaching",.55),(18.9,"pop",.3),(19.52,"pop",.3),(19.96,"pop",.3),(20.36,"pop",.3),(20.82,"pop",.3),
(21.4,"ding",.4),(22.1,"pop",.35),(23.54,"impact",.35),(24.36,"whoosh",.5),(25.16,"click",.55),(26.95,"whoosh",.6),(27.05,"ding",.35)]
def run(c): return subprocess.run(c,shell=True,capture_output=True,text=True)
# 1) voice clean + normalize to -14
pre="atrim=0:25.95,asetpts=PTS-STARTPTS,highpass=f=80,afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,equalizer=f=3500:t=q:w=1:g=1.5"
r=run(f'ffmpeg -hide_banner -i {S}/raw/AS-F-009_KelasPercuma.mp4 -af "{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json" -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
ln=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
run(f'ffmpeg -v error -y -i {S}/raw/AS-F-009_KelasPercuma.mp4 -af "{pre},{ln},aresample=48000,adelay=1000:all=1,apad=whole_dur=28.45" -ac 2 {S}/work/voice.wav')
# 2) music bed: -16.5 LUFS src -> ~-38 under speech, ~-26 on thumb/end
mus=f"atrim=0:28.45,asetpts=PTS-STARTPTS,aresample=48000,volume='if(lt(t,0.9),0.25,if(lt(t,1.2),0.25-(t-0.9)/0.3*0.184,if(lt(t,26.85),0.066,0.066+min((t-26.85)/0.3,1)*0.184)))':eval=frame,afade=t=out:st=27.9:d=0.55"
inputs=f'-i {S}/work/voice.wav -i {S}/music/aster_ceria.wav '
fl=f"[1:a]{mus}[m];"
for i,(t,n,g) in enumerate(SFX):
    inputs+=f"-i {S}/sfx/{n}.wav "
    fl+=f"[{i+2}:a]aresample=48000,volume={g},adelay={int(t*1000)}:all=1[s{i}];"
fl+="[0:a][m]"+"".join(f"[s{i}]" for i in range(len(SFX)))+f"amix=inputs={len(SFX)+2}:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]"
run(f'ffmpeg -v error -y {inputs} -filter_complex "{fl}" -map "[a]" -t 28.45 {S}/work/mix_pre.wav')
r=run(f'ffmpeg -hide_banner -i {S}/work/mix_pre.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
run(f'ffmpeg -v error -y -i {S}/work/mix_pre.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true,aresample=48000" {S}/work/mix.wav')
r=run(f'ffmpeg -hide_banner -i {S}/work/mix.wav -af ebur128=peak=true -f null -')
print(r.stderr[-400:])
json.dump([{"t":t,"name":n} for t,n,g in SFX],open(f"{S}/work/sfx.json","w"))
