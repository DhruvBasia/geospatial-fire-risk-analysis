# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

emojis_found = []
for i, ch in enumerate(text):
    cp = ord(ch)
    if ch == '✕':
        continue
    if (0x1F300 <= cp <= 0x1FAFF) or (0x2600 <= cp <= 0x27BF) or (0x1F600 <= cp <= 0x1F64F) or (0x1F680 <= cp <= 0x1F6FF):
        line_num = text[:i].count('\n') + 1
        emojis_found.append((line_num, f"U+{cp:04X}"))

print(f"Total other emojis/dingbats found: {len(emojis_found)}")
for line, cp in emojis_found[:20]:
    print(f"Line {line}: {cp}")
