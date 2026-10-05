import { pool } from '@/lib/db';

export const dynamic = 'force-dynamic';

// ใช้กับ readinessProbe / livenessProbe ของ container web
export async function GET() {
  try {
    await pool.query('SELECT 1');
    return Response.json({ ok: true, db: 'up' });
  } catch {
    return Response.json({ ok: false, db: 'down' }, { status: 503 });
  }
}
