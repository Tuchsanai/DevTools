import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // standalone = Next รวม node_modules เท่าที่ใช้จริงไว้ใน .next/standalone ให้เอง
  // ทำให้อิมเมจชั้น runtime ไม่ต้องมี node_modules ทั้งชุด (เล็กลงหลายร้อย MB)
  output: "standalone",
};

export default nextConfig;
