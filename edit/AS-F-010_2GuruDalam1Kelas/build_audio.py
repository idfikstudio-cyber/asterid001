import subprocess,json,re,sys
S="/tmp/claude-0/-home-user-asterid001/800365bc-ab7d-5fea-89c1-d7dec64a8258/scratchpad/a10";SFXD=S+"/../sfx"
SFX=[(0.0,"pop",.6),(0.95,"whoosh",.55),(1.05,"tick",.45),(1.3,"pop",.35),(4.85,"pop",.4),(8.77,"swoosh_down",.4),(10.55,"pop",.45),(12.37,"pop",.45),
(14.47,"whoosh",.5),(17.45,"bonk",.45),(19.36,"pop",.4),(19.96,"click",.5),(21.6,"pop",.4),(21.95,"click",.5),(22.64,"whoosh",.5),(23.0,"pop",.4),(24.66,"pop",.4),
(26.3,"whoosh",.5),(26.38,"ding",.4),(28.08,"impact",.3),(29.82,"pop",.4),(31.7,"pop",.4),(35.16,"ding",.4),(37.06,"click",.5),(38.7,"click",.5),(40.26,"pop",.4),
(41.8,"ding",.4),(43.3,"pop",.45),(44.82,"whoosh",.6),(44.92,"ding",.35)]
def run(c): return subprocess.run(c,shell=True,capture_output=True,text=True)
# 1) voice clean + normalize to -14
pre="aselect='between(t,0,2.52)+between(t,2.89,17.36)+between(t,17.77,44.60)',asetpts=N/SR/TB,highpass=f=80,afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,equalizer=f=3500:t=q:w=1:g=1.5"
r=run(f'ffmpeg -hide_banner -i {S}/raw.mp4 -af "{pre},loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json" -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
ln=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
run(f'ffmpeg -v error -y -i {S}/raw.mp4 -af "{pre},{ln},aresample=48000,adelay=1000:all=1,apad=whole_dur=46.32" -ac 2 {S}/work/voice.wav')
# 2) music bed: -16.5 LUFS src -> ~-38 under speech, ~-26 on thumb/end
mus=f"atrim=0:46.32,asetpts=PTS-STARTPTS,aresample=48000,volume='if(lt(t,0.9),0.25,if(lt(t,1.2),0.25-(t-0.9)/0.3*0.184,if(lt(t,44.72),0.066,0.066+min((t-44.72)/0.3,1)*0.184)))':eval=frame,afade=t=out:st=45.75:d=0.55"
inputs=f'-i {S}/work/voice.wav -i {S}/../music/aster_ceria_120.wav '
fl=f"[1:a]{mus}[m];"
for i,(t,n,g) in enumerate(SFX):
    inputs+=f"-i {SFXD}/{n}.wav "
    fl+=f"[{i+2}:a]aresample=48000,volume={g},adelay={int(t*1000)}:all=1[s{i}];"
fl+="[0:a][m]"+"".join(f"[s{i}]" for i in range(len(SFX)))+f"amix=inputs={len(SFX)+2}:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]"
run(f'ffmpeg -v error -y {inputs} -filter_complex "{fl}" -map "[a]" -t 46.32 {S}/work/mix_pre.wav')
r=run(f'ffmpeg -hide_banner -i {S}/work/mix_pre.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -')
m=json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}",r.stderr).group(0))
run(f'ffmpeg -v error -y -i {S}/work/mix_pre.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true,aresample=48000" {S}/work/mix.wav')
r=run(f'ffmpeg -hide_banner -i {S}/work/mix.wav -af ebur128=peak=true -f null -')
print(r.stderr[-400:])
json.dump([{"t":t,"name":n} for t,n,g in SFX],open(f"{S}/work/sfx.json","w"))
