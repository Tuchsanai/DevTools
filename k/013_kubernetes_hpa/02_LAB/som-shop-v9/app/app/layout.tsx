import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: process.env.SHOP_NAME ?? 'ร้านอาหารแมวน้องส้ม',
  description: 'แอปตัวอย่าง LAB Kubernetes Service: web หลาย Pod + db กลาง',
  icons: { icon: '/som.png' },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  );
}
