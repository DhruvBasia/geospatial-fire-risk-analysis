/* AgniDrishti, the Seelampur fire risk atlas — application logic.
   One filter state drives the map, insights, registry and role workspaces;
   every figure on screen is computed from the survey dataset in js/data.js. */
(() => {
  'use strict';

  const { WORKSHOPS_DATA: DATA, SCORING_MAP, STUDY_AREA_POLYGON } = window.FRA_DATA;

  // =========================================================
  // DOMAIN MODEL
  // =========================================================
  const APP_NAME = 'AgniDrishti';
  const TIERS = ['Severe', 'High', 'Moderate', 'Low'];
  // The Fire Risk Index is stored 0–1; people read it as a risk score out of 100, so `range` is in points.
  const TIER = {
    Severe:   { color: '#A61B1B', range: '70–100' },
    High:     { color: '#E2571C', range: '50–69' },
    Moderate: { color: '#D9A100', range: '30–49' },
    Low:      { color: '#0C8F7E', range: '0–29' }
  };
  const tierOf = fri => (fri >= 0.70 ? 'Severe' : fri >= 0.50 ? 'High' : fri >= 0.30 ? 'Moderate' : 'Low');
  const BASE_WEIGHTS = { egress: 0.45, hazard: 0.25, access: 0.30 };
  const SUBS = [
    { key: 'egress', name: 'Escape routes', short: 'Escape', note: 'Exits, stairs, corridors and floors' },
    { key: 'hazard', name: 'Fire hazards', short: 'Hazards', note: 'Dust, waste burning and the gap to the next building' },
    { key: 'access', name: 'Fire-engine access', short: 'Access', note: 'Distance to a station, response time and road width' }
  ];
  const FAIL_SCORE = 0.65; // a factor at or above this score counts as a deficiency
  // Each factor named as the problem it becomes when it scores badly.
  const PROBLEM = {
    exits: 'One exit', obstruction: 'Blocked path', emergency_exits: 'No fire exit', stair_width: 'Narrow stairs',
    workspace: 'Cramped space', floors: 'Tall building', light: 'No vents', windows: 'Barred windows',
    corridor: 'Tight corridor', dust: 'Lint & dust', building_gap: 'No gap', waste_burning: 'Waste burning',
    station_dist: 'Far station', response_time: 'Slow response', approach_road: 'Narrow lane'
  };

  // Factor catalogue. `levels` maps each survey category code to [label, plain-language reading].
  const FACTORS = {
    exits: { name: 'Exit routes', scope: 'inside', sub: 'egress', phrase: 'a single escape route', levels: {
      '1 exit': ['Single exit', 'Only one way out. If flames or smoke block this door, occupants have no alternate escape and become trapped.'],
      '2 exits': ['Two exits', 'Two separate routes give an alternate escape if one becomes impassable.'],
      '3+ exits': ['Three or more', 'Multiple independent exits allow rapid simultaneous evacuation.'] } },
    obstruction: { name: 'Evacuation path', scope: 'inside', sub: 'egress', phrase: 'a blocked evacuation path', levels: {
      obstructed: ['Blocked', 'Fabric scrap, machinery and stock clog the escape route and prevent a fast exit.'],
      partially_clear: ['Partly blocked', 'Clutter and raw material slow workers trying to leave quickly.'],
      clear: ['Clear', 'The evacuation route is kept open and free of heavy obstacles.'] } },
    emergency_exits: { name: 'Emergency exits', scope: 'inside', sub: 'egress', phrase: 'no working emergency exit', levels: {
      none: ['None', 'No designated emergency exit — occupants rely on the one congested main entrance.'],
      locked_or_blocked: ['Locked or blocked', 'The emergency door is locked, bolted or blocked with stock, so it is useless in a crisis.'],
      functional: ['Functional', 'A marked emergency exit opens outward and is kept operational.'] } },
    stair_width: { name: 'Staircase width', scope: 'inside', sub: 'egress', phrase: 'dangerously narrow stairs', levels: {
      under_0_8m: ['Under 0.8 m', 'Stairs under 80 cm create an immediate bottleneck and crush risk during panic.'],
      '0_8_to_1_2m': ['0.8 – 1.2 m', 'A sub-standard stair width causes congestion when several workers flee together.'],
      over_1_2m: ['Over 1.2 m', 'A wide, compliant staircase allows uninterrupted multi-person evacuation.'] } },
    workspace: { name: 'Workspace size', scope: 'inside', sub: 'egress', phrase: 'a heavily confined workspace', levels: {
      under_200sqft: ['Under 200 sq ft', 'Workers operate shoulder to shoulder, surrounded by combustible stock and heat sources.'],
      '200_to_500sqft': ['200 – 500 sq ft', 'A tight floor plate with limited room to move around workstations.'],
      over_500sqft: ['Over 500 sq ft', 'A spacious layout allows quick reaction and unobstructed movement.'] } },
    floors: { name: 'Building height', scope: 'inside', sub: 'egress', phrase: 'upper floors with no fire escape', levels: {
      g_plus_3_or_more: ['G+3 or taller', 'Four or more levels with no external fire escape — descending from the top through smoke is treacherous.'],
      g_plus_2: ['G+2', 'Three levels: escape requires stair travel through rising smoke.'],
      g_plus_1: ['G+1', 'Two levels: a short vertical descent to the street.'],
      ground_only: ['Ground only', 'A single-storey unit with direct street-level escape.'] } },
    light: { name: 'Light & ventilation', scope: 'inside', sub: 'egress', phrase: 'no smoke ventilation', levels: {
      dark_no_vent: ['Dark, unventilated', 'No natural ventilation: toxic smoke accumulates fast and visibility drops to zero.'],
      dim_partial: ['Dim, partial vents', 'Limited ventilation means smoke disperses slowly.'],
      well_lit: ['Well lit', 'Open ventilation and daylight let smoke escape and keep people oriented.'] } },
    windows: { name: 'Window openings', scope: 'inside', sub: 'egress', phrase: 'barred windows that prevent ladder rescue', levels: {
      no_windows_or_barred: ['None or barred', 'Windowless, or sealed behind iron grilles — no secondary escape and no ladder access for fire crews.'],
      few_restricted: ['Few, restricted', 'A small number of restricted openings; rescue through them is slow.'],
      operable_clear: ['Operable', 'Openable windows give fire-brigade ladders a viable rescue opening.'] } },
    corridor: { name: 'Internal corridors', scope: 'inside', sub: 'egress', phrase: 'sub-standard corridors', levels: {
      under_1m_cluttered: ['Under 1 m, cluttered', 'Corridors under a metre wide become a choke point during an emergency rush.'],
      '1_to_1_5m': ['1 – 1.5 m', 'A narrow corridor delays movement through smoke.'],
      wide_clear: ['Wide and clear', 'Wide corridors support orderly two-way emergency movement.'] } },
    dust: { name: 'Combustible dust', scope: 'inside', sub: 'hazard', phrase: 'heavy combustible lint', levels: {
      heavy_flammable_lint: ['Heavy lint', 'Dense textile fluff, solvent vapour or plastic dust creates an acute flashover risk.'],
      moderate_dust: ['Moderate', 'Noticeable airborne particles and fumes that need local extraction.'],
      low_dust: ['Low', 'Low dust levels with regular sweeping and ventilation.'] } },
    building_gap: { name: 'Building separation', scope: 'outside', sub: 'hazard', phrase: 'shared walls with neighbouring buildings', levels: {
      shared_wall_0m: ['Shared wall (0 m)', 'The building touches its neighbours: fire jumps from structure to structure within minutes.'],
      narrow_gap_under_1m: ['Under 1 m', 'A gap under a metre lets radiant heat ignite the building across the alley.'],
      gap_over_1m: ['Over 1 m', 'An adequate setback buffers radiant heat and slows external flame spread.'] } },
    waste_burning: { name: 'Open waste burning', scope: 'outside', sub: 'hazard', phrase: 'open scrap burning in adjacent lanes', levels: {
      daily_open_burning: ['Daily', 'Fabric scrap and refuse are burned in the adjoining lane every day — a constant ignition source.'],
      occasional_burning: ['Occasional', 'Occasional burning or unmonitored combustible dumps near external walls.'],
      none: ['None', 'No roadside burning or combustible dump piles nearby.'] } },
    station_dist: { name: 'Distance to fire station', scope: 'outside', sub: 'access', phrase: 'a long run from the nearest fire station', levels: {
      over_3km: ['Over 3 km', 'More than 3 km from a fire station through dense arterial traffic, delaying the first water.'],
      '1_5_to_3km': ['1.5 – 3 km', 'A 1.5–3 km turnout through congested commercial links.'],
      under_1_5km: ['Under 1.5 km', 'Close to a fire station, with quick turnout potential.'] } },
    response_time: { name: 'Brigade response time', scope: 'outside', sub: 'access', phrase: 'a protracted brigade response', levels: {
      over_25min: ['Over 25 min', 'Estimated arrival exceeds 25 minutes — a fire reaches full flashover long before crews arrive.'],
      '15_to_25min': ['15 – 25 min', 'A 15–25 minute arrival: fire may breach compartments before water is applied.'],
      under_15min: ['Under 15 min', 'A response under 15 minutes gives crews a chance to contain the fire early.'] } },
    approach_road: { name: 'Approach road', scope: 'outside', sub: 'access', phrase: 'a lane too narrow for fire engines', levels: {
      narrow_under_2_5m: ['Under 2.5 m', 'The lane is under 2.5 m. Fire engines cannot reach the door; crews must run a manual hose relay.'],
      medium_2_5_to_4m: ['2.5 – 4 m', 'Small rapid-response tenders fit, but heavy appliances do not.'],
      wide_over_4m: ['Over 4 m', 'A motorable road gives direct access for heavy tenders.'] } }
  };
  const FACTOR_KEYS = Object.keys(FACTORS);
  const score = (w, key) => (SCORING_MAP[key] && SCORING_MAP[key][w.cats[key]]) || 0;
  const levelOf = (w, key) => (FACTORS[key].levels[w.cats[key]] || [w.cats[key], '']);

  const FIRE_STATIONS = [
    { name: 'Shastri Park Fire Post', lat: 28.6675, lng: 77.2610, desc: 'First-responder tender post, GT Road corridor' },
    { name: 'Shahdara Fire Station', lat: 28.6738, lng: 77.2885, desc: 'Delhi Fire Service divisional headquarters' },
    { name: 'Geeta Colony Fire Station', lat: 28.6520, lng: 77.2710, desc: 'East Delhi water bowser and rescue base' }
  ];
  const HOSPITALS = [
    { name: 'Jag Pravesh Chandra Hospital', lat: 28.6750, lng: 77.2610, desc: '100-bed general and trauma facility, Shastri Park' },
    { name: 'Guru Teg Bahadur (GTB) Hospital', lat: 28.6825, lng: 77.3110, desc: '1,500-bed tertiary care and burns centre, Dilshad Garden' },
    { name: 'Dr. Hedgewar Arogya Sansthan', lat: 28.6575, lng: 77.2940, desc: 'Multi-specialty hospital, Karkardooma' },
    { name: 'Seelampur Primary Health Centre', lat: 28.6672, lng: 77.2683, desc: 'Local dispensary and emergency post' },
    { name: 'Jafrabad Aam Aadmi Clinic', lat: 28.6686, lng: 77.2742, desc: 'Neighbourhood urgent-care and burn dressing post' }
  ];
  const STAGING_ROADS = [
    { name: 'Grand Trunk Road', widthM: 30, lat: 28.6685, lng: 77.2665, desc: 'Six-lane divided arterial — main heavy-tender staging base' },
    { name: 'Marginal Bund (Pusta) Road', widthM: 24, lat: 28.6635, lng: 77.2685, desc: 'Embankment highway — south-west staging area' },
    { name: 'Seelampur 100 ft Road', widthM: 22, lat: 28.6630, lng: 77.2715, desc: 'Four-lane collector — direct water relay connection' },
    { name: 'Jafrabad Main Road', widthM: 18, lat: 28.6698, lng: 77.2710, desc: 'North-sector commercial arterial' },
    { name: 'Welcome Flyover Service Road', widthM: 20, lat: 28.6705, lng: 77.2735, desc: 'Service bay for heavy water bowsers' },
    { name: 'Swami Dayanand Marg', widthM: 28, lat: 28.6655, lng: 77.2768, desc: 'East perimeter arterial — high-capacity relay point' }
  ];

  const ROLES = {
    fire: { title: 'Fire Safety Officer', short: 'Fire officer', name: 'Insp. R. K. Singh', initials: 'RS', email: 'fire@usap.edu',
      workspace: 'Command', icon: 'flame', blurb: 'Dispatch simulation, hose relay planning and tender staging.' },
    planner: { title: 'Urban Disaster Planner', short: 'Planner', name: 'Neha Gupta', initials: 'NG', email: 'planner@usap.edu',
      workspace: 'Planning', icon: 'layers', blurb: 'Setback compliance, building stock and Master Plan directives.' },
    surveyor: { title: 'Field Survey Lead', short: 'Surveyor', name: 'Tariq Anjum', initials: 'TA', email: 'surveyor@usap.edu',
      workspace: 'Field audit', icon: 'clipboard', blurb: 'Record new audits on site and verify surveyed units.' },
    admin: { title: 'System Administrator', short: 'Admin', name: 'Prof. Amit Sharma', initials: 'AS', email: 'admin@usap.edu',
      workspace: 'Governance', icon: 'sliders', blurb: 'Tune the risk model weights and export the dataset.' }
  };
  const DEMO_PASSWORD = 'fire2026';

  const QUICK = [
    { id: 'single-exit', label: 'Single exit', test: w => w.cats.exits === '1 exit' },
    { id: 'shared-wall', label: 'Shared wall', test: w => w.cats.building_gap === 'shared_wall_0m' },
    { id: 'narrow-lane', label: 'Lane under 2.5 m', test: w => w.cats.approach_road === 'narrow_under_2_5m' },
    { id: 'tall', label: 'G+3 or taller', test: w => w.cats.floors === 'g_plus_3_or_more' },
    { id: 'incident', label: 'Past fire incident', test: w => !!w.incident }
  ];
  const QUICK_BY_ID = Object.fromEntries(QUICK.map(q => [q.id, q]));

  const POLICIES = {
    'Shanti Mohalla': [
      ['Textile warehouse separation', 'Retrofit two-hour fire-rated walls between contiguous garment godowns.'],
      ['External fire-escape easements', 'Mandate steel external fire stairs on rear alley elevations.'],
      ['Flammable scrap', 'Ban open-air sorting of synthetic cloth trimmings along residential lanes.']],
    'Seelampur': [
      ['Smelting and PCB salvage', 'Relocate unauthorised acid and copper recovery furnaces to the DSIIDC Narela industrial hub.'],
      ['Kabari Mandi arterial', 'Widen the main commercial approach to 6 m by clearing encroaching awnings.'],
      ['Transformer setbacks', 'Enforce a 3 m safety radius around BSES distribution transformers.']],
    'Gandhi Nagar': [
      ['Multi-storey egress', 'Mandate dual illuminated fire exits for workshops with more than 15 machine operators.'],
      ['Fire-engine approach', 'Install dry riser pipes at lane entries to supply upper-floor lofts without dragging hoses.']],
    'Subhash Nagar': [
      ['Mixed residential easements', 'Prevent ground-floor solvent storage beneath upper-floor living quarters.'],
      ['Narrow-lane quick attack', 'Deploy water-mist motorbikes for operations in lanes under 2 m.']]
  };

  // Cadastral context layers, loaded on demand from data/*.geojson.
  const CONTEXT = [
    { id: 'landuse', name: 'Land use', note: 'Parcel footprints by use class', kind: 'fill', files: [
      ['residential', 'Residential', '#2a78d6'], ['commercial', 'Commercial', '#e0602b'],
      ['com_res', 'Commercial + residential', '#12a06e'], ['ind_res', 'Industrial + residential', '#e0a100'],
      ['ind_com', 'Industrial + commercial', '#4a3aa7'], ['public_semi_public', 'Public / semi-public', '#C2337A']] },
    { id: 'height', name: 'Building height', note: 'Footprints by storey count', kind: 'fill', files: [
      ['g_plus_1', 'G+1', '#B9A2E3'], ['g_plus_2', 'G+2', '#8F72CE'], ['g_plus_3', 'G+3', '#6A4BB0'], ['g_plus_4', 'G+4', '#43297A']] },
    { id: 'streets', name: 'Street network', note: 'Surveyed lanes and major roads', kind: 'line', files: [
      ['streets', 'Lanes & streets', '#8A93A3', 1.2], ['roads', 'Major roads', '#3F4A5E', 2.6]] },
    { id: 'transit', name: 'Rail & metro', note: 'Red Line, stations and railway', kind: 'line', files: [
      ['railway', 'Railway', '#3F4A5E', 2, '6 5'], ['metro_line', 'Metro line', '#C2337A', 3], ['metro_station', 'Metro station', '#C2337A']] },
    { id: 'community', name: 'Community facilities', note: 'Schools, clinics, places of worship', kind: 'point', files: [
      ['schools', 'School', '#2a78d6'], ['health_centers', 'Health centre', '#12a06e'], ['religious_places', 'Place of worship', '#4a3aa7']] },
    { id: 'ward', name: 'Ward boundary', note: 'Municipal ward limit', kind: 'outline', files: [['ward_boundary', 'Ward boundary', '#3F4A5E']] }
  ];

  // =========================================================
  // STATE
  // =========================================================
  const state = {
    user: null,
    role: 'fire',
    view: 'map',
    filters: { q: '', loc: 'ALL', tiers: new Set(TIERS), quick: new Set(), factor: null },
    filtered: DATA,
    selectedId: null,
    side: null,            // null (overview) | 'unit' | 'dispatch' | 'hose'
    unitTab: 'inside',
    openMenu: null,        // null | 'conditions' | 'layers'
    sort: { col: 'fri', asc: false },
    weights: { ...BASE_WEIGHTS },
    basemap: 'streets',
    layers: { heat: false, incidents: false, stations: true, hospitals: true, boundary: true },
    context: new Set(),
    verified: new Set(),
    policyLoc: 'Seelampur',
    hosePlan: null,
    dispatchActive: false
  };

  // =========================================================
  // HELPERS
  // =========================================================
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const mean = arr => (arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0);
  const pct = (n, d) => (d ? Math.round((n / d) * 100) : 0);
  const f2 = n => Number(n).toFixed(2);
  // Plain-language readings of the 0–1 model values.
  const pts = v => Math.floor(v * 100 + 1e-9);                       // risk score out of 100; floored so it never crosses a tier line
  const grade = s => (s >= 0.7 ? 'Critical' : s >= 0.5 ? 'Poor' : s >= 0.3 ? 'Fair' : 'Good');
  const status = s => (s >= 0.7 ? ['High risk', 'bad'] : s >= 0.4 ? ['Some risk', 'warn'] : ['OK', 'ok']);
  const joinList = a => (a.length < 2 ? a.join('') : `${a.slice(0, -1).join(', ')} and ${a[a.length - 1]}`);
  const byId = id => DATA.find(w => w.id === id);
  const selected = () => (state.selectedId ? byId(state.selectedId) : null);
  const localities = () => {
    const m = new Map();
    DATA.forEach(w => m.set(w.loc, (m.get(w.loc) || 0) + 1));
    return [...m.entries()].sort((a, b) => b[1] - a[1]).map(([name]) => name);
  };
  const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

  const ICONS = {
    flame: '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/>',
    search: '<circle cx="11" cy="11" r="7"/><line x1="20" y1="20" x2="16.2" y2="16.2"/>',
    'chevron-down': '<polyline points="6 9 12 15 18 9"/>',
    'chevron-right': '<polyline points="9 18 15 12 9 6"/>',
    'arrow-left': '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
    plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    minus: '<line x1="5" y1="12" x2="19" y2="12"/>',
    x: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    frame: '<polyline points="8 3 3 3 3 8"/><polyline points="16 3 21 3 21 8"/><polyline points="8 21 3 21 3 16"/><polyline points="16 21 21 21 21 16"/>',
    crosshair: '<circle cx="12" cy="12" r="8"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>',
    truck: '<rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/>',
    cross: '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z"/>',
    play: '<polygon points="6 4 20 12 6 20 6 4"/>',
    pause: '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>',
    map: '<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/>',
    chart: '<line x1="4" y1="20" x2="20" y2="20"/><rect x="6" y="11" width="3" height="6"/><rect x="11" y="6" width="3" height="11"/><rect x="16" y="13" width="3" height="4"/>',
    table: '<rect x="3" y="4" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="10" x2="9" y2="20"/>',
    layers: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    clipboard: '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="m9 14 2 2 4-4"/>',
    sliders: '<line x1="4" y1="7" x2="6.5" y2="7"/><line x1="11.5" y1="7" x2="20" y2="7"/><circle cx="9" cy="7" r="2.5"/><line x1="4" y1="17" x2="12.5" y2="17"/><line x1="17.5" y1="17" x2="20" y2="17"/><circle cx="15" cy="17" r="2.5"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    filter: '<polygon points="3 4 21 4 14 12.5 14 19 10 21 10 12.5 3 4"/>',
    reset: '<polyline points="3 4 3 10 9 10"/><path d="M3.5 15a9 9 0 1 0 2.1-9.4L3 10"/>',
    droplet: '<path d="M12 2.5s6 6.3 6 11a6 6 0 0 1-12 0c0-4.7 6-11 6-11z"/>',
    route: '<circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M8.5 19H15a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h6.5"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/>',
    check: '<polyline points="20 6 9 17 4 12"/>',
    download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    printer: '<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
    building: '<rect x="4" y="3" width="16" height="18" rx="2"/><line x1="9" y1="8" x2="9" y2="8.01"/><line x1="15" y1="8" x2="15" y2="8.01"/><line x1="9" y1="12" x2="9" y2="12.01"/><line x1="15" y1="12" x2="15" y2="12.01"/><path d="M10 21v-4h4v4"/>',
    gauge: '<path d="M4 18a9 9 0 1 1 16 0"/><line x1="12" y1="14" x2="16" y2="9"/><circle cx="12" cy="14" r="1.5"/>',
    alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12" y2="17.01"/>',
    peak: '<polyline points="3 17 9 11 13 15 21 7"/><polyline points="15 7 21 7 21 13"/>',
    clock: '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.5 14"/>',
    ban: '<circle cx="12" cy="12" r="9"/><line x1="5.6" y1="5.6" x2="18.4" y2="18.4"/>',
    ruler: '<rect x="2" y="8" width="20" height="8" rx="1.5"/><line x1="7" y1="8" x2="7" y2="12"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="17" y1="8" x2="17" y2="12"/>',
    shield: '<path d="M12 3l8 3v6c0 4.5-3.2 7.9-8 9-4.8-1.1-8-4.5-8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    pin: '<path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>'
  };
  // Brighter tier colours for marks drawn on the dark hero panels.
  const TIER_GLOW = { Severe: '#FF5A4F', High: '#FF9142', Moderate: '#FFC83D', Low: '#2DD4BF' };
  const ico = (name, size = 16) =>
    `<svg class="ico" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ''}</svg>`;
  const hydrateIcons = root => $$('[data-ico]', root).forEach(el => { el.innerHTML = ico(el.dataset.ico); el.removeAttribute('data-ico'); });

  function toast(message, kind = 'info') {
    const el = document.createElement('div');
    el.className = `toast toast-${kind}`;
    el.textContent = message;
    $('#toasts').appendChild(el);
    setTimeout(() => { el.classList.add('is-leaving'); setTimeout(() => el.remove(), 220); }, 4200);
  }

  function download(filename, content, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const a = Object.assign(document.createElement('a'), { href: url, download: filename });
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  const tierTag = (tier, label = tier) => `<span class="tier tier-${tier}"><i></i>${label}</span>`;
  // Share of workshops per tier as a ring, with the total in the middle.
  function donutSvg(counts, n, onDark = true) {
    let acc = 0;
    const arcs = TIERS.filter(t => counts[t]).map(t => {
      const p = (counts[t] / n) * 100, seg = `<circle r="15.915" cx="21" cy="21" stroke="${onDark ? TIER_GLOW[t] : TIER[t].color}" data-tip="${t}: ${counts[t]} workshops (${pct(counts[t], n)}%)" stroke-dasharray="${Math.max(0.5, p - 1.2).toFixed(2)} ${(100 - Math.max(0.5, p - 1.2)).toFixed(2)}" stroke-dashoffset="${(25 - acc).toFixed(2)}"/>`;
      acc += p;
      return seg;
    }).join('');
    return `<svg class="donut-svg" viewBox="0 0 42 42" aria-hidden="true"><circle class="donut-track" r="15.915" cx="21" cy="21"/>${arcs}</svg>`;
  }
  const gaugeSvg = (fri, color) => `<svg class="gauge" viewBox="0 0 168 92" aria-hidden="true">
    <path class="gauge-track" d="M 14 84 A 70 70 0 0 1 154 84" pathLength="100"/>
    <path class="gauge-val" d="M 14 84 A 70 70 0 0 1 154 84" pathLength="100" stroke="${color}" stroke-dasharray="${(fri * 100).toFixed(1)} 100"/></svg>`;
  const meter = (value, color = 'var(--bar)') =>
    `<span class="meter"><span class="meter-fill" style="width:${Math.round(value * 100)}%;background:${color}"></span></span>`;
  const sevColor = s => (s >= 0.7 ? TIER.Severe.color : s >= 0.4 ? TIER.Moderate.color : TIER.Low.color);
  // One line of a ranked list: name, bar, value. `act` makes the row a control.
  const row = ({ name, sub = '', value, text, color, act = '', attrs = '', tip = '' }) =>
    `<li class="row${act ? ' is-link' : ''}"${act ? ` data-act="${act}" ${attrs} tabindex="0"` : ''}${tip ? ` data-tip="${tip}"` : ''}>
      <span class="row-name">${name}${sub ? `<em>${sub}</em>` : ''}</span>${meter(value, color)}<b>${text}</b></li>`;
  const tierCounts = list => Object.fromEntries(TIERS.map(t => [t, list.filter(w => w.tier === t).length]));
  const stackBar = (counts, n) => `<div class="stack" role="img" aria-label="Share of workshops by risk tier">
    ${TIERS.filter(t => counts[t]).map(t => `<span style="flex:${counts[t]};background:${TIER[t].color}" data-tip="${t}: ${counts[t]} workshops (${pct(counts[t], n)}%)"></span>`).join('')}</div>`;

  // =========================================================
  // SESSION
  // =========================================================
  const SESSION_KEY = 'seelampur_user';
  const VIEWS = ['map', 'insights', 'registry', 'workspace'];
  const readSession = () => { try { return JSON.parse(sessionStorage.getItem(SESSION_KEY)); } catch (e) { return null; } };
  const writeSession = user => {
    try { user ? sessionStorage.setItem(SESSION_KEY, JSON.stringify(user)) : sessionStorage.removeItem(SESSION_KEY); } catch (e) { /* storage unavailable */ }
  };

  function signIn(user) {
    state.user = user;
    state.role = ROLES[user.role] ? user.role : 'fire';
    writeSession(user);
    $('#login-screen').hidden = true;
    $('#app').hidden = false;
    renderShell();
    initMap();
    applyFilters();
    setView(VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'map');
  }

  function signOut() {
    endDispatch();
    setSide(null);
    state.user = null;
    writeSession(null);
    $('#app').hidden = true;
    $('#login-screen').hidden = false;
  }

  function renderLogin() {
    $('#login-roles').innerHTML = Object.entries(ROLES).map(([key, r]) => `
      <button type="button" class="role-item" data-act="quick-login" data-role="${key}">
        <span class="avatar avatar-${key}">${ico(r.icon, 18)}</span>
        <span class="role-item-text"><b>${r.title}</b><span>${r.name} · ${r.blurb}</span></span>
        <span class="role-item-go">${ico('chevron-right', 16)}</span>
      </button>`).join('');
    const severe = DATA.filter(w => w.tier === 'Severe').length;
    $('#login-stats').innerHTML = [
      [DATA.length, 'workshops surveyed'],
      [`${pct(severe, DATA.length)}%`, 'at severe risk'],
      [DATA.filter(w => w.incident).length, 'with a past fire'],
      [localities().length, 'localities']
    ].map(([v, l]) => `<div><dt>${v}</dt><dd>${l}</dd></div>`).join('');

    // Miniature atlas: the real survey points inside the study-area outline.
    const W = 520, H = 260, P = 14;
    const lats = STUDY_AREA_POLYGON.map(p => p[0]), lngs = STUDY_AREA_POLYGON.map(p => p[1]);
    const minLat = Math.min(...lats), maxLat = Math.max(...lats), minLng = Math.min(...lngs), maxLng = Math.max(...lngs);
    const kx = Math.cos(((minLat + maxLat) / 2) * Math.PI / 180);
    const s = Math.min((W - 2 * P) / ((maxLng - minLng) * kx), (H - 2 * P) / (maxLat - minLat));
    const ox = (W - (maxLng - minLng) * kx * s) / 2, oy = (H - (maxLat - minLat) * s) / 2;
    const pt = (lat, lng) => [(ox + (lng - minLng) * kx * s).toFixed(1), (oy + (maxLat - lat) * s).toFixed(1)];
    $('#login-atlas-svg').innerHTML = `<polygon class="atlas-outline" points="${STUDY_AREA_POLYGON.map(p => pt(p[0], p[1]).join(',')).join(' ')}"/>
      <g class="atlas-dots">${[...DATA].sort((a, b) => a.fri - b.fri).map((w, i) => {
        const [x, y] = pt(w.lat, w.lng);
        return `<circle cx="${x}" cy="${y}" r="3.6" fill="${TIER_GLOW[w.tier]}" style="animation-delay:${i * 5}ms"/>`;
      }).join('')}</g>`;
    $('#login-atlas-key').innerHTML = TIERS.map(t =>
      `<span><i style="background:${TIER_GLOW[t]}"></i>${t} <b>${DATA.filter(w => w.tier === t).length}</b></span>`).join('');
  }

  function handleLoginSubmit(e) {
    e.preventDefault();
    const email = $('#login-email').value.trim().toLowerCase();
    const password = $('#login-password').value;
    const err = $('#login-error');
    const fail = msg => { err.textContent = msg; err.hidden = false; };
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return fail('Enter a valid email address.');
    if (password !== DEMO_PASSWORD) return fail(`Password not recognised. The demo password is ${DEMO_PASSWORD}.`);
    err.hidden = true;
    const roleKey = Object.keys(ROLES).find(k => ROLES[k].email === email);
    const local = email.split('@')[0];
    signIn(roleKey
      ? { email, role: roleKey, name: ROLES[roleKey].name, title: ROLES[roleKey].title, initials: ROLES[roleKey].initials }
      : { email, role: 'fire', name: local, title: 'Fire Safety Analyst', initials: local.slice(0, 2).toUpperCase() });
  }

  // =========================================================
  // SHELL
  // =========================================================
  const VIEW_LABEL = { map: 'Map', insights: 'Insights', registry: 'Workshops' };

  function renderShell() {
    const role = ROLES[state.role];
    const viewIcon = { map: 'map', insights: 'chart', registry: 'table', workspace: role.icon };
    $('#nav').innerHTML = VIEWS.map(v =>
      `<button type="button" class="tab${state.view === v ? ' is-active' : ''}" data-act="view" data-view="${v}"><span class="tab-ico">${ico(viewIcon[v], 15)}</span><span class="tab-lbl">${v === 'workspace' ? role.workspace : VIEW_LABEL[v]}</span></button>`).join('');
    renderRoleMenu();
    const u = state.user;
    $('#user').innerHTML = `<span class="avatar avatar-${ROLES[u.role] ? u.role : 'fire'}">${esc(u.initials)}</span><span class="user-text"><b>${esc(u.name)}</b><span>${esc(u.title)}</span></span>`;
  }

  // Role switcher in the nav bar: a button showing the current desk, opening a menu of all four.
  function renderRoleMenu() {
    const el = $('#rolemenu'), r = ROLES[state.role], open = state.openMenu === 'role';
    el.className = `dd dd-right rolemenu${open ? ' is-open' : ''}`;
    el.innerHTML = `<button type="button" class="rolebtn" data-act="menu" data-menu="role" aria-expanded="${open}" title="Switch workspace">
        <span class="avatar avatar-${state.role}">${ico(r.icon, 14)}</span>
        <span class="rolebtn-text"><small>Viewing as</small><b>${r.short}</b></span>${ico('chevron-down', 13)}</button>
      <div class="dd-menu">
        <p class="dd-title">Switch workspace</p>
        ${Object.entries(ROLES).map(([key, x]) => `<button type="button" class="menuitem${key === state.role ? ' is-active' : ''}" data-act="role" data-role="${key}">
          <span class="avatar avatar-${key}">${ico(x.icon, 15)}</span>
          <span class="menuitem-text"><b>${x.title}</b><span>${x.workspace} workspace</span></span>${key === state.role ? ico('check', 15) : ''}</button>`).join('')}
      </div>`;
  }
  const renderMenus = () => { renderToolbar(); renderRoleMenu(); };

  function setView(view) {
    const changed = state.view !== view || !state.entered;
    state.entered = true;
    state.view = view;
    state.openMenu = null;
    $$('.view').forEach(el => {
      el.hidden = el.dataset.view !== view;
      // Entrance animation only when the view actually changes, not on every re-render.
      if (changed) el.classList.toggle('is-entering', el.dataset.view === view);
    });
    if (changed) setTimeout(() => $$('.view.is-entering').forEach(el => el.classList.remove('is-entering')), 900);
    $$('#nav .tab').forEach(b => b.classList.toggle('is-active', b.dataset.view === view));
    if (location.hash.slice(1) !== view) history.replaceState(null, '', `#${view}`);
    renderRoleMenu();
    renderFilterBar();
    if (view === 'map') { renderToolbar(); requestAnimationFrame(() => map && map.invalidateSize()); }
    if (view === 'insights') renderInsights();
    if (view === 'registry') renderRegistry();
    if (view === 'workspace') renderWorkspace();
  }

  function setRole(role) {
    state.role = role;
    renderShell();
    if (state.side === 'unit') renderSide();
    if (state.view === 'workspace') renderWorkspace();
  }

  // =========================================================
  // FILTERS
  // =========================================================
  function matches(w, skip) {
    const f = state.filters;
    if (skip !== 'loc' && f.loc !== 'ALL' && w.loc !== f.loc) return false;
    if (skip !== 'tier' && !f.tiers.has(w.tier)) return false;
    for (const id of f.quick) if (!QUICK_BY_ID[id].test(w)) return false;
    if (f.factor && score(w, f.factor) < FAIL_SCORE) return false;
    if (f.q) {
      const hay = `${w.ent} ${w.id} ${w.work} ${w.area} ${w.loc}`.toLowerCase();
      if (!hay.includes(f.q)) return false;
    }
    return true;
  }
  const isFiltered = () => {
    const f = state.filters;
    return !!(f.q || f.loc !== 'ALL' || f.tiers.size !== TIERS.length || f.quick.size || f.factor);
  };

  function resetFilters() {
    state.filters = { q: '', loc: 'ALL', tiers: new Set(TIERS), quick: new Set(), factor: null };
    $('#search-input').value = '';
    applyFilters();
  }

  function applyFilters() {
    state.filtered = DATA.filter(w => matches(w));
    renderMarkers();
    renderHeat();
    renderIncidentRings();
    renderToolbar();
    renderFilterBar();
    if (!state.side) renderSide();
    if (state.view === 'insights') renderInsights();
    if (state.view === 'registry') renderRegistry();
  }

  const checkrow = (kind, value, label, checked, note = '') =>
    `<label class="checkrow"><input type="checkbox" data-change="${kind}" value="${value}"${checked ? ' checked' : ''}><span>${label}</span>${note !== '' ? `<em>${note}</em>` : ''}</label>`;

  // The map toolbar: every filter one click away, tier toggles doubling as the legend.
  function renderToolbar() {
    const f = state.filters;
    const locBase = DATA.filter(w => matches(w, 'loc'));
    const tierBase = DATA.filter(w => matches(w, 'tier'));
    const nCond = f.quick.size + (f.factor ? 1 : 0);
    const caret = ico('chevron-down', 13);
    $('#toolbar').innerHTML = `
      <div class="dd${state.openMenu === 'loc' ? ' is-open' : ''}">
        <button type="button" class="tb-btn${f.loc !== 'ALL' ? ' is-set' : ''}" data-act="menu" data-menu="loc" aria-expanded="${state.openMenu === 'loc'}">${ico('pin', 14)}${f.loc === 'ALL' ? 'All localities' : esc(f.loc)}${caret}</button>
        <div class="dd-menu">
          <p class="dd-title">Locality</p>
          ${[['ALL', 'All localities', locBase.length], ...localities().map(l => [l, l, locBase.filter(w => w.loc === l).length])].map(([value, label, count]) =>
            `<button type="button" class="menuitem${f.loc === value ? ' is-active' : ''}" data-act="f-loc" data-loc="${esc(value)}"><span class="menuitem-text"><b>${esc(label)}</b></span><em>${count}</em>${f.loc === value ? ico('check', 14) : ''}</button>`).join('')}
        </div>
      </div>
      <div class="tb-tiers" role="group" aria-label="Risk tier">
        ${TIERS.map(t => `<button type="button" class="tiertoggle${f.tiers.has(t) ? ' is-on' : ''}" style="--c:${TIER[t].color}" data-act="f-tier" data-tier="${t}" aria-pressed="${f.tiers.has(t)}" title="${t} risk: score ${TIER[t].range}">
          <i></i>${t}<b>${tierBase.filter(w => w.tier === t).length}</b></button>`).join('')}
      </div>
      <div class="dd${state.openMenu === 'conditions' ? ' is-open' : ''}">
        <button type="button" class="tb-btn" data-act="menu" data-menu="conditions" aria-expanded="${state.openMenu === 'conditions'}">${ico('filter', 14)}Conditions${nCond ? `<b class="count">${nCond}</b>` : ''}${caret}</button>
        <div class="dd-menu">
          <p class="dd-title">Show only workshops with</p>
          ${QUICK.map(q => checkrow('quick', q.id, q.label, f.quick.has(q.id), state.filtered.filter(q.test).length)).join('')}
          ${f.factor ? `<p class="dd-note">Also limited to units deficient in ${FACTORS[f.factor].name.toLowerCase()}. <button type="button" class="link" data-act="f-factor-clear">Remove</button></p>` : ''}
        </div>
      </div>
      <button type="button" class="tb-btn tb-plain" data-act="f-reset"${isFiltered() ? '' : ' disabled'}>${ico('reset', 13)}<span>Reset</span></button>
      <span class="tb-space"></span>
      <div class="dd dd-right${state.openMenu === 'layers' ? ' is-open' : ''}">
        <button type="button" class="tb-btn" data-act="menu" data-menu="layers" aria-expanded="${state.openMenu === 'layers'}">${ico('layers', 14)}Layers${caret}</button>
        <div class="dd-menu dd-layers">
          <p class="dd-title">Basemap</p>
          <div class="seg">
            ${[['streets', 'Streets'], ['satellite', 'Satellite'], ['blank', 'None']].map(([id, label]) =>
              `<button type="button" class="seg-btn${state.basemap === id ? ' is-active' : ''}" data-act="basemap" data-base="${id}">${label}</button>`).join('')}
          </div>
          <p class="dd-title">Risk and response</p>
          ${checkrow('layer', 'heat', 'Risk heatmap', state.layers.heat)}
          ${checkrow('layer', 'incidents', 'Past fire incidents', state.layers.incidents)}
          ${checkrow('layer', 'stations', 'Fire stations', state.layers.stations, FIRE_STATIONS.length)}
          ${checkrow('layer', 'hospitals', 'Hospitals and clinics', state.layers.hospitals, HOSPITALS.length)}
          ${checkrow('layer', 'boundary', 'Study area outline', state.layers.boundary)}
          <p class="dd-title">Survey layers</p>
          ${CONTEXT.map(g => checkrow('context', g.id, g.name, state.context.has(g.id))).join('')}
        </div>
      </div>`;
  }

  // Active-filter summary shown above the page views (the map shows the same state in its toolbar).
  function renderFilterBar() {
    const bar = $('#filterbar');
    if (state.view === 'map' || !isFiltered()) { bar.hidden = true; return; }
    const f = state.filters;
    const chips = [];
    if (f.q) chips.push(['q', `Search “${esc(f.q)}”`]);
    if (f.loc !== 'ALL') chips.push(['loc', esc(f.loc)]);
    if (f.tiers.size !== TIERS.length) chips.push(['tier', f.tiers.size ? TIERS.filter(t => f.tiers.has(t)).join(', ') : 'No tiers']);
    f.quick.forEach(id => chips.push([`quick:${id}`, QUICK_BY_ID[id].label]));
    if (f.factor) chips.push(['factor', `Deficient: ${FACTORS[f.factor].name}`]);
    bar.hidden = false;
    bar.innerHTML = `<span class="fb-count">Filtered: <b>${state.filtered.length}</b> of ${DATA.length}</span>
      ${chips.map(([k, label]) => `<button type="button" class="fb-chip" data-act="f-remove" data-key="${k}" title="Remove filter">${label}${ico('x', 12)}</button>`).join('')}
      <button type="button" class="link" data-act="f-reset">Clear all</button>`;
  }

  // =========================================================
  // MAP
  // =========================================================
  let map = null;
  const lyr = { base: {}, units: null, halo: null, heat: null, rings: null, stations: null, hospitals: null, boundary: null, user: null, context: {} };
  let canvasRenderer = null;
  const FIT = { paddingTopLeft: [36, 36], paddingBottomRight: [36, 36] };

  function initMap() {
    if (map) { map.invalidateSize(); return; }
    // Whole-number zoom levels only: raster tiles are sharp at their native size and blur when scaled.
    map = L.map('map', { center: [28.6665, 77.2720], zoom: 16, maxZoom: 19, zoomSnap: 1, zoomControl: false });
    map.attributionControl.setPrefix(false);
    map.createPane('context').style.zIndex = 350;
    map.createPane('contextPts').style.zIndex = 390;
    canvasRenderer = L.canvas({ pane: 'context', padding: 0.4 });

    lyr.base.streets = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors' });
    lyr.base.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19, attribution: 'Imagery &copy; Esri, Maxar, Earthstar Geographics' });
    lyr.base.blank = L.layerGroup();
    lyr.base[state.basemap].addTo(map);

    lyr.boundary = L.polygon(STUDY_AREA_POLYGON, { color: '#15181C', weight: 1.5, dashArray: '6 5', fill: false, interactive: false });
    lyr.units = L.layerGroup().addTo(map);
    lyr.rings = L.layerGroup();

    const facility = (list, cls, icon, kicker) => L.layerGroup(list.map(p =>
      L.marker([p.lat, p.lng], { icon: L.divIcon({ className: '', html: `<div class="fac fac-${cls}">${ico(icon, 12)}</div>`, iconSize: [22, 22], iconAnchor: [11, 11] }), keyboard: false })
        .bindPopup(`<div class="pop"><p class="pop-kicker">${kicker}</p><p class="pop-title">${esc(p.name)}</p><p class="pop-desc">${esc(p.desc)}</p></div>`)));
    lyr.stations = facility(FIRE_STATIONS, 'station', 'flame', 'Fire station');
    lyr.hospitals = facility(HOSPITALS, 'hospital', 'cross', 'Medical');

    syncOverlays();
    renderLegend();
    fitTo(DATA, false);
    map.on('click', () => { if (state.side === 'unit') setSide(null); });
  }

  function fitTo(list, animate = true) {
    if (!map || !list.length) return;
    const b = L.latLngBounds(list.map(w => [w.lat, w.lng]));
    map[animate ? 'flyToBounds' : 'fitBounds'](b, { ...FIT, maxZoom: 18, duration: 0.6 });
  }
  const flyToUnit = (w, zoom = 18) => map.flyTo([w.lat, w.lng], Math.max(map.getZoom(), zoom), { duration: 0.6 });

  function setBasemap(id) {
    if (!lyr.base[id] || id === state.basemap) return;
    map.removeLayer(lyr.base[state.basemap]);
    lyr.base[id].addTo(map);
    state.basemap = id;
    renderToolbar();
  }

  function syncOverlays() {
    const toggle = (layer, on) => { if (!layer) return; on ? layer.addTo(map) : map.removeLayer(layer); };
    toggle(lyr.boundary, state.layers.boundary);
    toggle(lyr.stations, state.layers.stations);
    toggle(lyr.hospitals, state.layers.hospitals);
    toggle(lyr.rings, state.layers.incidents);
    toggle(lyr.heat, state.layers.heat);
  }

  function renderMarkers() {
    if (!map) return;
    lyr.units.clearLayers();
    [...state.filtered].sort((a, b) => a.fri - b.fri).forEach(w => {
      L.circleMarker([w.lat, w.lng], { radius: 6, fillColor: TIER[w.tier].color, fillOpacity: 1, color: '#fff', weight: 1.5, bubblingMouseEvents: false })
        .bindTooltip(`<b>${esc(w.ent)}</b><span>${esc(w.loc)} · ${w.tier} risk, ${pts(w.fri)}/100${w.incident ? ' · past fire' : ''}</span>`,
          { direction: 'top', offset: [0, -7], className: 'unit-tip' })
        .on('click', () => selectUnit(w.id))
        .addTo(lyr.units);
    });
    renderHalo();
  }

  function renderHalo() {
    if (!map) return;
    if (lyr.halo) { map.removeLayer(lyr.halo); lyr.halo = null; }
    const w = selected();
    if (w) lyr.halo = L.circleMarker([w.lat, w.lng], { radius: 12, color: '#15181C', weight: 2.5, fill: false, interactive: false }).addTo(map);
  }

  function renderHeat() {
    if (!map) return;
    if (lyr.heat) map.removeLayer(lyr.heat);
    lyr.heat = L.heatLayer(state.filtered.map(w => [w.lat, w.lng, w.fri]), {
      radius: 30, blur: 24, maxZoom: 17, minOpacity: 0.25,
      gradient: { 0.3: TIER.Low.color, 0.5: TIER.Moderate.color, 0.7: TIER.High.color, 1.0: TIER.Severe.color }
    });
    if (state.layers.heat) lyr.heat.addTo(map);
  }

  function renderIncidentRings() {
    if (!map) return;
    lyr.rings.clearLayers();
    state.filtered.filter(w => w.incident).forEach(w =>
      L.circleMarker([w.lat, w.lng], { radius: 10, color: '#15181C', weight: 1.4, dashArray: '2 3', fill: false, interactive: false }).addTo(lyr.rings));
  }

  // Key for the survey layers; the tier colours are already keyed by the toolbar toggles.
  function renderLegend() {
    const groups = CONTEXT.filter(g => state.context.has(g.id) && g.files.length > 1);
    const el = $('#legend');
    el.hidden = !groups.length;
    el.innerHTML = groups.map(g => `<div class="lg-block"><span class="lg-title">${g.name}</span>
      ${g.files.map(([, label, color]) => `<span class="lg-item"><i class="${g.kind === 'fill' ? 'sq' : g.kind === 'line' ? 'ln' : 'dot'}" style="background:${color}"></i>${label}</span>`).join('')}</div>`).join('');
  }

  async function toggleContext(id) {
    const group = CONTEXT.find(g => g.id === id);
    if (state.context.has(id)) {
      state.context.delete(id);
      if (lyr.context[id]) map.removeLayer(lyr.context[id]);
    } else {
      // Land use and building height describe the same footprints, so show one at a time.
      const rival = id === 'landuse' ? 'height' : id === 'height' ? 'landuse' : null;
      if (rival && state.context.has(rival)) { state.context.delete(rival); map.removeLayer(lyr.context[rival]); }
      state.context.add(id);
      try {
        if (!lyr.context[id]) lyr.context[id] = await loadContext(group);
        if (state.context.has(id)) lyr.context[id].addTo(map);
      } catch (err) {
        state.context.delete(id);
        toast(location.protocol === 'file:'
          ? 'Survey layers need the app served over http. Run start.bat or python serve.py.'
          : `Could not load the ${group.name.toLowerCase()} layer.`, 'error');
      }
    }
    renderToolbar();
    renderLegend();
  }

  async function loadContext(group) {
    const parts = await Promise.all(group.files.map(async ([file, label, color, weight, dash]) => {
      const res = await fetch(`data/${file}.geojson`);
      if (!res.ok) throw new Error(`${file}: ${res.status}`);
      const geo = await res.json();
      const isPoint = geo.features.length && geo.features[0].geometry.type === 'Point';
      if (isPoint) {
        return L.geoJSON(geo, { pointToLayer: (ft, latlng) =>
          L.circleMarker(latlng, { pane: 'contextPts', radius: 4.5, fillColor: color, fillOpacity: 1, color: '#fff', weight: 1.4 })
            .bindTooltip(esc((ft.properties && ft.properties.Name) || label), { className: 'unit-tip', direction: 'top', offset: [0, -6] }) });
      }
      const style = group.kind === 'fill' ? { fillColor: color, fillOpacity: 0.6, color: '#fff', weight: 0.5 }
        : group.kind === 'outline' ? { color, weight: 1.8, dashArray: '8 6', fill: false }
        : { color, weight: weight || 1.5, dashArray: dash || null, opacity: 0.9 };
      return L.geoJSON(geo, { renderer: canvasRenderer, pane: 'context', interactive: false, style });
    }));
    return L.layerGroup(parts);
  }

  function locateUser() {
    if (!navigator.geolocation) return toast('This browser does not support geolocation.', 'error');
    navigator.geolocation.getCurrentPosition(pos => {
      showUser(pos.coords.latitude, pos.coords.longitude);
      map.flyTo([pos.coords.latitude, pos.coords.longitude], 16, { duration: 0.6 });
    }, () => toast('Location permission was denied.', 'error'), { timeout: 10000 });
  }
  function showUser(lat, lng) {
    if (lyr.user) map.removeLayer(lyr.user);
    lyr.user = L.marker([lat, lng], { icon: L.divIcon({ className: '', html: '<div class="me"></div>', iconSize: [16, 16], iconAnchor: [8, 8] }), keyboard: false })
      .bindTooltip('Your position', { className: 'unit-tip', direction: 'top', offset: [0, -8] }).addTo(map);
  }

  // =========================================================
  // SIDE PANEL: overview, unit, dispatch, hose plan
  // =========================================================
  function selectUnit(id, { fly = false } = {}) {
    const w = byId(id);
    if (!w) return;
    state.selectedId = id;
    if (state.view !== 'map') setView('map');
    setSide('unit');
    if (fly) requestAnimationFrame(() => flyToUnit(w));
  }

  function setSide(mode) {
    if (state.side === 'hose' && mode !== 'hose') clearHose();
    state.side = mode;
    if (!mode && !state.dispatchActive) state.selectedId = null;
    renderSide();
    renderHalo();
  }

  function renderSide() {
    const el = $('#side'), w = selected();
    if (state.side === 'unit' && w) el.innerHTML = unitHtml(w);
    else if (state.side === 'hose' && state.hosePlan) el.innerHTML = hoseHtml(state.hosePlan);
    else if (state.side === 'dispatch' && state.dispatchActive) { el.innerHTML = dispatchHtml(); renderRouteSteps(); refreshSimControls(); }
    else { state.side = null; el.innerHTML = overviewHtml(); }
    $('#view-map').classList.toggle('has-detail', !!state.side);
  }

  const liveBanner = () => (state.dispatchActive ? `<div class="live-banner"><span class="pulse"></span><span>Dispatch in progress to <b>${esc(sim.target.ent)}</b></span>
    <button type="button" class="link" data-act="dispatch-view">Open</button></div>` : '');

  function overviewHtml() {
    const list = state.filtered, n = list.length, counts = tierCounts(list);
    const top = [...list].sort((a, b) => b.fri - a.fri).slice(0, 40);
    const avg = mean(list.map(w => w.fri));
    return `
      <header class="side-head">
        <span class="side-ico">${ico('map', 18)}</span>
        <div class="side-headline"><h2>Overview</h2>
          <p>${n} of ${DATA.length} workshops${isFiltered() ? ` · <button type="button" class="link" data-act="f-reset">clear filters</button>` : ''}</p></div>
      </header>
      <div class="side-body">
        ${liveBanner()}
        ${n ? `<section class="hero hero-overview">
          <div class="donut">${donutSvg(counts, n)}<div class="donut-num"><b>${n}</b><span>workshops</span></div></div>
          <div class="hero-side">
            <p class="hero-lbl">Average risk score</p>
            <p class="hero-big">${pts(avg)}<small>/100</small></p>
            <p class="hero-note">${tierTag(tierOf(avg), `${tierOf(avg)} risk`)}</p>
          </div>
          <dl class="hero-facts">
            <div><dt>Severe risk</dt><dd>${pct(counts.Severe, n)}%</dd></div>
            <div><dt>Had a fire before</dt><dd>${list.filter(w => w.incident).length}</dd></div>
            <div><dt>Only one exit</dt><dd>${list.filter(w => w.cats.exits === '1 exit').length}</dd></div>
          </dl>
        </section>
        <section class="side-sec">
          <h3>Risk levels <span>score out of 100</span></h3>
          <table class="mini">
            ${TIERS.map(t => `<tr><td>${tierTag(t)}</td><td class="muted">${TIER[t].range}</td><td class="num">${counts[t]}</td><td class="num muted">${pct(counts[t], n)}%</td></tr>`).join('')}
          </table>
        </section>
        <section class="side-sec">
          <h3>Highest risk in view <span>select to inspect</span></h3>
          <ul class="picklist">
            ${top.map((w, i) => `<li><button type="button" data-act="open-unit" data-id="${esc(w.id)}">
              <span class="pick-rank">${i + 1}</span>
              <span class="pick-name">${esc(w.ent)}<em>${esc(w.loc)}</em></span><b class="score score-${w.tier}">${pts(w.fri)}</b></button></li>`).join('')}
          </ul>
        </section>` : '<p class="side-empty">No workshops match the current filters.</p>'}
      </div>`;
  }

  // How this workshop compares with the rest, in one sentence.
  function unitStanding(w) {
    const below = DATA.filter(x => x.fri < w.fri).length, above = DATA.filter(x => x.fri > w.fri).length, others = DATA.length - 1;
    if (!above) return 'The highest risk of all the workshops surveyed.';
    return below >= above ? `Riskier than ${pct(below, others)}% of the other workshops surveyed.`
      : `Safer than ${pct(above, others)}% of the other workshops surveyed.`;
  }
  // The worst few findings, named as problems.
  function unitProblems(w) {
    const bad = FACTOR_KEYS.map(k => ({ k, s: score(w, k) })).filter(x => x.s >= FAIL_SCORE).sort((a, b) => b.s - a.s);
    if (!bad.length) return 'No serious problems were found here.';
    const more = bad.length > 3 ? `, plus ${bad.length - 3} more` : '';
    return `Main problems: ${joinList(bad.slice(0, 3).map(x => FACTORS[x.k].phrase))}${more}.`;
  }

  function unitHtml(w) {
    const factors = FACTOR_KEYS.filter(k => FACTORS[k].scope === state.unitTab)
      .map(k => ({ k, s: score(w, k), lv: levelOf(w, k) })).sort((a, b) => b.s - a.s);
    const nIn = FACTOR_KEYS.filter(k => FACTORS[k].scope === 'inside').length;
    const verified = state.verified.has(w.id) || w.verified;
    return `
      <header class="side-head">
        <span class="side-ico tier-${w.tier}">${ico('building', 18)}</span>
        <div class="side-headline">
          <p class="side-kicker"><span class="mono">${esc(w.id)}</span> · ${esc(w.area)}</p>
          <h2>${esc(w.ent)}</h2>
          <p>${esc(w.work)}</p>
        </div>
        <button type="button" class="icon-btn" data-act="side-close" aria-label="Close" title="Back to overview">${ico('x', 16)}</button>
      </header>
      <div class="side-body">
        ${liveBanner()}
        <section class="hero hero-unit" style="--glow:${TIER_GLOW[w.tier]}">
          <div class="hero-gauge">${gaugeSvg(w.fri, TIER_GLOW[w.tier])}
            <div class="hero-num"><b>${pts(w.fri)}</b><span>risk score out of 100</span></div></div>
          <div class="hero-side">
            <div class="hero-tags">${tierTag(w.tier, `${w.tier} risk`)}${w.incident ? `<span class="flag flag-fire">${ico('flame', 11)}Had a fire before</span>` : ''}${verified ? `<span class="flag flag-ok">${ico('check', 11)}Verified</span>` : ''}</div>
            <p class="hero-standing">${unitStanding(w)}</p>
          </div>
          <ul class="hero-subs">
            ${SUBS.map(s => `<li data-tip="${s.note}"><span>${s.name}</span>${meter(w[s.key], TIER_GLOW[tierOf(w[s.key])])}<b>${grade(w[s.key])}</b></li>`).join('')}
          </ul>
        </section>
        <p class="summary">${unitProblems(w)}</p>

        <div class="actions">
          <button type="button" class="btn btn-danger" data-act="dispatch" data-type="fire">${ico('flame', 16)}Dispatch fire tender</button>
          <button type="button" class="btn" data-act="dispatch" data-type="hospital">${ico('cross', 14)}Ambulance</button>
          <button type="button" class="btn" data-act="hose">${ico('droplet', 14)}Hose plan</button>
          <button type="button" class="btn" data-act="zoom-unit">${ico('target', 14)}Zoom to</button>
          <button type="button" class="btn" data-act="dispatch" data-type="user">${ico('route', 14)}Route from me</button>
          ${state.role === 'surveyor' && !verified ? `<button type="button" class="btn" data-act="verify" data-id="${esc(w.id)}">${ico('check', 14)}Mark verified</button>` : ''}
        </div>

        <section class="side-sec">
          <h3>What the survey found <span>select a row to read more</span></h3>
          <div class="seg" role="tablist">
            <button type="button" role="tab" class="seg-btn${state.unitTab === 'inside' ? ' is-active' : ''}" data-act="unit-tab" data-tab="inside">Inside the building (${nIn})</button>
            <button type="button" role="tab" class="seg-btn${state.unitTab === 'outside' ? ' is-active' : ''}" data-act="unit-tab" data-tab="outside">Surroundings (${FACTOR_KEYS.length - nIn})</button>
          </div>
          <ul class="factors">
            ${factors.map(({ k, s, lv }) => `
              <li><details>
                <summary>
                  <span class="factor-name">${FACTORS[k].name}</span>
                  <span class="factor-val">${esc(lv[0])}</span>
                  <span class="status status-${status(s)[1]}">${status(s)[0]}</span>
                </summary>
                <p>${esc(lv[1])}</p>
              </details></li>`).join('')}
          </ul>
        </section>
      </div>`;
  }

  // =========================================================
  // LIVE DISPATCH SIMULATION
  // =========================================================
  const sim = {
    running: false, paused: false, type: 'fire', speed: 2, follow: true, route: null, bounds: null,
    coords: [], dist: [], total: 0, duration: 0, elapsed: 0, last: 0, target: null, origin: null,
    step: 0, raf: null, fallback: false, arrived: false, layers: [], beacon: null, vehicle: null, done: null, todo: null
  };

  const toRad = d => d * Math.PI / 180;
  function distM(lat1, lng1, lat2, lng2) {
    const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1);
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
    return 6371000 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }
  function bearing(lat1, lng1, lat2, lng2) {
    const y = Math.sin(toRad(lng2 - lng1)) * Math.cos(toRad(lat2));
    const x = Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) - Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(toRad(lng2 - lng1));
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
  }
  const nearest = (list, w) => list.reduce((best, p) => (distM(w.lat, w.lng, p.lat, p.lng) < distM(w.lat, w.lng, best.lat, best.lng) ? p : best), list[0]);

  const TURN_SVG = {
    left: '<polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/>',
    right: '<polyline points="15 14 20 9 15 4"/><path d="M4 20v-7a4 4 0 0 1 4-4h12"/>',
    'slight-left': '<polyline points="6 10 6 4 12 4"/><line x1="6" y1="4" x2="18" y2="16"/><line x1="18" y1="16" x2="18" y2="20"/>',
    'slight-right': '<polyline points="18 10 18 4 12 4"/><line x1="18" y1="4" x2="6" y2="16"/><line x1="6" y1="16" x2="6" y2="20"/>',
    uturn: '<polyline points="9 10 4 15 9 20"/><path d="M20 4v7a5 5 0 0 1-10 0V4"/>',
    arrive: '<path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    straight: '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>'
  };
  const turnSvg = (action, size = 22) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${TURN_SVG[action.replace('sharp-', '')] || TURN_SVG.straight}</svg>`;

  function maneuver(step) {
    if (!step || !step.maneuver) return { action: 'straight', label: 'Continue', street: 'along the route' };
    const type = (step.maneuver.type || '').toLowerCase(), mod = (step.maneuver.modifier || '').toLowerCase();
    const street = step.name ? `onto ${step.name}` : 'into an unnamed lane';
    if (type === 'arrive') return { action: 'arrive', label: 'Arrive', street: step.name ? `at ${step.name}` : 'at the workshop lane' };
    if (type === 'depart') return { action: 'straight', label: 'Depart', street: step.name ? `from ${step.name}` : 'from base' };
    if (mod.includes('uturn')) return { action: 'uturn', label: 'U-turn', street };
    if (mod.includes('sharp left')) return { action: 'sharp-left', label: 'Sharp left', street };
    if (mod.includes('sharp right')) return { action: 'sharp-right', label: 'Sharp right', street };
    if (mod.includes('slight left')) return { action: 'slight-left', label: 'Bear left', street };
    if (mod.includes('slight right')) return { action: 'slight-right', label: 'Bear right', street };
    if (mod.includes('left')) return { action: 'left', label: 'Turn left', street };
    if (mod.includes('right')) return { action: 'right', label: 'Turn right', street };
    return { action: 'straight', label: 'Continue', street };
  }

  const DISPATCH = {
    fire: { unit: 'Fire tender', color: '#C92A1E', going: 'Fire tender en route', done: 'Fire tender on scene' },
    hospital: { unit: 'Ambulance', color: '#2a78d6', going: 'Ambulance en route', done: 'Ambulance on scene' },
    user: { unit: 'You', color: '#15181C', going: 'Routing from your position', done: 'You have arrived' }
  };

  function startDispatch(type, workshop) {
    const w = workshop || selected() || sim.target;
    if (!w) return toast('Select a workshop first.', 'error');
    if (type === 'user') {
      if (!navigator.geolocation) return toast('This browser does not support geolocation.', 'error');
      toast('Finding your position…');
      navigator.geolocation.getCurrentPosition(
        pos => { showUser(pos.coords.latitude, pos.coords.longitude); beginDispatch('user', w, { name: 'Your position', lat: pos.coords.latitude, lng: pos.coords.longitude }); },
        () => toast('Location permission was denied, so a route from you cannot be drawn.', 'error'),
        { timeout: 10000, enableHighAccuracy: true });
      return;
    }
    beginDispatch(type, w, nearest(type === 'fire' ? FIRE_STATIONS : HOSPITALS, w));
  }

  function beginDispatch(type, w, origin) {
    stopSim();
    clearRouteLayers();
    state.selectedId = w.id;
    state.dispatchActive = true;
    Object.assign(sim, { type, target: w, origin, route: null, fallback: false, arrived: false });
    if (state.view !== 'map') setView('map');
    if (sim.beacon) map.removeLayer(sim.beacon);
    sim.beacon = L.marker([w.lat, w.lng], { zIndexOffset: 3000, interactive: false,
      icon: L.divIcon({ className: '', html: `<div class="beacon"><span></span>${ico('flame', 14)}</div>`, iconSize: [32, 32], iconAnchor: [16, 16] }) }).addTo(map);
    setSide('dispatch');

    const url = `https://router.project-osrm.org/route/v1/driving/${origin.lng},${origin.lat};${w.lng},${w.lat}?overview=full&geometries=geojson&steps=true`;
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 6000);
    const token = sim.token = Symbol('dispatch');
    fetch(url, { signal: ctl.signal })
      .then(res => { clearTimeout(timer); if (!res.ok) throw new Error('router unavailable'); return res.json(); })
      .then(data => { if (!data.routes || !data.routes.length) throw new Error('no route'); return data.routes[0]; })
      .catch(() => { sim.fallback = true; return syntheticRoute(origin, w); })
      .then(route => { if (sim.token === token && state.dispatchActive) runRoute(route); });
  }

  // Straight-corridor estimate used when the public router cannot be reached.
  function syntheticRoute(origin, w) {
    const meters = Math.round(distM(origin.lat, origin.lng, w.lat, w.lng) * 1.35);
    const coords = [];
    for (let i = 0; i <= 12; i++) {
      const r = i / 12, mid = i > 0 && i < 12;
      coords.push([origin.lng + (w.lng - origin.lng) * r + (mid ? Math.cos(i * 1.6) * 0.0011 : 0),
        origin.lat + (w.lat - origin.lat) * r + (mid ? Math.sin(i * 1.6) * 0.0011 : 0)]);
    }
    const st = (type, modifier, i, name, share) => ({ maneuver: { type, modifier, location: coords[i] }, name, distance: meters * share });
    return { distance: meters, duration: Math.round(meters / 1000 / 30 * 3600), geometry: { coordinates: coords }, legs: [{ steps: [
      st('depart', null, 0, origin.name, 0.25), st('turn', 'right', 3, 'Grand Trunk Road', 0.35),
      st('turn', 'left', 7, 'Seelampur Main Road', 0.25), st('turn', 'sharp right', 10, 'the workshop lane', 0.15),
      st('arrive', null, 12, w.ent, 0)] }] };
  }

  function runRoute(route) {
    stopSim();
    clearRouteLayers();
    const coords = route.geometry.coordinates.map(c => [c[1], c[0]]);
    const dist = [0];
    for (let i = 1; i < coords.length; i++) dist.push(dist[i - 1] + distM(coords[i - 1][0], coords[i - 1][1], coords[i][0], coords[i][1]));
    Object.assign(sim, { route, coords, dist, total: dist[dist.length - 1] || 1, duration: Math.max(16, route.duration || 120),
      elapsed: 0, step: 0, running: true, paused: false, arrived: false });

    const cfg = DISPATCH[sim.type];
    const casing = L.polyline(coords, { color: '#fff', weight: 8, opacity: 0.95, interactive: false }).addTo(map);
    sim.todo = L.polyline(coords, { color: cfg.color, weight: 4.5, opacity: 0.95, interactive: false }).addTo(map);
    sim.done = L.polyline([coords[0]], { color: '#9AA3B2', weight: 4.5, opacity: 0.9, interactive: false }).addTo(map);
    const start = L.marker([sim.origin.lat, sim.origin.lng], { interactive: false,
      icon: L.divIcon({ className: '', html: '<div class="route-start"></div>', iconSize: [14, 14], iconAnchor: [7, 7] }) }).addTo(map);
    sim.vehicle = L.marker(coords[0], { zIndexOffset: 3500, interactive: false,
      icon: L.divIcon({ className: '', iconSize: [36, 36], iconAnchor: [18, 18],
        html: `<div class="vehicle" style="--c:${cfg.color}"><span class="vehicle-disc"><svg id="vehicle-arrow" width="16" height="16" viewBox="0 0 24 24" fill="#fff"><path d="M12 3l7 17-7-4-7 4z"/></svg></span><span class="vehicle-tag">${cfg.unit}</span></div>` }) }).addTo(map);
    sim.layers = [casing, sim.todo, sim.done, start, sim.vehicle];
    sim.bounds = casing.getBounds();
    // No animation: the follow camera starts panning on the next frame and would cut a zoom animation short.
    map.fitBounds(sim.bounds, { ...FIT, animate: false });

    if (state.side === 'dispatch') renderSide();
    sim.last = performance.now();
    sim.raf = requestAnimationFrame(tick);
  }

  function tick(ts) {
    if (!sim.running) return;
    if (sim.paused) { sim.last = ts; sim.raf = requestAnimationFrame(tick); return; }
    const dt = Math.min(0.25, (ts - sim.last) / 1000);
    sim.last = ts;
    // Compressed time: the whole route plays in about 32 s at 1×.
    sim.elapsed += dt * (sim.total / 32) * sim.speed;
    const progress = Math.min(1, sim.elapsed / sim.total);
    const cur = progress * sim.total;

    let i = 0;
    while (i < sim.dist.length - 1 && sim.dist[i + 1] < cur) i++;
    let lat, lng, brg = 0;
    if (i >= sim.coords.length - 1) {
      [lat, lng] = sim.coords[sim.coords.length - 1];
    } else {
      const p1 = sim.coords[i], p2 = sim.coords[i + 1], d1 = sim.dist[i], d2 = sim.dist[i + 1];
      const r = d2 > d1 ? (cur - d1) / (d2 - d1) : 0;
      lat = p1[0] + (p2[0] - p1[0]) * r;
      lng = p1[1] + (p2[1] - p1[1]) * r;
      brg = bearing(p1[0], p1[1], p2[0], p2[1]);
    }
    const speed = progress >= 1 ? 0 : Math.round(38 + Math.sin(sim.elapsed * 0.05) * 5);

    sim.vehicle.setLatLng([lat, lng]);
    const arrow = document.getElementById('vehicle-arrow');
    if (arrow) arrow.style.transform = `rotate(${brg}deg)`;
    sim.done.setLatLngs([...sim.coords.slice(0, i + 1), [lat, lng]]);
    sim.todo.setLatLngs([[lat, lng], ...sim.coords.slice(i + 1)]);
    if (sim.follow && progress < 1) map.panTo([lat, lng], { animate: false });

    updateTelemetry(progress, sim.total - cur, Math.round((1 - progress) * (sim.duration / sim.speed)), speed);
    updateGuidance(lat, lng);

    if (progress < 1) { sim.raf = requestAnimationFrame(tick); return; }
    sim.running = false;
    sim.arrived = true;
    updateTelemetry(1, 0, 0, 0);
    refreshSimControls();
  }

  const setText = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };

  function updateTelemetry(progress, metersLeft, secondsLeft, speed) {
    const m = Math.floor(secondsLeft / 60), s = secondsLeft % 60;
    setText('tele-eta', progress >= 1 ? 'On scene' : `${m}:${String(s).padStart(2, '0')}`);
    setText('tele-dist', metersLeft > 1000 ? `${(metersLeft / 1000).toFixed(1)} km` : `${Math.round(metersLeft)} m`);
    setText('tele-speed', `${speed} km/h`);
    const p = Math.round(progress * 100);
    const fill = document.getElementById('tele-fill');
    if (fill) fill.style.width = `${p}%`;
    setText('tele-pct', progress >= 1 ? 'Arrived' : `${p}% of route`);
    setText('dispatch-status', progress >= 1 ? DISPATCH[sim.type].done : DISPATCH[sim.type].going);
  }

  function updateGuidance(lat, lng) {
    const steps = sim.route && sim.route.legs && sim.route.legs[0] ? sim.route.legs[0].steps : [];
    if (!steps.length) return;
    let i = sim.step;
    while (i < steps.length - 1) {
      const loc = steps[i].maneuver.location;
      if (distM(lat, lng, loc[1], loc[0]) < 30) i++; else break;
    }
    sim.step = i;
    const info = maneuver(steps[i]), loc = steps[i].maneuver.location;
    const d = Math.round(distM(lat, lng, loc[1], loc[0]));
    const iconEl = document.getElementById('turn-icon');
    if (iconEl && iconEl.dataset.action !== info.action) { iconEl.dataset.action = info.action; iconEl.innerHTML = turnSvg(info.action, 24); }
    setText('turn-label', info.label);
    setText('turn-dist', info.action === 'arrive' && d < 25 ? 'now' : `in ${d} m`);
    setText('turn-street', info.street);
    $$('#route-steps li').forEach((el, n) => { el.classList.toggle('is-current', n === i); el.classList.toggle('is-done', n < i); });
  }

  function dispatchHtml() {
    const w = sim.target, cfg = DISPATCH[sim.type];
    return `
      <header class="side-head">
        <div class="side-headline">
          <p class="side-kicker live-status"><span class="pulse"></span><span id="dispatch-status">${sim.arrived ? cfg.done : cfg.going}</span></p>
          <h2>${esc(w.ent)}</h2>
          <p>${esc(w.loc)} · from ${esc(sim.origin.name)}</p>
        </div>
        <button type="button" class="icon-btn" data-act="dispatch-end" aria-label="End dispatch" title="End dispatch">${ico('x', 16)}</button>
      </header>
      <div class="side-body">
        <div class="seg">
          <button type="button" class="seg-btn${sim.type === 'fire' ? ' is-active' : ''}" data-act="dispatch" data-type="fire">Fire tender</button>
          <button type="button" class="seg-btn${sim.type === 'hospital' ? ' is-active' : ''}" data-act="dispatch" data-type="hospital">Ambulance</button>
        </div>

        <div class="turn">
          <div class="turn-icon" id="turn-icon">${turnSvg('straight', 24)}</div>
          <div><p class="turn-main"><span id="turn-label">${sim.route ? 'Depart' : 'Finding route…'}</span> <em id="turn-dist"></em></p>
            <p class="turn-street" id="turn-street">${sim.route ? '' : 'Contacting the routing service'}</p></div>
        </div>

        <dl class="tele">
          <div><dt>ETA</dt><dd id="tele-eta">–</dd></div>
          <div><dt>Remaining</dt><dd id="tele-dist">–</dd></div>
          <div><dt>Speed</dt><dd id="tele-speed">–</dd></div>
        </dl>
        <div>
          <div class="progress"><div class="progress-fill" id="tele-fill" style="width:${sim.arrived ? 100 : 0}%"></div></div>
          <p class="progress-lbl"><span>${esc(sim.origin.name)}</span><span id="tele-pct">${sim.arrived ? 'Arrived' : ''}</span></p>
        </div>

        <div class="simbar">
          <button type="button" class="btn" data-act="sim-toggle" id="sim-toggle"></button>
          <div class="seg seg-sm" id="sim-speeds">
            ${[1, 2, 4].map(s => `<button type="button" class="seg-btn" data-act="sim-speed" data-speed="${s}">${s}×</button>`).join('')}
          </div>
          <button type="button" class="btn" data-act="sim-follow" id="sim-follow" title="Keep the vehicle centred">Follow</button>
          <button type="button" class="btn" data-act="sim-fit" title="Show the whole route">Fit</button>
        </div>
        ${sim.fallback ? '<p class="notice">The routing service could not be reached. This is a straight-corridor estimate, not a street route.</p>' : ''}

        <section class="side-sec">
          <h3>Turn by turn <span id="route-count"></span></h3>
          <ol class="steps" id="route-steps"></ol>
        </section>
        <div class="actions">
          <button type="button" class="btn" data-act="dispatch-back">Unit details</button>
          <button type="button" class="btn" data-act="dispatch-end">End dispatch</button>
        </div>
      </div>`;
  }

  function renderRouteSteps() {
    const list = document.getElementById('route-steps');
    if (!list) return;
    const steps = sim.route && sim.route.legs && sim.route.legs[0] ? sim.route.legs[0].steps : [];
    setText('route-count', steps.length ? `${steps.length} steps` : '');
    list.innerHTML = steps.map((st, i) => {
      const info = maneuver(st), d = Math.round(st.distance || 0);
      return `<li data-act="step" data-step="${i}" class="${i === sim.step ? 'is-current' : i < sim.step ? 'is-done' : ''}">
        <span class="steps-icon">${turnSvg(info.action, 15)}</span>
        <span class="steps-text"><b>${info.label}</b> ${esc(info.street)}</span>
        <span class="steps-dist">${d ? `${d} m` : ''}</span></li>`;
    }).join('');
  }

  function refreshSimControls() {
    const toggle = document.getElementById('sim-toggle');
    if (!toggle) return;
    toggle.innerHTML = `${ico(sim.arrived || sim.paused ? 'play' : 'pause', 13)}<span>${sim.arrived ? 'Replay' : sim.paused ? 'Resume' : 'Pause'}</span>`;
    toggle.disabled = !sim.route;
    $$('#sim-speeds .seg-btn').forEach(b => b.classList.toggle('is-active', Number(b.dataset.speed) === sim.speed));
    const follow = document.getElementById('sim-follow');
    follow.classList.toggle('is-on', sim.follow);
    follow.setAttribute('aria-pressed', sim.follow);
  }

  function stopSim() {
    sim.running = false;
    if (sim.raf) cancelAnimationFrame(sim.raf);
    sim.raf = null;
  }
  function clearRouteLayers() {
    sim.layers.forEach(l => map && map.hasLayer(l) && map.removeLayer(l));
    sim.layers = [];
  }
  function endDispatch() {
    if (!state.dispatchActive) return;
    stopSim();
    clearRouteLayers();
    if (sim.beacon && map) map.removeLayer(sim.beacon);
    sim.beacon = null;
    sim.token = null;
    state.dispatchActive = false;
    if (state.side === 'dispatch') setSide(state.selectedId ? 'unit' : null);
    else renderSide();
  }

  // =========================================================
  // HOSE RELAY PLAN
  // =========================================================
  let hoseLayers = [];
  const STOREYS = { g_plus_3_or_more: 4, g_plus_2: 3, g_plus_1: 2, ground_only: 1 };

  function hosePlan(w) {
    const road = STAGING_ROADS.reduce((best, r) => (distM(w.lat, w.lng, r.lat, r.lng) < distM(w.lat, w.lng, best.lat, best.lng) ? r : best), STAGING_ROADS[0]);
    // Lanes wind: allow 1.35× the straight-line distance, with a 35 m minimum run.
    const meters = Math.max(35, Math.round(distM(w.lat, w.lng, road.lat, road.lng) * 1.35));
    const hoses = Math.ceil(meters / 30);                       // 30 m delivery lengths
    const friction = +(hoses * 0.35).toFixed(2);                 // ~0.35 bar per length at 500 L/min
    const storeys = STOREYS[w.cats.floors] || 1;
    const elevation = +((storeys - 1) * 0.35).toFixed(2);
    const pressure = +(3.5 + friction + elevation).toFixed(2);   // 3.5 bar at the branchpipe
    const obstruction = w.cats.obstruction === 'obstructed' ? 90 : w.cats.obstruction === 'partially_clear' ? 45 : 0;
    const narrow = w.cats.approach_road === 'narrow_under_2_5m' ? 30 : 0;
    const seconds = hoses * 45 + obstruction + narrow;           // 45 s per length for a two-person crew
    return { w, road, meters, hoses, friction, elevation, storeys, pressure, obstruction, narrow, seconds,
      time: `${Math.floor(seconds / 60)}m ${String(seconds % 60).padStart(2, '0')}s`, booster: meters > 150 || pressure > 6.5 };
  }

  function openHose(workshop) {
    const w = workshop || selected();
    if (!w) return toast('Select a workshop first.', 'error');
    state.selectedId = w.id;
    state.hosePlan = hosePlan(w);
    if (state.view !== 'map') setView('map');
    clearHose();
    drawHose(state.hosePlan);
    setSide('hose');
    requestAnimationFrame(fitHose);
  }
  function clearHose() {
    hoseLayers.forEach(l => map && map.hasLayer(l) && map.removeLayer(l));
    hoseLayers = [];
  }
  function fitHose() {
    if (hoseLayers.length) map.flyToBounds(L.featureGroup(hoseLayers).getBounds(), { ...FIT, maxZoom: 18, duration: 0.6 });
  }

  function drawHose(plan) {
    const a = [plan.road.lat, plan.road.lng], b = [plan.w.lat, plan.w.lng];
    const line = [a];
    // Schematic run: couplings evenly spaced, nudged alternately off the axis to suggest the winding lane.
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    const nx = -(b[1] - a[1]) / len, ny = (b[0] - a[0]) / len;
    for (let i = 1; i < plan.hoses; i++) {
      const r = i / plan.hoses, k = (i % 2 ? 1 : -1) * 0.00006;
      const p = [a[0] + (b[0] - a[0]) * r + nx * k, a[1] + (b[1] - a[1]) * r + ny * k];
      line.push(p);
      hoseLayers.push(L.marker(p, { zIndexOffset: 2600, icon: L.divIcon({ className: '', html: `<div class="coupling">${i}</div>`, iconSize: [18, 18], iconAnchor: [9, 9] }) })
        .bindTooltip(`Coupling ${i} · ${i * 30} m · ${(plan.pressure - i * 0.35).toFixed(2)} bar`, { className: 'unit-tip', direction: 'top', offset: [0, -8] }));
    }
    line.push(b);
    hoseLayers.unshift(
      L.polyline(line, { color: '#fff', weight: 8, opacity: 0.95, interactive: false }),
      L.polyline(line, { color: '#2a78d6', weight: 4, dashArray: '2 8', lineCap: 'round', opacity: 1, interactive: false }));
    hoseLayers.push(L.marker(a, { zIndexOffset: 2500, icon: L.divIcon({ className: '', html: `<div class="staging">${ico('truck', 14)}</div>`, iconSize: [26, 26], iconAnchor: [13, 13] }) })
      .bindTooltip(`Tender staging · ${esc(plan.road.name)}`, { className: 'unit-tip', direction: 'top', offset: [0, -12] }));
    hoseLayers.forEach(l => l.addTo(map));
  }

  function hoseHtml(p) {
    const w = p.w;
    const check = (level, title, text) => `<li class="check check-${level}"><span class="check-tag">${{ bad: 'Critical', warn: 'Caution', ok: 'OK' }[level]}</span><b>${title}</b><p>${text}</p></li>`;
    const penalties = [p.obstruction && `${p.obstruction} s blockage`, p.narrow && `${p.narrow} s narrow lane`].filter(Boolean).join(' + ');
    return `
      <header class="side-head">
        <div class="side-headline">
          <p class="side-kicker">Hose relay plan</p>
          <h2>${esc(w.ent)}</h2>
          <p>${esc(w.loc)} · approach lane ${esc(levelOf(w, 'approach_road')[0].toLowerCase())}</p>
        </div>
        <button type="button" class="icon-btn" data-act="hose-back" aria-label="Back to unit" title="Back to unit">${ico('x', 16)}</button>
      </header>
      <div class="side-body">
        <div class="stagecard">
          <p class="stagecard-kicker">Stage the tender at</p>
          <p class="stagecard-title">${esc(p.road.name)} <em>${p.road.widthM} m wide</em></p>
          <p class="stagecard-desc">${esc(p.road.desc)}.</p>
        </div>
        <dl class="kpis2">
          <div><dt>Hose run</dt><dd>${p.meters} m</dd><small>1.35 × straight-line distance</small></div>
          <div><dt>Lengths</dt><dd>${p.hoses} × 30 m</dd><small>${p.hoses * 30} m of delivery hose</small></div>
          <div><dt>Time to water</dt><dd>${p.time}</dd><small>${p.hoses} × 45 s${penalties ? ` + ${penalties}` : ''}</small></div>
          <div><dt>Pump pressure</dt><dd>${p.pressure} bar</dd><small>3.5 nozzle + ${p.friction} friction + ${p.elevation} lift</small></div>
        </dl>

        <section class="side-sec">
          <h3>Tactical checks</h3>
          <ul class="checks">
            ${p.narrow ? check('bad', 'No engine access', 'The lane is under 2.5 m. All water must be relayed by hand from the staging point.')
              : check('ok', 'Engine access', 'The approach road is motorable; a tender can reach the workshop frontage.')}
            ${p.booster ? check('bad', 'Booster pump required', `A ${p.meters} m relay at ${p.pressure} bar loses too much pressure. Place a portable booster near the ${Math.round(p.meters / 2)} m mark.`)
              : check('ok', 'Direct pumping', `At ${p.meters} m the tender pump holds 3.5 bar at the branchpipe without a booster.`)}
            ${p.obstruction === 90 ? check('bad', 'Lane obstructed', 'Scrap bales and stock block the run: expect kinks, puncture risk and about 90 s of delay.')
              : p.obstruction === 45 ? check('warn', 'Lane partly obstructed', 'Hose must be worked around stock in the lane, adding about 45 s.')
              : check('ok', 'Lane clear', 'A straight rollout is feasible at the standard 45 s per length.')}
            ${p.seconds > 300 ? check('bad', 'Slower than flashover', `Water arrives in ${p.time}. Textile and solvent fires typically flash over in 5 to 7 minutes, so evacuation comes first.`)
              : check('warn', 'Inside the flashover window', `Water in ${p.time} can beat a 5 to 7 minute flashover only if the turnout itself is fast.`)}
          </ul>
        </section>

        <section class="side-sec">
          <h3>Deployment sequence</h3>
          <ol class="sop">
            <li><b>Position the tender.</b> Stage on ${esc(p.road.name)}, chock wheels, engage the pump, set out warning markers.</li>
            <li><b>Roll out the relay.</b> Run ${p.hoses} lengths of 63 mm delivery hose through the lane in a two-crew relay.</li>
            <li><b>Set pressure.</b> Bring the pump to ${p.pressure} bar and bleed air at the branchpipe before entry.</li>
            <li><b>Attack.</b> Advance with the nozzle on a 30° fog cone to shield the crew at the entrance.</li>
          </ol>
        </section>

        <div class="actions">
          <button type="button" class="btn btn-danger" data-act="dispatch" data-type="fire">Dispatch fire tender</button>
          <button type="button" class="btn" data-act="hose-fit">Show relay</button>
          <button type="button" class="btn" data-act="hose-back">Unit details</button>
        </div>
      </div>`;
  }

  // =========================================================
  // PAGE BUILDING BLOCKS
  // =========================================================
  const PAGE_ICON = { Insights: 'chart', Workshops: 'table', Command: 'flame', Planning: 'layers', 'Field audit': 'clipboard', Governance: 'sliders' };
  const CARD_ICON = {
    'Risk levels': 'gauge', 'Score spread': 'chart', 'By locality': 'pin', 'Hard to escape, hard to reach': 'target', 'Risk by area': 'layers',
    'Most common problems': 'alert', 'Problems by locality': 'table', 'Past fires': 'flame', 'Hardest to reach': 'ban', 'Staging roads': 'truck',
    'First-due station': 'clock', 'Building separation': 'building', Storeys: 'layers', 'Approach roads': 'route', 'Master Plan 2041 directives': 'clipboard',
    'New audit': 'clipboard', 'Priority re-audit': 'alert', 'How the score is built': 'sliders', 'Effect on risk levels': 'peak'
  };
  const pagebar = (title, note, actions = '') =>
    `<header class="pagebar"><span class="page-ico">${ico(PAGE_ICON[title] || 'chart', 17)}</span><h2>${title}</h2><p>${note}</p><div class="pagebar-actions">${actions}</div></header>`;
  const kpi = (label, value, note, icon = 'chart', tone = 'ink') =>
    `<div class="kpi kpi-${tone}"><span class="kpi-ico">${ico(icon, 18)}</span><div class="kpi-text"><dt>${label}</dt><dd>${value}</dd><small>${note}</small></div></div>`;
  const btnIco = (act, icon, label, extra = '') => `<button type="button" class="btn" data-act="${act}"${extra}>${ico(icon, 14)}${label}</button>`;
  const card = (title, note, body, cls = '') =>
    `<article class="card ${cls}"><header class="card-head"><h3><i class="card-ico">${ico(CARD_ICON[title] || 'chart', 14)}</i>${title}</h3>${note ? `<span>${note}</span>` : ''}</header><div class="card-body">${body}</div></article>`;
  const emptyHtml = msg => `<div class="dash"><div class="empty"><p>${msg}</p><button type="button" class="btn" data-act="f-reset">Reset filters</button></div></div>`;

  // =========================================================
  // INSIGHTS
  // =========================================================
  function deficiencyRanking(list) {
    return FACTOR_KEYS.map(k => {
      const n = list.filter(w => score(w, k) >= FAIL_SCORE).length;
      return { k, n, share: list.length ? n / list.length : 0 };
    }).sort((a, b) => b.share - a.share);
  }

  function renderInsights() {
    const list = state.filtered, n = list.length;
    const el = $('#view-insights');
    if (!n) { el.innerHTML = emptyHtml('No workshops match the current filters.'); return; }

    const counts = tierCounts(list);
    const meanFri = mean(list.map(w => w.fri));
    const worst = [...list].sort((a, b) => b.fri - a.fri)[0];
    const locs = localities().map(l => {
      const ws = list.filter(w => w.loc === l);
      return { l, ws, n: ws.length, avg: mean(ws.map(w => w.fri)), counts: tierCounts(ws) };
    }).filter(x => x.n).sort((a, b) => b.avg - a.avg);

    // Score spread: 20 bands of 5 points.
    const bins = Array.from({ length: 20 }, () => 0);
    list.forEach(w => { bins[Math.min(19, Math.floor(w.fri * 20))]++; });
    const maxBin = Math.max(...bins);

    // Escape against fire-engine access: workshops grouped on a 5-point grid, one bubble per group.
    const cells = new Map();
    list.forEach(w => {
      const x = Math.round(w.access * 20) * 5, y = Math.round(w.egress * 20) * 5, key = `${x},${y}`;
      const c = cells.get(key) || { x, y, n: 0, sum: 0 };
      c.n++; c.sum += w.fri;
      cells.set(key, c);
    });
    const bubbles = [...cells.values()].sort((a, b) => b.n - a.n);
    const maxCell = bubbles[0].n;
    const both = list.filter(w => w.egress >= 0.5 && w.access >= 0.5).length;

    const areas = [...SUBS.map(s => ({ name: s.short, full: s.name, v: mean(list.map(w => w[s.key])), note: s.note })),
      { name: 'Social', full: 'Socio-economic vulnerability', v: mean(list.map(w => w.socio_vuln)), note: 'Recorded for context; not part of the score', muted: true }];

    const problems = deficiencyRanking(list);
    const heatCols = problems.slice(0, 5).map(d => d.k);
    const share = (ws, k) => (ws.length ? ws.filter(w => score(w, k) >= FAIL_SCORE).length / ws.length : 0);

    const fires = list.filter(w => w.incident);
    const fireRows = TIERS.map(t => ({ t, units: counts[t], fires: fires.filter(w => w.tier === t).length })).filter(x => x.units);
    const severeFires = fires.filter(w => w.tier === 'Severe').length;

    el.innerHTML = `<div class="dash">
      ${pagebar('Insights', n === DATA.length ? `All ${n} workshops` : `${n} of ${DATA.length} workshops (filtered)`,
        btnIco('export-csv', 'download', 'Export CSV') + btnIco('print', 'printer', 'Print'))}
      <dl class="kpis">
        ${kpi('Average risk score', `${pts(meanFri)}<i>/100</i>`, `${tierOf(meanFri)} risk on average`, 'gauge', 'hero')}
        ${kpi('Workshops', n, `${fires.length} have had a fire before`, 'building', 'indigo')}
        ${kpi('Severe risk', `${pct(counts.Severe, n)}%`, `${counts.Severe} workshops score 70 or more`, 'alert', 'red')}
        ${kpi('Highest score', `${pts(worst.fri)}<i>/100</i>`, `${esc(worst.ent)}, ${esc(worst.loc)}`, 'peak', 'amber')}
      </dl>
      <div class="dash-grid cols-4">
        ${card('Risk levels', 'Select a level to map it', `<div class="donutrow">
            <div class="donut donut-light">${donutSvg(counts, n, false)}<div class="donut-num"><b>${n}</b><span>workshops</span></div></div>
            <table class="mini">
              ${TIERS.map(t => `<tr class="is-link" data-act="insight-tier" data-tier="${t}" tabindex="0" data-tip="${t}: score ${TIER[t].range}">
                <td>${tierTag(t)}</td><td class="num">${counts[t]}</td><td class="num muted">${pct(counts[t], n)}%</td></tr>`).join('')}
            </table></div>`)}

        ${card('Score spread', 'Workshops per 5-point band', `<div class="hist" role="img" aria-label="Histogram of risk scores">
            ${bins.map((c, i) => `<span class="hist-col" data-tip="Score ${i * 5}–${i * 5 + 4}: ${c} workshop${c === 1 ? '' : 's'}">
              <i style="height:${maxBin ? (c / maxBin) * 100 : 0}%;background:${TIER[tierOf(i / 20 + 0.025)].color}"></i></span>`).join('')}
            <span class="hist-avg" style="left:${(meanFri * 100).toFixed(1)}%" data-tip="Average score ${pts(meanFri)}"><em>avg ${pts(meanFri)}</em></span>
          </div>
          <div class="hist-axis"><span style="left:0">0</span><span style="left:30%">30</span><span style="left:50%">50</span><span style="left:70%">70</span><span style="left:100%">100</span></div>`, 'card-hist')}

        ${card('By locality', 'Risk mix · average score', `<ul class="mixrows">
          ${locs.map(x => `<li data-act="insight-loc" data-loc="${esc(x.l)}" tabindex="0">
            <span class="mix-name">${esc(x.l)}<em>${x.n}</em></span>
            <span class="stack">${TIERS.filter(t => x.counts[t]).map(t => `<span style="flex:${x.counts[t]};background:${TIER[t].color}" data-tip="${esc(x.l)} · ${t}: ${x.counts[t]} of ${x.n}"></span>`).join('')}</span>
            <b>${pts(x.avg)}</b></li>`).join('')}</ul>`)}

        ${card('Hard to escape, hard to reach', `${both} are both`, `<div class="scatter" role="img" aria-label="Escape problems against fire-engine access problems">
            <span class="scatter-y">Harder to escape →</span><span class="scatter-x">Harder for fire engines to reach →</span>
            <div class="scatter-plot">
              <span class="scatter-zone"></span>
              ${bubbles.map(c => { const d = Math.round(7 + 21 * Math.sqrt(c.n / maxCell)), t = tierOf(c.sum / c.n);
                return `<i style="left:${c.x}%;bottom:${c.y}%;width:${d}px;height:${d}px;background:${TIER[t].color}" data-tip="${c.n} workshop${c.n === 1 ? '' : 's'} · escape ${c.y}, access ${c.x} · ${t} risk"></i>`; }).join('')}
            </div>
          </div>`, 'card-scatter')}

        ${card('Risk by area', 'Average out of 100 · higher is worse', `<div class="cols" role="img" aria-label="Average risk by area">
            ${areas.map(a => `<div class="col${a.muted ? ' is-muted' : ''}" data-tip="${a.full}: ${pts(a.v)} out of 100. ${a.note}">
              <b>${pts(a.v)}</b><span class="col-bar"><i style="height:${Math.round(a.v * 100)}%"></i></span><span class="col-name">${a.name}</span></div>`).join('')}
          </div>`, 'card-cols')}

        ${card('Most common problems', 'Select to list', `<ul class="rows">
          ${problems.slice(0, 8).map(d => row({ name: PROBLEM[d.k], value: d.share, text: `${Math.round(d.share * 100)}%`,
            act: 'insight-factor', attrs: `data-factor="${d.k}"`, tip: `${FACTORS[d.k].name}: ${d.n} of ${n} workshops` })).join('')}</ul>`)}

        ${card('Problems by locality', 'Share of workshops affected', `<table class="heat">
            <tr><th></th>${heatCols.map(k => `<th>${PROBLEM[k]}</th>`).join('')}</tr>
            ${locs.map(x => `<tr><td class="heat-name">${esc(x.l)}</td>${heatCols.map(k => { const s = share(x.ws, k);
              return `<td><span class="heat-cell${s > 0.55 ? ' is-dark' : ''}" style="--s:${Math.round(s * 100)}%" data-tip="${esc(x.l)} · ${PROBLEM[k]}: ${Math.round(s * 100)}% of ${x.n} workshops">${Math.round(s * 100)}</span></td>`; }).join('')}</tr>`).join('')}
          </table>`)}

        ${card('Past fires', 'Where fires have already happened', fires.length ? `<p class="callout"><b>${pct(severeFires, fires.length)}%</b><span>of the ${fires.length} past fires were in workshops now rated severe</span></p>
          <ul class="rows firerows">
            ${fireRows.map(x => row({ name: tierTag(x.t), value: x.fires / x.units, text: `${x.fires}/${x.units}`, color: TIER[x.t].color,
              tip: `${x.t} risk: ${x.fires} of ${x.units} workshops have had a fire` })).join('')}</ul>` : '<p class="muted">No past fires among these workshops.</p>')}
      </div>
    </div>`;
  }

  // =========================================================
  // REGISTRY
  // =========================================================
  const TIER_RANK = { Severe: 3, High: 2, Moderate: 1, Low: 0 };
  const COLUMNS = [
    ['id', 'ID'], ['ent', 'Workshop'], ['loc', 'Locality'], ['egress', 'Escape'], ['hazard', 'Hazards'],
    ['access', 'Access'], ['incident', 'Past fire'], ['fri', 'Risk score'], ['tier', 'Level']
  ];
  const NUMERIC = ['egress', 'hazard', 'access', 'fri'];

  function renderRegistry() {
    const { col, asc } = state.sort;
    const val = w => (col === 'tier' ? TIER_RANK[w.tier] : col === 'incident' ? (w.incident ? 1 : 0) : typeof w[col] === 'string' ? w[col].toLowerCase() : w[col]);
    const list = [...state.filtered].sort((a, b) => (val(a) < val(b) ? -1 : val(a) > val(b) ? 1 : 0) * (asc ? 1 : -1));
    const el = $('#view-registry');
    if (!list.length) { el.innerHTML = emptyHtml('No workshops match the current filters.'); return; }
    const scroller = $('.tablescroll', el), keep = scroller ? scroller.scrollTop : 0;

    el.innerHTML = `<div class="dash">
      ${pagebar('Workshops', `${list.length} of ${DATA.length} · select a row to open it on the map`,
        btnIco('export-csv', 'download', 'Export CSV') + btnIco('export-geojson', 'download', 'Export GeoJSON'))}
      <div class="card card-table">
        <div class="tablescroll">
          <table class="grid">
            <thead><tr>
              ${COLUMNS.map(([key, label]) => `<th class="c-${key}${NUMERIC.includes(key) ? ' num' : ''}" aria-sort="${col === key ? (asc ? 'ascending' : 'descending') : 'none'}">
                <button type="button" data-act="sort" data-col="${key}">${label}<span class="sortmark">${col === key ? (asc ? '↑' : '↓') : ''}</span></button></th>`).join('')}
            </tr></thead>
            <tbody>
              ${list.map(w => `<tr data-act="row" data-id="${esc(w.id)}" tabindex="0"${w.id === state.selectedId ? ' class="is-selected"' : ''}>
                <td class="c-id mono">${esc(w.id)}</td>
                <td class="c-ent"><span class="ent"><i class="ent-ico">${esc(w.ent.trim().charAt(0).toUpperCase())}</i><span><b>${esc(w.ent)}</b><span class="sub">${esc(w.work)}</span></span></span></td>
                <td class="c-loc">${esc(w.loc)}</td>
                ${SUBS.map(s => `<td class="c-${s.key} num"><span class="cellmeter" data-tip="${s.name}: ${grade(w[s.key])} (${pts(w[s.key])} out of 100, higher is worse)">${meter(w[s.key])}<span>${pts(w[s.key])}</span></span></td>`).join('')}
                <td class="c-incident">${w.incident ? `<span class="flag flag-fire">${ico('flame', 11)}Reported</span>` : '<span class="muted">–</span>'}</td>
                <td class="c-fri num"><b class="score score-${w.tier}">${pts(w.fri)}</b></td>
                <td class="c-tier">${tierTag(w.tier)}</td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>`;
    $('.tablescroll', el).scrollTop = keep;
  }

  // =========================================================
  // ROLE WORKSPACES
  // =========================================================
  function renderWorkspace() {
    $('#view-workspace').innerHTML = { fire: fireWorkspace, planner: plannerWorkspace, surveyor: surveyorWorkspace, admin: adminWorkspace }[state.role]();
    if (state.role === 'admin') updateWeightsUi();
  }

  const unitRow = (w, meta, actions) => `<li class="unitrow">
    <button type="button" class="unitrow-main" data-act="open-unit" data-id="${esc(w.id)}">
      <span class="unitrow-text"><b>${esc(w.ent)}</b><em>${meta}</em></span></button>
    <b class="score score-${w.tier}">${pts(w.fri)}</b>${actions}</li>`;

  function fireWorkspace() {
    const hard = DATA.filter(w => w.tier === 'Severe' && w.cats.approach_road === 'narrow_under_2_5m' && w.cats.exits === '1 exit')
      .sort((a, b) => b.fri - a.fri);
    const plans = DATA.map(hosePlan);
    const stationLoad = FIRE_STATIONS.map(s => {
      const ws = DATA.filter(w => nearest(FIRE_STATIONS, w) === s);
      return { s, n: ws.length, km: mean(ws.map(w => distM(w.lat, w.lng, s.lat, s.lng))) / 1000 };
    });
    const sel = selected();
    return `<div class="dash">
      ${pagebar('Command', 'Dispatch, hose relays and tender staging',
        `<button type="button" class="btn btn-danger" data-act="dispatch" data-type="fire"${sel ? '' : ' disabled'}>${ico('flame', 15)}${sel ? `Dispatch to ${esc(sel.ent)}` : 'Select a workshop to dispatch'}</button>`)}
      <dl class="kpis">
        ${kpi('No engine access', DATA.filter(w => w.cats.approach_road === 'narrow_under_2_5m').length, 'workshops on lanes under 2.5 m', 'ban', 'hero')}
        ${kpi('Booster pump needed', plans.filter(p => p.booster).length, 'relays over 150 m or 6.5 bar', 'droplet', 'indigo')}
        ${kpi('Water after 5 min', plans.filter(p => p.seconds > 300).length, 'relays slower than flashover', 'clock', 'red')}
        ${kpi('Median hose run', `${[...plans].sort((a, b) => a.meters - b.meters)[Math.floor(plans.length / 2)].meters} m`, 'from the nearest staging road', 'ruler', 'amber')}
      </dl>
      <div class="dash-grid cols-2 one-row">
        ${card('Hardest to reach', `${hard.length} severe units, single exit, no engine access`, `<ul class="unitlist">
          ${hard.map(w => { const p = hosePlan(w); return unitRow(w, `${esc(w.loc)} · ${p.meters} m relay · water in ${p.time}`,
            `<button type="button" class="btn btn-sm" data-act="hose" data-id="${esc(w.id)}">Hose plan</button>
             <button type="button" class="btn btn-sm btn-danger" data-act="dispatch" data-type="fire" data-id="${esc(w.id)}">Dispatch</button>`); }).join('')}
        </ul>`, 'card-flush')}
        <div class="stackcol">
          ${card('Staging roads', 'Select to view on the map', `<ul class="unitlist">
            ${STAGING_ROADS.map(r => `<li class="unitrow"><button type="button" class="unitrow-main" data-act="fly" data-lat="${r.lat}" data-lng="${r.lng}">
              <span class="unitrow-ico">${ico('truck', 15)}</span><span class="unitrow-text"><b>${esc(r.name)}</b><em>${plans.filter(p => p.road === r).length} workshops relay from here</em></span></button>
              <span class="unitrow-val">${r.widthM} m</span></li>`).join('')}
          </ul>`, 'card-flush card-grow')}
          ${card('First-due station', 'Units for which each station is closest', `<ul class="rows">
            ${stationLoad.map(x => row({ name: esc(x.s.name), sub: x.n ? `${x.km.toFixed(1)} km avg` : '', value: x.n / DATA.length, text: x.n })).join('')}</ul>`)}
        </div>
      </div>
    </div>`;
  }

  function plannerWorkspace() {
    const rows = key => Object.keys(SCORING_MAP[key]).map(code => ({ label: (FACTORS[key].levels[code] || [code])[0],
      n: DATA.filter(w => w.cats[key] === code).length, s: SCORING_MAP[key][code] })).filter(x => x.n)
      .map(x => row({ name: esc(x.label), sub: `${x.n} units`, value: x.n / DATA.length, text: `${pct(x.n, DATA.length)}%`, color: sevColor(x.s) })).join('');
    return `<div class="dash">
      ${pagebar('Planning', 'Building stock, setbacks and Master Plan directives',
        btnIco('quick-map', 'map', 'Map shared-wall units', ' data-quick="shared-wall"') + btnIco('quick-map', 'map', 'Map G+3 units', ' data-quick="tall"')
        + btnIco('context-map', 'layers', 'Land-use layer', ' data-layer="landuse"'))}
      <div class="dash-grid cols-2">
        ${card('Building separation', 'Shared walls let fire travel between units', `<ul class="rows">${rows('building_gap')}</ul>`)}
        ${card('Storeys', 'Taller buildings mean longer escape through smoke', `<ul class="rows">${rows('floors')}</ul>`)}
        ${card('Approach roads', 'Whether a fire engine can reach the door', `<ul class="rows">${rows('approach_road')}</ul>`)}
        ${card('Master Plan 2041 directives', '', `<div class="seg">
            ${Object.keys(POLICIES).map(l => `<button type="button" class="seg-btn${state.policyLoc === l ? ' is-active' : ''}" data-act="policy" data-loc="${esc(l)}">${esc(l)}</button>`).join('')}
          </div>
          <ol class="directives">${(POLICIES[state.policyLoc] || []).map(([t, d]) => `<li><b>${t}</b><p>${d}</p></li>`).join('')}</ol>`)}
      </div>
    </div>`;
  }

  function surveyorWorkspace() {
    const queue = DATA.filter(w => w.tier === 'Severe' && w.incident && !state.verified.has(w.id) && !w.verified).sort((a, b) => b.fri - a.fri);
    const select = key => `<label class="field"><span class="field-label">${FACTORS[key].name}</span>
      <select class="input" name="${key}">${Object.keys(SCORING_MAP[key]).map(code =>
        `<option value="${esc(code)}">${esc((FACTORS[key].levels[code] || [code])[0])}</option>`).join('')}</select></label>`;
    const c = map ? map.getCenter() : { lat: 28.6665, lng: 77.2720 };
    return `<div class="dash">
      ${pagebar('Field audit', 'Record new audits and verify surveyed units')}
      <dl class="kpis">
        ${kpi('Units audited', DATA.length, `across ${localities().length} localities`, 'clipboard', 'hero')}
        ${kpi('Verified this session', state.verified.size, 'marked from the unit panel', 'shield', 'teal')}
        ${kpi('Priority re-audit', queue.length, 'severe units with a past fire', 'alert', 'red')}
        ${kpi('Added this session', DATA.filter(w => w.added).length, 'not yet in the master dataset', 'pin', 'indigo')}
      </dl>
      <div class="dash-grid cols-2 one-row">
        ${card('New audit', 'Scored with the current model weights', `<form id="audit-form" class="form">
            <div class="form-grid">
              <label class="field span-2"><span class="field-label">Enterprise name</span><input class="input" name="ent" required></label>
              <label class="field"><span class="field-label">Locality</span><select class="input" name="loc">${localities().map(l => `<option>${esc(l)}</option>`).join('')}</select></label>
              <label class="field"><span class="field-label">Activity</span><input class="input" name="work"></label>
              <label class="field"><span class="field-label">Latitude</span><input class="input mono" name="lat" type="number" step="0.000001" required value="${c.lat.toFixed(6)}"></label>
              <label class="field"><span class="field-label">Longitude</span><input class="input mono" name="lng" type="number" step="0.000001" required value="${c.lng.toFixed(6)}"></label>
            </div>
            <p class="form-hint">Coordinates default to the map centre. <button type="button" class="link" data-act="audit-gps">Use my GPS position</button></p>
            ${SUBS.map(s => `<fieldset><legend>${s.name}</legend><div class="form-grid">${FACTOR_KEYS.filter(k => FACTORS[k].sub === s.key).map(select).join('')}</div></fieldset>`).join('')}
            <div class="form-actions"><button type="submit" class="btn btn-primary">Save and score</button></div>
          </form>`)}
        ${card('Priority re-audit', 'Severe units that have already had a fire', queue.length ? `<ul class="unitlist">${queue.map(w => unitRow(w, `${esc(w.loc)} · ${esc(w.work)}`,
          `<button type="button" class="btn btn-sm" data-act="verify" data-id="${esc(w.id)}">Verify</button>`)).join('')}</ul>` : '<p class="muted">Queue cleared for this session.</p>', 'card-flush')}
      </div>
    </div>`;
  }

  function adminWorkspace() {
    return `<div class="dash">
      ${pagebar('Governance', 'Model weights and data export',
        btnIco('export-csv', 'download', 'Export CSV', ' data-all="1"') + btnIco('export-geojson', 'download', 'Export GeoJSON') + btnIco('print', 'printer', 'Print'))}
      <div class="dash-grid cols-2 one-row">
        ${card('How the score is built', 'Shares always add up to 100%; every workshop is re-scored as you drag', `
          <p class="formula">Risk score = a weighted mix of escape routes, fire hazards and fire-engine access</p>
          <div class="weights-bar" id="weights-bar"></div>
          <div class="weights">
            ${SUBS.map(s => `<label class="weight"><span class="weight-head"><b>${s.name}</b><em>${s.note}</em><output id="w-out-${s.key}"></output></span>
              <input type="range" min="5" max="80" step="1" id="w-${s.key}" data-weight="${s.key}" value="${Math.round(state.weights[s.key] * 100)}"></label>`).join('')}
          </div>
          <div class="form-actions form-actions-start"><button type="button" class="btn" data-act="weights-reset">Reset to baseline (45 / 25 / 30)</button></div>`)}
        ${card('Effect on risk levels', 'Current mix against the survey baseline', '<div id="weights-effect"></div>')}
      </div>
    </div>`;
  }

  const baselineTier = w => tierOf(BASE_WEIGHTS.egress * w.egress + BASE_WEIGHTS.hazard * w.hazard + BASE_WEIGHTS.access * w.access);

  function updateWeightsUi() {
    const bar = $('#weights-bar');
    if (!bar) return;
    const shades = ['#16203A', '#3345B8', '#6C7BFF'];
    bar.innerHTML = SUBS.map((s, i) => `<span style="flex:${state.weights[s.key]};background:${shades[i]}" data-tip="${s.name}: ${Math.round(state.weights[s.key] * 100)}%"><em>${s.short} ${Math.round(state.weights[s.key] * 100)}%</em></span>`).join('');
    SUBS.forEach(s => { $(`#w-out-${s.key}`).textContent = `${Math.round(state.weights[s.key] * 100)}%`; });
    const moved = DATA.filter(w => w.tier !== baselineTier(w)).length;
    $('#weights-effect').innerHTML = `<table class="mini">
      <tr><th>Tier</th><th class="num">Now</th><th class="num">Baseline</th><th class="num">Change</th></tr>
      ${TIERS.map(t => { const now = DATA.filter(w => w.tier === t).length, base = DATA.filter(w => baselineTier(w) === t).length, d = now - base;
        return `<tr><td>${tierTag(t)}</td><td class="num">${now}</td><td class="num muted">${base}</td><td class="num">${d === 0 ? '–' : (d > 0 ? '+' : '−') + Math.abs(d)}</td></tr>`; }).join('')}
      </table>
      <p class="card-note">${moved ? `${moved} workshop${moved === 1 ? '' : 's'} changed tier.` : 'No workshop has changed tier.'} Average score ${pts(mean(DATA.map(w => w.fri)))} out of 100.</p>`;
  }

  function applyWeights() {
    const raw = Object.fromEntries(SUBS.map(s => [s.key, Number($(`#w-${s.key}`).value)]));
    const sum = SUBS.reduce((a, s) => a + raw[s.key], 0) || 1;
    SUBS.forEach(s => { state.weights[s.key] = raw[s.key] / sum; });
    rescore();
  }
  function rescore() {
    DATA.forEach(w => {
      w.fri = +(state.weights.egress * w.egress + state.weights.hazard * w.hazard + state.weights.access * w.access).toFixed(4);
      w.tier = tierOf(w.fri);
    });
    applyFilters();
    updateWeightsUi();
    if (state.side === 'unit') renderSide();
  }

  function saveAudit(form) {
    const fd = new FormData(form);
    const cats = Object.fromEntries(FACTOR_KEYS.map(k => [k, fd.get(k)]));
    const sub = key => +mean(FACTOR_KEYS.filter(k => FACTORS[k].sub === key).map(k => SCORING_MAP[k][cats[k]])).toFixed(4);
    const egress = sub('egress'), hazard = sub('hazard'), access = sub('access');
    const fri = +(state.weights.egress * egress + state.weights.hazard * hazard + state.weights.access * access).toFixed(4);
    const loc = fd.get('loc');
    const next = Math.max(...DATA.map(w => parseInt(String(w.id).replace(/\D/g, ''), 10) || 0)) + 1;
    const w = { id: `E${String(next).padStart(3, '0')}`, loc, area: `${loc} (field audit)`, ent: String(fd.get('ent')).trim(),
      work: String(fd.get('work')).trim() || 'Unclassified workshop', incident: false, lat: Number(fd.get('lat')), lng: Number(fd.get('lng')),
      cats, fri, egress, hazard, access, tier: tierOf(fri), socio_vuln: 0, verified: true, added: true };
    if (!w.ent || !isFinite(w.lat) || !isFinite(w.lng)) return toast('Enter a name and valid coordinates.', 'error');
    DATA.unshift(w);
    resetFilters();
    toast(`${w.ent} recorded: risk score ${pts(w.fri)} out of 100, ${w.tier.toLowerCase()} risk.`, 'success');
    selectUnit(w.id, { fly: true });
  }

  // =========================================================
  // EXPORTS
  // =========================================================
  const stamp = () => new Date().toISOString().slice(0, 10);
  function exportCsv(list) {
    const q = v => `"${String(v == null ? '' : v).replace(/"/g, '""')}"`;
    const head = ['EnterpriseID', 'Enterprise', 'Locality', 'Activity', 'FireRiskIndex', 'RiskTier', 'SUB_Egress', 'SUB_Hazard', 'SUB_Access', 'PastIncident', 'Latitude', 'Longitude', ...FACTOR_KEYS];
    const rows = list.map(w => [q(w.id), q(w.ent), q(w.loc), q(w.work), w.fri, w.tier, w.egress, w.hazard, w.access, w.incident ? 1 : 0, w.lat, w.lng, ...FACTOR_KEYS.map(k => q(w.cats[k]))].join(','));
    download(`seelampur_fire_risk_${stamp()}.csv`, [head.join(','), ...rows].join('\n'), 'text/csv;charset=utf-8;');
    toast(`Exported ${list.length} workshops as CSV.`, 'success');
  }
  function exportGeoJson(list) {
    const features = list.map(w => ({ type: 'Feature', geometry: { type: 'Point', coordinates: [w.lng, w.lat] },
      properties: { EnterpriseID: w.id, Enterprise: w.ent, Locality: w.loc, Area: w.area, Activity: w.work, FireRiskIndex: w.fri, RiskTier: w.tier,
        SUB_Egress: w.egress, SUB_Hazard: w.hazard, SUB_Access: w.access, PastIncident: w.incident ? 1 : 0, ...w.cats } }));
    download(`seelampur_fire_risk_${stamp()}.geojson`, JSON.stringify({ type: 'FeatureCollection', features }, null, 2), 'application/geo+json');
    toast(`Exported ${list.length} workshops as GeoJSON.`, 'success');
  }

  // =========================================================
  // EVENTS
  // =========================================================
  const ACTIONS = {
    'quick-login': el => { const r = ROLES[el.dataset.role]; signIn({ email: r.email, role: el.dataset.role, name: r.name, title: r.title, initials: r.initials }); },
    logout: () => signOut(),
    view: (el, e) => { e.preventDefault(); setView(el.dataset.view); },

    menu: el => { state.openMenu = state.openMenu === el.dataset.menu ? null : el.dataset.menu; renderMenus(); },
    role: el => { state.openMenu = null; setRole(el.dataset.role); },
    'f-loc': el => { state.filters.loc = el.dataset.loc; state.openMenu = null; applyFilters(); fitTo(state.filtered.length ? state.filtered : DATA); },
    'f-tier': el => { const t = el.dataset.tier, s = state.filters.tiers; s.has(t) ? s.delete(t) : s.add(t); applyFilters(); },
    'f-factor-clear': () => { state.filters.factor = null; applyFilters(); },
    'f-reset': () => { resetFilters(); if (state.view === 'map') fitTo(DATA); },
    'f-remove': el => {
      const k = el.dataset.key, f = state.filters;
      if (k === 'q') { f.q = ''; $('#search-input').value = ''; }
      else if (k === 'loc') f.loc = 'ALL';
      else if (k === 'tier') f.tiers = new Set(TIERS);
      else if (k === 'factor') f.factor = null;
      else if (k.startsWith('quick:')) f.quick.delete(k.slice(6));
      applyFilters();
    },

    basemap: el => setBasemap(el.dataset.base),
    'zoom-in': () => map.zoomIn(),
    'zoom-out': () => map.zoomOut(),
    fit: () => fitTo(state.filtered.length ? state.filtered : DATA),
    locate: () => locateUser(),

    'side-close': () => setSide(null),
    'unit-tab': el => {
      state.unitTab = el.dataset.tab;
      const top = $('#side .side-body').scrollTop;
      renderSide();
      $('#side .side-body').scrollTop = top;
    },
    'zoom-unit': () => { const w = selected(); if (w) flyToUnit(w, 19); },
    'open-unit': el => selectUnit(el.dataset.id, { fly: true }),
    row: el => selectUnit(el.dataset.id, { fly: true }),
    verify: el => {
      const w = byId(el.dataset.id);
      if (!w) return;
      state.verified.add(w.id);
      toast(`${w.ent} marked as verified.`, 'success');
      if (state.side === 'unit') renderSide();
      if (state.view === 'workspace') renderWorkspace();
    },

    dispatch: el => startDispatch(el.dataset.type, el.dataset.id ? byId(el.dataset.id) : null),
    'dispatch-end': () => endDispatch(),
    'dispatch-back': () => setSide('unit'),
    'dispatch-view': () => { state.selectedId = sim.target.id; setSide('dispatch'); },
    'sim-toggle': () => { if (sim.arrived) runRoute(sim.route); else sim.paused = !sim.paused; refreshSimControls(); },
    'sim-speed': el => { sim.speed = Number(el.dataset.speed); refreshSimControls(); },
    'sim-follow': () => { sim.follow = !sim.follow; refreshSimControls(); },
    'sim-fit': () => { if (sim.bounds) { sim.follow = false; refreshSimControls(); map.fitBounds(sim.bounds, FIT); } },
    step: el => { const st = sim.route.legs[0].steps[Number(el.dataset.step)]; if (st) { sim.follow = false; refreshSimControls(); map.flyTo([st.maneuver.location[1], st.maneuver.location[0]], 18, { duration: 0.6 }); } },

    hose: el => openHose(el.dataset.id ? byId(el.dataset.id) : null),
    'hose-back': () => setSide('unit'),
    'hose-fit': () => fitHose(),

    'insight-tier': el => { state.filters.tiers = new Set([el.dataset.tier]); applyFilters(); setView('map'); fitTo(state.filtered); },
    'insight-loc': el => { state.filters.loc = el.dataset.loc; applyFilters(); setView('map'); fitTo(state.filtered); },
    'insight-factor': el => { state.filters.factor = el.dataset.factor; applyFilters(); setView('registry'); },
    sort: el => {
      const col = el.dataset.col;
      state.sort = state.sort.col === col ? { col, asc: !state.sort.asc } : { col, asc: ['id', 'ent', 'work', 'loc'].includes(col) };
      renderRegistry();
    },

    fly: el => { setView('map'); requestAnimationFrame(() => map.flyTo([Number(el.dataset.lat), Number(el.dataset.lng)], 17, { duration: 0.6 })); },
    'quick-map': el => { resetFilters(); state.filters.quick.add(el.dataset.quick); applyFilters(); setView('map'); fitTo(state.filtered); },
    'context-map': el => { setView('map'); if (!state.context.has(el.dataset.layer)) toggleContext(el.dataset.layer); },
    policy: el => { state.policyLoc = el.dataset.loc; renderWorkspace(); },
    'weights-reset': () => { state.weights = { ...BASE_WEIGHTS }; SUBS.forEach(s => { $(`#w-${s.key}`).value = Math.round(BASE_WEIGHTS[s.key] * 100); }); rescore(); },
    'audit-gps': () => {
      if (!navigator.geolocation) return toast('This browser does not support geolocation.', 'error');
      navigator.geolocation.getCurrentPosition(pos => {
        const form = $('#audit-form');
        form.lat.value = pos.coords.latitude.toFixed(6);
        form.lng.value = pos.coords.longitude.toFixed(6);
        toast('Coordinates set from your GPS position.', 'success');
      }, () => toast('Location permission was denied.', 'error'), { timeout: 10000, enableHighAccuracy: true });
    },

    'export-csv': el => exportCsv(el.dataset.all ? DATA : state.filtered),
    'export-geojson': () => exportGeoJson(state.view === 'registry' ? state.filtered : DATA),
    print: () => { setView('insights'); setTimeout(() => window.print(), 80); }
  };

  // Form controls that change state on `change` rather than `click`.
  const CHANGES = {
    quick: el => { const s = state.filters.quick; el.checked ? s.add(el.value) : s.delete(el.value); applyFilters(); },
    layer: el => { state.layers[el.value] = el.checked; syncOverlays(); },
    context: el => toggleContext(el.value)
  };

  function bindEvents() {
    document.addEventListener('click', e => {
      if (state.openMenu && !e.target.closest('.dd')) { state.openMenu = null; renderMenus(); }
      const el = e.target.closest('[data-act]');
      if (!el || el.disabled) return;
      const fn = ACTIONS[el.dataset.act];
      if (fn) fn(el, e);
    });
    document.addEventListener('change', e => {
      const el = e.target;
      const fn = CHANGES[el.dataset.change];
      if (fn) fn(el);
    });
    document.addEventListener('keydown', e => {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName);
      if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('tr[data-act], li[data-act]')) { e.preventDefault(); e.target.click(); }
      if (e.key === '/' && !typing && !$('#app').hidden) { e.preventDefault(); $('#search-input').focus(); }
      if (e.key === 'Escape') {
        if (state.openMenu) { state.openMenu = null; return renderMenus(); }
        if (typing) return e.target.blur();
        if (state.side === 'dispatch') endDispatch(); else if (state.side) setSide(state.side === 'hose' ? 'unit' : null);
      }
    });

    $('#search-input').addEventListener('input', debounce(e => { state.filters.q = e.target.value.trim().toLowerCase(); applyFilters(); }, 140));
    $('#login-form').addEventListener('submit', handleLoginSubmit);
    document.addEventListener('submit', e => { if (e.target.id === 'audit-form') { e.preventDefault(); saveAudit(e.target); } });
    document.addEventListener('input', e => { if (e.target.dataset.weight) applyWeights(); });
    window.addEventListener('resize', debounce(() => map && map.invalidateSize(), 120));
    window.addEventListener('hashchange', () => {
      const v = location.hash.slice(1);
      if (state.user && v !== state.view && VIEWS.includes(v)) setView(v);
    });

    // Shared hover tooltip for chart marks.
    const tip = $('#tip');
    document.addEventListener('mousemove', e => {
      const el = e.target.closest ? e.target.closest('[data-tip]') : null;
      if (!el) { tip.hidden = true; return; }
      tip.textContent = el.dataset.tip;
      tip.hidden = false;
      const r = tip.getBoundingClientRect();
      tip.style.left = `${Math.min(window.innerWidth - r.width - 8, Math.max(8, e.clientX - r.width / 2))}px`;
      tip.style.top = `${Math.max(8, e.clientY - r.height - 14)}px`;
    });
  }

  // =========================================================
  // BOOT
  // =========================================================
  function boot() {
    // The map library comes from a CDN; say so plainly if it did not arrive instead of failing silently.
    if (!window.L || !L.heatLayer) {
      document.body.insertAdjacentHTML('afterbegin', '<p class="fatal">The map library could not be loaded. Check your connection and reload the page.</p>');
      return;
    }
    document.title = `${APP_NAME} — Seelampur fire risk atlas`;
    $$('[data-app-name]').forEach(el => { el.textContent = APP_NAME; });
    hydrateIcons(document);
    renderLogin();
    bindEvents();
    const session = readSession();
    if (session && session.name) signIn(session);
    else $('#login-screen').hidden = false;
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
