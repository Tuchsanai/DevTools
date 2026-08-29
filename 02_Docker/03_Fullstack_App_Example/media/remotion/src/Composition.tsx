import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type StepProps = {
  readonly index: number;
  readonly code: string;
  readonly title: string;
  readonly meaning: string;
  readonly color: string;
  readonly background: string;
};

const STEPS: ReadonlyArray<Omit<StepProps, "index">> = [
  { code: "US", title: "User Story", meaning: "ใคร · ต้องการอะไร · เพราะอะไร", color: "#2563eb", background: "#dbeafe" },
  { code: "REQ", title: "Requirement", meaning: "ระบบต้องทำอะไร", color: "#6d28d9", background: "#ede9fe" },
  { code: "AC", title: "Acceptance Criteria", meaning: "ผ่านเมื่อใด · ทดสอบอย่างไร", color: "#b45309", background: "#fef3c7" },
  { code: "NFR", title: "Non-Functional Requirement", meaning: "คุณภาพและข้อจำกัดของระบบ", color: "#047857", background: "#d1fae5" },
  { code: "DESIGN", title: "Design / Architecture", meaning: "เลือกโครงสร้างที่ทำให้ทุกข้อผ่าน", color: "#c2410c", background: "#ffedd5" },
];

const Step: React.FC<StepProps> = ({ index, code, title, meaning, color, background }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{ position: "relative", display: "flex", alignItems: "center", gap: 10 }}>
      <div
        style={{
          width: 175,
          height: 205,
          borderRadius: 24,
          border: `3px solid ${color}`,
          background,
          padding: "24px 20px",
          boxSizing: "border-box",
          opacity: interpolate(frame, [0, 0.5 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          translate: interpolate(frame, [0, 0.5 * fps], ["0px 28px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          boxShadow: "0 18px 42px rgba(15, 23, 42, 0.10)",
        }}
      >
        <div style={{ display: "inline-flex", minWidth: 64, height: 36, alignItems: "center", justifyContent: "center", padding: "0 12px", borderRadius: 999, backgroundColor: color, color: "white", fontSize: 21, fontWeight: 800, letterSpacing: 0.5 }}>
          {code}
        </div>
        <div style={{ marginTop: 17, color: "#0f172a", fontSize: 24, fontWeight: 800, lineHeight: 1.2 }}>{title}</div>
        <div style={{ marginTop: 12, color: "#475569", fontSize: 18, lineHeight: 1.3 }}>{meaning}</div>
      </div>
      {index < STEPS.length - 1 ? (
        <div
          style={{
            color: "#64748b",
            fontSize: 32,
            fontWeight: 700,
            opacity: interpolate(frame, [0.35 * fps, 0.7 * fps], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
          }}
        >
          →
        </div>
      ) : null}
    </div>
  );
};

const TraceExample: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const rows = [
    ["US-1", "ผู้ใช้ต้องการแจ้งซ่อมโดยเรื่องไม่หาย", "#2563eb"],
    ["REQ-01", "ระบบต้องสร้างใบแจ้งซ่อมได้", "#6d28d9"],
    ["เกณฑ์ผ่าน", "POST /api/tickets ตอบ 201 และสถานะ NEW", "#b45309"],
  ] as const;

  return (
    <div style={{ marginTop: 36, display: "grid", gridTemplateColumns: "1fr 1fr 1.35fr", gap: 12 }}>
      {rows.map(([label, detail, color], index) => (
        <div
          key={label}
          style={{
            borderLeft: `6px solid ${color}`,
            backgroundColor: "#ffffff",
            borderRadius: 12,
            padding: "14px 18px",
            boxShadow: "0 8px 26px rgba(15, 23, 42, 0.08)",
            opacity: interpolate(frame, [index * 0.45 * fps, (index * 0.45 + 0.45) * fps], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: interpolate(frame, [index * 0.45 * fps, (index * 0.45 + 0.45) * fps], ["0px 18px", "0px 0px"], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
          }}
        >
          <div style={{ color, fontSize: 20, fontWeight: 850 }}>{label}</div>
          <div style={{ color: "#334155", fontSize: 19, marginTop: 5, lineHeight: 1.3 }}>{detail}</div>
        </div>
      ))}
    </div>
  );
};

export const RequirementJourney: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ display: "block", background: "linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #fff7ed 100%)", color: "#0f172a", fontFamily: "Noto Sans Thai, Noto Sans, Arial, sans-serif", padding: "72px 80px 64px", boxSizing: "border-box" }}>
      <div
        style={{
          fontSize: 58,
          fontWeight: 900,
          letterSpacing: -1.5,
          opacity: interpolate(frame, [0, 0.65 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        จากเสียงผู้ใช้ → สถาปัตยกรรมที่ตรวจสอบได้
      </div>
      <div style={{ marginTop: 12, color: "#475569", fontSize: 29, lineHeight: 1.4 }}>ทุกแนวคิดมีคำถามเฉพาะของตนเอง และต้องสืบย้อนกลับไปหาหลักฐานต้นทางได้</div>
      <div style={{ marginTop: 44, display: "flex", alignItems: "center" }}>
        {STEPS.map((step, index) => (
          <Sequence key={step.code} from={Math.round((1.1 + index * 0.75) * fps)} durationInFrames={Math.round(7.5 * fps)} layout="none">
            <Step index={index} {...step} />
          </Sequence>
        ))}
      </div>
      <Sequence from={Math.round(5.1 * fps)} durationInFrames={Math.round(4.4 * fps)} layout="none">
        <TraceExample />
      </Sequence>
    </AbsoluteFill>
  );
};

export const MyComposition = () => (
  <Composition id="RequirementJourney" component={RequirementJourney} durationInFrames={300} fps={30} width={1280} height={720} />
);
