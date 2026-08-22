import {Easing, interpolate} from 'remotion';
import {CheckIcon, GitCommitIcon} from '../components/Icons';
import {cardStyle, colors, Eyebrow, LoopCrossfade, Scene} from '../theme';

const stages = [
  {label: 'commit', sub: 'Git'},
  {label: 'webhook', sub: 'trigger'},
  {label: 'checkout', sub: 'source'},
  {label: 'build image', sub: 'Docker'},
  {label: 'test', sub: 'pytest'},
  {label: 'push', sub: 'registry'},
  {label: 'deploy', sub: 'app'},
];

const PipelineFrame = ({storyFrame}: {storyFrame: number}) => {
  const tokenProgress = interpolate(storyFrame, [16, 276], [0, 6], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const tokenX = 104 + tokenProgress * 178;
  const bannerOpacity = interpolate(storyFrame, [279, 296], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <Scene>
      <div style={{position: 'absolute', left: 64, top: 50}}>
        <Eyebrow>PIPELINE AS A FLOW</Eyebrow>
        <div style={{fontSize: 48, fontWeight: 800, marginTop: 6}}>หนึ่ง commit เดินทางผ่านทุก stage</div>
      </div>
      <div style={{position: 'absolute', right: 64, top: 60, display: 'flex', alignItems: 'center', gap: 13, color: colors.gray, fontSize: 21, fontWeight: 700}}>
        <span style={{width: 14, height: 14, borderRadius: '50%', background: colors.graySoft}} /> รอ
        <span style={{width: 14, height: 14, borderRadius: '50%', background: colors.amber}} /> ทำงาน
        <span style={{width: 14, height: 14, borderRadius: '50%', background: colors.green}} /> ผ่าน
      </div>

      <div style={{position: 'absolute', left: 86, right: 86, top: 291, height: 10, borderRadius: 99, background: colors.graySoft}} />
      <div style={{position: 'absolute', left: 103, top: 274, width: Math.max(0, tokenX - 104), height: 10, borderRadius: 99, background: colors.green}} />

      {stages.map((stage, index) => {
        const activeStart = 18 + index * 42;
        const passed = storyFrame >= activeStart + 25;
        const active = storyFrame >= activeStart && !passed;
        return (
          <div
            key={stage.label}
            style={{
              ...cardStyle,
              position: 'absolute',
              left: 51 + index * 178,
              top: 325,
              width: 145,
              height: 142,
              borderWidth: 3,
              borderColor: passed ? colors.green : active ? colors.amber : colors.graySoft,
              background: passed ? colors.greenSoft : active ? colors.amberSoft : colors.white,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            <div style={{height: 34, display: 'grid', placeItems: 'center'}}>
              {index === 0 && !passed ? <GitCommitIcon color={active ? colors.amber : colors.gray} /> : passed ? <CheckIcon size={32} /> : <div style={{width: 20, height: 20, borderRadius: '50%', background: active ? colors.amber : colors.graySoft}} />}
            </div>
            <div style={{fontSize: stage.label.length > 9 ? 19 : 22, fontWeight: 900, textAlign: 'center'}}>{stage.label}</div>
            <div style={{fontSize: 17, color: colors.gray, fontWeight: 700}}>{stage.sub}</div>
          </div>
        );
      })}

      <div style={{position: 'absolute', left: tokenX - 18, top: 271, width: 45, height: 45, borderRadius: '50%', background: colors.blue, border: '7px solid white', boxShadow: '0 8px 18px rgba(37,99,235,.30)', scale: storyFrame < 12 ? .75 : 1}} />
      <div style={{position: 'absolute', left: tokenX - 5, top: 283, width: 12, height: 12, borderRadius: '50%', background: 'white'}} />

      <div style={{position: 'absolute', left: 320, right: 320, top: 522, height: 82, borderRadius: 22, background: colors.green, color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18, fontSize: 30, fontWeight: 900, opacity: bannerOpacity, translate: `0 ${interpolate(storyFrame, [278, 298], [18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)})}px`, boxShadow: '0 16px 30px rgba(22,163,74,.24)'}}>
        <CheckIcon size={36} color="white" /> Build #42 deployed
      </div>
      <div style={{position: 'absolute', bottom: 30, left: 0, right: 0, textAlign: 'center', color: colors.gray, fontSize: 20, fontWeight: 700}}>เทา → เหลือง → เขียว · สถานะเดียวกันทุกครั้ง</div>
    </Scene>
  );
};

export const PipelineFlow = () => <LoopCrossfade render={(storyFrame) => <PipelineFrame storyFrame={storyFrame} />} />;
