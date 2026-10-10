// The edit decision list: the name, scene windows, narration and sound cues.
// All times are in frames at 30 fps. Everything else in the film is timed relative to a scene's
// start, so changing a scene's `from` or `dur` here moves its picture, narration and sound together.
import atlas from './data/atlas.json';
import {ease, prog} from './lib/anim';

export const APP = 'AgniDrishti';
export const APP_HINDI = 'अग्निदृष्टि';
export const APP_MEANING = 'fire sight';
export const LIVE_URL = 'seelampur-fire-risk-map.onrender.com';

export const HERO = atlas.hero;
export const RELAY = atlas.hero.relay;
export const ROUTE = atlas.route;
export const TOTALS = atlas.totals;
export const INSIGHTS = atlas.insights;

/** Share of surveyed workshops on lanes too narrow for a fire engine (110 of 148). */
export const NARROW_SHARE = Math.round((TOTALS.narrow / TOTALS.workshops) * 100);
/** Share standing within a metre of the next building (126 of 148). */
export const TIGHT_SHARE = Math.round((TOTALS.tight / TOTALS.workshops) * 100);

// Scenes overlap by about ten frames so one dissolves into the next while the map camera keeps moving.
export const SCENES = {
  problem: {from: 0, dur: 262},     // 0:00 – 0:08  lanes too narrow, buildings wall to wall
  reveal: {from: 250, dur: 205},    // 0:08 – 0:15  AgniDrishti, 148 workshops
  risk: {from: 445, dur: 215},      // 0:15 – 0:22  the 0–100 risk score
  dispatch: {from: 650, dur: 200},  // 0:22 – 0:28  turn-by-turn dispatch
  relay: {from: 840, dur: 192},     // 0:28 – 0:34  the hose relay
  insights: {from: 1022, dur: 178}, // 0:34 – 0:40  the settlement at a glance
  close: {from: 1190, dur: 130},    // 0:40 – 0:44  tagline and link
};
export type SceneName = keyof typeof SCENES;
/** Absolute frame of a moment `offset` frames into a scene. */
export const at = (scene: SceneName, offset = 0) => SCENES[scene].from + offset;

// Shared clocks: the map draws these and the on-screen read-outs count along with them.
export const ROUTE_WINDOW = [at('dispatch', 50), at('dispatch', 160)];
export const HOSE_WINDOW = [at('relay', 46), at('relay', 130)];
export const routeProgress = (frame: number) => prog(frame, ROUTE_WINDOW[0], ROUTE_WINDOW[1], ease.inOut);
export const hoseProgress = (frame: number) => prog(frame, HOSE_WINDOW[0], HOSE_WINDOW[1], ease.inOut);
/** Frame at which hose coupling `n` (counted from the tender) clicks into place. */
export const couplingFrame = (n: number) => HOSE_WINDOW[0] + Math.round((n / RELAY.lengths) * (HOSE_WINDOW[1] - HOSE_WINDOW[0]) * 0.92) + 4;
export const GAUGE_START = at('risk', 50);
export const GAUGE_END = at('risk', 115);

// Narration. One clip per line so a re-recorded line can never drift out of sync with the picture.
// Drop your own recordings in public/vo/ under the same file names to replace the draft voice.
const LINES: {id: string; scene: SceneName; offset: number; text: string}[] = [
  {id: 'line-1', scene: 'problem', offset: 15, text: 'In Seelampur, Delhi, most lanes are too narrow for a fire engine.'},
  {id: 'line-2', scene: 'problem', offset: 160, text: 'And the buildings stand wall to wall.'},
  {id: 'line-3', scene: 'reveal', offset: 8, text: 'AgniDrishti maps the risk. A hundred and forty-eight workshops, surveyed door to door.'},
  {id: 'line-4', scene: 'risk', offset: 7, text: 'Each one gets a risk score out of a hundred, graded in plain words anyone can read.'},
  {id: 'line-5', scene: 'dispatch', offset: 7, text: 'When a fire starts, it routes the nearest engine, turn by turn.'},
  {id: 'line-6', scene: 'relay', offset: 6, text: 'Where the road ends, it plans the hose relay, down to the last metre.'},
  {id: 'line-7', scene: 'insights', offset: 8, text: 'And it shows the whole settlement at a glance: where the risk is, and why.'},
  {id: 'line-8', scene: 'close', offset: 6, text: 'AgniDrishti. Open source, and live now.'},
];
export const VOICEOVER = LINES.map((line) => ({...line, at: at(line.scene, line.offset)}));
export const VOICE_VOLUME = 1;

// Interface sounds: quiet, dry and tactile, sitting well under the voice. No music.
type Cue = {at: number; file: string; vol: number};
const cue = (scene: SceneName, offset: number, file: string, vol: number): Cue => ({at: at(scene, offset), file, vol});
const couplings: Cue[] = Array.from({length: RELAY.lengths - 1}, (_, i) => ({at: couplingFrame(i + 1), file: 'pop', vol: 0.22}));
export const SOUNDS: Cue[] = [
  // Problem: narrow lanes, then wall to wall
  cue('problem', 5, 'whoosh', 0.14),
  cue('problem', 10, 'type', 0.12),
  cue('problem', 66, 'click', 0.2),
  cue('problem', 96, 'count', 0.12),
  cue('problem', 124, 'pop', 0.2),
  cue('problem', 157, 'whoosh', 0.12),
  cue('problem', 178, 'click', 0.18),
  cue('problem', 188, 'count', 0.12),
  cue('problem', 216, 'pop', 0.18),
  // Reveal
  cue('reveal', 2, 'whoosh', 0.16),
  cue('reveal', 16, 'thud', 0.34),
  cue('reveal', 88, 'whoosh', 0.1),
  cue('reveal', 100, 'count', 0.12),
  cue('reveal', 128, 'tick', 0.14),
  cue('reveal', 133, 'tick', 0.14),
  cue('reveal', 138, 'tick', 0.14),
  cue('reveal', 143, 'tick', 0.14),
  // Risk score
  cue('risk', 2, 'whoosh', 0.16),
  cue('risk', 35, 'click', 0.22),
  {at: GAUGE_START, file: 'count-long', vol: 0.16},
  {at: GAUGE_END, file: 'thud', vol: 0.24},
  cue('risk', 88, 'tick', 0.14),
  cue('risk', 100, 'tick', 0.14),
  cue('risk', 112, 'tick', 0.14),
  cue('risk', 131, 'pop', 0.16),
  cue('risk', 138, 'pop', 0.16),
  cue('risk', 145, 'pop', 0.16),
  cue('risk', 152, 'pop', 0.16),
  // Dispatch
  cue('dispatch', 2, 'whoosh', 0.16),
  cue('dispatch', 48, 'click', 0.26),
  cue('dispatch', 78, 'click', 0.14),
  cue('dispatch', 102, 'click', 0.14),
  cue('dispatch', 128, 'click', 0.14),
  {at: ROUTE_WINDOW[1], file: 'chime', vol: 0.16},
  // Hose relay
  cue('relay', 2, 'whoosh', 0.16),
  cue('relay', 38, 'click', 0.22),
  ...couplings,
  cue('relay', 66, 'tick', 0.12),
  cue('relay', 73, 'tick', 0.12),
  cue('relay', 80, 'tick', 0.12),
  cue('relay', 87, 'tick', 0.12),
  {at: HOSE_WINDOW[1], file: 'thud', vol: 0.22},
  // Insights
  cue('insights', 2, 'whoosh', 0.16),
  cue('insights', 26, 'click', 0.18),
  cue('insights', 34, 'click', 0.18),
  cue('insights', 42, 'click', 0.18),
  cue('insights', 58, 'count-long', 0.1),
  cue('insights', 108, 'pop', 0.16),
  // Close
  cue('close', 2, 'whoosh', 0.16),
  cue('close', 26, 'thud', 0.26),
  cue('close', 76, 'click', 0.34),
  cue('close', 78, 'chime', 0.18),
];
