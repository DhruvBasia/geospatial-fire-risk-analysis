# scan_inputs.py
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = set(re.findall(r'<(?:input|select)\s+[^>]*class="([^"]+)"', c))
print('Input classes found:')
for m in sorted(matches):
    print(' ', m)
