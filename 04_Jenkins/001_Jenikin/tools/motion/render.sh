#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_dir="${project_dir}/out"
asset_dir="${project_dir}/../../slides_assets/motion"
browser_path="${REMOTION_BROWSER_EXECUTABLE:-}"

on_exit() {
  exit_code=$?
  echo "render.sh EXIT_CODE=${exit_code}"
}
trap on_exit EXIT

cd "${project_dir}"
echo '+ npm ci'
npm_config_cache="${project_dir}/.npm-cache" npm ci

if [[ -z "${browser_path}" ]]; then
  browser_path="$(find /root/.cache/ms-playwright -type f -path '*/chrome-headless-shell-linux64/chrome-headless-shell' -perm -111 2>/dev/null | sort -V | tail -n 1)"
fi
if [[ -z "${browser_path}" || ! -x "${browser_path}" ]]; then
  echo 'ERROR: local Playwright Chromium not found; refusing a network browser download.' >&2
  exit 2
fi
echo "Using local browser: ${browser_path}"

mkdir -p "${output_dir}" "${asset_dir}"

composition_ids=(
  mo-intro
  mo-manual-vs-ci
  mo-pipeline-flow
  mo-polling-vs-webhook
  mo-dood-socket
)
output_names=(
  mo_intro.mp4
  mo_manual_vs_ci.mp4
  mo_pipeline_flow.mp4
  mo_polling_vs_webhook.mp4
  mo_dood_socket.mp4
)

for index in "${!composition_ids[@]}"; do
  composition_id="${composition_ids[$index]}"
  output_name="${output_names[$index]}"
  echo "+ npx remotion render src/index.ts ${composition_id} out/${output_name} --codec=h264 --crf=28 --x264-preset=slow --muted --concurrency=8"
  npx remotion render src/index.ts "${composition_id}" "${output_dir}/${output_name}" \
    --codec=h264 \
    --crf=28 \
    --x264-preset=slow \
    --muted \
    --concurrency=8 \
    --browser-executable="${browser_path}"
  mv -f "${output_dir}/${output_name}" "${asset_dir}/${output_name}"
  ls -lh "${asset_dir}/${output_name}"
done

/opt/venv/bin/python manifest.py
echo 'Rendered assets:'
ls -lh "${asset_dir}"/*.mp4 "${asset_dir}/motion-manifest.json"
