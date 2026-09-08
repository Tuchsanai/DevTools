import { NextResponse, type NextRequest } from "next/server";

/** ส่ง path ปัจจุบันให้ server layout เพื่อไฮไลต์เมนูโดยไม่ใช้ client JavaScript. */
export function proxy(request: NextRequest) {
  const headers = new Headers(request.headers);
  headers.set("x-pathname", request.nextUrl.pathname);
  return NextResponse.next({ request: { headers } });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
