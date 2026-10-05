/** @type {import('next').NextConfig} */
const nextConfig = {
  // สร้างโฟลเดอร์ .next/standalone ที่มี server.js + node_modules เท่าที่จำเป็น → image เล็ก
  output: 'standalone',
};

export default nextConfig;
