# get_study_area_coords.py
import json

with open('data/study_area.geojson', 'r', encoding='utf-8') as f:
    sa = json.load(f)

feat = sa['features'][0]
geom = feat['geometry']
print('Geom type:', geom['type'])

# Extract coordinates in Leaflet format [[lat, lng], [lat, lng], ...]
if geom['type'] == 'MultiPolygon':
    poly_coords = []
    for poly in geom['coordinates']:
        ring_coords = []
        for pt in poly[0]:
            ring_coords.append([round(pt[1], 6), round(pt[0], 6)])
        poly_coords.append(ring_coords)
    print(f"MultiPolygon with {len(poly_coords)} rings, ring 0 has {len(poly_coords[0])} vertices")
elif geom['type'] == 'Polygon':
    poly_coords = []
    for pt in geom['coordinates'][0]:
        poly_coords.append([round(pt[1], 6), round(pt[0], 6)])
    print(f"Polygon with {len(poly_coords)} vertices")

with open('study_area_leaflet.json', 'w', encoding='utf-8') as f:
    json.dump(poly_coords, f)

print("Saved study_area_leaflet.json!")
