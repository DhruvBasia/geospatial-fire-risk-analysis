# inspect_login_logic.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('function quickLogin(')
print(c[idx:idx+600])

print("\n--- showApp snippet ---")
idx2 = c.find('function showApp()')
print(c[idx2:idx2+600])
