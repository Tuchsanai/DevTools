import os from "node:os";

export const THEMES = ["blue", "emerald", "amber", "rose", "violet", "slate"] as const;
export type Theme = (typeof THEMES)[number];

export type SystemStatus = {
  pod: string;
  version: string;
  theme: Theme;
  site_name: string;
  time: string;
  node?: string;
  api: { configured: boolean; reachable: boolean; pod?: string; error?: string };
  db: { status: "up" | "down" | "unknown"; error?: string };
};

function short(value: unknown, limit = 120): string {
  const text = value instanceof Error ? value.message : String(value);
  const oneLine = text.replace(/\s+/g, " ").trim() || "unknown error";
  return oneLine.length <= limit ? oneLine : `${oneLine.slice(0, limit - 1)}…`;
}

export function runtimeConfig() {
  const fallback = process.env.DEFAULT_THEME ?? "blue";
  const requested = process.env.THEME ?? fallback;
  const theme = (THEMES as readonly string[]).includes(requested)
    ? (requested as Theme)
    : "blue";
  return {
    pod: process.env.POD_NAME || os.hostname(),
    node: process.env.NODE_NAME || undefined,
    version: process.env.APP_VERSION || "v1",
    theme,
    siteName: process.env.SITE_NAME || "SkillSpace",
    apiBaseUrl: process.env.API_BASE_URL?.replace(/\/$/, "") || undefined,
  };
}

export function bangkokTime(): string {
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: "Asia/Bangkok",
  }).format(new Date());
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const config = runtimeConfig();
  const base: Omit<SystemStatus, "api" | "db"> = {
    pod: config.pod,
    version: config.version,
    theme: config.theme,
    site_name: config.siteName,
    time: bangkokTime(),
    ...(config.node ? { node: config.node } : {}),
  };

  if (!config.apiBaseUrl) {
    return {
      ...base,
      api: { configured: false, reachable: false },
      db: { status: "unknown" },
    };
  }

  try {
    const response = await fetch(`${config.apiBaseUrl}/ready`, {
      cache: "no-store",
      signal: AbortSignal.timeout(1800),
    });
    const body = (await response.json().catch(() => ({}))) as {
      pod?: string;
      db?: "up" | "down";
      error?: string;
      detail?: string;
    };
    const pod = response.headers.get("x-pod-name") || body.pod;
    const error = body.error || body.detail;
    return {
      ...base,
      api: { configured: true, reachable: true, ...(pod ? { pod } : {}) },
      db: {
        status: body.db === "up" ? "up" : "down",
        ...(!response.ok || error ? { error: short(error || `HTTP ${response.status}`) } : {}),
      },
    };
  } catch (error) {
    return {
      ...base,
      api: { configured: true, reachable: false, error: short(error) },
      db: { status: "unknown" },
    };
  }
}

export async function apiHealthIsReady(): Promise<boolean> {
  const { apiBaseUrl } = runtimeConfig();
  if (!apiBaseUrl) return true;
  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(1800),
    });
    return response.ok;
  } catch {
    return false;
  }
}
