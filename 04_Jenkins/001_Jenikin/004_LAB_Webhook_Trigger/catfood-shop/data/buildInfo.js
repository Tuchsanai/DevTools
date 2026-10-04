import os from 'node:os';

// ค่าเหล่านี้ถูก "อบ" เข้า image ตอน docker build ผ่าน --build-arg แล้วอ่านตอนรันจริง
export function getBuildInfo() {
  return {
    app: 'catfood-shop',
    version: process.env.APP_VERSION || 'dev',
    build: process.env.BUILD_NUMBER || 'local',
    commit: process.env.GIT_COMMIT || 'none',
    builtAt: process.env.BUILD_TIME || 'unknown',
    // hostname ของ container = container ID แบบย่อ ใช้ดูว่า container ตัวไหนตอบ
    host: os.hostname(),
  };
}
