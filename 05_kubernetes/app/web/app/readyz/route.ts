import { NextResponse } from "next/server";
import { apiHealthIsReady, runtimeConfig } from "../lib/runtime";

export const dynamic = "force-dynamic";

export async function GET() {
  const config = runtimeConfig();
  const ready = await apiHealthIsReady();
  return NextResponse.json(
    { status: ready ? "ready" : "not-ready", pod: config.pod, version: config.version },
    { status: ready ? 200 : 503 },
  );
}
