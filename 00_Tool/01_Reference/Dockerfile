# ---------------------------------------------------------------------------
# DevTools Base Learning Container
#   Ubuntu 26.04 LTS + Docker-in-Docker + Python + Node.js LTS + SSH
# ---------------------------------------------------------------------------

ARG UBUNTU_VERSION=26.04
FROM ubuntu:${UBUNTU_VERSION}

# ---- ปรับเวอร์ชัน/ค่าต่าง ๆ ได้ตอน build ด้วย --build-arg ------------------
ARG NODE_MAJOR=24
ARG TZ=Asia/Bangkok
ARG ROOT_PASSWORD=passwd
ARG BUILD_DATE=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="DevTools Base Learning Container" \
      org.opencontainers.image.description="Ubuntu LTS + Docker-in-Docker + Python + Node.js LTS + SSH สำหรับ DevTools labs" \
      org.opencontainers.image.source="https://github.com/tuchsanai/DevTools" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=${TZ} \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    # /opt/venv มาก่อน system python เพื่อเลี่ยง PEP 668 (externally-managed-environment)
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/usr/local/bin:$PATH \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    UV_LINK_MODE=copy

# bash + -euo pipefail: ทำให้ `curl ... | bash` ที่พังกลางทาง ทำให้ build ล้มจริง
# (ด้วย /bin/sh ปกติ exit code ของ pipe จะถูกกลืน = build ผ่านทั้งที่ของไม่ครบ)
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# ---------------------------------------------------------------------------
# 0) เปิด apt cache ให้ BuildKit เก็บ .deb ไว้ข้าม build ได้ (rebuild เร็วขึ้นมาก)
#    ไฟล์ที่ cache อยู่ใน cache mount ไม่ถูกนับเข้า image layer -> image ไม่บวม
# ---------------------------------------------------------------------------
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
 && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# ---------------------------------------------------------------------------
# 1) เครื่องมือพื้นฐาน + Python + timezone
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget gnupg lsb-release software-properties-common \
        sudo tini tzdata procps psmisc iproute2 \
        vim nano less tree htop tmux bash-completion \
        net-tools iputils-ping dnsutils rsync unzip zip jq ripgrep \
        build-essential make pkg-config \
        openssh-server openssh-client \
        python3 python3-pip python3-venv python-is-python3 \
 && ln -fs "/usr/share/zoneinfo/${TZ}" /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

# ---------------------------------------------------------------------------
# 2) Git เวอร์ชันล่าสุดจาก git-core PPA
#    (distro git ก็พอสำหรับ worktree แล้ว แต่ PPA ให้ subcommand ครบ เช่น repair/move)
#    ปิดท้ายด้วย self-test: ถ้า worktree ใช้ไม่ได้ ให้ build ล้มตั้งแต่ตอนนี้
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    add-apt-repository -y ppa:git-core/ppa \
 && apt-get update && apt-get install -y --no-install-recommends git git-lfs \
 && git --version \
 && git init -q /tmp/worktree-check \
 && git -C /tmp/worktree-check worktree list >/dev/null \
 && rm -rf /tmp/worktree-check

# ---------------------------------------------------------------------------
# 3) Docker Engine (Docker-in-Docker) จาก repo ทางการ
#    ใช้ keyring แยกไฟล์ + signed-by (วิธีปัจจุบัน) ไม่ใช่ apt-key ที่ deprecated แล้ว
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' \
      "$(dpkg --print-architecture)" \
      "$(. /etc/os-release && echo "${VERSION_CODENAME}")" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update && apt-get install -y --no-install-recommends \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin \
 && dockerd --version && docker buildx version && docker compose version

# ค่า default ของ dockerd ข้างใน: บังคับ overlay2 (กัน fallback ไป vfs ที่ช้ามาก)
# และหมุน log ไม่ให้ disk เต็มระหว่างเรียน
COPY <<'EOF' /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
EOF

# ---------------------------------------------------------------------------
# 4) Node.js LTS + corepack (เปิดใช้ pnpm / yarn ได้ทันที)
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g npm@latest \
 && corepack enable \
 && node --version && npm --version

# ---------------------------------------------------------------------------
# 5) Python: venv กลางที่ /opt/venv + uv (package manager รุ่นใหม่ เร็วกว่า pip มาก)
#    ทำแบบนี้เพื่อให้ `pip install` ใช้ได้เลย ไม่ชน PEP 668
# ---------------------------------------------------------------------------
RUN python3 -m venv "${VIRTUAL_ENV}" \
 && "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir --upgrade pip setuptools wheel \
 && curl -fsSL https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
 && uv --version && python --version && pip --version

# ---------------------------------------------------------------------------
# 6) GitHub CLI (gh) — ใช้ใน lab เรื่อง PR / issue / workflow
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /etc/apt/keyrings/githubcli.gpg \
 && chmod a+r /etc/apt/keyrings/githubcli.gpg \
 && printf 'deb [arch=%s signed-by=/etc/apt/keyrings/githubcli.gpg] https://cli.github.com/packages stable main\n' \
      "$(dpkg --print-architecture)" > /etc/apt/sources.list.d/github-cli.list \
 && apt-get update && apt-get install -y --no-install-recommends gh \
 && gh --version

# ---------------------------------------------------------------------------
# 7) SSH: root login ด้วย password (สำหรับห้องเรียนเท่านั้น)
#    เขียนเป็น drop-in ใน sshd_config.d/ แทนการ sed แก้ไฟล์หลัก
# ---------------------------------------------------------------------------
RUN echo "root:${ROOT_PASSWORD}" | chpasswd \
 && mkdir -p /etc/ssh/sshd_config.d \
 && printf 'PermitRootLogin yes\nPasswordAuthentication yes\nUseDNS no\nClientAliveInterval 60\nAcceptEnv LANG LC_*\n' \
      > /etc/ssh/sshd_config.d/10-devtools.conf \
 && sshd -t -f /etc/ssh/sshd_config \
 && printf '\n[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion\nsource /opt/venv/bin/activate 2>/dev/null || true\n' \
      >> /root/.bashrc

RUN install -d /workspace

# ---------------------------------------------------------------------------
# 8) Entrypoint — เขียนแบบ heredoc ให้ Dockerfile ยังเป็น "ไฟล์เดียวจบ"
#    ต่างจากเดิมตรงที่ "รอ dockerd พร้อมจริง" และ "ตายไวถ้าลืม --privileged"
# ---------------------------------------------------------------------------
COPY --chmod=0755 <<'EOF' /usr/local/bin/docker-entrypoint.sh
#!/usr/bin/env bash
set -euo pipefail

log() { printf '[entrypoint] %s\n' "$*" >&2; }

# ---- SSH ---------------------------------------------------------------
mkdir -p /run/sshd
ssh-keygen -A >/dev/null 2>&1 || true   # สร้าง host key ตอน run ครั้งแรก
/usr/sbin/sshd
log "sshd listening on :22"

# ---- Docker daemon (DinD) ---------------------------------------------
if [[ "${START_DOCKERD:-1}" == "1" ]]; then
  dockerd >/var/log/dockerd.log 2>&1 &
  dockerd_pid=$!

  timeout="${DOCKERD_TIMEOUT:-45}"
  log "waiting for dockerd (timeout ${timeout}s)..."
  for _ in $(seq 1 "$timeout"); do
    if docker info >/dev/null 2>&1; then
      log "dockerd ready: $(docker version --format '{{.Server.Version}}')"
      break
    fi
    if ! kill -0 "$dockerd_pid" 2>/dev/null; then
      log "ERROR: dockerd exited. tail of /var/log/dockerd.log:"
      tail -n 30 /var/log/dockerd.log >&2 || true
      log "HINT: ต้องรัน container ด้วย --privileged"
      exit 1
    fi
    sleep 1
  done

  docker info >/dev/null 2>&1 \
    || log "WARN: dockerd ยังไม่พร้อมหลัง ${timeout}s — ดู /var/log/dockerd.log"
fi

# `docker run -d` (ไม่มี TTY) + CMD bash => bash เจอ EOF แล้ว exit ทันที container ตาย
# กรณีนี้ให้ค้างไว้แทน แล้วผู้ใช้เข้าทาง `docker exec -it <name> bash`
# (`docker run -it` ยังได้ shell ปกติ, `docker run <img> node -v` ยังรันคำสั่งปกติ)
if [[ $# -eq 1 && "$1" == "bash" && ! -t 0 ]]; then
  log "no TTY attached — container จะค้างไว้ ใช้: docker exec -it <name> bash"
  exec sleep infinity
fi

exec "$@"
EOF

# storage ของ inner docker ต้องอยู่บน volume ไม่ใช่ overlay layer ของ container
VOLUME /var/lib/docker

EXPOSE 22

WORKDIR /workspace

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD pgrep -x sshd >/dev/null && { [ "${START_DOCKERD:-1}" != "1" ] || docker info >/dev/null 2>&1; }

# tini เป็น PID 1: reap zombie process ที่ dockerd/containerd ทิ้งไว้ + ส่งต่อ signal
# ให้ `docker stop` ปิดได้สะอาด (เดิมใช้ `sh -c ... & exec bash` ไม่มีตัวจัดการตรงนี้)
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["bash"]
