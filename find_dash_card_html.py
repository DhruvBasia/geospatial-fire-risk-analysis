# find_dash_card_html.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = [m.start() for m in re.finditer(r'<div class="dash-card">', c)]
print('Matches for <div class="dash-card">:', len(matches))
for pos in matches:
    print(c[pos:pos+150])
    print('---')
