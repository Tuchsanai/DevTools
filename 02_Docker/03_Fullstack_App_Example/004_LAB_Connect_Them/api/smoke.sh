#!/usr/bin/env bash
# =====================================================================
# smoke.sh — ทดสอบ REQ-01..REQ-12 ของ SkillSpace API ด้วย curl จริง
#
#   ใช้:  API=http://localhost:8000 ./smoke.sh
#   ต้องรันกับฐานข้อมูลที่ initdb ตาม app/db/initdb/ (seed ตั้งต้น)
#   exit 0 = ผ่านครบทุกข้อ · exit 1 = มีข้อที่ไม่ผ่าน
#
# แต่ละข้อทดสอบทั้ง "เคสสำเร็จ" และ "เคส error code ที่ contract กำหนด"
# =====================================================================
set -u

API="${API:-http://localhost:8000}"
BODY="$(mktemp)"          # body ของคำขอล่าสุด
FAILED=0
CUR=""
CUR_OK=1

# ---------- ตัวช่วย ----------
# req <method> <path> [json]  → ตั้งค่า $CODE และเขียน body ลง $BODY
req() {
    local method="$1" path="$2" data="${3:-}"
    if [ -n "$data" ]; then
        CODE=$(curl -sS -o "$BODY" -w '%{http_code}' -X "$method" \
               -H 'Content-Type: application/json' -d "$data" "$API$path")
    else
        CODE=$(curl -sS -o "$BODY" -w '%{http_code}' -X "$method" "$API$path")
    fi
}

# Jf <file> <นิพจน์ python>  → อ่าน JSON เป็นตัวแปร d แล้ว print ผล
# ใช้ python3 เพราะ Container สำหรับเรียนไม่มี jq ติดมา และมี python3 อยู่แล้ว
Jf() {
    python3 -c 'import json,sys; print(eval(sys.argv[2], {"d": json.load(open(sys.argv[1]))}))' "$1" "$2"
}
J() { Jf "$BODY" "$1"; }

save() { cp "$BODY" "$1"; }

start() { CUR="$1"; CUR_OK=1; echo; echo "──────── $1 : $2"; }

# ck <คำอธิบาย> <ค่าที่ได้> <ค่าที่ต้องการ>
ck() {
    if [ "$2" = "$3" ]; then
        printf '    ok   %-44s = %s\n' "$1" "$2"
    else
        printf '    NG   %-44s = %s  (ต้องการ %s)\n' "$1" "$2" "$3"
        CUR_OK=0
    fi
}

endreq() {
    if [ "$CUR_OK" = 1 ]; then
        echo "[PASS] $CUR"
    else
        echo "[FAIL] $CUR"
        FAILED=$((FAILED + 1))
    fi
}

# ทุก error ต้องมีรูป {"detail": "...", "code": "..."} (contract §4)
ck_err() {
    ck "code" "$(J 'd["code"]')" "$1"
    ck "detail เป็นข้อความ ไม่ใช่ array" "$(J 'isinstance(d.get("detail"), str) and len(d["detail"]) > 0')" "True"
}

echo "=== SkillSpace API smoke test ==="
echo "API = $API"

# ---------- รอให้ API พร้อม ----------
for _ in $(seq 1 30); do
    req GET /health && [ "$CODE" = "200" ] && break
    sleep 2
done

# ---------- /health ต้องแตะ db จริง ----------
start "HEALTH" "GET /health ต้องคุยกับฐานข้อมูลจริง"
req GET /health
ck "HTTP" "$CODE" "200"
ck "status" "$(J 'd["status"]')" "ok"
ck "db" "$(J 'd["db"]')" "up"
endreq

# =====================================================================
# REQ-01 : สร้างใบแจ้งซ่อมได้ → 201 และสถานะ NEW
# =====================================================================
start "REQ-01" "POST /api/tickets คืน 201 และใบใหม่มีสถานะ NEW"
req POST /api/tickets '{"asset_id":4,"title":"ไมค์ไร้สายเสียงขาดหาย","detail":"ใช้ไป 10 นาทีแล้วเสียงหาย","priority":"HIGH"}'
ck "HTTP" "$CODE" "201"
ck "status" "$(J 'd["status"]')" "NEW"
ck "assignee ยังว่าง" "$(J 'd["assignee"] is None')" "True"
TID_A="$(J 'd["id"]')"
echo "    (ใบที่สร้าง = #$TID_A)"
# ใบใหม่ต้องโผล่ในรายการจริง ๆ ไม่ใช่คืน 201 เฉย ๆ แล้วไม่บันทึก
req GET "/api/tickets?status=NEW"
ck "ใบใหม่อยู่ในรายการ NEW" "$(J "any(t['id'] == $TID_A for t in d)")" "True"
# เคสผิดรูป : priority นอกเหนือจาก LOW/NORMAL/HIGH ต้องได้ 422 รูปเดียวกับ error อื่น
req POST /api/tickets '{"asset_id":4,"title":"x","detail":"y","priority":"URGENT"}'
ck "HTTP (priority ผิด)" "$CODE" "422"
ck_err "VALIDATION_ERROR"
endreq

# =====================================================================
# REQ-02 : ลำดับสถานะ NEW → ASSIGNED → IN_PROGRESS → DONE เท่านั้น
# =====================================================================
start "REQ-02" "สั่ง NEW → DONE ตรง ๆ ต้องได้ 409 และสถานะไม่เปลี่ยน"
req PATCH "/api/tickets/$TID_A/status" '{"status":"DONE"}'
ck "HTTP" "$CODE" "409"
ck_err "INVALID_TRANSITION"
req GET "/api/tickets?status=NEW"
ck "สถานะยังเป็น NEW เหมือนเดิม" "$(J "any(t['id'] == $TID_A for t in d)")" "True"
# ถอยหลังก็ไม่ได้เช่นกัน
req PATCH "/api/tickets/$TID_A/status" '{"status":"NEW"}'
ck "HTTP (NEW → NEW)" "$CODE" "409"
# ไม่มีใบนี้ในระบบ → 404 ไม่ใช่ 409
req PATCH "/api/tickets/999999/status" '{"status":"ASSIGNED","assignee":"TECH-01"}'
ck "HTTP (ไม่พบใบ)" "$CODE" "404"
ck_err "NOT_FOUND"
endreq

# =====================================================================
# REQ-03 : มอบหมายงานต้องระบุชื่อช่าง
# =====================================================================
start "REQ-03" "เปลี่ยนเป็น ASSIGNED โดยไม่ส่งชื่อช่าง ต้องได้ 400"
req PATCH "/api/tickets/$TID_A/status" '{"status":"ASSIGNED"}'
ck "HTTP (ไม่ส่ง assignee)" "$CODE" "400"
ck_err "ASSIGNEE_REQUIRED"
req PATCH "/api/tickets/$TID_A/status" '{"status":"ASSIGNED","assignee":"   "}'
ck "HTTP (assignee เป็นช่องว่าง)" "$CODE" "400"
req PATCH "/api/tickets/$TID_A/status" '{"status":"ASSIGNED","assignee":"TECH-01"}'
ck "HTTP (ส่งชื่อช่างมาด้วย)" "$CODE" "200"
ck "status" "$(J 'd["status"]')" "ASSIGNED"
ck "assignee" "$(J 'd["assignee"]')" "TECH-01"
endreq

# =====================================================================
# REQ-04 : กรองใบแจ้งซ่อมตามช่างผู้รับผิดชอบ
# =====================================================================
start "REQ-04" "GET /api/tickets?assignee=... คืนเฉพาะงานของคนนั้น"
# ชื่อช่างของรอบทดสอบนี้ต้องไม่ซ้ำกับรอบก่อน ไม่งั้นรันซ้ำบนฐานข้อมูลเดิมแล้วจำนวนจะเพี้ยน
TECH_X="TECH-T$(date +%H%M%S)"
req POST /api/tickets '{"asset_id":6,"title":"แอร์ห้องแล็บ 2 มีน้ำหยด","detail":"น้ำหยดลงโต๊ะ","priority":"NORMAL"}'
TID_B="$(J 'd["id"]')"
req PATCH "/api/tickets/$TID_B/status" "{\"status\":\"ASSIGNED\",\"assignee\":\"$TECH_X\"}"
ck "มอบหมายใบที่สอง" "$CODE" "200"
req GET "/api/tickets?assignee=$TECH_X"
ck "ทุกใบที่คืนมาเป็นของช่างคนนั้น" "$(J "all(t['assignee'] == '$TECH_X' for t in d)")" "True"
ck "จำนวนใบของช่างคนนั้น" "$(J 'len(d)')" "1"
ck "เป็นใบที่เพิ่งมอบหมาย" "$(J 'd[0]["id"]')" "$TID_B"
req GET "/api/tickets?assignee=TECH-01"
ck "ทุกใบที่คืนมาเป็นของ TECH-01" "$(J 'all(t["assignee"] == "TECH-01" for t in d)')" "True"
ck "ไม่มีใบของช่างคนอื่นปนมา" "$(J "any(t['id'] == $TID_B for t in d)")" "False"
req GET "/api/tickets?assignee=TECH-NOBODY"
ck "ช่างที่ไม่มีอยู่จริง → ลิสต์ว่าง" "$(J 'len(d)')" "0"
# ค่าภาษาไทยใน query string ต้อง url-encode ก่อนเสมอ
# ถ้าส่งไบต์ไทยดิบ ๆ ไปกับ URL uvicorn จะตอบ 400 "Invalid HTTP request received."
# ตั้งแต่ชั้นแยกวิเคราะห์ HTTP โดยที่โค้ด FastAPI ยังไม่ถูกเรียกเลย
CODE=$(curl -sS -o "$BODY" -w '%{http_code}' --get \
       --data-urlencode "assignee=ช่างที่ไม่มีตัวตน" "$API/api/tickets")
ck "ค่าภาษาไทยที่ encode แล้ว ใช้งานได้" "$CODE" "200"
ck "และคืนลิสต์ว่าง" "$(J 'len(d)')" "0"
endreq

# =====================================================================
# REQ-05 : ปิดงานพร้อมบันทึกอะไหล่ → ยอดคงเหลือลดลงตามจำนวน
# =====================================================================
start "REQ-05" "ปิดงานพร้อมอะไหล่ 2 รายการ → ยอดคงเหลือของทั้งสองลดลง"
req GET /api/parts; save /tmp/parts_before.json
P2_BEFORE="$(Jf /tmp/parts_before.json '[p for p in d if p["id"]==2][0]["qty_on_hand"]')"
P3_BEFORE="$(Jf /tmp/parts_before.json '[p for p in d if p["id"]==3][0]["qty_on_hand"]')"
echo "    (ก่อนปิดงาน: part#2 = $P2_BEFORE · part#3 = $P3_BEFORE)"
# ปิดงานได้เฉพาะจาก IN_PROGRESS → ต้องเลื่อนขั้นก่อน (สอดคล้อง REQ-02)
req POST "/api/tickets/$TID_A/close" '{"parts":[]}'
ck "HTTP (ปิดตอนยังไม่ IN_PROGRESS)" "$CODE" "409"
ck_err "INVALID_TRANSITION"
req PATCH "/api/tickets/$TID_A/status" '{"status":"IN_PROGRESS"}'
ck "เลื่อนเป็น IN_PROGRESS" "$CODE" "200"
req POST "/api/tickets/$TID_A/close" '{"parts":[{"part_id":2,"qty":3},{"part_id":3,"qty":2}]}'
ck "HTTP" "$CODE" "200"
ck "status" "$(J 'd["status"]')" "DONE"
ck "มีเวลาปิดงาน" "$(J 'd["closed_at"] is not None')" "True"
req GET /api/parts; save /tmp/parts_after.json
ck "part#2 ลดลง 3" \
   "$(Jf /tmp/parts_after.json '[p for p in d if p["id"]==2][0]["qty_on_hand"]')" "$((P2_BEFORE - 3))"
ck "part#3 ลดลง 2" \
   "$(Jf /tmp/parts_after.json '[p for p in d if p["id"]==3][0]["qty_on_hand"]')" "$((P3_BEFORE - 2))"
# ไม่ใช้อะไหล่ก็ต้องปิดได้ (ใบที่สาม)
req POST /api/tickets '{"asset_id":7,"title":"เครื่องพิมพ์เสียงดัง","detail":"มีเสียงครืด ๆ","priority":"LOW"}'
TID_C="$(J 'd["id"]')"
req PATCH "/api/tickets/$TID_C/status" '{"status":"ASSIGNED","assignee":"TECH-01"}' >/dev/null
req PATCH "/api/tickets/$TID_C/status" '{"status":"IN_PROGRESS"}' >/dev/null
req POST "/api/tickets/$TID_C/close" '{"parts":[]}'
ck "HTTP (ปิดงานโดยไม่ใช้อะไหล่)" "$CODE" "200"
ck "status" "$(J 'd["status"]')" "DONE"
endreq

# =====================================================================
# REQ-06 : เบิกเกินยอด → 409 และยอดคงเหลือ "ไม่เปลี่ยน" (rollback ทั้งชุด)
# =====================================================================
start "REQ-06" "เบิกเกินยอด ต้องได้ 409 และยอดคงเหลือไม่เปลี่ยน"
req GET /api/parts; save /tmp/parts_b6.json
P1_BEFORE="$(Jf /tmp/parts_b6.json '[p for p in d if p["id"]==1][0]["qty_on_hand"]')"
P5_BEFORE="$(Jf /tmp/parts_b6.json '[p for p in d if p["id"]==5][0]["qty_on_hand"]')"
echo "    (ก่อนเบิก: part#1 = $P1_BEFORE · part#5 = $P5_BEFORE)"
req PATCH "/api/tickets/$TID_B/status" '{"status":"IN_PROGRESS"}' >/dev/null
# จงใจใส่ part#5 (พอ) มาก่อน part#1 (ไม่พอ)
# ถ้าไม่ได้อยู่ใน transaction เดียว part#5 จะถูกหักไปแล้วตอน part#1 ล้ม → ยอดจะเพี้ยน
req POST "/api/tickets/$TID_B/close" '{"parts":[{"part_id":5,"qty":1},{"part_id":1,"qty":99}]}'
ck "HTTP" "$CODE" "409"
ck_err "INSUFFICIENT_STOCK"
req GET /api/parts; save /tmp/parts_a6.json
ck "part#1 ยอดไม่เปลี่ยน" \
   "$(Jf /tmp/parts_a6.json '[p for p in d if p["id"]==1][0]["qty_on_hand"]')" "$P1_BEFORE"
ck "part#5 ยอดไม่เปลี่ยน (rollback)" \
   "$(Jf /tmp/parts_a6.json '[p for p in d if p["id"]==5][0]["qty_on_hand"]')" "$P5_BEFORE"
req GET "/api/tickets?status=IN_PROGRESS"
ck "ใบงานยังไม่ถูกปิด" "$(J "any(t['id'] == $TID_B for t in d)")" "True"
# เบิกตรง ๆ ผ่าน /move ก็ต้องกันเช่นกัน
req POST "/api/parts/1/move" '{"delta":-99,"reason":"ลองเบิกเกิน"}'
ck "HTTP (/move เบิกเกิน)" "$CODE" "409"
ck_err "INSUFFICIENT_STOCK"
req GET /api/parts
ck "part#1 ยอดยังไม่เปลี่ยน" "$(J '[p for p in d if p["id"]==1][0]["qty_on_hand"]')" "$P1_BEFORE"
endreq

# =====================================================================
# REQ-07 : ทุกการเคลื่อนไหวของอะไหล่ย้อนดูได้ เรียงใหม่ → เก่า
# =====================================================================
start "REQ-07" "GET /api/parts/{id}/moves แสดงรายการเบิก/รับเข้าเรียงตามเวลา"
req GET /api/parts/2/moves
ck "HTTP" "$CODE" "200"
ck "มีรายการเบิกของงานที่เพิ่งปิด" \
   "$(J "d[0]['delta'] == -3 and d[0]['ticket_id'] == $TID_A")" "True"
ck "เรียงเวลาใหม่ → เก่า" "$(J 'all(d[i]["created_at"] >= d[i+1]["created_at"] for i in range(len(d)-1))')" "True"
# รับเข้าคลัง (delta บวก) ต้องถูกบันทึกเหมือนกัน
req POST "/api/parts/6/move" '{"delta":5,"reason":"รับเข้าจากผู้ขาย"}'
ck "HTTP (รับเข้า)" "$CODE" "200"
req GET /api/parts/6/moves
ck "รายการรับเข้าอยู่บนสุด" "$(J 'd[0]["delta"]')" "5"
ck "มีเหตุผลกำกับ" "$(J 'd[0]["reason"]')" "รับเข้าจากผู้ขาย"
req GET /api/parts/1/moves
ck "อะไหล่ที่มีทั้งรับเข้าและเบิกออก" \
   "$(J 'any(m["delta"] > 0 for m in d) and any(m["delta"] < 0 for m in d)')" "True"
ck "เรียงเวลาใหม่ → เก่า" "$(J 'all(d[i]["created_at"] >= d[i+1]["created_at"] for i in range(len(d)-1))')" "True"
req GET /api/parts/999999/moves
ck "HTTP (ไม่พบอะไหล่)" "$CODE" "404"
endreq

# =====================================================================
# REQ-08 : หน้าสรุปนับใบแจ้งซ่อมแยกตามสถานะ ครบ 4 สถานะ
# =====================================================================
start "REQ-08" "GET /api/dashboard คืนจำนวนครบ 4 สถานะ ตรงกับที่นับจากฐานข้อมูล"
req GET /api/dashboard; save /tmp/dash.json
ck "HTTP" "$CODE" "200"
ck "มีครบ 4 สถานะ" \
   "$(Jf /tmp/dash.json 'sorted(d["tickets"].keys()) == ["ASSIGNED","DONE","IN_PROGRESS","NEW"]')" "True"
# นับซ้ำจากอีกทางหนึ่ง (ลิสต์ที่กรองตามสถานะ) แล้วต้องได้ตัวเลขเดียวกัน
for S in NEW ASSIGNED IN_PROGRESS DONE; do
    req GET "/api/tickets?status=$S"
    ck "จำนวน $S ตรงกับลิสต์จริง" "$(Jf /tmp/dash.json "d['tickets']['$S']")" "$(J 'len(d)')"
done
req GET /api/tickets
ck "ผลรวมทุกสถานะ = จำนวนใบทั้งหมด" "$(Jf /tmp/dash.json 'sum(d["tickets"].values())')" "$(J 'len(d)')"
endreq

# =====================================================================
# REQ-09 : หน้าสรุปชี้งานที่ค้างเกินกำหนด
# =====================================================================
start "REQ-09" "ใบที่เปิดเกิน sla_days ของความเร่งด่วนนั้น ปรากฏในรายการ overdue"
req GET /api/dashboard
echo "    (จำนวนงานค้างเกินกำหนดตอนนี้ = $(J 'len(d["overdue"])') ใบ · seed ตั้งต้นมี 2 ใบ)"
ck "มีงานค้างอย่างน้อย 2 ใบตาม seed" "$(J 'len(d["overdue"]) >= 2')" "True"
# ตรวจ "ไม่มีใบเกินมา" ด้วยการบังคับว่าทุกใบในรายการต้องค้างเกิน SLA จริง ๆ
ck "ทุกใบมี days_open เกิน sla_days จริง" \
   "$(J 'all(o["days_open"] > o["sla_days"] for o in d["overdue"])')" "True"
ck "ใบ NORMAL ที่ค้าง 9 วัน อยู่ในรายการ" \
   "$(J 'any("สวิตช์" in o["title"] for o in d["overdue"])')" "True"
ck "sla_days ตรงตามความเร่งด่วน" \
   "$(J 'all(o["sla_days"] == {"HIGH":1,"NORMAL":3,"LOW":7}[o["priority"]] for o in d["overdue"])')" "True"
ck "ใบ HIGH ที่ค้าง 5 วัน อยู่ในรายการ" \
   "$(J 'any("205" in o["title"] for o in d["overdue"])')" "True"
ck "ใบที่เพิ่งเปิดวันนี้ ไม่ถูกนับว่าค้าง" \
   "$(J "any(o['id'] == $TID_B for o in d['overdue'])")" "False"
ck "ใบที่ปิดแล้วไม่อยู่ในรายการค้าง" \
   "$(J "any(o['id'] == $TID_A for o in d['overdue'])")" "False"
endreq

# =====================================================================
# REQ-10 : ยืมครุภัณฑ์ที่ยังไม่ถูกคืน ไม่ได้
# =====================================================================
start "REQ-10" "ยืมชิ้นที่มีสัญญายืมค้างอยู่ ต้องได้ 409 ASSET_ON_LOAN"
# A-003 (id 3) คืนแล้วตาม seed → ยืมใหม่ได้ ใช้เป็นเคสสำเร็จ
req POST /api/loans '{"asset_id":3,"borrower":"ผู้ทดสอบระบบ"}'
ck "HTTP (ยืมของที่ว่าง)" "$CODE" "201"
LOAN_ID="$(J 'd["id"]')"
ck "ยังไม่คืน" "$(J 'd["returned_at"] is None')" "True"
req POST /api/loans '{"asset_id":3,"borrower":"ผู้ทดสอบระบบคนที่สอง"}'
ck "HTTP (ยืมซ้ำชิ้นเดิม)" "$CODE" "409"
ck_err "ASSET_ON_LOAN"
# A-001 (id 1) มีสัญญายืมค้างมาจาก seed
req POST /api/loans '{"asset_id":1,"borrower":"ผู้ทดสอบระบบ"}'
ck "HTTP (ยืมชิ้นที่ค้างจาก seed)" "$CODE" "409"
ck_err "ASSET_ON_LOAN"
req GET /api/assets
ck "สถานะครุภัณฑ์ A-001 คำนวณเป็น ON_LOAN" "$(J '[a for a in d if a["code"]=="A-001"][0]["status"]')" "ON_LOAN"
# คืนแล้วต้องยืมได้อีก
req POST "/api/loans/$LOAN_ID/return"
ck "HTTP (คืนของ)" "$CODE" "200"
ck "มีเวลาคืน" "$(J 'd["returned_at"] is not None')" "True"
req POST "/api/loans/$LOAN_ID/return"
ck "HTTP (คืนซ้ำ)" "$CODE" "404"
ck_err "NOT_FOUND"
req POST /api/loans '{"asset_id":3,"borrower":"ผู้ทดสอบระบบคนที่สอง"}'
ck "HTTP (ยืมใหม่หลังคืนแล้ว)" "$CODE" "201"
req POST "/api/loans/$(J 'd["id"]')/return" >/dev/null
endreq

# =====================================================================
# REQ-11 : ครุภัณฑ์ที่มีใบแจ้งซ่อมค้างอยู่ ยืมไม่ได้
# =====================================================================
start "REQ-11" "ยืมชิ้นที่มีใบซ่อมสถานะยังไม่ DONE ต้องได้ 409 ASSET_IN_REPAIR"
# A-005 (id 5) มีใบซ่อมสถานะ NEW มาจาก seed
req POST /api/loans '{"asset_id":5,"borrower":"ผู้ทดสอบระบบ"}'
ck "HTTP" "$CODE" "409"
ck_err "ASSET_IN_REPAIR"
req GET /api/assets
ck "สถานะครุภัณฑ์ A-005 คำนวณเป็น IN_REPAIR" "$(J '[a for a in d if a["code"]=="A-005"][0]["status"]')" "IN_REPAIR"
# A-004 มีใบซ่อมที่ปิดไปแล้วในข้อ REQ-05 → กลับมายืมได้
req POST /api/loans '{"asset_id":4,"borrower":"ผู้ทดสอบระบบ"}'
ck "HTTP (ใบซ่อมปิดแล้ว ยืมได้)" "$CODE" "201"
req POST "/api/loans/$(J 'd["id"]')/return" >/dev/null
req POST /api/loans '{"asset_id":999999,"borrower":"ผู้ทดสอบระบบ"}'
ck "HTTP (ไม่พบครุภัณฑ์)" "$CODE" "404"
ck_err "NOT_FOUND"
endreq

# =====================================================================
# REQ-12 : อะไหล่ที่เหลือต่ำกว่าจุดสั่งซื้อถูกทำเครื่องหมายเตือน
# =====================================================================
start "REQ-12" "อะไหล่ที่ qty_on_hand < reorder_point ปรากฏในรายการเตือน"
req GET /api/dashboard; save /tmp/dash12.json
ck "มีอะไหล่ในรายการเตือน" "$(Jf /tmp/dash12.json 'len(d["parts_low"]) >= 2')" "True"
ck "ทุกตัวในรายการต่ำกว่าจุดสั่งซื้อจริง" \
   "$(Jf /tmp/dash12.json 'all(p["qty_on_hand"] < p["reorder_point"] for p in d["parts_low"])')" "True"
ck "หลอดโปรเจกเตอร์ (2 < 5) อยู่ในรายการ" \
   "$(Jf /tmp/dash12.json 'any(p["sku"] == "LAMP-EPS-01" for p in d["parts_low"])')" "True"
ck "สาย HDMI (1 < 6) อยู่ในรายการ" \
   "$(Jf /tmp/dash12.json 'any(p["sku"] == "CBL-HDMI-3M" for p in d["parts_low"])')" "True"
# ต้องตรงกับธง below_reorder ของ /api/parts (คำนวณจากที่เดียวกัน)
req GET /api/parts
ck "จำนวนตรงกับธง below_reorder ของ /api/parts" \
   "$(J 'len([p for p in d if p["below_reorder"]])')" "$(Jf /tmp/dash12.json 'len(d["parts_low"])')"
ck "อะไหล่ที่ของเยอะ ไม่ถูกเตือน" "$(J '[p for p in d if p["id"]==5][0]["below_reorder"]')" "False"
# รับเข้าจนพ้นจุดสั่งซื้อ แล้วคำเตือนต้องหายไปเอง
req POST "/api/parts/4/move" '{"delta":10,"reason":"รับเข้าจากผู้ขาย"}'
ck "HTTP (รับสาย HDMI เข้า 10 เส้น)" "$CODE" "200"
ck "below_reorder กลายเป็น false" "$(J 'd["below_reorder"]')" "False"
req GET /api/dashboard
ck "หายจากรายการเตือนแล้ว" "$(J 'any(p["sku"] == "CBL-HDMI-3M" for p in d["parts_low"])')" "False"
req POST "/api/parts/4/move" '{"delta":-10,"reason":"คืนสภาพข้อมูลทดสอบ"}' >/dev/null
endreq

# ---------- สรุป ----------
rm -f "$BODY" /tmp/parts_before.json /tmp/parts_after.json /tmp/parts_b6.json \
      /tmp/parts_a6.json /tmp/dash.json /tmp/dash12.json
echo
echo "====================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "SUMMARY: ผ่านครบทุกข้อ REQ-01..REQ-12 (0 FAIL)"
    exit 0
else
    echo "SUMMARY: ไม่ผ่าน $FAILED ข้อ"
    exit 1
fi
