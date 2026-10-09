# find_broken_onclicks.py
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
for m in re.finditer(r'onclick="[^"]*flyTo[^"]*"', html):
    print("flyTo onclick:", m.group(0))

for m in re.finditer(r'onclick="[^"]*find[^"]*"', html):
    print("find onclick:", m.group(0))
