# inspect_factor_values.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

factors = [
    'Number of exit routes',
    'Obstruction-free evacuation',
    'Functional emergency exits',
    'Staircase width',
    'Workspace size (sq ft)',
    'Number of floors',
    'Natural light availability',
    'Windows / natural openings',
    'Corridor geometry',
    'Waste burning nearby',
    'Visible dust / emissions',
    'Gap to adjacent building',
    'Distance to fire station',
    'Fire-brigade response time',
    'Approach road for fire truck',
    'PastIncident'
]

for factor in factors:
    vals = set()
    for feat in survey['features']:
        p = feat.get('properties', {})
        vals.add(p.get(factor))
    print(f"{factor}: {sorted([str(v) for v in vals])}")
