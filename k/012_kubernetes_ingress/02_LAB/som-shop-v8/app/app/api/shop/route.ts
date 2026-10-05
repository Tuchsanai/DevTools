import { shopInfo } from '@/lib/shop';

export const dynamic = 'force-dynamic';

// 1.5: GET /api/shop → ค่าตั้งค่าร้านที่ Pod นี้ "เห็น" จาก env (ดูง่ายกว่า grep หน้าเว็บ)
export async function GET() {
  const { podName, version, theme, shopName, promo } = shopInfo();
  return Response.json({
    pod: podName,
    version,
    shopName,
    theme,
    promo,
    eyebrow: process.env.SHOP_EYEBROW ?? null,
    footer: process.env.SHOP_FOOTER ?? null,
  });
}
