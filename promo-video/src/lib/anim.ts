// Small, dependency-free animation helpers. Every value is a pure function of the frame number,
// which is what makes the film render identically every time.

export const clamp = (v: number, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const ease = {
  linear: (t: number) => t,
  in: (t: number) => t * t * t,
  out: (t: number) => 1 - Math.pow(1 - t, 3),
  outQuint: (t: number) => 1 - Math.pow(1 - t, 5),
  inOut: (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
};

/** Eased 0→1 progress of `frame` through the window [start, end]. */
export const prog = (frame: number, start: number, end: number, fn: (t: number) => number = ease.out) =>
  fn(clamp((frame - start) / (end - start)));

/** A damped spring from 0 to 1 that starts at `start`. Overshoots slightly by default. */
export const spring = (frame: number, start: number, opts: {stiffness?: number; damping?: number; fps?: number} = {}) => {
  const {stiffness = 190, damping = 17, fps = 30} = opts;
  const t = (frame - start) / fps;
  if (t <= 0) return 0;
  const w = Math.sqrt(stiffness);
  const z = damping / (2 * w);
  if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
};

/** Opacity for something that lives `total` frames: fades in at the start and out at the end. */
export const fade = (frame: number, total: number, inFrames = 10, outFrames = 12) =>
  Math.min(prog(frame, 0, inFrames, ease.linear), 1 - prog(frame, total - outFrames, total, ease.linear));

/** Piecewise-linear value through [frame, value] keyframes. */
export const track = (frame: number, keys: [number, number][]) => {
  if (frame <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (frame <= keys[i][0]) return lerp(keys[i - 1][1], keys[i][1], (frame - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0]));
  }
  return keys[keys.length - 1][1];
};

// Colour blending. Colours are [r, g, b] so several blends can be chained before printing.
export type RGB = [number, number, number];
export const rgb = (hex: string): RGB => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)) as RGB;
export const blend = (a: RGB, b: RGB, t: number): RGB => a.map((v, i) => lerp(v, b[i], clamp(t))) as RGB;
export const css = (c: RGB) => `rgb(${c.map(Math.round).join(', ')})`;
