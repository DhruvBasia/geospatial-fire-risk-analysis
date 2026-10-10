// The film: one continuous map shot, seven scenes of graphics over it, narration and sound.
import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {Atlas} from './components/Atlas';
import {Backdrop, Hud, Lockup, Scrims} from './components/Chrome';
import {SANS} from './fonts';
import {ease, prog} from './lib/anim';
import {Close} from './scenes/Close';
import {Dispatch} from './scenes/Dispatch';
import {Insights} from './scenes/Insights';
import {Problem} from './scenes/Problem';
import {Relay} from './scenes/Relay';
import {Reveal} from './scenes/Reveal';
import {Risk} from './scenes/Risk';
import {SCENES, SOUNDS, VOICEOVER, VOICE_VOLUME} from './story';
import {C} from './theme';

const Soundtrack: React.FC = () => (
  <>
    {VOICEOVER.map((line) => (
      <Sequence key={line.id} from={line.at} layout="none">
        <Audio src={staticFile(`vo/${line.id}.wav`)} volume={VOICE_VOLUME} />
      </Sequence>
    ))}
    {SOUNDS.map((cue, i) => (
      <Sequence key={i} from={cue.at} layout="none">
        <Audio src={staticFile(`sfx/${cue.file}.wav`)} volume={cue.vol} />
      </Sequence>
    ))}
  </>
);

export const Film: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: C.bg, color: C.text, fontFamily: SANS}}>
      <Backdrop />
      <Atlas />
      <Scrims />
      <Hud />

      <Sequence from={SCENES.problem.from} durationInFrames={SCENES.problem.dur}><Problem /></Sequence>
      <Sequence from={SCENES.reveal.from} durationInFrames={SCENES.reveal.dur}><Reveal /></Sequence>
      <Sequence from={SCENES.risk.from} durationInFrames={SCENES.risk.dur}><Risk /></Sequence>
      <Sequence from={SCENES.dispatch.from} durationInFrames={SCENES.dispatch.dur}><Dispatch /></Sequence>
      <Sequence from={SCENES.relay.from} durationInFrames={SCENES.relay.dur}><Relay /></Sequence>
      <Sequence from={SCENES.insights.from} durationInFrames={SCENES.insights.dur}><Insights /></Sequence>
      <Sequence from={SCENES.close.from} durationInFrames={SCENES.close.dur}><Close /></Sequence>

      <Lockup />
      <Soundtrack />

      {/* Open from black */}
      <AbsoluteFill style={{backgroundColor: '#000', opacity: 1 - prog(frame, 0, 12, ease.linear), pointerEvents: 'none'}} />
    </AbsoluteFill>
  );
};
