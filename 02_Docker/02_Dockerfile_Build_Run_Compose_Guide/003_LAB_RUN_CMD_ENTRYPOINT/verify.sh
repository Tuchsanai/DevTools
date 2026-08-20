#!/usr/bin/env bash
# verify.sh — ตรวจผลลัพธ์ของ LAB 3 (RUN vs CMD vs ENTRYPOINT) อัตโนมัติ
# รันจากในเครื่องเรียน ที่โฟลเดอร์ของแล็บนี้ :  bash verify.sh
# ผ่านทุกข้อ -> พิมพ์ ALL CHECKS PASSED และ exit 0

set -u

fail_count=0
pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; fail_count=$((fail_count + 1)); }

cd "$(dirname "$0")" || exit 1

# ตรวจก่อนว่า Docker daemon ตื่นแล้ว ไม่งั้นทุกข้อจะ FAIL ยกแผงโดยไม่บอกสาเหตุจริง
if ! docker info >/dev/null 2>&1; then
    echo '[FAIL] ต่อ Docker daemon ไม่ได้ — รอ dockerd ในเครื่องเรียนสัก 10-20 วินาทีแล้วลองใหม่'
    exit 1
fi

echo "== build image ทั้ง 11 ตัว (เงียบ ๆ) =="
build() {  # build <dockerfile> <tag>
    if docker build -q -f "$1" -t "$2" . >/dev/null 2>&1; then
        return 0
    fi
    fail "build $1 -> $2 ไม่สำเร็จ"
    return 1
}
build Dockerfile.run          demo-run
build Dockerfile.cmd          demo-cmd
build Dockerfile.entrypoint   demo-entrypoint
build Dockerfile.both         demo-both
build Dockerfile.multicmd     demo-multicmd
build Dockerfile.execform     demo-execform
build Dockerfile.shellform    demo-shellform
build Dockerfile.sigexec      demo-sigexec
build Dockerfile.sigshell     demo-sigshell
build Dockerfile.nocmd        demo-nocmd
build Dockerfile.nocmd_reset  demo-nocmd-reset
echo

# ---------- 6.1 RUN ----------
out=$(docker run --rm demo-run 2>&1)
if grep -q 'สร้างไฟล์ในขั้น Build' <<<"$out"; then
    pass '1. RUN สร้าง /message.txt ไว้ตอน build และ CMD อ่านออกมาได้'
else
    fail "1. demo-run ไม่ได้พิมพ์ข้อความจาก /message.txt (ได้: $out)"
fi

out=$(docker run --rm demo-run curl --version 2>&1)
if grep -q '^curl ' <<<"$out"; then
    pass '2. curl ที่ติดตั้งด้วย RUN ยังใช้ได้แม้แทนที่ CMD แล้ว'
else
    fail "2. demo-run curl --version ใช้ไม่ได้ (ได้: $out)"
fi

# ---------- 6.2 CMD ----------
out=$(docker run --rm demo-cmd 2>&1)
if grep -q 'ข้อความเริ่มต้นจาก CMD' <<<"$out"; then
    pass '3. รันเปล่า ๆ ได้ข้อความจาก CMD'
else
    fail "3. demo-cmd ไม่ได้ใช้ CMD เริ่มต้น (ได้: $out)"
fi

out=$(docker run --rm demo-cmd echo 'แทนที่CMDแล้ว' 2>&1)
if grep -q 'แทนที่CMDแล้ว' <<<"$out" && ! grep -q 'ข้อความเริ่มต้นจาก CMD' <<<"$out"; then
    pass '4. ค่าหลังชื่อ image แทนที่ CMD ทั้งชุด'
else
    fail "4. CMD ไม่ได้ถูกแทนที่อย่างที่คาด (ได้: $out)"
fi

# ---------- 6.3 ENTRYPOINT ----------
out=$(docker run --rm demo-entrypoint 2>&1)
if grep -q 'ข้อความจาก ENTRYPOINT:' <<<"$out"; then
    pass '5. รันเปล่า ๆ ได้ข้อความจาก ENTRYPOINT'
else
    fail "5. demo-entrypoint ไม่ทำงานตามคาด (ได้: $out)"
fi

out=$(docker run --rm demo-entrypoint สวัสดี Docker 2>&1)
if grep -q 'ข้อความจาก ENTRYPOINT: สวัสดี Docker' <<<"$out"; then
    pass '6. ค่าหลังชื่อ image ถูกต่อท้าย ENTRYPOINT เป็น argument'
else
    fail "6. ENTRYPOINT ไม่ได้ต่อ argument ตามคาด (ได้: $out)"
fi

out=$(docker run --rm --entrypoint sh demo-entrypoint -c 'echo overridden' 2>&1)
if grep -q '^overridden$' <<<"$out" && ! grep -q 'ข้อความจาก ENTRYPOINT:' <<<"$out"; then
    pass '7. --entrypoint แทนที่โปรแกรมหลักได้จริง'
else
    fail "7. --entrypoint ไม่ได้แทนที่ ENTRYPOINT (ได้: $out)"
fi

# ---------- 6.4 ENTRYPOINT + CMD ----------
out=$(docker run --rm demo-both 2>&1)
if grep -q '2 packets transmitted' <<<"$out"; then
    pass '8. รันเปล่า ๆ ได้ ping -c 2 127.0.0.1 จาก ENTRYPOINT+CMD'
else
    fail "8. demo-both ไม่ได้ใช้ CMD เริ่มต้น (ได้: $out)"
fi

out=$(docker run --rm demo-both -c 1 localhost 2>&1)
if grep -q '1 packets transmitted' <<<"$out"; then
    pass '9. argument ใหม่แทน CMD แต่ ENTRYPOINT (ping) ยังอยู่'
else
    fail "9. demo-both -c 1 localhost ไม่ทำงานตามคาด (ได้: $out)"
fi

# ---------- metadata ----------
meta() { docker image inspect --format '{{.Config.Entrypoint}}|{{.Config.Cmd}}' "$1" 2>/dev/null; }
ok=1
[ "$(meta demo-run)"        = "[]|[cat /message.txt]" ]                  || ok=0
[ "$(meta demo-cmd)"        = "[]|[echo ข้อความเริ่มต้นจาก CMD]" ]        || ok=0
[ "$(meta demo-entrypoint)" = "[echo ข้อความจาก ENTRYPOINT:]|[]" ]        || ok=0
[ "$(meta demo-both)"       = "[ping]|[-c 2 127.0.0.1]" ]                || ok=0
if [ "$ok" = 1 ]; then
    pass '10. metadata Entrypoint/Cmd ของทั้ง 4 image ตรงตามที่ Dockerfile เขียนไว้'
else
    fail "10. metadata ไม่ตรง: run=$(meta demo-run) cmd=$(meta demo-cmd) ep=$(meta demo-entrypoint) both=$(meta demo-both)"
fi

# ---------- CMD หลายบรรทัด ----------
m=$(meta demo-multicmd)
out=$(docker run --rm demo-multicmd 2>&1)
if grep -q 'ตัวสุดท้าย' <<<"$m" && ! grep -q 'ตัวแรก' <<<"$m" \
   && grep -q 'ตัวสุดท้าย' <<<"$out" && ! grep -q 'ตัวแรก' <<<"$out"; then
    pass '11. CMD หลายบรรทัด มีผลเฉพาะบรรทัดสุดท้าย'
else
    fail "11. CMD หลายบรรทัดไม่เป็นไปตามคาด (meta=$m out=$out)"
fi

# ---------- exec form vs shell form : PID 1 ----------
docker rm -f v-sigexec v-sigshell >/dev/null 2>&1
docker run -d --name v-sigexec  demo-sigexec  >/dev/null 2>&1
docker run -d --name v-sigshell demo-sigshell >/dev/null 2>&1
sleep 2

pid1_exec=$(docker exec v-sigexec  ps -o pid,args 2>/dev/null | awk '$1==1{$1="";print}')
pid1_shell=$(docker exec v-sigshell ps -o pid,args 2>/dev/null | awk '$1==1{$1="";print}')
if grep -q 'app.sh' <<<"$pid1_exec" && ! grep -q 'sh -c' <<<"$pid1_exec" \
   && grep -q 'sh -c' <<<"$pid1_shell"; then
    pass '12. exec form: PID 1 = แอปเอง · shell form: PID 1 = /bin/sh -c'
else
    fail "12. PID 1 ไม่ตรงตามคาด (exec='$pid1_exec' shell='$pid1_shell')"
fi

# ---------- exec form vs shell form : เวลาที่ docker stop ใช้ ----------
t_ms() {  # t_ms <container>
    local s e
    s=$(date +%s%N); docker stop "$1" >/dev/null 2>&1; e=$(date +%s%N)
    echo $(( (e - s) / 1000000 ))
}
ms_exec=$(t_ms v-sigexec)
ms_shell=$(t_ms v-sigshell)
if [ "$ms_exec" -lt 3000 ] && [ "$ms_shell" -ge 9000 ]; then
    pass "13. docker stop: exec form ${ms_exec} ms (<3s) · shell form ${ms_shell} ms (รอ SIGKILL ครบ 10s)"
else
    fail "13. เวลาที่ docker stop ใช้ไม่ตรงตามคาด (exec=${ms_exec}ms shell=${ms_shell}ms)"
fi

log_exec=$(docker logs v-sigexec 2>&1)
log_shell=$(docker logs v-sigshell 2>&1)
if grep -q 'ได้รับ SIGTERM' <<<"$log_exec" && ! grep -q 'ได้รับ SIGTERM' <<<"$log_shell"; then
    pass '14. exec form เท่านั้นที่แอปได้รับ SIGTERM (shell form ไม่ส่งต่อให้ลูก)'
else
    fail "14. log SIGTERM ไม่ตรงตามคาด (exec='$log_exec' shell='$log_shell')"
fi

docker rm -f v-sigexec v-sigshell >/dev/null 2>&1

# ---------- sleep exec/shell form : busybox ash exec optimization ----------
docker rm -f v-exec v-shell >/dev/null 2>&1
docker run -d --name v-exec  demo-execform  >/dev/null 2>&1
docker run -d --name v-shell demo-shellform >/dev/null 2>&1
sleep 1
p_e=$(docker exec v-exec  ps -o pid,args 2>/dev/null | awk '$1==1{$1="";print}')
p_s=$(docker exec v-shell ps -o pid,args 2>/dev/null | awk '$1==1{$1="";print}')
if grep -q 'sleep 300' <<<"$p_e" && grep -q 'sleep 300' <<<"$p_s" && ! grep -q 'sh -c' <<<"$p_s"; then
    pass '15. CMD sleep 300 (shell form คำสั่งเดียว) ถูก ash แทนตัวเองด้วย exec จึงได้ PID 1 เหมือน exec form'
else
    fail "15. พฤติกรรม exec optimization ของ busybox ash ไม่ตรงตามคาด (exec='$p_e' shell='$p_s')"
fi
docker rm -f v-exec v-shell >/dev/null 2>&1

# ---------- ทำให้พัง ----------
out=$(docker run --rm demo-nocmd 2>&1); st=$?
m=$(meta demo-nocmd)
if [ "$st" -eq 0 ] && [ "$m" = "[]|[/bin/sh]" ]; then
    pass '16. Dockerfile ที่ไม่มี CMD/ENTRYPOINT ยังรันได้ เพราะสืบทอด CMD [/bin/sh] มาจาก base image'
else
    fail "16. demo-nocmd ไม่เป็นไปตามคาด (exit=$st meta=$m out=$out)"
fi

out=$(docker run --rm demo-nocmd-reset 2>&1); st=$?
if [ "$st" -ne 0 ] && grep -qi 'no command specified' <<<"$out"; then
    pass '17. ล้าง ENTRYPOINT []/CMD [] แล้ว docker run พังจริงด้วย no command specified'
else
    fail "17. demo-nocmd-reset ไม่ได้พังตามคาด (exit=$st out=$out)"
fi

out=$(docker run --rm demo-both -c abc 2>&1); st=$?
if [ "$st" -ne 0 ] && grep -qi "invalid number 'abc'" <<<"$out"; then
    pass '18. ส่ง argument ผิดให้ ENTRYPOINT (ping -c abc) แล้ว ping ฟ้อง error จริง'
else
    fail "18. demo-both -c abc ไม่ได้ฟ้อง error ตามคาด (exit=$st out=$out)"
fi

echo
if [ "$fail_count" -eq 0 ]; then
    echo 'ALL CHECKS PASSED'
    exit 0
fi
printf '%d CHECK(S) FAILED\n' "$fail_count"
exit 1
