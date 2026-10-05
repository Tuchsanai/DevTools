#!/bin/bash
# start.sh — entrypoint ของ k8s-lab container (devtools + kind)
#   1) sshd        (port 22)   : root / passwd หรือ key devtoolSSH (map ./Devtool_SSH มา)
#   2) dockerd     (Docker-in-Docker, ต้อง --privileged) — kind ใช้สร้าง node เป็น container
#   3) k8s-up      (ถ้า KIND_AUTO_CREATE=1) : สร้าง kind cluster "lab" แบบ background
#   4) jupyter lab (port 8888) : ไม่มีรหัสผ่าน (ตั้งได้ด้วย $JUPYTER_PASSWORD)
#   NodePort 30080-30082 ของคลัสเตอร์ถูก map ออกมาที่ container (ดู kind-lab.yaml)
# ถ้ารันแบบมี tty (-it) จะเปิด bash ให้; ถ้ารันแบบ -d จะ tail log แทนเพื่อให้ container ไม่ดับ

# --- cgroup v2 nesting (ต้องทำก่อน sshd/dockerd/คำสั่งอื่นทั้งหมด) ----------------
# kind node รัน systemd ข้างใน ซึ่งต้องใช้ controller memory/io ด้วย ไม่งั้นจะล้มด้วย
#   "Failed to create /init.scope control group: Structure needs cleaning"
# บน cgroup v2 ถ้ายังมี process อยู่ใน root cgroup ของ container ตอนที่ dockerd/runc
# สร้าง /sys/fs/cgroup/docker ขึ้นมา cgroup จะถูกตั้งเป็น threaded และเปิด memory/io ไม่ได้อีกเลย
# จึงย้ายทุก process ไปไว้ใน /sys/fs/cgroup/init ก่อน แล้วเปิด controller ทั้งหมดให้ลูก
# (วิธีเดียวกับ entrypoint ของ docker:dind) — ระบบ cgroup v1 ไม่มีไฟล์นี้ จึงข้ามไป
CG=/sys/fs/cgroup
if [ -f "$CG/cgroup.controllers" ]; then
    mkdir -p "$CG/init"
    xargs -rn1 < "$CG/cgroup.procs" > "$CG/init/cgroup.procs" 2>/dev/null || :
    if ! sed -e 's/ / +/g' -e 's/^/+/' < "$CG/cgroup.controllers" \
            > "$CG/cgroup.subtree_control" 2>/dev/null; then
        # เปิดทั้งชุดไม่ได้ → ลองเปิดทีละ controller แล้วรายงานตัวที่เปิดไม่ได้
        echo "[start.sh] warning: cannot enable all cgroup v2 controllers at once, trying one by one"
        for c in $(cat "$CG/cgroup.controllers"); do
            echo "+$c" > "$CG/cgroup.subtree_control" 2>/dev/null \
                || echo "[start.sh] warning: cannot enable cgroup v2 controller: $c"
        done
    fi
    echo "[start.sh] cgroup v2 controllers: $(cat "$CG/cgroup.subtree_control")"
fi

mkdir -p /run/sshd
ssh-keygen -A >/dev/null 2>&1

# --- SSH key login ------------------------------------------------------------
# โฟลเดอร์ key = /etc/devtools/ssh (map volume มาจาก ./Devtool_SSH บน host)
#   - มี devtoolSSH + devtoolSSH.pub อยู่แล้ว (key สำเร็จรูปของ lab) → ใช้คู่นั้น
#   - ยังไม่มี → สร้างคู่ใหม่ลงโฟลเดอร์นั้นเลย นศ. หยิบ private key จาก host ไปใช้ได้ทันที
# public key ถูก copy เข้า /root/.ssh/authorized_keys (ไม่ mount ตรง เพราะ sshd ต้องการ
# owner=root และ permission 600 — bind mount จาก Windows จะเป็น 777 ทำให้ sshd ปฏิเสธ key)
SSH_KEY_DIR="${SSH_KEY_DIR:-/etc/devtools/ssh}"
SSH_KEY="$SSH_KEY_DIR/devtoolSSH"
install -d -m 700 /root/.ssh
touch /root/.ssh/authorized_keys
mkdir -p "$SSH_KEY_DIR" 2>/dev/null
if [ ! -s "$SSH_KEY.pub" ] && [ -w "$SSH_KEY_DIR" ]; then
    rm -f "$SSH_KEY" "$SSH_KEY.pub"
    ssh-keygen -q -t ed25519 -f "$SSH_KEY" -N "" -C devtools-lab
    # ให้ไฟล์เป็นของ user เจ้าของโฟลเดอร์บน host (Linux host ที่ไม่ใช่ root จะได้อ่าน key ได้)
    chown "$(stat -c %u:%g "$SSH_KEY_DIR")" "$SSH_KEY" "$SSH_KEY.pub" 2>/dev/null
    echo "[start.sh] generated new SSH key pair: $SSH_KEY{,.pub}"
fi
if [ -s "$SSH_KEY.pub" ]; then
    KEY_LINE="$(tr -d '\r' < "$SSH_KEY.pub" | head -n1)"
    grep -qxF "$KEY_LINE" /root/.ssh/authorized_keys || echo "$KEY_LINE" >> /root/.ssh/authorized_keys
    echo "[start.sh] SSH key login enabled: $SSH_KEY.pub"
else
    echo "[start.sh] no $SSH_KEY.pub — SSH key login disabled (password login still works)"
fi
chmod 600 /root/.ssh/authorized_keys
chown -R root:root /root/.ssh

/usr/sbin/sshd

# --- ไฟล์ตัวอย่าง -------------------------------------------------------------
# copy ตัวอย่างจาก image (/opt/k8s-lab/examples) ไปไว้ที่ /workspace/examples ครั้งแรกเท่านั้น
# ถ้ามีโฟลเดอร์อยู่แล้ว (เช่น /workspace เป็น volume ที่ นศ. แก้ไฟล์ไว้) จะไม่ copy ทับของเดิม
if [ ! -e /workspace/examples ] && [ -d /opt/k8s-lab/examples ]; then
    mkdir -p /workspace
    cp -r /opt/k8s-lab/examples /workspace/examples
    echo "[start.sh] copied examples → /workspace/examples"
fi

# --- ลบ pid file ค้างจากรอบก่อน ------------------------------------------------
# หลัง 'docker restart k8s-lab' ไฟล์ pid ของ dockerd/containerd ยังค้างอยู่ใน writable layer
# ของ container และ PID เดิมอาจถูก process อื่นในรอบนี้ใช้ไปแล้ว (เช่น sshd) dockerd จะเข้าใจว่า
# มีตัวเองรันอยู่แล้วและไม่ยอมขึ้น ("process with PID .. is still running")
# ลบทิ้งได้อย่างปลอดภัย เพราะ start.sh คือ PID 1 ที่เพิ่งเริ่ม ยังไม่มี dockerd ตัวใดรันแน่นอน
rm -f /var/run/docker.pid /var/run/docker/containerd/containerd.pid

dockerd > /var/log/dockerd.log 2>&1 &

# --- kind cluster (optional) ------------------------------------------------
# KIND_AUTO_CREATE=1 → รัน k8s-up แบบ background (รอ dockerd พร้อมเอง) log อยู่ที่ /var/log/k8s-up.log
# ค่าเริ่มต้น 0 = ไม่สร้างอัตโนมัติ (นักศึกษาสั่ง k8s-up เองตอนเรียน)
KIND_AUTO_CREATE="${KIND_AUTO_CREATE:-0}"
if [ "$KIND_AUTO_CREATE" = "1" ]; then
    nohup /usr/local/bin/k8s-up > /var/log/k8s-up.log 2>&1 &
    echo "[start.sh] KIND_AUTO_CREATE=1 → creating kind cluster in background (log: /var/log/k8s-up.log)"
fi

# --- JupyterLab -------------------------------------------------------------
# ค่าเริ่มต้น: ไม่มีรหัสผ่าน (เปิด http://localhost:8888 ได้เลย)
# ถ้าต้องการรหัสผ่านให้รันด้วย -e JUPYTER_PASSWORD=xxx (hash เก็บในไฟล์ config ไม่โชว์บน ps)
export JUPYTER_PASSWORD="${JUPYTER_PASSWORD:-}"
mkdir -p /root/.jupyter
python3 - <<'PY'
import json, os
from jupyter_server.auth import passwd
pw = os.environ.get("JUPYTER_PASSWORD", "")
cfg = {"PasswordIdentityProvider": {"hashed_password": passwd(pw) if pw else ""}}
with open("/root/.jupyter/jupyter_server_config.json", "w") as f:
    json.dump(cfg, f, indent=2)
PY

# หมายเหตุ: คำสั่งที่ bash script รันแบบ background (&) จะถูกตั้ง SIGINT/SIGQUIT = ignore
# และสืบทอดไปยัง terminal ใน JupyterLab ทำให้ Ctrl+C หยุดโปรเซสไม่ได้
# จึง reset signal กลับเป็น default ก่อน exec jupyter
cd /workspace
python3 -c '
import os, signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGQUIT, signal.SIG_DFL)
os.execvp("jupyter", ["jupyter", "lab"])
' > /var/log/jupyter.log 2>&1 &

echo "[start.sh] sshd :22 | dockerd | jupyter lab :8888 (password: ${JUPYTER_PASSWORD:-<none>}) | NodePort :30080-30082 (kind auto-create: $KIND_AUTO_CREATE) — logs: /var/log/jupyter.log /var/log/dockerd.log /var/log/k8s-up.log"

if [ -t 0 ]; then
    exec bash
else
    exec tail -F /var/log/jupyter.log
fi
