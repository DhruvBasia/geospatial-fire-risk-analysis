# check_literal_template_strings.py
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'\$\{[a-zA-Z0-9_.]+\}', html)
print(f"Literal JS template strings in index.html: {len(matches)}")
for m in sorted(set(matches))[:30]:
    print(" ", m)
