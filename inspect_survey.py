# inspect_survey.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

valid = []
invalid = []

for i, feat in enumerate(survey['features']):
    geom = feat.get('geometry')
    props = feat.get('properties', {})
    if geom and geom.get('coordinates'):
        valid.append((i, props, geom['coordinates']))
    else:
        invalid.append((i, props))

print(f'Total features: {len(survey["features"])}')
print(f'Valid geometry: {len(valid)}')
print(f'Invalid geometry: {len(invalid)}')

if invalid:
    print('Invalid features sample:')
    for idx, p in invalid[:5]:
        print(f'  Index {idx}: ID={p.get("EnterpriseID")}, Enterprise={p.get("Enterprise")}, Locality={p.get("Locality")}')

if valid:
    lats = [c[1] for _, _, c in valid]
    lngs = [c[0] for _, _, c in valid]
    print(f'Lat min={min(lats):.6f}, max={max(lats):.6f}, mean={sum(lats)/len(lats):.6f}')
    print(f'Lng min={min(lngs):.6f}, max={max(lngs):.6f}, mean={sum(lngs)/len(lngs):.6f}')

    # Group by locality
    by_loc = {}
    for _, p, c in valid:
        loc = p.get('Locality', 'Unknown')
        by_loc.setdefault(loc, []).append((p, c))
    
    print('\nLocalities breakdown in valid points:')
    for loc, items in by_loc.items():
        sub_lats = [c[1] for _, c in items]
        sub_lngs = [c[0] for _, c in items]
        print(f'  {loc}: {len(items)} points, lat [{min(sub_lats):.4f}, {max(sub_lats):.4f}], lng [{min(sub_lngs):.4f}, {max(sub_lngs):.4f}]')
