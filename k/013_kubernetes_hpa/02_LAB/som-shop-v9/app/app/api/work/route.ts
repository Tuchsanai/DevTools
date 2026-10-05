import os from 'node:os';

export const dynamic = 'force-dynamic';

// 1.7: GET /api/work?ms=20 → "som-web-xxxxx 1.7 work=20ms"
// จำลอง "งานหนักของวันลดราคา" (เช่น คิดส่วนลด) = หมุน CPU ms มิลลิวินาทีต่อ 1 request ไม่แตะฐานข้อมูล
// ใช้สร้างโหลด CPU ให้ HPA เห็น (จำกัด 0–200 ms กันพิมพ์ผิดแล้ว Pod ค้าง)
export async function GET(req: Request) {
  const raw = Number(new URL(req.url).searchParams.get('ms') ?? '20');
  const ms = Math.min(Math.max(Number.isFinite(raw) ? Math.round(raw) : 20, 0), 200);
  const start = Date.now();
  let x = 0;
  while (Date.now() - start < ms) x += Math.sqrt(x + 1); // วนคิดเลขเปล่า ๆ = ใช้ CPU จริง
  return new Response(`${os.hostname()} ${process.env.APP_VERSION ?? 'dev'} work=${ms}ms\n`, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}
