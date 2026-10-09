# inspect_all_data.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    gj = json.load(f)

print(f"Total features: {len(gj['features'])}")

tiers = {}
localities = {}
for i, feat in enumerate(gj['features']):
    p = feat.get('properties', {})
    geom = feat.get('geometry')
    tier = p.get('RiskTier', 'Unknown')
    tiers[tier] = tiers.get(tier, 0) + 1
    loc = p.get('Locality', 'Unknown')
    localities[loc] = localities.get(loc, 0) + 1

print("\nTiers count in survey_points.geojson:")
for t, c in sorted(tiers.items()):
    print(f"  {t}: {c}")

print("\nLocalities count in survey_points.geojson:")
for loc, c in sorted(localities.items()):
    print(f"  {loc}: {c}")

sample = gj['features'][0]['properties']
print("\nSample properties of E001:")
for k, v in sample.items():
    print(f"  {k}: {v}")
