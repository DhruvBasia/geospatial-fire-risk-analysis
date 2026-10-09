# inspect_dashboards.py
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
print('=== DEMO USERS ===')
idx = c.find('const DEMO_USERS =')
if idx != -1:
    print(c[idx:idx+450])

print('\n=== DASH-CARDS BELOW MAP ===')
for m in re.finditer(r'<span class="dash-card-title">([^<]+)</span>', c):
    print(' -', m.group(1))

print('\n=== TABS / NAVIGATION ===')
for m in re.finditer(r'class="[^"]*nav-tab[^"]*"[^>]*>([^<]+)<', c):
    print(' - Tab:', m.group(1))

for m in re.finditer(r'<button[^>]*class="[^"]*role-btn[^"]*"[^>]*>.*?<div class="role-btn-name">([^<]+)</div>.*?<div class="role-btn-desc">([^<]+)</div>', c, re.DOTALL):
    print(' - Role Button:', m.group(1), '|', m.group(2))
