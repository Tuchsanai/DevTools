import { apiGet, type Order, type OrderStatus, type Queue } from "../lib/api";
import { OrderCard, STATUS_LABEL } from "../ui";

export const dynamic = "force-dynamic";
const STEPS:OrderStatus[]=["QUEUED","BREWING","READY"];

export default async function Orders({searchParams}:{searchParams:Promise<{id?:string;created?:string}>}) {
  const params=await searchParams; const queue=await apiGet<Queue>("/api/queue");
  let tracked:Order|null=null; if(params.id && /^\d+$/.test(params.id)){try{tracked=await apiGet<Order>(`/api/orders/${params.id}`)}catch{tracked=null}}
  const current=tracked?STEPS.indexOf(tracked.status):-1;
  return <><meta httpEquiv="refresh" content="3"/>
    <section className="mb-7 flex flex-wrap items-end justify-between gap-4"><div><p className="text-xs font-bold tracking-[.2em] text-caramel-500">LIVE ORDER BOARD</p><h1 className="text-4xl font-black">คิวเครื่องดื่มของคุณ</h1><p className="mt-2 text-coffee-700">อัปเดตอัตโนมัติทุก 3 วินาที · ตอนนี้มี {queue.count} ออเดอร์กำลังชง</p></div><div className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-xs font-bold shadow-sm"><span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500"/> LIVE</div></section>
    {params.created && tracked && <div className="mb-5 rounded-2xl border border-emerald-300 bg-emerald-50 px-5 py-4 font-bold text-emerald-800">รับออเดอร์ #{tracked.id} แล้ว! เราจะเริ่มชงให้ทันที</div>}
    {tracked && <section data-tracked-order={tracked.id} className="mb-7 rounded-[1.7rem] border border-caramel-400/40 bg-gradient-to-r from-orange-50 to-cream-100 p-6 shadow-lg shadow-caramel-400/10"><div className="mb-5 flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-bold tracking-wider text-caramel-500">กำลังติดตามออเดอร์ของคุณ</p><h2 className="text-2xl font-black">#{tracked.id} · {tracked.menu_name_th} × {tracked.qty}</h2></div><strong className="text-lg">คุณ {tracked.customer_name}</strong></div><div className="grid grid-cols-3 gap-2">{STEPS.map((step,index)=><div key={step} className={`rounded-xl px-3 py-3 text-center text-sm font-bold ${index<=current?"bg-coffee-900 text-white":"bg-white/70 text-coffee-700"}`}><span className="block text-lg">{index<current?"✓":index===current?"●":"○"}</span>{STATUS_LABEL[step]}</div>)}</div></section>}
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{queue.items.length?queue.items.map(order=><OrderCard key={order.id} order={order}/>):<div className="col-span-full rounded-[2rem] border border-dashed border-coffee-900/20 bg-white/60 py-20 text-center"><div className="text-5xl">✨</div><h2 className="mt-3 text-xl font-black">คิวโล่ง พร้อมชงแก้วถัดไป</h2></div>}</section>
  </>;
}
