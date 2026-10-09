# inspect_layers.py
import json, os

files = ['com_res.geojson', 'ind_res.geojson', 'ind_com.geojson', 'residential.geojson', 'g_plus_1.geojson', 'g_plus_2.geojson', 'g_plus_3.geojson', 'g_plus_4.geojson', 'drain.geojson']
for name in files:
    path = os.path.join('data', name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        feats = len(d.get('features', []))
        kb = os.path.getsize(path)/1024
        print(f"{name}: {feats} features, {kb:.1f} KB")
