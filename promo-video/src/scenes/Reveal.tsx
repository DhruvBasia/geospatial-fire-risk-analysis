// 0:08 – 0:15 · The reveal. The logo lands centre-frame with the name in Hindi (see Lockup),
// then steps aside while the count runs up to 148 and every workshop takes the colour of its risk level.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Bar, Label, Rise, Words, useCount} from '../components/ui';
import {MONO} from '../fonts';
import {fade, prog} from '../lib/anim';
import {SCENES, TOTALS} from '../story';
import {C, TIER_NAMES} from '../theme';

export const Reveal: React.FC = () => {
  const frame = useCurrentFrame();
  const count = useCount(0, TOTALS.workshops, 100, 28);
  const most = Math.max(...TOTALS.tiers);
  return (
    <AbsoluteFill style={{opacity: fade(frame, SCENES.reveal.dur, 1, 14)}}>
      <div style={{position: 'absolute', left: 110, top: 214, opacity: prog(frame, 96, 110)}}>
        <div style={{fontSize: 224, fontWeight: 800, letterSpacing: '-0.055em', lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{count}</div>
        <Words text="workshops," at={108} size={60} weight={700} style={{marginTop: 6}} />
        <Words text="surveyed door to door." at={114} size={60} weight={700} color={C.dim} />
      </div>

      <div style={{position: 'absolute', left: 110, top: 648, width: 640}}>
        <Rise at={120}><Label>Coloured by risk level</Label></Rise>
        {TIER_NAMES.map((tier, i) => {
          const fill = prog(frame, 128 + i * 5, 150 + i * 5);
          return (
            <Rise key={tier} at={124 + i * 5} style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 20}}>
              <i style={{width: 15, height: 15, borderRadius: '50%', background: C.tiers[i], boxShadow: `0 0 16px ${C.tiers[i]}`}} />
              <span style={{width: 150, fontSize: 30, fontWeight: 700}}>{tier}</span>
              <Bar value={(TOTALS.tiers[i] / most) * fill} color={C.tiers[i]} style={{flex: 1}} />
              <span style={{width: 70, textAlign: 'right', fontFamily: MONO, fontSize: 28, fontVariantNumeric: 'tabular-nums'}}>{Math.round(TOTALS.tiers[i] * fill)}</span>
            </Rise>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
