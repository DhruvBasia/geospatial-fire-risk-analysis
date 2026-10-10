// 0:15 – 0:22 · The risk score. The camera dives to one real workshop and its card builds:
// the gauge counts from 0 to its Fire Risk Index, then the three areas are graded in plain words.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {cameraAt, project} from '../camera';
import {Gauge} from '../components/Gauge';
import {Bar, Label, Panel, Pop, Rise, Tag, Words} from '../components/ui';
import {MONO} from '../fonts';
import {ease, fade, lerp, prog} from '../lib/anim';
import {GAUGE_END, GAUGE_START, HERO, SCENES} from '../story';
import {C, GRADE_COLOR, H, W} from '../theme';

const FINDINGS = ['Single exit', 'Blocked escape path', 'No fire exit', 'Shared wall'];
const GRADES = ['Critical', 'Poor', 'Fair', 'Good'];
const CARD = {left: 1040, top: 172, width: 770, height: 736};

export const Risk: React.FC = () => {
  const frame = useCurrentFrame();
  const global = frame + SCENES.risk.from;
  const [hx, hy] = project(cameraAt(global), HERO.x, HERO.y);
  const score = lerp(0, HERO.score, prog(global, GAUGE_START, GAUGE_END, ease.out));
  const settled = prog(global, GAUGE_END, GAUGE_END + 18, ease.linear);
  const link = prog(frame, 34, 54, ease.inOut);
  return (
    <AbsoluteFill style={{opacity: fade(frame, SCENES.risk.dur, 1, 14)}}>
      <div style={{position: 'absolute', left: 110, top: 190}}>
        <Words text="Every workshop gets" at={12} size={64} />
        <Words text="a score out of 100." at={22} size={64} accent={['100']} />
      </div>

      {/* Leader line from the workshop on the map to its card */}
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <path d={`M${hx + 30} ${hy} H${CARD.left - 70} V${CARD.top + 250} H${CARD.left}`} fill="none" stroke="rgba(255, 255, 255, 0.55)" strokeWidth={2}
          pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - link} />
      </svg>
      <Pop at={40} style={{position: 'absolute', left: hx + 34, top: hy - 74}}>
        <span style={{fontFamily: MONO, fontSize: 22, padding: '6px 12px', borderRadius: 10, background: C.navy, border: '1px solid rgba(255,255,255,0.25)'}}>{HERO.id}</span>
      </Pop>

      <Rise at={28} y={44} dur={20} style={{position: 'absolute', left: CARD.left, top: CARD.top, width: CARD.width, height: CARD.height}}>
        <Panel style={{width: '100%', height: '100%', padding: '38px 42px'}}>
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
            <Label>Workshop {HERO.id} · {HERO.locality}</Label>
            {HERO.pastFire ? <Tag color={C.tiers[0]} style={{height: 38, fontSize: 19}}>Had a fire before</Tag> : null}
          </div>
          <div style={{marginTop: 12, fontSize: 44, fontWeight: 800, letterSpacing: '-0.03em', whiteSpace: 'nowrap'}}>{HERO.name}</div>

          <div style={{display: 'flex', alignItems: 'center', gap: 36, marginTop: 26}}>
            <Gauge value={score} size={310} settled={settled} />
            <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 30}}>
              {HERO.areas.map((area, i) => {
                const fill = prog(frame, 88 + i * 12, 112 + i * 12, ease.out);
                return (
                  <Rise key={area.name} at={84 + i * 12}>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10}}>
                      <span style={{fontSize: 24, fontWeight: 600, color: C.dim, whiteSpace: 'nowrap'}}>{area.name}</span>
                      <span style={{fontSize: 25, fontWeight: 800, color: GRADE_COLOR[area.grade], opacity: prog(frame, 106 + i * 12, 114 + i * 12)}}>{area.grade}</span>
                    </div>
                    <Bar value={area.value * fill} color={GRADE_COLOR[area.grade]} />
                  </Rise>
                );
              })}
            </div>
          </div>

          <div style={{position: 'absolute', left: 42, right: 42, bottom: 38}}>
            <Rise at={124}><Label style={{marginBottom: 16}}>What the survey found</Label></Rise>
            <div style={{display: 'flex', flexWrap: 'wrap', gap: 12}}>
              {FINDINGS.map((text, i) => <Pop key={text} at={131 + i * 7}><Tag color={C.tiers[0]}>{text}</Tag></Pop>)}
            </div>
          </div>
        </Panel>
      </Rise>

      <div style={{position: 'absolute', left: 110, top: 862}}>
        <Rise at={104}><Label style={{marginBottom: 16}}>Graded in plain words</Label></Rise>
        <div style={{display: 'flex', gap: 12}}>
          {GRADES.map((g, i) => <Pop key={g} at={112 + i * 8}><Tag color={GRADE_COLOR[g]}>{g}</Tag></Pop>)}
        </div>
      </div>
    </AbsoluteFill>
  );
};
