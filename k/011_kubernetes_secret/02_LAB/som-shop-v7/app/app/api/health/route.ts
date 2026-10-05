import { pool } from '@/lib/db';

export const dynamic = 'force-dynamic';

// readinessProbe: ต่อ db ได้ไหม (SELECT 1) — ไม่ตรวจว่ามีตาราง
// ถ้าตรวจตารางด้วย ตอน db ใหม่ยังว่าง web ทุก Pod จะ not ready พร้อมกัน → Service ไม่มีที่ส่ง ทั้งร้านเข้าไม่ได้
export async function GET() {
  try {
    await pool.query('SELECT 1');
    return Response.json({ ok: true, db: 'up' });
  } catch {
    return Response.json({ ok: false, db: 'down' }, { status: 503 });
  }
}
