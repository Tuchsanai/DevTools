-- =====================================================================
-- SkillSpace · โครงสร้างฐานข้อมูล (5 ตาราง ตาม docs/02_contract.md §3)
-- ไฟล์ใน /docker-entrypoint-initdb.d จะถูกรันเรียงตามชื่อไฟล์
-- และรัน "ครั้งแรกครั้งเดียว" ตอน data directory ยังว่างเท่านั้น
-- =====================================================================

-- ครุภัณฑ์ · ไม่มีคอลัมน์ status เพราะสถานะเป็นค่าที่ "คำนวณ" จาก tickets/loans
-- (เก็บเป็นคอลัมน์เมื่อไหร่ ข้อมูลจะขัดกันเองทันทีเมื่อลืมอัปเดต)
CREATE TABLE assets (
    id          SERIAL PRIMARY KEY,
    code        TEXT        NOT NULL UNIQUE,
    name        TEXT        NOT NULL,
    location    TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ใบแจ้งซ่อม
-- CHECK คุมค่าที่เป็นไปได้ตั้งแต่ชั้นฐานข้อมูล เผื่อมีใครยิง SQL ตรง ๆ ข้าม API
CREATE TABLE tickets (
    id          SERIAL PRIMARY KEY,
    asset_id    INTEGER     NOT NULL REFERENCES assets(id),
    title       TEXT        NOT NULL,
    detail      TEXT        NOT NULL DEFAULT '',
    priority    TEXT        NOT NULL CHECK (priority IN ('LOW', 'NORMAL', 'HIGH')),
    status      TEXT        NOT NULL DEFAULT 'NEW'
                            CHECK (status IN ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'DONE')),
    assignee    TEXT        NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at   TIMESTAMPTZ NULL
);

-- สัญญายืม · returned_at IS NULL = ยังไม่คืน (ใช้ตัดสิน ASSET_ON_LOAN)
CREATE TABLE loans (
    id          SERIAL PRIMARY KEY,
    asset_id    INTEGER     NOT NULL REFERENCES assets(id),
    borrower    TEXT        NOT NULL,
    borrowed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    returned_at TIMESTAMPTZ NULL
);

-- อะไหล่ · CHECK qty_on_hand >= 0 คือด่านสุดท้าย
-- ชั้น API ตรวจก่อนอยู่แล้ว แต่ถ้าโค้ดพลาด ฐานข้อมูลจะไม่ยอมให้ติดลบ
CREATE TABLE parts (
    id            SERIAL PRIMARY KEY,
    sku           TEXT    NOT NULL UNIQUE,
    name          TEXT    NOT NULL,
    qty_on_hand   INTEGER NOT NULL CHECK (qty_on_hand >= 0),
    reorder_point INTEGER NOT NULL DEFAULT 0
);

-- การเคลื่อนไหวของอะไหล่ · delta ติดลบ = เบิกออก, บวก = รับเข้า
-- ticket_id NULL ได้ เพราะการรับเข้าคลังไม่ได้ผูกกับใบแจ้งซ่อมใบไหน
CREATE TABLE stock_moves (
    id          SERIAL PRIMARY KEY,
    part_id     INTEGER     NOT NULL REFERENCES parts(id),
    ticket_id   INTEGER     NULL REFERENCES tickets(id),
    delta       INTEGER     NOT NULL,
    reason      TEXT        NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ดัชนีตามคอลัมน์ที่ API ใช้กรองบ่อย (REQ-04 กรองตามช่าง · REQ-07 ประวัติอะไหล่)
CREATE INDEX idx_tickets_status   ON tickets(status);
CREATE INDEX idx_tickets_assignee ON tickets(assignee);
CREATE INDEX idx_loans_asset_open ON loans(asset_id) WHERE returned_at IS NULL;
CREATE INDEX idx_moves_part       ON stock_moves(part_id, created_at DESC);
