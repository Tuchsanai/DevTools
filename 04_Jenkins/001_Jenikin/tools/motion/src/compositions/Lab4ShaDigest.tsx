import {Easing, Interactive, interpolate} from 'remotion';
import {LoopCrossfade, Scene} from '../theme';

const Stage = ({x, title, detail, active}: {x: number; title: string; detail: string; active: number}) => (
  <div style={{position: 'absolute', left: x, top: 302, width: 238, height: 170, borderRadius: 24, border: `4px solid ${active > 0.7 ? '#16a34a' : active > 0.1 ? '#f59e0b' : '#cbd5e1'}`, background: active > 0.7 ? '#ecfdf5' : active > 0.1 ? '#fffbeb' : '#ffffff', boxShadow: '0 16px 36px rgba(15,23,42,.12)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
    <div style={{fontSize: 34, fontWeight: 900, color: '#0f172a'}}>{title}</div>
    <div style={{fontSize: 23, fontWeight: 700, color: '#64748b', marginTop: 9}}>{detail}</div>
    <div style={{position: 'absolute', right: 15, top: 15, width: 24, height: 24, borderRadius: '50%', background: active > 0.7 ? '#16a34a' : active > 0.1 ? '#f59e0b' : '#cbd5e1'}} />
  </div>
);

const Frame = ({storyFrame}: {storyFrame: number}) => {
  const progress = interpolate(storyFrame, [10, 190], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const tokenX = 112 + progress * 1000;
  const active = (start: number) => interpolate(storyFrame, [start, start + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Scene>
      <Interactive.Div name="LAB title" style={{position: 'absolute', left: 78, top: 62, fontSize: 25, fontWeight: 800, color: '#2563eb', letterSpacing: 1.2}}>LAB 4 · PIPELINE FROM GIT</Interactive.Div>
      <Interactive.Div name="Headline" style={{position: 'absolute', left: 78, top: 104, fontSize: 58, lineHeight: 1.12, fontWeight: 900, color: '#0f172a'}}>หนึ่ง SHA เดินทางถึง digest</Interactive.Div>
      <Interactive.Div name="Subtitle" style={{position: 'absolute', left: 80, top: 188, fontSize: 29, fontWeight: 700, color: '#64748b'}}>source เดียว · tag ตรวจย้อนกลับได้ · content เปลี่ยนไม่ได้</Interactive.Div>

      <div style={{position: 'absolute', left: 112, top: 277, width: 1000, height: 12, borderRadius: 99, background: '#e2e8f0'}} />
      <div style={{position: 'absolute', left: 112, top: 277, width: 1000 * progress, height: 12, borderRadius: 99, background: '#16a34a'}} />
      <div style={{position: 'absolute', left: tokenX - 18, top: 265, width: 38, height: 38, borderRadius: '50%', background: '#2563eb', border: '6px solid white', boxShadow: '0 8px 20px rgba(37,99,235,.35)'}} />

      <Stage x={48} title="GitHub" detail="anonymous checkout" active={active(8)} />
      <Stage x={348} title="Test" detail="diff = exit 0" active={active(58)} />
      <Stage x={648} title="Build + Push" detail="full / short SHA" active={active(108)} />
      <Stage x={948} title="Pull + Run" detail="sha256 digest" active={active(158)} />

      <Interactive.Div name="SHA evidence" style={{position: 'absolute', left: 92, top: 520, padding: '15px 23px', borderRadius: 14, background: '#0f172a', color: '#dbeafe', fontFamily: 'monospace', fontSize: 24, fontWeight: 800, opacity: interpolate(storyFrame, [12, 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>SHA 261970a1f0a8…</Interactive.Div>
      <Interactive.Div name="Digest evidence" style={{position: 'absolute', right: 92, top: 520, padding: '15px 23px', borderRadius: 14, background: '#052e20', color: '#bbf7d0', fontFamily: 'monospace', fontSize: 24, fontWeight: 800, opacity: interpolate(storyFrame, [170, 192], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>digest sha256:42ea0707…</Interactive.Div>
      <Interactive.Div name="Conclusion" style={{position: 'absolute', left: 250, right: 250, bottom: 43, textAlign: 'center', fontSize: 30, fontWeight: 900, color: '#15803d', opacity: interpolate(storyFrame, [185, 207], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>Git SHA = OCI revision · pull-run ผ่าน</Interactive.Div>
    </Scene>
  );
};

export const Lab4ShaDigest = () => <LoopCrossfade render={(storyFrame) => <Frame storyFrame={storyFrame} />} />;
