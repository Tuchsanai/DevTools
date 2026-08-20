import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Gear} from '../components/Icons';
import {colors, Eyebrow, Scene} from '../theme';

const stages = ['plan', 'code', 'build', 'test', 'release', 'deploy', 'operate'];

export const Intro = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const phase = interpolate(frame, [0, durationInFrames - 8], [0, 360], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const dotAngle = ((phase - 90) * Math.PI) / 180;
  const pulse = 1 + 0.08 * Math.sin((phase * Math.PI) / 90);

  return (
    <Scene>
      <div style={{position: 'absolute', left: 78, top: 94, width: 610}}>
        <Eyebrow>DEVTOOLS · CI/CD</Eyebrow>
        <div style={{fontSize: 68, lineHeight: 1.13, fontWeight: 800, marginTop: 24, letterSpacing: -1.5}}>
          CI/CD ด้วย Jenkins
          <br />
          <span style={{color: colors.blue}}>บน Docker</span>
        </div>
        <div style={{fontSize: 29, color: colors.gray, fontWeight: 600, marginTop: 30, lineHeight: 1.45}}>
          จาก push หนึ่งครั้ง
          <br />
          สู่วงจรส่งมอบที่ทำงานต่อเนื่อง
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: 42}}>
          <div style={{height: 6, width: 110, background: colors.blue, borderRadius: 99}} />
          <div style={{fontSize: 20, color: colors.gray, fontWeight: 700}}>PLAN → OPERATE → PLAN</div>
        </div>
      </div>

      <svg width="1280" height="720" viewBox="0 0 1280 720" style={{position: 'absolute', inset: 0}} aria-hidden="true">
        <circle cx="975" cy="356" r="208" fill="white" stroke={colors.graySoft} strokeWidth="34" />
        <circle cx="975" cy="356" r="208" fill="none" stroke={colors.blue} strokeWidth="8" strokeDasharray="24 14" strokeLinecap="round" opacity=".88" />
        <circle cx="975" cy="356" r="153" fill={colors.blueSoft} opacity=".58" />
        <path d="M1072 223l22 3-10 20" fill="none" stroke={colors.blue} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M857 488l-22-3 10-20" fill="none" stroke={colors.blue} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={975 + Math.cos(dotAngle) * 208} cy={356 + Math.sin(dotAngle) * 208} r={11 * pulse} fill={colors.green} stroke="white" strokeWidth="5" />
      </svg>

      {stages.map((stage, index) => {
        const angle = ((index / stages.length) * 360 - 90) * (Math.PI / 180);
        return (
          <div
            key={stage}
            style={{
              position: 'absolute',
              left: 975 + Math.cos(angle) * 276 - 51,
              top: 356 + Math.sin(angle) * 276 - 22,
              width: 102,
              textAlign: 'center',
              fontSize: 20,
              fontWeight: 800,
              color: index < 2 ? colors.blue : colors.ink,
              background: 'rgba(248,250,252,.92)',
              borderRadius: 12,
              padding: '4px 5px',
            }}
          >
            {stage}
          </div>
        );
      })}

      <div style={{position: 'absolute', left: 915, top: 298}}>
        <Gear size={126} rotation={phase} color={colors.blue} />
      </div>
      <div style={{position: 'absolute', left: 1018, top: 390}}>
        <Gear size={82} rotation={-phase * 1.4} color={colors.green} />
      </div>
      <div style={{position: 'absolute', right: 31, bottom: 25, fontSize: 16, color: colors.gray, fontWeight: 700}}>
        GENERIC AUTOMATION GRAPHIC
      </div>
    </Scene>
  );
};
