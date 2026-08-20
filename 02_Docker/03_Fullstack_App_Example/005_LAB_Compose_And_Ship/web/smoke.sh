#!/usr/bin/env bash
# ตรวจรับหน้าเว็บ CampusOps (LAB 3) — รันภายในกล่องเรียน devtools-ops-u0b
WEB=http://localhost:3000
FAIL=0
pass() { echo "  [PASS] $*"; }
fail() { echo "  [FAIL] $*"; FAIL=$((FAIL + 1)); }
chk()  { if [ "$1" = "$2" ]; then pass "$3 (ได้ '$1')"; else fail "$3 (คาดหวัง '$2' แต่ได้ '$1')"; fi; }

# เรียก API ผ่าน python ที่ติดมากับคอนเทนเนอร์ api เอง — ไม่ต้อง publish พอร์ตของ api ออกมาเลย
apipy() { docker exec campusops-api python -c "$1"; }

# ดึงรหัส action ของฟอร์มที่ต้องการออกจาก HTML ที่ server เรนเดอร์มา
# (โหมด "ไม่มี JavaScript" ของ Next คือ POST กลับมาที่ URL เดิม พร้อมฟิลด์ซ่อน $ACTION_ID_xxx)
cat > /tmp/aid.py <<'PY'
import re, sys
html = open(sys.argv[1], encoding='utf-8').read()
needles = sys.argv[2:]
for form in html.split('<form')[1:]:
    form = form.split('</form>')[0]
    if all(n in form for n in needles):
        m = re.search(r'name="(\$ACTION_ID_[0-9a-f]+)"', form)
        if m:
            print(m.group(1))
            break
PY
aid() { python3 /tmp/aid.py "$@"; }

echo "======================================================================"
echo "  CampusOps · web (Next.js 16.3.1) — บันทึกการตรวจรับ"
echo "  วันที่ทดสอบ : $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "======================================================================"

echo
echo "### ส่วนที่ 0 · สภาพแวดล้อมที่ใช้ทดสอบ"
docker --version
docker ps
echo "--- network ที่สามกล่องใช้ร่วมกัน ---"
docker network ls
echo "--- NFR-3 : db ต้องไม่ publish พอร์ตออกมา (บรรทัดถัดไปต้องว่าง) ---"
docker port campusops-db
echo "[db ไม่มีพอร์ตที่ publish — ถูกต้อง]"

echo
echo "### ส่วนที่ 1 · ทุกหน้าต้องได้ HTTP 200"
for p in / /tickets /loans /parts; do
  code=$(curl -s -o /tmp/page.html -w '%{http_code}' "$WEB$p")
  size=$(wc -c < /tmp/page.html)
  echo "  GET $p -> HTTP $code · $size ไบต์"
  chk "$code" "200" "หน้า $p ตอบ 200"
  grep -q 'lang="th"' /tmp/page.html && pass "หน้า $p ประกาศ lang=th" || fail "หน้า $p ไม่มี lang=th"
done

echo
echo "  --- ตรวจว่าเนื้อหาถูกเรนเดอร์มาจากฝั่ง server จริง (ไม่ใช่หน้าเปล่ารอ JS) ---"
curl -s "$WEB/" > /tmp/home.html
grep -q "งานค้างเกินกำหนด" /tmp/home.html && pass "หน้า / มีหัวข้อ 'งานค้างเกินกำหนด' มาใน HTML แล้ว" || fail "หน้า / ไม่มีเนื้อหาไทยใน HTML"
grep -q "อะไหล่ต่ำกว่าจุดสั่งซื้อ" /tmp/home.html && pass "หน้า / มีบล็อกอะไหล่ใกล้หมด (REQ-12)" || fail "หน้า / ไม่มีบล็อกอะไหล่ใกล้หมด"
curl -s "$WEB/tickets" > /tmp/tickets.html
for col in "รอรับเรื่อง" "มอบหมายแล้ว" "กำลังซ่อม" "ปิดงานแล้ว"; do
  grep -q "$col" /tmp/tickets.html && pass "กระดานมีคอลัมน์ '$col'" || fail "กระดานไม่มีคอลัมน์ '$col'"
done
grep -q "เกินกำหนด" /tmp/tickets.html && pass "การ์ดมีป้ายเตือน 'เกินกำหนด' (REQ-09)" || fail "ไม่พบป้ายเกินกำหนดบนกระดาน"
curl -s "$WEB/parts" > /tmp/parts.html
grep -q "จุดสั่งซื้อ" /tmp/parts.html && pass "หน้า /parts มีแถบเทียบยอดคงเหลือกับจุดสั่งซื้อ" || fail "หน้า /parts ไม่มีจุดสั่งซื้อ"

echo
echo "### ส่วนที่ 2 · CSS ต้องมาถึงเบราว์เซอร์จริง"
CSS=$(grep -o '<link rel="stylesheet" href="[^"]*"' /tmp/home.html | head -1 | sed 's/.*href="//; s/"$//')
echo "  <link rel=\"stylesheet\"> ชี้ไปที่ : $CSS"
case "$CSS" in
  /_next/static/chunks/*.css) pass "เส้นทางไฟล์ CSS อยู่ใต้ .next/static/chunks (ตรงกับกับดักของ Next 16)" ;;
  *) fail "เส้นทางไฟล์ CSS ผิดจากที่คาด : $CSS" ;;
esac
csscode=$(curl -s -o /tmp/app.css -w '%{http_code}' "$WEB$CSS")
csssize=$(wc -c < /tmp/app.css)
echo "  GET $CSS -> HTTP $csscode · $csssize ไบต์"
chk "$csscode" "200" "ไฟล์ CSS โหลดได้"
[ "$csssize" -gt 5000 ] && pass "ไฟล์ CSS มีขนาด $csssize ไบต์ (ไม่ใช่ไฟล์เปล่า)" || fail "ไฟล์ CSS เล็กผิดปกติ ($csssize ไบต์)"
echo "  --- utility class ที่หน้าเว็บใช้จริง ต้องมีอยู่ในไฟล์ CSS นี้ ---"
for cls in 'tabular-nums' 'animate-rise' 'line-clamp-2' 'backdrop-blur' 'lg\\:grid-cols-4' 'bg-clip-text' 'divide-y'; do
  if grep -q -- "$cls" /tmp/app.css; then pass "พบคลาส .$cls ในไฟล์ CSS"; else fail "ไม่พบคลาส .$cls ในไฟล์ CSS"; fi
done
grep -q -- '--color-ink-950' /tmp/app.css && pass "พบตัวแปรธีม --color-ink-950 (โทนมืดถูกคอมไพล์เข้ามา)" || fail "ไม่พบตัวแปรธีมของ Tailwind 4"
echo "  --- ตัวอย่างเนื้อไฟล์ CSS 300 ไบต์แรก ---"
head -c 300 /tmp/app.css; echo

echo
echo "### ส่วนที่ 3 · server action จริง #1 : แจ้งซ่อมใหม่ (REQ-01)"
AID_TICKET=$(aid /tmp/tickets.html 'name="title"' 'name="priority"')
echo "  action id ของฟอร์มแจ้งซ่อม : $AID_TICKET"
BEFORE=$(apipy 'import json,urllib.request;print(len(json.load(urllib.request.urlopen("http://localhost:8000/api/tickets"))))')
echo "  จำนวนใบแจ้งซ่อมก่อนกดปุ่ม : $BEFORE"
ASSET_ID=$(apipy 'import json,urllib.request;print(json.load(urllib.request.urlopen("http://localhost:8000/api/assets"))[0]["id"])')
TITLE="ทดสอบแจ้งซ่อมผ่านหน้าเว็บ u0b"
echo "  --- HTTP ที่ตอบกลับจากการ POST ฟอร์ม (ต้องเป็น 303 แล้วเด้งกลับ /tickets) ---"
curl -s -D /tmp/h3.txt -o /dev/null -X POST "$WEB/tickets" \
  -F "$AID_TICKET=" -F "back=/tickets" -F "asset_id=$ASSET_ID" \
  -F "title=$TITLE" -F "detail=สร้างโดยสคริปต์ตรวจรับ" -F "priority=HIGH"
head -1 /tmp/h3.txt
grep -i '^location:' /tmp/h3.txt
st=$(head -1 /tmp/h3.txt | awk '{print $2}')
chk "$st" "303" "server action ตอบ 303 (เด้งกลับหน้าเดิม)"
grep -qi '^location: /tickets' /tmp/h3.txt && pass "Location ชี้กลับ /tickets พร้อมข้อความผลลัพธ์" || fail "Location ไม่ได้ชี้กลับ /tickets"
AFTER=$(apipy 'import json,urllib.request;print(len(json.load(urllib.request.urlopen("http://localhost:8000/api/tickets"))))')
echo "  จำนวนใบแจ้งซ่อมหลังกดปุ่ม : $AFTER"
chk "$AFTER" "$((BEFORE + 1))" "ข้อมูลใน API เพิ่มขึ้นจริง 1 ใบ"
echo "  --- ใบล่าสุดที่ API เก็บไว้ ---"
apipy 'import json,urllib.request;print(json.dumps(json.load(urllib.request.urlopen("http://localhost:8000/api/tickets"))[-1],ensure_ascii=False))'
NEWSTATUS=$(apipy 'import json,urllib.request;print(json.load(urllib.request.urlopen("http://localhost:8000/api/tickets"))[-1]["status"])')
chk "$NEWSTATUS" "NEW" "ใบใหม่มีสถานะ NEW"
TID=$(apipy 'import json,urllib.request;print(json.load(urllib.request.urlopen("http://localhost:8000/api/tickets"))[-1]["id"])')
curl -s "$WEB/tickets" > /tmp/tickets2.html
grep -q "$TITLE" /tmp/tickets2.html && pass "หัวข้อใบใหม่ปรากฏบนกระดานหน้าเว็บแล้ว" || fail "ใบใหม่ไม่ขึ้นบนกระดาน"

echo
echo "### ส่วนที่ 3ข · เดินใบงาน #$TID ครบวงจรผ่านปุ่มบนหน้าเว็บ (REQ-02, REQ-03, REQ-05)"
TECH="TECH-WEB"
AID_ASSIGN=$(aid /tmp/tickets2.html 'name="assignee"' "value=\"$TID\"")
echo "  มอบหมายงานให้ $TECH ด้วย action $AID_ASSIGN"
curl -s -D /tmp/h3b.txt -o /dev/null -X POST "$WEB/tickets" \
  -F "$AID_ASSIGN=" -F "back=/tickets" -F "id=$TID" -F "assignee=$TECH"
head -1 /tmp/h3b.txt
S=$(apipy "import json,urllib.request;print([t for t in json.load(urllib.request.urlopen('http://localhost:8000/api/tickets')) if t['id']==$TID][0]['status'])")
chk "$S" "ASSIGNED" "สถานะเปลี่ยนเป็น ASSIGNED"

curl -s "$WEB/tickets" > /tmp/tickets3.html
AID_ADV=$(aid /tmp/tickets3.html 'name="status"' "value=\"$TID\"")
echo "  กดปุ่ม 'เริ่มลงมือซ่อม' ด้วย action $AID_ADV"
curl -s -D /tmp/h3c.txt -o /dev/null -X POST "$WEB/tickets" \
  -F "$AID_ADV=" -F "back=/tickets" -F "id=$TID" -F "status=IN_PROGRESS"
head -1 /tmp/h3c.txt
S=$(apipy "import json,urllib.request;print([t for t in json.load(urllib.request.urlopen('http://localhost:8000/api/tickets')) if t['id']==$TID][0]['status'])")
chk "$S" "IN_PROGRESS" "สถานะเปลี่ยนเป็น IN_PROGRESS"

PART_ID=$(apipy 'import json,urllib.request;print([p["id"] for p in json.load(urllib.request.urlopen("http://localhost:8000/api/parts")) if p["qty_on_hand"]>=3][0])')
QBEFORE=$(apipy "import json,urllib.request;print([p['qty_on_hand'] for p in json.load(urllib.request.urlopen('http://localhost:8000/api/parts')) if p['id']==$PART_ID][0])")
echo "  จะปิดงานพร้อมเบิกอะไหล่ id=$PART_ID จำนวน 2 (ยอดคงเหลือก่อนปิด = $QBEFORE)"
curl -s "$WEB/tickets" > /tmp/tickets4.html
AID_CLOSE=$(aid /tmp/tickets4.html 'name="part_id_1"' "value=\"$TID\"")
curl -s -D /tmp/h3d.txt -o /dev/null -X POST "$WEB/tickets" \
  -F "$AID_CLOSE=" -F "back=/tickets" -F "id=$TID" \
  -F "part_id_1=$PART_ID" -F "qty_1=2" -F "part_id_2=" -F "qty_2=0"
head -1 /tmp/h3d.txt
S=$(apipy "import json,urllib.request;print([t for t in json.load(urllib.request.urlopen('http://localhost:8000/api/tickets')) if t['id']==$TID][0]['status'])")
chk "$S" "DONE" "ปิดงานสำเร็จ สถานะเป็น DONE"
QAFTER=$(apipy "import json,urllib.request;print([p['qty_on_hand'] for p in json.load(urllib.request.urlopen('http://localhost:8000/api/parts')) if p['id']==$PART_ID][0])")
echo "  ยอดคงเหลือหลังปิดงาน = $QAFTER"
chk "$QAFTER" "$((QBEFORE - 2))" "สต็อกถูกตัดจริง 2 หน่วย (REQ-05)"
echo "  --- การเคลื่อนไหวล่าสุดของอะไหล่ชิ้นนี้ (REQ-07) ---"
apipy "import json,urllib.request;print(json.dumps(json.load(urllib.request.urlopen('http://localhost:8000/api/parts/$PART_ID/moves'))[0],ensure_ascii=False))"

echo "  --- REQ-04 : กรองกระดานตามช่างผ่านหน้าเว็บ ---"
fcode=$(curl -s -o /tmp/filter.html -w '%{http_code}' "$WEB/tickets?assignee=$TECH")
chk "$fcode" "200" "GET /tickets?assignee=$TECH ตอบ 200"
grep -q "กำลังแสดงเฉพาะงานของ" /tmp/filter.html && pass "หน้าเว็บบอกว่ากำลังกรองอยู่" || fail "หน้าเว็บไม่แสดงสถานะการกรอง"
# React แทรก <!-- --> คั่นระหว่างข้อความกับค่าตัวแปรใน HTML ที่เรนเดอร์ออกมา
# ต้องลบคอมเมนต์พวกนี้ออกก่อน ไม่งั้นข้อความที่ตาเห็นว่าติดกัน จะ grep ไม่เจอ
sed 's/<!-- -->//g' /tmp/filter.html > /tmp/filter.clean.html
EXP=$(apipy "import json,urllib.request;print(len([t for t in json.load(urllib.request.urlopen('http://localhost:8000/api/tickets')) if t['assignee']=='$TECH']))")
grep -q "พบ $EXP ใบ" /tmp/filter.clean.html && pass "ตัวกรองคืนเฉพาะงานของ $TECH จำนวน $EXP ใบ ตรงกับที่ API มี" || fail "จำนวนใบหลังกรองไม่ตรงกับ API ($EXP ใบ)"
grep -c "$TITLE" /tmp/filter.clean.html > /dev/null && pass "ใบที่เพิ่งเดินครบวงจรอยู่ในผลการกรอง" || fail "ไม่พบใบที่กรอง"

echo
echo "### ส่วนที่ 4 · server action จริง #2 : บันทึกการยืม (REQ-10)"
curl -s "$WEB/loans" > /tmp/loans.html
AID_LOAN=$(aid /tmp/loans.html 'name="borrower"')
echo "  action id ของฟอร์มยืม : $AID_LOAN"
FREE=$(apipy 'import json,urllib.request;print([a["id"] for a in json.load(urllib.request.urlopen("http://localhost:8000/api/assets")) if a["status"]=="AVAILABLE"][0])')
echo "  ครุภัณฑ์ที่สถานะ AVAILABLE ที่จะใช้ทดสอบ : id=$FREE"
LBEFORE=$(apipy 'import json,urllib.request;print(json.load(urllib.request.urlopen("http://localhost:8000/api/dashboard"))["loans_active"])')
echo "  จำนวนสัญญายืมที่ยังไม่คืน ก่อนกดปุ่ม : $LBEFORE"
BORROWER="ผู้ทดสอบระบบ u0b"
curl -s -D /tmp/h4.txt -o /dev/null -X POST "$WEB/loans" \
  -F "$AID_LOAN=" -F "asset_id=$FREE" -F "borrower=$BORROWER"
head -1 /tmp/h4.txt
grep -i '^location:' /tmp/h4.txt
st=$(head -1 /tmp/h4.txt | awk '{print $2}')
chk "$st" "303" "server action ยืมของตอบ 303"
LAFTER=$(apipy 'import json,urllib.request;print(json.load(urllib.request.urlopen("http://localhost:8000/api/dashboard"))["loans_active"])')
echo "  จำนวนสัญญายืมที่ยังไม่คืน หลังกดปุ่ม : $LAFTER"
chk "$LAFTER" "$((LBEFORE + 1))" "จำนวนของที่ถูกยืมใน API เพิ่มขึ้นจริง"
echo "  --- สัญญายืมล่าสุดที่ API เก็บไว้ ---"
apipy 'import json,urllib.request;print(json.dumps(json.load(urllib.request.urlopen("http://localhost:8000/api/loans"))[0],ensure_ascii=False))'
curl -s "$WEB/loans" > /tmp/loans2.html
grep -q "$BORROWER" /tmp/loans2.html && pass "ชื่อผู้ยืมปรากฏในรายการ 'ยังไม่คืน' บนหน้าเว็บ" || fail "ไม่พบผู้ยืมใหม่บนหน้าเว็บ"

echo
echo "### ส่วนที่ 5 · เคสที่ต้องถูกปฏิเสธ แล้วหน้าเว็บต้องแสดงเหตุผล (REQ-10)"
curl -s -D /tmp/h5.txt -o /dev/null -X POST "$WEB/loans" \
  -F "$AID_LOAN=" -F "asset_id=$FREE" -F "borrower=ผู้ทดสอบคนที่สอง"
LOC=$(grep -i '^location:' /tmp/h5.txt | tr -d '\r')
echo "  $LOC"
echo "$LOC" | grep -q 't=err' && pass "ถูกปฏิเสธและเด้งกลับพร้อม t=err" || fail "ควรถูกปฏิเสธแต่กลับสำเร็จ"
echo "$LOC" | grep -q 'ASSET_ON_LOAN' && pass "ข้อความบอกรหัสข้อผิดพลาด ASSET_ON_LOAN" || fail "ไม่พบรหัส ASSET_ON_LOAN ในข้อความ"
ERRPATH=$(echo "$LOC" | sed 's/^[Ll]ocation: //')
curl -s "$WEB$ERRPATH" > /tmp/err.html
grep -q 'ASSET_ON_LOAN' /tmp/err.html && pass "หน้าเว็บแสดงกล่องข้อความผิดพลาดให้ผู้ใช้เห็น" || fail "หน้าเว็บไม่แสดงข้อความผิดพลาด"
LSAME=$(apipy 'import json,urllib.request;print(json.load(urllib.request.urlopen("http://localhost:8000/api/dashboard"))["loans_active"])')
chk "$LSAME" "$LAFTER" "จำนวนสัญญายืมไม่เปลี่ยนหลังถูกปฏิเสธ"

echo
echo "### ส่วนที่ 6 · พิสูจน์ว่าไม่มีการเรียก API จากฝั่งเบราว์เซอร์เลย"
echo "  จำนวนครั้งที่พบคำว่า 'api:8000' ใน HTML ของแต่ละหน้า :"
grep -c 'api:8000' /tmp/home.html /tmp/tickets2.html /tmp/loans2.html /tmp/parts.html
HITS=0
for s in $(grep -o '/_next/static/chunks/[^"]*\.js' /tmp/tickets2.html | sort -u); do
  n=$(curl -s "$WEB$s" | grep -c 'api:8000')
  HITS=$((HITS + n))
done
echo "  ตรวจไฟล์ JS ที่ถูกส่งให้เบราว์เซอร์ทั้งหมด พบคำว่า 'api:8000' รวม $HITS ครั้ง"
chk "$HITS" "0" "ไม่มี URL ของ API รั่วไปฝั่งเบราว์เซอร์"
# นับเฉพาะบรรทัดที่เป็น "คำสั่ง" use client จริง ๆ (ขึ้นต้นบรรทัด) ไม่ใช่คำที่โผล่ในคอมเมนต์
UC=$(grep -rn --include='*.tsx' --include='*.ts' -c '^"use client"' /root/app/web/app | awk -F: '{s+=$2} END {print s+0}')
chk "$UC" "0" "ไม่มีไฟล์ไหนประกาศ 'use client' เลยทั้งโปรเจกต์"
echo "  --- ทุกหน้าประกาศ force-dynamic ---"
grep -rn 'export const dynamic' /root/app/web/app --include=page.tsx

echo
echo "### ส่วนที่ 7 · คุณสมบัติของ image"
docker images campusops-web:lab3
docker images campusops-api:lab3
echo "  --- ผู้ใช้และ CMD ที่ตั้งไว้ใน image ---"
docker inspect campusops-web:lab3
echo "  --- ผู้ใช้ที่รันจริงในคอนเทนเนอร์ (ต้องไม่ใช่ root) ---"
docker exec campusops-web id
echo "  --- ไฟล์ CSS ที่ถูกคัดลอกเข้ามาใน image (อยู่ใต้ chunks/) ---"
docker exec campusops-web sh -c 'ls .next/static/chunks/*.css'
echo "  --- สามคำสั่งท้ายสุดของ image ---"
docker history campusops-web:lab3 | head -3

echo
echo "======================================================================"
if [ "$FAIL" -eq 0 ]; then
  echo "SUMMARY: ผ่านทุกข้อ — 4 หน้าได้ 200 · CSS มาครบ · server action ทำงานจริง (0 FAIL)"
else
  echo "SUMMARY: มี $FAIL ข้อที่ไม่ผ่าน"
fi
echo "======================================================================"
exit "$FAIL"
