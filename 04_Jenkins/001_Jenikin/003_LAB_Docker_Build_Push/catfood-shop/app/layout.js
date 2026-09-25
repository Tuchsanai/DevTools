import './globals.css';

export const metadata = {
  title: 'Meow Mart — ร้านอาหารแมว',
  description: 'อาหารแมวคุณภาพ คัดสรรเพื่อเจ้านายตัวน้อย',
};

export default function RootLayout({ children }) {
  return (
    <html lang="th">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Mitr:wght@400;500;600&family=Sarabun:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
