// One continuous camera move over the map for the whole film. Scenes never cut: the camera
// pushes in, pulls back and travels, and the on-screen graphics change around it.
// Map units are metres from the map centre; `z` is pixels per metre; (fx, fy) is where the
// camera target sits on the 1920×1080 frame.
import atlas from './data/atlas.json';
import {ease, lerp} from './lib/anim';
import {at} from './story';
import {DURATION} from './theme';

export type Camera = {x: number; y: number; z: number; fx: number; fy: number};
type Key = Camera & {f: number};

const hero = atlas.hero;
const relay = hero.relay;
const relayMid = {x: (relay.sx + hero.x) / 2, y: (relay.sy + hero.y) / 2};

const KEYS: Key[] = [
  {f: 0, x: 0, y: 0, z: 1.12, fx: 1350, fy: 550},                           // settlement on the right, slow push in
  {f: at('reveal', 2), x: 0, y: 0, z: 1.3, fx: 1350, fy: 550},
  {f: at('reveal', 36), x: 0, y: 6, z: 1.06, fx: 960, fy: 560},              // centre up behind the logo
  {f: at('reveal', 88), x: 0, y: 6, z: 1.09, fx: 960, fy: 560},
  {f: at('reveal', 122), x: 0, y: 6, z: 1.24, fx: 1320, fy: 560},            // slide right for the count
  {f: at('risk', 0), x: 0, y: 6, z: 1.3, fx: 1320, fy: 560},
  {f: at('risk', 43), x: hero.x, y: hero.y, z: 5.0, fx: 500, fy: 610},       // dive to the hero workshop
  {f: at('dispatch', 0), x: hero.x, y: hero.y, z: 5.6, fx: 500, fy: 610},
  {f: at('dispatch', 38), x: -540, y: 70, z: 0.98, fx: 1236, fy: 500},       // pull back to show the route
  {f: at('dispatch', 186), x: -528, y: 74, z: 1.03, fx: 1236, fy: 500},
  {f: at('relay', 34), x: relayMid.x, y: relayMid.y, z: 5.4, fx: 520, fy: 548},   // into the lane for the relay
  {f: at('insights', 0), x: relayMid.x, y: relayMid.y, z: 5.9, fx: 520, fy: 548},
  {f: at('insights', 36), x: 0, y: 0, z: 1.0, fx: 960, fy: 540},             // back out for the charts and the close
  {f: DURATION, x: 0, y: 0, z: 1.1, fx: 960, fy: 540},
];

export const cameraAt = (frame: number): Camera => {
  const f = Math.max(KEYS[0].f, Math.min(KEYS[KEYS.length - 1].f, frame));
  let i = 1;
  while (i < KEYS.length - 1 && KEYS[i].f < f) i++;
  const a = KEYS[i - 1], b = KEYS[i];
  const t = ease.inOut((f - a.f) / (b.f - a.f || 1));
  return {
    x: lerp(a.x, b.x, t),
    y: lerp(a.y, b.y, t),
    z: Math.exp(lerp(Math.log(a.z), Math.log(b.z), t)), // zoom feels even when it is geometric
    fx: lerp(a.fx, b.fx, t),
    fy: lerp(a.fy, b.fy, t),
  };
};

/** Map metres → frame pixels. */
export const project = (cam: Camera, x: number, y: number): [number, number] => [cam.fx + (x - cam.x) * cam.z, cam.fy + (y - cam.y) * cam.z];

/** The camera target as latitude / longitude, for the coordinate read-out. */
export const cameraLatLng = (cam: Camera) => {
  const mx = 111320 * Math.cos((atlas.center.lat * Math.PI) / 180);
  return {lat: atlas.center.lat - cam.y / 110574, lng: atlas.center.lng + cam.x / mx};
};
