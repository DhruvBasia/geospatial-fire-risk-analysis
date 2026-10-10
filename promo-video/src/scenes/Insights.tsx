// 0:34 – 0:40 · The settlement at a glance. Three charts build over the dimmed map: the mix of
// risk levels, the most common problems, and where fires have already happened.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Bar, Label, Panel, Rise, Words} from '../components/ui';
import {MONO} from '../fonts';
import {clamp, ease, fade, prog} from '../lib/anim';
import {INSIGHTS, SCENES, TOTALS} from '../story';
import {C, TIER_NAMES, scoreTier} from '../theme';

const CARD = {top: 372, width: 540, height: 556};
const LEFTS = [110, 690, 1270];
const FIRE_COLUMNS = 14;

/** Risk-level ring that sweeps round once; the number in the middle counts with it. */
const Donut: React.FC<{sweep: number; size: number}> = ({sweep, size}) => {
  const total = TOTALS.workshops;
  let before = 0;
  return (
    <div style={{position: 'relative', width: size, height: size, flex: 'none'}}>
      <svg width={size} height={size} viewBox="0 0 42 42" style={{display: 'block', transform: 'rotate(-90deg)'}}>
        <circle cx={21} cy={21} r={15.915} fill="none" stroke="rgba(255, 255, 255, 0.10)" strokeWidth={5} />
        {TOTALS.tiers.map((n, i) => {
          const share = (n / total) * 100;
          const shown = clamp(sweep * 100 - before, 0, Math.max(0, share - 1.2));
          const segment = <circle key={i} cx={21} cy={21} r={15.915} fill="none" stroke={C.tiers[i]} strokeWidth={5} strokeDasharray={`${shown} ${100 - shown}`} strokeDashoffset={-before} />;
          before += share;
          return shown > 0 ? segment : null;
        })}
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
        <span style={{fontSize: size * 0.27, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.round(sweep * total)}</span>
        <span style={{marginTop: 4, fontSize: size * 0.085, color: C.dim}}>workshops</span>
      </div>
    </div>
  );
};

export const Insights: React.FC = () => {
  const frame = useCurrentFrame();
  const sweep = prog(frame, 36, 82, ease.inOut);
  const fires = INSIGHTS.fires;
  const lit = Math.round(prog(frame, 58, 110, ease.linear) * fires.total);
  const panel: React.CSSProperties = {width: '100%', height: '100%', padding: '32px 36px'};
  const card = (i: number): React.CSSProperties => ({position: 'absolute', left: LEFTS[i], top: CARD.top, width: CARD.width, height: CARD.height});
  return (
    <AbsoluteFill style={{opacity: fade(frame, SCENES.insights.dur, 1, 12)}}>
      <div style={{position: 'absolute', left: 110, top: 176}}>
        <Words text="The whole settlement," at={10} size={64} />
        <Words text="at a glance." at={20} size={64} accent={['at', 'a', 'glance']} />
      </div>

      {/* Risk levels */}
      <Rise at={24} y={44} dur={20} style={card(0)}>
        <Panel style={panel} glow="rgba(124, 139, 255, 0.36)">
          <Label>Risk levels</Label>
          <div style={{display: 'flex', alignItems: 'center', gap: 30, marginTop: 26}}>
            <Donut sweep={sweep} size={226} />
            <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
              {TIER_NAMES.map((tier, i) => (
                <Rise key={tier} at={44 + i * 6} style={{display: 'flex', alignItems: 'center', gap: 12}}>
                  <i style={{width: 13, height: 13, borderRadius: '50%', background: C.tiers[i], boxShadow: `0 0 14px ${C.tiers[i]}`}} />
                  <span style={{flex: 1, fontSize: 26, fontWeight: 600}}>{tier}</span>
                  <span style={{fontFamily: MONO, fontSize: 26, fontVariantNumeric: 'tabular-nums'}}>{Math.round(TOTALS.tiers[i] * prog(frame, 46 + i * 6, 76 + i * 6))}</span>
                </Rise>
              ))}
            </div>
          </div>
          <div style={{position: 'absolute', left: 36, right: 36, bottom: 32, paddingTop: 22, borderTop: `1px solid ${C.hair}`, display: 'flex', alignItems: 'baseline', gap: 14, opacity: prog(frame, 66, 80)}}>
            <span style={{fontSize: 76, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.round(INSIGHTS.mean * prog(frame, 70, 100))}</span>
            <span style={{fontFamily: MONO, fontSize: 24, color: C.faint}}>/100</span>
            <span style={{marginLeft: 8, fontSize: 24, lineHeight: 1.3, color: C.dim}}>average score<br />{scoreTier(INSIGHTS.mean)} risk</span>
          </div>
        </Panel>
      </Rise>

      {/* Most common problems */}
      <Rise at={32} y={44} dur={20} style={card(1)}>
        <Panel style={panel} glow="rgba(255, 138, 76, 0.34)">
          <Label>Most common problems</Label>
          <div style={{marginTop: 24, display: 'flex', flexDirection: 'column', gap: 23}}>
            {INSIGHTS.problems.map((problem, i) => {
              const fill = prog(frame, 50 + i * 7, 82 + i * 7, ease.out);
              return (
                <Rise key={problem.name} at={46 + i * 7}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10}}>
                    <span style={{fontSize: 27, fontWeight: 600}}>{problem.name}</span>
                    <span style={{fontFamily: MONO, fontSize: 25, fontVariantNumeric: 'tabular-nums'}}>{Math.round(problem.share * fill)}%</span>
                  </div>
                  <Bar value={(problem.share / 100) * fill} color={C.ember2} />
                </Rise>
              );
            })}
          </div>
        </Panel>
      </Rise>

      {/* Past fires */}
      <Rise at={40} y={44} dur={20} style={card(2)}>
        <Panel style={panel} glow="rgba(255, 90, 79, 0.36)">
          <Label>Past fires</Label>
          <div style={{display: 'flex', alignItems: 'baseline', gap: 16, marginTop: 14}}>
            <span style={{fontSize: 148, fontWeight: 800, letterSpacing: '-0.05em', lineHeight: 1, fontVariantNumeric: 'tabular-nums', color: '#FFD9D2', textShadow: '0 0 54px rgba(255, 90, 79, 0.6)'}}>{lit}</span>
            <span style={{fontSize: 28, fontWeight: 600, color: C.dim}}>workshops have<br />already had a fire</span>
          </div>
          <div style={{display: 'grid', gridTemplateColumns: `repeat(${FIRE_COLUMNS}, 1fr)`, gap: 9, marginTop: 26}}>
            {Array.from({length: fires.total}, (_, i) => (
              <i key={i} style={{aspectRatio: '1', borderRadius: '50%', background: i < lit ? C.tiers[0] : 'rgba(255, 255, 255, 0.12)', boxShadow: i < lit ? `0 0 12px ${C.tiers[0]}` : 'none'}} />
            ))}
          </div>
          <Rise at={108} style={{position: 'absolute', left: 36, right: 36, bottom: 32, fontSize: 27, fontWeight: 600, lineHeight: 1.35}}>
            {fires.severe === fires.total ? 'Every one is now rated ' : `${fires.severe} of them are now rated `}
            <span style={{color: C.tiers[0]}}>severe</span>.
          </Rise>
        </Panel>
      </Rise>
    </AbsoluteFill>
  );
};
