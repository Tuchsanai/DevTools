#!/usr/bin/env bash
set -uo pipefail

readme=${1:-}
block_timeout=${BLOCK_TIMEOUT:-180}
if [[ -z "$readme" || ! -f "$readme" ]]; then
  echo "usage: $0 <readme.md>" >&2
  exit 2
fi

work=$(mktemp -d)
declare -a bg_pids=()
cleanup() {
  local pid
  for pid in "${bg_pids[@]}"; do kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; done
  rm -rf "$work"
}
trap cleanup EXIT INT TERM

# (1) แยก fenced bash พร้อม tag บรรทัดก่อนหน้าเป็นไฟล์ชั่วคราวทีละ block
awk -v out="$work" '
  /^<!--[[:space:]]*(run|bg|expect-fail(:[0-9]+)?|skip-auto([[:space:]].*)?)[[:space:]]*-->[[:space:]]*$/ { tag=$0; next }
  /^```bash[[:space:]]*$/ && !inside {
    inside=1; n++; file=sprintf("%s/block-%03d.sh",out,n); print tag "\t" file >> (out "/manifest"); tag=""; next
  }
  /^```[[:space:]]*$/ && inside { inside=0; close(file); next }
  inside { print >> file }
  END { if (inside) exit 3 }
' "$readme" || { echo "ERROR: fenced bash ไม่สมบูรณ์"; exit 3; }

touch "$work/manifest"
declare -A count=([run]=0 [bg]=0 [expect-fail]=0 [skip-auto]=0)
passed=0 failed=0 index=0

# (2) รันตามลำดับ; background ถูกจำกัดเวลาและเก็บ PID ไว้ cleanup
while IFS=$'\t' read -r raw file; do
  ((index+=1))
  if [[ $raw =~ ^\<!--[[:space:]]*bg ]]; then kind=bg
  elif [[ $raw =~ ^\<!--[[:space:]]*expect-fail(:([0-9]+))? ]]; then kind=expect-fail; expected=${BASH_REMATCH[2]:-}
  elif [[ $raw =~ ^\<!--[[:space:]]*skip-auto ]]; then kind=skip-auto
  elif [[ $raw =~ ^\<!--[[:space:]]*run ]]; then kind=run
  else kind=run; fi
  ((count[$kind]+=1))
  echo "BLOCK $index [$kind]"
  case "$kind" in
    skip-auto) echo "SKIP $raw"; ((passed+=1));;
    bg) timeout "${block_timeout}s" bash "$file" & bg_pids+=("$!"); echo "PASS started pid=${bg_pids[-1]}"; ((passed+=1));;
    run)
      if timeout "${block_timeout}s" bash "$file"; then echo "PASS"; ((passed+=1)); else rc=$?; echo "FAIL exit=$rc"; ((failed+=1)); fi;;
    expect-fail)
      timeout "${block_timeout}s" bash "$file"; rc=$?
      if [[ -n ${expected:-} && $rc -ne $expected ]]; then echo "FAIL expected=$expected actual=$rc"; ((failed+=1))
      elif [[ -z ${expected:-} && $rc -eq 0 ]]; then echo "FAIL expected=non-zero actual=0"; ((failed+=1))
      else echo "PASS expected failure exit=$rc"; ((passed+=1)); fi;;
  esac
done < "$work/manifest"

# (3) สรุปจำนวนทุกประเภทและใช้ exit code ตัดสินผลรวม
echo "SUMMARY run=${count[run]} bg=${count[bg]} expect-fail=${count[expect-fail]} skip-auto=${count[skip-auto]} passed=$passed failed=$failed"
(( failed == 0 ))
