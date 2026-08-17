/**
 * ตัวห่อการเรียก API — ใช้ได้เฉพาะฝั่ง server เท่านั้น
 *
 * ทำไมห้ามเรียกจาก browser : ชื่อโฮสต์ "api" มีความหมายอยู่แค่ภายใน Docker network
 * เครื่องของผู้ใช้ที่เปิดหน้าเว็บอยู่นอก network นั้น resolve ชื่อนี้ไม่ได้แน่นอน
 * (และเราจงใจไม่ publish พอร์ตของ api ตามข้อกำหนด NFR-3 ของฐานข้อมูล/สถาปัตยกรรม)
 * → ทุกหน้าเป็น server component และทุกฟอร์มเป็น server action
 */

const BASE = process.env.API_BASE_URL ?? "http://api:8000";

// ---------- รูปข้อมูลตามที่ api/main.py คืนมาจริง ----------
export type Priority = "LOW" | "NORMAL" | "HIGH";
export type TicketStatus = "NEW" | "ASSIGNED" | "IN_PROGRESS" | "DONE";

export type Asset = {
  id: number;
  code: string;
  name: string;
  location: string;
  created_at: string;
  status: "AVAILABLE" | "ON_LOAN" | "IN_REPAIR";
};

export type Ticket = {
  id: number;
  asset_id: number;
  title: string;
  detail: string;
  priority: Priority;
  status: TicketStatus;
  assignee: string | null;
  created_at: string;
  closed_at: string | null;
};

export type Loan = {
  id: number;
  asset_id: number;
  asset_code: string;
  asset_name: string;
  borrower: string;
  borrowed_at: string;
  returned_at: string | null;
};

export type Part = {
  id: number;
  sku: string;
  name: string;
  qty_on_hand: number;
  reorder_point: number;
  below_reorder: boolean;
};

export type StockMove = {
  id: number;
  part_id: number;
  ticket_id: number | null;
  delta: number;
  reason: string;
  created_at: string;
};

export type Dashboard = {
  tickets: Record<TicketStatus, number>;
  overdue: {
    id: number;
    title: string;
    priority: Priority;
    assignee: string | null;
    days_open: number;
    sla_days: number;
  }[];
  loans_active: number;
  parts_low: {
    id: number;
    sku: string;
    name: string;
    qty_on_hand: number;
    reorder_point: number;
  }[];
};

/** GET แล้วคืน JSON — cache:"no-store" เพราะหน้าจอต้องเห็นค่าล่าสุดเสมอหลังกดปุ่ม */
export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`GET ${path} ล้มเหลว (HTTP ${res.status})`);
  }
  return (await res.json()) as T;
}

export type ApiResult = { ok: boolean; status: number; message: string };

/**
 * ส่ง POST/PATCH แล้วแปลง error ของ API ให้เป็นข้อความไทยพร้อมแสดง
 * API คืน error รูปเดียวกันหมด {"detail": "...", "code": "..."} (contract §4)
 * จึงหยิบ detail มาโชว์ได้ตรง ๆ ไม่ต้อง map รหัสเป็นข้อความเองอีกชั้น
 */
export async function apiSend(
  path: string,
  method: "POST" | "PATCH",
  body?: unknown,
): Promise<ApiResult> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body ?? {}),
      cache: "no-store",
    });
  } catch (err) {
    return { ok: false, status: 0, message: `ติดต่อบริการเบื้องหลังไม่ได้: ${String(err)}` };
  }

  if (res.ok) {
    return { ok: true, status: res.status, message: "" };
  }

  let message = `เกิดข้อผิดพลาด (HTTP ${res.status})`;
  try {
    const data = (await res.json()) as { detail?: string; code?: string };
    if (data?.detail) {
      message = data.code ? `${data.detail} [${data.code}]` : data.detail;
    }
  } catch {
    // ถ้า body ไม่ใช่ JSON ก็ใช้ข้อความตั้งต้นไป
  }
  return { ok: false, status: res.status, message };
}
