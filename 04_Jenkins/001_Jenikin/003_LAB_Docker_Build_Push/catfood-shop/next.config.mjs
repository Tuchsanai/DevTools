/** @type {import('next').NextConfig} */
const nextConfig = {
  // สร้างโฟลเดอร์ .next/standalone ที่มีเฉพาะไฟล์ที่ server ต้องใช้ → image เล็กลงมาก
  output: 'standalone',
  poweredByHeader: false,
};

export default nextConfig;
