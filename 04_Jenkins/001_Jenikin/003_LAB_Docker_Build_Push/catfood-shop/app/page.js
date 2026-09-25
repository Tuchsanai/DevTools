import Shop from './components/Shop';
import { products, categories } from '../data/products';
import { getBuildInfo } from '../data/buildInfo';

// อ่าน build info ทุก request (ไม่ prerender ตอน build) เพื่อให้เห็นค่าจาก container ที่รันจริง
export const dynamic = 'force-dynamic';

const perks = [
  { icon: '🚚', title: 'ส่งฟรีทั่วไทย', text: 'เมื่อสั่งครบ ฿599 ถึงมือใน 1–2 วัน' },
  { icon: '🩺', title: 'สัตวแพทย์คัดสรร', text: 'ทุกสูตรผ่านการตรวจสอบโภชนาการ' },
  { icon: '💛', title: 'น้องไม่กิน ยินดีคืน', text: 'รับคืนภายใน 14 วัน ไม่ต้องถามเหตุผล' },
];

export default function Home() {
  const info = getBuildInfo();

  return (
    <>
      <div className="ribbon">
        <span>🎉 โปรเดือนนี้: ขนมแมวทุกชิ้นลด 10% · ส่งฟรีเมื่อครบ ฿599</span>
        <span className="chip" data-testid="version-chip">
          v{info.version} · build #{info.build}
        </span>
      </div>

      <header className="nav">
        <a className="logo" href="#">
          <span className="logo-paw">🐾</span> Meow&nbsp;Mart
        </a>
        <nav>
          <a href="#shop">สินค้า</a>
          <a href="#perks">ทำไมต้องเรา</a>
          <a href="#deploy">Deployment</a>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-text">
          <p className="eyebrow">ร้านอาหารแมวออนไลน์</p>
          <h1>
            อาหารดี ๆ<br />
            <span>สำหรับเจ้านายตัวน้อย</span>
          </h1>
          <p className="lead">
            คัดสรรอาหารเม็ด อาหารเปียก และขนมแมวคุณภาพพรีเมียม
            ส่งตรงถึงบ้านพร้อมคำแนะนำจากสัตวแพทย์
          </p>
          <div className="hero-cta">
            <a className="btn primary" href="#shop">เลือกซื้อเลย</a>
            <a className="btn ghost" href="#deploy">ดูข้อมูล build</a>
          </div>
          <ul className="stats">
            <li><b>12k+</b> น้องแมวที่ไว้ใจ</li>
            <li><b>4.9★</b> รีวิวเฉลี่ย</li>
            <li><b>24 ชม.</b> จัดส่งด่วน</li>
          </ul>
        </div>
        <div className="hero-art" aria-hidden="true">
          <img src="/images/hero_cat.jpg" alt="" />
        </div>
      </section>

      <Shop products={products} categories={categories} />

      <section id="perks" className="perks">
        {perks.map((p) => (
          <article key={p.title}>
            <span className="perk-icon">{p.icon}</span>
            <h3>{p.title}</h3>
            <p>{p.text}</p>
          </article>
        ))}
      </section>

      <section id="deploy" className="deploy">
        <div>
          <p className="eyebrow">Deployment info</p>
          <h2>เว็บนี้มาจาก image ไหน?</h2>
          <p className="muted">
            ค่าในตารางถูกฝังเข้า Docker image ตอน build และอ่านจาก container ที่กำลังรันจริง
            ใช้ยืนยันว่า Pipeline deploy เวอร์ชันที่ต้องการแล้ว
          </p>
        </div>
        <dl className="info-grid" data-testid="build-info">
          <div><dt>Version</dt><dd>{info.version}</dd></div>
          <div><dt>Jenkins build</dt><dd>#{info.build}</dd></div>
          <div><dt>Git commit</dt><dd>{info.commit}</dd></div>
          <div><dt>Built at (UTC)</dt><dd>{info.builtAt}</dd></div>
          <div><dt>Container</dt><dd>{info.host}</dd></div>
          <div><dt>Health API</dt><dd>/api/health</dd></div>
        </dl>
      </section>

      <footer className="footer">
        <span>🐾 Meow Mart · Jenkins CI/CD LAB</span>
        <span>
          catfood-shop v{info.version} · build #{info.build} · commit {info.commit}
        </span>
      </footer>
    </>
  );
}
