import { movePartAction } from "../actions";
import { apiGet, type Part, type StockMove } from "../lib/api";
import {
  buttonClass,
  Chip,
  Flash,
  inputClass,
  labelClass,
  Panel,
  PanelHead,
  StockBar,
  thaiDate,
} from "../ui/kit";

export const dynamic = "force-dynamic";

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

  const low = parts.filter((p) => p.below_reorder);
  const totalQty = parts.reduce((sum, p) => sum + p.qty_on_hand, 0);

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <section className="animate-rise mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-brand-400 uppercase">Inventory</p>
          <h1 className="mt-1.5 text-3xl font-bold tracking-tight text-slate-50">คลังอะไหล่</h1>
          <p className="mt-1.5 max-w-3xl text-sm text-slate-400">
            ทุกการรับเข้าและเบิกออกถูกบันทึกไว้ย้อนดูได้ · เบิกเกินยอดคงเหลือไม่ได้ ยอดจึงไม่มีทางติดลบ
          </p>
        </div>
        <div className="flex gap-2">
          <Chip className="border-white/12 bg-white/6 px-3 py-1 text-xs text-slate-200">
            อะไหล่ {parts.length} รายการ · รวม {totalQty} ชิ้น
          </Chip>
          <Chip
            className={
              low.length
                ? "border-rose-400/40 bg-rose-500/15 px-3 py-1 text-xs text-rose-200"
                : "border-emerald-400/40 bg-emerald-400/12 px-3 py-1 text-xs text-emerald-200"
            }
          >
            ต่ำกว่าจุดสั่งซื้อ {low.length} รายการ
          </Chip>
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-2">
        {parts.map((part) => {
          const moves = movesByPart.get(part.id) ?? [];
          return (
            <Panel key={part.id} className="animate-rise overflow-hidden">
              {/* ---------- หัวการ์ด + แถบสัดส่วน ---------- */}
              <div className="px-5 pt-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="text-base font-semibold text-slate-50">{part.name}</h2>
                    <p className="mt-0.5 font-mono text-[11px] tracking-wide text-slate-500">
                      {part.sku}
                    </p>
                  </div>
                  <div className="text-right">
                    <p
                      className={`text-4xl leading-none font-bold tabular-nums ${
                        part.below_reorder ? "text-rose-300" : "text-slate-50"
                      }`}
                    >
                      {part.qty_on_hand}
                    </p>
                    <p className="mt-1 text-[11px] text-slate-500">จุดสั่งซื้อ {part.reorder_point}</p>
                  </div>
                </div>

                <div className="mt-4">
                  <StockBar
                    qty={part.qty_on_hand}
                    reorder={part.reorder_point}
                    below={part.below_reorder}
                  />
                  <div className="mt-1.5 flex items-center justify-between text-[11px]">
                    <span className="text-slate-500">
                      ขีดขาวคือจุดสั่งซื้อ · แถบเลยขีดไปทางขวา = ยอดปลอดภัย
                    </span>
                    {part.below_reorder ? (
                      <Chip className="border-rose-400/50 bg-rose-500/20 text-rose-100">
                        ต้องสั่งเพิ่ม
                      </Chip>
                    ) : (
                      <Chip className="border-emerald-400/40 bg-emerald-400/12 text-emerald-200">
                        เพียงพอ
                      </Chip>
                    )}
                  </div>
                </div>
              </div>

              {/* ---------- ฟอร์มรับเข้า / เบิกออก ---------- */}
              <form
                action={movePartAction}
                className="mt-4 grid grid-cols-2 gap-3 border-t border-white/8 bg-white/3 px-5 py-4 sm:grid-cols-12"
              >
                <input type="hidden" name="id" value={part.id} />
                <div className="col-span-1 sm:col-span-2">
                  <label className={labelClass} htmlFor={`qty-${part.id}`}>
                    จำนวน
                  </label>
                  <input
                    id={`qty-${part.id}`}
                    name="qty"
                    type="number"
                    min={1}
                    defaultValue={1}
                    required
                    className={inputClass}
                  />
                </div>
                <div className="col-span-1 sm:col-span-6">
                  <label className={labelClass} htmlFor={`reason-${part.id}`}>
                    เหตุผล
                  </label>
                  <input
                    id={`reason-${part.id}`}
                    name="reason"
                    placeholder="เช่น รับเข้าจากผู้ขาย"
                    className={inputClass}
                  />
                </div>
                {/* ปุ่มสองปุ่มใช้ฟอร์มเดียวกัน แยกกันด้วยค่า name="direction" ที่ปุ่มส่งไปเอง */}
                <div className="col-span-2 flex items-end gap-2 sm:col-span-4">
                  <button
                    type="submit"
                    name="direction"
                    value="in"
                    className={`${buttonClass} flex-1 bg-emerald-400 hover:bg-emerald-300`}
                  >
                    รับเข้า
                  </button>
                  <button
                    type="submit"
                    name="direction"
                    value="out"
                    className={`${buttonClass} flex-1 bg-amber-400 hover:bg-amber-300`}
                  >
                    เบิกออก
                  </button>
                </div>
              </form>

              {/* ---------- ประวัติการเคลื่อนไหว ---------- */}
              <details className="border-t border-white/8">
                <summary className="cursor-pointer px-5 py-3 text-xs font-medium text-slate-400 transition hover:text-slate-200">
                  ประวัติการเคลื่อนไหว ({moves.length} รายการ)
                </summary>
                <ul className="divide-y divide-white/6 border-t border-white/8">
                  {moves.length === 0 ? (
                    <li className="px-5 py-4 text-center text-xs text-slate-500">ยังไม่มีการเคลื่อนไหว</li>
                  ) : (
                    moves.map((move) => (
                      <li key={move.id} className="flex items-center gap-3 px-5 py-2.5 text-xs">
                        <span
                          className={`w-12 shrink-0 text-right font-semibold tabular-nums ${
                            move.delta > 0 ? "text-emerald-300" : "text-amber-300"
                          }`}
                        >
                          {move.delta > 0 ? `+${move.delta}` : move.delta}
                        </span>
                        <span className="min-w-0 flex-1 truncate text-slate-300">
                          {move.reason}
                          {move.ticket_id ? (
                            <span className="text-slate-500"> · ใบซ่อม #{move.ticket_id}</span>
                          ) : null}
                        </span>
                        <span className="shrink-0 tabular-nums text-slate-500">
                          {thaiDate(move.created_at)}
                        </span>
                      </li>
                    ))
                  )}
                </ul>
              </details>
            </Panel>
          );
        })}
      </div>
    </>
  );
}
