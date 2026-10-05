import { pool } from '@/lib/db';

export const dynamic = 'force-dynamic';

export async function GET() {
  const { rows } = await pool.query(
    'SELECT id, sku, name_th, category, price_baht, stock, emoji FROM products ORDER BY id',
  );
  return Response.json(rows);
}
