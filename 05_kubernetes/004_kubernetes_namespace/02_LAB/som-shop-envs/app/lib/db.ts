import { Pool } from 'pg';

// ต่อฐานข้อมูลผ่าน DATABASE_URL เช่น postgres://som:meow1234@localhost:5432/catshop
// ใน Pod เดียวกัน web กับ db ใช้ network ร่วมกัน จึงเรียก db ด้วย localhost ได้
const globalForPool = globalThis as unknown as { pool?: Pool };

export const pool =
  globalForPool.pool ??
  new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 5,
    connectionTimeoutMillis: 2000,
  });

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
