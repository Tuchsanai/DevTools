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
import { IconAlert, IconCheck, IconChevron } from "../ui/icons";
import {
  buttonClass,
  Flash,
  ghostButtonClass,
  inputClass,
  labelClass,
  PageHead,
  Panel,
  PanelHead,
  PriorityBadge,
  smallButtonClass,
  STATUS_HINT,
  STATUS_LABEL,
  thaiDate,
} from "../ui/kit";

export const dynamic = "force-dynamic";

const COLUMNS: TicketStatus[] = ["NEW", "ASSIGNED", "IN_PROGRESS", "DONE"];

/** แถบสีบนหัวคอลัมน์ = ordinal ramp ของขั้นงาน (อ่อน→เข้ม) ไม่ใช่สี่สีที่ไม่เกี่ยวกัน */
const STAGE_BAR: Record<TicketStatus, string> = {
  NEW: "bg-stage-1",
  ASSIGNED: "bg-stage-2",
  IN_PROGRESS: "bg-stage-3",
  DONE: "bg-stage-4",
};

export default async function TicketsPage({
  searchParams,
}: {
  searchParams: Promise<{ t?: string; m?: string; assignee?: string }>;
}) {
  const sp = await searchParams;
  const assignee = (sp.assignee ?? "").trim();

  // ต้อง encodeURIComponent เสมอ : ชื่อช่างเป็นภาษาไทยได้
  // และ uvicorn ปฏิเสธไบต์ non-ASCII ดิบใน URL ตั้งแต่ชั้นแยกวิเคราะห์ HTTP
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

      <PageHead
        eyebrow="กระดานงานซ่อม"
        title="งานเดินทีละขั้น ข้ามขั้นไม่ได้"
        right={
          // ---------- REQ-04 : ตัวกรองตามช่างผู้รับผิดชอบ ----------
          <form action={filterTicketsAction} className="flex items-end gap-2">
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
                className={`${inputClass} sm:w-48`}
              />
              <datalist id="technicians">
                {technicians.map((name) => (
                  <option key={name} value={name} />
                ))}
              </datalist>
            </div>
            <button type="submit" className={ghostButtonClass}>
              กรอง
            </button>
            {assignee ? (
              <Link href="/tickets" className={ghostButtonClass}>
                ล้าง
              </Link>
            ) : null}
          </form>
        }
      />

      {assignee ? (
        <p className="mb-4 rounded border border-l-[3px] border-accent-line border-l-accent bg-accent-wash px-4 py-2 text-[14px] text-ink">
          กำลังแสดงเฉพาะงานของ <span className="font-bold">{assignee}</span> — พบ{" "}
          <span className="num font-bold">{tickets.length}</span> ใบ จากทั้งหมด{" "}
          <span className="num font-bold">{allTickets.length}</span> ใบ
        </p>
      ) : null}

      {/* ================= REQ-01 · ฟอร์มแจ้งซ่อม ================= */}
      <Panel className="mb-4">
        <PanelHead
          title="แจ้งซ่อมใหม่"
          sub="ใบใหม่เข้าคอลัมน์ “รอรับเรื่อง” เสมอ — จะข้ามไปมอบหมายทันทีไม่ได้"
        />
        <form action={createTicketAction} className="grid gap-4 px-6 py-4 lg:grid-cols-12">
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
          <div className="lg:col-span-3">
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
          <div className="lg:col-span-2">
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
            <button type="submit" className={`${buttonClass} w-full px-2 whitespace-nowrap`}>
              แจ้งซ่อม
            </button>
          </div>
        </form>
      </Panel>

      {/* ================= กระดาน 4 คอลัมน์ (REQ-02, REQ-03, REQ-05) ================= */}
      <div className="grid gap-4 xl:grid-cols-4">
        {COLUMNS.map((status) => {
          const items = tickets.filter((t) => t.status === status);
          return (
            <section key={status} className="flex min-w-0 flex-col">
              <header className="rounded-t border border-rule bg-card">
                <span className={`block h-[2px] rounded-t ${STAGE_BAR[status]}`} />
                <div className="flex items-start justify-between gap-3 px-4 py-2">
                  <div className="min-w-0">
                    <h2 className="flex items-center gap-2 text-[15px] leading-[1.4] font-bold tracking-tight text-ink">
                      <span
                        className={`h-2.5 w-2.5 shrink-0 rounded-[2px] ${STAGE_BAR[status]}`}
                        aria-hidden="true"
                      />
                      <span className="truncate">{STATUS_LABEL[status]}</span>
                    </h2>
                    <p className="truncate text-[12px] text-ink-3">{STATUS_HINT[status]}</p>
                  </div>
                  <span className="num shrink-0 text-[22px] leading-tight font-bold text-ink">
                    {items.length}
                  </span>
                </div>
              </header>

              <div className="flex flex-col gap-3 rounded-b border border-t-0 border-rule bg-wash p-3">
                {items.length === 0 ? (
                  <p className="rounded border border-dashed border-rule-strong px-3 py-6 text-center text-[13px] leading-[1.5] text-ink-3">
                    {assignee ? "ช่างคนนี้ไม่มีงานในขั้นนี้" : "ยังไม่มีใบแจ้งซ่อมค้างอยู่ในขั้นนี้"}
                  </p>
                ) : (
                  items.map((ticket) => {
                    const asset = assetById.get(ticket.asset_id);
                    const overdue = overdueById.get(ticket.id);
                    return (
                      <article
                        key={ticket.id}
                        className="rounded border border-rule bg-card transition-colors hover:border-rule-strong"
                      >
                        {/* แถบเตือนเกินกำหนด — สี + ไอคอน + คำ ครบสามอย่าง ไม่ได้สื่อด้วยสีอย่างเดียว */}
                        {overdue ? (
                          <p className="num flex items-center gap-1.5 rounded-t border-b border-crit-line bg-crit-wash px-3 py-1 text-[12px] font-semibold text-crit-ink">
                            <IconAlert className="h-3.5 w-3.5 shrink-0" />
                            ค้าง {overdue.days_open} วัน · กำหนด {overdue.sla_days} วัน
                          </p>
                        ) : null}

                        <div className="px-3 py-2">
                          <div className="mb-1 flex items-start justify-between gap-2">
                            <PriorityBadge priority={ticket.priority} />
                            <span className="num shrink-0 font-mono text-[12px] text-ink-3">
                              #{ticket.id}
                            </span>
                          </div>

                          <h3 className="text-[15px] leading-[1.5] font-semibold text-ink">
                            {ticket.title}
                          </h3>

                          {/* ครุภัณฑ์ + ที่ตั้ง อยู่บรรทัดเดียว (บีบความสูงของการ์ดลง 1 แถว) */}
                          <p className="mt-0.5 truncate text-[13px] leading-[1.5] text-ink-2">
                            <span className="font-mono text-[12px]">
                              {asset ? asset.code : `#${ticket.asset_id}`}
                            </span>
                            {asset ? ` · ${asset.name}` : ""}
                          </p>

                          {ticket.detail ? (
                            <p className="mt-1 line-clamp-2 text-[13px] leading-[1.5] text-ink-2">
                              {ticket.detail}
                            </p>
                          ) : null}

                          {/* บรรทัด meta : ที่ตั้ง (ช่างต้องรู้ว่าไปที่ไหน) · ช่าง · วันที่แจ้ง */}
                          <p className="mt-2 flex items-baseline justify-between gap-2 border-t border-rule pt-1.5 text-[12px]">
                            <span className="min-w-0 truncate text-ink-3">
                              {ticket.assignee ? (
                                <span className="font-semibold text-ink-2">{ticket.assignee}</span>
                              ) : (
                                <span className="italic">ยังไม่มอบหมาย</span>
                              )}
                              {asset ? ` · ${asset.location}` : ""}
                            </span>
                            <span className="num shrink-0 text-ink-3">
                              {thaiDate(ticket.created_at)}
                            </span>
                          </p>
                        </div>

                        {/* ---------- ปุ่มของขั้นนั้น ---------- */}
                        {ticket.status === "NEW" ? (
                          <form
                            action={assignTicketAction}
                            className="flex gap-2 border-t border-rule bg-wash px-3 py-2"
                          >
                            <input type="hidden" name="back" value={back} />
                            <input type="hidden" name="id" value={ticket.id} />
                            <input
                              name="assignee"
                              list="technicians"
                              placeholder="ชื่อช่าง"
                              aria-label={`ชื่อช่างสำหรับใบ #${ticket.id}`}
                              className={`${inputClass} h-8 text-[13px]`}
                            />
                            <button type="submit" className={`${smallButtonClass} shrink-0`}>
                              มอบหมาย
                            </button>
                          </form>
                        ) : null}

                        {ticket.status === "ASSIGNED" ? (
                          <form
                            action={advanceTicketAction}
                            className="border-t border-rule bg-wash px-3 py-2"
                          >
                            <input type="hidden" name="back" value={back} />
                            <input type="hidden" name="id" value={ticket.id} />
                            <input type="hidden" name="status" value="IN_PROGRESS" />
                            <button type="submit" className={`${smallButtonClass} w-full`}>
                              เริ่มลงมือซ่อม
                            </button>
                          </form>
                        ) : null}

                        {ticket.status === "IN_PROGRESS" ? (
                          // <details> ของ HTML แท้ ๆ คือกลไกพับ-กางเดียวที่ใช้ได้ — ไม่มี JS ฝั่ง browser
                          <details className="group border-t border-rule bg-wash">
                            <summary
                              className={`${smallButtonClass} m-2 w-[calc(100%-1rem)] cursor-pointer`}
                            >
                              ปิดงาน + บันทึกอะไหล่
                              <IconChevron className="h-3 w-3 transition-transform group-open:rotate-90" />
                            </summary>
                            <form
                              action={closeTicketAction}
                              className="space-y-2 border-t border-rule px-3 py-2"
                            >
                              <input type="hidden" name="back" value={back} />
                              <input type="hidden" name="id" value={ticket.id} />
                              <p className="text-[12px] leading-[1.5] text-ink-3">
                                เว้นว่างได้ถ้าไม่ได้ใช้อะไหล่ · ถ้าอะไหล่ตัวใดไม่พอ
                                ระบบจะไม่ตัดสต็อกเลยสักตัว
                              </p>
                              {["1", "2"].map((row) => (
                                <div key={row} className="flex gap-2">
                                  <select
                                    name={`part_id_${row}`}
                                    defaultValue=""
                                    aria-label={`อะไหล่ช่องที่ ${row}`}
                                    className={`${inputClass} h-8 text-[13px]`}
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
                                    aria-label={`จำนวนช่องที่ ${row}`}
                                    className={`${inputClass} num h-8 w-14 shrink-0 text-right text-[13px]`}
                                  />
                                </div>
                              ))}
                              <button type="submit" className={`${smallButtonClass} w-full`}>
                                ยืนยันปิดงาน
                              </button>
                            </form>
                          </details>
                        ) : null}

                        {ticket.status === "DONE" ? (
                          // "ปิดงานแล้ว" เป็น *สถานะ* (ไม่ใช่ *ขั้น*) จึงใช้ชุดสี ok ได้
                          <p className="num flex items-center gap-1.5 border-t border-ok-line bg-ok-wash px-3 py-2 text-[12px] font-medium text-ok-ink">
                            <IconCheck className="h-3.5 w-3.5 shrink-0" />
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
