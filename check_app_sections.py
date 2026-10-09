# check_app_sections.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

import re
print("Top bar snippet:")
idx = c.find('<header class="top-bar">')
print(c[idx:idx+400])

print("\nAnalytics section snippet:")
idx2 = c.find('id="analytics-dashboard-card"')
if idx2 == -1: idx2 = c.find('class="analytics-dashboard-card"')
if idx2 == -1: idx2 = c.find('analytics-grid-row')
print(c[idx2-100:idx2+500])
