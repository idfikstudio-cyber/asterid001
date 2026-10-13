# Colour grade + face key light + vignette for IMG_0571.
# usage: grade.sh in.MOV out.mp4 [scale]   (scale default 1080:1920)
D=$(dirname "$0")/../edit
ffmpeg -y -i "$1" -i $D/keymask.png -i $D/vigmask.png -filter_complex "$(cat $D/grade_filter.txt),scale=${3:-1080:1920},format=yuv420p[o]" -map "[o]" -map 0:a -c:v libx264 -crf 18 -c:a aac "$2"
