import {Composition} from 'remotion';
import {Intro} from './compositions/Intro';
import {ManualVsCi} from './compositions/ManualVsCi';
import {PipelineFlow} from './compositions/PipelineFlow';
import {PollingVsWebhook} from './compositions/PollingVsWebhook';
import {DoodSocket} from './compositions/DoodSocket';

export const MotionRoot = () => (
  <>
    <Composition id="mo-intro" component={Intro} durationInFrames={240} fps={30} width={1280} height={720} />
    <Composition id="mo-manual-vs-ci" component={ManualVsCi} durationInFrames={360} fps={30} width={1280} height={720} />
    <Composition id="mo-pipeline-flow" component={PipelineFlow} durationInFrames={360} fps={30} width={1280} height={720} />
    <Composition id="mo-polling-vs-webhook" component={PollingVsWebhook} durationInFrames={360} fps={30} width={1280} height={720} />
    <Composition id="mo-dood-socket" component={DoodSocket} durationInFrames={360} fps={30} width={1280} height={720} />
  </>
);
