import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

// NEXT_PUBLIC_* ถูกฝังเป็นค่าคงที่ตอน build (ARG → ENV ใน Dockerfile)
// ต่างจาก API_BASE_URL ที่อ่านตอนรัน — เปลี่ยนได้โดยไม่ต้อง build ใหม่
const SITE_NAME = process.env.NEXT_PUBLIC_SITE_NAME || "CampusOps";

export const metadata: Metadata = {
  title: `${SITE_NAME} · ระบบงานซ่อมและครุภัณฑ์`,
  description: "ระบบแจ้งซ่อม ยืม-คืนครุภัณฑ์ และคลังอะไหล่ ของสำนักงานคณะ",
};

const NAV = [
  { href: "/", label: "สรุปภาพรวม" },
  { href: "/tickets", label: "กระดานงานซ่อม" },
  { href: "/loans", label: "ยืม-คืนครุภัณฑ์" },
  { href: "/parts", label: "คลังอะไหล่" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body className="min-h-screen font-sans antialiased">
        <header className="sticky top-0 z-20 border-b border-white/8 bg-ink-950/80 backdrop-blur-xl">
          <div className="mx-auto flex max-w-[92rem] flex-wrap items-center gap-x-6 gap-y-3 px-5 py-3.5">
            <Link href="/" className="flex items-center gap-2.5">
              {/* โลโก้วาดด้วย SVG ในไฟล์ ไม่ดึงไอคอนจาก CDN */}
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-400 to-violet-500 text-ink-950 shadow-lg shadow-brand-500/20">
                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M3 20h18" />
                  <path d="M6 20V9l6-5 6 5v11" />
                  <path d="M10 20v-5h4v5" />
                </svg>
              </span>
              <span className="leading-tight">
                <span className="block text-sm font-bold tracking-tight text-slate-50">{SITE_NAME}</span>
                <span className="block text-[11px] text-slate-400">สำนักงานคณะเทคโนโลยีสารสนเทศ</span>
              </span>
            </Link>

            <nav className="flex flex-wrap items-center gap-1 text-sm">
              {NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-lg px-3 py-1.5 font-medium text-slate-300 transition hover:bg-white/8 hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            <span className="ml-auto hidden items-center gap-2 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1 text-[11px] font-medium text-emerald-200 sm:inline-flex">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              เรนเดอร์ฝั่งเซิร์ฟเวอร์ทั้งหมด
            </span>
          </div>
        </header>

        <main className="mx-auto max-w-[92rem] px-5 py-8">{children}</main>

        <footer className="mx-auto max-w-[92rem] px-5 pb-10 text-xs text-slate-500">
          {SITE_NAME} · หน้าเว็บนี้คุยกับบริการเบื้องหลังผ่านเครือข่ายภายในของ Docker เท่านั้น
        </footer>
      </body>
    </html>
  );
}
