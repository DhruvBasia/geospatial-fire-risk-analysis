// The parts of the frame that are not a scene: the backdrop, the readability scrims, the
// live coordinate read-out and the logo lockup that travels through the film.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {cameraAt, cameraLatLng} from '../camera';
import {DEVANAGARI, MONO} from '../fonts';
import {clamp, ease, lerp, prog, spring, track} from '../lib/anim';
import {APP, APP_HINDI, APP_MEANING, at} from '../story';
import {C, DURATION, H, W} from '../theme';
import {Mark} from './ui';

/** Deep navy field with slow colour washes, a fine survey grid and a vignette. */
export const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 40;
  return (
    <AbsoluteFill style={{
      background: `radial-gradient(1100px 700px at ${82 + drift / 40}% -6%, rgba(240, 69, 47, 0.30), transparent 62%),
        radial-gradient(1000px 760px at ${4 - drift / 50}% 108%, rgba(76, 95, 213, 0.36), transparent 62%),
        linear-gradient(160deg, #0D1629 0%, ${C.bg} 70%)`,
    }}>
      <AbsoluteFill style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
        backgroundSize: '60px 60px', backgroundPosition: `${-frame * 0.12}px ${-frame * 0.07}px`,
      }} />
    </AbsoluteFill>
  );
};

/** Gradients that keep text legible over the map; each side lights only when a scene puts type there. */
export const Scrims: React.FC = () => {
  const frame = useCurrentFrame();
  const left = track(frame, [
    [0, 1], [at('reveal', 6), 1], [at('reveal', 22), 0], [at('reveal', 88), 0], [at('reveal', 110), 1],
    [at('risk', 0), 1], [at('risk', 27), 0.55], [at('dispatch', -4), 0.55], [at('dispatch', 14), 1],
    [at('relay', -4), 1], [at('relay', 20), 0], [DURATION, 0],
  ]);
  const right = track(frame, [[at('relay', 0), 0], [at('relay', 30), 1], [at('insights', -2), 1], [at('insights', 20), 0]]);
  const centre = track(frame, [
    [at('reveal', 2), 0], [at('reveal', 20), 1], [at('reveal', 86), 1], [at('reveal', 110), 0],
    [at('insights', 0), 0], [at('insights', 26), 1], [DURATION, 1],
  ]);
  const edge = `linear-gradient(90deg, rgba(6,10,20,0.94) 0%, rgba(6,10,20,0.82) 30%, rgba(6,10,20,0) 58%)`;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: edge, opacity: left}} />
      <AbsoluteFill style={{background: edge, opacity: right, transform: 'scaleX(-1)'}} />
      <AbsoluteFill style={{background: 'radial-gradient(1200px 760px at 50% 48%, rgba(6,10,20,0.90), rgba(6,10,20,0.55) 60%, rgba(6,10,20,0.25))', opacity: centre}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.55) 100%)'}} />
    </AbsoluteFill>
  );
};

/** Coordinates and map scale of whatever the camera is looking at, plus corner registration marks. */
export const Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = cameraAt(frame);
  const {lat, lng} = cameraLatLng(cam);
  const scale = Math.round(1 / (cam.z * 0.0002646) / 10) * 10; // 1 CSS pixel is 0.2646 mm
  const readout = prog(frame, 20, 40) * (1 - prog(frame, at('insights', -6), at('insights', 14)));
  const corner = (x: number, y: number, sx: number, sy: number) => (
    <path d={`M${x} ${y + 34 * sy} V${y} H${x + 34 * sx}`} fill="none" stroke="rgba(255,255,255,0.42)" strokeWidth={2} />
  );
  return (
    <AbsoluteFill>
      <svg width={W} height={H} style={{opacity: prog(frame, 20, 40)}}>
        {corner(44, 44, 1, 1)}{corner(W - 44, 44, -1, 1)}{corner(44, H - 44, 1, -1)}{corner(W - 44, H - 44, -1, -1)}
      </svg>
      <div style={{position: 'absolute', right: 96, bottom: 62, display: 'flex', alignItems: 'center', gap: 22, fontFamily: MONO, fontSize: 20, color: C.dim, fontVariantNumeric: 'tabular-nums', opacity: readout}}>
        <svg width={22} height={22} viewBox="0 0 24 24" fill="none" stroke={C.ember2} strokeWidth={2}>
          <circle cx={12} cy={12} r={7} /><path d="M12 1v6M12 17v6M1 12h6M17 12h6" />
        </svg>
        <span>{lat.toFixed(5)}° N</span>
        <span>{lng.toFixed(5)}° E</span>
        <span style={{color: C.faint}}>1 : {scale.toLocaleString('en-US')}</span>
      </div>
    </AbsoluteFill>
  );
};

/** The logo. It arrives centre-frame with the name in Hindi, parks in the corner while the product
 *  is shown, then returns for the close. Position is the centre of the mark-and-name row. */
export const Lockup: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < at('reveal', 6)) return null;
  const toCorner = prog(frame, at('reveal', 88), at('reveal', 118), ease.inOut);
  const toClose = prog(frame, at('close', 0), at('close', 30), ease.inOut);
  const x = lerp(lerp(960, 240, toCorner), 960, toClose);
  const y = lerp(lerp(432, 96, toCorner), 286, toClose);
  const scale = lerp(lerp(1.1, 0.3, toCorner), 0.78, toClose);
  const open = spring(frame, at('reveal', 10), {stiffness: 150, damping: 15});
  const sub = prog(frame, at('reveal', 44), at('reveal', 58)) * (1 - prog(frame, at('reveal', 76), at('reveal', 88)));
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) scale(${scale})`}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 36}}>
        <div style={{transform: `scale(${0.6 + 0.4 * clamp(open)})`, opacity: clamp(open * 2)}}><Mark size={156} open={open} /></div>
        <div style={{fontSize: 138, fontWeight: 800, letterSpacing: '-0.045em', lineHeight: 1, whiteSpace: 'nowrap'}}>
          {APP.split('').map((ch, i) => {
            const p = prog(frame, at('reveal', 16) + i * 2, at('reveal', 32) + i * 2, ease.outQuint);
            return <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 46}px)`}}>{ch}</span>;
          })}
        </div>
      </div>
      {/* Under the name: how it is written in Hindi, and what it means */}
      <div style={{position: 'absolute', left: '50%', top: '100%', transform: `translate(-50%, ${(1 - sub) * 14}px)`, marginTop: 30, opacity: sub, textAlign: 'center', whiteSpace: 'nowrap'}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22, color: C.text}}>
          <span style={{fontFamily: DEVANAGARI, fontSize: 56, fontWeight: 600, lineHeight: 1.3}}>{APP_HINDI}</span>
          <span style={{width: 7, height: 7, borderRadius: '50%', background: C.ember2}} />
          <span style={{fontSize: 40, fontWeight: 600, color: C.dim}}>“{APP_MEANING}”</span>
        </div>
        <div style={{marginTop: 18, fontFamily: MONO, fontSize: 26, letterSpacing: '0.3em', textTransform: 'uppercase', color: C.faint}}>Seelampur Fire Risk Atlas</div>
      </div>
    </div>
  );
};
