# inspect_topbar_kpi.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<header class="top-bar">' in l:
        for j in range(i, i+65):
            print(f"{j+1}: {lines[j]}", end='')
        break
