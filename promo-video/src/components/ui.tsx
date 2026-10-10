// Motion-graphic building blocks. Each one animates from the current frame of the scene it is in.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {MONO} from '../fonts';
import {clamp, ease, lerp, prog, spring} from '../lib/anim';
import {C, EMBER_GRADIENT} from '../theme';

type Style = React.CSSProperties;

/** Fades and lifts its children into place. */
export const Rise: React.FC<{at: number; dur?: number; y?: number; style?: Style; children: React.ReactNode}> = ({at, dur = 16, y = 26, style, children}) => {
  const frame = useCurrentFrame();
  const p = prog(frame, at, at + dur);
  return <div style={{opacity: p, transform: `translateY(${(1 - p) * y}px)`, ...style}}>{children}</div>;
};

/** Pops its children in with a small overshoot. */
export const Pop: React.FC<{at: number; style?: Style; children: React.ReactNode}> = ({at, style, children}) => {
  const frame = useCurrentFrame();
  const s = spring(frame, at, {stiffness: 240, damping: 15});
  return <div style={{opacity: clamp(s * 1.6), transform: `scale(${0.82 + 0.18 * s})`, ...style}}>{children}</div>;
};

/** Kinetic typography: words rise and sharpen one after another. `accent` words take the ember gradient. */
export const Words: React.FC<{text: string; at: number; size: number; stagger?: number; weight?: number; color?: string; accent?: string[]; style?: Style}> = ({
  text, at, size, stagger = 3, weight = 800, color = C.text, accent = [], style,
}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{fontSize: size, fontWeight: weight, letterSpacing: '-0.035em', lineHeight: 1.04, color, ...style}}>
      {text.split(' ').map((word, i) => {
        const p = prog(frame, at + i * stagger, at + i * stagger + 15, ease.outQuint);
        const lit = accent.includes(word.replace(/[.,]/g, ''));
        return (
          <span key={i} style={{
            display: 'inline-block', marginRight: '0.24em', opacity: p,
            transform: `translateY(${(1 - p) * 0.42}em)`, filter: p < 1 ? `blur(${(1 - p) * 9}px)` : undefined,
            ...(lit ? {backgroundImage: EMBER_GRADIENT, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'} : {}),
          }}>{word}</span>
        );
      })}
    </div>
  );
};

/** A number that counts between two values. */
export const useCount = (from: number, to: number, at: number, dur: number) => {
  const frame = useCurrentFrame();
  return Math.round(lerp(from, to, prog(frame, at, at + dur, ease.out)));
};

/** Text that types itself, with a block cursor. */
export const Typed: React.FC<{text: string; at: number; perFrame?: number; style?: Style; cursor?: string; linger?: number}> = ({text, at, perFrame = 1, style, cursor = C.ember2, linger = 9999}) => {
  const frame = useCurrentFrame();
  const n = clamp(Math.floor((frame - at) * perFrame), 0, text.length);
  const typing = n < text.length;
  const gone = frame > at + text.length / perFrame + linger;
  const blink = !gone && (typing || Math.floor(frame / 8) % 2 === 0);
  return (
    <span style={{fontFamily: MONO, whiteSpace: 'pre', ...style}}>
      {text.slice(0, n)}
      <span style={{display: 'inline-block', width: '0.55em', height: '1em', marginLeft: 3, verticalAlign: '-0.12em', background: cursor, opacity: frame >= at && blink ? 0.95 : 0}} />
    </span>
  );
};

/** Dark glass panel with a lit top edge. */
export const Panel: React.FC<{style?: Style; glow?: string; children: React.ReactNode}> = ({style, glow = 'rgba(255, 122, 69, 0.34)', children}) => (
  <div style={{
    position: 'relative', boxSizing: 'border-box', overflow: 'hidden', borderRadius: 30,
    background: `radial-gradient(520px 320px at 100% 0%, ${glow}, transparent 70%), linear-gradient(160deg, rgba(30, 42, 72, 0.96), rgba(11, 18, 32, 0.97))`,
    border: '1px solid rgba(255, 255, 255, 0.12)',
    boxShadow: '0 50px 110px -40px rgba(0, 0, 0, 0.85), inset 0 1px 0 rgba(255, 255, 255, 0.10)',
    ...style,
  }}>{children}</div>
);

/** Small mono label, letter-spaced. */
export const Label: React.FC<{style?: Style; children: React.ReactNode}> = ({style, children}) => (
  <div style={{fontFamily: MONO, fontSize: 20, letterSpacing: '0.16em', textTransform: 'uppercase', color: C.faint, ...style}}>{children}</div>
);

/** Rounded tag. */
export const Tag: React.FC<{color?: string; style?: Style; children: React.ReactNode}> = ({color, style, children}) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', gap: 10, height: 44, padding: '0 18px', borderRadius: 999,
    background: 'rgba(255, 255, 255, 0.08)', border: '1px solid rgba(255, 255, 255, 0.12)', fontSize: 22, fontWeight: 700, whiteSpace: 'nowrap', ...style,
  }}>
    {color ? <i style={{width: 11, height: 11, borderRadius: '50%', background: color, boxShadow: `0 0 14px ${color}`}} /> : null}
    {children}
  </span>
);

/** Horizontal bar that fills to `value` (0–1). */
export const Bar: React.FC<{value: number; color: string; height?: number; style?: Style}> = ({value, color, height = 12, style}) => (
  <div style={{height, borderRadius: 999, background: 'rgba(255, 255, 255, 0.10)', overflow: 'hidden', ...style}}>
    <div style={{width: `${clamp(value) * 100}%`, height: '100%', borderRadius: 999, background: color, boxShadow: `0 0 18px ${color}`}} />
  </div>
);

/** The AgniDrishti mark: fire on the left, held back by a clean break. `open` (0–1) slides the two halves together. */
export const Mark: React.FC<{size: number; open?: number}> = ({size, open = 1}) => {
  const slide = (1 - clamp(open)) * 16;
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" style={{display: 'block', filter: 'drop-shadow(0 14px 30px rgba(240, 69, 47, 0.45))'}}>
      <defs>
        <linearGradient id="mk-tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#1F2B4D" /><stop offset="1" stopColor="#0B1220" /></linearGradient>
        <linearGradient id="mk-fire" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stopColor="#FFB25E" /><stop offset="0.55" stopColor="#F0452F" /><stop offset="1" stopColor="#D7263D" /></linearGradient>
      </defs>
      <rect x="1" y="1" width="62" height="62" rx="16" fill="url(#mk-tile)" stroke="#FFFFFF" strokeOpacity="0.16" />
      <path fill="url(#mk-fire)" opacity={clamp(open * 1.4)} transform={`translate(${-slide} ${slide * 0.6})`} d="M14 50V26c0-6.600 5.400-12 12-12h9L20 50z" />
      <path fill="#F5F7FF" opacity={clamp(open * 1.4)} transform={`translate(${slide} ${-slide * 0.6})`} d="M30 50l15-36h5v24c0 6.600-5.400 12-12 12z" />
    </svg>
  );
};
