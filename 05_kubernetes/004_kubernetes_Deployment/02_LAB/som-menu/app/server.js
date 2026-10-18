// ร้านอาหารแมวน้องส้ม (Deployment) — เว็บหน้าร้านเล็ก ๆ ด้วย Node.js ล้วน ไม่มี dependency
// แต่ละ Pod คือ "สาขา" หนึ่งสาขา หน้าเว็บบอกว่าใครเสิร์ฟ (ชื่อ Pod) และเป็นเวอร์ชันอะไร
// ใช้ดู rolling update: ระหว่างเปลี่ยนรุ่น จะเห็นทั้งสาขา v1.0 และ v2.0 เปิดพร้อมกัน
const http = require("node:http");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const PORT = Number(process.env.PORT || 3000);
const VERSION = process.env.APP_VERSION || "1.0";       // ฝังมาตอน docker build (--build-arg)
const SHOP_NAME = process.env.SHOP_NAME || "ร้านอาหารแมวน้องส้ม";
const POD_NAME = os.hostname();                          // ใน Kubernetes = ชื่อ Pod
const STARTED_AT = Date.now();
const SOM_PNG = fs.readFileSync(path.join(__dirname, "public", "som.png"));

const MENU = [
  { name: "อาหารเม็ดสูตรปลาทูน่า", price: 459 },
  { name: "อาหารเปียกปลาซาบะ", price: 35 },
  { name: "ขนมแมวเลียรสไก่", price: 59 },
];
if (VERSION.startsWith("2")) {
  MENU.push({ name: "ไอศกรีมแมว รสนมแพะ", price: 49, isNew: true });
}

const THEME = VERSION.startsWith("2")
  ? { main: "#0f766e", soft: "#ccfbf1", label: `เวอร์ชัน ${VERSION} · เมนูใหม่!` }
  : { main: "#ea580c", soft: "#ffedd5", label: `เวอร์ชัน ${VERSION}` };

let served = 0;

function page() {
  const upSec = Math.round((Date.now() - STARTED_AT) / 1000);
  const items = MENU.map(
    (m) => `<li><span>${m.name}${m.isNew ? ' <b class="new">ใหม่</b>' : ""}</span><span>${m.price} บาท</span></li>`
  ).join("");
  return `<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${SHOP_NAME}</title>
<style>
  body { margin: 0; font-family: system-ui, "Noto Sans Thai", sans-serif; background: ${THEME.soft}; color: #1e293b; }
  main { max-width: 560px; margin: 32px auto; background: #fff; border-radius: 20px; padding: 28px;
         box-shadow: 0 8px 24px rgba(15, 23, 42, .12); }
  header { display: flex; align-items: center; gap: 16px; }
  header img { width: 88px; height: 88px; object-fit: contain; }
  h1 { margin: 0; font-size: 26px; }
  .badge { display: inline-block; margin-top: 6px; padding: 4px 12px; border-radius: 999px;
           background: ${THEME.main}; color: #fff; font-weight: 600; }
  .pod { margin: 20px 0; padding: 14px 16px; border: 2px dashed ${THEME.main}; border-radius: 14px; }
  .pod code { font-size: 20px; font-weight: 700; color: ${THEME.main}; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }
  .new { color: #fff; background: #db2777; padding: 1px 8px; border-radius: 999px; font-size: 13px; }
  footer { margin-top: 16px; color: #64748b; font-size: 14px; }
</style></head>
<body><main>
  <header>
    <img src="/som.png" alt="น้องส้ม">
    <div><h1>🐱 ${SHOP_NAME}</h1><span class="badge">${THEME.label}</span></div>
  </header>
  <div class="pod">หน้าร้านนี้เสิร์ฟโดย Pod<br><code>${POD_NAME}</code></div>
  <ul>${items}</ul>
  <footer>สาขานี้เปิดมาแล้ว ${upSec} วินาที · เสิร์ฟไปแล้ว ${served} ครั้ง</footer>
</main></body></html>`;
}

const server = http.createServer((req, res) => {
  if (req.url === "/api/health") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ status: "ok" }));
  }
  if (req.url === "/api/info") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ pod: POD_NAME, version: VERSION }));
  }
  if (req.url === "/som.png") {
    res.writeHead(200, { "content-type": "image/png" });
    return res.end(SOM_PNG);
  }
  if (req.url === "/" || req.url.startsWith("/?")) {
    served += 1;
    console.log(`[v${VERSION}] ${POD_NAME} เสิร์ฟหน้าร้านครั้งที่ ${served}`);
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    return res.end(page());
  }
  res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
  res.end("ไม่พบหน้านี้");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`${SHOP_NAME} v${VERSION} เปิดสาขา ${POD_NAME} ที่ port ${PORT}`);
});

// kubectl delete pod → Kubernetes ส่ง SIGTERM มาก่อน ปิดร้านให้เรียบร้อยแล้วจบทันที
process.on("SIGTERM", () => {
  console.log(`ปิดสาขา ${POD_NAME}`);
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 2000).unref();
});
