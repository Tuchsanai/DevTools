import type { Order, OrderStatus } from "./lib/api";

export const MENU_META: Record<string,{emoji:string; note:string; tone:string}> = {
  latte:{emoji:"☕",note:"นุ่มละมุนด้วยนมสด",tone:"from-amber-100 to-orange-50"},
  espresso:{emoji:"⚡",note:"ช็อตเข้ม ปลุกทุกเช้า",tone:"from-stone-200 to-amber-50"},
  americano:{emoji:"🫘",note:"หอมใส ดื่มง่ายทั้งวัน",tone:"from-orange-100 to-yellow-50"},
  mocha:{emoji:"🍫",note:"กาแฟโกโก้แสนกลมกล่อม",tone:"from-rose-100 to-orange-50"},
  matcha:{emoji:"🍵",note:"มัทฉะหอม นมสดเนียน",tone:"from-lime-100 to-emerald-50"},
  cocoa:{emoji:"🥛",note:"โกโก้เข้มข้นแสนสบาย",tone:"from-yellow-100 to-amber-50"},
};

export const STATUS_LABEL: Record<OrderStatus,string> = {QUEUED:"รอชง",BREWING:"กำลังชง",READY:"พร้อมรับ"};
export const STATUS_STYLE: Record<OrderStatus,string> = {
  QUEUED:"border-amber-300 bg-amber-100 text-amber-800",
  BREWING:"border-orange-300 bg-orange-100 text-orange-800 animate-pulse",
  READY:"border-emerald-300 bg-emerald-100 text-emerald-800",
};

export function StatusChip({status}:{status:OrderStatus}) {
  return <span data-status={status} className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${STATUS_STYLE[status]}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{STATUS_LABEL[status]}</span>;
}

export function OrderCard({order}:{order:Order}) {
  return <article className="rounded-2xl border border-coffee-900/10 bg-white p-4 shadow-sm shadow-coffee-900/5">
    <div className="flex items-start justify-between gap-3"><div><p className="text-xs font-bold tracking-widest text-caramel-500">ORDER #{order.id}</p><h3 className="mt-1 text-lg font-black">{MENU_META[order.menu_code]?.emoji} {order.menu_name_th} × {order.qty}</h3></div><StatusChip status={order.status}/></div>
    <div className="mt-3 flex items-center justify-between border-t border-dashed border-coffee-900/10 pt-3 text-sm"><span className="text-coffee-700">คุณ {order.customer_name}</span><strong>฿{order.price_total.toFixed(2)}</strong></div>
  </article>;
}
