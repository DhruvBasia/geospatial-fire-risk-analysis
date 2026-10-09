import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all document.getElementById('...')
js_ids = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", html))
# Find all id='...' in html
html_ids = set(re.findall(r"id=['\"]([^'\"]+)['\"]", html))

missing = js_ids - html_ids
print('Referenced IDs in JS:', len(js_ids))
print('IDs in HTML:', len(html_ids))
print('Missing IDs:', missing)

# Check for unmatched brackets or syntax flaws in script
script_start = html.find('<script>')
script_end = html.rfind('</script>')
script = html[script_start+8:script_end]

open_curlies = script.count('{')
close_curlies = script.count('}')
open_parens = script.count('(')
close_parens = script.count(')')
open_brackets = script.count('[')
close_brackets = script.count(']')

print(f"Curlies: {open_curlies} vs {close_curlies}")
print(f"Parens: {open_parens} vs {close_parens}")
print(f"Brackets: {open_brackets} vs {close_brackets}")
