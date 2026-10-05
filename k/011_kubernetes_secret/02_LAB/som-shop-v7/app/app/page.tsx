import Image from 'next/image';
import { pool, type Product } from '@/lib/db';
import { shopInfo, readAnnouncement } from '@/lib/shop';
import OrderButton from './OrderButton';

// อ่านข้อมูลจากฐานข้อมูลทุกครั้งที่เปิดหน้า (ไม่ build เป็นหน้า static)
export const dynamic = 'force-dynamic';

const CATEGORY: Record<Product['category'], string> = {
  dry: 'อาหารเม็ด',
  wet: 'อาหารเปียก',
  treat: 'ขนมแมว',
};

const baht = (v: string) => Number(v).toLocaleString('th-TH', { maximumFractionDigits: 0 });

export default async function Home() {
  const { shopName, podName, version, theme, promo } = shopInfo();
  const announcement = readAnnouncement(); // 1.5: อ่านไฟล์ใหม่ทุกครั้งที่เปิดหน้า
  // ข้อความหัว/ท้ายหน้าอ่านจาก env (ไม่ตั้ง = ค่าเริ่มต้นของบท 006)
  const eyebrow = process.env.SHOP_EYEBROW ?? '⚓ ท่าเรือ Kubernetes · ReplicaSet + Service';
  const footerNote = process.env.SHOP_FOOTER ?? 'Next.js + PostgreSQL · Kubernetes LAB 006';
  const podLine = `🐱 เสิร์ฟโดย Pod: ${podName} · เวอร์ชัน ${version}`; // ข้อความก้อนเดียว → grep ง่าย

  let data;
  try {
    data = await Promise.all([
      pool.query<Product>('SELECT id, sku, name_th, category, price_baht, stock, emoji FROM products ORDER BY id'),
      pool.query<{ orders: number; items: number }>(
        'SELECT count(*)::int AS orders, coalesce(sum(qty), 0)::int AS items FROM orders',
      ),
      pool.query<{ id: number; name_th: string; qty: number; at: string }>(
        `SELECT o.id, p.name_th, o.qty, to_char(o.created_at AT TIME ZONE 'Asia/Bangkok', 'HH24:MI:SS') AS at
           FROM orders o JOIN products p ON p.id = o.product_id ORDER BY o.id DESC LIMIT 5`,
      ),
    ]);
  } catch {
    // ปกติ proxy.ts ตอบ 503 ไปก่อนแล้ว — ตรงนี้กันกรณี db หายระหว่างโหลดหน้า
    return (
      <main className={`theme-${theme} preparing`}>
        <h1>ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱</h1>
        <p>{podLine}</p>
      </main>
    );
  }
  const [products, stats, recent] = data;
  const { orders, items } = stats.rows[0];

  return (
    <div className={`theme-${theme}`}>
      {promo && <div className="promo">{promo}</div>}
      {announcement && <div className="announcement">📢 {announcement}</div>}
      <header className="hero">
        <div className="hero-inner">
          <Image src="/som.png" alt="น้องส้ม" width={120} height={120} className="avatar" priority />
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h1>
              {shopName} <span className="version">{`เวอร์ชัน ${version}`}</span>
            </h1>
            <p className="podbar">{podLine}</p>
            <p className="tagline">อาหารแมวคัดพิเศษโดยน้องส้ม ผู้ช่วยกัปตันประจำท่าเรือ</p>
          </div>
        </div>
        <div className="stats">
          <div className="stat">
            <span className="num">{orders.toLocaleString('th-TH')}</span>
            <span className="label">ออเดอร์ทั้งหมด</span>
          </div>
          <div className="stat">
            <span className="num">{items.toLocaleString('th-TH')}</span>
            <span className="label">ชิ้นที่ขายแล้ว</span>
          </div>
          <div className="stat">
            <span className="num">{products.rows.length}</span>
            <span className="label">สินค้าในร้าน</span>
          </div>
        </div>
      </header>

      <main className="container">
        <h2 className="section-title">เมนูวันนี้ 🐾</h2>
        <section className="grid">
          {products.rows.map((p) => (
            <article key={p.id} className="card">
              <div className={`emoji cat-${p.category}`}>{p.emoji ?? '🐱'}</div>
              <span className={`badge cat-${p.category}`}>{CATEGORY[p.category]}</span>
              <h3>{p.name_th}</h3>
              <p className="sku">{p.sku}</p>
              <div className="price-row">
                <span className="price">฿{baht(p.price_baht)}</span>
                <span className={p.stock <= 5 ? 'stock low' : 'stock'}>เหลือ {p.stock} ชิ้น</span>
              </div>
              <OrderButton productId={p.id} stock={p.stock} />
            </article>
          ))}
        </section>

        <section className="recent">
          <h2 className="section-title">ออเดอร์ล่าสุด</h2>
          {recent.rows.length === 0 ? (
            <p className="empty">ยังไม่มีออเดอร์ ลองกดสั่งซื้อดูสิ 😺</p>
          ) : (
            <ul>
              {recent.rows.map((o) => (
                <li key={o.id}>
                  <span className="oid">#{o.id}</span> {o.name_th} × {o.qty} <span className="at">{o.at}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <footer className="footer">
        <span>
          🐱 เสิร์ฟโดย Pod: <code>{podName}</code>
        </span>
        <span className="muted">{footerNote}</span>
      </footer>
    </div>
  );
}
