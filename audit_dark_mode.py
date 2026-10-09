# audit_dark_mode.py
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re

# Find any css rules before DARK MODE THEME OVERRIDES that set background to #fff or #ffffff or white
css_part = c[:c.find('/* =========================================================\n       DARK MODE THEME OVERRIDES')]
white_bg_selectors = re.findall(r'([^{}\n]+)\s*\{[^}]*background:\s*(?:#fff|#ffffff|white)\b', css_part)
print(f'Found {len(white_bg_selectors)} selectors with light background:')
for s in sorted(set(s.strip() for s in white_bg_selectors)):
    print(' ', s)
