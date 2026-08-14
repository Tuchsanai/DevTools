-- สคริปต์นี้ทำงานเฉพาะครั้งแรกที่ PostgreSQL volume ยังว่าง
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  owner TEXT NOT NULL DEFAULT 'student',
  status TEXT NOT NULL DEFAULT 'seed',
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- ข้อมูลตัวอย่างสำหรับ DevOps Board
INSERT INTO items (name, owner, status) VALUES
  ('เขียน Dockerfile ให้ web', 'stage build', 'seed'),
  ('สร้าง Flask API image', 'backend team', 'seed'),
  ('เชื่อม Redis ด้วย Compose', 'platform team', 'seed'),
  ('เตรียม PostgreSQL volume', 'database team', 'seed');
