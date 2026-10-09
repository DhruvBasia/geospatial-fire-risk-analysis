# apply_theme_and_polish.py
# Applies Dark/Light mode toggle, CARTO Dark Matter basemap, glassmorphism, and modern UI polish.
import re

with open('generate_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add early theme execution script to <head>
early_theme_script = """  <script>
    (function() {{
      try {{
        var saved = localStorage.getItem('seelampur_theme');
        var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        var theme = saved || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
      }} catch(e) {{}}
    }})();
  </script>
"""

if '<script>\n    (function() {' not in content:
    content = content.replace('<head>\n', '<head>\n' + early_theme_script, 1)

# 2. Add Dark Theme CSS and Modern Polish CSS
dark_mode_and_polish_css = """
    /* =========================================================
       MODERN SCROLLBARS & SMOOTH ELEVATION
       ========================================================= */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
      background: rgba(148, 163, 184, 0.4);
      border-radius: 9999px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: rgba(148, 163, 184, 0.7);
    }}
    [data-theme="dark"] ::-webkit-scrollbar-thumb {{
      background: rgba(255, 255, 255, 0.2);
    }}
    [data-theme="dark"] ::-webkit-scrollbar-thumb:hover {{
      background: rgba(255, 255, 255, 0.4);
    }}

    /* =========================================================
       THEME TOGGLE BUTTON COMPONENT
       ========================================================= */
    .theme-toggle-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 12px 5px 6px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: var(--radius-full);
      color: #f1f5f9;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
    }}
    .theme-toggle-btn:hover {{
      background: rgba(255, 255, 255, 0.16);
      border-color: rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
    }}
    .theme-toggle-indicator {{
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.12);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #38bdf8;
      transition: all 0.25s ease;
    }}
    [data-theme="dark"] .theme-toggle-indicator {{
      background: #0284c7;
      color: #fef08a;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.45);
    }}
    .theme-toggle-btn:hover .theme-toggle-indicator {{
      transform: scale(1.08) rotate(15deg);
    }}

    .login-theme-bar {{
      position: absolute;
      top: 24px;
      right: 24px;
      z-index: 50;
    }}
    .login-theme-btn {{
      background: var(--paper-card);
      border: 1px solid var(--border);
      color: var(--text-primary);
      box-shadow: var(--shadow-sm);
    }}
    .login-theme-btn:hover {{
      background: var(--paper);
      border-color: var(--border-dark);
    }}
    [data-theme="dark"] .login-theme-btn {{
      background: #162238;
      border-color: #2a3d60;
      color: #f8fafc;
    }}

    /* =========================================================
       DARK MODE THEME OVERRIDES (COMPREHENSIVE)
       ========================================================= */
    [data-theme="dark"], body.dark-theme {{
      --navy-950: #02060c;
      --navy-900: #060c16;
      --navy-850: #0a1322;
      --navy-800: #0f1c30;
      --navy-700: #142742;
      --navy-600: #1b355a;
      
      --paper: #090e17;
      --paper-card: #111a2e;
      --border: #1e2c47;
      --border-dark: #2a3d60;
      --text-primary: #f8fafc;
      --text-secondary: #cbd5e1;
      --text-muted: #8292ab;
      
      --risk-low-bg: rgba(22, 163, 74, 0.16);
      --risk-moderate-bg: rgba(217, 119, 6, 0.16);
      --risk-high-bg: rgba(234, 88, 12, 0.16);
      --risk-severe-bg: rgba(220, 38, 38, 0.16);
      
      --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.4);
      --shadow-md: 0 4px 10px -1px rgba(0, 0, 0, 0.45);
      --shadow-lg: 0 12px 24px -3px rgba(0, 0, 0, 0.55);
      --shadow-xl: 0 20px 30px -5px rgba(0, 0, 0, 0.65);
      --shadow-modal: 0 25px 60px -10px rgba(0, 0, 0, 0.75);
    }}

    [data-theme="dark"] html,
    [data-theme="dark"] body {{
      background-color: var(--paper);
      color: var(--text-primary);
    }}

    /* Top Bar & KPI Strip in Dark Mode */
    [data-theme="dark"] .top-bar {{
      background: var(--navy-900);
      border-bottom: 1px solid var(--border);
    }}
    [data-theme="dark"] .kpi-strip {{
      background: #111a2e;
      border-bottom: 1px solid var(--border);
    }}
    [data-theme="dark"] .kpi-label {{
      color: var(--text-muted);
    }}
    [data-theme="dark"] .kpi-value {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .kpi-refresh-note {{
      color: var(--text-muted);
    }}

    /* Cards, Panels & Headers in Dark Mode */
    [data-theme="dark"] .filter-controls-card,
    [data-theme="dark"] .analytics-rail-card,
    [data-theme="dark"] .map-widget-card,
    [data-theme="dark"] .dash-card,
    [data-theme="dark"] .preview-card {{
      background: #111a2e;
      border-color: var(--border);
      box-shadow: var(--shadow-sm);
    }}

    [data-theme="dark"] .filter-card-header,
    [data-theme="dark"] .analytics-rail-header,
    [data-theme="dark"] .map-widget-header,
    [data-theme="dark"] .dash-card-header {{
      background: #0d1525;
      border-bottom: 1px solid var(--border);
      color: var(--text-primary);
    }}

    [data-theme="dark"] .map-widget-title,
    [data-theme="dark"] .filter-card-title,
    [data-theme="dark"] .analytics-rail-title,
    [data-theme="dark"] .dash-card-title,
    [data-theme="dark"] .preview-name {{
      color: var(--text-primary);
    }}

    [data-theme="dark"] .map-widget-footer {{
      background: #0d1525;
      border-top: 1px solid var(--border);
    }}
    [data-theme="dark"] .map-footer-legend {{
      color: var(--text-secondary);
    }}

    /* Controls & Form Inputs in Dark Mode */
    [data-theme="dark"] .form-input,
    [data-theme="dark"] .locality-select,
    [data-theme="dark"] .search-box-sm {{
      background: #162238;
      border-color: #2a3d60;
      color: #f8fafc;
    }}
    [data-theme="dark"] .form-input::placeholder,
    [data-theme="dark"] .search-box-sm::placeholder {{
      color: #64748b;
    }}
    [data-theme="dark"] .form-input:focus,
    [data-theme="dark"] .locality-select:focus,
    [data-theme="dark"] .search-box-sm:focus {{
      border-color: #06b6d4;
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2);
    }}
    [data-theme="dark"] .search-clear-btn {{
      color: #94a3b8;
    }}

    [data-theme="dark"] .style-btn-pill {{
      background: #162238;
      border-color: #2a3d60;
      color: #94a3b8;
    }}
    [data-theme="dark"] .style-btn-pill:hover {{
      background: #1e2c47;
      color: #f8fafc;
    }}
    [data-theme="dark"] .style-btn-pill.active {{
      background: #0e7490;
      border-color: #06b6d4;
      color: #ffffff;
    }}

    [data-theme="dark"] .layer-toggle-item {{
      background: #162238;
      border-color: #1e2c47;
      color: #cbd5e1;
    }}
    [data-theme="dark"] .layer-toggle-item:hover {{
      background: #1e2c47;
    }}

    [data-theme="dark"] .btn-locate-me {{
      background: #162238;
      border-color: #2a3d60;
      color: #38bdf8;
    }}
    [data-theme="dark"] .btn-locate-me:hover {{
      background: #1e2c47;
    }}

    [data-theme="dark"] .btn-expand-map {{
      background: #162238;
      border-color: #2a3d60;
      color: #cbd5e1;
    }}
    [data-theme="dark"] .btn-expand-map:hover {{
      background: #1e2c47;
      color: #ffffff;
    }}

    /* Preview & Deficiency Cards in Dark Mode */
    [data-theme="dark"] .preview-stat-card,
    [data-theme="dark"] .preview-deficiency-box,
    [data-theme="dark"] .deficiency-mini-card {{
      background: #162238;
      border-color: #1e2c47;
    }}
    [data-theme="dark"] .preview-stat-label {{
      color: var(--text-muted);
    }}
    [data-theme="dark"] .preview-stat-val {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .preview-def-title,
    [data-theme="dark"] .def-mini-name {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .def-mini-val {{
      color: var(--text-muted);
    }}
    [data-theme="dark"] .factor-track-mini {{
      background: #1e2c47;
    }}

    /* Analytics Dashboard in Dark Mode */
    [data-theme="dark"] .dash-table-wrap {{
      background: #111a2e;
      border-color: var(--border);
    }}
    [data-theme="dark"] .dash-table th {{
      background: #0d1525;
      color: var(--text-muted);
      border-bottom-color: var(--border);
    }}
    [data-theme="dark"] .dash-table td {{
      color: var(--text-secondary);
      border-bottom-color: #162238;
    }}
    [data-theme="dark"] .dash-table tr:hover td {{
      background: #162238;
      color: var(--text-primary);
    }}
    [data-theme="dark"] .factor-rank-name,
    [data-theme="dark"] .locality-rank-label {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .factor-rank-score,
    [data-theme="dark"] .locality-rank-val {{
      color: var(--text-muted);
    }}
    [data-theme="dark"] .factor-rank-track,
    [data-theme="dark"] .locality-rank-track {{
      background: #162238;
    }}
    [data-theme="dark"] .tier-split-legend-label {{
      color: var(--text-secondary);
    }}
    [data-theme="dark"] .tier-split-legend-val {{
      color: var(--text-primary);
    }}

    /* Modals in Dark Mode */
    [data-theme="dark"] .workshop-modal,
    [data-theme="dark"] .hose-modal {{
      background: #111a2e;
      border-color: #22324f;
      box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.75);
    }}
    [data-theme="dark"] .modal-header,
    [data-theme="dark"] .hose-modal-header {{
      background: #0d1525;
      border-bottom-color: var(--border);
    }}
    [data-theme="dark"] .modal-footer,
    [data-theme="dark"] .hose-modal-footer {{
      background: #0d1525;
      border-top-color: var(--border);
    }}
    [data-theme="dark"] .modal-body,
    [data-theme="dark"] .hose-modal-body {{
      background: #111a2e;
    }}
    [data-theme="dark"] .modal-title,
    [data-theme="dark"] .hose-modal-title {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .modal-close-btn,
    [data-theme="dark"] .hose-close-btn {{
      background: #162238;
      border-color: #2a3d60;
      color: #cbd5e1;
    }}
    [data-theme="dark"] .modal-close-btn:hover,
    [data-theme="dark"] .hose-close-btn:hover {{
      background: #1e2c47;
      color: #ffffff;
    }}
    [data-theme="dark"] .modal-summary-banner {{
      background: #162238;
      border-color: #2a3d60;
      color: #f1f5f9;
    }}
    [data-theme="dark"] .factor-group-card {{
      background: #162238;
      border-color: #1e2c47;
    }}
    [data-theme="dark"] .factor-group-title {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .factor-item {{
      border-bottom-color: #1e2c47;
    }}
    [data-theme="dark"] .factor-label {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .factor-desc {{
      color: var(--text-secondary);
    }}
    [data-theme="dark"] .factor-track {{
      background: #111a2e;
    }}
    [data-theme="dark"] .btn-action {{
      background: #162238;
      border-color: #2a3d60;
      color: #cbd5e1;
    }}
    [data-theme="dark"] .btn-action:hover {{
      background: #1e2c47;
      color: #ffffff;
    }}
    [data-theme="dark"] .btn-modal-dismiss {{
      background: #162238;
      border-color: #2a3d60;
      color: #cbd5e1;
    }}

    /* Hose Modal Elements in Dark Mode */
    [data-theme="dark"] .hose-kpi-card,
    [data-theme="dark"] .hose-hazard-card,
    [data-theme="dark"] .sop-card {{
      background: #162238;
      border-color: #1e2c47;
    }}
    [data-theme="dark"] .hose-kpi-label {{
      color: var(--text-muted);
    }}
    [data-theme="dark"] .hose-kpi-val,
    [data-theme="dark"] .hose-hazard-title {{
      color: var(--text-primary);
    }}
    [data-theme="dark"] .hose-hazard-val {{
      color: var(--text-secondary);
    }}
    [data-theme="dark"] .sop-step-item {{
      border-bottom-color: #1e2c47;
    }}
    [data-theme="dark"] .sop-step-text {{
      color: #cbd5e1;
    }}
    [data-theme="dark"] .hose-breakdown-table {{
      border-color: #1e2c47;
    }}
    [data-theme="dark"] .hose-breakdown-table th {{
      background: #0d1525;
      color: var(--text-muted);
      border-bottom-color: #1e2c47;
    }}
    [data-theme="dark"] .hose-breakdown-table td {{
      background: #162238;
      color: #cbd5e1;
      border-bottom-color: #1e2c47;
    }}

    /* Simulation HUD & Navigation in Dark Mode */
    [data-theme="dark"] .sim-control-bar,
    [data-theme="dark"] .route-card {{
      background: #111a2e;
      border-color: #2a3d60;
    }}
    [data-theme="dark"] .route-step-item {{
      border-bottom-color: #1e2c47;
      color: #cbd5e1;
    }}

    /* Login Screen Right Panel in Dark Mode */
    [data-theme="dark"] .login-form-panel {{
      background: #090e17;
      position: relative;
    }}
    [data-theme="dark"] .login-box {{
      background: #111a2e;
      border: 1px solid #1e2c47;
      border-radius: var(--radius-lg);
      padding: 32px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}
    [data-theme="dark"] .login-heading {{
      color: #f8fafc;
    }}
    [data-theme="dark"] .login-subheading {{
      color: #94a3b8;
    }}
    [data-theme="dark"] .role-btn {{
      background: #162238;
      border-color: #2a3d60;
    }}
    [data-theme="dark"] .role-btn:hover {{
      background: #1e2c47;
      border-color: #38bdf8;
    }}
    [data-theme="dark"] .role-btn-name {{
      color: #f8fafc;
    }}
    [data-theme="dark"] .role-btn-desc {{
      color: #94a3b8;
    }}
    [data-theme="dark"] .btn-guest-bypass {{
      background: rgba(14, 116, 144, 0.2);
      border-color: rgba(6, 182, 212, 0.4);
      color: #22d3ee;
    }}
    [data-theme="dark"] .btn-guest-bypass:hover {{
      background: rgba(14, 116, 144, 0.35);
    }}
    [data-theme="dark"] .demo-notice {{
      background: #162238;
      border-color: #1e2c47;
      color: #94a3b8;
    }}
    [data-theme="dark"] .login-divider {{
      color: #64748b;
    }}
    [data-theme="dark"] .login-divider::before,
    [data-theme="dark"] .login-divider::after {{
      background: #1e2c47;
    }}

    /* Leaflet Overrides for Dark Mode */
    [data-theme="dark"] .leaflet-container {{
      background: #090e17 !important;
    }}
    [data-theme="dark"] .leaflet-bar {{
      border: 1px solid #2a3d60 !important;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }}
    [data-theme="dark"] .leaflet-bar a {{
      background-color: #162238 !important;
      border-bottom: 1px solid #2a3d60 !important;
      color: #f8fafc !important;
    }}
    [data-theme="dark"] .leaflet-bar a:hover {{
      background-color: #1e2c47 !important;
    }}
    [data-theme="dark"] .leaflet-control-attribution {{
      background: rgba(9, 14, 23, 0.8) !important;
      color: #94a3b8 !important;
      backdrop-filter: blur(4px);
    }}
    [data-theme="dark"] .leaflet-control-attribution a {{
      color: #38bdf8 !important;
    }}
    [data-theme="dark"] .leaflet-popup-content-wrapper {{
      background: #111a2e !important;
      color: #f8fafc !important;
      border: 1px solid #2a3d60 !important;
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.6) !important;
    }}
    [data-theme="dark"] .leaflet-popup-tip {{
      background: #111a2e !important;
    }}
    [data-theme="dark"] .custom-map-tooltip {{
      background: #0d1525 !important;
      color: #f8fafc !important;
      border: 1px solid #2a3d60 !important;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
    }}
"""

# Insert CSS before </style>
if '/* DARK MODE THEME OVERRIDES' not in content:
    content = content.replace('  </style>', dark_mode_and_polish_css + '\n  </style>', 1)

# 3. Top bar theme toggle button
top_bar_btn_html = """        <!-- Modern Dark/Light Theme Toggle -->
        <button type="button" id="theme-toggle-btn" class="theme-toggle-btn" onclick="toggleTheme()" title="Switch Theme (Dark / Light)" aria-label="Toggle dark and light theme">
          <span class="theme-toggle-indicator">
            <svg id="theme-icon-sun" class="svg-icon theme-icon" viewBox="0 0 24 24" style="display:none; width:13px; height:13px;"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            <svg id="theme-icon-moon" class="svg-icon theme-icon" viewBox="0 0 24 24" style="width:13px; height:13px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </span>
          <span id="theme-toggle-label" class="theme-toggle-label">Dark Mode</span>
        </button>

"""

target_topbar = '<div class="top-bar-right">\n        <div class="user-profile-pill">'
if 'id="theme-toggle-btn"' not in content:
    content = content.replace(target_topbar, '<div class="top-bar-right">\n' + top_bar_btn_html + '        <div class="user-profile-pill">', 1)

# 4. Login screen theme toggle button
login_theme_btn_html = """    <div class="login-form-panel">
      <div class="login-theme-bar">
        <button type="button" id="login-theme-btn" class="theme-toggle-btn login-theme-btn" onclick="toggleTheme()" title="Switch Theme (Dark / Light)">
          <span class="theme-toggle-indicator">
            <svg id="login-theme-sun" class="svg-icon theme-icon" viewBox="0 0 24 24" style="display:none; width:13px; height:13px;"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            <svg id="login-theme-moon" class="svg-icon theme-icon" viewBox="0 0 24 24" style="width:13px; height:13px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </span>
          <span id="login-theme-label" class="theme-toggle-label">Dark Mode</span>
        </button>
      </div>"""

if 'id="login-theme-btn"' not in content:
    content = content.replace('    <div class="login-form-panel">', login_theme_btn_html, 1)

# 5. Map style buttons: add Dark Matter button
dark_tile_btn_html = '<button type="button" id="tile-btn-dark" class="style-btn-pill" onclick="setBaseTile(\'dark\')">Dark Matter</button>\n              '
if 'id="tile-btn-dark"' not in content:
    content = content.replace(
        '<button type="button" id="tile-btn-satellite" class="style-btn-pill" onclick="setBaseTile(\'satellite\')">Satellite</button>\n              ',
        '<button type="button" id="tile-btn-satellite" class="style-btn-pill" onclick="setBaseTile(\'satellite\')">Satellite</button>\n              ' + dark_tile_btn_html,
        1
    )

# 6. JS for dark tile and theme switcher logic
js_theme_logic = """
    // =========================================================
    // THEME STATE & TOGGLE ENGINE (DARK / LIGHT MODE)
    // =========================================================
    let currentTheme = 'light';

    function initTheme() {{
      let saved = null;
      try {{
        saved = localStorage.getItem('seelampur_theme');
      }} catch (e) {{
        console.warn('LocalStorage unavailable for theme:', e);
      }}

      if (saved === 'dark' || saved === 'light') {{
        applyTheme(saved, false);
      }} else {{
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light', false);
      }}

      if (window.matchMedia) {{
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {{
          let userSet = null;
          try {{ userSet = localStorage.getItem('seelampur_theme'); }} catch (_) {{}}
          if (!userSet) {{
            applyTheme(e.matches ? 'dark' : 'light', true);
          }}
        }});
      }}
    }}

    function applyTheme(theme, switchTile) {{
      currentTheme = theme;
      document.documentElement.setAttribute('data-theme', theme);
      document.body.classList.toggle('dark-theme', theme === 'dark');

      const label = document.getElementById('theme-toggle-label');
      const sun = document.getElementById('theme-icon-sun');
      const moon = document.getElementById('theme-icon-moon');
      const loginLabel = document.getElementById('login-theme-label');
      const loginSun = document.getElementById('login-theme-sun');
      const loginMoon = document.getElementById('login-theme-moon');

      if (theme === 'dark') {{
        if (label) label.textContent = 'Light Mode';
        if (sun) sun.style.display = 'block';
        if (moon) moon.style.display = 'none';
        if (loginLabel) loginLabel.textContent = 'Light Mode';
        if (loginSun) loginSun.style.display = 'block';
        if (loginMoon) loginMoon.style.display = 'none';

        if (switchTile && window.map && (currentTile === 'google' || currentTile === 'osm' || currentTile === 'esri')) {{
          setBaseTile('dark');
        }}
      }} else {{
        if (label) label.textContent = 'Dark Mode';
        if (sun) sun.style.display = 'none';
        if (moon) moon.style.display = 'block';
        if (loginLabel) loginLabel.textContent = 'Dark Mode';
        if (loginSun) loginSun.style.display = 'none';
        if (loginMoon) loginMoon.style.display = 'block';

        if (switchTile && window.map && currentTile === 'dark') {{
          setBaseTile('google');
        }}
      }}

      try {{
        localStorage.setItem('seelampur_theme', theme);
      }} catch (e) {{
        console.warn('LocalStorage save failed:', e);
      }}
    }}

    function toggleTheme() {{
      const next = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(next, true);
    }}
    window.toggleTheme = toggleTheme;
"""

# Insert js_theme_logic right before window.addEventListener('DOMContentLoaded'
if 'let currentTheme =' not in content:
    content = content.replace(
        "    window.addEventListener('DOMContentLoaded', () => {{",
        js_theme_logic + "\n    window.addEventListener('DOMContentLoaded', () => {{\n      initTheme();",
        1
    )

# 7. Add baseLayers.dark to initMap()
dark_baselayer_code = """
      // CARTO Dark Matter (High-Aesthetic Dark Mode Map)
      baseLayers.dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {{
        attribution: '&copy; CARTO &copy; OpenStreetMap contributors',
        subdomains: 'abcd',
        maxZoom: 20
      }});
"""

if 'baseLayers.dark =' not in content:
    content = content.replace(
        "      // Esri World Street Map",
        dark_baselayer_code + "      // Esri World Street Map",
        1
    )

# Update default basemap selection if in dark theme
default_basemap_code = """      // Set default basemap according to theme
      if (currentTheme === 'dark') {{
        baseLayers.dark.addTo(map);
        currentTile = 'dark';
        const darkBtn = document.getElementById('tile-btn-dark');
        const googleBtn = document.getElementById('tile-btn-google');
        if (darkBtn) darkBtn.classList.add('active');
        if (googleBtn) googleBtn.classList.remove('active');
      }} else {{
        baseLayers.google.addTo(map);
        currentTile = 'google';
      }}
"""

if 'if (currentTheme === \'dark\') {{' not in content:
    content = content.replace(
        "      // Set Google Street as default basemap\n      baseLayers.google.addTo(map);",
        default_basemap_code,
        1
    )

# Update setBaseTile to handle 'dark'
if "'dark'" not in content:
    content = content.replace(
        "['google', 'satellite', 'osm', 'esri'].forEach(t => {{",
        "['google', 'satellite', 'dark', 'osm', 'esri'].forEach(t => {{",
        1
    )

with open('generate_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: generate_app.py updated with Dark/Light theme toggle and modern aesthetics!")
