// 0:28 – 0:34 · The hose relay. Where the engine has to stop, the hose runs on: the line lays
// itself down the lane coupling by coupling while the distance counts up beside it.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {cameraAt, project} from '../camera';
import {Label, Pop, Rise, Words} from '../components/ui';
import {MONO} from '../fonts';
import {fade, prog} from '../lib/anim';
import {HERO, RELAY, SCENES, hoseProgress} from '../story';
import {C} from '../theme';

export const Relay: React.FC = () => {
  const frame = useCurrentFrame();
  const global = frame + SCENES.relay.from;
  const cam = cameraAt(global);
  const metres = Math.round(RELAY.run * hoseProgress(global));
  const [sx, sy] = project(cam, RELAY.sx, RELAY.sy);
  const [hx, hy] = project(cam, HERO.x, HERO.y);
  const time = `${Math.floor(RELAY.seconds / 60)}m ${String(RELAY.seconds % 60).padStart(2, '0')}s`;
  const tiles: [string, string, boolean][] = [
    [`${RELAY.lengths} × 30 m`, 'hose lengths', false],
    [time, 'until water reaches the door', false],
    [`${RELAY.pressure} bar`, 'pump pressure', false],
    RELAY.booster ? ['Booster pump', `needed near the ${Math.round(RELAY.run / 2)} m mark`, true] : ['Direct pumping', 'no booster needed', false],
  ];
  const chip: React.CSSProperties = {position: 'absolute', padding: '9px 15px', borderRadius: 12, background: C.navy, border: '1px solid rgba(255,255,255,0.22)', fontSize: 22, fontWeight: 700, whiteSpace: 'nowrap'};
  return (
    <AbsoluteFill style={{opacity: fade(frame, SCENES.relay.dur, 1, 14)}}>
      <div style={{position: 'absolute', left: 1010, top: 176}}>
        <Words text="Where the road ends," at={12} size={66} />
        <Words text="the hose relay begins." at={24} size={66} accent={['hose', 'relay']} />
      </div>

      <Rise at={40} style={{position: 'absolute', left: 1010, top: 372}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 14}}>
          <span style={{fontSize: 208, fontWeight: 800, letterSpacing: '-0.055em', lineHeight: 1, fontVariantNumeric: 'tabular-nums', color: '#DCEBFF', textShadow: '0 0 60px rgba(90, 169, 255, 0.55)'}}>{metres}</span>
          <span style={{fontSize: 80, fontWeight: 800, color: C.water}}>m</span>
        </div>
        <Label style={{marginTop: 4, color: C.dim}}>of hose from {RELAY.road}</Label>
      </Rise>

      <div style={{position: 'absolute', left: 1010, top: 682, width: 800, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16}}>
        {tiles.map(([value, label, alert], i) => (
          <Pop key={label} at={64 + i * 7}>
            <div style={{padding: '20px 24px', borderRadius: 22, background: alert ? 'rgba(240, 69, 47, 0.16)' : 'rgba(255, 255, 255, 0.07)', border: `1px solid ${alert ? 'rgba(255, 138, 76, 0.55)' : 'rgba(255, 255, 255, 0.10)'}`}}>
              <div style={{fontSize: 42, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.15, color: alert ? '#FFC9AE' : C.text, whiteSpace: 'nowrap'}}>{value}</div>
              <div style={{marginTop: 4, fontSize: 21, color: C.dim, whiteSpace: 'nowrap'}}>{label}</div>
            </div>
          </Pop>
        ))}
      </div>

      {/* Labels pinned to the map */}
      <div style={{...chip, left: sx + 50, top: sy - 24, opacity: prog(frame, 38, 50)}}>
        Tender stages here <span style={{fontFamily: MONO, fontWeight: 400, color: C.dim, marginLeft: 8}}>{RELAY.roadWidth} m road</span>
      </div>
      <div style={{...chip, left: hx + 46, top: hy - 24, opacity: prog(frame, 132, 144)}}>Water at the door</div>
    </AbsoluteFill>
  );
};
