-- LAB 2 — PostgreSQL tour of Plane
-- run: pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -f - < sql_tour.sql
-- (PGHOST=plane-db is set inside the container, so psql goes over TCP and needs the password)
\echo '== 1) how many tables did the migrator create?'
SELECT count(*) AS tables FROM information_schema.tables WHERE table_schema = 'public';

\echo '== 2) the 6 states of project PLAB (Triage is hidden from the UI)'
SELECT s.name, s."group", s.sequence, s."default", s.is_triage
FROM states s JOIN projects p ON p.id = s.project_id
WHERE p.identifier = 'PLAB' AND s.deleted_at IS NULL ORDER BY s.sequence;

\echo '== 3) work items of PLAB + their sequence ledger (numbers are never reused)'
SELECT i.sequence_id AS "PLAB-N", left(i.name, 40) AS name, st.name AS state, i.completed_at, i.deleted_at
FROM issues i JOIN projects p ON p.id = i.project_id JOIN states st ON st.id = i.state_id
WHERE p.identifier = 'PLAB' ORDER BY i.sequence_id;
SELECT q.sequence, q.deleted, (q.issue_id IS NOT NULL) AS issue_still_linked
FROM issue_sequences q JOIN projects p ON p.id = q.project_id
WHERE p.identifier = 'PLAB' ORDER BY q.sequence;

\echo '== 4) instance configuration lives in the DB, not in plane.env (SKIP_ENV_VAR=1)'
SELECT key, value FROM instance_configurations
WHERE key IN ('ENABLE_SIGNUP','ENABLE_EMAIL_PASSWORD','ENABLE_MAGIC_LINK_LOGIN','ENABLE_SMTP','EMAIL_HOST') ORDER BY key;

\echo '== 5) the beat schedule (celery.py) is copied into django_celery_beat_periodictask'
SELECT name, last_run_at, total_run_count FROM django_celery_beat_periodictask ORDER BY name;
