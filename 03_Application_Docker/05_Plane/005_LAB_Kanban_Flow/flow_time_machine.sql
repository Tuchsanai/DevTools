-- flow_time_machine.sql — "ย้อนเวลา" ให้ PBI ของ CampusEats มีประวัติ flow จริงจังใน 7 วันที่ผ่านมา
-- เพื่อให้ flow_metrics.py มี lead time / cycle time / throughput ที่ไม่ใช่ศูนย์ (แล็บทำใน 1 ชั่วโมง ไม่ใช่ 1 สัปดาห์)
--
-- ใช้:  pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -f - < flow_time_machine.sql
-- เลือกใบงานด้วย external_id ที่ seed_backlog.py (LAB 4) ใส่ไว้ — ไม่ใช่เลข PLAB-N ซึ่งต่างกันในแต่ละเครื่อง
-- ทำอะไร: (1) สำรองแถวเดิม (created_at / completed_at / state_id และ activity field='state') ไว้ในตาราง lab5_backup_*
--         (2) 6 ใบที่ "เสร็จ": PBI-01 PBI-02 PBI-10 (Done ตั้งแต่ Sprint 1) + PBI-03 PBI-05 PBI-09 (Sprint 2)
--             → ตั้ง state = Done, created_at / completed_at กระจายใน 7 วัน และ activity Backlog → Todo → In Progress → Done
--         (3) ใบที่ "กำลังทำ" (อยู่ในกลุ่ม started ตอนนี้ สูงสุด 3 ใบ) → คง state เดิม แต่ให้ activity เข้า state นั้นย้อนหลัง 5 / 3 / 1 วัน เพื่อให้ WIP มีอายุ
--         state ในบอร์ด, completed_at และ activity จึงเล่าเรื่องเดียวกัน (flow_metrics.py / check_lab05.sh อ่านทั้งสามอย่าง)
-- ย้อนกลับ: ดูบล็อก RESTORE ท้ายไฟล์
BEGIN;

-- (0) ใบงานเป้าหมาย: ชั่วโมงย้อนหลังของ created / started / done
CREATE TEMP TABLE tm AS
SELECT i.id, i.sequence_id AS seq, i.external_id AS ext, x.created_h, x.started_h, x.done_h
FROM (VALUES
  ('PBI-01', 168, 156, 120),   -- สร้าง 7 วันก่อน · เริ่ม 6.5 วันก่อน · เสร็จ 5 วันก่อน → lead 48 h, cycle 36 h
  ('PBI-02', 144, 120, 108),   --                                                → lead 36 h, cycle 12 h
  ('PBI-10', 120,  96,  48),   --                                                → lead 72 h, cycle 48 h
  ('PBI-03', 156,  96,  36),   --                                                → lead 120 h, cycle 60 h
  ('PBI-05',  96,  72,  24),   --                                                → lead 72 h, cycle 48 h
  ('PBI-09',  72,  48,  12))   --                                                → lead 60 h, cycle 36 h
  AS x(ext, created_h, started_h, done_h)
JOIN issues i ON i.external_source = 'lab' AND i.external_id = x.ext AND i.deleted_at IS NULL
 AND i.project_id = (SELECT id FROM projects WHERE identifier = 'PLAB' AND deleted_at IS NULL);

-- ใบที่กำลังทำ (กลุ่ม started) ที่ไม่อยู่ในชุด "เสร็จ" — เรียงตามเลขใบ เอา 3 ใบแรก
INSERT INTO tm
SELECT w.id, w.sequence_id, w.external_id, h.created_h, h.started_h, NULL
FROM (SELECT i.id, i.sequence_id, i.external_id, row_number() OVER (ORDER BY i.sequence_id) AS rn
      FROM issues i JOIN states s ON s.id = i.state_id
      WHERE s."group" = 'started' AND i.deleted_at IS NULL AND i.id NOT IN (SELECT id FROM tm)
        AND i.project_id = (SELECT id FROM projects WHERE identifier = 'PLAB' AND deleted_at IS NULL)) w
JOIN (VALUES (1, 132, 120), (2, 84, 72), (3, 36, 24)) AS h(rn, created_h, started_h) ON h.rn = w.rn;

-- (1) สำรอง
CREATE TABLE IF NOT EXISTS lab5_backup_issues AS
  SELECT id, sequence_id, created_at, completed_at, state_id FROM issues WHERE false;
CREATE TABLE IF NOT EXISTS lab5_backup_activities AS
  SELECT * FROM issue_activities WHERE false;
INSERT INTO lab5_backup_issues
  SELECT i.id, i.sequence_id, i.created_at, i.completed_at, i.state_id FROM issues i
  WHERE i.id IN (SELECT id FROM tm) AND i.id NOT IN (SELECT id FROM lab5_backup_issues);
INSERT INTO lab5_backup_activities
  SELECT a.* FROM issue_activities a
  WHERE a.issue_id IN (SELECT id FROM tm) AND a.field = 'state' AND a.id NOT IN (SELECT id FROM lab5_backup_activities);

\echo '--- BEFORE'
SELECT 'PLAB-' || i.sequence_id AS item, t.ext, s.name AS state, i.created_at, i.completed_at,
       (SELECT count(*) FROM issue_activities a WHERE a.issue_id = i.id AND a.field = 'state') AS state_activities
FROM tm t JOIN issues i ON i.id = t.id JOIN states s ON s.id = i.state_id ORDER BY i.sequence_id;

-- (2) เวลาในตาราง issues + state ของใบที่เสร็จ = Done (กลุ่ม completed) ใน transaction เดียวกัน
UPDATE issues i
SET created_at   = now() - (t.created_h || ' hours')::interval,
    completed_at = CASE WHEN t.done_h IS NULL THEN NULL ELSE now() - (t.done_h || ' hours')::interval END,
    state_id     = CASE WHEN t.done_h IS NULL THEN i.state_id
                        ELSE (SELECT id FROM states WHERE project_id = i.project_id AND "group" = 'completed'
                              AND name = 'Done' AND deleted_at IS NULL) END
FROM tm t WHERE i.id = t.id;

-- (3) แทน activity state เดิมของใบเหล่านี้ (สำรองไว้แล้ว) ด้วยลำดับที่สอดคล้องกับเวลาใหม่
DELETE FROM issue_activities WHERE field = 'state' AND issue_id IN (SELECT id FROM tm);

INSERT INTO issue_activities (id, created_at, updated_at, verb, field, old_value, new_value, comment, attachments,
                              issue_id, project_id, workspace_id, actor_id, created_by_id, updated_by_id, epoch)
SELECT gen_random_uuid(), v.ts, v.ts, 'updated', 'state', v.old_v, v.new_v, 'updated the state to ' || v.new_v, '{}',
       i.id, i.project_id, i.workspace_id, u.id, u.id, u.id, extract(epoch FROM v.ts)
FROM tm t
JOIN issues i ON i.id = t.id
JOIN states s ON s.id = i.state_id                       -- state ปัจจุบัน (Done สำหรับใบที่เสร็จ / In Progress·In Review สำหรับ WIP)
CROSS JOIN (SELECT id FROM users WHERE email = 'admin@example.com') u
CROSS JOIN LATERAL (VALUES
  (now() - (t.created_h - 1 || ' hours')::interval, 'Backlog', 'Todo'),
  (now() - (t.started_h || ' hours')::interval,     'Todo',    CASE WHEN t.done_h IS NULL THEN s.name ELSE 'In Progress' END),
  (CASE WHEN t.done_h IS NULL THEN NULL ELSE now() - (t.done_h || ' hours')::interval END, 'In Progress', 'Done')
) AS v(ts, old_v, new_v)
WHERE v.ts IS NOT NULL;

\echo '--- AFTER'
SELECT 'PLAB-' || i.sequence_id AS item, t.ext, s.name AS state, i.created_at, i.completed_at,
       round(extract(epoch FROM (i.completed_at - i.created_at)) / 3600) AS lead_h,
       (SELECT count(*) FROM issue_activities a WHERE a.issue_id = i.id AND a.field = 'state') AS state_activities
FROM tm t JOIN issues i ON i.id = t.id JOIN states s ON s.id = i.state_id ORDER BY i.sequence_id;
COMMIT;

-- RESTORE (ถ้าอยากได้ state/เวลาเดิมคืน): รันสามคำสั่งนี้ใน psql
-- UPDATE issues i SET created_at=b.created_at, completed_at=b.completed_at, state_id=b.state_id FROM lab5_backup_issues b WHERE b.id=i.id;
-- DELETE FROM issue_activities WHERE field='state' AND issue_id IN (SELECT id FROM lab5_backup_issues);
-- INSERT INTO issue_activities SELECT * FROM lab5_backup_activities;
