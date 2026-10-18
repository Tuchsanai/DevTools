// ร้านอาหารแมวน้องส้ม (ConfigMap + Secret) — เว็บหน้าร้านเล็ก ๆ ด้วย Node.js ล้วน ไม่มี dependency
// ค่าทุกอย่างมาจากนอก image:
//   - SHOP_NAME, ANNOUNCEMENT  → env จาก ConfigMap (อ่านครั้งเดียวตอนเริ่ม เปลี่ยนแล้วต้อง restart Pod)
//   - เมนู                     → ไฟล์ /etc/som-menu/menu.txt จาก ConfigMap (อ่านใหม่ทุกครั้งที่มีลูกค้า)
//   - ADMIN_PASSWORD           → env จาก Secret (ใช้เข้าหน้า /admin)
const http = require("node:http");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const PORT = Number(process.env.PORT || 3000);
const SHOP_NAME = process.env.SHOP_NAME || "ร้านอาหารแมวน้องส้ม";
const ANNOUNCEMENT = process.env.ANNOUNCEMENT || "";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "";
const MENU_FILE = process.env.MENU_FILE || "/etc/som-menu/menu.txt";
const POD_NAME = os.hostname();                          // ใน Kubernetes = ชื่อ Pod
const SOM_PNG = fs.readFileSync(path.join(__dirname, "public", "som.png"));

// เมนูสำรอง ใช้เมื่อไม่มีไฟล์เมนู (เช่น ยังไม่ได้ mount ConfigMap)
const DEFAULT_MENU = [{ name: "อาหารเม็ดสูตรปลาทูน่า", price: 459 }];

// ไฟล์เมนู 1 บรรทัด = 1 รายการ รูปแบบ "ชื่อ|ราคา"
function readMenu() {
  try {
    const items = fs.readFileSync(MENU_FILE, "utf8").split("\n")
      .map((line) => line.trim()).filter(Boolean)
      .map((line) => { const [name, price] = line.split("|"); return { name, price: Number(price) }; });
    return { items, from: `ConfigMap (${MENU_FILE})` };
  } catch {
    return { items: DEFAULT_MENU, from: "เมนูสำรองในโค้ด (ไม่พบไฟล์เมนู)" };
  }
}

let served = 0;

function page() {
  const menu = readMenu();
  const items = menu.items.map((m) => `<li><span>${m.name}</span><span>${m.price} บาท</span></li>`).join("");
  const notice = ANNOUNCEMENT ? `<div class="notice">📢 ${ANNOUNCEMENT}</div>` : "";
  return `<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${SHOP_NAME}</title>
<style>
  body { margin: 0; font-family: system-ui, "Noto Sans Thai", sans-serif; background: #ffedd5; color: #1e293b; }
  main { max-width: 560px; margin: 32px auto; background: #fff; border-radius: 20px; padding: 28px;
         box-shadow: 0 8px 24px rgba(15, 23, 42, .12); }
  header { display: flex; align-items: center; gap: 16px; }
  header img { width: 88px; height: 88px; object-fit: contain; }
  h1 { margin: 0; font-size: 26px; }
  .notice { margin: 18px 0 0; padding: 12px 16px; border-radius: 14px; background: #fef3c7; font-weight: 600; }
  .pod { margin: 18px 0; padding: 12px 16px; border: 2px dashed #ea580c; border-radius: 14px; }
  .pod code { font-size: 18px; font-weight: 700; color: #ea580c; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }
  footer { margin-top: 16px; color: #64748b; font-size: 14px; }
</style></head>
<body><main>
  <header>
    <img src="/som.png" alt="น้องส้ม">
    <h1>🐱 ${SHOP_NAME}</h1>
  </header>
  ${notice}
  <div class="pod">หน้าร้านนี้เสิร์ฟโดย Pod <code>${POD_NAME}</code></div>
  <ul>${items}</ul>
  <footer>เมนูมาจาก: ${menu.from}</footer>
</main></body></html>`;
}

// หน้าหลังร้าน: ต้องใส่ชื่อผู้ใช้ som + รหัสผ่านจาก Secret (HTTP Basic Auth)
function isAdmin(req) {
  const auth = req.headers.authorization || "";
  const [user, pass] = Buffer.from(auth.replace("Basic ", ""), "base64").toString().split(":");
  return ADMIN_PASSWORD !== "" && user === "som" && pass === ADMIN_PASSWORD;
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
  if (req.url === "/admin") {
    if (!isAdmin(req)) {
      res.writeHead(401, { "content-type": "text/plain; charset=utf-8", "www-authenticate": 'Basic realm="som-menu"' });
      return res.end("หลังร้าน: รหัสผ่านไม่ถูกต้อง\n");
    }
    res.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
    return res.end(`หลังร้าน ${POD_NAME}: เสิร์ฟไปแล้ว ${served} ครั้ง\n`);
  }
  if (req.url === "/" || req.url.startsWith("/?")) {
    served += 1;
    console.log(`${POD_NAME} เสิร์ฟหน้าร้านครั้งที่ ${served}`);
    // connection: close = refresh แต่ละครั้งเป็นการเชื่อมต่อใหม่ ที่ Service ส่งไปสาขาไหนก็ได้ (บทที่ 5)
    res.writeHead(200, { "content-type": "text/html; charset=utf-8", connection: "close" });
    return res.end(page());
  }
  res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
  res.end("ไม่พบหน้านี้\n");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`${SHOP_NAME} เปิดสาขา ${POD_NAME} ที่ port ${PORT} ประกาศ: "${ANNOUNCEMENT}" ตั้งรหัสหลังร้าน: ${ADMIN_PASSWORD ? "แล้ว" : "ยังไม่ตั้ง"}`);
});

// Pod ถูกลบ/ถูกเปลี่ยน → รอ 5 วินาทีให้ Service ถอดสาขานี้ออกก่อน แล้วค่อยปิดร้าน (บทที่ 5)
process.on("SIGTERM", () => {
  console.log(`ปิดสาขา ${POD_NAME}`);
  setTimeout(() => {
    server.close(() => process.exit(0));
    setTimeout(() => process.exit(0), 2000).unref();
  }, 5000);
});
