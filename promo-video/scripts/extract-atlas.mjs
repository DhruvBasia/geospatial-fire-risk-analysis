#!/usr/bin/env node
/* Builds src/data/atlas.json — the vector map the film draws.
   Everything on screen comes from the real project: the surveyed street network, the study-area
   outline, the 148 workshops with their risk tier, and the OSRM street route to the hero unit.
   Coordinates are projected to metres east (x) and south (y) of the map centre, so one map unit
   is one metre on the ground. Re-run after the survey data changes:  npm run atlas            */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const video = path.resolve(here, '..');
const repo = path.resolve(video, '..');

const CENTER = { lat: 28.6665, lng: 77.2720 };
const MX = 111320 * Math.cos(CENTER.lat * Math.PI / 180), MY = 110574;
const proj = (lng, lat) => [+((lng - CENTER.lng) * MX).toFixed(1), +((CENTER.lat - lat) * MY).toFixed(1)];
const geo = name => JSON.parse(readFileSync(path.join(repo, 'data', `${name}.geojson`), 'utf8'));

// Douglas–Peucker: drop points that sit within `tol` metres of the simplified line.
function simplify(pts, tol) {
  if (pts.length < 3) return pts;
  const [ax, ay] = pts[0], [bx, by] = pts[pts.length - 1];
  const len = Math.hypot(bx - ax, by - ay) || 1;
  let worst = 0, at = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    const d = Math.abs((bx - ax) * (ay - pts[i][1]) - (ax - pts[i][0]) * (by - ay)) / len;
    if (d > worst) { worst = d; at = i; }
  }
  if (worst <= tol) return [pts[0], pts[pts.length - 1]];
  return [...simplify(pts.slice(0, at + 1), tol).slice(0, -1), ...simplify(pts.slice(at), tol)];
}

// All line strings of a layer, projected, clipped to a box, simplified, as one SVG path string.
function linePath(name, box, tol) {
  const parts = [];
  for (const f of geo(name).features) {
    const g = f.geometry;
    const lines = g.type === 'MultiLineString' ? g.coordinates : g.type === 'LineString' ? [g.coordinates] : [];
    for (const line of lines) {
      let run = [];
      const flush = () => { if (run.length > 1) parts.push(simplify(run, tol)); run = []; };
      for (const [lng, lat] of line) {
        const p = proj(lng, lat);
        if (p[0] < box[0] || p[0] > box[2] || p[1] < box[1] || p[1] > box[3]) flush(); else run.push(p);
      }
      flush();
    }
  }
  return parts.map(l => 'M' + l.map(p => `${p[0]} ${p[1]}`).join('L')).join('');
}

// --- Survey workshops
globalThis.window = {};
new Function('window', readFileSync(path.join(repo, 'js', 'data.js'), 'utf8'))(globalThis.window);
const { WORKSHOPS_DATA: workshops, STUDY_AREA_POLYGON, SCORING_MAP } = window.FRA_DATA;
const TIERS = ['Severe', 'High', 'Moderate', 'Low'];
const points = workshops.map(w => {
  const [x, y] = proj(w.lng, w.lat);
  const g = w.cats.building_gap === 'shared_wall_0m' ? 0 : w.cats.building_gap === 'narrow_gap_under_1m' ? 1 : 2;
  return { id: w.id, x, y, t: TIERS.indexOf(w.tier), s: Math.floor(w.fri * 100 + 1e-9), n: w.cats.approach_road === 'narrow_under_2_5m' ? 1 : 0, g };
});

// --- Hero workshop and its hose relay, using the same model as the app
const HERO_ID = 'E016';
const w = workshops.find(x => x.id === HERO_ID);
const grade = s => (s >= 0.7 ? 'Critical' : s >= 0.5 ? 'Poor' : s >= 0.3 ? 'Fair' : 'Good');
const STAGING = [
  ['Grand Trunk Road', 30, 28.6685, 77.2665], ['Marginal Bund (Pusta) Road', 24, 28.6635, 77.2685], ['Seelampur 100 ft Road', 22, 28.6630, 77.2715],
  ['Jafrabad Main Road', 18, 28.6698, 77.2710], ['Welcome Flyover Service Road', 20, 28.6705, 77.2735], ['Swami Dayanand Marg', 28, 28.6655, 77.2768]];
// Great-circle distance in metres between two [lat, lng] pairs — the same formula the app uses.
const metres = (a, b) => {
  const rad = d => d * Math.PI / 180, dLat = rad(b[0] - a[0]), dLng = rad(b[1] - a[1]);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(dLng / 2) ** 2;
  return 6371000 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
};
const road = STAGING.reduce((best, r) => (metres([w.lat, w.lng], [r[2], r[3]]) < metres([w.lat, w.lng], [best[2], best[3]]) ? r : best), STAGING[0]);
const run = Math.max(35, Math.round(metres([w.lat, w.lng], [road[2], road[3]]) * 1.35));   // lanes wind: 1.35 × straight line
const lengths = Math.ceil(run / 30);                                                        // 30 m delivery hose
const storeys = { g_plus_3_or_more: 4, g_plus_2: 3, g_plus_1: 2, ground_only: 1 }[w.cats.floors] || 1;
const pressure = +(3.5 + lengths * 0.35 + (storeys - 1) * 0.35).toFixed(2);
const seconds = lengths * 45 + (w.cats.obstruction === 'obstructed' ? 90 : w.cats.obstruction === 'partially_clear' ? 45 : 0) + (w.cats.approach_road === 'narrow_under_2_5m' ? 30 : 0);
const [hx, hy] = proj(w.lng, w.lat), [sx, sy] = proj(road[3], road[2]);
const hero = {
  id: w.id, name: w.ent, locality: w.loc, x: hx, y: hy, score: Math.floor(w.fri * 100 + 1e-9), tier: w.tier, pastFire: !!w.incident,
  areas: [['Escape routes', w.egress], ['Fire hazards', w.hazard], ['Fire-engine access', w.access]].map(([name, v]) => ({ name, value: +v.toFixed(3), grade: grade(v) })),
  relay: { road: road[0], roadWidth: road[1], sx, sy, run, lengths, pressure, seconds, booster: run > 150 || pressure > 6.5 }
};

// --- Street route (OSRM), saved beside this script by `npm run route`
const r = JSON.parse(readFileSync(path.join(video, 'data-src', 'route.json'), 'utf8'));
const routePts = r.coords.map(([lng, lat]) => proj(lng, lat));
const LABEL = { left: 'Turn left', right: 'Turn right', 'slight left': 'Bear left', 'slight right': 'Bear right', 'sharp left': 'Sharp left', 'sharp right': 'Sharp right', uturn: 'U-turn', straight: 'Continue' };
let along = 0;
const steps = r.steps.map(s => {
  const step = { at: Math.round(along), label: s.type === 'depart' ? 'Depart' : s.type === 'arrive' ? 'Arrive' : (LABEL[s.modifier] || 'Continue'),
    dir: s.type === 'arrive' ? 'arrive' : s.type === 'depart' ? 'straight' : s.modifier.includes('left') ? 'left' : s.modifier.includes('right') ? 'right' : 'straight', metres: Math.round(s.distance) };
  along += s.distance;
  return step;
});
const [stx, sty] = proj(r.from.lng, r.from.lat);

// --- Settlement-wide figures for the insights scene, using the app's own definitions
const PROBLEM = {
  exits: 'One exit', obstruction: 'Blocked path', emergency_exits: 'No fire exit', stair_width: 'Narrow stairs', workspace: 'Cramped space',
  floors: 'Tall building', light: 'No vents', windows: 'Barred windows', corridor: 'Tight corridor', dust: 'Lint & dust',
  building_gap: 'No gap', waste_burning: 'Waste burning', station_dist: 'Far station', response_time: 'Slow response', approach_road: 'Narrow lane'
};
const FAIL_SCORE = 0.65; // a factor at or above this score counts as a problem
const problems = Object.keys(PROBLEM).map(k => ({ name: PROBLEM[k], share: Math.round(workshops.filter(x => ((SCORING_MAP[k] || {})[x.cats[k]] || 0) >= FAIL_SCORE).length / workshops.length * 100) }))
  .sort((a, b) => b.share - a.share).slice(0, 5);
const fires = workshops.filter(x => x.incident);
const meanScore = Math.floor(workshops.reduce((sum, x) => sum + x.fri, 0) / workshops.length * 100 + 1e-9);
const insights = { mean: meanScore, problems, fires: { total: fires.length, severe: fires.filter(x => x.tier === 'Severe').length } };

// --- Assemble
const atlas = {
  note: 'Generated by scripts/extract-atlas.mjs — do not edit by hand. Units are metres from the map centre.',
  center: CENTER,
  outline: STUDY_AREA_POLYGON.map(([lat, lng]) => proj(lng, lat).join(',')).join(' '),
  streets: linePath('streets', [-1400, -760, 1000, 760], 0.7),
  roads: linePath('roads', [-1500, -800, 1100, 800], 1.2),
  points,
  totals: { workshops: workshops.length, narrow: points.filter(p => p.n).length, tiers: TIERS.map((t, i) => points.filter(p => p.t === i).length), pastFires: fires.length,
    gaps: [0, 1, 2].map(g => points.filter(p => p.g === g).length), tight: points.filter(p => p.g < 2).length },
  insights,
  hero,
  route: { station: 'Shastri Park Fire Post', sx: stx, sy: sty, metres: Math.round(r.distance), seconds: Math.round(r.duration), points: routePts, steps }
};
mkdirSync(path.join(video, 'src', 'data'), { recursive: true });
const out = path.join(video, 'src', 'data', 'atlas.json');
writeFileSync(out, JSON.stringify(atlas));
console.log(`atlas.json: ${(JSON.stringify(atlas).length / 1024).toFixed(0)} KB · ${points.length} workshops · streets ${(atlas.streets.length / 1024).toFixed(0)} KB · roads ${(atlas.roads.length / 1024).toFixed(0)} KB`);
console.log('totals', JSON.stringify(atlas.totals));
console.log('insights', JSON.stringify(insights));
console.log('hero', JSON.stringify(hero));
console.log('route', atlas.route.metres, 'm,', atlas.route.seconds, 's,', routePts.length, 'points, start', stx, sty, '| steps', steps.map(s => `${s.label}@${s.at}`).join(', '));
