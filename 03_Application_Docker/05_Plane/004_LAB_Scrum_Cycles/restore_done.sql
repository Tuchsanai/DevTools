-- restore_done.sql — คืนค่า completed_at เดิมจาก lab4_completed_backup (คู่ของ sprint_time_machine.sql)
-- ใช้:  pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -f - < restore_done.sql
BEGIN;
\echo '--- restoring from lab4_completed_backup'
UPDATE issues i
SET completed_at = b.completed_at
FROM lab4_completed_backup b
WHERE i.id = b.id;
SELECT i.external_id AS pbi, 'PLAB-' || i.sequence_id AS item, i.completed_at
FROM issues i JOIN lab4_completed_backup b ON b.id = i.id
ORDER BY i.sequence_id;
DROP TABLE lab4_completed_backup;
COMMIT;
