# compare_schema.py
import json

with open('data/survey_points.geojson', 'r', encoding='utf-8') as f:
    survey = json.load(f)

with open('workshops_data.json', 'r', encoding='utf-8') as f:
    app_data = json.load(f)

print(f"Survey features count: {len(survey['features'])}")
print(f"App workshops count: {len(app_data['workshops'])}")

s0 = survey['features'][0]['properties']
w0 = app_data['workshops'][0]

print("\n--- SURVEY POINT 0 PROPERTIES ---")
for k, v in s0.items():
    print(f"  {k}: {v}")

print("\n--- APP WORKSHOP 0 PROPERTIES ---")
for k, v in w0.items():
    if k != 'cats':
        print(f"  {k}: {v}")
    else:
        print(f"  cats: {list(v.keys())}")
