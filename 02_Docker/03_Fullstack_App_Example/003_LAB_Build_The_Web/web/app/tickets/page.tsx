import Link from "next/link";
import {
  advanceTicketAction,
  assignTicketAction,
  closeTicketAction,
  createTicketAction,
  filterTicketsAction,
} from "../actions";
import {
  apiGet,
  type Asset,
  type Dashboard,
  type Part,
  type Ticket,
  type TicketStatus,
} from "../lib/api";
import {
  buttonClass,
  Chip,
  Flash,
  ghostButtonClass,
  inputClass,
  labelClass,
  Panel,
  PanelHead,
  PRIORITY_LABEL,
  PRIORITY_STYLE,
  STATUS_ACCENT,
  STATUS_LABEL,
  thaiDate,
} from "../ui/kit";

export const dynamic = "force-dynamic";

const COLUMNS: TicketStatus[] = ["NEW", "ASSIGNED", "IN_PROGRESS", "DONE"];

export default async function TicketsPage({
  searchParams,
}: {
  searchParams: Promise<{ t?: string; m?: string; assignee?: string }>;
}) {
  const sp = await searchParams;
  const assignee = (sp.assignee ?? "").trim();

  // ต้อง encodeURIComponent เสมอ : ชื่อช่างเป็นภาษาไทยได้
  // และ uvicorn จะปฏิเสธไบต์ non-ASCII ดิบใน URL ตั้งแต่ชั้นแยกวิเคราะห์ HTTP (ได้ 400 เป็น plain text)
  const ticketsPath = assignee
    ? `/api/tickets?assignee=${encodeURIComponent(assignee)}`
    : "/api/tickets";

  const [tickets, allTickets, assets, parts, dash] = await Promise.all([
    apiGet<Ticket[]>(ticketsPath),
    apiGet<Ticket[]>("/api/tickets"),
    apiGet<Asset[]>("/api/assets"),
    apiGet<Part[]>("/api/parts"),
    apiGet<Dashboard>("/api/dashboard"),
  ]);

  const assetById = new Map(assets.map((a) => [a.id, a]));
  // งานค้างเกินกำหนดถือตามที่ API คำนวณ (REQ-09) ไม่คำนวณซ้ำเองฝั่งหน้าเว็บ
  const overdueById = new Map(dash.overdue.map((o) => [o.id, o]));
  const technicians = [...new Set(allTickets.map((t) => t.assignee).filter(Boolean))] as string[];

  // path ปัจจุบัน — แนบไปกับทุกฟอร์ม เพื่อให้กดปุ่มแล้วยังอยู่ในตัวกรองเดิม
  const back = assignee ? `/tickets?assignee=${encodeURIComponent(assignee)}` : "/tickets";

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <section className="animate-rise mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-brand-400 uppercase">Board</p>
          <h1 className="mt-1.5 text-3xl font-bold tracking-tight text-slate-50">กระดานงานซ่อม</h1>
          <p className="mt-1.5 text-sm text-slate-400">
            ใบแจ้งซ่อมเดินหน้าทีละขั้น รอรับเรื่อง → มอบหมายแล้ว → กำลังซ่อม → ปิดงาน · ข้ามขั้นไม่ได้
          </p>
        </div>

        {/* ---------- ตัวกรองตามช่าง (REQ-04) ---------- */}
        <form action={filterTicketsAction} className="flex flex-wrap items-end gap-2">
          <div>
            <label className={labelClass} htmlFor="filter-assignee">
              กรองตามช่างผู้รับผิดชอบ
            </label>
            <input
              id="filter-assignee"
              name="assignee"
              defaultValue={assignee}
              list="technicians"
              placeholder="เช่น TECH-01"
              className={`${inputClass} sm:w-56`}
            />
            <datalist id="technicians">
              {technicians.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>
          </div>
          <button type="submit" className={buttonClass}>
            กรอง
          </button>
          {assignee ? (
            <Link href="/tickets" className={ghostButtonClass}>
              ล้างตัวกรอง
            </Link>
          ) : null}
        </form>
      </section>

      {assignee ? (
        <p className="mb-5 text-sm text-slate-300">
          กำลังแสดงเฉพาะงานของ{" "}
          <span className="font-semibold text-brand-400">{assignee}</span> — พบ {tickets.length} ใบ
        </p>
      ) : null}

      {/* ---------- ฟอร์มแจ้งซ่อม (REQ-01) ---------- */}
      <Panel className="animate-rise mb-6">
        <PanelHead title="แจ้งซ่อมใหม่" hint="ใบใหม่จะเข้าคอลัมน์ “รอรับเรื่อง” เสมอ" />
        <form action={createTicketAction} className="grid gap-4 px-5 py-5 lg:grid-cols-12">
          <input type="hidden" name="back" value={back} />
          <div className="lg:col-span-3">
            <label className={labelClass} htmlFor="asset_id">
              ครุภัณฑ์
            </label>
            <select id="asset_id" name="asset_id" required className={inputClass}>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.code} · {a.name}
                </option>
              ))}
            </select>
          </div>
          <div className="lg:col-span-3">
            <label className={labelClass} htmlFor="title">
              หัวข้อ
            </label>
            <input
              id="title"
              name="title"
              required
              placeholder="เช่น โปรเจกเตอร์ห้อง 301 ภาพวูบ"
              className={inputClass}
            />
          </div>
          <div className="lg:col-span-4">
            <label className={labelClass} htmlFor="detail">
              รายละเอียดอาการ
            </label>
            <input
              id="detail"
              name="detail"
              placeholder="อาการที่พบ เช่น เปิดแล้วภาพดับเอง"
              className={inputClass}
            />
          </div>
          <div className="lg:col-span-1">
            <label className={labelClass} htmlFor="priority">
              ความเร่งด่วน
            </label>
            <select id="priority" name="priority" defaultValue="NORMAL" className={inputClass}>
              <option value="HIGH">เร่งด่วน</option>
              <option value="NORMAL">ปกติ</option>
              <option value="LOW">ไม่เร่ง</option>
            </select>
          </div>
          <div className="flex items-end lg:col-span-1">
            <button type="submit" className={`${buttonClass} w-full`}>
              แจ้งซ่อม
            </button>
          </div>
        </form>
      </Panel>

      {/* ---------- กระดาน 4 คอลัมน์ ---------- */}
      <div className="grid gap-4 lg:grid-cols-4">
        {COLUMNS.map((status) => {
          const items = tickets.filter((t) => t.status === status);
          return (
            <section key={status} className="animate-rise flex min-w-0 flex-col">
              <header className="mb-3 flex items-center gap-2.5 px-1">
                <span className={`h-2.5 w-2.5 rounded-full ${STATUS_ACCENT[status]}`} />
                <h2 className="text-sm font-semibold text-slate-100">{STATUS_LABEL[status]}</h2>
                <span className="ml-auto rounded-full bg-white/8 px-2 py-0.5 text-xs font-semibold tabular-nums text-slate-300">
                  {items.length}
                </span>
              </header>

              <div className="flex flex-col gap-3 rounded-2xl bg-white/3 p-3 ring-1 ring-white/6">
                {items.length === 0 ? (
                  <p className="rounded-xl border border-dashed border-white/10 px-3 py-8 text-center text-xs text-slate-500">
                    ไม่มีงานในคอลัมน์นี้
                  </p>
                ) : (
                  items.map((ticket) => {
                    const asset = assetById.get(ticket.asset_id);
                    const overdue = overdueById.get(ticket.id);
                    const style = PRIORITY_STYLE[ticket.priority];
                    return (
                      <article
                        key={ticket.id}
                        className="relative overflow-hidden rounded-xl border border-white/8 bg-ink-850 p-3.5 pl-4 transition hover:border-white/18 hover:bg-ink-800"
                      >
                        {/* แถบสีความเร่งด่วนที่ขอบซ้ายของการ์ด */}
                        <span className={`absolute inset-y-0 left-0 w-1 ${style.bar}`} />

                        <div className="mb-1.5 flex flex-wrap items-center gap-1.5">
                          <Chip className={style.chip}>{PRIORITY_LABEL[ticket.priority]}</Chip>
                          {overdue ? (
                            <Chip className="animate-pulse border-rose-400/60 bg-rose-500/25 font-semibold text-rose-100">
                              เกินกำหนด {overdue.days_open}/{overdue.sla_days} วัน
                            </Chip>
                          ) : null}
                          <span className="ml-auto text-[11px] tabular-nums text-slate-500">
                            #{ticket.id}
                          </span>
                        </div>

                        <h3 className="text-sm leading-snug font-semibold text-slate-100">
                          {ticket.title}
                        </h3>
                        {ticket.detail ? (
                          <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-400">
                            {ticket.detail}
                          </p>
                        ) : null}

                        <p className="mt-2 text-[11px] text-slate-500">
                          {asset ? `${asset.code} · ${asset.name}` : `ครุภัณฑ์ #${ticket.asset_id}`}
                          <br />
                          {asset?.location}
                        </p>

                        <div className="mt-2.5 flex items-center justify-between gap-2 border-t border-white/8 pt-2.5 text-[11px] text-slate-400">
                          <span>
                            {ticket.assignee ? (
                              <>
                                ช่าง <span className="font-semibold text-slate-200">{ticket.assignee}</span>
                              </>
                            ) : (
                              "ยังไม่มีผู้รับผิดชอบ"
                            )}
                          </span>
                          <span className="tabular-nums">{thaiDate(ticket.created_at)}</span>
                        </div>

                        {/* ---------- ปุ่มตามสถานะ ---------- */}
                        {ticket.status === "NEW" ? (
                          <form action={assignTicketAction} className="mt-3 flex gap-2">
                            <input type="hidden" name="back" value={back} />
                            <input type="hidden" name="id" value={ticket.id} />
                            <input
                              name="assignee"
                              list="technicians"
                              placeholder="ชื่อช่าง"
                              className={`${inputClass} py-1.5 text-xs`}
                            />
                            <button type="submit" className={`${buttonClass} shrink-0 px-2.5 py-1.5 text-xs`}>
                              มอบหมาย
                            </button>
                          </form>
                        ) : null}

                        {ticket.status === "ASSIGNED" ? (
                          <form action={advanceTicketAction} className="mt-3">
                            <input type="hidden" name="back" value={back} />
                            <input type="hidden" name="id" value={ticket.id} />
                            <input type="hidden" name="status" value="IN_PROGRESS" />
                            <button type="submit" className={`${buttonClass} w-full py-1.5 text-xs`}>
                              เริ่มลงมือซ่อม
                            </button>
                          </form>
                        ) : null}

                        {ticket.status === "IN_PROGRESS" ? (
                          // ใช้ <details> ของ HTML แท้ ๆ ในการพับ/กางฟอร์ม — ไม่ต้องมี JavaScript ฝั่ง client เลย
                          <details className="group mt-3">
                            <summary className={`${buttonClass} w-full cursor-pointer list-none py-1.5 text-xs`}>
                              ปิดงาน + บันทึกอะไหล่
                            </summary>
                            <form action={closeTicketAction} className="mt-2.5 space-y-2 rounded-lg bg-ink-950/60 p-2.5">
                              <input type="hidden" name="back" value={back} />
                              <input type="hidden" name="id" value={ticket.id} />
                              <p className="text-[11px] text-slate-500">
                                เว้นว่างได้ถ้าไม่ได้ใช้อะไหล่ · ถ้าอะไหล่ตัวใดไม่พอ ระบบจะไม่ตัดสต็อกเลยสักตัว
                              </p>
                              {["1", "2"].map((row) => (
                                <div key={row} className="flex gap-2">
                                  <select
                                    name={`part_id_${row}`}
                                    defaultValue=""
                                    className={`${inputClass} py-1.5 text-xs`}
                                  >
                                    <option value="">— ไม่ใช้อะไหล่ —</option>
                                    {parts.map((p) => (
                                      <option key={p.id} value={p.id}>
                                        {p.name} (เหลือ {p.qty_on_hand})
                                      </option>
                                    ))}
                                  </select>
                                  <input
                                    name={`qty_${row}`}
                                    type="number"
                                    min={0}
                                    defaultValue={0}
                                    className={`${inputClass} w-16 shrink-0 py-1.5 text-xs`}
                                  />
                                </div>
                              ))}
                              <button type="submit" className={`${buttonClass} w-full py-1.5 text-xs`}>
                                ยืนยันปิดงาน
                              </button>
                            </form>
                          </details>
                        ) : null}

                        {ticket.status === "DONE" ? (
                          <p className="mt-3 rounded-lg bg-emerald-400/10 px-2.5 py-1.5 text-[11px] text-emerald-200">
                            ปิดงานเมื่อ {thaiDate(ticket.closed_at)}
                          </p>
                        ) : null}
                      </article>
                    );
                  })
                )}
              </div>
            </section>
          );
        })}
      </div>
    </>
  );
}
