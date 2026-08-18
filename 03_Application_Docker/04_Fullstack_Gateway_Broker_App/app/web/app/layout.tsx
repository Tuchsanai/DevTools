import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = { title:"ChongJai Café · ชงใจทุกแก้ว", description:"สั่งกาแฟ ดูคิว และติดตามแก้วโปรด" };
const NAV = [{href:"/",label:"สั่งเครื่องดื่ม"},{href:"/orders",label:"คิวลูกค้า"},{href:"/barista",label:"จอบาริสต้า"},{href:"/dashboard",label:"ยอดขาย"}];

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="th"><body className="paper-noise min-h-screen font-sans antialiased">
    <header className="sticky top-0 z-30 border-b border-coffee-900/10 bg-cream-50/90 backdrop-blur-xl"><div className="mx-auto flex max-w-7xl flex-wrap items-center gap-5 px-5 py-3">
      <Link href="/" className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-2xl bg-coffee-900 text-xl text-cream-100 shadow-lg shadow-coffee-900/20">☕</span><span><b className="block text-lg leading-none tracking-tight">ChongJai Café</b><small className="text-[11px] tracking-[.16em] text-coffee-700">ชงใจ · ชงสด · ชงเพื่อคุณ</small></span></Link>
      <nav className="flex flex-1 flex-wrap justify-end gap-1">{NAV.map(item=><Link key={item.href} href={item.href} className="rounded-xl px-3 py-2 text-sm font-semibold text-coffee-700 transition hover:bg-coffee-900 hover:text-cream-50">{item.label}</Link>)}</nav>
    </div></header>
    <main className="mx-auto min-h-[calc(100vh-11rem)] max-w-7xl px-5 py-8">{children}</main>
    <footer className="mx-auto flex max-w-7xl flex-wrap justify-between gap-2 border-t border-coffee-900/10 px-5 py-7 text-xs text-coffee-700"><span>© ChongJai Café · ข้อมูลสดจากหน้าร้านผ่าน Gateway</span><span>SSR + Server Actions · ไม่พึ่ง CDN</span></footer>
  </body></html>;
}
