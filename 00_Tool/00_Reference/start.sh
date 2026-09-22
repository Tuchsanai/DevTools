#!/bin/bash
# start.sh — entrypoint ของ devtools container
#   1) sshd        (port 22)   : root / passwd
#   2) dockerd     (Docker-in-Docker, ต้อง --privileged)
#   3) jupyter lab (port 8888) : ไม่มีรหัสผ่าน (ตั้งได้ด้วย $JUPYTER_PASSWORD)
# ถ้ารันแบบมี tty (-it) จะเปิด bash ให้; ถ้ารันแบบ -d จะ tail log แทนเพื่อให้ container ไม่ดับ

mkdir -p /run/sshd
ssh-keygen -A >/dev/null 2>&1
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
