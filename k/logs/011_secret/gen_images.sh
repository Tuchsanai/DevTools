#!/usr/bin/env bash
# สร้างภาพจาก images.json ทีละ 3 ภาพพร้อมกันด้วย cyolo1 (ข้ามภาพที่มีอยู่แล้ว)
set -u
L=/root/workspace/DevTools/k/logs/011_secret
REF=/root/workspace/DevTools/k/011_kubernetes_secret/01_Theory/images/00-character-som.png
mkdir -p $L/img
gen() {  # $1=id $2=path $3=promptfile
  local id=$1 out=$2 pf=$3
  local p="ใช้เครื่องมือสร้างภาพในตัว (built-in image generation / image_gen) สร้างภาพ 1 ภาพ แนบภาพ reference ตัวละครน้องส้มมาด้วย (00-character-som.png) ให้วาดน้องส้มให้เหมือน reference ทุกประการ บันทึกผลเป็น PNG ที่ path นี้เท่านั้น: $out (ถ้าเครื่องมือบันทึกไว้ที่อื่นให้ copy มาที่ path นี้) ห้ามวาดด้วยโค้ด/SVG/PIL และห้ามแก้ไฟล์อื่น ตอบสั้น ๆ ว่าบันทึกที่ไหน

$(cat $pf)"
  cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort="high" -i "$REF" --json -o $L/img/$id.out "$p" < /dev/null > $L/img/$id.jsonl 2>&1
  if [ -s "$out" ] && ! grep -q turn.failed $L/img/$id.jsonl; then echo "$(date +%T) OK   $id $out"; else echo "$(date +%T) FAIL $id"; fi
}
python3 - <<'PY' > $L/img/queue.tsv
import json
for i in json.load(open('/root/workspace/DevTools/k/logs/011_secret/images.json')):
    pf=f"/root/workspace/DevTools/k/logs/011_secret/img/{i['id']}.prompt"
    open(pf,'w').write(i['prompt'])
    print(i['id'],i['path'],pf,sep='\t')
PY
ONLY=${ONLY:-.}; SKIP=${SKIP:-^$}
mapfile -t Q < <(while IFS=$'\t' read -r id path pf; do [[ "$id" =~ $ONLY ]] || continue; [[ "$id" =~ $SKIP ]] && continue; [ -s "$path" ] || echo "$id|$path|$pf"; done < $L/img/queue.tsv)
echo "$(date +%T) queue: ${#Q[@]} images"
for ((k=0; k<${#Q[@]}; k+=3)); do
  for j in $k $((k+1)) $((k+2)); do
    [ $j -lt ${#Q[@]} ] || continue
    IFS='|' read -r id path pf <<< "${Q[$j]}"
    gen "$id" "$path" "$pf" &
  done
  wait
done
echo "$(date +%T) DONE"
