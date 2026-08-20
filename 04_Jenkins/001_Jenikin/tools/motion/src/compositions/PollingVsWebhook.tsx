import {Easing, interpolate} from 'remotion';
import {GitCommitIcon, JenkinsNode} from '../components/Icons';
import {cardStyle, colors, Eyebrow, LoopCrossfade, Scene} from '../theme';

const pollFrames = [42, 94, 188, 250];
const tickXs = [330, 490, 720, 900];

const Timeline = ({y, color}: {y: number; color: string}) => (
  <>
    <div style={{position: 'absolute', left: 275, top: y, width: 690, height: 8, borderRadius: 99, background: colors.graySoft}} />
    <div style={{position: 'absolute', left: 962, top: y - 7, width: 0, height: 0, borderTop: '11px solid transparent', borderBottom: '11px solid transparent', borderLeft: `18px solid ${color}`}} />
  </>
);

const PollingFrame = ({storyFrame}: {storyFrame: number}) => {
  const commitFrame = 132;
  const latestPoll = pollFrames.reduce((result, value, index) => (storyFrame >= value ? index : result), -1);
  const currentPollFrame = latestPoll >= 0 ? pollFrames[latestPoll] : -100;
  const pingProgress = interpolate(storyFrame, [currentPollFrame, currentPollFrame + 15, currentPollFrame + 30], [0, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const webhookProgress = interpolate(storyFrame, [commitFrame, commitFrame + 25], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const webhookX = 620 + webhookProgress * 395;

  return (
    <Scene>
      <div style={{position: 'absolute', left: 60, top: 39}}>
        <Eyebrow>TRIGGER TIMING</Eyebrow>
        <div style={{fontSize: 46, fontWeight: 800, marginTop: 5}}>Polling ต้องถาม · Webhook บอกทันที</div>
      </div>

      <div style={{...cardStyle, position: 'absolute', left: 52, top: 132, width: 1176, height: 245, borderLeft: `8px solid ${colors.gray}`}}>
        <div style={{position: 'absolute', left: 24, top: 20, fontSize: 29, fontWeight: 900}}>Polling</div>
        <div style={{position: 'absolute', left: 24, top: 61, fontSize: 19, color: colors.gray, fontWeight: 700}}>Jenkins ถามตาม tick</div>
        <Timeline y={139} color={colors.gray} />
        {tickXs.map((x, index) => {
          const happened = storyFrame >= pollFrames[index];
          const found = index === 2 && happened;
          return (
            <div key={x}>
              <div style={{position: 'absolute', left: x, top: 126, width: 4, height: 32, borderRadius: 9, background: happened ? (found ? colors.amber : colors.gray) : colors.graySoft}} />
              <div style={{position: 'absolute', left: x - 41, top: 169, width: 86, textAlign: 'center', color: found ? colors.amber : colors.gray, fontSize: 17, fontWeight: 800, opacity: happened ? 1 : .28}}>{found ? 'พบ commit' : 'ไม่มี'}</div>
            </div>
          );
        })}
        <div style={{position: 'absolute', left: 594, top: 87, display: 'flex', alignItems: 'center', gap: 8, opacity: storyFrame >= commitFrame ? 1 : .2}}>
          <GitCommitIcon color={colors.blue} />
          <div style={{fontSize: 19, fontWeight: 900, color: colors.blue}}>commit เกิดตรงนี้</div>
        </div>
        {latestPoll >= 0 && (
          <div style={{position: 'absolute', left: 965 - pingProgress * (965 - tickXs[latestPoll]), top: 254 - 132, width: 20, height: 20, borderRadius: '50%', background: latestPoll === 2 ? colors.amber : colors.gray, border: '4px solid white', boxShadow: '0 4px 12px rgba(15,23,42,.18)'}} />
        )}
        <div style={{position: 'absolute', right: 45, top: 40, display: 'flex', flexDirection: 'column', alignItems: 'center'}}><JenkinsNode color={colors.gray} /><div style={{fontSize: 18, fontWeight: 900}}>Jenkins</div></div>
        <div style={{position: 'absolute', right: 25, bottom: 18, background: storyFrame >= 212 ? colors.amberSoft : colors.graySoft, color: storyFrame >= 212 ? colors.amber : colors.gray, borderRadius: 14, padding: '8px 16px', fontSize: 21, fontWeight: 900}}>delay ≈ 40 วิ</div>
      </div>

      <div style={{...cardStyle, position: 'absolute', left: 52, top: 400, width: 1176, height: 245, borderLeft: `8px solid ${colors.green}`}}>
        <div style={{position: 'absolute', left: 24, top: 20, fontSize: 29, fontWeight: 900}}>Webhook</div>
        <div style={{position: 'absolute', left: 24, top: 61, fontSize: 19, color: colors.green, fontWeight: 700}}>Git ส่งเหตุการณ์ทันที</div>
        <Timeline y={139} color={colors.green} />
        <div style={{position: 'absolute', left: 594, top: 87, display: 'flex', alignItems: 'center', gap: 8, opacity: storyFrame >= commitFrame ? 1 : .2}}>
          <GitCommitIcon color={colors.green} />
          <div style={{fontSize: 19, fontWeight: 900, color: colors.green}}>push!</div>
        </div>
        <div style={{position: 'absolute', left: webhookX - 52, top: 128, width: 26, height: 26, borderRadius: '50%', background: colors.green, border: '5px solid white', boxShadow: '0 5px 14px rgba(22,163,74,.30)', opacity: storyFrame >= commitFrame ? 1 : 0}} />
        <div style={{position: 'absolute', right: 45, top: 40, display: 'flex', flexDirection: 'column', alignItems: 'center'}}><JenkinsNode color={storyFrame >= commitFrame + 25 ? colors.green : colors.gray} /><div style={{fontSize: 18, fontWeight: 900}}>Jenkins</div></div>
        <div style={{position: 'absolute', right: 25, bottom: 18, background: storyFrame >= commitFrame + 25 ? colors.greenSoft : colors.graySoft, color: storyFrame >= commitFrame + 25 ? colors.green : colors.gray, borderRadius: 14, padding: '8px 16px', fontSize: 21, fontWeight: 900}}>delay &lt; 1 วิ</div>
        <div style={{position: 'absolute', left: 785, top: 40, background: colors.greenSoft, color: colors.green, borderRadius: 14, padding: '9px 14px', fontSize: 18, fontWeight: 900, opacity: storyFrame >= commitFrame + 30 ? 1 : 0}}>BUILD ✓</div>
      </div>
    </Scene>
  );
};

export const PollingVsWebhook = () => <LoopCrossfade render={(storyFrame) => <PollingFrame storyFrame={storyFrame} />} />;
