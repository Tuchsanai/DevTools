import { NextResponse } from "next/server";
import { getSystemStatus } from "../lib/runtime";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(await getSystemStatus());
}
