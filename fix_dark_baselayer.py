# fix_dark_baselayer.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the tilelayer url curly braces
old_str = "baseLayers.dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'"
new_str = "baseLayers.dark = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png'"

if old_str in c:
    c = c.replace(old_str, new_str)
    print("Found and replaced old_str with doubled curly braces!")
else:
    print("old_str not found, checking...")
    # let's search for cartocdn
    idx = c.find('cartocdn.com')
    if idx != -1:
        print("Surrounding:", c[idx-40:idx+80])

with open('generate_app.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("generate_app.py saved!")
