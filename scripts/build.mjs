#!/usr/bin/env node
/* Builds the deployable site into dist/.
   Only the files the app serves are copied, so scripts, raw data and screenshots in the
   repository are never published. Asset URLs in index.html get a content-hash query so a
   new deploy is never masked by a cached stylesheet or script. No dependencies. */
import { cpSync, rmSync, mkdirSync, readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'dist');
const fail = msg => { console.error(`build failed: ${msg}`); process.exit(1); };

// Files the app needs, with a minimum plausible size so an empty or truncated file stops the deploy.
const required = { 'index.html': 3000, 'css/app.css': 20000, 'js/app.js': 50000, 'js/data.js': 50000, 'assets/logo.svg': 300 };
for (const [file, min] of Object.entries(required)) {
  const abs = path.join(root, file);
  if (!existsSync(abs)) fail(`${file} is missing`);
  if (statSync(abs).size < min) fail(`${file} is only ${statSync(abs).size} bytes (expected at least ${min})`);
}

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });
for (const dir of ['css', 'js']) cpSync(path.join(root, dir), path.join(out, dir), { recursive: true });
mkdirSync(path.join(out, 'assets'));
cpSync(path.join(root, 'assets/logo.svg'), path.join(out, 'assets/logo.svg'));

// Survey layers the map loads on demand.
mkdirSync(path.join(out, 'data'));
const layers = readdirSync(path.join(root, 'data')).filter(f => f.endsWith('.geojson') || f === 'manifest.json');
if (!layers.length) fail('data/ contains no GeoJSON layers');
for (const f of layers) {
  const src = path.join(root, 'data', f);
  try { JSON.parse(readFileSync(src, 'utf8')); } catch (e) { fail(`data/${f} is not valid JSON`); }
  cpSync(src, path.join(out, 'data', f));
}

// Cache-bust local assets referenced from index.html.
let html = readFileSync(path.join(root, 'index.html'), 'utf8');
for (const file of ['css/app.css', 'js/data.js', 'js/app.js', 'assets/logo.svg']) {
  const hash = createHash('sha256').update(readFileSync(path.join(root, file))).digest('hex').slice(0, 10);
  const before = html;
  html = html.split(`"${file}"`).join(`"${file}?v=${hash}"`);
  if (html === before) fail(`index.html does not reference ${file}`);
}
writeFileSync(path.join(out, 'index.html'), html);

const size = dir => readdirSync(dir, { withFileTypes: true })
  .reduce((n, e) => n + (e.isDirectory() ? size(path.join(dir, e.name)) : statSync(path.join(dir, e.name)).size), 0);
console.log(`built dist/: ${layers.length} data layers, ${(size(out) / 1024).toFixed(0)} KB total`);
