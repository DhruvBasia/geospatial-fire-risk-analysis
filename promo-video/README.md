# AgniDrishti — 44-second launch film

A motion-graphics film for [AgniDrishti](https://seelampur-fire-risk-map.onrender.com)
(अग्निदृष्टि, "fire sight"), built with [Remotion](https://www.remotion.dev) (React).
1920×1080, 30 fps, 44 seconds.

There are no screenshots in it. The map is drawn from the project's own survey files: Seelampur's
street network, the study-area outline, all 148 workshops with their risk level, the real street
route from Shastri Park Fire Post to workshop E016, and that workshop's hose relay.

## Make the video

You need [Node.js](https://nodejs.org) 18 or newer. From this folder:

```bash
npm install
```

```bash
npm run render
```

The film is written to `out/agnidrishti-launch.mp4`. The first render downloads a small headless
browser, which takes a minute; later renders are faster.

To preview and scrub the timeline in the browser instead:

```bash
npm run studio
```

## Narration

The repository includes a **draft** narration made with the computer's built-in voice, so the film
has timing you can listen to. Replace it before you publish:

1. Record each line below (or generate it with a text-to-speech service you like).
2. Save them as `public/vo/line-1.wav` … `public/vo/line-8.wav` (WAV, any sample rate).
3. Run `npm run render` again.

| Clip | Starts | Must finish by | Line |
| :--- | :--- | :--- | :--- |
| `line-1` | 0:00.5 | 0:05.2 | In Seelampur, Delhi, most lanes are too narrow for a fire engine. |
| `line-2` | 0:05.3 | 0:08.4 | And the buildings stand wall to wall. |
| `line-3` | 0:08.6 | 0:15.0 | AgniDrishti maps the risk. A hundred and forty-eight workshops, surveyed door to door. |
| `line-4` | 0:15.1 | 0:21.7 | Each one gets a risk score out of a hundred, graded in plain words anyone can read. |
| `line-5` | 0:21.9 | 0:28.0 | When a fire starts, it routes the nearest engine, turn by turn. |
| `line-6` | 0:28.2 | 0:34.2 | Where the road ends, it plans the hose relay, down to the last metre. |
| `line-7` | 0:34.3 | 0:39.7 | And it shows the whole settlement at a glance: where the risk is, and why. |
| `line-8` | 0:39.9 | 0:44.0 | AgniDrishti. Open source, and live now. |

Delivery: calm, clear and unhurried — a briefing, not an advert. About 140 words a minute.

### Saying the Hindi words

| Word | Say it as | Devanagari |
| :--- | :--- | :--- |
| AgniDrishti | **UG**-nee **DRISH**-tee ("ug" as in *ugly*, a soft dental *t*) | अग्निदृष्टि |
| Seelampur | **SEE**-lum-poor | सीलमपुर |

The built-in draft voice is an American-English voice, so `scripts/make-audio.mjs` feeds it
phonetic spellings for these two words (the `SAY` list near the bottom of that file). The spellings
are only heard, never shown. If you add another Hindi word to the script, add its spelling there.

For a more natural result on Windows, install an Indian voice: **Settings → Time & language →
Speech → Add voices → English (India)**. The script picks an `en-IN` voice automatically when one
is installed; then run:

```bash
node scripts/make-audio.mjs --force
```

`npm run audio` regenerates anything missing in `public/` and never overwrites a clip that is
already there. `--force` remakes the draft voice; `--silent` writes silent narration clips if you
want the picture and sound effects only.

## Sound

There is no music. The interface sounds in `public/sfx/` are synthesised by
`scripts/make-audio.mjs` (short sine tones and filtered noise) and mixed well under the voice.
Every cue and its volume is listed in `src/story.ts`.

## Changing things

| To change | Edit |
| :--- | :--- |
| The name, scene timing, narration lines, sound cues | `src/story.ts` |
| Total length | `DURATION` in `src/theme.ts` (and the scene windows in `src/story.ts`) |
| The camera move over the map | `src/camera.ts` |
| Colours | `src/theme.ts` |
| A scene's layout and wording | `src/scenes/*.tsx` |
| The map, route and hose drawing | `src/components/Atlas.tsx` |

Everything inside a scene is timed from that scene's start, so moving a scene in `src/story.ts`
moves its picture, narration and sound together.

The numbers on screen are read from `src/data/atlas.json`, which is generated from the survey:

```bash
npm run atlas
```

Run that after the survey data in `../js/data.js` or `../data/*.geojson` changes. To feature a
different workshop, change `HERO_ID` in `scripts/extract-atlas.mjs`, fetch its street route into
`data-src/route.json`, and run `npm run atlas` again.

## Where the figures come from

- **74% out of reach** — 110 of the 148 surveyed workshops are on lanes under 2.5 m wide, the
  width of a fire engine.
- **85% within a metre of the next building** — 34 share a wall and 92 have a gap under 1 m
  (126 of 148).
- **78 / 100, Severe** — the Fire Risk Index of workshop E016, Block Carving & Print Studio.
- **1.4 km route** — returned by the public OSRM routing service the live app uses.
- **161 m, 6 × 30 m, 6.3 bar, 6m 30s, booster pump** — the app's hose-relay plan for that
  workshop from Seelampur 100 ft Road.
- **Most common problems** and **average score 70** — the same definitions as the app's Insights
  page (a factor scoring 0.65 or worse counts as a problem).
- **56 past fires, every one now rated severe** — workshops with a reported fire incident.
