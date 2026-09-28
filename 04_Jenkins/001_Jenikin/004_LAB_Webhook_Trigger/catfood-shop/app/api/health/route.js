import { getBuildInfo } from '../../../data/buildInfo';

export const dynamic = 'force-dynamic';

// GET /api/health — ใช้ใน stage Test/Verify ของ Pipeline
export function GET() {
  return Response.json({ status: 'ok', ...getBuildInfo() });
}
