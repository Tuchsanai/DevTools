import { PageHead, Panel } from "./kit";

export function UnavailablePage({ title }: { title: string }) {
  const standalone = !process.env.API_BASE_URL;
  return (
    <>
      <PageHead eyebrow="SkillSpace" title={title} />
      <Panel className="border-dashed">
        <div className="grid min-h-64 place-items-center px-6 py-12 text-center">
          <div className="max-w-xl">
            <div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-full bg-wash text-2xl">
              {standalone ? "◌" : "!"}
            </div>
            <h2 className="text-xl font-bold text-ink">
              {standalone ? "รอเชื่อมต่อ API" : "ฐานข้อมูลยังไม่พร้อม"}
            </h2>
            <p className="mt-2 text-[14px] leading-7 text-ink-3">
              {standalone
                ? "ขณะนี้เว็บกำลังทำงานในโหมดเดี่ยว เมนูและ endpoint ของเว็บยังใช้งานได้ตามปกติ"
                : "หน้าเว็บยังทำงานและตอบสนองได้ โปรดลองรีเฟรชหลังจากบริการเบื้องหลังกลับมาพร้อม"}
            </p>
          </div>
        </div>
      </Panel>
    </>
  );
}
