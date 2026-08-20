import {Easing, interpolate, spring} from 'remotion';
import {CheckIcon, DockerBoxIcon, JenkinsNode} from '../components/Icons';
import {cardStyle, colors, Eyebrow, LoopCrossfade, Scene} from '../theme';

const ContainerCard = ({x, y, title, subtitle, accent, children}: {x: number; y: number; title: string; subtitle: string; accent: string; children: React.ReactNode}) => (
  <div style={{...cardStyle, position: 'absolute', left: x, top: y, width: 230, height: 180, border: `3px solid ${accent}`, background: 'white', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
    {children}
    <div style={{fontSize: 27, fontWeight: 900, marginTop: 4}}>{title}</div>
    <div style={{fontSize: 17, color: colors.gray, fontWeight: 700}}>{subtitle}</div>
  </div>
);

const DoodFrame = ({storyFrame}: {storyFrame: number}) => {
  const commandProgress = interpolate(storyFrame, [42, 162], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const commandX = interpolate(commandProgress, [0, .48, 1], [390, 650, 930]);
  const commandY = interpolate(commandProgress, [0, .48, 1], [353, 353, 310]);
  const arrived = storyFrame >= 162;
  const appScale = spring({frame: storyFrame - 172, fps: 30, config: {damping: 14, mass: .7, stiffness: 135}});
  const responseProgress = interpolate(storyFrame, [232, 284], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

  return (
    <Scene>
      <div style={{position: 'absolute', left: 63, top: 37}}>
        <Eyebrow>DOCKER-OUTSIDE-OF-DOCKER</Eyebrow>
        <div style={{fontSize: 45, fontWeight: 800, marginTop: 5}}>Jenkins สั่ง dockerd ของ Host ผ่าน socket</div>
      </div>

      <div style={{position: 'absolute', left: 49, top: 126, width: 1182, height: 540, borderRadius: 30, border: `4px solid ${colors.blue}`, background: 'rgba(219,234,254,.30)', boxShadow: 'inset 0 0 0 10px rgba(255,255,255,.65)'}}>
        <div style={{position: 'absolute', left: 30, top: 20, display: 'flex', alignItems: 'center', gap: 12}}>
          <div style={{width: 16, height: 16, borderRadius: '50%', background: colors.blue}} />
          <div style={{fontSize: 28, fontWeight: 900, color: colors.blue}}>เครื่อง Host</div>
        </div>

        <ContainerCard x={92} y={165} title="Jenkins" subtitle="container" accent={colors.blue}><JenkinsNode /></ContainerCard>

        <div style={{position: 'absolute', left: 468, top: 166, width: 215, height: 176, borderRadius: 22, border: `3px dashed ${colors.amber}`, background: colors.amberSoft, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
          <div style={{width: 84, height: 42, borderRadius: 9, background: colors.amber, position: 'relative'}}>
            <div style={{position: 'absolute', left: 12, right: 12, top: 13, height: 7, borderRadius: 9, background: 'white'}} />
          </div>
          <div style={{fontSize: 22, fontWeight: 900, marginTop: 12}}>docker.sock</div>
          <div style={{fontSize: 15, color: colors.gray, fontWeight: 700}}>/var/run/docker.sock</div>
          <div style={{fontSize: 15, color: colors.amber, fontWeight: 900, marginTop: 5}}>ไฟล์บน Host</div>
        </div>

        <div style={{...cardStyle, position: 'absolute', left: 848, top: 102, width: 245, height: 182, border: `3px solid ${colors.green}`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
          <DockerBoxIcon color={colors.green} />
          <div style={{fontSize: 29, fontWeight: 900}}>dockerd</div>
          <div style={{fontSize: 17, color: colors.gray, fontWeight: 700}}>daemon ของ Host</div>
        </div>

        <svg width="1182" height="540" style={{position: 'absolute', inset: 0}} aria-hidden="true">
          <path d="M322 255H470M683 255C770 255 770 193 848 193" fill="none" stroke={colors.blue} strokeWidth="7" strokeLinecap="round" strokeDasharray="15 11" />
          <path d="M827 182l22 11-20 14" fill="none" stroke={colors.blue} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M955 291C922 369 774 405 683 405" fill="none" stroke={colors.green} strokeWidth="6" strokeLinecap="round" strokeDasharray="13 10" opacity={responseProgress} />
        </svg>

        <div style={{position: 'absolute', left: commandX - 49, top: commandY - 126, width: 38, height: 38, borderRadius: '50%', background: arrived ? colors.green : colors.blue, border: '6px solid white', boxShadow: '0 7px 16px rgba(37,99,235,.30)', opacity: storyFrame < 35 ? 0 : 1}} />
        <div style={{position: 'absolute', left: 319, top: 112, color: colors.blue, background: colors.blueSoft, borderRadius: 12, padding: '7px 13px', fontSize: 17, fontWeight: 900, opacity: storyFrame >= 34 && storyFrame < 176 ? 1 : .25}}>docker run app</div>

        <div style={{position: 'absolute', left: 493, top: 364, width: 232, height: 155, scale: Math.max(0, Math.min(1.08, appScale)), opacity: storyFrame >= 168 ? 1 : 0}}>
          <div style={{...cardStyle, width: '100%', height: '100%', border: `3px solid ${colors.green}`, background: colors.greenSoft, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
            <DockerBoxIcon color={colors.green} />
            <div style={{fontSize: 29, fontWeight: 900}}>app</div>
            <div style={{fontSize: 17, color: colors.green, fontWeight: 900}}>sibling container</div>
          </div>
        </div>
        <div style={{position: 'absolute', left: 94, bottom: 24, width: 343, height: 58, borderRadius: 15, background: colors.white, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: colors.blue, fontSize: 20, fontWeight: 900}}>
          <CheckIcon color={colors.blue} /> app ไม่ได้อยู่ใน Jenkins
        </div>
      </div>
    </Scene>
  );
};

export const DoodSocket = () => <LoopCrossfade render={(storyFrame) => <DoodFrame storyFrame={storyFrame} />} />;
