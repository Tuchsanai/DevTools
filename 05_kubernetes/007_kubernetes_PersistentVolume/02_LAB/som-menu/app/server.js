// ร้านอาหารแมวน้องส้ม (PersistentVolume) — เว็บหน้าร้านเล็ก ๆ ด้วย Node.js ล้วน ไม่มี dependency
// ลูกค้ากดสั่งอาหาร → เขียนต่อท้าย "สมุดออเดอร์" /data/orders.txt ซึ่งอยู่บน PVC
// Pod ถูกลบ / restart / เปลี่ยนรุ่น สมุดก็ยังอยู่ เพราะไฟล์ไม่ได้อยู่ใน container
const http = require("node:http");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const PORT = Number(process.env.PORT || 3000);
const SHOP_NAME = process.env.SHOP_NAME || "ร้านอาหารแมวน้องส้ม";
const ORDERS_FILE = process.env.ORDERS_FILE || "/data/orders.txt";
const POD_NAME = os.hostname();                          // ใน Kubernetes = ชื่อ Pod
const SOM_PNG = fs.readFileSync(path.join(__dirname, "public", "som.png"));

const MENU = {
  tuna: { name: "อาหารเม็ดสูตรปลาทูน่า", price: 459 },
  saba: { name: "อาหารเปียกปลาซาบะ", price: 35 },
  chicken: { name: "ขนมแมวเลียรสไก่", price: 59 },
};

// สมุดออเดอร์ 1 บรรทัด = 1 ออเดอร์ รูปแบบ "เวลา|Pod ที่รับ|ชื่อเมนู"
function readOrders() {
  try {
    return fs.readFileSync(ORDERS_FILE, "utf8").split("\n").filter(Boolean).map((line) => {
      const [time, pod, name] = line.split("|");
      return { time, pod, name };
    });
  } catch {
    return [];                                           // ยังไม่มีสมุด = ยังไม่มีออเดอร์
  }
}

function addOrder(key) {
  const item = MENU[key];
  if (!item) return null;
  const time = new Date().toLocaleTimeString("th-TH", { hour12: false, timeZone: "Asia/Bangkok" });
  fs.appendFileSync(ORDERS_FILE, `${time}|${POD_NAME}|${item.name}\n`);
  return { no: readOrders().length, ...item };
}

function page() {
  const orders = readOrders();
  const buttons = Object.entries(MENU).map(([key, m]) =>
    `<li><span>${m.name} · ${m.price} บาท</span>
       <form method="post" action="/order"><input type="hidden" name="menu" value="${key}"><button>สั่ง</button></form></li>`
  ).join("");
  const last = orders.slice(-5).reverse()
    .map((o) => `<li><span>${o.time} ${o.name}</span><span>รับโดย ${o.pod}</span></li>`).join("");
  return `<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${SHOP_NAME}</title>
<style>
  body { margin: 0; font-family: system-ui, "Noto Sans Thai", sans-serif; background: #ffedd5; color: #1e293b; }
  main { max-width: 600px; margin: 32px auto; background: #fff; border-radius: 20px; padding: 28px;
         box-shadow: 0 8px 24px rgba(15, 23, 42, .12); }
  header { display: flex; align-items: center; gap: 16px; }
  header img { width: 88px; height: 88px; object-fit: contain; }
  h1 { margin: 0; font-size: 26px; }
  h2 { font-size: 18px; margin: 22px 0 6px; }
  .pod { margin: 18px 0; padding: 12px 16px; border: 2px dashed #ea580c; border-radius: 14px; }
  .pod code { font-size: 18px; font-weight: 700; color: #ea580c; }
  .total { font-size: 20px; font-weight: 700; color: #0f766e; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e2e8f0; font-size: 15px; }
  form { margin: 0; }
  button { background: #ea580c; color: #fff; border: 0; border-radius: 999px; padding: 6px 16px; font-size: 15px; cursor: pointer; }
</style></head>
<body><main>
  <header><img src="/som.png" alt="น้องส้ม"><h1>🐱 ${SHOP_NAME}</h1></header>
  <div class="pod">หน้าร้านนี้เสิร์ฟโดย Pod <code>${POD_NAME}</code></div>
  <h2>เมนู</h2>
  <ul>${buttons}</ul>
  <h2>สมุดออเดอร์ (เก็บบน PVC ที่ ${ORDERS_FILE})</h2>
  <p class="total">ออเดอร์ทั้งหมด ${orders.length} รายการ</p>
  <ul>${last || "<li>ยังไม่มีออเดอร์</li>"}</ul>
</main></body></html>`;
}

const server = http.createServer((req, res) => {
  if (req.url === "/api/health") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ status: "ok" }) + "\n");
  }
  if (req.url === "/som.png") {
    res.writeHead(200, { "content-type": "image/png" });
    return res.end(SOM_PNG);
  }
  if (req.url === "/api/orders") {
    res.writeHead(200, { "content-type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ pod: POD_NAME, total: readOrders().length }) + "\n");
  }
  if (req.url === "/order" && req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => { body += chunk; });
    return req.on("end", () => {
      const order = addOrder(new URLSearchParams(body).get("menu"));
      if (!order) {
        res.writeHead(400, { "content-type": "text/plain; charset=utf-8" });
        return res.end("ไม่มีเมนูนี้\n");
      }
      console.log(`${POD_NAME} รับออเดอร์ #${order.no} ${order.name}`);
      if ((req.headers.accept || "").includes("text/html")) {   // กดปุ่มจาก browser → กลับหน้าร้าน
        res.writeHead(303, { location: "/" });
        return res.end();
      }
      res.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
      return res.end(`รับออเดอร์ #${order.no} ${order.name} โดย ${POD_NAME}\n`);
    });
  }
  if (req.url === "/" || req.url.startsWith("/?")) {
    // connection: close = refresh แต่ละครั้งเป็นการเชื่อมต่อใหม่ ที่ Service ส่งไปสาขาไหนก็ได้ (บทที่ 5)
    res.writeHead(200, { "content-type": "text/html; charset=utf-8", connection: "close" });
    return res.end(page());
  }
  res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
  res.end("ไม่พบหน้านี้\n");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`${SHOP_NAME} เปิดสาขา ${POD_NAME} ที่ port ${PORT} สมุดออเดอร์มีอยู่แล้ว ${readOrders().length} รายการ`);
});

// Pod ถูกลบ/ถูกเปลี่ยน → รอ 5 วินาทีให้ Service ถอดสาขานี้ออกก่อน แล้วค่อยปิดร้าน (บทที่ 5)
process.on("SIGTERM", () => {
  console.log(`ปิดสาขา ${POD_NAME}`);
  setTimeout(() => {
    server.close(() => process.exit(0));
    setTimeout(() => process.exit(0), 2000).unref();
  }, 5000);
});
