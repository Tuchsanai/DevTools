"use server";

import { redirect } from "next/navigation";
import { apiSend } from "./lib/api";

// รับฟอร์มเมนูหนึ่งใบ แล้วเรียก API ผ่าน gateway ภายใน
export async function createOrderAction(form: FormData) {
  const result = await apiSend("/api/orders", {
    menu_code: String(form.get("menu_code") ?? ""),
    qty: Number(form.get("qty") ?? 1),
    customer_name: String(form.get("customer_name") ?? "").trim(),
  });
  if (result.ok && result.data) redirect(`/orders?id=${result.data.id}&created=1`);
  redirect(`/?error=${encodeURIComponent(result.message)}`);
}
