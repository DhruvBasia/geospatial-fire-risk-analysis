import React from 'react';
import {Composition} from 'remotion';
import {Film} from './Film';
import {DURATION, FPS, H, W} from './theme';

export const Root: React.FC = () => (
  <Composition id="AgniDrishti" component={Film} durationInFrames={DURATION} fps={FPS} width={W} height={H} />
);
