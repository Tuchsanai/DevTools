import { pool } from '@/lib/db';
import { shopInfo } from '@/lib/shop';

export const dynamic = 'force-dynamic';

// GET /api/stats → "som-web-4nhz6 1.2 orders=3 products=6"
// ใช้เทียบว่าทุกบูธเห็นออเดอร์ "ชุดเดียวกัน" (db กลาง) — db ยังไม่มีตาราง → 503
export async function GET() {
  const { podName, version } = shopInfo();
  const text = (s: string, status = 200) =>
    new Response(`${podName} ${version} ${s}\n`, { status, headers: { 'content-type': 'text/plain; charset=utf-8' } });
  try {
    const { rows } = await pool.query<{ orders: number; products: number }>(
      'SELECT (SELECT count(*)::int FROM orders) AS orders, (SELECT count(*)::int FROM products) AS products',
    );
    return text(`orders=${rows[0].orders} products=${rows[0].products}`);
  } catch {
    return text('db-not-ready', 503);
  }
}
