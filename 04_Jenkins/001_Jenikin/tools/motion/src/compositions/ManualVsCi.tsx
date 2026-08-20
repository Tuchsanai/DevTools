import {Easing, interpolate} from 'remotion';
import {CheckIcon, GitCommitIcon} from '../components/Icons';
import {cardStyle, colors, Eyebrow, LoopCrossfade, Scene, StatusDot} from '../theme';

const MiniStage = ({x, label, active, good}: {x: number; label: string; active: boolean; good: boolean}) => (
  <div
    style={{
      ...cardStyle,
      position: 'absolute',
      left: x,
      top: 372,
      width: 130,
      height: 82,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 7,
      borderColor: good ? colors.green : active ? colors.amber : colors.graySoft,
      background: good ? colors.greenSoft : active ? colors.amberSoft : colors.white,
      fontSize: 22,
      fontWeight: 800,
    }}
  >
    {good ? <CheckIcon size={22} /> : <StatusDot color={active ? colors.amber : colors.graySoft} size={11} />}
    {label}
  </div>
);

const Person = () => (
  <svg width="86" height="128" viewBox="0 0 86 128" fill="none" aria-hidden="true">
    <circle cx="43" cy="20" r="15" fill={colors.amberSoft} stroke={colors.amber} strokeWidth="4" />
    <path d="M43 36v42M43 49 18 70M43 49l25 14M43 78 24 112M43 78l23 34" stroke={colors.ink} strokeWidth="7" strokeLinecap="round" />
  </svg>
);

const ManualVsCiFrame = ({storyFrame}: {storyFrame: number}) => {
  const manualCycle = storyFrame % 126;
  const manualX = interpolate(manualCycle, [0, 38, 78, 112, 125], [130, 275, 420, 500, 130], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const manualY = 313 - Math.sin((manualCycle / 126) * Math.PI * 3) * 18;
  const errorOn = manualCycle >= 82 && manualCycle < 118;
  const errorOpacity = errorOn ? (Math.floor(storyFrame / 5) % 2 === 0 ? 1 : 0.28) : 0;
  const ciCycle = storyFrame % 96;
  const tokenX = interpolate(ciCycle, [0, 12, 84, 95], [724, 724, 1165, 724], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  return (
    <Scene>
      <div style={{position: 'absolute', left: 58, right: 58, top: 42, display: 'flex', justifyContent: 'space-between', alignItems: 'end'}}>
        <div>
          <Eyebrow>จังหวะการส่งมอบ</Eyebrow>
          <div style={{fontSize: 45, fontWeight: 800, marginTop: 7}}>กด Deploy เอง vs CI/CD อัตโนมัติ</div>
        </div>
        <div style={{fontSize: 22, color: colors.gray, fontWeight: 700}}>งานเท่ากัน · ประสบการณ์ต่างกัน</div>
      </div>

      <div style={{...cardStyle, position: 'absolute', left: 52, top: 142, width: 566, height: 520, borderTop: `8px solid ${colors.red}`}}>
        <div style={{position: 'absolute', left: 28, top: 24, fontSize: 33, fontWeight: 800}}>Deploy มือ</div>
        <div style={{position: 'absolute', right: 27, top: 31, fontSize: 20, color: colors.red, fontWeight: 800}}>ช้า · เสี่ยงพลาด</div>
        <div style={{position: 'absolute', left: 29, top: 105}}><Person /></div>
        <div style={{position: 'absolute', left: 128, top: 115, fontSize: 23, fontWeight: 700, lineHeight: 1.45, color: colors.gray}}>
          ลากไฟล์ทีละขั้น
          <br />จำคำสั่งเองทุกครั้ง
        </div>
        <div style={{position: 'absolute', left: 62, top: 316, width: 430, height: 7, borderRadius: 99, background: colors.graySoft}} />
        <MiniStage x={42} label="build" active={manualCycle < 38} good={false} />
        <MiniStage x={216} label="copy" active={manualCycle >= 38 && manualCycle < 78} good={false} />
        <MiniStage x={390} label="ssh" active={manualCycle >= 78} good={false} />
        <div style={{position: 'absolute', left: manualX, top: manualY, width: 58, height: 43, borderRadius: 10, background: colors.amber, color: 'white', display: 'grid', placeItems: 'center', fontSize: 16, fontWeight: 800, boxShadow: '0 9px 20px rgba(217,119,6,.28)'}}>FILE</div>
        <div style={{position: 'absolute', left: 422, top: 234, opacity: errorOpacity, background: colors.redSoft, color: colors.red, border: `2px solid ${colors.red}`, borderRadius: 15, padding: '10px 15px', fontSize: 21, fontWeight: 900}}>ERROR!</div>
        <div style={{position: 'absolute', left: 35, bottom: 23, display: 'flex', alignItems: 'center', gap: 14, fontSize: 22, color: colors.gray, fontWeight: 700}}>
          <div style={{width: 42, height: 42, border: `4px solid ${colors.gray}`, borderRadius: '50%', position: 'relative'}}>
            <div style={{position: 'absolute', left: 17, top: 5, width: 4, height: 14, background: colors.gray, borderRadius: 9, rotate: `${storyFrame * 7}deg`, transformOrigin: '2px 16px'}} />
          </div>
          เวลารอสะสมทุกขั้น
        </div>
      </div>

      <div style={{...cardStyle, position: 'absolute', left: 662, top: 142, width: 566, height: 520, borderTop: `8px solid ${colors.green}`}}>
        <div style={{position: 'absolute', left: 28, top: 24, fontSize: 33, fontWeight: 800}}>CI/CD</div>
        <div style={{position: 'absolute', right: 27, top: 31, fontSize: 20, color: colors.green, fontWeight: 800}}>เร็ว · ทำซ้ำได้</div>
        <div style={{position: 'absolute', left: 45, top: 104, display: 'flex', alignItems: 'center', gap: 17}}>
          <GitCommitIcon />
          <div><div style={{fontSize: 25, fontWeight: 800}}>git push</div><div style={{fontSize: 19, color: colors.gray, fontWeight: 600}}>จุดเริ่มเดียว</div></div>
        </div>
        <div style={{position: 'absolute', left: 45, right: 45, top: 266, height: 58, borderRadius: 15, background: colors.blueSoft, overflow: 'hidden'}}>
          {Array.from({length: 10}).map((_, index) => (
            <div key={index} style={{position: 'absolute', left: ((index * 70 + storyFrame * 7) % 700) - 40, top: 23, width: 34, height: 10, borderRadius: 99, background: colors.blue, opacity: .32}} />
          ))}
        </div>
        <div style={{position: 'absolute', left: tokenX - 662, top: 276, width: 38, height: 38, borderRadius: '50%', background: colors.blue, border: '6px solid white', boxShadow: '0 6px 16px rgba(37,99,235,.32)'}} />
        <MiniStage x={704 - 662} label="test" active={ciCycle >= 10 && ciCycle < 35} good={ciCycle >= 35} />
        <MiniStage x={878 - 662} label="build" active={ciCycle >= 35 && ciCycle < 60} good={ciCycle >= 60} />
        <MiniStage x={1052 - 662} label="deploy" active={ciCycle >= 60 && ciCycle < 84} good={ciCycle >= 84} />
        <div style={{position: 'absolute', left: 42, right: 42, bottom: 26, height: 54, borderRadius: 16, background: colors.greenSoft, color: colors.green, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, fontSize: 22, fontWeight: 900}}>
          <CheckIcon /> ไหลต่อเนื่องด้วยมาตรฐานเดิม
        </div>
      </div>
    </Scene>
  );
};

export const ManualVsCi = () => <LoopCrossfade render={(storyFrame) => <ManualVsCiFrame storyFrame={storyFrame} />} />;
