/**
 * ไอคอนทั้งระบบอยู่ไฟล์นี้ไฟล์เดียว
 *
 * กติกา : inline SVG เขียนเอง · viewBox 24 · stroke-width 1.5 · สีมาจาก currentColor
 * ห้ามใช้ emoji แทนไอคอน (ขนาด/เส้น/สีคุมไม่ได้ และอ่านบนโปรเจกเตอร์ไม่ชัด)
 * ห้ามโหลดชุดไอคอนจาก CDN (หน้าเว็บนี้ต้องทำงานได้แม้เครื่องลูกค้าออกเน็ตไม่ได้)
 *
 * ทุกตัวเป็น server component ธรรมดา — เป็นแค่ฟังก์ชันที่คืน JSX ไม่มี state
 */

type IconProps = { className?: string };

function icon(shape: React.ReactNode) {
  return function Icon({ className = "h-4 w-4" }: IconProps) {
    return (
      <svg
        viewBox="0 0 24 24"
        className={className}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        {shape}
      </svg>
    );
  };
}

/* ---------- เมนูหลัก ---------- */

export const IconOverview = icon(
  <>
    <path d="M3 20h18" />
    <path d="M6 20v-6" />
    <path d="M11 20V9" />
    <path d="M16 20v-3" />
    <path d="M21 20V5" />
  </>,
);

export const IconBoard = icon(
  <>
    <rect x="3" y="4" width="5.5" height="16" rx="1" />
    <rect x="10.5" y="4" width="5.5" height="11" rx="1" />
    <rect x="18" y="4" width="3" height="7" rx="1" />
  </>,
);

export const IconLoan = icon(
  <>
    <path d="M4 7h10a3 3 0 0 1 3 3v9" />
    <path d="M7 4 4 7l3 3" />
    <path d="M20 17H10a3 3 0 0 1-3-3" />
    <path d="m17 20 3-3-3-3" />
  </>,
);

export const IconParts = icon(
  <>
    <path d="M3 8.5 12 4l9 4.5v7L12 20l-9-4.5z" />
    <path d="M3 8.5 12 13l9-4.5" />
    <path d="M12 13v7" />
  </>,
);

/* ---------- สถานะ ---------- */

/** เตือน — ใช้คู่กับสี crit เสมอ (สี + ไอคอน + คำ ครบสามอย่าง) */
export const IconAlert = icon(
  <>
    <path d="M12 4.5 21 19.5H3z" />
    <path d="M12 10v4" />
    <path d="M12 17.2v.1" />
  </>,
);

/** เรียบร้อย */
export const IconCheck = icon(<path d="m4.5 12.5 5 5 10-11" />);

/** จุดกลาง — ใช้กับ badge ที่ "ไม่ต้องเตือน" (ปกติ · ไม่เร่ง · เพียงพอ · ว่าง) */
export const IconDot = icon(<circle cx="12" cy="12" r="3.5" fill="currentColor" />);

/** ประแจ — ครุภัณฑ์อยู่ระหว่างซ่อม */
export const IconWrench = icon(
  <path d="M15.5 4a5 5 0 0 0-4.6 7l-6.2 6.2a1.8 1.8 0 0 0 2.5 2.5l6.2-6.2A5 5 0 1 0 15.5 4z" />,
);

/** มือส่งของ — ครุภัณฑ์ถูกยืมอยู่ */
export const IconHandoff = icon(
  <>
    <path d="M3 11h3l3.5 3.5" />
    <path d="M6 11V6.5a1.5 1.5 0 0 1 3 0V11" />
    <path d="M9 9.5V5a1.5 1.5 0 0 1 3 0v4.5" />
    <path d="M12 9.5V6a1.5 1.5 0 0 1 3 0v5" />
    <path d="M15 11V8a1.5 1.5 0 0 1 3 0v6a6 6 0 0 1-6 6h-1.5a5 5 0 0 1-3.6-1.5L3.5 15" />
  </>,
);

/** นาฬิกา — เวลา/ระยะเวลา */
export const IconClock = icon(
  <>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 7.5V12l3 2" />
  </>,
);

/* ---------- ทิศทาง ---------- */

export const IconArrow = icon(
  <>
    <path d="M4.5 12h14" />
    <path d="m13 6 6 6-6 6" />
  </>,
);

export const IconChevron = icon(<path d="m9 5 7 7-7 7" />);

/** อาคาร — โลโก้ของระบบในแถบนำทาง */
export const IconBuilding = icon(
  <>
    <path d="M3 20h18" />
    <path d="M6 20V9l6-4.5L18 9v11" />
    <path d="M10 20v-4.5h4V20" />
    <path d="M10 11h.01M14 11h.01" />
  </>,
);
