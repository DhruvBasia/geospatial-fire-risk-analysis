# find_analytics_markup.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('<!-- Risk Tier Distribution & Locality Ranking -->')
print(c[idx:idx+800])
