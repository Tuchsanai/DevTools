// unit test ข้อมูลสินค้า — stage Test รันด้วย `npm test` ใน image ที่เพิ่ง build
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { products, categories } from '../data/products.js';

test('ทุกสินค้ามีราคาเป็นจำนวนเต็มบวก', () => {
  for (const p of products) {
    assert.ok(Number.isInteger(p.price) && p.price > 0, `${p.id}: ราคา ${p.price} ไม่ถูกต้อง`);
  }
});

test('id ไม่ซ้ำ และทุกสินค้าอยู่ในหมวดที่มีจริง', () => {
  assert.equal(new Set(products.map((p) => p.id)).size, products.length, 'มี id ซ้ำ');
  const ids = categories.map((c) => c.id);
  for (const p of products) assert.ok(ids.includes(p.category), `${p.id}: ไม่มีหมวด ${p.category}`);
});

test('ไฟล์รูปสินค้ามีอยู่จริง', () => {
  for (const p of products) {
    assert.ok(existsSync(new URL(`../public${p.image}`, import.meta.url)), `${p.id}: ไม่พบ ${p.image}`);
  }
});
