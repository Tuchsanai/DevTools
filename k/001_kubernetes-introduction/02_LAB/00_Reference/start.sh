#!/bin/bash
# start.sh — entrypoint ของ devtools container
#   1) sshd        (port 22)   : root / passwd หรือ key devtoolSSH (map ./Devtool_SSH มา)
#   2) dockerd     (Docker-in-Docker, ต้อง --privileged)
#   3) jupyter lab (port 8888) : ไม่มีรหัสผ่าน (ตั้งได้ด้วย $JUPYTER_PASSWORD)
# ถ้ารันแบบมี tty (-it) จะเปิด bash ให้; ถ้ารันแบบ -d จะ tail log แทนเพื่อให้ container ไม่ดับ

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

dockerd > /var/log/dockerd.log 2>&1 &

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

echo "[start.sh] sshd :22 | dockerd | jupyter lab :8888 (password: ${JUPYTER_PASSWORD:-<none>}) — logs: /var/log/jupyter.log /var/log/dockerd.log"

if [ -t 0 ]; then
    exec bash
else
    exec tail -F /var/log/jupyter.log
fi
