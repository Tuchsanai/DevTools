import { movePartAction } from "../actions";
import { apiGet, type Part, type StockMove } from "../lib/api";
import { IconAlert, IconDot } from "../ui/icons";
import {
  Badge,
  buttonClass,
  Empty,
  Flash,
  ghostButtonClass,
  inputClass,
  labelClass,
  PageHead,
  Panel,
  PanelHead,
  StockMeter,
  thaiDateTime,
  thClass,
  thNumClass,
  trClass,
} from "../ui/kit";

export const dynamic = "force-dynamic";

const LEDGER_LIMIT = 12;

export default async function PartsPage({
  searchParams,
}: {
  searchParams: Promise<{ t?: string; m?: string }>;
}) {
  const sp = await searchParams;
  const parts = await apiGet<Part[]>("/api/parts");

  // ประวัติของอะไหล่แต่ละตัวเป็นคนละ endpoint — ยิงพร้อมกันทีเดียว ไม่ไล่ทีละตัว
  const movesByPart = new Map<number, StockMove[]>(
    await Promise.all(
      parts.map(
        async (p) =>
          [p.id, await apiGet<StockMove[]>(`/api/parts/${p.id}/moves`)] as [number, StockMove[]],
      ),
    ),
  );

  const partById = new Map(parts.map((p) => [p.id, p]));
  // REQ-07 : รวมความเคลื่อนไหวของทุกอะไหล่เป็นสมุดบัญชีเล่มเดียว เรียงใหม่→เก่า
  const ledger = [...movesByPart.values()]
    .flat()
    .sort((a, b) => b.created_at.localeCompare(a.created_at));

  const low = parts.filter((p) => p.below_reorder);
  const totalQty = parts.reduce((sum, p) => sum + p.qty_on_hand, 0);

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <PageHead eyebrow="คลังอะไหล่" title="เหลือเท่าไหร่ และตัวไหนต้องสั่งก่อน" />

      {/* ================= REQ-06 · บันทึกการเคลื่อนไหว ================= */}
      <Panel className="mb-4">
        <PanelHead
          title="บันทึกการเคลื่อนไหว"
          sub="กรอกจำนวนเป็นเลขบวกเสมอ แล้วเลือกทิศทางที่ปุ่ม — เบิกเกินยอดคงเหลือระบบจะปฏิเสธ และยอดไม่เปลี่ยน"
        />
        <form action={movePartAction} className="grid gap-4 px-6 py-4 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <label className={labelClass} htmlFor="part-id">
              อะไหล่
            </label>
            <select id="part-id" name="id" required className={inputClass}>
              {parts.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.sku} · {p.name} (เหลือ {p.qty_on_hand})
                </option>
              ))}
            </select>
          </div>
          <div className="lg:col-span-2">
            <label className={labelClass} htmlFor="move-qty">
              จำนวน
            </label>
            <input
              id="move-qty"
              name="qty"
              type="number"
              min={1}
              defaultValue={1}
              required
              className={`${inputClass} num text-right`}
            />
          </div>
          <div className="lg:col-span-3">
            <label className={labelClass} htmlFor="move-reason">
              เหตุผล
            </label>
            <input
              id="move-reason"
              name="reason"
              placeholder="เช่น รับเข้าจากผู้ขาย"
              className={inputClass}
            />
          </div>
          {/* ปุ่มสองปุ่มใช้ฟอร์มเดียวกัน แยกกันที่ค่า name="direction" ที่ปุ่มส่งไปเอง */}
          <div className="flex items-end gap-2 lg:col-span-3">
            <button type="submit" name="direction" value="in" className={`${buttonClass} flex-1`}>
              รับเข้า
            </button>
            <button
              type="submit"
              name="direction"
              value="out"
              className={`${ghostButtonClass} flex-1`}
            >
              เบิกออก
            </button>
          </div>
        </form>
      </Panel>

      {/* ================= REQ-12 · ยอดคงเหลือรายอะไหล่ ================= */}
      <Panel className="mb-4">
        <PanelHead
          title="ยอดคงเหลือรายอะไหล่"
          sub="รางของมิเตอร์ยาวสองเท่าของจุดสั่งซื้อ ขีดดำจึงอยู่กึ่งกลางทุกแถว — แถบสั้นกว่าครึ่ง แปลว่าต้องสั่งเพิ่ม"
          right={
            <Badge
              tone={low.length ? "crit" : "neutral"}
              icon={low.length ? <IconAlert className="h-3 w-3" /> : undefined}
            >
              ต่ำกว่าจุดสั่งซื้อ <span className="num font-bold">{low.length}</span> รายการ
            </Badge>
          }
        />
        <table className="w-full">
          <thead>
            <tr>
              <th className={`${thClass} w-32`}>รหัส</th>
              <th className={thClass}>ชื่ออะไหล่</th>
              <th className={thNumClass}>คงเหลือ</th>
              <th className={thNumClass}>จุดสั่งซื้อ</th>
              <th className={thNumClass}>ส่วนต่าง</th>
              <th className={`${thClass} w-[220px]`}>ระดับเทียบจุดสั่งซื้อ</th>
              <th className={thClass}>สถานะ</th>
              <th className={thNumClass}>เคลื่อนไหว</th>
            </tr>
          </thead>
          <tbody>
            {parts.map((part) => {
              const diff = part.qty_on_hand - part.reorder_point;
              const moves = movesByPart.get(part.id) ?? [];
              return (
                <tr key={part.id} className={trClass}>
                  <td className="px-4 py-2 font-mono text-[12px] whitespace-nowrap text-ink-3">
                    {part.sku}
                  </td>
                  <td className="px-4 py-2 text-[14px] font-semibold text-ink">{part.name}</td>
                  <td
                    className={`num px-4 py-2 text-right text-[17px] font-bold ${
                      part.below_reorder ? "text-crit-ink" : "text-ink"
                    }`}
                  >
                    {part.qty_on_hand}
                  </td>
                  <td className="num px-4 py-2 text-right text-[14px] text-ink-2">
                    {part.reorder_point}
                  </td>
                  {/* ส่วนต่างใช้หมึกกลาง ยกเว้นค่าติดลบที่เป็นสัญญาณต้องลงมือจริง ๆ */}
                  <td
                    className={`num px-4 py-2 text-right text-[14px] font-semibold ${
                      diff < 0 ? "text-crit-ink" : "text-ink-2"
                    }`}
                  >
                    {diff > 0 ? `+${diff}` : diff}
                  </td>
                  <td className="px-4 py-2">
                    <StockMeter
                      qty={part.qty_on_hand}
                      reorder={part.reorder_point}
                      below={part.below_reorder}
                    />
                  </td>
                  <td className="px-4 py-2">
                    {part.below_reorder ? (
                      <Badge tone="crit" icon={<IconAlert className="h-3 w-3" />}>
                        ต้องสั่งเพิ่ม
                      </Badge>
                    ) : (
                      // "เพียงพอ" ห้ามเป็นสีเขียว — ไม่งั้นทั้งตารางเขียวจนแถวที่ต้องสั่งไม่เด่น
                      <Badge tone="neutral" icon={<IconDot className="h-2.5 w-2.5" />}>
                        เพียงพอ
                      </Badge>
                    )}
                  </td>
                  <td className="num px-4 py-2 text-right text-[13px] text-ink-3">
                    {moves.length}
                  </td>
                </tr>
              );
            })}
          </tbody>
          {/* แถวรวม — คั่นด้วยเส้นหนา 2px ตามธรรมเนียมงบดุล */}
          <tfoot>
            <tr className="border-t-2 border-rule-strong bg-wash">
              <td className="px-4 py-2 text-[11px] font-semibold tracking-[0.12em] text-ink-3" colSpan={2}>
                รวมทุกรายการ · {parts.length} รายการในทะเบียนคลัง
              </td>
              <td className="num px-4 py-2 text-right whitespace-nowrap">
                <span className="text-[17px] font-bold text-ink">{totalQty}</span>
                <span className="ml-1 text-[12px] font-medium text-ink-3">ชิ้น</span>
              </td>
              <td colSpan={4} />
              <td className="num px-4 py-2 text-right text-[13px] text-ink-3">{ledger.length}</td>
            </tr>
          </tfoot>
        </table>
      </Panel>

      {/* ================= REQ-07 · สมุดความเคลื่อนไหว ================= */}
      <Panel>
        <PanelHead
          title="ความเคลื่อนไหวของคลัง"
          sub="รวมทุกอะไหล่ไว้เล่มเดียว เรียงจากใหม่ไปเก่า — รายการที่มีเลขใบซ่อมคือของที่ถูกตัดตอนช่างปิดงาน"
          right={
            <Badge tone="neutral">
              ทั้งหมด <span className="num font-bold text-ink">{ledger.length}</span> รายการ
            </Badge>
          }
        />
        {ledger.length === 0 ? (
          <Empty
            title="ยังไม่มีความเคลื่อนไหว"
            hint="เมื่อมีการรับเข้า เบิกออก หรือปิดใบซ่อมที่ใช้อะไหล่ รายการจะมาปรากฏที่นี่"
          />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr>
                  <th className={`${thClass} w-40`}>เวลา</th>
                  <th className={thClass}>อะไหล่</th>
                  <th className={thClass}>เหตุผล</th>
                  <th className={`${thClass} w-32`}>อ้างอิงใบซ่อม</th>
                  <th className={`${thClass} w-24`}>ทิศทาง</th>
                  <th className={thNumClass}>จำนวน</th>
                </tr>
              </thead>
              <tbody>
                {ledger.slice(0, LEDGER_LIMIT).map((move) => {
                  const part = partById.get(move.part_id);
                  const inbound = move.delta > 0;
                  return (
                    <tr key={move.id} className={trClass}>
                      <td className="num px-4 py-1.5 text-[13px] whitespace-nowrap text-ink-3">
                        {thaiDateTime(move.created_at)}
                      </td>
                      <td className="px-4 py-1.5 text-[14px] font-medium whitespace-nowrap text-ink">
                        {part?.name ?? `อะไหล่ #${move.part_id}`}
                      </td>
                      <td className="px-4 py-1.5 text-[13px] text-ink-2">{move.reason}</td>
                      <td className="px-4 py-1.5 font-mono text-[12px] text-ink-3">
                        {move.ticket_id ? `#${move.ticket_id}` : "—"}
                      </td>
                      {/* รับเข้า/เบิกออก คืองานปกติ ไม่ใช่สถานะเตือน — อ่านจากคำ + เครื่องหมาย ไม่ย้อมสี */}
                      <td className="px-4 py-1.5 text-[13px] text-ink-2">
                        {inbound ? "รับเข้า" : "เบิกออก"}
                      </td>
                      <td className="num px-4 py-1.5 text-right text-[14px] font-bold text-ink">
                        {inbound ? `+${move.delta}` : `−${Math.abs(move.delta)}`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {ledger.length > LEDGER_LIMIT ? (
              <p className="border-t border-rule px-6 py-2 text-[13px] text-ink-3">
                แสดง {LEDGER_LIMIT} รายการล่าสุด จากทั้งหมด{" "}
                <span className="num font-semibold text-ink-2">{ledger.length}</span> รายการ
              </p>
            ) : null}
          </>
        )}
      </Panel>
    </>
  );
}
