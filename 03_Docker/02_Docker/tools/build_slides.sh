#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template="$root_dir/tools/Docker_Practical_Journey.template.html"
output="$root_dir/Docker_Practical_Journey.html"

encode() { base64 -w0 "$1"; }

regular_font="$(encode /usr/share/fonts/truetype/custom/IBMPlexSansThai-Regular.ttf)"
semibold_font="$(encode /usr/share/fonts/truetype/custom/IBMPlexSansThai-SemiBold.ttf)"
journey="$(encode "$root_dir/images/docker-learning-journey.svg")"
lab1="$(encode "$root_dir/001_LAB_Container_Detective/images/actual-container-detective.png")"
lab2="$(encode "$root_dir/002_LAB_Image_Factory/images/actual-image-factory.png")"
lab3="$(encode "$root_dir/003_LAB_Volume_Time_Machine/images/actual-volume-persisted.png")"
lab4="$(encode "$root_dir/004_LAB_Compose_Service_Radar/images/actual-compose-radar.png")"
lab5_bad="$(encode "$root_dir/005_LAB_Chaos_Clinic/images/actual-unhealthy.png")"
lab5_good="$(encode "$root_dir/005_LAB_Chaos_Clinic/images/actual-healthy.png")"

sed \
  -e "s|@@FONT_REGULAR@@|$regular_font|g" \
  -e "s|@@FONT_SEMIBOLD@@|$semibold_font|g" \
  -e "s|@@JOURNEY@@|$journey|g" \
  -e "s|@@LAB1@@|$lab1|g" \
  -e "s|@@LAB2@@|$lab2|g" \
  -e "s|@@LAB3@@|$lab3|g" \
  -e "s|@@LAB4@@|$lab4|g" \
  -e "s|@@LAB5_BAD@@|$lab5_bad|g" \
  -e "s|@@LAB5_GOOD@@|$lab5_good|g" \
  "$template" > "$output"

echo "Built $output"
