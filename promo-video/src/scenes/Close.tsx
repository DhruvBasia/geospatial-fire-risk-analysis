// 0:40 – 0:44 · The close. The logo returns to centre (see Lockup), the product's own tagline
// rises under it, and a cursor clicks the live address.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Rise, Tag, Typed, Words} from '../components/ui';
import {clamp, ease, lerp, prog} from '../lib/anim';
import {LIVE_URL, TOTALS} from '../story';
import {C} from '../theme';

const CLICK = 76;

export const Close: React.FC = () => {
  const frame = useCurrentFrame();
  const press = clamp(1 - Math.abs(frame - (CLICK + 2)) / 4); // a quick squeeze on the click
  const travel = prog(frame, 58, 74, ease.inOut);
  const cursorX = lerp(1400, 1150, travel), cursorY = lerp(940, 716, travel);
  const ripple = prog(frame, CLICK, CLICK + 16, ease.out);
  return (
    <AbsoluteFill style={{opacity: prog(frame, 0, 8, ease.linear)}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 452, textAlign: 'center'}}>
        <Words text="See which workshops are at risk," at={16} size={62} />
        <Words text="and reach them fast." at={26} size={62} accent={['and', 'reach', 'them', 'fast']} />
      </div>

      <Rise at={36} style={{position: 'absolute', left: 0, right: 0, top: 664, display: 'flex', justifyContent: 'center'}}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 16, height: 88, padding: '0 34px', borderRadius: 999, transform: `scale(${1 - press * 0.035})`,
          border: '1.5px solid transparent',
          background: 'linear-gradient(#101A30, #0B1220) padding-box, linear-gradient(110deg, rgba(255, 150, 96, 0.95), rgba(255, 255, 255, 0.18) 40%, rgba(124, 139, 255, 0.85)) border-box',
          boxShadow: `0 30px 70px -30px rgba(240, 69, 47, ${0.55 + press * 0.4})`,
        }}>
          <svg width={30} height={30} viewBox="0 0 24 24" fill="none" stroke={C.ember2} strokeWidth={1.8}><circle cx={12} cy={12} r={9} /><path d="M3 12h18M12 3c3 3.2 3 14.800 0 18M12 3c-3 3.2-3 14.800 0 18" /></svg>
          <Typed text={LIVE_URL} at={40} perFrame={2} linger={8} style={{fontSize: 36, color: C.text}} />
        </div>
      </Rise>

      <div style={{position: 'absolute', left: 0, right: 0, top: 800, display: 'flex', justifyContent: 'center', gap: 14}}>
        <Rise at={50}><Tag color={C.indigo}>Open source</Tag></Rise>
        <Rise at={54}><Tag color={C.tiers[3]}>Live on Render</Tag></Rise>
        <Rise at={58}><Tag color={C.ember2}>{TOTALS.workshops} workshops mapped</Tag></Rise>
      </div>

      {/* Cursor travels to the address and clicks */}
      {ripple > 0 && ripple < 1 ? (
        <div style={{position: 'absolute', left: cursorX - 40, top: cursorY - 40, width: 80, height: 80, borderRadius: '50%', border: `3px solid ${C.ember2}`, transform: `scale(${0.3 + ripple * 1.1})`, opacity: 1 - ripple}} />
      ) : null}
      <svg width={40} height={40} viewBox="0 0 24 24" style={{position: 'absolute', left: cursorX, top: cursorY, opacity: prog(frame, 54, 60), transform: `scale(${1 - press * 0.12})`, filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.6))'}}>
        <path d="M5 3l14 8-6 1.600L10 19z" fill="#fff" stroke={C.navy} strokeWidth={1.4} strokeLinejoin="round" />
      </svg>
    </AbsoluteFill>
  );
};
