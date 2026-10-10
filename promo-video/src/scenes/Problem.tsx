// 0:00 – 0:08 · The problem, in two beats.
// First: three in four surveyed workshops sit on lanes no fire engine can enter.
// Then: most stand within a metre of the next building, so a fire has nowhere to stop.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Label, Rise, Typed, Words, useCount} from '../components/ui';
import {MONO} from '../fonts';
import {ease, fade, lerp, prog} from '../lib/anim';
import {NARROW_SHARE, SCENES, TIGHT_SHARE, TOTALS} from '../story';
import {C, EMBER_GRADIENT} from '../theme';

const GAPS = [
  {name: 'Shared wall', color: C.tiers[0]},
  {name: 'Under 1 m', color: C.ember2},
  {name: 'Over 1 m', color: C.slate},
];
const bigNumber: React.CSSProperties = {
  display: 'inline-block', fontSize: 184, fontWeight: 800, letterSpacing: '-0.05em', lineHeight: 1, fontVariantNumeric: 'tabular-nums',
  backgroundImage: EMBER_GRADIENT, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
};

export const Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const narrow = useCount(0, NARROW_SHARE, 96, 28);
  const tight = useCount(0, TIGHT_SHARE, 188, 28);
  const lane = lerp(360, 232, prog(frame, 76, 96, ease.inOut));
  const first = 1 - prog(frame, 144, 156, ease.linear);  // the first beat leaves…
  const second = prog(frame, 156, 166, ease.linear);     // …as the second arrives
  const row: React.CSSProperties = {display: 'flex', alignItems: 'center', gap: 20, height: 46};
  const name: React.CSSProperties = {width: 172, fontSize: 25, fontWeight: 600, color: C.dim};
  return (
    <AbsoluteFill style={{opacity: fade(frame, SCENES.problem.dur, 1, 14)}}>
      <div style={{position: 'absolute', left: 110, top: 124}}>
        <Rise at={4}><Label>Lat · Lon</Label></Rise>
        <div style={{marginTop: 10, fontSize: 40, color: '#FFDCC4', textShadow: '0 0 26px rgba(255, 138, 76, 0.8)'}}>
          <Typed text="28.6665° N   77.2720° E" at={10} perFrame={0.8} linger={34} />
        </div>
        <Rise at={38} style={{marginTop: 14}}><Label style={{color: C.dim}}>Seelampur · North-East Delhi</Label></Rise>
      </div>

      {/* Beat one: the lanes */}
      <AbsoluteFill style={{opacity: first}}>
        <div style={{position: 'absolute', left: 110, top: 322, width: 980}}>
          <Words text="Lanes too narrow" at={26} size={106} />
          <Words text="for a fire engine." at={36} size={106} accent={['fire', 'engine']} />
        </div>
        <Rise at={64} style={{position: 'absolute', left: 110, top: 588}}>
          <div style={row}>
            <span style={name}>Fire engine</span>
            <div style={{width: 360, height: 20, borderRadius: 6, background: 'rgba(255, 255, 255, 0.88)'}} />
            <span style={{fontFamily: MONO, fontSize: 23, color: C.dim}}>2.5 m wide</span>
          </div>
          <div style={row}>
            <span style={name}>Most lanes</span>
            <div style={{width: lane, height: 20, borderRadius: 6, background: EMBER_GRADIENT, boxShadow: '0 0 24px rgba(240, 69, 47, 0.6)'}} />
            <span style={{fontFamily: MONO, fontSize: 23, color: '#FFB89A', opacity: prog(frame, 86, 98)}}>under 2.5 m</span>
          </div>
        </Rise>
        <div style={{position: 'absolute', left: 110, top: 742, display: 'flex', alignItems: 'center', gap: 36}}>
          <Rise at={94}><div style={bigNumber}>{narrow}%</div></Rise>
          <div>
            <Words text="of workshops are" at={106} size={48} weight={700} />
            <Words text="out of reach." at={112} size={48} weight={700} />
            <Rise at={124} style={{marginTop: 14}}><Label style={{fontSize: 19, color: C.dim}}>{TOTALS.narrow} of {TOTALS.workshops} surveyed</Label></Rise>
          </div>
        </div>
      </AbsoluteFill>

      {/* Beat two: the buildings */}
      <AbsoluteFill style={{opacity: second}}>
        <div style={{position: 'absolute', left: 110, top: 322, width: 980}}>
          <Words text="Buildings stand" at={160} size={106} />
          <Words text="wall to wall." at={170} size={106} accent={['wall', 'to']} />
        </div>
        {/* Gap to the next building, as shares of all surveyed workshops */}
        <Rise at={178} style={{position: 'absolute', left: 110, top: 592, width: 740}}>
          <div style={{display: 'flex', gap: 5, height: 20, transform: `scaleX(${prog(frame, 180, 206, ease.out)})`, transformOrigin: 'left center'}}>
            {GAPS.map((gap, i) => <div key={gap.name} style={{flex: TOTALS.gaps[i], borderRadius: 6, background: gap.color}} />)}
          </div>
          <div style={{display: 'flex', gap: 5, marginTop: 12, opacity: prog(frame, 196, 210)}}>
            {GAPS.map((gap, i) => <div key={gap.name} style={{flex: TOTALS.gaps[i], fontFamily: MONO, fontSize: 21, color: C.dim, whiteSpace: 'nowrap'}}>{gap.name}</div>)}
          </div>
        </Rise>
        <div style={{position: 'absolute', left: 110, top: 742, display: 'flex', alignItems: 'center', gap: 36}}>
          <Rise at={186}><div style={bigNumber}>{tight}%</div></Rise>
          <div>
            <Words text="stand within a metre" at={198} size={48} weight={700} />
            <Words text="of the next building." at={204} size={48} weight={700} />
            <Rise at={216} style={{marginTop: 14}}><Label style={{fontSize: 19, color: C.dim}}>{TOTALS.tight} of {TOTALS.workshops} surveyed</Label></Rise>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
