"use server";

/**
 * Server actions ทั้งหมดของหน้าเว็บ
 *
 * ทุกฟอร์มในโปรเจกต์นี้ยิงมาที่ไฟล์นี้ ไม่มี fetch ฝั่ง browser เลยแม้แต่ที่เดียว
 * ผลลัพธ์ถูกส่งกลับหน้าเดิมเป็น query string (?t=ok|err&m=ข้อความ)
 * แทนที่จะใช้ useState — เพราะทุกหน้าต้องเป็น server component ล้วน
 */

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { apiSend, type ApiResult } from "./lib/api";

/** อ่านค่าจากฟอร์มเป็นข้อความที่ตัดช่องว่างหัวท้ายแล้ว */
function str(form: FormData, key: string): string {
  return String(form.get(key) ?? "").trim();
}

function num(form: FormData, key: string): number {
  return Number(form.get(key) ?? 0);
}

/** ปลายทางที่จะพากลับไป — ฟอร์มแนบมาเองเพื่อรักษาตัวกรองที่ผู้ใช้ตั้งไว้ */
function backTo(form: FormData, fallback: string): string {
  const back = str(form, "back");
  // รับเฉพาะ path ภายในเว็บนี้ กัน open-redirect ไปโดเมนอื่น
  return back.startsWith("/") && !back.startsWith("//") ? back : fallback;
}

/**
 * จบงาน 1 action : ล้างแคชของหน้า แล้วเด้งกลับพร้อมข้อความ
 * redirect() ทำงานด้วยการ throw — ต้องเรียกนอก try/catch เสมอ ไม่งั้นจะถูกกลืน
 */
function finish(path: string, result: ApiResult, okMessage: string): never {
  const tone = result.ok ? "ok" : "err";
  const message = result.ok ? okMessage : result.message;
  const sep = path.includes("?") ? "&" : "?";
  redirect(`${path}${sep}t=${tone}&m=${encodeURIComponent(message)}`);
}

// ---------------------------------------------------------------
// ใบแจ้งซ่อม
// ---------------------------------------------------------------

/** REQ-01 : แจ้งซ่อมใหม่ → API สร้างเป็นสถานะ NEW ให้เสมอ */
export async function createTicketAction(form: FormData) {
  const path = backTo(form, "/tickets");
  const result = await apiSend("/api/tickets", "POST", {
    asset_id: num(form, "asset_id"),
    title: str(form, "title"),
    detail: str(form, "detail"),
    priority: str(form, "priority") || "NORMAL",
  });
  revalidatePath("/tickets");
  revalidatePath("/");
  finish(path, result, `แจ้งซ่อมเรียบร้อย — ใบใหม่อยู่ในคอลัมน์ "รอรับเรื่อง"`);
}

/** REQ-03 : มอบหมายงาน ต้องมีชื่อช่างเสมอ (ถ้าเว้นว่าง API จะตอบ 400 ASSIGNEE_REQUIRED) */
export async function assignTicketAction(form: FormData) {
  const path = backTo(form, "/tickets");
  const id = num(form, "id");
  const result = await apiSend(`/api/tickets/${id}/status`, "PATCH", {
    status: "ASSIGNED",
    assignee: str(form, "assignee"),
  });
  revalidatePath("/tickets");
  revalidatePath("/");
  finish(path, result, `มอบหมายใบ #${id} ให้ ${str(form, "assignee")} แล้ว`);
}

/** REQ-02 : เลื่อนสถานะทีละขั้น ข้ามขั้นไม่ได้ (API ตอบ 409 INVALID_TRANSITION) */
export async function advanceTicketAction(form: FormData) {
  const path = backTo(form, "/tickets");
  const id = num(form, "id");
  const status = str(form, "status");
  const result = await apiSend(`/api/tickets/${id}/status`, "PATCH", { status });
  revalidatePath("/tickets");
  revalidatePath("/");
  finish(path, result, `ใบ #${id} เปลี่ยนเป็นสถานะ ${status} แล้ว`);
}

/**
 * REQ-05 / REQ-06 : ปิดงานพร้อมตัดอะไหล่
 * ฟอร์มมีช่องอะไหล่ 2 แถว — แถวไหนไม่เลือกอะไหล่หรือใส่จำนวน 0 จะไม่ถูกส่งไป
 * (ปิดงานโดยไม่ใช้อะไหล่เลยก็ได้ ตามข้อกำหนด)
 */
export async function closeTicketAction(form: FormData) {
  const path = backTo(form, "/tickets");
  const id = num(form, "id");

  const parts: { part_id: number; qty: number }[] = [];
  for (const row of ["1", "2"]) {
    const partId = num(form, `part_id_${row}`);
    const qty = num(form, `qty_${row}`);
    if (partId > 0 && qty > 0) parts.push({ part_id: partId, qty });
  }

  const result = await apiSend(`/api/tickets/${id}/close`, "POST", { parts });
  revalidatePath("/tickets");
  revalidatePath("/parts");
  revalidatePath("/");
  const suffix = parts.length ? ` และตัดอะไหล่ ${parts.length} รายการ` : " (ไม่ได้ใช้อะไหล่)";
  finish(path, result, `ปิดใบ #${id} แล้ว${suffix}`);
}

/** ตัวกรอง "งานของช่างคนไหน" (REQ-04) — ทำเป็น action แล้วเด้งไป path พร้อม query */
export async function filterTicketsAction(form: FormData) {
  const assignee = str(form, "assignee");
  redirect(assignee ? `/tickets?assignee=${encodeURIComponent(assignee)}` : "/tickets");
}

// ---------------------------------------------------------------
// ยืม-คืนครุภัณฑ์
// ---------------------------------------------------------------

/** REQ-10 / REQ-11 : ของที่ยังไม่คืน หรือมีใบซ่อมค้าง จะถูก API ปฏิเสธด้วย 409 */
export async function createLoanAction(form: FormData) {
  const result = await apiSend("/api/loans", "POST", {
    asset_id: num(form, "asset_id"),
    borrower: str(form, "borrower"),
  });
  revalidatePath("/loans");
  revalidatePath("/");
  finish("/loans", result, `บันทึกการยืมให้ ${str(form, "borrower")} แล้ว`);
}

export async function returnLoanAction(form: FormData) {
  const id = num(form, "id");
  const result = await apiSend(`/api/loans/${id}/return`, "POST");
  revalidatePath("/loans");
  revalidatePath("/");
  finish("/loans", result, `รับคืนสัญญา #${id} เรียบร้อย`);
}

// ---------------------------------------------------------------
// คลังอะไหล่
// ---------------------------------------------------------------

/**
 * REQ-06 / REQ-07 : รับเข้า (direction=in) หรือเบิกออก (direction=out)
 * ฟอร์มให้กรอกจำนวนเป็นบวกเสมอ แล้วมาใส่เครื่องหมายลบตรงนี้
 * เพื่อไม่ให้ผู้ใช้ต้องคิดเรื่องเลขติดลบเอง (และกันพิมพ์ผิดเป็น "-" ซ้อน "-")
 */
export async function movePartAction(form: FormData) {
  const id = num(form, "id");
  const qty = Math.abs(num(form, "qty"));
  const direction = str(form, "direction");
  const delta = direction === "out" ? -qty : qty;
  const reason =
    str(form, "reason") || (direction === "out" ? "เบิกออกจากคลัง" : "รับเข้าคลัง");

  const result = await apiSend(`/api/parts/${id}/move`, "POST", { delta, reason });
  revalidatePath("/parts");
  revalidatePath("/");
  finish(
    "/parts",
    result,
    direction === "out" ? `เบิกออก ${qty} หน่วยแล้ว` : `รับเข้า ${qty} หน่วยแล้ว`,
  );
}
