// The living map. Drawn entirely from the survey's own geometry: Seelampur's street network,
// the study-area outline, the 148 workshops, the real street route to the hero unit and its
// hose relay. Nothing here is a screenshot.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import atlas from '../data/atlas.json';
import {cameraAt, project} from '../camera';
import {blend, clamp, css, ease, prog, rgb, spring, track} from '../lib/anim';
import {HOSE_WINDOW, ROUTE_WINDOW, at, couplingFrame, hoseProgress, routeProgress} from '../story';
import {C, DURATION, H, W} from '../theme';

const HERO = atlas.hero;
const RELAY = HERO.relay;
const ROUTE = atlas.route.points as number[][];
type Point = (typeof atlas.points)[number];

const SLATE = rgb(C.slate);
const NO_ACCESS = rgb(C.tiers[0]);
const TIGHT = rgb(C.ember2);
const TIER_RGB = C.tiers.map(rgb);

// ---- Route geometry -------------------------------------------------------------------------
const routeCum = [0];
for (let i = 1; i < ROUTE.length; i++) routeCum.push(routeCum[i - 1] + Math.hypot(ROUTE[i][0] - ROUTE[i - 1][0], ROUTE[i][1] - ROUTE[i - 1][1]));
const routeLength = routeCum[routeCum.length - 1];

/** Point on a polyline `dist` map-metres from its start, with the heading there. */
const along = (pts: number[][], cum: number[], dist: number) => {
  const d = clamp(dist, 0, cum[cum.length - 1]);
  let i = 1;
  while (i < cum.length - 1 && cum[i] < d) i++;
  const a = pts[i - 1], b = pts[i];
  const t = (d - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
  return {x: a[0] + (b[0] - a[0]) * t, y: a[1] + (b[1] - a[1]) * t, angle: (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI, index: i};
};
const slice = (pts: number[][], cum: number[], dist: number) => {
  const head = along(pts, cum, dist);
  return [...pts.slice(0, head.index), [head.x, head.y]];
};

// ---- Hose relay geometry: couplings evenly spaced, nudged alternately off the axis ------------
const hose: number[][] = (() => {
  const a = [RELAY.sx, RELAY.sy], b = [HERO.x, HERO.y];
  const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
  const nx = -(b[1] - a[1]) / len, ny = (b[0] - a[0]) / len;
  const pts = [a];
  for (let i = 1; i < RELAY.lengths; i++) {
    const r = i / RELAY.lengths, k = (i % 2 ? 1 : -1) * 5;
    pts.push([a[0] + (b[0] - a[0]) * r + nx * k, a[1] + (b[1] - a[1]) * r + ny * k]);
  }
  pts.push(b);
  return pts;
})();
const hoseCum = [0];
for (let i = 1; i < hose.length; i++) hoseCum.push(hoseCum[i - 1] + Math.hypot(hose[i][0] - hose[i - 1][0], hose[i][1] - hose[i - 1][1]));
const hoseLength = hoseCum[hoseCum.length - 1];
const HOSE_COUPLINGS = hose.slice(1, -1);

export const Atlas: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = cameraAt(frame);
  const toScreen = (p: number[]) => project(cam, p[0], p[1]);
  const line = (pts: number[][]) => pts.map((p) => toScreen(p).map((v) => v.toFixed(1)).join(',')).join(' ');

  // The map as a whole: fades up at the start, sinks back behind the logo, the charts and the close.
  const mapAlpha = track(frame, [
    [0, 0], [16, 1],
    [at('reveal', 6), 1], [at('reveal', 26), 0.3], [at('reveal', 84), 0.3], [at('reveal', 110), 1],
    [at('insights', 0), 1], [at('insights', 26), 0.28], [at('close', 0), 0.28], [at('close', 26), 0.34], [DURATION, 0.34],
  ]);
  // A radar sweep reveals the street network outward from the centre.
  const scanRadius = prog(frame, 4, 84, ease.out) * 1900;
  const scanGlow = 1 - prog(frame, 30, 84, ease.linear);
  const outlineAlpha = prog(frame, 36, 66) * track(frame, [[at('risk', -5), 1], [at('risk', 35), 0.35], [at('insights', 0), 0.35], [at('insights', 30), 0.9]]);
  const streetWidth = 0.5 + 1.0 * Math.sqrt(cam.z);
  const roadWidth = 1.2 + 2.3 * Math.sqrt(cam.z);

  // Workshops. Their colour tells the story in three steps: no engine access (red), then standing
  // within a metre of the next building (amber, with a ripple), then each one's own risk level.
  const dotRadius = 4.6 + 1.5 * Math.sqrt(cam.z);
  const dimOthers = track(frame, [[at('risk', 5), 1], [at('risk', 39), 0.34], [at('insights', 0), 0.34], [at('insights', 30), 0.8]]);
  const rippleOn = prog(frame, at('problem', 160), at('problem', 172)) * (1 - prog(frame, at('reveal', 0), at('reveal', 16)));
  const dot = (p: Point) => {
    const [sx, sy] = project(cam, p.x, p.y);
    if (sx < -40 || sx > W + 40 || sy < -40 || sy > H + 40) return null;
    const appear = spring(frame, 80 + (Math.hypot(p.x, p.y) / 620) * 30, {stiffness: 220, damping: 15});
    if (appear <= 0.01) return null;
    const wave = (p.x + 470) / 940; // west to east
    const toGap = prog(frame, at('problem', 158) + wave * 24, at('problem', 172) + wave * 24);
    const toTier = prog(frame, at('reveal', 104) + wave * 36, at('reveal', 118) + wave * 36);
    const colour = css(blend(blend(p.n ? NO_ACCESS : SLATE, p.g < 2 ? TIGHT : SLATE, toGap), TIER_RGB[p.t], toTier));
    const ripple = rippleOn > 0.01 && p.g < 2 ? (((frame - at('problem', 160) - wave * 24) % 46) + 46) % 46 / 46 : -1;
    return (
      <g key={p.id} opacity={p.id === HERO.id ? 1 : dimOthers}>
        {ripple >= 0 ? <circle cx={sx} cy={sy} r={dotRadius + ripple * 26} fill="none" stroke={C.ember2} strokeWidth={2} opacity={(1 - ripple) * 0.7 * rippleOn} /> : null}
        <circle cx={sx} cy={sy} r={dotRadius * 2.5 * appear} fill={colour} opacity={0.16} />
        <circle cx={sx} cy={sy} r={dotRadius * appear} fill={colour} stroke={C.bg} strokeWidth={1.6} />
      </g>
    );
  };

  // Hero workshop: a reticle that keeps pulsing while it is the subject.
  const [hx, hy] = project(cam, HERO.x, HERO.y);
  const heroStart = at('risk', 27);
  const heroOn = prog(frame, heroStart, heroStart + 20) * (1 - prog(frame, at('insights', 0), at('insights', 18)));
  const pulse = (Math.max(0, frame - heroStart) % 44) / 44;

  // Dispatch route.
  const routeAlpha = prog(frame, at('dispatch', 30), at('dispatch', 46)) * (1 - prog(frame, at('dispatch', 184), at('dispatch', 204)));
  const travelled = routeProgress(frame) * routeLength;
  const vehicle = along(ROUTE, routeCum, travelled);
  const [vx, vy] = project(cam, vehicle.x, vehicle.y);
  const [stx, sty] = project(cam, atlas.route.sx, atlas.route.sy);
  const arrived = prog(frame, ROUTE_WINDOW[1] - 2, ROUTE_WINDOW[1] + 12);

  // Hose relay.
  const hoseAlpha = prog(frame, at('relay', 32), at('relay', 44)) * (1 - prog(frame, at('insights', 0), at('insights', 16)));
  const laid = hoseProgress(frame) * hoseLength;
  const nozzle = along(hose, hoseCum, laid);
  const [nzx, nzy] = project(cam, nozzle.x, nozzle.y);
  const [sgx, sgy] = project(cam, RELAY.sx, RELAY.sy);
  const stagingPop = spring(frame, at('relay', 34), {stiffness: 200, damping: 14});
  const reached = prog(frame, HOSE_WINDOW[1], HOSE_WINDOW[1] + 18);

  return (
    <AbsoluteFill style={{opacity: mapAlpha}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <clipPath id="atlas-scan">
            <circle cx={0} cy={0} r={scanRadius} />
          </clipPath>
        </defs>

        {/* Street network, in map space. Strokes keep a constant width on screen. */}
        <g transform={`translate(${cam.fx - cam.x * cam.z} ${cam.fy - cam.y * cam.z}) scale(${cam.z})`}>
          <g clipPath="url(#atlas-scan)" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d={atlas.roads} stroke={C.indigo} strokeWidth={roadWidth * 5} opacity={0.07} vectorEffect="non-scaling-stroke" />
            <path d={atlas.streets} stroke={C.street} strokeWidth={streetWidth} vectorEffect="non-scaling-stroke" />
            <path d={atlas.roads} stroke={C.road} strokeWidth={roadWidth} vectorEffect="non-scaling-stroke" />
            <polygon points={atlas.outline} fill="rgba(124, 139, 255, 0.05)" stroke="rgba(255, 255, 255, 0.5)" strokeWidth={1.6} strokeDasharray="7 7" vectorEffect="non-scaling-stroke" opacity={outlineAlpha} />
          </g>
          {scanGlow > 0.01 && (
            <circle cx={0} cy={0} r={scanRadius} fill="none" stroke={C.ember2} strokeWidth={2.4} opacity={scanGlow * 0.8} vectorEffect="non-scaling-stroke" />
          )}
        </g>

        {/* Everything below is positioned in frame pixels so marks stay crisp at any zoom. */}
        <g>{atlas.points.filter((p) => p.id !== HERO.id).map(dot)}</g>

        {routeAlpha > 0.01 && (
          <g opacity={routeAlpha} fill="none" strokeLinecap="round" strokeLinejoin="round">
            <polyline points={line(ROUTE)} stroke="rgba(255, 255, 255, 0.34)" strokeWidth={3} strokeDasharray="2 10" />
            <polyline points={line(slice(ROUTE, routeCum, travelled))} stroke={C.ember} strokeWidth={20} opacity={0.2} />
            <polyline points={line(slice(ROUTE, routeCum, travelled))} stroke={C.ember2} strokeWidth={7} />
            <polyline points={line(slice(ROUTE, routeCum, travelled))} stroke="#FFE3C7" strokeWidth={2} opacity={0.9} />
            {/* Station */}
            <g transform={`translate(${stx} ${sty}) scale(${spring(frame, at('dispatch', 34))})`}>
              <rect x={-17} y={-17} width={34} height={34} rx={10} fill={C.navy} stroke={C.ember2} strokeWidth={2.5} />
              <circle r={5.5} fill={C.ember2} />
            </g>
            {/* Vehicle */}
            <g transform={`translate(${vx} ${vy})`} opacity={1 - arrived}>
              <circle r={30} fill={C.ember} opacity={0.18} />
              <circle r={17} fill={C.ember} stroke="#fff" strokeWidth={3} />
              <path d="M9 0 L-6 -7 L-2.5 0 L-6 7 Z" fill="#fff" transform={`rotate(${vehicle.angle})`} />
            </g>
          </g>
        )}

        {hoseAlpha > 0.01 && (
          <g opacity={hoseAlpha} fill="none" strokeLinecap="round" strokeLinejoin="round">
            <polyline points={line(slice(hose, hoseCum, laid))} stroke={C.water} strokeWidth={24} opacity={0.16} />
            <polyline points={line(slice(hose, hoseCum, laid))} stroke={C.water} strokeWidth={8} />
            {/* Water moving through the hose */}
            <polyline points={line(slice(hose, hoseCum, laid))} stroke="#EAF4FF" strokeWidth={2.4} strokeDasharray="5 22" strokeDashoffset={-frame * 2.4} opacity={0.95} />
            {HOSE_COUPLINGS.map((c, i) => {
              const pop = spring(frame, couplingFrame(i + 1), {stiffness: 260, damping: 14});
              if (pop <= 0.01) return null;
              const [cx, cy] = toScreen(c);
              return (
                <g key={i} transform={`translate(${cx} ${cy}) scale(${pop})`}>
                  <circle r={19} fill="#fff" stroke={C.water} strokeWidth={5} />
                  <text y={7} textAnchor="middle" fontSize={19} fontWeight={800} fill={C.navy} style={{fontFamily: 'inherit'}}>{i + 1}</text>
                </g>
              );
            })}
            {/* Nozzle head */}
            <circle cx={nzx} cy={nzy} r={9} fill="#fff" stroke={C.water} strokeWidth={4} opacity={1 - reached} />
            {/* Tender staging point */}
            <g transform={`translate(${sgx} ${sgy}) scale(${stagingPop})`}>
              <rect x={-30} y={-30} width={60} height={60} rx={17} fill={C.navy} stroke={C.ember2} strokeWidth={3} />
              <g stroke="#FFD2B0" strokeWidth={2.6}>
                <rect x={-17} y={-9} width={21} height={15} rx={3} />
                <path d="M4 -5 h8 l5 6 v5 h-13 z" />
                <circle cx={-9} cy={9} r={3.6} fill={C.navy} />
                <circle cx={10} cy={9} r={3.6} fill={C.navy} />
              </g>
            </g>
          </g>
        )}

        <g>{atlas.points.filter((p) => p.id === HERO.id).map(dot)}</g>

        {heroOn > 0.01 && (
          <g opacity={heroOn} fill="none">
            <circle cx={hx} cy={hy} r={dotRadius + 10 + pulse * 46} stroke={C.tiers[0]} strokeWidth={2.5} opacity={(1 - pulse) * 0.75} />
            <circle cx={hx} cy={hy} r={dotRadius + 9} stroke="#fff" strokeWidth={2.5} />
            {[0, 90, 180, 270].map((a) => (
              <line key={a} x1={hx} y1={hy - dotRadius - 16} x2={hx} y2={hy - dotRadius - 30} stroke="#fff" strokeWidth={2.5} strokeLinecap="round" transform={`rotate(${a + frame * 0.6} ${hx} ${hy})`} />
            ))}
          </g>
        )}

        {/* Arrival burst at the workshop: the engine, then the water. */}
        {[arrived, reached].map((v, i) => (v > 0.01 && v < 1 ? <circle key={i} cx={hx} cy={hy} r={20 + v * 90} fill="none" stroke={i ? C.water : C.ember2} strokeWidth={4} opacity={1 - v} /> : null))}
      </svg>
    </AbsoluteFill>
  );
};
