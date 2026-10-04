#!/bin/bash
# ย้ายทุก process จาก root cgroup เข้า /init ทีละตัว พร้อมแสดง error
for p in $(cat /sys/fs/cgroup/cgroup.procs); do
    printf '%s (%s): ' "$p" "$(cat /proc/$p/comm 2>/dev/null)"
    if echo "$p" > /sys/fs/cgroup/init/cgroup.procs; then echo moved; fi
done
echo "left in root: $(cat /sys/fs/cgroup/cgroup.procs | tr '\n' ' ')"
for c in $(cat /sys/fs/cgroup/cgroup.controllers); do
    echo "+$c" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null && echo "$c ok" || echo "$c FAIL"
done
echo "subtree now: $(cat /sys/fs/cgroup/cgroup.subtree_control)"
