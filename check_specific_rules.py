# check_specific_rules.py
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

for cls in ['.nav-tab-btn', '.modal-score-card', '.rider-progress-wrap', '#route-card']:
    idx = c.find(cls)
    if idx != -1:
        print(f'=== {cls} ===')
        print(c[idx:idx+200])
        print()
