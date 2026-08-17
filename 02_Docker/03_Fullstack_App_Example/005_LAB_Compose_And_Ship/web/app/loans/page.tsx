import { createLoanAction, returnLoanAction } from "../actions";
import { apiGet, type Asset, type Loan } from "../lib/api";
import {
  buttonClass,
  Chip,
  daysSince,
  Flash,
  ghostButtonClass,
  inputClass,
  labelClass,
  Panel,
  PanelHead,
  thaiDate,
} from "../ui/kit";

export const dynamic = "force-dynamic";

// ป้ายกำกับสถานะครุภัณฑ์ที่ API คำนวณมาให้ (ไม่ใช่คอลัมน์ในฐานข้อมูล)
const ASSET_STATUS: Record<Asset["status"], { label: string; chip: string }> = {
  AVAILABLE: { label: "พร้อมให้ยืม", chip: "border-emerald-400/40 bg-emerald-400/12 text-emerald-200" },
  ON_LOAN: { label: "ถูกยืมอยู่", chip: "border-violet-400/40 bg-violet-400/12 text-violet-200" },
  IN_REPAIR: { label: "อยู่ระหว่างซ่อม", chip: "border-amber-300/40 bg-amber-400/12 text-amber-100" },
};

export default async function LoansPage({
  searchParams,
}: {
  searchParams: Promise<{ t?: string; m?: string }>;
}) {
  const sp = await searchParams;
  const [loans, assets] = await Promise.all([
    apiGet<Loan[]>("/api/loans"),
    apiGet<Asset[]>("/api/assets"),
  ]);

  const active = loans.filter((l) => l.returned_at === null);
  const history = loans.filter((l) => l.returned_at !== null);
  const availableCount = assets.filter((a) => a.status === "AVAILABLE").length;

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <section className="animate-rise mb-6">
        <p className="text-xs font-medium tracking-[0.2em] text-brand-400 uppercase">Loans</p>
        <h1 className="mt-1.5 text-3xl font-bold tracking-tight text-slate-50">ยืม-คืนครุภัณฑ์</h1>
        <p className="mt-1.5 max-w-3xl text-sm text-slate-400">
          ระบบจะปฏิเสธการยืมของที่ยังไม่ถูกคืน และของที่มีใบแจ้งซ่อมค้างอยู่ — แทนสมุดยืม-คืนที่จ่ายของซ้ำ
        </p>
      </section>

      <div className="grid gap-5 lg:grid-cols-[22rem_1fr]">
        {/* ---------- ฟอร์มยืม ---------- */}
        <div className="flex flex-col gap-5">
          <Panel className="animate-rise">
            <PanelHead title="บันทึกการยืม" hint={`พร้อมให้ยืมอยู่ ${availableCount} ชิ้น`} />
            <form action={createLoanAction} className="space-y-4 px-5 py-5">
              <div>
                <label className={labelClass} htmlFor="asset_id">
                  ครุภัณฑ์
                </label>
                <select id="asset_id" name="asset_id" required className={inputClass}>
                  {assets.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.code} · {a.name} — {ASSET_STATUS[a.status].label}
                    </option>
                  ))}
                </select>
                <p className="mt-1.5 text-[11px] text-slate-500">
                  เลือกชิ้นที่ไม่ว่างได้ เพื่อดูว่าระบบปฏิเสธพร้อมบอกเหตุผลอย่างไร
                </p>
              </div>
              <div>
                <label className={labelClass} htmlFor="borrower">
                  ผู้ยืม
                </label>
                <input
                  id="borrower"
                  name="borrower"
                  required
                  placeholder="เช่น อาจารย์ประจำวิชา 101"
                  className={inputClass}
                />
              </div>
              <button type="submit" className={`${buttonClass} w-full`}>
                บันทึกการยืม
              </button>
            </form>
          </Panel>

          <Panel className="animate-rise">
            <PanelHead title="สถานะครุภัณฑ์ทั้งหมด" hint="สถานะนี้คำนวณจากใบซ่อมและสัญญายืมที่ค้างอยู่" />
            <ul className="max-h-80 divide-y divide-white/6 overflow-y-auto">
              {assets.map((a) => (
                <li key={a.id} className="flex items-center gap-3 px-5 py-2.5">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-medium text-slate-200">{a.name}</p>
                    <p className="text-[11px] text-slate-500">{a.code}</p>
                  </div>
                  <Chip className={ASSET_STATUS[a.status].chip}>{ASSET_STATUS[a.status].label}</Chip>
                </li>
              ))}
            </ul>
          </Panel>
        </div>

        {/* ---------- รายการที่ยังไม่คืน + ประวัติ ---------- */}
        <div className="flex flex-col gap-5">
          <Panel className="animate-rise">
            <PanelHead
              title="ยังไม่คืน"
              hint="กดปุ่มรับคืนแล้วครุภัณฑ์จะกลับมาให้ยืมได้ทันที"
              right={
                <Chip className="border-violet-400/40 bg-violet-400/15 text-violet-200">
                  {active.length} รายการ
                </Chip>
              }
            />
            <ul className="divide-y divide-white/6">
              {active.length === 0 ? (
                <li className="px-5 py-10 text-center text-sm text-slate-500">
                  ไม่มีครุภัณฑ์ที่ค้างอยู่กับผู้ยืม
                </li>
              ) : (
                active.map((loan) => {
                  const days = daysSince(loan.borrowed_at);
                  return (
                    <li key={loan.id} className="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-4">
                      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-violet-400/15 text-sm font-bold text-violet-200 tabular-nums">
                        {days}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-semibold text-slate-100">
                          {loan.asset_code} · {loan.asset_name}
                        </p>
                        <p className="mt-0.5 text-xs text-slate-400">
                          ผู้ยืม {loan.borrower} · ตั้งแต่ {thaiDate(loan.borrowed_at)} ({days} วัน)
                        </p>
                      </div>
                      <form action={returnLoanAction}>
                        <input type="hidden" name="id" value={loan.id} />
                        <button type="submit" className={ghostButtonClass}>
                          รับคืน
                        </button>
                      </form>
                    </li>
                  );
                })
              )}
            </ul>
          </Panel>

          <Panel className="animate-rise">
            <PanelHead title="ประวัติการคืน" hint="เก็บไว้ตอบคำถามย้อนหลังว่าใครเคยยืมอะไรเมื่อไหร่" />
            <div className="overflow-x-auto">
              <table className="w-full min-w-[38rem] text-sm">
                <thead>
                  <tr className="border-b border-white/8 text-left text-xs text-slate-400">
                    <th className="px-5 py-2.5 font-medium">ครุภัณฑ์</th>
                    <th className="px-5 py-2.5 font-medium">ผู้ยืม</th>
                    <th className="px-5 py-2.5 font-medium">ยืมเมื่อ</th>
                    <th className="px-5 py-2.5 font-medium">คืนเมื่อ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/6">
                  {history.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-5 py-8 text-center text-slate-500">
                        ยังไม่มีประวัติการคืน
                      </td>
                    </tr>
                  ) : (
                    history.map((loan) => (
                      <tr key={loan.id} className="text-slate-300">
                        <td className="px-5 py-2.5">
                          <span className="text-slate-100">{loan.asset_code}</span>{" "}
                          <span className="text-slate-500">{loan.asset_name}</span>
                        </td>
                        <td className="px-5 py-2.5">{loan.borrower}</td>
                        <td className="px-5 py-2.5 text-xs tabular-nums">{thaiDate(loan.borrowed_at)}</td>
                        <td className="px-5 py-2.5 text-xs tabular-nums text-emerald-300">
                          {thaiDate(loan.returned_at)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Panel>
        </div>
      </div>
    </>
  );
}
