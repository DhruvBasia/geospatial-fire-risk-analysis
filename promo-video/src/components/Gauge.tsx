// Radial risk gauge. The arc, the number and the tier label all follow one value, so as the
// score climbs the gauge passes through Low, Moderate and High before it settles on Severe.
import React from 'react';
import {MONO} from '../fonts';
import {clamp} from '../lib/anim';
import {C, scoreColor, scoreTier} from '../theme';

const SWEEP = 270; // degrees of arc
const START = 135; // arc begins bottom-left

export const Gauge: React.FC<{value: number; size?: number; settled?: number}> = ({value, size = 360, settled = 0}) => {
  const r = 150, cx = 180, cy = 180, stroke = 22;
  const circumference = 2 * Math.PI * r;
  const arc = circumference * (SWEEP / 360);
  const v = clamp(value / 100);
  const color = scoreColor(value);
  const angle = ((START + SWEEP * v) * Math.PI) / 180;
  const tipX = cx + Math.cos(angle) * r, tipY = cy + Math.sin(angle) * r;
  const tick = (score: number, long: boolean) => {
    const a = ((START + (SWEEP * score) / 100) * Math.PI) / 180;
    const r1 = r + stroke / 2 + 8, r2 = r1 + (long ? 16 : 8);
    return <line key={score} x1={cx + Math.cos(a) * r1} y1={cy + Math.sin(a) * r1} x2={cx + Math.cos(a) * r2} y2={cy + Math.sin(a) * r2} stroke={long ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.25)'} strokeWidth={long ? 3 : 2} strokeLinecap="round" />;
  };
  return (
    <div style={{position: 'relative', width: size, height: size}}>
      <svg width={size} height={size} viewBox="-20 -20 400 400" style={{display: 'block', overflow: 'visible'}}>
        {/* Scale ticks; the tier thresholds at 30, 50 and 70 are marked longer */}
        {Array.from({length: 11}, (_, i) => tick(i * 10, [30, 50, 70].includes(i * 10)))}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255, 255, 255, 0.10)" strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={`${arc} ${circumference}`} transform={`rotate(${START} ${cx} ${cy})`} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={stroke + 16} strokeLinecap="round" opacity={0.2}
          strokeDasharray={`${arc * v} ${circumference}`} transform={`rotate(${START} ${cx} ${cy})`} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={`${arc * v} ${circumference}`} transform={`rotate(${START} ${cx} ${cy})`} />
        <circle cx={tipX} cy={tipY} r={7} fill="#fff" />
        {/* A ring that flashes outward when the count lands */}
        {settled > 0 && settled < 1 ? <circle cx={cx} cy={cy} r={r + 30 + settled * 50} fill="none" stroke={color} strokeWidth={3} opacity={1 - settled} /> : null}
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingBottom: 14}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 4}}>
          <span style={{fontSize: size * 0.34, fontWeight: 800, letterSpacing: '-0.05em', lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.round(value)}</span>
          <span style={{fontFamily: MONO, fontSize: size * 0.075, color: C.faint}}>/100</span>
        </div>
        <div style={{marginTop: 6, fontFamily: MONO, fontSize: size * 0.05, letterSpacing: '0.14em', textTransform: 'uppercase', color: C.faint}}>Fire Risk Index</div>
        <div style={{marginTop: 14, display: 'inline-flex', alignItems: 'center', gap: 10, height: size * 0.115, padding: `0 ${size * 0.05}px`, borderRadius: 999, background: 'rgba(255,255,255,0.10)', fontSize: size * 0.062, fontWeight: 700}}>
          <i style={{width: 11, height: 11, borderRadius: '50%', background: color, boxShadow: `0 0 14px ${color}`}} />
          {scoreTier(value)} risk
        </div>
      </div>
    </div>
  );
};
