import subprocess,json,re,sys
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad/a11";SFXD=S+"/../sfx"
SFX=[(0.0,"pop",.6),(0.95,"whoosh",.55),(1.0,"chaching",.5),(1.3,"pop",.35),(1.94,"pop",.45),(2.76,"pop",.3),(3.22,"pop",.3),(3.52,"pop",.3),(3.90,"pop",.3),(4.12,"pop",.3),
(5.48,"ding",.35),(6.3,"pop",.4),(7.04,"pop",.4),(8.12,"whoosh",.5),(8.2,"ding",.3),(9.2,"ding",.3),(10.26,"ding",.3),(12.22,"ding",.3),(13.56,"whoosh",.5),(13.62,"pop",.4),
(15.6,"pop",.35),(16.86,"pop",.4),(19.8,"chaching",.55),(21.04,"click",.55),(22.62,"whoosh",.45),(22.7,"ding",.35)]
def run(c): return subprocess.run(c,shell=True,capture_output=True,text=True)
# 1) voice clean + normalize to -14
pre="atrim=0:21.57,asetpts=PTS-STARTPTS,afade=t=out:st=21.55:d=0.02,highpass=f=80,afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,equalizer=f=3500:t=q:w=1:g=1.5"
r=run(f'ffmpeg -hide_banner -i {S}/raw.mp4 -af "{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json" -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
ln=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
run(f'ffmpeg -v error -y -i {S}/raw.mp4 -af "{pre},{ln},aresample=48000,adelay=1000:all=1,apad=whole_dur=24.07" -ac 2 {S}/work/voice.wav')
# 2) music bed: -16.5 LUFS src -> ~-38 under speech, ~-26 on thumb/end
mus=f"atrim=0:24.07,asetpts=PTS-STARTPTS,aresample=48000,volume='if(lt(t,0.9),0.25,if(lt(t,1.2),0.25-(t-0.9)/0.3*0.184,if(lt(t,22.57),0.066,0.066+min((t-22.57)/0.3,1)*0.184)))':eval=frame,afade=t=out:st=23.52:d=0.55"
inputs=f'-i {S}/work/voice.wav -i {S}/../music/aster_ceria_120.wav '
fl=f"[1:a]{mus}[m];"
for i,(t,n,g) in enumerate(SFX):
    inputs+=f"-i {SFXD}/{n}.wav "
    fl+=f"[{i+2}:a]aresample=48000,volume={g},adelay={int(t*1000)}:all=1[s{i}];"
fl+="[0:a][m]"+"".join(f"[s{i}]" for i in range(len(SFX)))+f"amix=inputs={len(SFX)+2}:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]"
run(f'ffmpeg -v error -y {inputs} -filter_complex "{fl}" -map "[a]" -t 24.07 {S}/work/mix_pre.wav')
r=run(f'ffmpeg -hide_banner -i {S}/work/mix_pre.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
run(f'ffmpeg -v error -y -i {S}/work/mix_pre.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true,aresample=48000" {S}/work/mix.wav')
r=run(f'ffmpeg -hide_banner -i {S}/work/mix.wav -af ebur128=peak=true -f null -')
print(r.stderr[-400:])
json.dump([{"t":t,"name":n} for t,n,g in SFX],open(f"{S}/work/sfx.json","w"))
