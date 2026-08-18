import { createOrderAction } from "./actions";
import { apiGet, type Menu } from "./lib/api";
import { MENU_META } from "./ui";

export const dynamic = "force-dynamic";

export default async function Home({searchParams}:{searchParams:Promise<{error?:string}>}) {
  const [menu, version, params] = await Promise.all([apiGet<{items:Menu[]}>("/api/menu"), apiGet<{version:string;tagline:string}>("/api/version"), searchParams]);
  return <>
    <section className="relative mb-9 overflow-hidden rounded-[2rem] bg-coffee-950 px-7 py-9 text-cream-50 shadow-2xl shadow-coffee-900/20 sm:px-11">
      <div className="absolute -right-12 -top-20 h-72 w-72 rounded-full bg-caramel-400/20 blur-3xl"/><div className="relative grid items-center gap-7 md:grid-cols-[1fr_auto]">
        <div><p className="mb-3 text-xs font-bold tracking-[.24em] text-caramel-400">WELCOME TO YOUR DAILY RITUAL · V{version.version}</p><h1 className="max-w-3xl text-4xl font-black leading-tight tracking-tight sm:text-6xl">วันนี้ ให้เราชง<br/><span className="text-caramel-400">แก้วที่ใช่</span> ให้คุณ</h1><p className="mt-4 max-w-xl text-base text-cream-200">{version.tagline} — เลือกเมนู สั่งล่วงหน้า แล้วแวะมารับแบบไม่ต้องยืนรอหน้าเคาน์เตอร์</p></div>
        <div className="hidden h-44 w-44 place-items-center rounded-full border border-cream-100/15 bg-cream-100/5 md:grid"><span className="steam text-8xl">☕</span></div>
      </div>
    </section>
    {params.error && <div role="alert" className="mb-6 rounded-2xl border border-rose-300 bg-rose-50 px-5 py-4 font-semibold text-rose-800">สั่งไม่สำเร็จ: {params.error}</div>}
    <div className="mb-5 flex items-end justify-between"><div><p className="text-xs font-bold tracking-[.2em] text-caramel-500">OUR MENU</p><h2 className="text-3xl font-black">เลือกความสุขของคุณ</h2></div><p className="hidden text-sm text-coffee-700 sm:block">ทุกแก้วชงสดตามลำดับคิว</p></div>
    <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{menu.items.map(item=>{const meta=MENU_META[item.code]; return <article key={item.code} className="animate-float-in group overflow-hidden rounded-[1.6rem] border border-coffee-900/10 bg-white shadow-lg shadow-coffee-900/5 transition hover:-translate-y-1 hover:shadow-xl">
      <div className={`relative grid h-36 place-items-center bg-gradient-to-br ${meta.tone}`}><svg viewBox="0 0 180 100" className="absolute h-full w-full opacity-30" aria-hidden="true"><path d="M15 80 Q50 10 90 65 T170 35" fill="none" stroke="currentColor" strokeWidth="2"/><circle cx="35" cy="25" r="12" fill="none" stroke="currentColor"/></svg><span className="relative text-7xl drop-shadow-md transition group-hover:scale-110">{meta.emoji}</span><span className="absolute right-4 top-4 rounded-full bg-white/80 px-3 py-1 text-sm font-black">฿{item.price.toFixed(2)}</span></div>
      <div className="p-5"><h3 className="text-xl font-black">{item.name_th}</h3><p className="mb-4 text-sm text-coffee-700">{meta.note}</p><form action={createOrderAction} className="grid grid-cols-[1fr_5.2rem] gap-2"><input type="hidden" name="menu_code" value={item.code}/><label className="col-span-2 text-xs font-bold text-coffee-700">ชื่อผู้รับ</label><input data-menu-name={item.code} required maxLength={80} name="customer_name" placeholder="เช่น มะลิ" className="col-span-2 rounded-xl border border-coffee-900/15 bg-cream-50 px-3 py-2.5 outline-none ring-caramel-400 focus:ring-2"/><select name="qty" aria-label="จำนวนแก้ว" className="rounded-xl border border-coffee-900/15 bg-cream-50 px-3 font-bold"><option value="1">1 แก้ว</option><option value="2">2 แก้ว</option><option value="3">3 แก้ว</option></select><button data-order-menu={item.code} className="rounded-xl bg-coffee-900 px-3 py-2.5 text-sm font-bold text-white transition hover:bg-caramel-500">สั่งเลย →</button></form></div>
    </article>})}</section>
  </>;
}
