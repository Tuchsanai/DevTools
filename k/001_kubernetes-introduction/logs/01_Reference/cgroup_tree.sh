#!/bin/bash
# แสดง cgroup tree + type + controllers ของ container ทดลอง
cd /sys/fs/cgroup
echo "root type: $(cat cgroup.type 2>&1)"
find . -maxdepth 3 -name cgroup.type | while read -r f; do
    d=$(dirname "$f")
    printf '%-60s type=%-16s procs=%-3s subtree=[%s]\n' "$d" "$(cat "$f" 2>&1)" "$(wc -l < "$d/cgroup.procs" 2>/dev/null)" "$(cat "$d/cgroup.subtree_control" 2>/dev/null)"
done
echo "max.depth=$(cat cgroup.max.depth) max.descendants=$(cat cgroup.max.descendants)"
cat /proc/1/cgroup
uname -r
