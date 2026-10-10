#!/usr/bin/env node
/* Creates the film's audio in public/. No downloads, no dependencies.

   1. Interface sounds (public/sfx/*.wav) are synthesised here from sine tones and filtered
      noise: short, dry and quiet, made to sit under a voice. There is no music.
   2. Narration (public/vo/line-N.wav): one clip per line of the script in src/story.ts.
      - If a clip already exists it is left alone, so your own recordings are never overwritten.
      - Otherwise a DRAFT is made with the computer's built-in voice (Windows, macOS or Linux
        with espeak-ng) so the film has timing you can listen to. Replace it before publishing.
      - If no system voice is available a silent clip is written so the render still works.

   Usage:  node scripts/make-audio.mjs            create whatever is missing
           node scripts/make-audio.mjs --force    regenerate the draft narration too
           node scripts/make-audio.mjs --silent   write silent narration clips (sound effects only) */
import { writeFileSync, mkdirSync, existsSync, readFileSync, rmSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = new Set(process.argv.slice(2));
const SR = 44100;

// ---------- WAV helpers ----------
function wav(samples, rate = SR) {
  const data = Buffer.alloc(samples.length * 2);
  for (let i = 0; i < samples.length; i++) data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, samples[i])) * 32767), i * 2);
  const head = Buffer.alloc(44);
  head.write('RIFF', 0); head.writeUInt32LE(36 + data.length, 4); head.write('WAVEfmt ', 8);
  head.writeUInt32LE(16, 16); head.writeUInt16LE(1, 20); head.writeUInt16LE(1, 22);
  head.writeUInt32LE(rate, 24); head.writeUInt32LE(rate * 2, 28); head.writeUInt16LE(2, 32); head.writeUInt16LE(16, 34);
  head.write('data', 36); head.writeUInt32LE(data.length, 40);
  return Buffer.concat([head, data]);
}
function wavSeconds(file) {
  const b = readFileSync(file);
  let at = 12, rate = 0, block = 0;
  while (at + 8 <= b.length) {
    const id = b.toString('ascii', at, at + 4), size = b.readUInt32LE(at + 4);
    if (id === 'fmt ') { rate = b.readUInt32LE(at + 12); block = b.readUInt16LE(at + 20); }
    if (id === 'data') return rate && block ? size / (rate * block) : 0;
    at += 8 + size + (size % 2);
  }
  return 0;
}

/** Rewrites a 16-bit PCM WAV without its leading and trailing silence. Returns the new length in seconds. */
function trimSilence(file, threshold = 350, pad = 0.03) {
  const b = readFileSync(file);
  let at = 12, rate = 0, channels = 1, bits = 16, start = 0, size = 0;
  while (at + 8 <= b.length) {
    const id = b.toString('ascii', at, at + 4), len = b.readUInt32LE(at + 4);
    if (id === 'fmt ') { channels = b.readUInt16LE(at + 10); rate = b.readUInt32LE(at + 12); bits = b.readUInt16LE(at + 22); }
    if (id === 'data') { start = at + 8; size = Math.min(len, b.length - start); break; }
    at += 8 + len + (len % 2);
  }
  if (!rate || bits !== 16 || !size) return wavSeconds(file);
  const frame = 2 * channels, frames = Math.floor(size / frame);
  const loud = i => Math.abs(b.readInt16LE(start + i * frame)) > threshold;
  let first = 0, last = frames - 1;
  while (first < last && !loud(first)) first++;
  while (last > first && !loud(last)) last--;
  first = Math.max(0, first - Math.round(pad * rate)); last = Math.min(frames - 1, last + Math.round(pad * 2 * rate));
  const mono = new Float32Array(last - first + 1);
  for (let i = 0; i < mono.length; i++) mono[i] = b.readInt16LE(start + (first + i) * frame) / 32768;
  writeFileSync(file, wav(mono, rate));
  return mono.length / rate;
}

// ---------- Synthesis ----------
let seed = 20261010;
const noise = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 2147483648 - 1; };
const buffer = seconds => new Float32Array(Math.ceil(seconds * SR));
/** Adds a decaying sine, optionally sweeping from f0 to f1, to `out` starting at `at` seconds. */
function tone(out, at, { f0, f1 = f0, attack = 0.002, decay = 0.03, gain = 0.5, length = 0.2 }) {
  let phase = 0;
  const start = Math.floor(at * SR), n = Math.floor(length * SR);
  for (let i = 0; i < n && start + i < out.length; i++) {
    const t = i / SR, f = f0 + (f1 - f0) * Math.min(1, t / length);
    phase += (2 * Math.PI * f) / SR;
    const env = t < attack ? t / attack : Math.exp(-(t - attack) / decay);
    out[start + i] += Math.sin(phase) * env * gain;
  }
}
/** Adds a short burst of high-passed noise: the "tick" of a physical switch. */
function snap(out, at, { length = 0.004, gain = 0.3 }) {
  const start = Math.floor(at * SR), n = Math.floor(length * SR);
  let prev = 0;
  for (let i = 0; i < n && start + i < out.length; i++) {
    const x = noise(), hp = x - prev; prev = x;
    out[start + i] += hp * 0.5 * (1 - i / n) * gain;
  }
}
const sounds = {
  tick() { const o = buffer(0.05); snap(o, 0, { gain: 0.35 }); tone(o, 0, { f0: 2050, decay: 0.008, gain: 0.4, length: 0.04 }); return o; },
  click() { const o = buffer(0.09); snap(o, 0, { length: 0.003, gain: 0.6 }); tone(o, 0.001, { f0: 250, f1: 150, decay: 0.018, gain: 0.55, length: 0.08 }); return o; },
  pop() { const o = buffer(0.14); tone(o, 0, { f0: 640, f1: 300, decay: 0.03, gain: 0.55, length: 0.13 }); return o; },
  thud() { const o = buffer(0.36); snap(o, 0, { gain: 0.25 }); tone(o, 0, { f0: 86, f1: 52, decay: 0.09, gain: 0.85, length: 0.35 }); return o; },
  chime() {
    const o = buffer(1.0);
    tone(o, 0, { f0: 880, attack: 0.006, decay: 0.26, gain: 0.26, length: 1.0 });
    tone(o, 0.06, { f0: 1318.5, attack: 0.006, decay: 0.3, gain: 0.2, length: 0.94 });
    return o;
  },
  whoosh() {
    // Noise through a low-pass whose cutoff rises and falls: air moving past, nothing more.
    const o = buffer(0.56); let lp = 0, lp2 = 0;
    for (let i = 0; i < o.length; i++) {
      const t = i / o.length, cutoff = 300 + 2600 * Math.sin(Math.PI * t) ** 2;
      const a = 1 - Math.exp((-2 * Math.PI * cutoff) / SR);
      lp += a * (noise() - lp); lp2 += a * (lp - lp2);
      o[i] = lp2 * Math.sin(Math.PI * t) ** 2 * 1.3;
    }
    return o;
  },
  type() { const o = buffer(1.05); for (let i = 0; i < 14; i++) { const at = 0.02 + i * 0.07 + (noise() + 1) * 0.008; snap(o, at, { gain: 0.3 }); tone(o, at, { f0: 1700 + noise() * 260, decay: 0.006, gain: 0.3, length: 0.03 }); } return o; },
  // A run of ticks that slows as it lands, for numbers counting up.
  count(seconds = 1.0, ticks = 18) { const o = buffer(seconds + 0.06); for (let i = 0; i < ticks; i++) { const u = i / (ticks - 1), at = seconds * (1 - (1 - u) ** 0.55) * 0.98; snap(o, at, { gain: 0.22 }); tone(o, at, { f0: 1500 + u * 700, decay: 0.007, gain: 0.3, length: 0.03 }); } return o; },
};

mkdirSync(path.join(root, 'public', 'sfx'), { recursive: true });
mkdirSync(path.join(root, 'public', 'vo'), { recursive: true });
const sfx = { tick: sounds.tick(), click: sounds.click(), pop: sounds.pop(), thud: sounds.thud(), chime: sounds.chime(), whoosh: sounds.whoosh(), type: sounds.type(), count: sounds.count(1.0, 18), 'count-long': sounds.count(2.0, 30) };
for (const [name, samples] of Object.entries(sfx)) writeFileSync(path.join(root, 'public', 'sfx', `${name}.wav`), wav(samples));
console.log(`sound effects: ${Object.keys(sfx).join(', ')}`);

// ---------- Narration ----------
// Read the lines straight from the story file so the script has one source of truth.
const story = readFileSync(path.join(root, 'src', 'story.ts'), 'utf8');
const scenes = Object.fromEntries([...story.matchAll(/^\s+(\w+): \{from: (\d+), dur: (\d+)\}/gm)].map(m => [m[1], Number(m[2])]));
const total = Number((readFileSync(path.join(root, 'src', 'theme.ts'), 'utf8').match(/DURATION = (\d+)/) || [])[1]) || 0;
const lines = [...story.matchAll(/\{id: '(line-\d+)', scene: '(\w+)', offset: (\d+), text: '((?:[^'\\]|\\.)*)'\}/g)]
  .map(m => ({ id: m[1], at: scenes[m[2]] + Number(m[3]), text: m[4].replace(/\\'/g, "'") }));
if (!lines.length || !total || lines.some(l => Number.isNaN(l.at))) { console.error('Could not read the narration lines and timings from src/story.ts'); process.exit(1); }

// How the computer's own voice should say the Hindi words. These spellings are only ever heard,
// never shown. Each was checked against the phonemes the Windows voice actually produces:
// "Ugnee Drishtee" gives UG-nee DRISH-tee, and "Seelumpoohr" gives SEE-lum-poor.
const SAY = [['AgniDrishti', 'Ugnee Drishtee'], ['Seelampur', 'Seelumpoohr']];
const spoken = text => SAY.reduce((t, [word, sound]) => t.split(word).join(sound), text);

function speak(text, file) {
  const env = { ...process.env, FB_TEXT: text, FB_OUT: file };
  if (process.platform === 'win32') {
    // Windows' built-in speech engine. Prefers an Indian-English voice, then a natural-sounding one.
    const ps = `Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer;
      $pick = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -like 'en-*' } | Sort-Object { if ($_.VoiceInfo.Culture.Name -eq 'en-IN') { 0 } elseif ($_.VoiceInfo.Name -match 'Natural|Online') { 1 } elseif ($_.VoiceInfo.Name -match 'Zira|Hazel|Susan') { 2 } else { 3 } } | Select-Object -First 1;
      if ($pick) { $s.SelectVoice($pick.VoiceInfo.Name) }; $s.Rate = 0; $s.Volume = 100;
      $s.SetOutputToWaveFile($env:FB_OUT); $s.Speak($env:FB_TEXT); $s.Dispose(); if ($pick) { $pick.VoiceInfo.Name }`;
    return spawnSync('powershell', ['-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-Command', ps], { env, encoding: 'utf8' });
  }
  if (process.platform === 'darwin') return spawnSync('say', ['-o', file, '--data-format=LEI16@44100', text], { encoding: 'utf8' });
  return spawnSync('espeak-ng', ['-s', '165', '-w', file, text], { encoding: 'utf8' });
}

let voice = '';
for (let i = 0; i < lines.length; i++) {
  const line = lines[i], file = path.join(root, 'public', 'vo', `${line.id}.wav`);
  if (existsSync(file) && !args.has('--force') && !args.has('--silent')) { console.log(`${line.id}: kept existing clip`); continue; }
  let made = false;
  if (!args.has('--silent')) {
    rmSync(file, { force: true });
    const r = speak(spoken(line.text), file);
    made = !r.error && r.status === 0 && existsSync(file) && wavSeconds(file) > 0.3;
    if (made && r.stdout && r.stdout.trim()) voice = r.stdout.trim().split(/\r?\n/).pop();
  }
  if (!made) { writeFileSync(file, wav(buffer(0.25))); console.log(`${line.id}: silent placeholder`); continue; }
  const seconds = trimSilence(file), room = ((i + 1 < lines.length ? lines[i + 1].at : total) - line.at) / 30;
  console.log(`${line.id}: draft voice, ${seconds.toFixed(1)} s of ${room.toFixed(1)} s available${seconds > room ? '  <-- runs into the next line; shorten it or raise the rate' : ''}`);
}
if (voice) console.log(`draft narration voice: ${voice}`);
