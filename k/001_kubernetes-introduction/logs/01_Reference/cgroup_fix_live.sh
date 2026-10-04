#!/bin/bash
# ทดลอง cgroup v2 nesting fix แบบ live ใน container ทดลอง (เหมือน dind entrypoint ของ docker:dind)
kind delete cluster --name dbg >/dev/null 2>&1
if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
    mkdir -p /sys/fs/cgroup/init
    xargs -rn1 < /sys/fs/cgroup/cgroup.procs > /sys/fs/cgroup/init/cgroup.procs 2>/dev/null || :
    sed -e 's/ / +/g' -e 's/^/+/' < /sys/fs/cgroup/cgroup.controllers > /sys/fs/cgroup/cgroup.subtree_control
fi
echo "subtree after fix: $(cat /sys/fs/cgroup/cgroup.subtree_control)"
k8s-up
