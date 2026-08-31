#!/bin/bash
# check_lab01.sh — LAB 1 evidence gate. Prints exactly one PASS line when every proof from the lab is present.
URL=${PLANE_URL:-http://localhost:8080}
sql() { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tAc "$1" 2>/dev/null | tr -d '[:space:]'; }
fail=0
ok()  { echo "  ok   $1"; }
bad() { echo "  FAIL $1"; fail=1; }

n_services=$(pc config --services 2>/dev/null | wc -l)
[ "$n_services" -eq 13 ] && ok "compose declares 13 services" || bad "compose services = $n_services (expected 13)"

n_up=$(pc ps --format '{{.State}}' 2>/dev/null | grep -c '^running$')
[ "$n_up" -eq 12 ] && ok "12 containers running" || bad "running containers = $n_up (expected 12)"

mig=$(pc ps -a --format '{{.Service}} {{.State}} {{.ExitCode}}' 2>/dev/null | awk '$1=="migrator"{print $2"/"$3}')
[ "$mig" = "exited/0" ] && ok "migrator Exited (0)" || bad "migrator state = ${mig:-missing} (expected exited/0)"

setup=$(curl -s --max-time 5 "$URL/api/instances/" | python3 -c 'import sys,json; print(json.load(sys.stdin)["instance"]["is_setup_done"])' 2>/dev/null)
[ "$setup" = "True" ] && ok "instance is_setup_done = True" || bad "is_setup_done = ${setup:-no answer} (expected True)"

ws=$(sql "select count(*) from workspaces where slug='devtools-lab' and deleted_at is null")
[ "$ws" = "1" ] && ok "workspace slug devtools-lab" || bad "workspace devtools-lab rows = ${ws:-?}"

proj=$(sql "select cycle_view::int||'/'||module_view::int||'/'||issue_views_view::int from projects where identifier='PLAB' and deleted_at is null")
[ "$proj" = "1/1/1" ] && ok "project PLAB with Cycles/Modules/Views ON" || bad "project PLAB cycle_view/module_view/issue_views_view = ${proj:-missing} (expected 1/1/1)"

issues=$(sql "select count(*) from issues i join projects p on p.id=i.project_id where p.identifier='PLAB' and i.deleted_at is null")
[ "${issues:-0}" -ge 3 ] && ok "$issues work items in PLAB" || bad "PLAB work items = ${issues:-0} (expected >= 3)"

if [ "$fail" = 0 ]; then
  echo "PASS: LAB 1 — 13 services · 12 Up · migrator Exited (0) · setup done · workspace devtools-lab · project PLAB (cycles/modules/views on) · $issues work items"
else
  echo "FAIL: fix the lines above, then run: bash check_lab01.sh"; exit 1
fi
