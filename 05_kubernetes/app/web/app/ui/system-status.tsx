import type { SystemStatus } from "../lib/runtime";

const dot = {
  ok: "bg-ok",
  err: "bg-crit",
  quiet: "bg-zinc-400",
};

export function SystemStatusCard({ status }: { status: SystemStatus }) {
  const apiTone = !status.api.configured ? "quiet" : status.api.reachable ? "ok" : "err";
  const dbTone = status.db.status === "up" ? "ok" : status.db.status === "down" ? "err" : "quiet";

  return (
    <section
      className="mx-auto mt-4 w-[calc(100%-3rem)] max-w-[calc(92rem-4rem)] overflow-hidden rounded-[10px] border border-rule bg-card lg:w-[calc(100%-4rem)]"
      aria-label="สถานะระบบ Kubernetes"
      data-testid="system-status"
    >
      <div className="grid min-h-11 items-center gap-2 border-b border-rule bg-accent-wash px-4 py-2 text-[13px] lg:grid-cols-[72px_1fr_auto]">
        <strong className="uppercase tracking-[0.12em] text-accent">web</strong>
        <span className="min-w-0 text-ink-2">
          ตอบโดย Pod: <b className="font-mono text-ink">{status.pod}</b>
          {status.node ? <span className="text-ink-3"> · Node: {status.node}</span> : null}
        </span>
        <span className="flex flex-wrap items-center gap-2">
          <b className="rounded-[5px] bg-accent px-3 py-1 text-[17px] leading-none text-white">
            {status.version}
          </b>
          <span className="text-ink-3">
            {status.time} · {status.site_name} · theme: <b>{status.theme}</b>
          </span>
        </span>
      </div>
      <StatusRow label="api" tone={apiTone}>
        {!status.api.configured
          ? "โหมดเดี่ยว — ยังไม่ได้เชื่อม API"
          : status.api.reachable
            ? `เชื่อมต่อได้ · Pod: ${status.api.pod || "ไม่ทราบชื่อ"}`
            : `เชื่อมต่อไม่ได้ · ${status.api.error || "API ไม่ตอบสนอง"}`}
      </StatusRow>
      <StatusRow label="db" tone={dbTone} last>
        {status.db.status === "up"
          ? "up · PostgreSQL พร้อมใช้งาน"
          : status.db.status === "down"
            ? `down · ${status.db.error || "ฐานข้อมูลยังไม่พร้อม"}`
            : "unknown · ยังตรวจสอบฐานข้อมูลไม่ได้"}
      </StatusRow>
    </section>
  );
}

function StatusRow({
  label,
  tone,
  last = false,
  children,
}: {
  label: string;
  tone: keyof typeof dot;
  last?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`grid min-h-9 grid-cols-[72px_1fr] items-center gap-2 px-4 py-1.5 text-[13px] ${last ? "" : "border-b border-rule"}`}
    >
      <strong className="uppercase tracking-[0.12em] text-ink-2">{label}</strong>
      <span className="flex min-w-0 items-center gap-2 text-ink-2">
        <span className={`h-2 w-2 shrink-0 rounded-full ${dot[tone]}`} aria-hidden="true" />
        <span className="truncate">{children}</span>
      </span>
    </div>
  );
}
