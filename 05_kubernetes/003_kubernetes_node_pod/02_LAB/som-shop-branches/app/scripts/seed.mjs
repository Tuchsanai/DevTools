// สร้างตารางและใส่ข้อมูลตั้งต้น — รันใน init container "db-seed"
// รันซ้ำได้ (idempotent): CREATE TABLE IF NOT EXISTS + INSERT ... ON CONFLICT DO NOTHING
import pg from 'pg';

const products = [
  ['DRY-TUNA-15', 'อาหารเม็ดสูตรปลาทูน่า 1.5 กก.', 'dry', 459, 20, '🐟'],
  ['DRY-KITTEN-1', 'อาหารเม็ดลูกแมว สูตรนมแพะ 1 กก.', 'dry', 389, 15, '🍼'],
  ['DRY-SENIOR-12', 'อาหารเม็ดแมวสูงวัย 1.2 กก.', 'dry', 499, 10, '🐾'],
  ['WET-SABA-85', 'อาหารเปียกปลาซาบะ 85 ก.', 'wet', 35, 60, '🥫'],
  ['TRT-LICK-4', 'ขนมแมวเลียรสไก่ (แพ็ก 4)', 'treat', 59, 40, '🍗'],
  ['TRT-SALMON-40', 'ขนมฟรีซดรายแซลมอน 40 ก.', 'treat', 129, 25, '🍣'],
];

const client = new pg.Client({ connectionString: process.env.DATABASE_URL });
await client.connect();
console.log('connected to database');

await client.query(`
  CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    sku         TEXT UNIQUE NOT NULL,
    name_th     TEXT NOT NULL,
    category    TEXT NOT NULL CHECK (category IN ('dry','wet','treat')),
    price_baht  NUMERIC(8,2) NOT NULL CHECK (price_baht >= 0),
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    emoji       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
  );
  CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    qty         INTEGER NOT NULL CHECK (qty > 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
  );
`);
console.log('tables ready: products, orders');

let inserted = 0;
for (const [sku, name, category, price, stock, emoji] of products) {
  const r = await client.query(
    `INSERT INTO products (sku, name_th, category, price_baht, stock, emoji)
     VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (sku) DO NOTHING`,
    [sku, name, category, price, stock, emoji],
  );
  inserted += r.rowCount;
}
const { rows } = await client.query('SELECT count(*)::int AS n FROM products');
console.log(`seeded ${rows[0].n} products (new: ${inserted})`);
await client.end();
