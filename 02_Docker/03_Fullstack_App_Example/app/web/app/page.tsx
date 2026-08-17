import Link from "next/link";
import { apiGet, type Asset, type Dashboard, type TicketStatus } from "./lib/api";
import {
  Chip,
  Flash,
  Panel,
  PanelHead,
  PRIORITY_LABEL,
  PRIORITY_STYLE,
  STATUS_ACCENT,
  STATUS_LABEL,
  StockBar,
} from "./ui/kit";

// ห้ามให้ Next แคชหน้านี้ตอน build — ตัวเลขต้องมาจากฐานข้อมูลจริง ณ เวลาที่เปิดดู
export const dynamic = "force-dynamic";

const ORDER: TicketStatus[] = ["NEW", "ASSIGNED", "IN_PROGRESS", "DONE"];

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ t?: string; m?: string }>;
}) {
  const sp = await searchParams;
  // ยิงสองเส้นพร้อมกัน ไม่ต้องรอทีละอัน
  const [dash, assets] = await Promise.all([
    apiGet<Dashboard>("/api/dashboard"),
    apiGet<Asset[]>("/api/assets"),
  ]);

  const openTickets = dash.tickets.NEW + dash.tickets.ASSIGNED + dash.tickets.IN_PROGRESS;
  const available = assets.filter((a) => a.status === "AVAILABLE").length;

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <section className="animate-rise mb-8">
        <p className="text-xs font-medium tracking-[0.2em] text-brand-400 uppercase">Dashboard</p>
        <h1 className="mt-1.5 text-3xl font-bold tracking-tight text-slate-50 sm:text-4xl">
          หน้าจอเดียวที่บอกว่า{" "}
          <span className="bg-gradient-to-r from-brand-400 to-violet-400 bg-clip-text text-transparent">
            งานอะไรอยู่ในมือใคร
          </span>
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          ตอนนี้มีงานค้างอยู่ {openTickets} ใบ · ค้างเกินกำหนด {dash.overdue.length} ใบ ·
          ครุภัณฑ์ถูกยืมอยู่ {dash.loans_active} ชิ้น · อะไหล่ต่ำกว่าจุดสั่งซื้อ {dash.parts_low.length} รายการ
        </p>
      </section>

      {/* ---------- การ์ดตัวเลขใหญ่ (REQ-08) ---------- */}
      <section className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-5">
        {ORDER.map((status) => (
          <Panel key={status} className="animate-rise relative overflow-hidden p-5">
            <span className={`absolute inset-x-0 top-0 h-1 ${STATUS_ACCENT[status]}`} />
            <p className="text-xs font-medium text-slate-400">{STATUS_LABEL[status]}</p>
            <p className="mt-2 text-5xl font-bold tracking-tight tabular-nums text-slate-50">
              {dash.tickets[status]}
            </p>
            <p className="mt-1 text-[11px] text-slate-500">ใบแจ้งซ่อม</p>
          </Panel>
        ))}

        <Panel className="animate-rise relative overflow-hidden p-5">
          <span className="absolute inset-x-0 top-0 h-1 bg-violet-400" />
          <p className="text-xs font-medium text-slate-400">ครุภัณฑ์ถูกยืมอยู่</p>
          <p className="mt-2 text-5xl font-bold tracking-tight tabular-nums text-slate-50">
            {dash.loans_active}
          </p>
          <p className="mt-1 text-[11px] text-slate-500">
            พร้อมให้ยืมอีก {available} จาก {assets.length} ชิ้น
          </p>
        </Panel>
      </section>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* ---------- งานค้างเกินกำหนด (REQ-09) ---------- */}
        <Panel className="animate-rise">
          <PanelHead
            title="งานค้างเกินกำหนด"
            hint="เกินเวลามาตรฐานตามความเร่งด่วน · เร่งด่วน 1 วัน · ปกติ 3 วัน · ไม่เร่ง 7 วัน"
            right={
              <Chip className="border-rose-400/40 bg-rose-500/15 text-rose-200">
                {dash.overdue.length} ใบ
              </Chip>
            }
          />
          <ul className="divide-y divide-white/6">
            {dash.overdue.length === 0 ? (
              <li className="px-5 py-8 text-center text-sm text-slate-500">
                ไม่มีงานค้างเกินกำหนด 🎉
              </li>
            ) : (
              dash.overdue.map((item) => (
                <li key={item.id} className="flex items-center gap-4 px-5 py-3.5">
                  <span className={`h-9 w-1 shrink-0 rounded-full ${PRIORITY_STYLE[item.priority].bar}`} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-slate-100">
                      #{item.id} {item.title}
                    </p>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {item.assignee ? `ผู้รับผิดชอบ ${item.assignee}` : "ยังไม่มีผู้รับผิดชอบ"}
                    </p>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="text-sm font-semibold text-rose-300 tabular-nums">
                      ค้าง {item.days_open} วัน
                    </p>
                    <p className="text-[11px] text-slate-500">
                      กำหนด {item.sla_days} วัน · {PRIORITY_LABEL[item.priority]}
                    </p>
                  </div>
                </li>
              ))
            )}
          </ul>
          <div className="border-t border-white/8 px-5 py-3">
            <Link href="/tickets" className="text-xs font-medium text-brand-400 hover:text-brand-500">
              ไปที่กระดานงานซ่อม →
            </Link>
          </div>
        </Panel>

        {/* ---------- อะไหล่ใกล้หมด (REQ-12) ---------- */}
        <Panel className="animate-rise">
          <PanelHead
            title="อะไหล่ต่ำกว่าจุดสั่งซื้อ"
            hint="ยอดคงเหลือน้อยกว่าจุดสั่งซื้อที่ตั้งไว้ ควรสั่งเพิ่ม"
            right={
              <Chip className="border-amber-300/40 bg-amber-400/15 text-amber-100">
                {dash.parts_low.length} รายการ
              </Chip>
            }
          />
          <ul className="divide-y divide-white/6">
            {dash.parts_low.length === 0 ? (
              <li className="px-5 py-8 text-center text-sm text-slate-500">อะไหล่เพียงพอทุกรายการ</li>
            ) : (
              dash.parts_low.map((part) => (
                <li key={part.id} className="px-5 py-3.5">
                  <div className="flex items-baseline justify-between gap-3">
                    <p className="truncate text-sm font-medium text-slate-100">{part.name}</p>
                    <p className="shrink-0 text-sm tabular-nums text-slate-300">
                      <span className="font-semibold text-rose-300">{part.qty_on_hand}</span>
                      <span className="text-slate-500"> / จุดสั่งซื้อ {part.reorder_point}</span>
                    </p>
                  </div>
                  <p className="mb-2 text-[11px] text-slate-500">{part.sku}</p>
                  <StockBar qty={part.qty_on_hand} reorder={part.reorder_point} below={true} />
                </li>
              ))
            )}
          </ul>
          <div className="border-t border-white/8 px-5 py-3">
            <Link href="/parts" className="text-xs font-medium text-brand-400 hover:text-brand-500">
              ไปที่คลังอะไหล่ →
            </Link>
          </div>
        </Panel>
      </div>
    </>
  );
}
