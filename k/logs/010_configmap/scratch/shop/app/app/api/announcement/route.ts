import { readAnnouncement, shopInfo } from '@/lib/shop';

export const dynamic = 'force-dynamic';

// 1.4: GET /api/announcement → "som-web-xxxx 1.4 <ข้อความในไฟล์ประกาศ>" (ไม่มีไฟล์ = "(ไม่มีประกาศ)")
// ใช้ curl ดูว่าไฟล์จาก ConfigMap volume เปลี่ยนเองโดยไม่ restart Pod
export async function GET() {
  const { podName, version } = shopInfo();
  const text = readAnnouncement() ?? '(ไม่มีประกาศ)';
  return new Response(`${podName} ${version} ${text}\n`, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
}
