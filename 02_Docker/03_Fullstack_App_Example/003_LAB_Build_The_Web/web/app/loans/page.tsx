import { createLoanAction, returnLoanAction } from "../actions";
import { apiGet, type Asset, type Loan } from "../lib/api";
import {
  ASSET_HEX,
  ASSET_LABEL,
  AssetBadge,
  Badge,
  buttonClass,
  daysSince,
  Empty,
  EmptyRow,
  Flash,
  inputClass,
  labelClass,
  Legend,
  PageHead,
  Panel,
  PanelHead,
  ShareBar,
  smallGhostClass,
  thaiDate,
  thaiDateTime,
  thClass,
  thNumClass,
  trClass,
  type Segment,
} from "../ui/kit";

export const dynamic = "force-dynamic";

const ASSET_ORDER: Asset["status"][] = ["AVAILABLE", "ON_LOAN", "IN_REPAIR"];

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

  // ★ คอลัมน์ "ผู้ยืมปัจจุบัน" ของทะเบียน — ไม่งั้นต้องเงยไปอ่านตารางด้านบนเพื่อตอบว่าของอยู่กับใคร
  const borrowerByAsset = new Map(active.map((l) => [l.asset_id, l.borrower]));

  const segments: Segment[] = ASSET_ORDER.map((s) => ({
    key: s,
    label: ASSET_LABEL[s],
    value: assets.filter((a) => a.status === s).length,
    hex: ASSET_HEX[s],
  }));

  return (
    <>
      <Flash tone={sp.t} message={sp.m} />

      <PageHead eyebrow="ยืม-คืนครุภัณฑ์" title="ของชิ้นนี้อยู่กับใคร ตั้งแต่เมื่อไหร่" />

      <Panel className="mb-4">
        <div className="grid lg:grid-cols-[1fr_2fr]">
          {/* ---------- REQ-10 / REQ-11 · ฟอร์มยืม ---------- */}
          <div className="flex flex-col border-b border-rule lg:border-r lg:border-b-0">
            <PanelHead
              title="บันทึกการยืม"
              sub="เลือกชิ้นที่ไม่ว่างได้ เพื่อดูว่าระบบปฏิเสธพร้อมเหตุผลอย่างไร"
            />
          <form action={createLoanAction} className="space-y-3 px-6 py-3">
            <div>
              <label className={labelClass} htmlFor="asset_id">
                ครุภัณฑ์
              </label>
              <select id="asset_id" name="asset_id" required className={inputClass}>
                {assets.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.code} · {a.name} — {ASSET_LABEL[a.status]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass} htmlFor="borrower">
                ผู้ยืม
              </label>
              <input
                id="borrower"
                name="borrower"
                required
                placeholder="เช่น วิทยากรหลักสูตร Data 101"
                className={inputClass}
              />
            </div>
            <button type="submit" className={`${buttonClass} w-full`}>
              บันทึกการยืม
            </button>
            <p className="border-t border-rule pt-2 text-[13px] leading-[1.5] text-ink-3">
              ของที่ยังไม่ถูกคืน หรือมีใบแจ้งซ่อมค้างอยู่ ระบบจะปฏิเสธพร้อมบอกเหตุผล
            </p>
            </form>
          </div>

          {/* ---------- ครุภัณฑ์ที่ยังไม่คืน ---------- */}
          <div className="flex flex-col">
            <PanelHead
            title="ครุภัณฑ์ที่ยังไม่คืน"
            sub="กดรับคืนแล้วครุภัณฑ์ชิ้นนั้นกลับมายืมได้ทันที"
            right={
              <Badge tone="neutral">
                <span className="num font-bold text-ink">{active.length}</span> รายการ
              </Badge>
            }
          />
          {active.length === 0 ? (
            <Empty
              title="ยังไม่มีของค้างคืน — ครุภัณฑ์ทุกชิ้นอยู่ในตู้"
              hint="บันทึกการยืมรายการใหม่ได้จากฟอร์มด้านซ้าย"
            />
          ) : (
            <table className="w-full">
              <thead>
                <tr>
                  <th className={thClass}>ครุภัณฑ์</th>
                  <th className={thClass}>ผู้ยืม</th>
                  <th className={thClass}>ยืมเมื่อ</th>
                  <th className={thNumClass}>ยืมมาแล้ว</th>
                  <th className={`${thClass} text-right`}>รับคืน</th>
                </tr>
              </thead>
              <tbody>
                {active.map((loan) => (
                  <tr key={loan.id} className={trClass}>
                    <td className="px-4 py-2">
                      <span className="font-mono text-[12px] text-ink-3">{loan.asset_code}</span>{" "}
                      <span className="text-[14px] font-semibold text-ink">{loan.asset_name}</span>
                    </td>
                    <td className="px-4 py-2 text-[14px] text-ink-2">{loan.borrower}</td>
                    <td className="num px-4 py-2 text-[13px] whitespace-nowrap text-ink-2">
                      {thaiDateTime(loan.borrowed_at)}
                    </td>
                    <td className="num px-4 py-2 text-right whitespace-nowrap">
                      <span className="text-[14px] font-semibold text-ink">
                        {daysSince(loan.borrowed_at)}
                      </span>
                      <span className="ml-1 text-[12px] text-ink-3">วัน</span>
                    </td>
                    <td className="px-4 py-2 text-right">
                      <form action={returnLoanAction} className="inline-flex">
                        <input type="hidden" name="id" value={loan.id} />
                        <button type="submit" className={smallGhostClass}>
                          รับคืน
                        </button>
                      </form>
                    </td>
                  </tr>
                ))}
              </tbody>
              </table>
            )}
            <p className="mt-auto border-t border-rule px-6 py-2 text-[13px] leading-[1.5] text-ink-3">
              ครุภัณฑ์ที่เหลือดูได้ในทะเบียนด้านล่าง · ชิ้นที่มีใบแจ้งซ่อมค้างอยู่จะยืมไม่ได้จนกว่าจะปิดใบซ่อม
            </p>
          </div>
        </div>
      </Panel>

      {/* ---------- ทะเบียนครุภัณฑ์ทั้งหมด (แสดงครบทุกแถวโดยไม่ใช้พื้นที่เลื่อนย่อย) ---------- */}
      <Panel className="mb-4">
        <PanelHead
          title="ทะเบียนครุภัณฑ์ทั้งหมด"
          sub={`ทั้งหมด ${assets.length} ชิ้น · สถานะคำนวณจากใบซ่อมและสัญญายืมที่ค้างอยู่ ไม่ใช่คอลัมน์ในฐานข้อมูล`}
          right={
            /* แถบสัดส่วนบรรทัดเดียวแทนแถบตัวเลข 3 ช่องที่กินความสูงไปเปล่า ๆ */
            <div className="flex items-center gap-4">
              <div className="w-[140px] shrink-0">
                <ShareBar segments={segments} height={12} showValue={false} />
              </div>
              <Legend segments={segments} />
            </div>
          }
        />
        <table className="w-full">
          <thead>
            <tr>
              <th className={`${thClass} w-24`}>รหัส</th>
              <th className={thClass}>ชื่อครุภัณฑ์</th>
              <th className={thClass}>ที่ตั้ง</th>
              <th className={thClass}>สถานะ</th>
              <th className={thClass}>ผู้ยืมปัจจุบัน</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((a) => {
              const borrower = borrowerByAsset.get(a.id);
              return (
                <tr key={a.id} className={trClass}>
                  <td className="px-4 py-1 font-mono text-[12px] text-ink-3">{a.code}</td>
                  <td className="px-4 py-1 text-[14px] font-medium text-ink">{a.name}</td>
                  <td className="px-4 py-1 text-[13px] text-ink-2">{a.location}</td>
                  <td className="px-4 py-1">
                    <AssetBadge status={a.status} />
                  </td>
                  <td className="px-4 py-1 text-[13px] text-ink-2">
                    {borrower ?? <span className="text-ink-3">—</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Panel>

      {/* ---------- ประวัติการคืน ---------- */}
      <Panel>
        <PanelHead
          title="ประวัติการคืน"
          sub="เก็บไว้ตอบคำถามย้อนหลังว่าใครเคยยืมอะไร เมื่อไหร่ และคืนเมื่อไหร่"
          right={
            <Badge tone="neutral">
              <span className="num font-bold text-ink">{history.length}</span> รายการ
            </Badge>
          }
        />
        <table className="w-full">
          <thead>
            <tr>
              <th className={`${thClass} w-24`}>รหัส</th>
              <th className={thClass}>ครุภัณฑ์</th>
              <th className={thClass}>ผู้ยืม</th>
              <th className={thClass}>ยืมเมื่อ</th>
              <th className={thClass}>คืนเมื่อ</th>
              <th className={thNumClass}>ยืมไปทั้งหมด</th>
            </tr>
          </thead>
          <tbody>
            {history.length === 0 ? (
              <EmptyRow
                colSpan={6}
                title="ยังไม่มีประวัติการคืน"
                hint="เมื่อกดรับคืนสัญญาแรก รายการจะมาปรากฏที่นี่พร้อมวันที่ยืมและวันที่คืน"
              />
            ) : (
              history.map((loan) => {
                const days = Math.max(
                  0,
                  Math.floor(
                    (new Date(loan.returned_at!).getTime() -
                      new Date(loan.borrowed_at).getTime()) /
                      86_400_000,
                  ),
                );
                return (
                  <tr key={loan.id} className={trClass}>
                    <td className="px-4 py-1.5 font-mono text-[12px] text-ink-3">
                      {loan.asset_code}
                    </td>
                    <td className="px-4 py-1.5 text-[14px] font-medium text-ink">
                      {loan.asset_name}
                    </td>
                    <td className="px-4 py-1.5 text-[13px] text-ink-2">{loan.borrower}</td>
                    <td className="num px-4 py-1.5 text-[13px] text-ink-2">
                      {thaiDate(loan.borrowed_at)}
                    </td>
                    <td className="num px-4 py-1.5 text-[13px] font-medium text-ink">
                      {thaiDate(loan.returned_at)}
                    </td>
                    <td className="num px-4 py-1.5 text-right whitespace-nowrap">
                      <span className="text-[14px] font-semibold text-ink">{days}</span>
                      <span className="ml-1 text-[12px] text-ink-3">วัน</span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </Panel>
    </>
  );
}
