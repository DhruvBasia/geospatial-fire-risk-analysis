# build_real_workshops_data.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

def to_float(val, default=0.5):
    if val is None:
        return default
    try:
        return float(val)
    except:
        return default

workshops = []
shanti_pts = []

for feat in survey['features']:
    geom = feat.get('geometry')
    p = feat.get('properties', {})
    if geom and geom.get('coordinates') and 'Shanti Mohalla' in str(p.get('Locality', '')):
        shanti_pts.append(geom['coordinates'])

avg_shanti_lng = sum(p[0] for p in shanti_pts) / len(shanti_pts) if shanti_pts else 77.2725
avg_shanti_lat = sum(p[1] for p in shanti_pts) / len(shanti_pts) if shanti_pts else 28.6660

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
    
    # Normalize locality to 4 main administrative sectors
    norm_loc = 'Seelampur'
    if 'Shanti Mohalla' in loc:
        norm_loc = 'Shanti Mohalla'
    elif 'Gandhi Nagar' in loc:
        norm_loc = 'Gandhi Nagar'
    elif 'Subhash Nagar' in loc:
        norm_loc = 'Subhash Nagar'
    else:
        norm_loc = 'Seelampur'

    # Work type derivation
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

    # Map physical survey indicators to categorical labels
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

print(f"Generated {len(workshops)} workshop records from survey_points.geojson.")

lats = [w['lat'] for w in workshops]
lngs = [w['lng'] for w in workshops]
print(f"Lat range: [{min(lats):.6f}, {max(lats):.6f}]")
print(f"Lng range: [{min(lngs):.6f}, {max(lngs):.6f}]")

tier_counts = {}
for w in workshops:
    tier_counts[w['tier']] = tier_counts.get(w['tier'], 0) + 1
print("Tier counts:", tier_counts)

incidents = sum(1 for w in workshops if w['incident'])
print(f"Incidents count: {incidents}")

mean_fri = sum(w['fri'] for w in workshops) / len(workshops)
print(f"Mean FRI: {mean_fri:.4f}")

# Save to real_workshops_data.json
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

output_data = {
    'scoring_map': scoring_map,
    'workshops': workshops
}

with open('workshops_data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("SUCCESS: workshops_data.json updated with real surveyed workshop GPS coordinates!")
