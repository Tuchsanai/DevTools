'use client';

import { useMemo, useState } from 'react';

const baht = (n) => `฿${n.toLocaleString('th-TH')}`;

export default function Shop({ products, categories }) {
  const [filter, setFilter] = useState('all');
  const [cart, setCart] = useState({});

  const shown = filter === 'all' ? products : products.filter((p) => p.category === filter);
  const count = Object.values(cart).reduce((a, b) => a + b, 0);
  const total = useMemo(
    () => products.reduce((sum, p) => sum + (cart[p.id] || 0) * p.price, 0),
    [cart, products]
  );

  const add = (id) => setCart((c) => ({ ...c, [id]: (c[id] || 0) + 1 }));

  return (
    <section id="shop" className="shop">
      <div className="shop-head">
        <div>
          <p className="eyebrow">สินค้าแนะนำ</p>
          <h2>เมนูโปรดของน้องแมว</h2>
        </div>
        <div className="cart" data-testid="cart">
          🛒 <b>{count}</b> ชิ้น · {baht(total)}
        </div>
      </div>

      <div className="filters" role="tablist">
        {categories.map((c) => (
          <button
            key={c.id}
            role="tab"
            aria-selected={filter === c.id}
            className={filter === c.id ? 'active' : ''}
            onClick={() => setFilter(c.id)}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="grid">
        {shown.map((p) => (
          <article className="card" key={p.id}>
            <div className="card-img">
              <img src={p.image} alt={p.name} loading="lazy" />
              {p.badge && <span className="badge">{p.badge}</span>}
            </div>
            <div className="card-body">
              <h3>{p.name}</h3>
              <p className="muted">{p.desc}</p>
              <p className="meta">
                <span>{p.size}</span>
                <span>★ {p.rating}</span>
              </p>
              <div className="card-foot">
                <span className="price">{baht(p.price)}</span>
                <button className="btn primary small" onClick={() => add(p.id)}>
                  + ใส่ตะกร้า
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
