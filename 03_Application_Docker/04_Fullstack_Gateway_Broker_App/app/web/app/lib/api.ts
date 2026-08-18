const BASE = process.env.API_BASE_URL ?? "http://traefik";

export type Menu = { code: string; name_th: string; price: number };
export type OrderStatus = "QUEUED" | "BREWING" | "READY";
export type Order = { id: number; menu_code: string; menu_name_th: string; qty: number; customer_name: string; status: OrderStatus; price_total: number; created_at: string; ready_at: string | null };
export type Queue = { items: Order[]; count: number };
export type Sales = { items: {menu_code:string; name_th:string; cups:number; revenue:number}[]; totals:{cups:number; revenue:number}; claim:"trend-level" };
export type ApiResult = { ok: boolean; status: number; message: string; data?: Order };

// ทุก GET เกิดฝั่ง Next.js server และผ่าน Traefik เสมอ
export async function apiGet<T>(path: string, authorization?: string): Promise<T> {
  const headers: Record<string,string> = {};
  if (authorization) headers.Authorization = authorization;
  const response = await fetch(`${BASE}${path}`, { cache: "no-store", headers });
  if (!response.ok) throw new Error(`GET ${path} ล้มเหลว (HTTP ${response.status})`);
  return await response.json() as T;
}

// server action ใช้ helper เดียว ไม่มี fetch ใน browser
export async function apiSend(path: string, body: unknown): Promise<ApiResult> {
  try {
    const response = await fetch(`${BASE}${path}`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body), cache: "no-store" });
    const data = await response.json().catch(() => ({})) as {detail?:string} & Partial<Order>;
    if (response.ok) return {ok:true, status:response.status, message:"", data:data as Order};
    return {ok:false, status:response.status, message:data.detail ?? `HTTP ${response.status}`};
  } catch (error) {
    return {ok:false, status:0, message:`ติดต่อบริการไม่ได้: ${String(error)}`};
  }
}
