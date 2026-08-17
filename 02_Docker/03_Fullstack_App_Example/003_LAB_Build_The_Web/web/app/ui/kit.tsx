/**
 * ชิ้นส่วน UI ที่ใช้ซ้ำหลายหน้า — ทุกตัวเป็น server component ล้วน
 * ไม่มี "use client" ที่ไหนเลยทั้งโปรเจกต์ (ดูเหตุผลใน app/lib/api.ts)
 */

import type { Priority, TicketStatus } from "../lib/api";

/** แถบข้อความผลลัพธ์หลังกดปุ่ม — รับค่ามาจาก query string ที่ server action เด้งกลับมา */
export function Flash({ tone, message }: { tone?: string; message?: string }) {
  if (!message) return null;
  const ok = tone === "ok";
  return (
    <div
      role="status"
      className={[
        "animate-rise mb-6 flex items-start gap-3 rounded-2xl border px-4 py-3 text-sm backdrop-blur",
        ok
          ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-100"
          : "border-rose-400/30 bg-rose-400/10 text-rose-100",
      ].join(" ")}
    >
      <span className="mt-0.5 text-base leading-none">{ok ? "✓" : "!"}</span>
      <p className="leading-relaxed">{message}</p>
    </div>
  );
}

/** กล่องพื้นฐานโทนมืด ใช้เป็นฐานของทุกการ์ดในระบบ */
export function Panel({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-2xl border border-white/8 bg-ink-900/70 shadow-[0_1px_0_rgba(255,255,255,0.04)_inset,0_18px_40px_-24px_rgba(0,0,0,0.9)] backdrop-blur ${className}`}
    >
      {children}
    </section>
  );
}

export function PanelHead({
  title,
  hint,
  right,
}: {
  title: string;
  hint?: string;
  right?: React.ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-3 border-b border-white/8 px-5 py-4">
      <div>
        <h2 className="text-base font-semibold tracking-tight text-slate-100">{title}</h2>
        {hint ? <p className="mt-0.5 text-xs text-slate-400">{hint}</p> : null}
      </div>
      {right}
    </header>
  );
}

// ---------- ป้ายและสี ----------

export const PRIORITY_LABEL: Record<Priority, string> = {
  HIGH: "เร่งด่วน",
  NORMAL: "ปกติ",
  LOW: "ไม่เร่ง",
};

/** สีตามความเร่งด่วน — เก็บไว้ที่เดียว ทั้งแถบข้างการ์ดและป้ายใช้ชุดเดียวกัน */
export const PRIORITY_STYLE: Record<Priority, { bar: string; chip: string }> = {
  HIGH: { bar: "bg-rose-500", chip: "border-rose-400/40 bg-rose-500/15 text-rose-200" },
  NORMAL: { bar: "bg-amber-400", chip: "border-amber-300/40 bg-amber-400/15 text-amber-100" },
  LOW: { bar: "bg-sky-400", chip: "border-sky-300/40 bg-sky-400/15 text-sky-100" },
};

export const STATUS_LABEL: Record<TicketStatus, string> = {
  NEW: "รอรับเรื่อง",
  ASSIGNED: "มอบหมายแล้ว",
  IN_PROGRESS: "กำลังซ่อม",
  DONE: "ปิดงานแล้ว",
};

export const STATUS_ACCENT: Record<TicketStatus, string> = {
  NEW: "bg-slate-400",
  ASSIGNED: "bg-violet-400",
  IN_PROGRESS: "bg-brand-400",
  DONE: "bg-emerald-400",
};

export function Chip({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium ${className}`}
    >
      {children}
    </span>
  );
}

// ---------- ฟอร์ม ----------

export const inputClass =
  "w-full rounded-xl border border-white/10 bg-ink-950/70 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand-400/60 focus:ring-2 focus:ring-brand-400/25";

export const labelClass = "mb-1 block text-xs font-medium text-slate-400";

export const buttonClass =
  "inline-flex items-center justify-center gap-1.5 rounded-xl bg-brand-500 px-3.5 py-2 text-sm font-semibold text-ink-950 transition hover:bg-brand-400 active:translate-y-px";

export const ghostButtonClass =
  "inline-flex items-center justify-center gap-1.5 rounded-xl border border-white/12 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-white/25 hover:bg-white/10 active:translate-y-px";

// ---------- ตัวช่วยเรื่องเวลา ----------

/** จำนวนวันเต็มที่ผ่านมาแล้วนับจากเวลาที่ให้มา (ปัดลง เหมือนที่ API คำนวณ days_open) */
export function daysSince(iso: string): number {
  const ms = Date.now() - new Date(iso).getTime();
  return Math.floor(ms / 86_400_000);
}

/** แสดงวันที่แบบสั้นเป็นภาษาไทย — เลือก timeZone ตายตัวเพื่อให้ server/ผู้ดูเห็นตรงกัน */
export function thaiDate(iso: string | null): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("th-TH", {
    day: "numeric",
    month: "short",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Bangkok",
  }).format(new Date(iso));
}

/**
 * แถบสัดส่วน "ยอดคงเหลือเทียบจุดสั่งซื้อ"
 * สเกลของแถบ = 2 เท่าของจุดสั่งซื้อ เพื่อให้ขีดจุดสั่งซื้ออยู่กลางแถบพอดีเสมอ
 * มองปราดเดียวรู้ทันทีว่าอยู่ซ้าย (ต่ำกว่าจุดสั่งซื้อ) หรือขวาของขีด
 */
export function StockBar({
  qty,
  reorder,
  below,
}: {
  qty: number;
  reorder: number;
  below: boolean;
}) {
  const scale = Math.max(reorder * 2, qty, 1);
  const fill = Math.min(100, Math.round((qty / scale) * 100));
  const mark = Math.min(100, Math.round((reorder / scale) * 100));
  return (
    <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-white/8">
      <div
        className={`h-full rounded-full transition-all ${
          below ? "bg-gradient-to-r from-rose-500 to-rose-400" : "bg-gradient-to-r from-brand-500 to-emerald-400"
        }`}
        style={{ width: `${fill}%` }}
      />
      {/* ขีดบอกจุดสั่งซื้อ */}
      <div
        className="absolute top-0 h-full w-0.5 bg-white/70"
        style={{ left: `${mark}%` }}
        aria-hidden="true"
      />
    </div>
  );
}
