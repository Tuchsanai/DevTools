#!/bin/bash
# ตรวจว่า controller ไหนเปิดใน subtree_control ได้บ้าง
echo "procs left in root: $(wc -l < /sys/fs/cgroup/cgroup.procs)"
echo "procs in init: $(wc -l < /sys/fs/cgroup/init/cgroup.procs)"
for c in $(cat /sys/fs/cgroup/cgroup.controllers); do
    if echo "+$c" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null; then echo "$c: ok"; else echo "$c: FAIL"; fi
done
echo "subtree now: $(cat /sys/fs/cgroup/cgroup.subtree_control)"
cat /proc/self/mountinfo | grep cgroup
