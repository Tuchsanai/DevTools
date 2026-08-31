import type { Metadata } from "next";
import { headers } from "next/headers";
import Link from "next/link";
import "./globals.css";
import { apiGet, type Dashboard } from "./lib/api";
import {
  IconAlert,
  IconBoard,
  IconCheck,
  IconLoan,
  IconOverview,
  IconParts,
  IconSkillSpace,
} from "./ui/icons";

// ต่างจาก API_BASE_URL ที่อ่านตอนรัน — เปลี่ยนได้โดยไม่ต้อง build image ใหม่
const SITE_NAME = process.env.NEXT_PUBLIC_SITE_NAME || "SkillSpace";

export const metadata: Metadata = {
  title: `${SITE_NAME} · ระบบงานซ่อมและครุภัณฑ์`,
  description: "ระบบแจ้งซ่อม ยืม-คืนครุภัณฑ์ และคลังอะไหล่ของ SkillSpace",
};

type NavItem = {
  href: string;
  label: string;
  caption: string;
  Icon: (p: { className?: string }) => React.JSX.Element;
};

const NAV: NavItem[] = [
  { href: "/", label: "สรุปภาพรวม", caption: "ตัวเลขวันนี้", Icon: IconOverview },
  { href: "/tickets", label: "กระดานงานซ่อม", caption: "งานอยู่ในมือใคร", Icon: IconBoard },
  { href: "/loans", label: "ยืม-คืนครุภัณฑ์", caption: "ของอยู่กับใคร", Icon: IconLoan },
  { href: "/parts", label: "คลังอะไหล่", caption: "เหลือเท่าไหร่", Icon: IconParts },
];

/**
 * ตัวเลขคิวงานข้างเมนู + ตัวเลขเตือนบนแถบบน — ดึงครั้งเดียวที่ layout ใช้ได้ทั้งสองที่
 * ถ้าบริการเบื้องหลังยังไม่ขึ้น แถบนำทางต้องยังเรนเดอร์ได้ (แค่ไม่มีตัวเลข) จึงกลืน error ไว้
 */
async function loadCounts() {
  try {
    const dash = await apiGet<Dashboard>("/api/dashboard");
    return {
      queue: {
        "/tickets": dash.tickets.NEW + dash.tickets.ASSIGNED + dash.tickets.IN_PROGRESS,
        "/loans": dash.loans_active,
        "/parts": dash.parts_low.length,
      } as Record<string, number>,
      overdue: dash.overdue.length,
      partsLow: dash.parts_low.length,
      ready: true,
    };
  } catch {
    return { queue: {} as Record<string, number>, overdue: 0, partsLow: 0, ready: false };
  }
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // layout เป็น server component จึงไม่มี usePathname() ให้ใช้ (และห้ามมี JS ฝั่ง browser)
  // middleware.ts จึงแปะ path ปัจจุบันมาให้ทาง header แทน
  const [h, counts] = await Promise.all([headers(), loadCounts()]);
  const pathname = h.get("x-pathname") ?? "/";
  const stamp = new Intl.DateTimeFormat("th-TH", {
    day: "numeric",
    month: "short",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Bangkok",
  }).format(new Date());

  return (
    <html lang="th">
      <body className="min-h-screen font-sans">
        <div className="flex min-h-screen">
          {/* ============ แถบนำทางถาวรด้านซ้าย ============ */}
          <aside className="sticky top-0 hidden h-screen w-[264px] shrink-0 flex-col overflow-hidden bg-rail lg:flex">
            <Link
              href="/"
              className="group relative flex items-center gap-3 border-b border-rail-2 px-6 py-5 transition-colors hover:bg-rail-2"
            >
              <span className="absolute inset-x-0 top-0 h-1 bg-accent-2" aria-hidden="true" />
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-[10px] bg-accent text-white transition-colors group-hover:bg-accent-2">
                <IconSkillSpace className="h-6 w-6" />
              </span>
              <span className="min-w-0 leading-[1.4]">
                <span className="block text-[17px] font-bold tracking-tight text-white">
                  {SITE_NAME}
                </span>
                <span className="block truncate text-[12px] text-zinc-400">
                  Learning Operations
                </span>
              </span>
            </Link>

            <nav className="flex-1 px-3 py-4" aria-label="เมนูหลัก">
              <p className="eyebrow px-3 pb-2 text-zinc-400">ส่วนงาน</p>
              <ul className="space-y-1">
                {NAV.map((item) => {
                  const active =
                    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
                  const count = counts.queue[item.href];
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        aria-current={active ? "page" : undefined}
                        className={[
                          "flex items-center gap-3 rounded-[8px] border px-3 py-2.5 transition-colors",
                          active
                            ? "border-white bg-card text-ink"
                            : "border-transparent text-zinc-400 hover:border-rail-3 hover:bg-rail-2 hover:text-white",
                        ].join(" ")}
                      >
                        <item.Icon className="h-[18px] w-[18px] shrink-0" />
                        <span className="min-w-0 flex-1 leading-[1.4]">
                          <span
                            className={`block truncate text-[14px] font-semibold ${
                              active ? "text-ink" : "text-zinc-200"
                            }`}
                          >
                            {item.label}
                          </span>
                          <span
                            className={`block truncate text-[12px] ${
                              active ? "text-ink-3" : "text-zinc-400"
                            }`}
                          >
                            {item.caption}
                          </span>
                        </span>
                        {typeof count === "number" && count > 0 ? (
                          <span
                            className={`num shrink-0 rounded-[2px] px-1.5 py-[1px] text-[12px] font-bold ${
                              active ? "bg-wash text-ink" : "bg-rail-3 text-white"
                            }`}
                          >
                            {count}
                          </span>
                        ) : null}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </nav>

            <div className="border-t border-rail-2 px-6 py-4">
              <div className="mb-3 flex items-center justify-between text-[11px] font-semibold tracking-[0.08em] text-zinc-400">
                <span>SKILLSPACE SERVICES</span>
                <span className="rounded-full border border-rail-3 px-2 py-0.5 text-zinc-300">3 สาขา</span>
              </div>
              <p className="flex items-center gap-2 text-[13px] leading-[1.5] text-zinc-400">
                <span
                  className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                    counts.ready ? "bg-ok" : "bg-crit"
                  }`}
                  aria-hidden="true"
                />
                {counts.ready ? "เชื่อมต่อบริการเบื้องหลังแล้ว" : "ติดต่อบริการเบื้องหลังไม่ได้"}
              </p>
            </div>
          </aside>

          {/* ============ เนื้อหา ============ */}
          <div className="flex min-w-0 flex-1 flex-col">
            {/* เมนูสำรองสำหรับจอแคบ — แถบข้างถูกซ่อนต่ำกว่า lg */}
            <header className="flex items-center gap-4 border-b border-rule bg-card px-6 py-2 lg:hidden">
              <span className="text-[15px] font-bold tracking-tight">{SITE_NAME}</span>
              <nav className="flex flex-wrap gap-1 text-[14px]">
                {NAV.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="rounded-[4px] px-2 py-1 font-medium text-ink-2 hover:bg-wash hover:text-ink"
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </header>

            {/* แถบบน 48px — ซ้ายบอกความสดของข้อมูล ขวาเหลือเฉพาะ "สัญญาณที่ต้องลงมือ" สองตัว
                (ไม่ใช่ตัวเลขทั้งสี่ตัว เพราะจะไปซ้ำกับ hero ของหน้าสรุป) */}
            <div className="hidden h-14 shrink-0 items-center justify-between border-b border-rule bg-card px-8 lg:flex">
              <div className="flex items-center gap-3 text-[13px]">
                <span className="font-semibold tracking-[0.08em] text-ink">OPERATIONS CONSOLE</span>
                <span className="h-4 w-px bg-rule-strong" aria-hidden="true" />
                <span className="text-ink-3">
                  ข้อมูล ณ <span className="num font-medium text-ink-2">{stamp} น.</span>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <AlertLink
                  href="/tickets"
                  label="เกินกำหนด"
                  value={counts.overdue}
                  unit="ใบ"
                  zero="ไม่มีงานเกินกำหนด"
                />
                <AlertLink
                  href="/parts"
                  label="อะไหล่ต่ำ"
                  value={counts.partsLow}
                  unit="รายการ"
                  zero="อะไหล่พอทุกรายการ"
                />
              </div>
            </div>

            <main className="mx-auto w-full max-w-[92rem] flex-1 px-6 py-5 lg:px-8">{children}</main>

            <footer className="mx-auto w-full max-w-[92rem] px-6 pb-5 lg:px-8">
              <p className="border-t border-rule pt-3 text-[13px] text-ink-3">
                {SITE_NAME} · ทุกการกดปุ่มคือ form POST ที่ประมวลผลฝั่งเซิร์ฟเวอร์ ·
                หน้าเว็บคุยกับบริการเบื้องหลังผ่านเครือข่ายภายในของ Docker เท่านั้น
              </p>
            </footer>
          </div>
        </div>
      </body>
    </html>
  );
}

/** สัญญาณเตือนบนแถบบน — มีทั้งไอคอน ตัวเลข และคำ ไม่ได้สื่อด้วยสีอย่างเดียว */
function AlertLink({
  href,
  label,
  value,
  unit,
  zero,
}: {
  href: string;
  label: string;
  value: number;
  unit: string;
  zero: string;
}) {
  if (value === 0) {
    return (
      <span className="inline-flex items-center gap-1 rounded-[2px] border border-rule bg-wash px-2 py-[2px] text-[12px] font-medium text-ink-3">
        <IconCheck className="h-3 w-3" />
        {zero}
      </span>
    );
  }
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-1 rounded-[2px] border border-crit-line bg-crit-wash px-2 py-[2px] text-[12px] font-semibold text-crit-ink transition-colors hover:border-crit hover:bg-card"
    >
      <IconAlert className="h-3 w-3" />
      {label} <span className="num font-bold">{value}</span> {unit}
    </Link>
  );
}
