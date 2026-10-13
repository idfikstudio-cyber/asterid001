# Natural grade for IMG_0571: original skin tone kept, light contrast + clarity, subtle edge vignette.
# usage: grade.sh in.MOV out.mp4 [scale]   (scale default 1080:1920)
D=$(dirname "$0")/../edit
ffmpeg -y -i "$1" -i $D/vigmask.png -filter_complex "$(cat $D/grade_filter.txt),scale=${3:-1080:1920},format=yuv420p[o]" -map "[o]" -map 0:a -c:v libx264 -crf 18 -c:a aac "$2"
