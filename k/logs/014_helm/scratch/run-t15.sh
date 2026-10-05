mkdir -p /workspace/pc/first && cd /workspace/pc/first
helm create mychart
find mychart -type f | sort
cat mychart/Chart.yaml | grep -v "^#" | grep -v "^$"
grep -v "^\s*#" mychart/values.yaml | grep -v "^$" | head -60
