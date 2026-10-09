# check_points_on_map.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

with open('data/study_area.geojson', 'r', encoding='utf-8') as f:
    study = json.load(f)

print(f"Total survey points: {len(survey['features'])}")

points = []
for i, f in enumerate(survey['features']):
    p = f.get('properties', {})
    geom = f.get('geometry')
    if geom and geom.get('coordinates'):
        lng, lat = geom['coordinates']
        points.append({
            'idx': i,
            'id': p.get('EnterpriseID', f'E{i+1:03d}'),
            'name': p.get('Enterprise', 'Unknown Workshop'),
            'loc': p.get('Locality', 'Seelampur'),
            'fri': p.get('FireRiskIndex', 0.5),
            'tier': p.get('RiskTier', 'Moderate'),
            'lat': lat,
            'lng': lng
        })
    else:
        print(f"Missing coords for index {i}: {p}")

print(f"Valid points with GPS: {len(points)}")

lats = [pt['lat'] for pt in points]
lngs = [pt['lng'] for pt in points]

print(f"Bounding box:")
print(f"  Lat: {min(lats):.6f} to {max(lats):.6f} (center: {(min(lats)+max(lats))/2:.6f})")
print(f"  Lng: {min(lngs):.6f} to {max(lngs):.6f} (center: {(min(lngs)+max(lngs))/2:.6f})")

# Check localities in points
loc_counts = {}
for pt in points:
    loc_counts[pt['loc']] = loc_counts.get(pt['loc'], 0) + 1

print("\nLocality counts:")
for l, c in sorted(loc_counts.items(), key=lambda x: -x[1]):
    print(f"  {l}: {c}")
