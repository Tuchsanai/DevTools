-- sprint_time_machine.sql — "เครื่องย้อนเวลา" ของ LAB 4
-- Plane วาด burndown จากคอลัมน์ issues.completed_at เท่านั้น: งานที่ Done วันนี้ทั้ง 3 ใบทำให้กราฟตกแค่จุดเดียว
-- สคริปต์นี้กระจาย completed_at ของ PBI ที่ Done (external_source='lab' — ใบจาก seed_backlog.py เท่านั้น
-- ไม่แตะใบจาก LAB 1-3) ให้เป็น "3 วันก่อน / 2 วันก่อน / เมื่อวาน" (เรียงตามเลขใบ)
-- เพื่อให้เห็นเส้น actual ไต่ลงหลายวันเทียบกับเส้น ideal · ทำใน transaction และสำรองค่าเดิมไว้ที่ตาราง lab4_completed_backup
-- ใช้:  pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -f - < sprint_time_machine.sql
-- ย้อนกลับ:  pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -f - < restore_done.sql
BEGIN;

CREATE TABLE IF NOT EXISTS lab4_completed_backup AS
SELECT i.id, i.completed_at
FROM issues i
JOIN projects p ON p.id = i.project_id
JOIN states s ON s.id = i.state_id
WHERE p.identifier = 'PLAB' AND i.external_source = 'lab' AND s."group" = 'completed' AND i.deleted_at IS NULL;

\echo '--- BEFORE'
SELECT i.external_id AS pbi, 'PLAB-' || i.sequence_id AS item, s.name AS state, i.completed_at
FROM issues i
JOIN projects p ON p.id = i.project_id
JOIN states s ON s.id = i.state_id
WHERE p.identifier = 'PLAB' AND i.external_source = 'lab' AND s."group" = 'completed' AND i.deleted_at IS NULL
ORDER BY i.sequence_id;

WITH done AS (
  SELECT i.id, ROW_NUMBER() OVER (ORDER BY i.sequence_id) AS rn
  FROM issues i
  JOIN projects p ON p.id = i.project_id
  JOIN states s ON s.id = i.state_id
  WHERE p.identifier = 'PLAB' AND i.external_source = 'lab' AND s."group" = 'completed' AND i.deleted_at IS NULL
)
UPDATE issues i
SET completed_at = now() - make_interval(days => GREATEST(1, 4 - done.rn::int))
FROM done
WHERE i.id = done.id;

\echo '--- AFTER'
SELECT i.external_id AS pbi, 'PLAB-' || i.sequence_id AS item, s.name AS state, i.completed_at,
       (current_date - i.completed_at::date) AS days_ago
FROM issues i
JOIN projects p ON p.id = i.project_id
JOIN states s ON s.id = i.state_id
WHERE p.identifier = 'PLAB' AND i.external_source = 'lab' AND s."group" = 'completed' AND i.deleted_at IS NULL
ORDER BY i.sequence_id;

COMMIT;
