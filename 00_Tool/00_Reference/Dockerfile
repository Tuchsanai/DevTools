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

# ตั้งรหัสผ่าน root = passwd และเปิดให้ login ผ่าน SSH ด้วย password ได้
RUN echo 'root:passwd' | chpasswd \
 && mkdir -p /etc/ssh/sshd_config.d \
 && printf 'PermitRootLogin yes\nPasswordAuthentication yes\n' \
      > /etc/ssh/sshd_config.d/10-root-login.conf

VOLUME /var/lib/docker

# 22=ssh
EXPOSE 22

WORKDIR /workspace

CMD ["sh", "-c", "mkdir -p /run/sshd && ssh-keygen -A >/dev/null 2>&1; /usr/sbin/sshd; dockerd > /var/log/dockerd.log 2>&1 & exec bash"]
