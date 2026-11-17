#!/bin/sh
# Usage: sh sheet.sh <scene_file_stem> <SceneClass> [n_frames]
# Renders a scene at low quality and writes build/<SceneClass>_sheet.png,
# a contact sheet of frames taken evenly along the video (for checking).
set -e
PY=../.venv/Scripts/python.exe
$PY -m manim -ql --disable_caching "scenes/$1.py" "$2" > "build/$2.log" 2>&1 || { tail -30 "build/$2.log"; exit 1; }
FF=$($PY -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
V="build/media/videos/$1/480p15/$2.mp4"
N=${3:-8}
DUR=$("$FF" -i "$V" 2>&1 | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p' | awk -F: '{print $1*3600+$2*60+$3}')
FPS=$(awk -v d="$DUR" -v n="$N" 'BEGIN{print n/d}')
"$FF" -v error -y -i "$V" -vf "fps=$FPS,scale=640:-1,tile=2x$(( (N+1)/2 ))" -frames:v 1 "build/$2_sheet.png"
echo "duration $DUR s"
