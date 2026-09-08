import { NextResponse } from "next/server";
import { runtimeConfig } from "../lib/runtime";

export const dynamic = "force-dynamic";

export function GET() {
  const config = runtimeConfig();
  return NextResponse.json({ status: "ok", pod: config.pod, version: config.version });
}
