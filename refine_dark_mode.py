# refine_dark_mode.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

extra_dark_rules = """
    /* Specific Element Overrides for Route HUD, Navigation & Modals */
    [data-theme="dark"] #route-card,
    [data-theme="dark"] .route-card {{
      background: #111a2e;
      border: 1px solid #2a3d60;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
    }}
    [data-theme="dark"] .route-header {{
      background: #0d1525;
      border-bottom: 1px solid #1e2c47;
      color: #f8fafc;
    }}
    [data-theme="dark"] .route-title {{
      color: #f8fafc;
    }}
    [data-theme="dark"] .route-summary-bar {{
      background: #162238;
      border-bottom: 1px solid #1e2c47;
    }}
    [data-theme="dark"] .route-kpi-val {{
      color: #f8fafc;
    }}
    [data-theme="dark"] .route-kpi-label {{
      color: #8292ab;
    }}
    [data-theme="dark"] .route-step-item {{
      border-bottom: 1px solid #1e2c47;
      color: #cbd5e1;
    }}
    [data-theme="dark"] .route-step-item:hover {{
      background: #162238;
      color: #f8fafc;
    }}
    [data-theme="dark"] .route-step-icon {{
      background: #1e2c47;
      color: #38bdf8;
    }}
    [data-theme="dark"] .rider-progress-wrap {{
      background: #162238;
      border-bottom: 1px solid #1e2c47;
    }}
    [data-theme="dark"] .rider-hud-road {{
      color: #f8fafc;
    }}
    [data-theme="dark"] .modal-score-card {{
      background: #162238;
      border-color: #2a3d60;
    }}
    [data-theme="dark"] .nav-tab-btn {{
      background: #162238;
      border-color: #2a3d60;
      color: #94a3b8;
    }}
    [data-theme="dark"] .nav-tab-btn:hover {{
      background: #1e2c47;
      color: #f8fafc;
    }}
    [data-theme="dark"] .nav-tab-btn.active {{
      background: #0e7490;
      border-color: #06b6d4;
      color: #ffffff;
    }}
    [data-theme="dark"] .search-input {{
      background: #162238;
      border-color: #2a3d60;
      color: #f8fafc;
    }}
    [data-theme="dark"] .search-input:focus {{
      border-color: #06b6d4;
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2);
    }}
    [data-theme="dark"] .route-fallback-notice {{
      background: rgba(217, 119, 6, 0.15);
      border-color: rgba(245, 158, 11, 0.3);
      color: #fbbf24;
    }}
"""

if '/* Specific Element Overrides for Route HUD' not in c:
    idx = c.find('/* Leaflet Overrides for Dark Mode */')
    if idx != -1:
        c = c[:idx] + extra_dark_rules + '\n    ' + c[idx:]
        with open('generate_app.py', 'w', encoding='utf-8') as f:
            f.write(c)
        print("SUCCESS: extra dark mode rules added to generate_app.py!")
    else:
        print("Target insertion point not found!")
else:
    print("Already inserted.")
