import os from 'node:os';

export const dynamic = 'force-dynamic';

// GET /api/whoami → "som-web-4nhz6 1.2" (ชื่อ Pod + เวอร์ชัน) ไม่แตะฐานข้อมูล
// ใช้กับ hit.sh เพื่อนับว่าแต่ละ request ไปตก Pod ไหน
export async function GET() {
  return new Response(`${os.hostname()} ${process.env.APP_VERSION ?? 'dev'}\n`, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}
