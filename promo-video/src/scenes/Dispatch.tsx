// 0:22 – 0:28 · Dispatch. The real street route from the nearest fire post draws across the
// map while the turn card, ETA and distance count down with the engine.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {cameraAt, project} from '../camera';
import {Bar, Label, Panel, Rise, Words} from '../components/ui';
import {MONO} from '../fonts';
import {fade, prog} from '../lib/anim';
import {HERO, ROUTE, SCENES, routeProgress} from '../story';
import {C, EMBER_GRADIENT} from '../theme';

const ARROWS: Record<string, string> = {
  left: 'M9 14 4 9l5-5 M20 20v-7a4 4 0 0 0-4-4H4',
  right: 'M15 14l5-5-5-5 M4 20v-7a4 4 0 0 1 4-4h12',
  straight: 'M12 19V5 M5 12l7-7 7 7',
  arrive: 'M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z M12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
};

export const Dispatch: React.FC = () => {
  const frame = useCurrentFrame();
  const global = frame + SCENES.dispatch.from;
  const cam = cameraAt(global);
  const p = routeProgress(global);
  const travelled = p * ROUTE.metres;
  const left = Math.max(0, ROUTE.metres - travelled);
  const seconds = Math.round((1 - p) * ROUTE.seconds);

  // The manoeuvre coming up next, and how far away it is.
  const steps = ROUTE.steps;
  let next = steps.findIndex((s) => s.at > travelled + 1);
  if (next === -1) next = steps.length - 1;
  const step = p >= 1 ? steps[steps.length - 1] : steps[next];
  const toStep = Math.max(0, Math.round(step.at - travelled));
  const running = p > 0 && p < 1;
  const speed = running ? Math.round(40 + Math.sin(global / 7) * 4) : 0;

  const [sx, sy] = project(cam, ROUTE.sx, ROUTE.sy);
  const [hx, hy] = project(cam, HERO.x, HERO.y);
  const chip: React.CSSProperties = {position: 'absolute', padding: '8px 14px', borderRadius: 12, background: C.navy, border: '1px solid rgba(255,255,255,0.22)', fontSize: 21, fontWeight: 700, whiteSpace: 'nowrap'};
  const tile: React.CSSProperties = {flex: 1, padding: '14px 18px', borderRadius: 18, background: 'rgba(255, 255, 255, 0.07)'};

  return (
    <AbsoluteFill style={{opacity: fade(frame, SCENES.dispatch.dur, 1, 14)}}>
      <Rise at={30} y={40} dur={20} style={{position: 'absolute', left: 110, top: 190, width: 540}}>
        <Panel style={{padding: '30px 32px'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
            <i style={{width: 12, height: 12, borderRadius: '50%', background: C.ember, boxShadow: `0 0 ${10 + Math.sin(global / 4) * 8}px ${C.ember}`}} />
            <Label style={{color: '#FFB89A'}}>{p >= 1 ? 'Fire tender on scene' : 'Fire tender en route'}</Label>
          </div>
          <div style={{marginTop: 8, fontSize: 23, color: C.dim}}>from {ROUTE.station}</div>

          <div style={{display: 'flex', alignItems: 'center', gap: 20, marginTop: 24, padding: 18, borderRadius: 22, background: 'rgba(6, 10, 20, 0.6)', border: '1px solid rgba(255,255,255,0.08)'}}>
            <div style={{width: 78, height: 78, borderRadius: 20, background: EMBER_GRADIENT, display: 'grid', placeItems: 'center', boxShadow: '0 16px 30px -12px rgba(240, 69, 47, 0.8)'}}>
              <svg width={42} height={42} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"><path d={ARROWS[step.dir] || ARROWS.straight} /></svg>
            </div>
            <div>
              <div style={{fontSize: 42, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1}}>{step.label}</div>
              <div style={{fontFamily: MONO, fontSize: 23, color: C.dim, fontVariantNumeric: 'tabular-nums'}}>{p >= 1 ? 'at the workshop lane' : `in ${toStep} m`}</div>
            </div>
          </div>

          <div style={{display: 'flex', gap: 12, marginTop: 16}}>
            {[
              ['ETA', `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`],
              ['Remaining', left >= 1000 ? `${(left / 1000).toFixed(1)} km` : `${Math.round(left)} m`],
              ['Speed', `${speed} km/h`],
            ].map(([label, value]) => (
              <div key={label} style={tile}>
                <div style={{fontSize: 19, color: C.faint}}>{label}</div>
                <div style={{fontSize: 31, fontWeight: 800, letterSpacing: '-0.02em', fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap'}}>{value}</div>
              </div>
            ))}
          </div>
          <Bar value={p} color={C.ember2} height={10} style={{marginTop: 18}} />
        </Panel>
      </Rise>

      <div style={{position: 'absolute', left: 110, top: 800}}>
        <Words text="Routes the nearest engine." at={12} size={64} />
        <Words text="Turn by turn." at={24} size={64} accent={['Turn', 'by', 'turn']} />
      </div>

      {/* Labels pinned to the map */}
      <div style={{...chip, left: sx, top: sy - 30, transform: 'translate(-12%, -100%)', opacity: prog(frame, 38, 50)}}>{ROUTE.station}</div>
      <div style={{...chip, left: hx, top: hy - 34, transform: 'translate(-82%, -100%)', opacity: prog(frame, 44, 56)}}>{HERO.name}</div>
    </AbsoluteFill>
  );
};
