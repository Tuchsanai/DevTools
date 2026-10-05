import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';
import { preparingHtml } from '@/lib/shop';

// proxy (ชื่อใหม่ของ middleware ใน Next.js 16) ทำงานก่อนหน้าแรก "/"
// ตรวจว่าตาราง products มีอยู่ไหม: ไม่มี/ต่อ db ไม่ได้ → ตอบหน้า "ร้านกำลังเตรียมสินค้า" ด้วย 503
// (/api/health ไม่ตรวจตาราง Pod จึงยัง Ready และ Service ยังส่งลูกค้ามาได้)
export const config = { matcher: '/' };

export async function proxy() {
  try {
    await pool.query('SELECT 1 FROM products LIMIT 1');
    return NextResponse.next();
  } catch {
    return new NextResponse(preparingHtml(), {
      status: 503,
      headers: { 'content-type': 'text/html; charset=utf-8', 'retry-after': '5' },
    });
  }
}
