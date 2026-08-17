import {
  apiGet,
  type Asset,
  type Dashboard,
  type Loan,
  type Ticket,
  type TicketStatus,
} from "./lib/api";
import { IconAlert } from "./ui/icons";
import {
  ASSET_HEX,
  ASSET_LABEL,
  Badge,
  daysSince,
  Empty,
  Flash,
  FootLink,
  Hero,
  Legend,
  MiniStat,
  OverdueBar,
  PageHead,
  Panel,
  PanelHead,
  PriorityBadge,
  ShareBar,
  STATUS_HEX,
  STATUS_LABEL,
  StockMeter,
  thClass,
  thNumClass,
  trClass,
  type Segment,
} from "./ui/kit";

// ห้ามให้ Next แคชหน้านี้ตอน build — ตัวเลขต้องมาจากฐานข้อมูลจริง ณ เวลาที่เปิดดู
export const dynamic = "force-dynamic";

const ORDER: TicketStatus[] = ["NEW", "ASSIGNED", "IN_PROGRESS", "DONE"];
const ASSET_ORDER: Asset["status"][] = ["AVAILABLE", "ON_LOAN", "IN_REPAIR"];

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ t?: string; m?: string }>;
}) {
  const sp = await searchParams;
  // ยิงทุกเส้นพร้อมกัน ไม่ไล่ทีละอัน
  const [dash, assets, tickets, loans] = await Promise.all([
    apiGet<Dashboard>("/api/dashboard"),
    apiGet<Asset[]>("/api/assets"),
    apiGet<Ticket[]>("/api/tickets"),
    apiGet<Loan[]>("/api/loans"),
  ]);

  const openCount = dash.tickets.NEW + dash.tickets.ASSIGNED + dash.tickets.IN_PROGRESS;
  const totalTickets = openCount + dash.tickets.DONE;
  const available = assets.filter((a) => a.status === "AVAILABLE").length;
  const inRepair = assets.filter((a) => a.status === "IN_REPAIR").length;

  const stageSegments: Segment[] = ORDER.map((s) => ({
    key: s,
    label: STATUS_LABEL[s],
    value: dash.tickets[s],
    hex: STATUS_HEX[s],
  }));

  // ---------- REQ-09 : สเกลเดียวกันทุกแถบ จึงเทียบความยาวกันได้จริง (เผื่อหัวท้าย 15%) ----------
  const overdueScale = Math.max(...dash.overdue.map((o) => o.days_open), 1) * 1.15;

  // ---------- ภาระงานต่อช่าง : ตอบประโยคแรกของหัวหน้าสำนักงานตรง ๆ ----------
  // "ผมอยากเห็นหน้าจอเดียวที่บอกว่าตอนนี้มีงานอะไรอยู่ในมือใครบ้าง" (00_story.md)
  // ตั้งต้นด้วยแถว "ยังไม่มอบหมาย" แล้วเติมชื่อช่างทุกคนที่เคยมีในระบบ
  // ช่างที่ไม่มีงานค้างต้องยังขึ้นเป็นแถวค่า 0 ติดป้าย "ว่าง" — ไม่งั้นหัวหน้าจะมองไม่เห็นคนที่ว่าง
  const overdueIds = new Set(dash.overdue.map((o) => o.id));
  const load = new Map<string, { open: number; late: number }>([["", { open: 0, late: 0 }]]);
  for (const t of tickets) {
    if (!load.has(t.assignee ?? "")) load.set(t.assignee ?? "", { open: 0, late: 0 });
  }
  for (const t of tickets) {
    if (t.status === "DONE") continue;
    const row = load.get(t.assignee ?? "")!;
    row.open += 1;
    if (overdueIds.has(t.id)) row.late += 1;
  }
  const workload = [...load.entries()]
    .map(([name, v]) => ({ name, open: v.open, late: v.late }))
    // แถว "ยังไม่มอบหมาย" อยู่บนสุดเสมอ เพราะเป็นกองที่หัวหน้าต้องลงมือก่อน
    .sort((a, b) => (a.name === "" ? -1 : b.name === "" ? 1 : b.open - a.open || a.name.localeCompare(b.name)));
  const workloadMax = Math.max(1, ...workload.map((w) => w.open));

  const assetSegments: Segment[] = ASSET_ORDER.map((s) => ({
    key: s,
    label: ASSET_LABEL[s],
    value: assets.filter((a) => a.status === s).length,
    hex: ASSET_HEX[s],
  }));
  // แสดงเฉพาะชิ้นที่ "ถูกยืมอยู่" พร้อมชื่อผู้ยืม — ตอบคำถาม "ของอยู่กับใคร" ได้ในบรรทัดเดียว
  // ส่วนชิ้นที่ติดซ่อมไม่ต้องลิสต์ซ้ำที่นี่ เพราะมันคือใบแจ้งซ่อมที่อยู่ในสองแผงด้านบนอยู่แล้ว
  const activeLoans = loans.filter((l) => l.returned_at === null);

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <PageHead eyebrow="สรุปภาพรวม" title="ตอนนี้งานอะไรอยู่ในมือใคร" />

      {/* ========== แถว 1 : ตัวเลขนำของหน้า + สัดส่วนตามขั้นของงาน (REQ-08) ==========
          รวมเป็นแผงเดียวที่มีเส้นแบ่งกลาง — ไม่ใช่สองการ์ดลอย จึงไม่มีช่องว่างตายระหว่างกัน */}
      <Panel className="mb-4">
        <div className="grid xl:grid-cols-[1fr_1.6fr]">
          <div className="flex flex-col border-b border-rule xl:border-r xl:border-b-0">
            <Hero
              label="งานที่ยังไม่ปิด"
              value={openCount}
              unit="ใบ"
              note={
                <>
                  จากใบแจ้งซ่อมทั้งหมด <span className="num font-semibold text-ink-2">{totalTickets}</span> ใบ
                  · ปิดไปแล้ว <span className="num font-semibold text-ink-2">{dash.tickets.DONE}</span> ใบ
                </>
              }
            />
            <div className="mt-auto">
              <MiniStat
                label="ค้างเกินกำหนด"
                note={dash.overdue.length ? "ต้องเร่งวันนี้" : "ทุกใบยังอยู่ในกำหนด"}
                value={dash.overdue.length}
                unit="ใบ"
                tone={dash.overdue.length ? "crit" : "ink"}
              />
              <MiniStat
                label="ครุภัณฑ์ถูกยืมอยู่"
                note={`พร้อมให้ยืมอีก ${available} · ติดซ่อม ${inRepair}`}
                value={dash.loans_active}
                unit="ชิ้น"
              />
              <MiniStat
                label="อะไหล่ต้องสั่งเพิ่ม"
                note="ยอดต่ำกว่าจุดสั่งซื้อที่ตั้งไว้"
                value={dash.parts_low.length}
                unit="รายการ"
                tone={dash.parts_low.length ? "crit" : "ink"}
              />
            </div>
          </div>

          <div className="flex flex-col justify-between gap-4 px-6 py-4">
            <div className="flex items-baseline justify-between gap-4">
              <h2 className="text-[17px] leading-[1.4] font-semibold tracking-tight text-ink">
                สัดส่วนใบแจ้งซ่อมตามขั้นของงาน
              </h2>
              <p className="text-[13px] text-ink-3">แถบยิ่งเข้ม = งานเดินไปไกลขึ้น</p>
            </div>
            <ShareBar segments={stageSegments} height={44} />
            <Legend segments={stageSegments} />
            <p className="border-t border-rule pt-3 text-[13px] text-ink-3">
              ตัวเลขในแถบคือ <span className="font-medium text-ink-2">จำนวนใบ</span> ·
              ทั้งกระดานมี <span className="num font-semibold text-ink-2">{totalTickets}</span> ใบ
              และงานเดินหน้าทีละขั้นเท่านั้น ข้ามขั้นไม่ได้
            </p>
          </div>
        </div>
      </Panel>

      {/* ========== แถว 2 : งานอยู่ในมือใคร · งานค้างเกินกำหนด ========== */}
      <div className="mb-4 grid items-start gap-4 xl:grid-cols-[1fr_1.6fr]">
        <Panel className="flex flex-col">
          <PanelHead
            title="งานที่ยังไม่ปิด อยู่ในมือใคร"
            sub="นับเฉพาะใบที่ยังไม่ปิดงาน · ช่างที่ไม่มีงานค้างก็ยังขึ้นแถวเพื่อให้เห็นว่าใครว่าง"
            right={<Badge tone="neutral">{openCount} ใบ</Badge>}
          />
          <div>
            {workload.map((w) => (
              <WorkloadLine
                key={w.name || "unassigned"}
                name={w.name || "ยังไม่มอบหมาย"}
                value={w.open}
                max={workloadMax}
                late={w.late}
              />
            ))}
          </div>
          <FootLink href="/tickets" label="กรองงานตามช่างผู้รับผิดชอบ" />
        </Panel>

        <Panel className="flex flex-col">
          <PanelHead
            title="งานค้างเกินกำหนด"
            sub="ขีดดำคือเส้นกำหนดตามความเร่งด่วน · แถบแดงคือส่วนที่สายไปแล้ว"
            right={
              <Badge
                tone={dash.overdue.length ? "crit" : "neutral"}
                icon={dash.overdue.length ? <IconAlert className="h-3 w-3" /> : undefined}
              >
                <span className="num font-bold">{dash.overdue.length}</span> ใบ
              </Badge>
            }
          />
          {dash.overdue.length === 0 ? (
            <Empty
              title="ไม่มีงานค้างเกินกำหนด"
              hint="ทุกใบที่เปิดอยู่ยังอยู่ในเวลามาตรฐานของความเร่งด่วนนั้น"
            />
          ) : (
            <ul>
              {dash.overdue.map((item) => (
                <li key={item.id} className="border-b border-rule px-6 py-2 last:border-0">
                  <div className="flex items-baseline justify-between gap-4">
                    <p className="min-w-0 truncate text-[14px] font-semibold text-ink">
                      <span className="mr-1.5 font-mono text-[12px] font-medium text-ink-3">
                        #{item.id}
                      </span>
                      {item.title}
                    </p>
                    <p className="shrink-0">
                      <span className="num text-[22px] leading-none font-bold text-crit-ink">
                        {item.days_open}
                      </span>
                      <span className="ml-1 text-[12px] font-medium text-ink-3">วัน</span>
                    </p>
                  </div>
                  <div className="mt-2">
                    <OverdueBar days={item.days_open} sla={item.sla_days} scale={overdueScale} />
                  </div>
                  <div className="mt-2 flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-[13px] text-ink-3">
                    <span className="flex items-center gap-2">
                      <PriorityBadge priority={item.priority} />
                      {item.assignee ? (
                        <span>
                          ช่าง <span className="font-semibold text-ink-2">{item.assignee}</span>
                        </span>
                      ) : (
                        <span className="font-semibold text-crit-ink">ยังไม่มีผู้รับผิดชอบ</span>
                      )}
                    </span>
                    <span className="num">
                      กำหนด {item.sla_days} วัน · เกินมา{" "}
                      <span className="font-semibold text-crit-ink">
                        {item.days_open - item.sla_days}
                      </span>{" "}
                      วัน
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
          <FootLink href="/tickets" label="เปิดกระดานงานซ่อม" />
        </Panel>
      </div>

      {/* ========== แถว 3 : อะไหล่ต่ำกว่าจุดสั่งซื้อ (REQ-12) · สถานะครุภัณฑ์ ========== */}
      <div className="grid items-start gap-4 xl:grid-cols-[1fr_1.6fr]">
        <Panel className="flex flex-col">
          <PanelHead
            title="อะไหล่ต่ำกว่าจุดสั่งซื้อ"
            sub="ขีดดำคือจุดสั่งซื้อ · แถบสั้นกว่าครึ่ง = ต้องสั่งเพิ่ม"
            right={
              <Badge
                tone={dash.parts_low.length ? "crit" : "neutral"}
                icon={dash.parts_low.length ? <IconAlert className="h-3 w-3" /> : undefined}
              >
                <span className="num font-bold">{dash.parts_low.length}</span> รายการ
              </Badge>
            }
          />
          {dash.parts_low.length === 0 ? (
            <Empty
              title="อะไหล่เพียงพอทุกรายการ"
              hint="ยังไม่มีตัวไหนที่ยอดคงเหลือต่ำกว่าจุดสั่งซื้อที่ตั้งไว้"
            />
          ) : (
            <ul>
              {dash.parts_low.map((part) => (
                <li key={part.id} className="border-b border-rule px-6 py-2 last:border-0">
                  <div className="flex items-baseline justify-between gap-3">
                    <p className="min-w-0 truncate text-[14px] font-semibold text-ink">
                      {part.name}
                    </p>
                    <p className="num shrink-0 text-[14px] font-bold text-crit-ink">
                      {part.qty_on_hand}
                      <span className="font-medium text-ink-3"> / {part.reorder_point}</span>
                    </p>
                  </div>
                  <div className="mt-2">
                    <StockMeter
                      qty={part.qty_on_hand}
                      reorder={part.reorder_point}
                      below={true}
                    />
                  </div>
                  <div className="mt-2 flex items-baseline justify-between gap-3 text-[13px]">
                    <span className="font-mono text-[12px] tracking-wide text-ink-3">
                      {part.sku}
                    </span>
                    <span className="num text-ink-3">
                      ต้องเติมอีกอย่างน้อย{" "}
                      <span className="font-semibold text-ink-2">
                        {part.reorder_point - part.qty_on_hand}
                      </span>{" "}
                      ชิ้น
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
          <FootLink href="/parts" label="เปิดคลังอะไหล่" />
        </Panel>

        <Panel className="flex flex-col">
          <PanelHead
            title="สถานะครุภัณฑ์"
            sub="สถานะคำนวณจากใบซ่อมและสัญญายืมที่ค้างอยู่ ไม่ใช่คอลัมน์ในฐานข้อมูล"
            right={
              <Badge tone="neutral">
                <span className="num font-bold">{assets.length}</span> ชิ้น
              </Badge>
            }
          />
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-b border-rule px-6 py-2">
            <div className="w-[200px] shrink-0">
              <ShareBar segments={assetSegments} height={12} showValue={false} />
            </div>
            <Legend segments={assetSegments} />
          </div>
          <table className="w-full">
            <thead>
              <tr>
                <th className={thClass}>ชิ้นที่ถูกยืมอยู่ตอนนี้</th>
                <th className={thClass}>อยู่กับใคร</th>
                <th className={thNumClass}>ยืมมาแล้ว</th>
              </tr>
            </thead>
            <tbody>
              {activeLoans.length === 0 ? (
                <tr>
                  <td colSpan={3}>
                    <Empty
                      title="ยังไม่มีของค้างคืน — ครุภัณฑ์ทุกชิ้นอยู่ในตู้"
                      hint={`อีก ${inRepair} ชิ้นยืมไม่ได้เพราะมีใบแจ้งซ่อมที่ยังไม่ปิด`}
                    />
                  </td>
                </tr>
              ) : (
                activeLoans.map((loan) => (
                  <tr key={loan.id} className={trClass}>
                    <td className="px-4 py-1.5">
                      <span className="font-mono text-[12px] text-ink-3">{loan.asset_code}</span>{" "}
                      <span className="text-[14px] font-medium text-ink">{loan.asset_name}</span>
                    </td>
                    <td className="px-4 py-1.5 text-[13px] text-ink-2">{loan.borrower}</td>
                    <td className="num px-4 py-1.5 text-right whitespace-nowrap">
                      <span className="text-[14px] font-semibold text-ink">
                        {daysSince(loan.borrowed_at)}
                      </span>
                      <span className="ml-1 text-[12px] text-ink-3">วัน</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          <FootLink
            href="/loans"
            label={`ดูทะเบียนครุภัณฑ์ทั้ง ${assets.length} ชิ้น · ติดซ่อมอยู่ ${inRepair} ชิ้น`}
          />
        </Panel>
      </div>
    </>
  );
}

/** หนึ่งแถวของแผงภาระงาน — ป้ายค่าอยู่ปลายแท่ง ไม่ต้องมี legend เพราะมีชุดข้อมูลชุดเดียว */
function WorkloadLine({
  name,
  value,
  max,
  late,
}: {
  name: string;
  value: number;
  max: number;
  late: number;
}) {
  const pct = value > 0 ? Math.max(4, Math.round((value / max) * 100)) : 0;
  return (
    <div className="flex items-center gap-3 border-t border-rule px-6 py-2">
      <p className="w-[108px] shrink-0 truncate text-[14px] font-semibold text-ink">{name}</p>
      <div className="h-2.5 min-w-0 flex-1 rounded-[2px] bg-accent-wash">
        <div className="h-full rounded-[2px] bg-accent-2" style={{ width: `${pct}%` }} />
      </div>
      <span className="num w-4 shrink-0 text-right text-[14px] font-bold text-ink">{value}</span>
      <span className="w-[96px] shrink-0 text-right">
        {late > 0 ? (
          <Badge tone="crit" icon={<IconAlert className="h-3 w-3" />}>
            เกินกำหนด <span className="num font-bold">{late}</span>
          </Badge>
        ) : value === 0 ? (
          <Badge tone="quiet">ว่าง</Badge>
        ) : null}
      </span>
    </div>
  );
}
