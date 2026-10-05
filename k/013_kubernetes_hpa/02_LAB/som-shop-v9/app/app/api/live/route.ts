export const dynamic = 'force-dynamic';

// livenessProbe: ตอบได้ = process ยังไม่ค้าง (ไม่แตะ db — db ล่มไม่ควรทำให้ web ถูก restart)
export async function GET() {
  return Response.json({ ok: true });
}
