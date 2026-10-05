import os from 'node:os';

// ข้อมูลประจำ Pod/รุ่น ที่แสดงบนหน้าเว็บ (APP_VERSION/APP_THEME มาจาก build-arg ใน Dockerfile)
export function shopInfo() {
  return {
    podName: os.hostname(), // ใน Kubernetes = ชื่อ Pod
    version: process.env.APP_VERSION ?? 'dev',
    theme: process.env.APP_THEME ?? 'harbor',
    shopName: process.env.SHOP_NAME ?? 'ร้านอาหารแมวน้องส้ม',
  };
}

// หน้า "ร้านกำลังเตรียมสินค้า" (HTML ล้วน) — ส่งพร้อม HTTP 503 เมื่ออ่านตารางใน db ไม่ได้
// เช่น Pod db เพิ่งเกิดใหม่ (emptyDir ว่าง) และยังไม่มีใคร seed ตาราง
export function preparingHtml() {
  const { podName, version, theme, shopName } = shopInfo();
  const bg = theme === 'sunset' ? 'linear-gradient(135deg,#ff7a45,#ff4f8b)' : 'linear-gradient(135deg,#1b2a5c,#1a9e9a)';
  return `<!doctype html><html lang="th"><head><meta charset="utf-8"><meta http-equiv="refresh" content="5">
<title>${shopName} · กำลังเตรียมสินค้า</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:'Noto Sans Thai','Leelawadee UI',Tahoma,sans-serif;background:${bg};color:#fff;text-align:center}
.box{background:rgba(255,255,255,.12);padding:32px 40px;border-radius:20px;max-width:560px}
h1{margin:12px 0}code{background:#f39a2b;color:#1b2a5c;padding:2px 10px;border-radius:8px;font-weight:700}</style></head>
<body><div class="box"><img src="/som.png" width="96" height="96" alt="น้องส้ม" style="border-radius:50%;background:#fff">
<h1>ร้านกำลังเตรียมสินค้า กรุณารอสักครู่ 🐱</h1>
<p>ฐานข้อมูลยังไม่มีสินค้า (HTTP 503) · หน้านี้จะลองใหม่เองทุก 5 วินาที</p>
<p>เสิร์ฟโดย Pod: <code>${podName}</code> · เวอร์ชัน ${version}</p></div></body></html>`;
}
