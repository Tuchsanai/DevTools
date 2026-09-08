// Tailwind 4 เสียบเข้ามาทาง PostCSS ตัวเดียว ไม่ต้องมี tailwind.config.js อีกแล้ว
// (คลาสถูกสแกนจากไฟล์ต้นทางอัตโนมัติ ตั้งค่าธีมทำใน globals.css ด้วย @theme)
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};

export default config;
