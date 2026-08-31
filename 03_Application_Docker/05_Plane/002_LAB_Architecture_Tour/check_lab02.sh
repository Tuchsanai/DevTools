#!/bin/bash
# LAB 2 evidence gate — prints exactly one PASS: line when every proof of this lab is present.
fail() { echo "FAIL: $*"; exit 1; }
SQL() { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -Atc "$1" 2>/dev/null | tr -d '\r'; }
# 1) 12 services Up, migrator exited 0
up=$(pc ps --format '{{.Service}} {{.Status}}' 2>/dev/null | grep -c ' Up')
[ "$up" -ge 12 ] || fail "only $up services Up (need 12)"
pc ps -a --format '{{.Service}} {{.Status}}' | grep -q '^migrator Exited (0)' || fail "migrator did not exit 0"
# 2) proxy routes (signatures)
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:8080/api/instances/)" = 200 ] || fail "/api/instances/ not 200"
curl -s localhost:8080/live/health | grep -q '"status":"OK"' || fail "/live/health not OK"
curl -s localhost:8080/uploads/does-not-exist | grep -q "<Error><Code>" || fail "/uploads/ not routed to MinIO (no S3 XML error)"
# 3) worker consuming the celery queue
pc exec -T plane-mq rabbitmqctl list_queues -p plane name consumers 2>/dev/null | grep -qE '^celery\s+[1-9]' || fail "no consumer on queue celery (is worker started?)"
# 4) SQL proofs: 6 states incl. Triage, ≥4 sequences with a deleted one, an attachment row
st=$(SQL "select count(*) from states s join projects p on p.id=s.project_id where p.identifier='PLAB' and s.deleted_at is null")
[ "$st" = 6 ] || fail "PLAB has $st states (need 6)"
seqs=$(SQL "select count(*) from issue_sequences q join projects p on p.id=q.project_id where p.identifier='PLAB'")
del=$(SQL "select count(*) from issue_sequences q join projects p on p.id=q.project_id where p.identifier='PLAB' and (q.deleted or q.issue_id is null)")
[ "$seqs" -ge 4 ] && [ "$del" -ge 1 ] || fail "issue_sequences: $seqs rows / $del deleted (need >=4 / >=1)"
att=$(SQL "select count(*) from file_assets where entity_type='ISSUE_ATTACHMENT' and is_uploaded")
[ "$att" -ge 1 ] || fail "no uploaded ISSUE_ATTACHMENT in file_assets"
pages=$(SQL "select count(*) from pages where name='Live test' and deleted_at is null")
[ "$pages" -ge 1 ] || fail "page 'Live test' not found"
echo "PASS: lab02 — $up services Up, migrator Exited (0), proxy routes OK, worker consuming 'celery', PLAB states=$st, sequences=$seqs (deleted=$del), attachments=$att, live page OK"
