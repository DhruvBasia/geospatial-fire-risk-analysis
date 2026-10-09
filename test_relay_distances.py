# test_relay_distances.py
import json
import math

with open('workshops_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

staging_roads = [
    {'name': 'GT Road Arterial', 'lat': 28.6685, 'lng': 77.2665},
    {'name': 'Marginal Bund Road', 'lat': 28.6635, 'lng': 77.2685},
    {'name': 'Dharampura 100ft Road', 'lat': 28.6630, 'lng': 77.2715},
    {'name': 'Jafrabad Main Road', 'lat': 28.6698, 'lng': 77.2710},
    {'name': 'Welcome Flyover Service Road', 'lat': 28.6705, 'lng': 77.2735},
    {'name': 'Swami Dayanand Marg', 'lat': 28.6655, 'lng': 77.2768}
]

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

dists = []
for w in d['workshops']:
    min_d = float('inf')
    best_road = None
    for r in staging_roads:
        d_m = haversine_m(w['lat'], w['lng'], r['lat'], r['lng']) * 1.35 # sinuosity
        if d_m < min_d:
            min_d = d_m
            best_road = r['name']
    dists.append(min_d)

print(f"Hose relay distance range: {min(dists):.1f}m to {max(dists):.1f}m")
print(f"Average relay distance: {sum(dists)/len(dists):.1f}m")
print(f"Hoses required range: {math.ceil(min(dists)/30)} to {math.ceil(max(dists)/30)} hoses (30m lengths)")
