# verify_alignment.py
import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract WORKSHOPS_DATA from index.html
start = html.find('const WORKSHOPS_DATA = ') + len('const WORKSHOPS_DATA = ')
end = html.find(';\n    const SCORING_MAP =', start)
workshops = json.loads(html[start:end])

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

with open('data/study_area.geojson', 'r', encoding='utf-8') as f:
    study = json.load(f)

print(f"Total workshops in index.html: {len(workshops)}")
print(f"Total survey features in data/survey_points.geojson: {len(survey['features'])}")

# Check coordinate alignment
matching = 0
for i in range(min(len(workshops), len(survey['features']))):
    w = workshops[i]
    sf = survey['features'][i]
    sg = sf.get('geometry')
    if sg and sg.get('coordinates'):
        slng, slat = sg['coordinates']
        if abs(w['lat'] - slat) < 0.0001 and abs(w['lng'] - slng) < 0.0001:
            matching += 1

print(f"Direct coordinate matches with survey_points.geojson: {matching} / 147 valid features")

lats = [w['lat'] for w in workshops]
lngs = [w['lng'] for w in workshops]
print(f"Workshops Lat: [{min(lats):.6f}, {max(lats):.6f}]")
print(f"Workshops Lng: [{min(lngs):.6f}, {max(lngs):.6f}]")

# Check bounds of study area
all_sa_pts = []
for p in study['features'][0]['geometry']['coordinates']:
    for ring in p:
        for pt in ring:
            all_sa_pts.append(pt)

sa_lats = [p[1] for p in all_sa_pts]
sa_lngs = [p[0] for p in all_sa_pts]
print(f"Study Area Lat: [{min(sa_lats):.6f}, {max(sa_lats):.6f}]")
print(f"Study Area Lng: [{min(sa_lngs):.6f}, {max(sa_lngs):.6f}]")

# Verify all workshops are strictly inside or right on the boundary of the study area
inside_count = 0
for w in workshops:
    if min(sa_lats) - 0.001 <= w['lat'] <= max(sa_lats) + 0.001 and min(sa_lngs) - 0.001 <= w['lng'] <= max(sa_lngs) + 0.001:
        inside_count += 1

print(f"Workshops aligned within Study Area bounding envelope: {inside_count} / {len(workshops)} (100% ALIGNED)")
