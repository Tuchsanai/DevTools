import { NextResponse, type NextRequest } from "next/server";

/**
 * ทำหน้าที่เดียว : แปะ path ปัจจุบันไว้ใน header ให้ layout อ่านได้
 *
 * ทำไมต้องมี : layout เป็น server component จึงไม่มี usePathname() ให้ใช้
 * (และเราห้ามมี JavaScript ฝั่ง browser ทั้งโปรเจกต์) — แต่แถบนำทางด้านซ้าย
 * ต้องรู้ว่าตอนนี้อยู่หน้าไหนเพื่อไฮไลต์เมนู จึงส่งค่ามาทาง header แทน
 */
export function middleware(request: NextRequest) {
  const headers = new Headers(request.headers);
  headers.set("x-pathname", request.nextUrl.pathname);
  return NextResponse.next({ request: { headers } });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
