# check_onclick_functions.py
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
onclicks = re.findall(r'onclick="([^"]+)"', html)
print(f"Total onclick handlers in HTML: {len(onclicks)}")

called_fns = set()
for oc in onclicks:
    # extract function names like foo()
    fns = re.findall(r'([a-zA-Z0-9_$]+)\s*\(', oc)
    for fn in fns:
        called_fns.add(fn)

print(f"Unique functions called in onclick: {len(called_fns)}")

# Now check where these functions are defined and if they are on window
script_part = html[html.find('<script>'):]
for fn in sorted(called_fns):
    def_pattern = f"function {fn}"
    win_pattern = f"window.{fn} ="
    in_script = def_pattern in script_part
    on_window = win_pattern in script_part
    print(f"  {fn}: defined={in_script}, on_window={on_window}")
