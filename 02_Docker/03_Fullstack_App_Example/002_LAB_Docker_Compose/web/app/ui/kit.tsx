/**
 * ชิ้นส่วน UI ที่ใช้ซ้ำทั้งระบบ — server component ล้วนทุกตัว
 * ไม่มี "use client" ที่ไหนเลยทั้งโปรเจกต์ (เหตุผลอยู่ใน app/lib/api.ts)
 *
 * กติกาของระบบออกแบบ (ค่าตัวแปรทั้งหมดอยู่ใน globals.css ที่เดียว)
 *   สเกลระยะ   4 · 8 · 12 · 16 · 24 · 32 · 48 เท่านั้น
 *   สเกลอักษร  11 · 12 · 13 · 14 · 15 · 17 · 22 · 28 · 48 เท่านั้น (9 ขั้น)
 *   มุมโค้ง    4px (ป้าย) · 8px (ช่องกรอก/ปุ่ม) · 10px (แผง) — ตามลำดับชั้นของพื้นที่
 *   เส้น       1px ทุกที่ · 2px เฉพาะใต้ header ของหน้า และเส้นบนแถวรวมของตาราง
 *   เงา        ไม่มีทั้งระบบ — ยกระดับด้วยเส้นและระนาบพื้นผิวเท่านั้น
 */

import Link from "next/link";
import type { Asset, Priority, TicketStatus } from "../lib/api";
import {
  IconAlert,
  IconArrow,
  IconCheck,
  IconDot,
  IconHandoff,
  IconWrench,
} from "./icons";

/* ==================================================================
   1. แถบผลลัพธ์ของ server action
   ================================================================== */

/**
 * ข้อความจาก lib/api.ts มาในรูป "ประโยคไทย [ERROR_CODE]"
 * เจ้าหน้าที่ที่ไม่ใช่ IT ต้องอ่านประโยคไทยรู้เรื่องก่อน ส่วนรหัสเป็นของผู้สอน/ผู้ดูแล
 * จึงแยกรหัสออกมาวางเป็น <code> ตัวเล็กท้ายบรรทัด แทนที่จะปนอยู่กลางประโยค
 */
function splitCode(message: string): { text: string; code: string | null } {
  const matched = message.match(/^(.*?)\s*\[([A-Z0-9_]+)\]\s*$/);
  return matched ? { text: matched[1], code: matched[2] } : { text: message, code: null };
}

export function Flash({ tone, message }: { tone?: string; message?: string }) {
  if (!message) return null;
  const ok = tone === "ok";
  const { text, code } = splitCode(message);
  return (
    <div
      role="status"
      className={[
        "mb-4 flex items-start gap-2 rounded border border-l-[3px] px-4 py-3 text-[14px]",
        ok
          ? "border-ok-line border-l-ok bg-ok-wash"
          : "border-crit-line border-l-crit bg-crit-wash",
      ].join(" ")}
    >
      <span className={`mt-[3px] shrink-0 ${ok ? "text-ok-ink" : "text-crit-ink"}`}>
        {ok ? <IconCheck className="h-4 w-4" /> : <IconAlert className="h-4 w-4" />}
      </span>
      <p className="min-w-0 leading-[1.55] text-ink">
        <span className={`font-semibold ${ok ? "text-ok-ink" : "text-crit-ink"}`}>
          {ok ? "สำเร็จ · " : "ทำรายการไม่ได้ · "}
        </span>
        {text}
        {code ? (
          <code className="ml-2 font-mono text-[11px] tracking-wide text-ink-3">{code}</code>
        ) : null}
      </p>
    </div>
  );
}

/* ==================================================================
   2. โครงของหน้า
   ================================================================== */

/**
 * หัวเรื่องของหน้า — ลำดับชั้นเดียวกันทุกหน้า : eyebrow 11 → H1 28 → เส้นดำ 2px
 * ไม่มีย่อหน้าอธิบายใต้ H1 โดยตั้งใจ (คำอธิบายไปอยู่ใต้หัวแผงที่มันเกี่ยวข้องจริง ๆ)
 * เพราะหน้านี้ถูกเปิดวันละหลายรอบ คนใช้ไม่ได้มาอ่านคำอธิบายซ้ำทุกครั้ง
 */
export function PageHead({
  eyebrow,
  title,
  right,
}: {
  eyebrow: string;
  title: string;
  right?: React.ReactNode;
}) {
  return (
    <header className="mb-4 flex flex-wrap items-end justify-between gap-4 border-b-2 border-ink pb-2">
      <div className="min-w-0">
        <p className="eyebrow">{eyebrow}</p>
        <h1 className="mt-1 text-[28px] leading-[1.3] font-bold tracking-tight text-ink">
          {title}
        </h1>
      </div>
      {right ? <div className="shrink-0 pb-1">{right}</div> : null}
    </header>
  );
}

/** แผงข้อมูล — ขอบ 1px ไม่มีเงา เพื่อให้กลมกลืนกับภาษาภาพของสไลด์ */
export function Panel({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-[10px] border border-rule bg-card ${className}`}>{children}</section>
  );
}

export function PanelHead({
  title,
  sub,
  right,
}: {
  title: string;
  sub?: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <header className="flex items-start justify-between gap-4 border-b border-rule px-6 py-3">
      <div className="min-w-0 flex-1">
        <h2 className="text-[17px] leading-[1.4] font-semibold tracking-tight text-ink">
          {title}
        </h2>
        {sub ? <p className="mt-0.5 text-[13px] leading-[1.5] text-ink-3">{sub}</p> : null}
      </div>
      {right ? <div className="shrink-0 pt-0.5">{right}</div> : null}
    </header>
  );
}

/** สภาวะว่าง — ต้องเขียนว่า "แปลว่าอะไร" ไม่ใช่แค่ "ไม่มีข้อมูล" */
export function Empty({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="px-6 py-8 text-center">
      <p className="text-[14px] font-medium text-ink-2">{title}</p>
      {hint ? (
        <p className="mx-auto mt-1 max-w-md text-[13px] leading-[1.5] text-ink-3">{hint}</p>
      ) : null}
    </div>
  );
}

export function EmptyRow({
  colSpan,
  title,
  hint,
}: {
  colSpan: number;
  title: string;
  hint?: string;
}) {
  return (
    <tr>
      <td colSpan={colSpan}>
        <Empty title={title} hint={hint} />
      </td>
    </tr>
  );
}

/** ลิงก์ท้ายแผง — accent ใช้ได้ที่นี่เพราะเป็น "ลิงก์" (1 ใน 4 ที่ที่อนุญาต) */
export function FootLink({ href, label }: { href: string; label: string }) {
  return (
    <div className="mt-auto border-t border-rule px-6 py-2">
      <Link
        href={href}
        className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-accent transition-colors hover:text-ink"
      >
        {label}
        <IconArrow className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}

/* ==================================================================
   3. ระบบ badge — ทุกตัวมี "ขอบ 1px + พื้น + ไอคอน + คำ"
      ไม่มี badge ตัวไหนในระบบที่สื่อความหมายด้วยสีเพียงอย่างเดียว
   ================================================================== */

export type Tone = "neutral" | "quiet" | "ok" | "warn" | "crit" | "accent";

const TONE_CLASS: Record<Tone, string> = {
  neutral: "border-rule-strong bg-wash text-ink-2",
  quiet: "border-rule bg-wash text-ink-3",
  ok: "border-ok-line bg-ok-wash text-ok-ink",
  warn: "border-warn-line bg-warn-wash text-warn-ink",
  crit: "border-crit-line bg-crit-wash text-crit-ink",
  accent: "border-accent-line bg-accent-wash text-accent",
};

export function Badge({
  tone = "neutral",
  icon,
  children,
  className = "",
}: {
  tone?: Tone;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-[4px] border px-1.5 py-[1px] text-[12px] leading-[1.5] font-medium whitespace-nowrap ${TONE_CLASS[tone]} ${className}`}
    >
      {icon ? <span className="shrink-0">{icon}</span> : null}
      {children}
    </span>
  );
}

/* ---------- ความเร่งด่วน : "ย้อมระดับเดียว" ----------
   ถ้าย้อมครบสามระดับ สีแดงจะเลิกหมายความว่าอะไร
   → เร่งด่วนเท่านั้นที่ได้สีวิกฤต · ปกติ/ไม่เร่งเป็น badge กลาง แยกกันด้วยคำ */
export const PRIORITY_LABEL: Record<Priority, string> = {
  HIGH: "เร่งด่วน",
  NORMAL: "ปกติ",
  LOW: "ไม่เร่ง",
};

const PRIORITY_TONE: Record<Priority, Tone> = {
  HIGH: "crit",
  NORMAL: "neutral",
  LOW: "quiet",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <Badge
      tone={PRIORITY_TONE[priority]}
      icon={
        priority === "HIGH" ? (
          <IconAlert className="h-3 w-3" />
        ) : (
          <IconDot className="h-2.5 w-2.5" />
        )
      }
    >
      {PRIORITY_LABEL[priority]}
    </Badge>
  );
}

/* ---------- ขั้นของใบแจ้งซ่อม : ordinal ramp สีเดียว ---------- */
export const STATUS_LABEL: Record<TicketStatus, string> = {
  NEW: "รอรับเรื่อง",
  ASSIGNED: "มอบหมายแล้ว",
  IN_PROGRESS: "กำลังซ่อม",
  DONE: "ปิดงานแล้ว",
};

export const STATUS_HINT: Record<TicketStatus, string> = {
  NEW: "รอหัวหน้ามอบหมาย",
  ASSIGNED: "ช่างรับแล้ว ยังไม่เริ่ม",
  IN_PROGRESS: "ช่างกำลังลงมือ",
  DONE: "ปิดพร้อมตัดอะไหล่แล้ว",
};

export const STATUS_HEX: Record<TicketStatus, string> = {
  NEW: "#86b6ef",
  ASSIGNED: "#5598e7",
  IN_PROGRESS: "#2a78d6",
  DONE: "#1c5cab",
};

/* ---------- สถานะครุภัณฑ์ (ค่าที่คำนวณ ไม่ใช่คอลัมน์ในฐานข้อมูล) ---------- */
export const ASSET_LABEL: Record<Asset["status"], string> = {
  AVAILABLE: "พร้อมให้ยืม",
  ON_LOAN: "ถูกยืมอยู่",
  IN_REPAIR: "อยู่ระหว่างซ่อม",
};

const ASSET_TONE: Record<Asset["status"], Tone> = {
  AVAILABLE: "ok",
  ON_LOAN: "accent",
  IN_REPAIR: "warn",
};

/** สีของท่อนในแถบสัดส่วนครุภัณฑ์ — "ว่าง" เป็นสีกลาง เพราะไม่ใช่เรื่องที่ต้องสังเกต */
export const ASSET_HEX: Record<Asset["status"], string> = {
  AVAILABLE: "#d4d4d8",
  ON_LOAN: "#2a78d6",
  IN_REPAIR: "#fab219",
};

export function AssetBadge({ status }: { status: Asset["status"] }) {
  const icon =
    status === "AVAILABLE" ? (
      <IconCheck className="h-3 w-3" />
    ) : status === "ON_LOAN" ? (
      <IconHandoff className="h-3 w-3" />
    ) : (
      <IconWrench className="h-3 w-3" />
    );
  return (
    <Badge tone={ASSET_TONE[status]} icon={icon}>
      {ASSET_LABEL[status]}
    </Badge>
  );
}

/* ==================================================================
   4. ฟอร์ม — คลาสชุดเดียวใช้ทั้งระบบ
   ================================================================== */

export const labelClass = "mb-1 block text-[11px] font-semibold tracking-[0.12em] text-ink-3";

export const inputClass =
  "h-9 w-full rounded-[8px] border border-rule-strong bg-card px-2.5 text-[14px] text-ink outline-none transition-colors placeholder:text-ink-3 hover:border-zinc-400 focus:border-accent";

export const buttonClass =
  "inline-flex h-9 items-center justify-center gap-1.5 rounded-[8px] border border-accent bg-accent px-4 text-[14px] font-semibold text-white transition-colors hover:border-ink hover:bg-ink";

export const ghostButtonClass =
  "inline-flex h-9 items-center justify-center gap-1.5 rounded-[8px] border border-rule-strong bg-card px-3 text-[14px] font-medium text-ink-2 transition-colors hover:bg-wash hover:text-ink";

export const smallButtonClass =
  "inline-flex h-8 items-center justify-center gap-1.5 rounded-[8px] border border-accent bg-accent px-3 text-[13px] font-semibold text-white transition-colors hover:border-ink hover:bg-ink";

export const smallGhostClass =
  "inline-flex h-8 items-center justify-center gap-1.5 rounded-[8px] border border-rule-strong bg-card px-2.5 text-[13px] font-medium text-ink-2 transition-colors hover:bg-wash hover:text-ink";

/* ==================================================================
   5. ตาราง — คลาสร่วม (หัวคอลัมน์เป็น eyebrow · ตัวเลขชิดขวาเสมอ)
   ================================================================== */

export const thClass =
  "border-b border-rule-strong bg-wash px-4 py-2 text-left text-[11px] font-semibold tracking-[0.12em] whitespace-nowrap text-ink-3";

export const thNumClass = `${thClass} text-right`;

export const trClass = "border-b border-rule transition-colors last:border-0 hover:bg-wash";

export const tdClass = "px-4 py-2 align-middle text-[14px] text-ink-2";

export const tdNumClass = `${tdClass} num text-right font-semibold text-ink`;

/* ==================================================================
   6. ตัวช่วยเรื่องเวลา
   ================================================================== */

/** จำนวนวันเต็มที่ผ่านมาแล้ว — ปัดลง ให้ตรงกับวิธีที่ API คำนวณ days_open */
export function daysSince(iso: string): number {
  return Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
}

/** ตรึง timeZone ไว้เสมอ ไม่งั้น server กับผู้ดูหน้าจออาจเห็นวันคนละวัน */
export function thaiDate(iso: string | null): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("th-TH", {
    day: "numeric",
    month: "short",
    year: "2-digit",
    timeZone: "Asia/Bangkok",
  }).format(new Date(iso));
}

export function thaiDateTime(iso: string | null): string {
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

/* ==================================================================
   7. ชิ้นส่วนนำเสนอตัวเลข
   ================================================================== */

/**
 * ตัวเลขนำของหน้า — หน้าละ 1 ตัวเท่านั้น
 * ใช้สัดส่วนตัวอักษรจริง (ไม่ tabular) เพราะไม่ได้เรียงเทียบกับตัวเลขอื่น
 */
export function Hero({
  label,
  value,
  unit,
  note,
}: {
  label: string;
  value: number | string;
  unit: string;
  note?: React.ReactNode;
}) {
  return (
    <div className="px-6 py-4">
      <p className="eyebrow">{label}</p>
      <p className="mt-1 flex items-baseline gap-1.5">
        <span className="text-[48px] leading-[1.05] font-bold tracking-tight text-ink">
          {value}
        </span>
        <span className="text-[13px] font-medium text-ink-3">{unit}</span>
      </p>
      {note ? <p className="mt-1 text-[13px] leading-[1.5] text-ink-3">{note}</p> : null}
    </div>
  );
}

/** ตัวเลขรอง — เล็กกว่า hero หนึ่งขั้นชัดเจน จึงไม่แย่งสายตากับตัวเลขนำ */
export function MiniStat({
  label,
  note,
  value,
  unit,
  tone = "ink",
}: {
  label: string;
  note: string;
  value: number | string;
  unit: string;
  tone?: "ink" | "crit";
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-t border-rule px-6 py-2">
      <div className="min-w-0">
        <p className="text-[14px] font-semibold text-ink">{label}</p>
        <p className="truncate text-[12px] text-ink-3">{note}</p>
      </div>
      <p className="shrink-0">
        <span
          className={`num text-[22px] leading-none font-bold ${
            tone === "crit" ? "text-crit-ink" : "text-ink"
          }`}
        >
          {value}
        </span>
        <span className="ml-1 text-[12px] font-medium text-ink-3">{unit}</span>
      </p>
    </div>
  );
}

export type Segment = { key: string; label: string; value: number; hex: string };

/**
 * แถบสัดส่วนรวม — ช่องว่างสีพื้น 2px คั่นทุกท่อน (ใช้ที่ว่างคั่น ไม่ใช้เส้นขอบ)
 * ตัวเลขจำนวนอยู่ "ในท่อน" ที่เดียว → legend ใต้แถบจึงบอกแค่ชื่อขั้นกับสัดส่วน ไม่พิมพ์ซ้ำ
 */
/**
 * เลือกสีตัวอักษรในท่อนแถบด้วยการคำนวณค่าความสว่างจริง ไม่ใช่เดาจากสายตา
 * (ท่อน #5598e7 ดูเข้มแต่ตัวขาวบนพื้นนี้ได้แค่ 3.1:1 — ต้องใช้หมึกดำถึงจะผ่าน)
 */
function readableOn(hex: string): string {
  const channel = (v: number) => {
    const c = v / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  const r = channel(parseInt(hex.slice(1, 3), 16));
  const g = channel(parseInt(hex.slice(3, 5), 16));
  const b = channel(parseInt(hex.slice(5, 7), 16));
  const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  const onWhite = 1.05 / (lum + 0.05);
  const onInk = (lum + 0.05) / (0.0085 + 0.05);
  return onInk >= onWhite ? "text-ink" : "text-white";
}

/**
 * แถบสัดส่วนรวม — ช่องว่างสีพื้น 2px คั่นทุกท่อน (ใช้ที่ว่างคั่น ไม่ใช้เส้นขอบ)
 * แบบสูง (showValue) ใส่จำนวนไว้ในท่อน → legend ใต้แถบจึงบอกแค่ชื่อกับสัดส่วน ไม่พิมพ์ซ้ำ
 * แบบเตี้ยใช้เป็นแถบอ้างอิงข้าง legend เท่านั้น
 */
export function ShareBar({
  segments,
  height = 36,
  showValue = true,
}: {
  segments: Segment[];
  height?: number;
  showValue?: boolean;
}) {
  const total = segments.reduce((sum, s) => sum + s.value, 0) || 1;
  return (
    <div
      className="flex w-full gap-[2px] overflow-hidden rounded-[2px]"
      style={{ height }}
      role="img"
      aria-label={segments.map((s) => `${s.label} ${s.value}`).join(" · ")}
    >
      {segments
        .filter((s) => s.value > 0)
        .map((s) => {
          const pct = (s.value / total) * 100;
          // ท่อนที่แคบกว่า 11% ใส่ตัวเลขไม่ลง จะถูกตัดขอบ — ปล่อยให้ legend ทำหน้าที่แทน
          return (
            <div
              key={s.key}
              className="flex items-center justify-center"
              style={{ width: `${pct}%`, backgroundColor: s.hex }}
            >
              {showValue && pct >= 11 ? (
                <span className={`num text-[13px] font-bold ${readableOn(s.hex)}`}>{s.value}</span>
              ) : null}
            </div>
          );
        })}
    </div>
  );
}

/** คำอธิบายใต้แถบ — จุดสี + ชื่อ + สัดส่วน % (จำนวนอยู่ในแถบแล้ว ไม่พิมพ์ซ้ำ) */
export function Legend({ segments }: { segments: Segment[] }) {
  const total = segments.reduce((sum, s) => sum + s.value, 0) || 1;
  return (
    <ul className="flex flex-wrap gap-x-6 gap-y-1">
      {segments.map((s) => (
        <li key={s.key} className="flex items-baseline gap-2 text-[13px]">
          <span
            className="h-2.5 w-2.5 shrink-0 translate-y-[1px] rounded-[2px]"
            style={{ backgroundColor: s.hex }}
            aria-hidden="true"
          />
          <span className="text-ink-2">{s.label}</span>
          <span className="num font-semibold text-ink">
            {Math.round((s.value / total) * 100)}%
          </span>
        </li>
      ))}
    </ul>
  );
}

/**
 * แถบ "ค้างกี่วัน เทียบกำหนด" (REQ-09)
 * ท่อนเทา = ช่วงที่ยังอยู่ในกำหนด · ท่อนแดง = ส่วนที่สายไปจริง ๆ · คั่นด้วยช่องว่างสีพื้น 2px
 * ขีดดำที่เส้นกำหนดมีขอบสีพื้นข้างละ 2px จึงไม่จมหายไปในแถบ
 * → "สายแค่ไหน" อ่านจากความยาวท่อนแดงตรง ๆ ไม่ต้องเทียบระยะกับขีดเอง
 */
export function OverdueBar({ days, sla, scale }: { days: number; sla: number; scale: number }) {
  const max = Math.max(scale, sla, days, 1);
  const within = Math.min(100, (Math.min(days, sla) / max) * 100);
  const over = Math.max(0, Math.min(100, (days / max) * 100) - within);
  const mark = Math.min(100, (sla / max) * 100);
  return (
    <div className="relative h-2 w-full rounded-[2px] bg-wash">
      <div className="flex h-full">
        <div
          className="h-full rounded-l-[2px] bg-rule-strong"
          style={{ width: `${within}%` }}
        />
        {over > 0 ? <div className="h-full w-[2px] shrink-0 bg-card" /> : null}
        <div className="h-full rounded-r-[2px] bg-crit" style={{ width: `${over}%` }} />
      </div>
      <span
        className="absolute top-[-3px] h-[14px] w-[7px] border-x-2 border-card bg-ink"
        style={{ left: `calc(${mark}% - 3.5px)` }}
        aria-hidden="true"
      />
    </div>
  );
}

/**
 * มาตรวัดยอดคงเหลือเทียบจุดสั่งซื้อ (REQ-12)
 * สเกล = จุดสั่งซื้อ × 2 เสมอ → ขีดจุดสั่งซื้ออยู่กึ่งกลางรางทุกแถว
 * กวาดตาลงคอลัมน์แล้วเห็นทันทีว่าแถวไหนสั้นกว่าครึ่ง = แถวที่ต้องสั่งเพิ่ม
 * แถวปกติใช้สี accent (เงียบ) ไม่ใช้เขียว — ไม่งั้นแถวปกติจะแย่งสายตาไปจากแถวที่ต้องลงมือ
 */
export function StockMeter({
  qty,
  reorder,
  below,
}: {
  qty: number;
  reorder: number;
  below: boolean;
}) {
  const scale = Math.max(reorder * 2, 1);
  const fill = Math.min(100, (qty / scale) * 100);
  return (
    <div className={`relative h-2 w-full rounded-[2px] ${below ? "bg-crit-wash" : "bg-accent-wash"}`}>
      <div
        className={`h-full rounded-[2px] ${below ? "bg-crit" : "bg-accent-2"}`}
        style={{ width: `${fill}%` }}
      />
      <span
        className="absolute top-[-3px] left-[calc(50%-3.5px)] h-[14px] w-[7px] border-x-2 border-card bg-ink"
        aria-hidden="true"
      />
    </div>
  );
}
