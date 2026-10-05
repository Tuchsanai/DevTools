import { pool } from '@/lib/db';

export const dynamic = 'force-dynamic';

// POST /api/orders  body: {"product_id": 1, "qty": 1}
export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const productId = Number(body.product_id);
  const qty = Number(body.qty ?? 1);
  if (!Number.isInteger(productId) || !Number.isInteger(qty) || qty < 1 || qty > 10) {
    return Response.json({ ok: false, error: 'ข้อมูลไม่ถูกต้อง' }, { status: 400 });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    // ลด stock เฉพาะเมื่อมีของพอ (ทำใน transaction เดียวกับการบันทึกออเดอร์)
    const updated = await client.query(
      'UPDATE products SET stock = stock - $2 WHERE id = $1 AND stock >= $2 RETURNING id, name_th, stock',
      [productId, qty],
    );
    if (updated.rowCount === 0) {
      await client.query('ROLLBACK');
      return Response.json({ ok: false, error: 'สินค้าไม่พอหรือไม่มีสินค้านี้' }, { status: 409 });
    }
    const order = await client.query(
      'INSERT INTO orders (product_id, qty) VALUES ($1, $2) RETURNING id',
      [productId, qty],
    );
    await client.query('COMMIT');
    return Response.json({ ok: true, order_id: order.rows[0].id, product: updated.rows[0] }, { status: 201 });
  } catch (err) {
    await client.query('ROLLBACK').catch(() => {});
    console.error('order failed:', err);
    return Response.json({ ok: false, error: 'ระบบขัดข้อง' }, { status: 500 });
  } finally {
    client.release();
  }
}
