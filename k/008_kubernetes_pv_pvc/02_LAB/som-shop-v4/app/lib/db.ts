import { Pool } from 'pg';

// ต่อฐานข้อมูลผ่าน DATABASE_URL เช่น postgres://som:meow1234@som-db:5432/catshop
// บท 006: db อยู่คนละ Pod → เรียกด้วย "ชื่อ Service" (som-db) ไม่ใช่ IP ของ Pod
// Pod db เกิดใหม่ IP เปลี่ยนได้ แต่ชื่อและ ClusterIP ของ Service เดิมเสมอ (pool ต่อใหม่เองเมื่อสายเก่าขาด)
const globalForPool = globalThis as unknown as { pool?: Pool };

export const pool =
  globalForPool.pool ??
  new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 5,
    connectionTimeoutMillis: 2000,
  });

// Pod db ถูกลบ → สายที่ค้างใน pool ถูกตัด (terminating connection due to administrator command)
// ต้องดัก event 'error' ไว้ ไม่งั้นเป็น uncaughtException; pool จะเปิดสายใหม่ไปที่ som-db เองในครั้งถัดไป
if (!globalForPool.pool) {
  pool.on('error', (err) => console.warn(`db connection lost: ${err.message} (จะต่อใหม่เองใน request ถัดไป)`));
}

globalForPool.pool = pool;

export type Product = {
  id: number;
  sku: string;
  name_th: string;
  category: 'dry' | 'wet' | 'treat';
  price_baht: string;
  stock: number;
  emoji: string | null;
};
