'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function OrderButton({ productId, stock }: { productId: number; stock: number }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  async function order() {
    setBusy(true);
    setMsg(null);
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, qty: 1 }),
      });
      const data = await res.json();
      setMsg(res.ok ? { ok: true, text: `สั่งซื้อแล้ว! ออเดอร์ #${data.order_id}` } : { ok: false, text: data.error });
      router.refresh(); // โหลดข้อมูล stock / จำนวนออเดอร์ใหม่จากเซิร์ฟเวอร์
    } catch {
      setMsg({ ok: false, text: 'เชื่อมต่อร้านไม่ได้' });
    } finally {
      setBusy(false);
    }
  }

  const soldOut = stock <= 0;
  return (
    <div className="order">
      <button className="btn" onClick={order} disabled={busy || soldOut}>
        {soldOut ? 'สินค้าหมด' : busy ? 'กำลังสั่ง…' : '🛒 สั่งซื้อ'}
      </button>
      {msg && <p className={msg.ok ? 'msg ok' : 'msg err'}>{msg.text}</p>}
    </div>
  );
}
