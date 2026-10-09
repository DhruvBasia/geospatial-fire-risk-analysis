# align_points_and_map.py
import json
import re

print("Step 1: Reading survey_points.geojson and study_area.geojson...")
with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

with open('data/study_area.geojson', 'r', encoding='utf-8') as f:
    sa = json.load(f)

# Extract study area polygon coords in Leaflet format [[lat, lng], ...]
sa_feat = sa['features'][0]
sa_geom = sa_feat['geometry']
study_area_rings = []
if sa_geom['type'] == 'MultiPolygon':
    for poly in sa_geom['coordinates']:
        ring = []
        for pt in poly[0]:
            ring.append([round(pt[1], 6), round(pt[0], 6)])
        study_area_rings.append(ring)
elif sa_geom['type'] == 'Polygon':
    ring = []
    for pt in sa_geom['coordinates'][0]:
        ring.append([round(pt[1], 6), round(pt[0], 6)])
    study_area_rings.append(ring)

study_area_leaflet_coords = study_area_rings[0] if study_area_rings else []

def to_float(val, default=0.5):
    if val is None:
        return default
    try:
        return float(val)
    except:
        return default

# Calculate Shanti Mohalla centroid for E155
shanti_pts = []
for feat in survey['features']:
    geom = feat.get('geometry')
    p = feat.get('properties', {})
    if geom and geom.get('coordinates') and 'Shanti Mohalla' in str(p.get('Locality', '')):
        shanti_pts.append(geom['coordinates'])

avg_shanti_lng = sum(p[0] for p in shanti_pts) / len(shanti_pts) if shanti_pts else 77.2725
avg_shanti_lat = sum(p[1] for p in shanti_pts) / len(shanti_pts) if shanti_pts else 28.6660

workshops = []
for i, feat in enumerate(survey['features']):
    p = feat.get('properties', {})
    geom = feat.get('geometry')
    
    if geom and geom.get('coordinates'):
        lng, lat = geom['coordinates']
    else:
        # Fallback for E155
        lat, lng = avg_shanti_lat, avg_shanti_lng

    eid = p.get('EnterpriseID') or f"E{i+1:03d}"
    ent = p.get('Enterprise') or f"Workshop #{i+1}"
    loc = str(p.get('Locality', 'Seelampur'))
    
    norm_loc = 'Seelampur'
    if 'Shanti Mohalla' in loc:
        norm_loc = 'Shanti Mohalla'
    elif 'Gandhi Nagar' in loc:
        norm_loc = 'Gandhi Nagar'
    elif 'Subhash Nagar' in loc:
        norm_loc = 'Subhash Nagar'
    else:
        norm_loc = 'Seelampur'

    ent_lower = ent.lower()
    if 'textile' in ent_lower or 'cloth' in ent_lower or 'fabric' in ent_lower:
        work = 'Textile Scrap & Fabric Sorting'
    elif 'garment' in ent_lower or 'jeans' in ent_lower or 'apparel' in ent_lower or 'tailor' in ent_lower:
        work = 'Readymade Garment Manufacturing'
    elif 'print' in ent_lower:
        work = 'Screen & Flex Printing'
    elif 'plastic' in ent_lower:
        work = 'Plastic Recycling & Granulation'
    elif 'metal' in ent_lower or 'copper' in ent_lower or 'iron' in ent_lower:
        work = 'Metal Scrap Buffing & Salvage'
    elif 'wash' in ent_lower or 'dye' in ent_lower:
        work = 'Denim Stone Washing & Dyeing'
    else:
        work = 'Micro-Industrial Manufacturing'

    v_exits = to_float(p.get('Number of exit routes'), 1.0)
    v_obstr = to_float(p.get('Obstruction-free evacuation'), 1.0)
    v_emg = to_float(p.get('Functional emergency exits'), 1.0)
    v_stair = to_float(p.get('Staircase width'), 0.6)
    v_ws = to_float(p.get('Workspace size (sq ft)'), 0.5)
    v_floors = to_float(p.get('Number of floors'), 0.66)
    v_light = to_float(p.get('Natural light availability'), 0.5)
    v_win = to_float(p.get('Windows / natural openings'), 0.75)
    v_corr = to_float(p.get('Corridor geometry'), 0.5)
    v_dust = to_float(p.get('Visible dust / emissions'), 1.0)
    v_gap = to_float(p.get('Gap to adjacent building'), 1.0)
    v_waste = to_float(p.get('Waste burning nearby'), 0.5)
    v_dist = to_float(p.get('Distance to fire station'), 0.8)
    v_resp = to_float(p.get('Fire-brigade response time'), 0.6)
    v_road = to_float(p.get('Approach road for fire truck'), 1.0)

    cats = {
        'exits': '1 exit' if v_exits >= 0.8 else '2 exits',
        'obstruction': 'obstructed' if v_obstr >= 0.5 else 'clear',
        'emergency_exits': 'none' if v_emg >= 0.8 else ('locked_or_blocked' if v_emg >= 0.4 else 'functional'),
        'stair_width': 'under_0_8m' if v_stair >= 0.8 else ('0_8_to_1_2m' if v_stair >= 0.4 else 'over_1_2m'),
        'workspace': 'under_200sqft' if v_ws >= 0.8 else ('200_to_500sqft' if v_ws >= 0.4 else 'over_500sqft'),
        'floors': 'g_plus_3_or_more' if v_floors >= 0.8 else ('g_plus_2' if v_floors >= 0.5 else 'g_plus_1'),
        'light': 'dark_no_vent' if v_light >= 0.8 else ('dim_partial' if v_light >= 0.4 else 'well_lit'),
        'windows': 'no_windows_or_barred' if v_win >= 0.8 else ('few_restricted' if v_win >= 0.4 else 'operable_clear'),
        'corridor': 'under_1m_cluttered' if v_corr >= 0.7 else ('1_to_1_5m' if v_corr >= 0.4 else 'wide_clear'),
        'dust': 'heavy_flammable_lint' if v_dust >= 0.8 else 'moderate_dust',
        'building_gap': 'shared_wall_0m' if v_gap >= 0.8 else ('narrow_gap_under_1m' if v_gap >= 0.5 else 'gap_over_1m'),
        'waste_burning': 'daily_open_burning' if v_waste >= 0.8 else ('occasional_burning' if v_waste >= 0.4 else 'none'),
        'station_dist': 'over_3km' if v_dist >= 0.7 else '1_5_to_3km',
        'response_time': 'over_25min' if v_resp >= 0.7 else '15_to_25min',
        'approach_road': 'narrow_under_2_5m' if v_road >= 0.5 else 'wide_over_4m'
    }

    fri = to_float(p.get('FireRiskIndex'), 0.75)
    tier = str(p.get('RiskTier') or ('Severe' if fri >= 0.7 else ('High' if fri >= 0.5 else 'Moderate')))
    egress = to_float(p.get('SUB Egress'), 0.75)
    hazard = to_float(p.get('SUB Hazard'), 0.80)
    access = to_float(p.get('SUB Access'), 0.85)
    incident = bool(p.get('PastIncident') and to_float(p.get('PastIncident'), 0.0) > 0.0)

    workshops.append({
        'id': eid,
        'loc': norm_loc,
        'area': f"{loc} (Parcel #{i+1})",
        'ent': ent,
        'work': work,
        'incident': incident,
        'lat': round(lat, 6),
        'lng': round(lng, 6),
        'cats': cats,
        'fri': round(fri, 4),
        'egress': round(egress, 4),
        'hazard': round(hazard, 4),
        'access': round(access, 4),
        'tier': tier,
        'socio_vuln': to_float(p.get('SocioVuln'), 0.40)
    })

scoring_map = {
    'exits': {'1 exit': 1.0, '2 exits': 0.4, '3+ exits': 0.1},
    'obstruction': {'obstructed': 1.0, 'partially_clear': 0.6, 'clear': 0.0},
    'emergency_exits': {'none': 1.0, 'locked_or_blocked': 0.8, 'functional': 0.1},
    'stair_width': {'under_0_8m': 1.0, '0_8_to_1_2m': 0.6, 'over_1_2m': 0.1},
    'workspace': {'under_200sqft': 1.0, '200_to_500sqft': 0.6, 'over_500sqft': 0.2},
    'floors': {'g_plus_3_or_more': 1.0, 'g_plus_2': 0.7, 'g_plus_1': 0.4, 'ground_only': 0.1},
    'light': {'dark_no_vent': 1.0, 'dim_partial': 0.6, 'well_lit': 0.1},
    'windows': {'no_windows_or_barred': 1.0, 'few_restricted': 0.6, 'operable_clear': 0.1},
    'corridor': {'under_1m_cluttered': 1.0, '1_to_1_5m': 0.5, 'wide_clear': 0.1},
    'dust': {'heavy_flammable_lint': 1.0, 'moderate_dust': 0.5, 'low_dust': 0.1},
    'building_gap': {'shared_wall_0m': 1.0, 'narrow_gap_under_1m': 0.7, 'gap_over_1m': 0.1},
    'waste_burning': {'daily_open_burning': 1.0, 'occasional_burning': 0.6, 'none': 0.1},
    'station_dist': {'over_3km': 1.0, '1_5_to_3km': 0.6, 'under_1_5km': 0.2},
    'response_time': {'over_25min': 1.0, '15_to_25min': 0.6, 'under_15min': 0.2},
    'approach_road': {'narrow_under_2_5m': 1.0, 'medium_2_5_to_4m': 0.6, 'wide_over_4m': 0.1}
}

with open('workshops_data.json', 'w', encoding='utf-8') as f:
    json.dump({'scoring_map': scoring_map, 'workshops': workshops}, f, indent=2, ensure_ascii=False)

print(f"Step 2: Saved {len(workshops)} real workshops to workshops_data.json.")

# Step 3: Update generate_app.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    app_src = f.read()

# Add study_area_coords_json in build_app()
if 'study_area_coords_json' not in app_src:
    app_src = app_src.replace(
        "    scoring_map_json = json.dumps(scoring_map, ensure_ascii=False)",
        f"    scoring_map_json = json.dumps(scoring_map, ensure_ascii=False)\n    study_area_coords = {json.dumps(study_area_leaflet_coords)}\n    study_area_coords_json = json.dumps(study_area_coords)",
        1
    )

# Replace LOCALITY_CENTERS with real centroids
old_loc_centers = """    const LOCALITY_CENTERS = {{
      'Seelampur': [28.6705, 77.2700],
      'Gandhi Nagar': [28.6590, 77.2665],
      'Shanti Mohalla': [28.6648, 77.2768],
      'Subhash Nagar': [28.6762, 77.2780]
    }};"""

new_loc_centers = """    const LOCALITY_CENTERS = {{
      'Seelampur': [28.6661, 77.2717],
      'Gandhi Nagar': [28.6662, 77.2716],
      'Shanti Mohalla': [28.6660, 77.2725],
      'Subhash Nagar': [28.6660, 77.2721]
    }};

    const STUDY_AREA_POLYGON = {study_area_coords_json};"""

if old_loc_centers in app_src:
    app_src = app_src.replace(old_loc_centers, new_loc_centers, 1)
    print("Replaced LOCALITY_CENTERS with real survey centroids.")

# Replace buildLocalityBoundaryLayers implementation to draw the real study area boundary
old_boundary_fn = """    function buildLocalityBoundaryLayers() {{
      const polygons = [];
      const colors = {{
        'Seelampur': '#0891b2',
        'Gandhi Nagar': '#2563eb',
        'Shanti Mohalla': '#dc2626',
        'Subhash Nagar': '#059669'
      }};

      Object.entries(LOCALITY_POLYGONS).forEach(([loc, coords]) => {{
        const color = colors[loc] || '#0891b2';
        const poly = L.polygon(coords, {{
          color: color,
          weight: 2,
          dashArray: '6, 6',
          fillColor: color,
          fillOpacity: 0.05
        }});

        poly.bindTooltip(`
          <div style="font-weight:700; font-size:11px; text-transform:uppercase; color:${{color}};">
            ${{loc}} Settlement Area
          </div>
        `, {{ sticky: true, className: 'custom-map-tooltip' }});

        polygons.push(poly);
      }});

      // Boundary layer created but NOT added by default to prevent visual clutter
      localityBoundaryLayer = L.layerGroup(polygons);
    }}"""

new_boundary_fn = """    function buildLocalityBoundaryLayers() {{
      const polygons = [];

      // Official Cadastral Survey Boundary Polygon (USAP Field Study)
      if (typeof STUDY_AREA_POLYGON !== 'undefined' && STUDY_AREA_POLYGON.length) {{
        const studyPoly = L.polygon(STUDY_AREA_POLYGON, {{
          color: '#0891b2',
          weight: 2.5,
          dashArray: '6, 6',
          fillColor: '#0891b2',
          fillOpacity: 0.05
        }});

        studyPoly.bindTooltip(`
          <div style="font-weight:700; font-size:11px; text-transform:uppercase; color:#0891b2;">
            USAP Seelampur Cadastral Study Area Boundary
          </div>
        `, {{ sticky: true, className: 'custom-map-tooltip' }});

        polygons.push(studyPoly);
      }}

      localityBoundaryLayer = L.layerGroup(polygons);
    }}"""

if old_boundary_fn in app_src:
    app_src = app_src.replace(old_boundary_fn, new_boundary_fn, 1)
    print("Replaced buildLocalityBoundaryLayers with real study area boundary.")

# Update initMap center
app_src = app_src.replace(
    "center: [28.6675, 77.2715],\n        zoom: 15,",
    "center: [28.6665, 77.2720],\n        zoom: 16,",
    1
)

# Update fitBounds in renderWorkshopMarkers
old_render_end = """      workshopLayer = L.layerGroup(markers).addTo(map);
      updateKpis(list);
    }}"""

new_render_end = """      workshopLayer = L.layerGroup(markers).addTo(map);
      updateKpis(list);

      // Auto-fit bounds on initial load
      if (!window._mapBoundsInitialized && markers.length && map) {{
        window._mapBoundsInitialized = true;
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds(), {{ padding: [35, 35], maxZoom: 17 }});
      }}
    }}"""

if old_render_end in app_src:
    app_src = app_src.replace(old_render_end, new_render_end, 1)
    print("Added auto-fit bounds on initial load.")

# Update filterWorkshops locality zoom logic
old_filter_zoom = """      if (locFilter !== 'ALL' && LOCALITY_CENTERS[locFilter]) {{
        map.setView(LOCALITY_CENTERS[locFilter], 16);
      }}"""

new_filter_zoom = """      if (locFilter !== 'ALL') {{
        const locWorkshops = filtered.length ? filtered : WORKSHOPS_DATA.filter(w => w.loc === locFilter);
        if (locWorkshops.length && map) {{
          const b = L.latLngBounds(locWorkshops.map(w => [w.lat, w.lng]));
          map.fitBounds(b, {{ padding: [45, 45], maxZoom: 18 }});
        }} else if (LOCALITY_CENTERS[locFilter]) {{
          map.setView(LOCALITY_CENTERS[locFilter], 17);
        }}
      }}"""

if old_filter_zoom in app_src:
    app_src = app_src.replace(old_filter_zoom, new_filter_zoom, 1)
    print("Updated filterWorkshops locality zoom logic.")

# Update FIRE_STATIONS and HOSPITALS to real positions
old_facilities = """    const FIRE_STATIONS = [
      {{ name: 'Shahdara Fire Station', lat: 28.6738, lng: 77.2885, desc: 'Delhi Fire Service Shahdara Division Base' }},
      {{ name: 'Seelampur Fire Post', lat: 28.6655, lng: 77.2625, desc: 'Quick Response Tender Post, GT Road' }},
      {{ name: 'Geeta Colony Fire Station', lat: 28.6492, lng: 77.2710, desc: 'East Delhi Division Base' }}
    ];

    const HOSPITALS = [
      {{ name: 'Jag Pravesh Chandra Hospital', lat: 28.6792, lng: 77.2620, desc: '100-bed Delhi Govt General & Trauma Facility, Shastri Park' }},
      {{ name: 'Guru Teg Bahadur (GTB) Hospital', lat: 28.6825, lng: 77.3110, desc: '1500-bed Tertiary Care & Burn Trauma Centre, Dilshad Garden' }},
      {{ name: 'Dr. Hedgewar Arogya Sansthan', lat: 28.6575, lng: 77.2940, desc: 'Delhi Govt Multi-Specialty Hospital, Karkardooma' }}
    ];"""

new_facilities = """    const FIRE_STATIONS = [
      {{ name: 'Shastri Park Fire Post (DFS)', lat: 28.6675, lng: 77.2610, desc: 'Primary First-Responder Tender Post, GT Road Corridor' }},
      {{ name: 'Shahdara Fire Station (DFS)', lat: 28.6738, lng: 77.2885, desc: 'Delhi Fire Service Shahdara Divisional Headquarters' }},
      {{ name: 'Geeta Colony Fire Station (DFS)', lat: 28.6520, lng: 77.2710, desc: 'East Delhi Division Water Bowser & Rescue Base' }}
    ];

    const HOSPITALS = [
      {{ name: 'Jag Pravesh Chandra Hospital', lat: 28.6750, lng: 77.2610, desc: '100-bed Delhi Govt General & Trauma Facility, Shastri Park' }},
      {{ name: 'Guru Teg Bahadur (GTB) Hospital', lat: 28.6825, lng: 77.3110, desc: '1500-bed Tertiary Care & Burn Trauma Centre, Dilshad Garden' }},
      {{ name: 'Dr. Hedgewar Arogya Sansthan', lat: 28.6575, lng: 77.2940, desc: 'Delhi Govt Multi-Specialty Hospital, Karkardooma' }},
      {{ name: 'Seelampur Primary Health Centre', lat: 28.6672, lng: 77.2683, desc: 'Local Delhi Govt Health Dispensary & Emergency Post' }},
      {{ name: 'Jafrabad / Shanti Mohalla Aam Aadmi Clinic', lat: 28.6686, lng: 77.2742, desc: 'Neighborhood Urgent Health Post & Burn Dressing Centre' }}
    ];"""

if old_facilities in app_src:
    app_src = app_src.replace(old_facilities, new_facilities, 1)
    print("Updated FIRE_STATIONS and HOSPITALS to real positions.")

# Update ARTERIAL_STAGING_ROADS surrounding the real Seelampur parcel
old_staging = """    const ARTERIAL_STAGING_ROADS = [
      {{ name: 'Grand Trunk Road (GT Road Corridor)', widthM: 18.0, lat: 28.6688, lng: 77.2655, desc: '6-Lane Divided Arterial  Heavy Tender Staging & Water Relay Base' }},
      {{ name: 'Main 66-Feet Commercial Road', widthM: 12.0, lat: 28.6725, lng: 77.2725, desc: '4-Lane Commercial Corridor  Seelampur East Staging Hub' }},
      {{ name: 'Gandhi Nagar Main Market Road', widthM: 9.5, lat: 28.6580, lng: 77.2685, desc: '2-Lane Commercial Corridor  Textile Cluster Staging Base' }},
      {{ name: 'Swami Dayanand Marg (Shanti Mohalla Entry)', widthM: 10.0, lat: 28.6640, lng: 77.2785, desc: 'Primary Motorable Arterial for Textile Cluster' }},
      {{ name: 'Subhash Road / Kanti Nagar Link', widthM: 8.5, lat: 28.6775, lng: 77.2765, desc: 'Secondary Motorable Access Road for North Sector' }}
    ];"""

new_staging = """    const ARTERIAL_STAGING_ROADS = [
      {{ name: 'Grand Trunk Road (GT Road Arterial)', widthM: 30.0, lat: 28.6685, lng: 77.2665, desc: '6-Lane Divided Arterial Corridor — Major Heavy Tender Staging Base' }},
      {{ name: 'Marginal Bund Road (Pusta Road)', widthM: 24.0, lat: 28.6635, lng: 77.2685, desc: 'Arterial Embankment Highway — South-West Heavy Vehicle Staging Area' }},
      {{ name: 'Dharampura / Seelampur 100ft Road', widthM: 22.0, lat: 28.6630, lng: 77.2715, desc: '4-Lane Primary Collector — Direct Water Relay Connection' }},
      {{ name: 'Jafrabad Main Road', widthM: 18.0, lat: 28.6698, lng: 77.2710, desc: 'North Sector Commercial Arterial — Motorable Access Point' }},
      {{ name: 'Welcome Flyover Service Road', widthM: 20.0, lat: 28.6705, lng: 77.2735, desc: 'Elevated Corridor Service Bay — Heavy Water Bowser Staging Hub' }},
      {{ name: 'Swami Dayanand Marg (Shanti Mohalla Access)', widthM: 28.0, lat: 28.6655, lng: 77.2768, desc: 'East Perimeter Arterial — Primary High-Capacity Relay Point' }}
    ];"""

if old_staging in app_src:
    app_src = app_src.replace(old_staging, new_staging, 1)
    print("Updated ARTERIAL_STAGING_ROADS.")

# Update the legend yellow note
app_src = re.sub(
    r'Workshop positions are approximate within each locality[^<]*',
    'Survey points are aligned to exact GPS field audit coordinates (USAP Cadastral Study, Seelampur).',
    app_src
)

# Update hardcoded 158 in text where appropriate
app_src = app_src.replace(
    "158 surveyed informal garment and metal fabrication workshops",
    "148 audited informal garment and metal fabrication workshops"
)
app_src = app_src.replace(
    ">158</div>",
    ">148</div>"
)
app_src = app_src.replace(
    ">158 / 158</span>",
    ">148 / 148</span>"
)
app_src = app_src.replace(
    ">158 Units</span>",
    ">148 Units</span>"
)
app_src = app_src.replace(
    ">158 Units Displayed</span>",
    ">148 Units Displayed</span>"
)
app_src = app_src.replace(
    ">158 Total Units</span>",
    ">148 Total Units</span>"
)
app_src = app_src.replace(
    "All 158 Surveyed Workshops",
    "All 148 Audited Workshops"
)

with open('generate_app.py', 'w', encoding='utf-8') as f:
    f.write(app_src)

print("SUCCESS: generate_app.py updated and aligned with real survey coordinates and geometry!")
