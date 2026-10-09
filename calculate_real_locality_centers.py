# calculate_real_locality_centers.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

# Group by normalized locality
groups = {
    'Seelampur': [],
    'Gandhi Nagar': [],
    'Shanti Mohalla': [],
    'Subhash Nagar': []
}

other = []

for feat in survey['features']:
    p = feat.get('properties', {})
    geom = feat.get('geometry')
    if not geom or not geom.get('coordinates'):
        continue
    lng, lat = geom['coordinates']
    loc = p.get('Locality', '')
    
    if 'Shanti Mohalla' in loc:
        groups['Shanti Mohalla'].append((lat, lng))
    elif 'Gandhi Nagar' in loc:
        groups['Gandhi Nagar'].append((lat, lng))
    elif 'Subhash Nagar' in loc:
        groups['Subhash Nagar'].append((lat, lng))
    else: # Default Seelampur and other clusters
        groups['Seelampur'].append((lat, lng))

print("=== REAL SURVEY LOCALITY CENTROIDS & BOUNDS ===")
for loc, pts in groups.items():
    if pts:
        lats = [pt[0] for pt in pts]
        lngs = [pt[1] for pt in pts]
        mean_lat = sum(lats) / len(lats)
        mean_lng = sum(lngs) / len(lngs)
        print(f"'{loc}': count={len(pts)}")
        print(f"  Center: [{mean_lat:.6f}, {mean_lng:.6f}]")
        print(f"  Lat range: [{min(lats):.6f}, {max(lats):.6f}]")
        print(f"  Lng range: [{min(lngs):.6f}, {max(lngs):.6f}]")
        print()
