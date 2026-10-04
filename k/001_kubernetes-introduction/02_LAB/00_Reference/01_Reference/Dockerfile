FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Bangkok \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        gnupg \
        lsb-release \
        software-properties-common \
        sudo \
        vim \
        nano \
        less \
        net-tools \
        iputils-ping \
        dnsutils \
        git \
        openssh-server \
        tzdata \
        python3 \
        python3-pip \
        python3-venv \
        python-is-python3 \
 && ln -fs "/usr/share/zoneinfo/${TZ}" /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

# Git ล่าสุดจาก git-core PPA (git worktree ต้องใช้ git >= 2.5; Ubuntu 24.04 มี 2.43 อยู่แล้ว
# แต่ติดตั้งเวอร์ชันล่าสุดไว้เพื่อให้ได้ฟีเจอร์ worktree ครบทุกคำสั่ง เช่น repair/move)
RUN add-apt-repository -y ppa:git-core/ppa \
 && apt-get update && apt-get install -y --no-install-recommends git \
 && git --version \
 && git init -q /tmp/worktree-check \
 && git -C /tmp/worktree-check worktree list >/dev/null \
 && rm -rf /tmp/worktree-check /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME}") stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update && apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

# Node.js (LTS 22.x) สำหรับ run Next.js / React / Vite
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g npm@latest \
 && rm -rf /var/lib/apt/lists/*

RUN install -d /workspace

# ------------------------------------------------------------------
# JupyterLab + extensions (ติดตั้งลง system python เพื่อให้ kernel เห็น
# package เดียวกับที่ใช้ใน terminal / SSH)
#   - jupytext                : เปิด .py / .md เป็น notebook ได้ (pair notebook <-> script)
#   - jupyterlab-git          : Git UI ใน sidebar
#   - jupyterlab-lsp          : autocomplete / hover / diagnostics (python-lsp-server)
#   - jupyterlab-code-formatter + black + isort : จัดรูปแบบโค้ด
#   - jupyterlab-execute-time : แสดงเวลารันของแต่ละ cell
#   - jupyter-resource-usage  : แสดง CPU / RAM ใน status bar
#   - ipywidgets              : interactive widgets
#   - bash_kernel             : เขียน notebook ด้วย Bash kernel (เหมาะกับ DevTools lab)
# ------------------------------------------------------------------
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN pip install \
        "jupyterlab>=4.3,<5" \
        notebook \
        ipywidgets \
        jupytext \
        jupyterlab-git \
        jupyterlab-lsp \
        "python-lsp-server[all]" \
        jupyterlab-code-formatter \
        black \
        isort \
        jupyterlab-execute-time \
        jupyter-resource-usage \
        bash_kernel \
 && python -m bash_kernel.install --sys-prefix \
 && jupyter lab --version \
 && jupyter labextension list 2>&1 | grep -E 'enabled|OK' | head -20

# Jupyter Server config (system-wide)
RUN mkdir -p /etc/jupyter \
 && cat > /etc/jupyter/jupyter_server_config.py <<'EOF'
c = get_config()  # noqa

c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.root_dir = "/"          # เห็นทั้ง filesystem (โฟลเดอร์งานอยู่ที่ /workspace)
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.allow_remote_access = True

# แสดง hidden file / folder (ชื่อขึ้นต้นด้วย ".") ใน file browser เช่น .env .git .gitignore
# (ฝั่ง UI ตั้ง showHiddenFiles ไว้ใน overrides.json; ต้องเปิดทั้งสองฝั่งจึงจะเห็น)
c.ContentsManager.allow_hidden = True

# terminal ใน JupyterLab ใช้ bash login shell (อ่าน /etc/profile, ~/.bashrc)
c.ServerApp.terminals_enabled = True
c.ServerApp.terminado_settings = {"shell_command": ["/bin/bash", "-l"]}

# ไม่ใช้ token; รหัสผ่าน (ถ้ามี) ถูกตั้งจาก start.sh ผ่าน $JUPYTER_PASSWORD (default: ไม่มีรหัสผ่าน)
c.IdentityProvider.token = ""
c.PasswordIdentityProvider.allow_password_change = False
EOF

# JupyterLab UI defaults — file browser แสดง hidden file/folder และ terminal ให้ copy/paste ได้สะดวก:
#   * Ctrl+V           = paste (pasteWithCtrlV)
#   * Ctrl+Shift+C / V = copy / paste
#   * Ctrl+Insert / Shift+Insert = copy / paste
#   * คลิกขวาที่ terminal จะมีเมนู Copy / Paste
COPY jupyter_overrides.json /usr/local/share/jupyter/lab/settings/overrides.json

# ตั้งรหัสผ่าน root = passwd และเปิดให้ login ผ่าน SSH ได้ทั้ง password และ key
#   - password : ssh root@localhost -p 2223            (password: passwd)
#   - key      : ssh -i ssh/devtoolSSH root@localhost -p 2223
#     start.sh จะนำ public key จาก /etc/devtools/ssh/devtoolSSH.pub (mount มาจาก ./ssh บน host)
#     ไปใส่ใน /root/.ssh/authorized_keys ทุกครั้งที่ container start
RUN echo 'root:passwd' | chpasswd \
 && mkdir -p /etc/ssh/sshd_config.d /etc/devtools/ssh \
 && install -d -m 700 /root/.ssh \
 && printf 'PermitRootLogin yes\nPasswordAuthentication yes\nPubkeyAuthentication yes\n' \
      > /etc/ssh/sshd_config.d/10-root-login.conf

# ------------------------------------------------------------------
# Kubernetes tools สำหรับ lab: kind (Kubernetes IN Docker), kubectl, helm, k9s
#   - pin เวอร์ชันด้วย ARG (เปลี่ยนตอน build ได้: --build-arg KUBECTL_VERSION=v1.xx.x)
#   - รองรับ amd64 / arm64 (เลือกไฟล์ตาม dpkg --print-architecture)
#   - ดาวน์โหลดจาก official release และตรวจ sha256 ทุกตัว
#   - kind ใช้ dockerd ภายใน container (Docker-in-Docker) สร้าง node เป็น container
# ------------------------------------------------------------------
ARG KIND_VERSION=v0.33.0
ARG KUBECTL_VERSION=v1.37.1
ARG HELM_VERSION=v4.3.0
ARG K9S_VERSION=v0.51.0

# bash-completion: ให้กด Tab เติมคำสั่ง kubectl / kind / helm ได้
RUN apt-get update && apt-get install -y --no-install-recommends bash-completion \
 && rm -rf /var/lib/apt/lists/*

# kubectl — ไฟล์ binary + .sha256 จาก dl.k8s.io
RUN set -eux; ARCH="$(dpkg --print-architecture)"; cd /tmp \
 && curl -fsSLo kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl" \
 && curl -fsSLo kubectl.sha256 "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl.sha256" \
 && echo "$(cat kubectl.sha256)  kubectl" | sha256sum -c - \
 && install -m 0755 kubectl /usr/local/bin/kubectl \
 && rm -f kubectl kubectl.sha256 \
 && kubectl version --client

# kind — binary + .sha256sum จาก GitHub release ของ kubernetes-sigs/kind
RUN set -eux; ARCH="$(dpkg --print-architecture)"; cd /tmp \
 && curl -fsSLo "kind-linux-${ARCH}" "https://github.com/kubernetes-sigs/kind/releases/download/${KIND_VERSION}/kind-linux-${ARCH}" \
 && curl -fsSLo kind.sha256sum "https://github.com/kubernetes-sigs/kind/releases/download/${KIND_VERSION}/kind-linux-${ARCH}.sha256sum" \
 && sha256sum -c kind.sha256sum \
 && install -m 0755 "kind-linux-${ARCH}" /usr/local/bin/kind \
 && rm -f "kind-linux-${ARCH}" kind.sha256sum \
 && kind --version

# helm — tarball + .sha256sum จาก get.helm.sh
RUN set -eux; ARCH="$(dpkg --print-architecture)"; cd /tmp \
 && TGZ="helm-${HELM_VERSION}-linux-${ARCH}.tar.gz" \
 && curl -fsSLo "$TGZ" "https://get.helm.sh/${TGZ}" \
 && curl -fsSLo helm.sha256sum "https://get.helm.sh/${TGZ}.sha256sum" \
 && sha256sum -c helm.sha256sum \
 && tar -xzf "$TGZ" "linux-${ARCH}/helm" \
 && install -m 0755 "linux-${ARCH}/helm" /usr/local/bin/helm \
 && rm -rf "$TGZ" helm.sha256sum "linux-${ARCH}" \
 && helm version

# k9s — terminal UI สำหรับดู cluster (tarball + checksums.sha256 จาก GitHub release)
RUN set -eux; ARCH="$(dpkg --print-architecture)"; cd /tmp \
 && TGZ="k9s_Linux_${ARCH}.tar.gz" \
 && curl -fsSLo "$TGZ" "https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/${TGZ}" \
 && curl -fsSLo k9s.sha256 "https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/checksums.sha256" \
 && grep " ${TGZ}\$" k9s.sha256 | sha256sum -c - \
 && tar -xzf "$TGZ" k9s \
 && install -m 0755 k9s /usr/local/bin/k9s \
 && rm -f "$TGZ" k9s.sha256 k9s \
 && k9s version --short

# shell completion + alias k=kubectl
#   - completion script ใน /etc/bash_completion.d/ ถูกโหลดโดย bash-completion
#   - เขียนไว้ใน /etc/bash.bashrc → ใช้ได้ทั้ง SSH และ terminal ของ JupyterLab (bash -l อ่าน /etc/profile → bash.bashrc)
RUN kubectl completion bash > /etc/bash_completion.d/kubectl \
 && kind completion bash    > /etc/bash_completion.d/kind \
 && helm completion bash    > /etc/bash_completion.d/helm \
 && cat >> /etc/bash.bashrc <<'EOF2'

# --- Kubernetes lab: bash-completion + alias k=kubectl ---
if ! shopt -oq posix && [ -z "${BASH_COMPLETION_VERSINFO:-}" ] && [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
fi
alias k=kubectl
complete -o default -F __start_kubectl k 2>/dev/null || true
EOF2

# kind cluster config + script สร้าง/ลบคลัสเตอร์ (k8s-up / k8s-down)
COPY kind-lab.yaml /etc/devtools/kind/kind-lab.yaml
# ไฟล์ตัวอย่าง (manifest + myapp) — start.sh จะ copy ไป /workspace/examples ตอน container start
COPY examples /opt/k8s-lab/examples
COPY k8s-up k8s-down /usr/local/bin/
RUN chmod +x /usr/local/bin/k8s-up /usr/local/bin/k8s-down

# start script: sshd + dockerd + jupyter lab (+ k8s-up ถ้า KIND_AUTO_CREATE=1)
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

VOLUME /var/lib/docker

# 22=ssh, 8888=jupyterlab, 30080-30082=NodePort ของ kind cluster (map ผ่าน extraPortMappings)
EXPOSE 22 8888 30080 30081 30082

WORKDIR /workspace

CMD ["/usr/local/bin/start.sh"]
