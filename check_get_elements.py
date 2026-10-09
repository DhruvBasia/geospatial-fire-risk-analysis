# check_get_elements.py
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = set(re.findall(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)", html))
print(f"Total document.getElementById calls: {len(matches)}")

missing = []
for el_id in sorted(matches):
    pattern = f'id="{el_id}"'
    if pattern not in html and f"id='{el_id}'" not in html:
        missing.append(el_id)

print(f"Missing element IDs in DOM: {len(missing)}")
for m in missing:
    print("  MISSING:", m)
