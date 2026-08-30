-- =====================================================================
-- SkillSpace · ข้อมูลตั้งต้นของฐานข้อมูล skillspace สำหรับตารางทั้ง 5
--   ครุภัณฑ์ 12 · ใบแจ้งซ่อม 8 (คละสถานะ ค้างเกินกำหนด 2)
--   สัญญายืม 3 (ยังไม่คืน 2) · อะไหล่ 6 (ต่ำกว่าจุดสั่งซื้อ 2)
--
-- ใช้ now() - interval แทนวันที่ตายตัว เพราะ "ค้างเกินกำหนด" ต้องจริงเสมอ
-- ไม่ว่าจะสร้างฐานข้อมูลวันไหน (ถ้า hard-code วันที่ พอเวลาผ่านไป REQ-09 จะเพี้ยน)
-- =====================================================================

-- ---------- ครุภัณฑ์ 12 ชิ้น ----------
INSERT INTO assets (code, name, location) VALUES
    ('A-001', 'โน้ตบุ๊ก Dell Latitude',       'ห้องพัสดุ ชั้น 1'),
    ('A-002', 'โปรเจกเตอร์ Epson EB-X51',     'ห้องอบรม 301'),
    ('A-003', 'กล้อง Sony ZV-1',              'ห้องพัสดุ ชั้น 1'),
    ('A-004', 'ไมโครโฟนไร้สาย Shure',         'ห้องประชุมใหญ่'),
    ('A-005', 'โปรเจกเตอร์ BenQ MW550',       'ห้องอบรม 205'),
    ('A-006', 'เครื่องปรับอากาศ ห้องแล็บ 2',  'ห้องแล็บคอมพิวเตอร์ 2'),
    ('A-007', 'เครื่องพิมพ์ HP LaserJet',     'สำนักงาน ชั้น 2'),
    ('A-008', 'สวิตช์เครือข่าย 24 พอร์ต',     'ห้องเซิร์ฟเวอร์'),
    ('A-009', 'โน้ตบุ๊ก Lenovo ThinkPad',     'ห้องแล็บคอมพิวเตอร์ 4'),
    ('A-010', 'จอแสดงผล LG 27 นิ้ว',          'ห้องแล็บคอมพิวเตอร์ 1'),
    ('A-011', 'เครื่องสแกนเอกสาร Canon',      'สำนักงาน ชั้น 2'),
    ('A-012', 'ลำโพงห้องอบรม 402',            'ห้องอบรม 402');

-- ---------- สัญญายืม 3 รายการ (ยังไม่คืน 2) ----------
-- A-001 กับ A-002 ยังไม่คืน → ยืมซ้ำต้องได้ 409 ASSET_ON_LOAN (REQ-10)
-- A-003 คืนแล้ว → ยืมใหม่ได้ ใช้เป็นเคสสำเร็จของแล็บ
INSERT INTO loans (asset_id, borrower, borrowed_at, returned_at) VALUES
    ((SELECT id FROM assets WHERE code = 'A-001'), 'วิทยากรหลักสูตร Data 101', now() - interval '4 days',  NULL),
    ((SELECT id FROM assets WHERE code = 'A-002'), 'เจ้าหน้าที่ธุรการ',     now() - interval '1 day',   NULL),
    ((SELECT id FROM assets WHERE code = 'A-003'), 'วิทยากรหลักสูตร UX 204', now() - interval '10 days', now() - interval '6 days');

-- ---------- ใบแจ้งซ่อม 8 ใบ ----------
-- จงใจผูกกับครุภัณฑ์คนละชิ้นกับที่ถูกยืมค้าง (A-001/A-002)
-- เพื่อให้แยกเคส ASSET_ON_LOAN ออกจาก ASSET_IN_REPAIR ได้ชัดตอนทดสอบ
-- นับตามสถานะ : NEW 3 · ASSIGNED 2 · IN_PROGRESS 1 · DONE 2
-- ค้างเกินกำหนด 2 ใบ = ใบ HIGH อายุ 5 วัน (SLA 1) และใบ NORMAL อายุ 9 วัน (SLA 3)
INSERT INTO tickets (asset_id, title, detail, priority, status, assignee, created_at, closed_at) VALUES
    -- 1) ค้างเกินกำหนดใบที่ 1 : HIGH อายุ 5 วัน > SLA 1 วัน
    ((SELECT id FROM assets WHERE code = 'A-005'), 'โปรเจกเตอร์ห้อง 205 ภาพวูบดับ',
     'เปิดไปสักพักภาพดับเอง ต้องถอดปลั๊กแล้วเสียบใหม่', 'HIGH', 'NEW', NULL,
     now() - interval '5 days', NULL),

    -- 2) เพิ่งแจ้งวันนี้ ยังไม่ค้าง
    ((SELECT id FROM assets WHERE code = 'A-006'), 'แอร์ห้องแล็บ 2 ไม่เย็น',
     'ลมออกแต่ไม่เย็น อาจต้องเติมน้ำยา', 'NORMAL', 'NEW', NULL,
     now() - interval '2 hours', NULL),

    -- 3) LOW อายุ 2 วัน ยังไม่เกิน SLA 7 วัน
    ((SELECT id FROM assets WHERE code = 'A-007'), 'เครื่องพิมพ์ป้อนกระดาษซ้อน',
     'ดึงกระดาษทีละ 2 แผ่น', 'LOW', 'NEW', NULL,
     now() - interval '2 days', NULL),

    -- 4) ค้างเกินกำหนดใบที่ 2 : NORMAL อายุ 9 วัน > SLA 3 วัน
    ((SELECT id FROM assets WHERE code = 'A-008'), 'สวิตช์เครือข่ายพอร์ต 12 ไฟไม่ติด',
     'เสียบสายแล้วไม่มีลิงก์ ย้ายไปพอร์ตอื่นใช้ได้', 'NORMAL', 'ASSIGNED', 'TECH-01',
     now() - interval '9 days', NULL),

    -- 5) HIGH แต่เพิ่งมอบหมายวันนี้ ยังไม่ค้าง
    ((SELECT id FROM assets WHERE code = 'A-009'), 'โน้ตบุ๊กแล็บ 4 เปิดไม่ติด',
     'กดปุ่มแล้วไฟไม่ขึ้นเลย', 'HIGH', 'ASSIGNED', 'TECH-02',
     now() - interval '3 hours', NULL),

    -- 6) กำลังทำ NORMAL อายุ 1 วัน ยังไม่เกิน SLA 3 วัน
    ((SELECT id FROM assets WHERE code = 'A-010'), 'จอแล็บ 1 มีเส้นแนวตั้ง',
     'เส้นสีชมพูกลางจอ', 'NORMAL', 'IN_PROGRESS', 'TECH-01',
     now() - interval '1 day', NULL),

    -- 7) ปิดงานแล้ว (ใบที่ใช้อะไหล่ ดูประวัติได้ที่ stock_moves)
    ((SELECT id FROM assets WHERE code = 'A-011'), 'สแกนเนอร์สแกนแล้วมีเส้นดำ',
     'ทำความสะอาดกระจกแล้วยังเป็น', 'LOW', 'DONE', 'TECH-03',
     now() - interval '12 days', now() - interval '9 days'),

    -- 8) ปิดงานแล้ว
    ((SELECT id FROM assets WHERE code = 'A-012'), 'ลำโพงห้อง 402 ไม่มีเสียง',
     'สายชำรุด เปลี่ยนสายใหม่', 'HIGH', 'DONE', 'TECH-01',
     now() - interval '7 days', now() - interval '6 days');

-- ---------- อะไหล่ 6 รายการ (ต่ำกว่าจุดสั่งซื้อ 2) ----------
-- LAMP-EPS-01 (2 < 5) และ CBL-HDMI-3M (1 < 6) คือสองรายการที่ต้องขึ้นเตือน (REQ-12)
-- ของสองตัวนี้ยอดน้อยโดยตั้งใจ ใช้เป็นเคสทดสอบเบิกเกินยอด (REQ-06) ได้เลย
INSERT INTO parts (sku, name, qty_on_hand, reorder_point) VALUES
    ('LAMP-EPS-01',  'หลอดโปรเจกเตอร์ Epson',      2, 5),
    ('FAN-NB-14',    'พัดลมระบายความร้อนโน้ตบุ๊ก', 12, 4),
    ('KBD-USB-01',   'คีย์บอร์ด USB',              8, 3),
    ('CBL-HDMI-3M',  'สาย HDMI ยาว 3 เมตร',        1, 6),
    ('SSD-256',      'SSD 256GB',                  20, 5),
    ('MIC-CAP-01',   'หัวไมโครโฟนสำรอง',            9, 2);

-- ---------- ประวัติการเคลื่อนไหวของอะไหล่ ----------
-- มีทั้งรับเข้า (delta บวก) และเบิกใช้ในงานซ่อม (delta ลบ) เพื่อให้ REQ-07 มีของให้ดู
INSERT INTO stock_moves (part_id, ticket_id, delta, reason, created_at) VALUES
    ((SELECT id FROM parts WHERE sku = 'LAMP-EPS-01'), NULL, 5, 'รับเข้าจากผู้ขาย', now() - interval '30 days'),
    ((SELECT id FROM parts WHERE sku = 'LAMP-EPS-01'), NULL, -3, 'เบิกใช้เตรียมห้องอบรมประจำเดือน', now() - interval '20 days'),
    ((SELECT id FROM parts WHERE sku = 'CBL-HDMI-3M'), NULL, 6, 'รับเข้าจากผู้ขาย', now() - interval '25 days'),
    ((SELECT id FROM parts WHERE sku = 'CBL-HDMI-3M'),
     (SELECT id FROM tickets WHERE title = 'ลำโพงห้อง 402 ไม่มีเสียง'),
     -5, 'ใช้ในงานซ่อม', now() - interval '6 days'),
    ((SELECT id FROM parts WHERE sku = 'KBD-USB-01'), NULL, 9, 'รับเข้าจากผู้ขาย', now() - interval '28 days'),
    ((SELECT id FROM parts WHERE sku = 'KBD-USB-01'),
     (SELECT id FROM tickets WHERE title = 'สแกนเนอร์สแกนแล้วมีเส้นดำ'),
     -1, 'ใช้ในงานซ่อม', now() - interval '9 days');
-- ยอดรวมของ delta ข้างบนตรงกับ qty_on_hand ของอะไหล่แต่ละตัวโดยตั้งใจ
-- (5-3=2 · 6-5=1 · 9-1=8) เพื่อให้ประวัติกับยอดคงเหลืออ่านแล้วไม่ขัดกัน
