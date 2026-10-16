# Music bed: Mixkit track, ducked under the voice, louder on the end card, faded out. Pass a pre-trimmed track to start mid-song.
# usage: music.sh music.mp3 voice_source.mp4 DUR SPEECH_END out.m4a
M=$1; V=$2; DUR=$3; END=$4; OUT=$5
ffmpeg -v error -y -i "$M" -i "$V" -filter_complex "\
[0:a]atrim=0:$DUR,asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,loudnorm=I=-27:TP=-3,volume='if(lt(t,$END),1,1.9)':eval=frame,afade=t=in:d=0.6,afade=t=out:st=$(echo "$DUR-1.6"|bc):d=1.6[m];\
[1:a]aformat=channel_layouts=stereo,asplit[sc][x];[x]anullsink;\
[m][sc]sidechaincompress=threshold=0.05:ratio=4:attack=30:release=400:makeup=1[o]" -map "[o]" -c:a aac -b:a 128k "$OUT"
