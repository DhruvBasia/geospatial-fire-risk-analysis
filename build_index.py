import json
import re

with open('workshops_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

workshops_json = json.dumps(data['workshops'], ensure_ascii=False)
scoring_map_json = json.dumps(data['scoring_map'], ensure_ascii=False)

html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Seelampur Fire Watch — USAP Fire Risk Intelligence</title>
  
  <!-- Inter Font -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  
  <style>
    /* Global Reset & Design Tokens */
    :root {{
      --navy: #0e3a5f;
      --navy-dark: #07253d;
      --navy-light: #164e7e;
      --navy-hover: #1e5a8f;
      --teal: #0e7490;
      --teal-dark: #155e75;
      --teal-light: #e0f2fe;
      --paper: #f4f6fa;
      --paper-card: #ffffff;
      --border: #e2e8f0;
      --border-dark: #cbd5e1;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --risk-low: #2f9e44;
      --risk-moderate: #d9932a;
      --risk-high: #e2683c;
      --risk-severe: #cf3a3a;
      --risk-low-bg: #ebfbee;
      --risk-moderate-bg: #fff9db;
      --risk-high-bg: #fff4e6;
      --risk-severe-bg: #ffe3e3;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
      --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.15), 0 10px 10px -5px rgba(0,0,0,0.04);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-full: 9999px;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html, body {{
      width: 100%;
      height: 100%;
      font-family: var(--font);
      background-color: var(--paper);
      color: var(--text-primary);
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }}

    .num-tnum {{
      font-feature-settings: 'tnum';
      font-variant-numeric: tabular-nums;
    }}

    /* Accessibility */
    :focus-visible {{
      outline: 2px solid var(--teal);
      outline-offset: 2px;
    }}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }}
    }}

    /* Eyebrow Label */
    .eyebrow {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--teal);
      display: inline-block;
    }}

    /* Screen Views */
    .screen {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      display: none;
    }}

    .screen.active {{
      display: flex;
    }}

    /* =========================================================
       1. LOGIN SCREEN
       ========================================================= */
    #login-screen {{
      display: flex;
      flex-direction: row;
      z-index: 2000;
      background: #081d30;
    }}

    .login-hero {{
      flex: 1.15;
      background: linear-gradient(145deg, #07253d 0%, #0e3a5f 55%, #164e7e 100%);
      padding: 48px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: #ffffff;
      position: relative;
      overflow: hidden;
    }}

    .login-hero::before {{
      content: "";
      position: absolute;
      top: -20%;
      right: -20%;
      width: 500px;
      height: 500px;
      background: radial-gradient(circle, rgba(14, 116, 144, 0.25) 0%, rgba(14, 116, 144, 0) 70%);
      border-radius: 50%;
      pointer-events: none;
    }}

    .hero-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .hero-badge {{
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 6px 12px;
      border-radius: var(--radius-full);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.04em;
      color: #7dd3fc;
    }}

    .hero-center {{
      margin: auto 0;
      max-width: 540px;
    }}

    .hero-title {{
      font-size: 38px;
      line-height: 1.2;
      font-weight: 800;
      margin-bottom: 16px;
      letter-spacing: -0.02em;
    }}

    .hero-desc {{
      font-size: 15px;
      line-height: 1.6;
      color: #cbd5e1;
      margin-bottom: 28px;
    }}

    /* Risk Scale Bar */
    .hero-scale {{
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: var(--radius-md);
      padding: 16px;
      margin-bottom: 32px;
    }}

    .hero-scale-header {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
      color: #94a3b8;
      margin-bottom: 8px;
    }}

    .scale-bar {{
      height: 10px;
      border-radius: 5px;
      background: linear-gradient(to right, #2f9e44 0%, #d9932a 35%, #e2683c 65%, #cf3a3a 100%);
      margin-bottom: 8px;
    }}

    .scale-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 600;
    }}

    .scale-labels span:nth-child(1) {{ color: #4ade80; }}
    .scale-labels span:nth-child(2) {{ color: #facc15; }}
    .scale-labels span:nth-child(3) {{ color: #fb923c; }}
    .scale-labels span:nth-child(4) {{ color: #f87171; }}

    /* Hero Stats */
    .hero-stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }}

    .stat-pill {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-md);
      padding: 14px 16px;
    }}

    .stat-pill-val {{
      font-size: 26px;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 2px;
    }}

    .stat-pill-val.severe {{
      color: #f87171;
    }}

    .stat-pill-lbl {{
      font-size: 12px;
      color: #94a3b8;
      font-weight: 500;
      line-height: 1.3;
    }}

    .hero-footer {{
      font-size: 12px;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Login Form Right Panel */
    .login-form-panel {{
      flex: 0.85;
      background: #ffffff;
      padding: 48px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      overflow-y: auto;
    }}

    .login-box {{
      max-width: 420px;
      width: 100%;
      margin: 0 auto;
    }}

    .login-heading {{
      font-size: 24px;
      font-weight: 800;
      color: var(--navy-dark);
      margin-bottom: 6px;
    }}

    .login-subheading {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 24px;
      line-height: 1.5;
    }}

    /* Quick Sign-In Grid */
    .quick-login-section {{
      margin-bottom: 24px;
    }}

    .quick-login-title {{
      margin-bottom: 12px;
    }}

    .quick-roles-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}

    .role-btn {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .role-btn:hover {{
      background: #f1f5f9;
      border-color: var(--teal);
      transform: translateY(-1px);
    }}

    .avatar-initials {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 12px;
      font-weight: 700;
      flex-shrink: 0;
    }}

    .role-btn-info {{
      overflow: hidden;
    }}

    .role-btn-name {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .role-btn-desc {{
      font-size: 11px;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .login-divider {{
      display: flex;
      align-items: center;
      margin: 20px 0;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 500;
    }}

    .login-divider::before, .login-divider::after {{
      content: "";
      flex: 1;
      height: 1px;
      background: var(--border);
    }}

    .login-divider span {{
      padding: 0 12px;
    }}

    /* Form Inputs */
    .form-group {{
      margin-bottom: 16px;
    }}

    .form-label {{
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 6px;
    }}

    .form-input {{
      width: 100%;
      padding: 10px 14px;
      font-size: 14px;
      font-family: inherit;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: #f8fafc;
      color: var(--text-primary);
      transition: border-color 0.15s ease, background-color 0.15s ease;
    }}

    .form-input:focus {{
      outline: none;
      border-color: var(--teal);
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(14, 116, 144, 0.12);
    }}

    .btn-submit {{
      width: 100%;
      padding: 12px;
      font-size: 14px;
      font-weight: 700;
      font-family: inherit;
      color: #ffffff;
      background: var(--navy);
      border: none;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: background-color 0.15s ease, transform 0.1s ease;
      margin-top: 8px;
    }}

    .btn-submit:hover {{
      background: var(--navy-hover);
    }}

    .btn-submit:active {{
      transform: scale(0.99);
    }}

    .login-error {{
      background: var(--risk-severe-bg);
      border: 1px solid #fca5a5;
      color: #b91c1c;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 500;
      margin-bottom: 14px;
      display: none;
    }}

    .demo-notice {{
      margin-top: 20px;
      padding: 12px 14px;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: var(--radius-sm);
      font-size: 12px;
      line-height: 1.5;
      color: #166534;
    }}

    /* =========================================================
       MAIN APP SHELL (POST-LOGIN)
       ========================================================= */
    #app-screen {{
      flex-direction: column;
      z-index: 100;
      background: var(--paper);
    }}

    /* Top Bar */
    .top-bar {{
      height: 56px;
      background: var(--navy-dark);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      color: #ffffff;
      flex-shrink: 0;
      z-index: 1300;
    }}

    .top-bar-left {{
      display: flex;
      align-items: center;
      gap: 18px;
    }}

    .app-logo {{
      display: flex;
      align-items: center;
      gap: 9px;
      font-size: 16px;
      font-weight: 800;
      letter-spacing: -0.01em;
      color: #ffffff;
      text-decoration: none;
    }}

    .app-logo-flame {{
      background: #cf3a3a;
      width: 28px;
      height: 28px;
      border-radius: 7px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
    }}

    .app-subtitle-badge {{
      font-size: 11px;
      font-weight: 600;
      background: rgba(255, 255, 255, 0.1);
      padding: 3px 8px;
      border-radius: var(--radius-full);
      color: #93c5fd;
    }}

    /* Tab Switcher */
    .tab-switcher {{
      display: flex;
      background: rgba(0, 0, 0, 0.25);
      padding: 3px;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .tab-btn {{
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      font-family: inherit;
      color: #94a3b8;
      background: transparent;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .tab-btn:hover {{
      color: #ffffff;
    }}

    .tab-btn.active {{
      background: var(--teal);
      color: #ffffff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }}

    .top-bar-right {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .user-profile-pill {{
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(255, 255, 255, 0.08);
      padding: 4px 10px 4px 6px;
      border-radius: var(--radius-full);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}

    .user-avatar {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--teal);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
    }}

    .user-info {{
      display: flex;
      flex-direction: column;
      line-height: 1.2;
    }}

    .user-name {{
      font-size: 12px;
      font-weight: 700;
      color: #f8fafc;
    }}

    .user-role-tag {{
      font-size: 10px;
      color: #94a3b8;
    }}

    .btn-logout {{
      background: transparent;
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #cbd5e1;
      padding: 5px 10px;
      font-size: 12px;
      font-weight: 600;
      font-family: inherit;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .btn-logout:hover {{
      background: rgba(239, 68, 68, 0.2);
      border-color: #ef4444;
      color: #fca5a5;
    }}

    /* Main Content Wrapper */
    .main-body {{
      flex: 1;
      position: relative;
      overflow: hidden;
      display: flex;
    }}

    /* =========================================================
       MAP VIEW & KPI STRIP
       ========================================================= */
    #tab-view-map {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      display: flex;
      flex-direction: column;
    }}

    /* KPI Strip */
    .kpi-strip {{
      height: 52px;
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      padding: 0 16px;
      gap: 12px;
      z-index: 1100;
      flex-shrink: 0;
      overflow-x: auto;
      box-shadow: var(--shadow-sm);
    }}

    .kpi-card {{
      display: flex;
      align-items: center;
      gap: 9px;
      padding: 4px 12px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .kpi-icon {{
      font-size: 16px;
    }}

    .kpi-data {{
      display: flex;
      flex-direction: column;
      line-height: 1.15;
    }}

    .kpi-val {{
      font-size: 14px;
      font-weight: 800;
      color: var(--text-primary);
    }}

    .kpi-val.severe {{
      color: var(--risk-severe);
    }}

    .kpi-lbl {{
      font-size: 10px;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    /* Map Workspace Area */
    .map-workspace {{
      flex: 1;
      position: relative;
      display: flex;
    }}

    /* Filter Rail (Left) */
    .filter-rail {{
      width: 290px;
      background: #ffffff;
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 1100;
      box-shadow: var(--shadow-md);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      flex-shrink: 0;
    }}

    .rail-header {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .rail-title {{
      font-size: 13px;
      font-weight: 800;
      color: var(--navy-dark);
      letter-spacing: -0.01em;
    }}

    .rail-reset-btn {{
      background: transparent;
      border: none;
      font-size: 11px;
      font-weight: 600;
      color: var(--teal);
      cursor: pointer;
    }}

    .rail-reset-btn:hover {{
      text-decoration: underline;
    }}

    .rail-content {{
      padding: 16px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    .filter-group {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .filter-group-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .filter-group-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
    }}

    /* Search Box */
    .search-box {{
      position: relative;
    }}

    .search-input {{
      width: 100%;
      padding: 8px 30px 8px 10px;
      font-size: 13px;
      font-family: inherit;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: #f8fafc;
      color: var(--text-primary);
    }}

    .search-input:focus {{
      outline: none;
      border-color: var(--teal);
      background: #ffffff;
      box-shadow: 0 0 0 2px rgba(14, 116, 144, 0.1);
    }}

    .search-clear {{
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      font-size: 14px;
      color: var(--text-muted);
      cursor: pointer;
      display: none;
    }}

    /* Risk Tier Checkboxes */
    .tier-checkboxes {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .tier-check-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 8px;
      border-radius: 6px;
      background: #f8fafc;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.1s;
    }}

    .tier-check-item:hover {{
      background: #f1f5f9;
    }}

    .tier-check-left {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 600;
    }}

    .tier-color-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    .tier-count-chip {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: var(--radius-full);
      background: #e2e8f0;
      color: var(--text-secondary);
    }}

    /* Locality Selector */
    .locality-select {{
      width: 100%;
      padding: 8px 10px;
      font-size: 13px;
      font-family: inherit;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: #f8fafc;
      color: var(--text-primary);
      cursor: pointer;
    }}

    .locality-select:focus {{
      outline: none;
      border-color: var(--teal);
    }}

    /* Map Style Segmented Control */
    .segmented-control {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      background: #f1f5f9;
      padding: 3px;
      border-radius: var(--radius-sm);
      gap: 2px;
    }}

    .segment-btn {{
      padding: 6px 4px;
      font-size: 11px;
      font-weight: 600;
      font-family: inherit;
      background: transparent;
      border: none;
      border-radius: 4px;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
      text-align: center;
    }}

    .segment-btn.active {{
      background: #ffffff;
      color: var(--navy);
      box-shadow: 0 1px 2px rgba(0,0,0,0.1);
      font-weight: 700;
    }}

    /* Layer Switch Toggles */
    .layer-switches {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .layer-switch-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
    }}

    .toggle-switch {{
      position: relative;
      width: 36px;
      height: 20px;
      cursor: pointer;
    }}

    .toggle-switch input {{
      opacity: 0;
      width: 0;
      height: 0;
    }}

    .slider {{
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: #cbd5e1;
      transition: .2s;
      border-radius: 20px;
    }}

    .slider:before {{
      position: absolute;
      content: "";
      height: 14px;
      width: 14px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .2s;
      border-radius: 50%;
    }}

    input:checked + .slider {{
      background-color: var(--teal);
    }}

    input:checked + .slider:before {{
      transform: translateX(16px);
    }}

    /* Locate Me Button */
    .btn-locate {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px;
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      color: var(--navy);
      font-size: 12px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .btn-locate:hover {{
      background: var(--teal-light);
      border-color: var(--teal);
      color: var(--teal-dark);
    }}

    /* Map Canvas Container */
    #map-container {{
      flex: 1;
      height: 100%;
      position: relative;
      background: #e5e7eb;
    }}

    /* Floating Map Legend */
    .map-legend {{
      position: absolute;
      bottom: 24px;
      left: 16px;
      z-index: 1050;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(8px);
      padding: 12px 16px;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      border: 1px solid var(--border);
      max-width: 320px;
      pointer-events: auto;
    }}

    .legend-title {{
      font-size: 12px;
      font-weight: 800;
      color: var(--navy-dark);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-tiers {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 12px;
      margin-bottom: 10px;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .legend-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 0 0 1px rgba(0,0,0,0.15);
      flex-shrink: 0;
    }}

    .legend-disclaimer {{
      font-size: 10.5px;
      line-height: 1.4;
      color: #854d0e;
      background: #fef9c3;
      padding: 6px 8px;
      border-radius: 4px;
      border: 1px solid #fde047;
    }}

    /* Mobile Drawer Toggle */
    .mobile-filter-toggle {{
      display: none;
      position: absolute;
      top: 14px;
      left: 14px;
      z-index: 1050;
      background: var(--navy);
      color: #ffffff;
      border: none;
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      font-size: 13px;
      font-weight: 700;
      font-family: inherit;
      box-shadow: var(--shadow-md);
      cursor: pointer;
    }}

    /* =========================================================
       3. SLIDING DETAIL PANEL (RIGHT)
       ========================================================= */
    .detail-panel {{
      position: absolute;
      top: 0;
      right: 0;
      width: 440px;
      height: 100%;
      background: #ffffff;
      box-shadow: -4px 0 25px rgba(0, 0, 0, 0.15);
      border-left: 1px solid var(--border);
      z-index: 1200;
      display: flex;
      flex-direction: column;
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .detail-panel.open {{
      transform: translateX(0);
    }}

    .panel-header {{
      padding: 18px 20px 14px;
      border-bottom: 1px solid var(--border);
      position: relative;
      background: #f8fafc;
    }}

    .panel-close-btn {{
      position: absolute;
      top: 16px;
      right: 16px;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: #ffffff;
      border: 1px solid var(--border);
      color: var(--text-secondary);
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .panel-close-btn:hover {{
      background: #f1f5f9;
      color: var(--text-primary);
    }}

    .panel-header-top {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }}

    .panel-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--navy-dark);
      line-height: 1.25;
      padding-right: 28px;
    }}

    .panel-meta {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* Score Card in Panel Header */
    .panel-score-card {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 14px;
      padding: 12px 14px;
      background: #ffffff;
      border-radius: var(--radius-md);
      border: 1px solid var(--border);
    }}

    .score-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .score-circle {{
      width: 52px;
      height: 52px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 19px;
      font-weight: 800;
      box-shadow: inset 0 2px 4px rgba(0,0,0,0.15);
    }}

    .score-title-wrap {{
      display: flex;
      flex-direction: column;
    }}

    .score-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }}

    .score-tier-badge {{
      display: inline-block;
      font-size: 13px;
      font-weight: 800;
      margin-top: 2px;
    }}

    .incident-flag {{
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    /* Plain Language Summary Box */
    .panel-summary-box {{
      padding: 14px 20px;
      background: #f0fdfa;
      border-bottom: 1px solid #ccfbf1;
      font-size: 13px;
      line-height: 1.55;
      color: #115e59;
      font-weight: 500;
    }}

    /* Action Buttons Row */
    .panel-actions {{
      padding: 12px 20px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      background: #ffffff;
      border-bottom: 1px solid var(--border);
    }}

    .action-btn {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 8px 4px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-family: inherit;
      color: var(--navy);
      font-size: 11px;
      font-weight: 700;
      transition: all 0.15s ease;
    }}

    .action-btn:hover {{
      background: var(--teal-light);
      border-color: var(--teal);
      color: var(--teal-dark);
      transform: translateY(-1px);
    }}

    .action-btn span.icon {{
      font-size: 16px;
    }}

    /* Scrollable Factors List */
    .panel-scroll {{
      flex: 1;
      overflow-y: auto;
      padding: 16px 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .factor-section {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .factor-section-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }}

    .factor-section-title {{
      font-size: 12px;
      font-weight: 800;
      color: var(--navy-dark);
      letter-spacing: 0.04em;
      text-transform: uppercase;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .factor-card {{
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      transition: border-color 0.15s ease;
    }}

    .factor-card:hover {{
      border-color: var(--border-dark);
    }}

    .factor-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}

    .factor-title-wrap {{
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 13px;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .factor-score-pill {{
      font-size: 11px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: var(--radius-full);
      color: #ffffff;
      flex-shrink: 0;
    }}

    .factor-desc {{
      font-size: 12px;
      line-height: 1.5;
      color: var(--text-secondary);
    }}

    .factor-bar-bg {{
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
      margin-top: 2px;
    }}

    .factor-bar-fill {{
      height: 100%;
      border-radius: 3px;
      transition: width 0.3s ease;
    }}

    /* =========================================================
       4. ROUTE CARD (NAVIGATION)
       ========================================================= */
    .route-card {{
      position: absolute;
      top: 16px;
      left: 306px;
      width: 360px;
      background: #ffffff;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-xl);
      border: 1px solid var(--border);
      z-index: 1200;
      display: none;
      flex-direction: column;
      max-height: calc(100% - 32px);
      overflow: hidden;
    }}

    .route-card.active {{
      display: flex;
    }}

    .route-header {{
      padding: 14px 16px;
      background: var(--navy-dark);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .route-header-left {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .route-title {{
      font-size: 13px;
      font-weight: 800;
    }}

    .route-close-btn {{
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 18px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }}

    .route-close-btn:hover {{
      color: #ffffff;
    }}

    .route-summary {{
      padding: 14px 16px;
      background: #f8fafc;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .route-metrics {{
      display: flex;
      gap: 16px;
    }}

    .route-metric {{
      display: flex;
      flex-direction: column;
    }}

    .route-metric-val {{
      font-size: 20px;
      font-weight: 800;
      color: var(--navy);
    }}

    .route-metric-lbl {{
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
    }}

    .route-waypoints {{
      font-size: 11px;
      color: var(--text-secondary);
      line-height: 1.4;
      max-width: 140px;
      text-align: right;
    }}

    .route-notice {{
      padding: 8px 14px;
      background: #fffbeb;
      border-bottom: 1px solid #fef3c7;
      font-size: 11px;
      color: #92400e;
      display: none;
    }}

    .route-steps {{
      overflow-y: auto;
      padding: 12px 16px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .route-step-item {{
      display: flex;
      gap: 10px;
      padding: 6px 0;
      border-bottom: 1px solid #f1f5f9;
      font-size: 12px;
      line-height: 1.4;
    }}

    .step-icon {{
      font-size: 15px;
      color: var(--teal);
      flex-shrink: 0;
      margin-top: 1px;
    }}

    .step-text {{
      flex: 1;
      color: var(--text-primary);
    }}

    .step-dist {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* =========================================================
       5. DASHBOARD VIEW
       ========================================================= */
    #tab-view-dashboard {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      display: none;
      flex-direction: column;
      overflow-y: auto;
      padding: 24px 32px 48px;
      background: var(--paper);
    }}

    .dash-container {{
      max-width: 1280px;
      width: 100%;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}

    .dash-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}

    .dash-heading {{
      font-size: 26px;
      font-weight: 800;
      color: var(--navy-dark);
      letter-spacing: -0.02em;
    }}

    .dash-subheading {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-top: 4px;
    }}

    /* Dashboard Grid of Charts */
    .dash-charts-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}

    .dash-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
    }}

    .dash-card-title {{
      font-size: 14px;
      font-weight: 800;
      color: var(--navy-dark);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    .dash-card-desc {{
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 16px;
    }}

    /* Segmented Bar Widget */
    .segmented-bar-widget {{
      margin-top: 8px;
    }}

    .seg-bar {{
      height: 28px;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      background: #e2e8f0;
      margin-bottom: 16px;
    }}

    .seg-part {{
      height: 100%;
      transition: width 0.3s ease;
      position: relative;
    }}

    .seg-legend {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }}

    .seg-legend-item {{
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
    }}

    .seg-legend-top {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 700;
      margin-bottom: 4px;
    }}

    .seg-legend-val {{
      font-size: 18px;
      font-weight: 800;
      color: var(--text-primary);
    }}

    .seg-legend-pct {{
      font-size: 11px;
      color: var(--text-muted);
      font-weight: 600;
    }}

    /* Locality Ranked Bars */
    .loc-bars-list {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .loc-bar-row {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .loc-bar-label {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .loc-bar-meter {{
      height: 12px;
      background: #e2e8f0;
      border-radius: 6px;
      overflow: hidden;
    }}

    .loc-bar-meter-fill {{
      height: 100%;
      border-radius: 6px;
      transition: width 0.3s ease;
    }}

    /* Top Problems Grid */
    .top-problems-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-top: 8px;
    }}

    .problem-card {{
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 8px;
    }}

    .problem-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .scope-tag {{
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .scope-tag.inside {{
      background: #e0f2fe;
      color: #0369a1;
    }}

    .scope-tag.outside {{
      background: #fef3c7;
      color: #b45309;
    }}

    .problem-name {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.35;
    }}

    .problem-meter {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .problem-pct {{
      font-size: 16px;
      font-weight: 800;
      color: var(--risk-severe);
    }}

    /* Master Table Card */
    .dash-table-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .table-controls {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      background: #f8fafc;
    }}

    .table-controls-left {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      max-width: 500px;
    }}

    .table-wrapper {{
      overflow-x: auto;
      max-height: 520px;
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}

    .data-table th {{
      background: #f1f5f9;
      padding: 12px 16px;
      font-weight: 700;
      color: var(--text-secondary);
      border-bottom: 2px solid var(--border);
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}

    .data-table th:hover {{
      background: #e2e8f0;
    }}

    .data-table td {{
      padding: 10px 16px;
      border-bottom: 1px solid var(--border);
      color: var(--text-primary);
      white-space: nowrap;
    }}

    .data-table tr:hover {{
      background: #f8fafc;
      cursor: pointer;
    }}

    .badge-tier {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: var(--radius-full);
      font-size: 11px;
      font-weight: 700;
      color: #ffffff;
    }}

    .badge-tier.Severe {{ background: var(--risk-severe); }}
    .badge-tier.High {{ background: var(--risk-high); }}
    .badge-tier.Moderate {{ background: var(--risk-moderate); }}
    .badge-tier.Low {{ background: var(--risk-low); }}

    .btn-view-map {{
      background: var(--teal-light);
      border: 1px solid var(--teal);
      color: var(--teal-dark);
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .btn-view-map:hover {{
      background: var(--teal);
      color: #ffffff;
    }}

    /* Leaflet Custom Marker & Popup Styles */
    .leaflet-popup-content-wrapper {{
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      padding: 0;
      overflow: hidden;
    }}

    .leaflet-popup-content {{
      margin: 0 !important;
      line-height: 1.4;
    }}

    .custom-tooltip {{
      background: rgba(15, 23, 42, 0.95) !important;
      color: #ffffff !important;
      border: none !important;
      border-radius: 6px !important;
      padding: 6px 10px !important;
      font-family: var(--font) !important;
      font-size: 12px !important;
      box-shadow: var(--shadow-md) !important;
    }}

    .custom-tooltip::before {{
      border-top-color: rgba(15, 23, 42, 0.95) !important;
    }}

    /* Responsive Queries */
    @media (max-width: 900px) {{
      #login-screen {{
        flex-direction: column;
      }}
      .login-hero {{
        flex: none;
        padding: 32px 24px;
      }}
      .login-form-panel {{
        flex: 1;
        padding: 32px 24px;
      }}
      .hero-title {{
        font-size: 28px;
      }}
      .hero-stats {{
        grid-template-columns: 1fr 1fr;
      }}
      .filter-rail {{
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        transform: translateX(-100%);
      }}
      .filter-rail.open {{
        transform: translateX(0);
      }}
      .mobile-filter-toggle {{
        display: block;
      }}
      .route-card {{
        left: 14px;
        right: 14px;
        width: auto;
      }}
      .detail-panel {{
        width: 100%;
      }}
      .dash-charts-grid {{
        grid-template-columns: 1fr;
      }}
      .top-problems-grid {{
        grid-template-columns: 1fr 1fr;
      }}
      .app-subtitle-badge {{
        display: none;
      }}
    }}
  </style>
</head>
<body>

  <!-- =========================================================
       1. LOGIN SCREEN
       ========================================================= -->
  <div id="login-screen" class="screen active">
    <!-- Left Navy Hero Panel -->
    <div class="login-hero">
      <div class="hero-brand">
        <div class="app-logo-flame">🔥</div>
        <div>
          <h2 style="font-size: 18px; font-weight: 800; letter-spacing: -0.01em;">Seelampur Fire Watch</h2>
          <span class="hero-badge">School of Architecture & Planning • USAP DRR Survey</span>
        </div>
      </div>

      <div class="hero-center">
        <h1 class="hero-title">See which workshops are at risk — and reach them fast</h1>
        <p class="hero-desc">
          A spatial decision-support platform evaluating structural fire vulnerabilities, egress bottlenecks, 
          and emergency access across 158 informal manufacturing workshops surveyed in Seelampur, North-East Delhi.
        </p>

        <!-- Risk Scale Bar -->
        <div class="hero-scale">
          <div class="hero-scale-header">
            <span>COMPOSITE FIRE RISK INDEX (FRI)</span>
            <span>0.00 → 1.00</span>
          </div>
          <div class="scale-bar"></div>
          <div class="scale-labels">
            <span>Low (&lt;0.30)</span>
            <span>Moderate (&lt;0.50)</span>
            <span>High (&lt;0.70)</span>
            <span>Severe (≥0.70)</span>
          </div>
        </div>

        <!-- Key Stats -->
        <div class="hero-stats">
          <div class="stat-pill">
            <div class="stat-pill-val num-tnum">158</div>
            <div class="stat-pill-lbl">Audited Informal Workshops</div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill-val severe num-tnum">114</div>
            <div class="stat-pill-lbl">Severe Risk Bracket (72.2%)</div>
          </div>
          <div class="stat-pill">
            <div class="stat-pill-val num-tnum">4</div>
            <div class="stat-pill-lbl">Informal Localities Mapped</div>
          </div>
        </div>
      </div>

      <div class="hero-footer">
        <span>📍 Survey Area: Seelampur, Gandhi Nagar, Shanti Mohalla & Subhash Nagar</span>
      </div>
    </div>

    <!-- Right Sign-In Form Panel -->
    <div class="login-form-panel">
      <div class="login-box">
        <h2 class="login-heading">Sign In to Fire Watch</h2>
        <p class="login-subheading">Authorised access for urban planners, fire safety officers, and field survey teams.</p>

        <!-- Error Banner -->
        <div id="login-error" class="login-error">
          Invalid email or password. Please use demo password <strong>fire2026</strong> or pick a Quick Sign-in role below.
        </div>

        <!-- Quick Sign-In -->
        <div class="quick-login-section">
          <span class="eyebrow quick-login-title">Quick Sign-in (Demo Roles)</span>
          <div class="quick-roles-grid">
            <button type="button" class="role-btn" onclick="quickLogin('admin@usap.edu')">
              <div class="avatar-initials" style="background:#0e3a5f;">AS</div>
              <div class="role-btn-info">
                <div class="role-btn-name">Admin</div>
                <div class="role-btn-desc">Prof. Amit Sharma</div>
              </div>
            </button>
            <button type="button" class="role-btn" onclick="quickLogin('planner@usap.edu')">
              <div class="avatar-initials" style="background:#0e7490;">NG</div>
              <div class="role-btn-info">
                <div class="role-btn-name">Urban Planner</div>
                <div class="role-btn-desc">Neha Gupta</div>
              </div>
            </button>
            <button type="button" class="role-btn" onclick="quickLogin('fire@usap.edu')">
              <div class="avatar-initials" style="background:#cf3a3a;">RS</div>
              <div class="role-btn-info">
                <div class="role-btn-name">Fire Officer</div>
                <div class="role-btn-desc">Insp. R. K. Singh</div>
              </div>
            </button>
            <button type="button" class="role-btn" onclick="quickLogin('surveyor@usap.edu')">
              <div class="avatar-initials" style="background:#2f9e44;">TA</div>
              <div class="role-btn-info">
                <div class="role-btn-name">Field Surveyor</div>
                <div class="role-btn-desc">Tariq Anjum</div>
              </div>
            </button>
          </div>
        </div>

        <div class="login-divider">
          <span>or sign in with credentials</span>
        </div>

        <!-- Standard Form -->
        <form id="email-login-form" onsubmit="handleFormLogin(event)">
          <div class="form-group">
            <label class="form-label" for="login-email">Email Address</label>
            <input type="email" id="login-email" class="form-input" placeholder="e.g. fire@usap.edu" required value="fire@usap.edu">
          </div>
          <div class="form-group">
            <label class="form-label" for="login-password">Password</label>
            <input type="password" id="login-password" class="form-input" placeholder="Enter password" required value="fire2026">
          </div>
          <button type="submit" class="btn-submit">Sign In to Dashboard →</button>
        </form>

        <div class="demo-notice">
          <strong>Demo Mode:</strong> All roles pre-configured. Use demo password <strong>fire2026</strong>. 
          Production environment verifies against USAP LDAP / Delhi Fire Service directory.
        </div>
      </div>
    </div>
  </div>

  <!-- =========================================================
       2. MAIN APPLICATION SHELL
       ========================================================= -->
  <div id="app-screen" class="screen">
    <!-- Top Navigation Bar -->
    <header class="top-bar">
      <div class="top-bar-left">
        <a href="#" class="app-logo">
          <div class="app-logo-flame">🔥</div>
          <span>Seelampur Fire Watch</span>
        </a>
        <span class="app-subtitle-badge">USAP DRR Survey • North-East Delhi</span>

        <!-- Tab Switcher -->
        <div class="tab-switcher">
          <button type="button" id="tab-btn-map" class="tab-btn active" onclick="switchTab('map')">
            <span>🗺️</span> Map View
          </button>
          <button type="button" id="tab-btn-dashboard" class="tab-btn" onclick="switchTab('dashboard')">
            <span>📊</span> Risk Dashboard
          </button>
        </div>
      </div>

      <div class="top-bar-right">
        <div class="user-profile-pill">
          <div id="top-user-avatar" class="user-avatar">FO</div>
          <div class="user-info">
            <div id="top-user-name" class="user-name">Insp. R. K. Singh</div>
            <div id="top-user-role" class="user-role-tag">Delhi Fire Service (DFS)</div>
          </div>
        </div>
        <button type="button" class="btn-logout" onclick="handleLogout()">Sign Out</button>
      </div>
    </header>

    <div class="main-body">
      <!-- =======================================================
           VIEW A: MAP VIEW
           ======================================================= -->
      <div id="tab-view-map">
        <!-- KPI Strip -->
        <div class="kpi-strip">
          <div class="kpi-card">
            <span class="kpi-icon">🏭</span>
            <div class="kpi-data">
              <span id="kpi-count" class="kpi-val num-tnum">158 / 158</span>
              <span class="kpi-lbl">Workshops Shown</span>
            </div>
          </div>

          <div class="kpi-card">
            <span class="kpi-icon">📈</span>
            <div class="kpi-data">
              <span id="kpi-mean-fri" class="kpi-val num-tnum">0.74</span>
              <span class="kpi-lbl">Average Risk</span>
            </div>
          </div>

          <div class="kpi-card">
            <span class="kpi-icon">🚨</span>
            <div class="kpi-data">
              <span id="kpi-severe" class="kpi-val severe num-tnum">114 (72.2%)</span>
              <span class="kpi-lbl">Severe Risk Tier</span>
            </div>
          </div>

          <div class="kpi-card">
            <span class="kpi-icon">📍</span>
            <div class="kpi-data">
              <span id="kpi-worst-area" class="kpi-val num-tnum">Shanti Mohalla (0.82)</span>
              <span class="kpi-lbl">Riskiest Area</span>
            </div>
          </div>

          <div class="kpi-card">
            <span class="kpi-icon">🔥</span>
            <div class="kpi-data">
              <span id="kpi-incidents" class="kpi-val num-tnum">41</span>
              <span class="kpi-lbl">Had Past Fire</span>
            </div>
          </div>
        </div>

        <!-- Map Workspace Area -->
        <div class="map-workspace">
          <!-- Mobile Drawer Toggle Button -->
          <button type="button" class="mobile-filter-toggle" onclick="toggleFilterRail()">
            ☰ Filters &amp; Layers
          </button>

          <!-- Left Filter Rail -->
          <aside id="filter-rail" class="filter-rail">
            <div class="rail-header">
              <span class="rail-title">Filters &amp; Layers</span>
              <button type="button" class="rail-reset-btn" onclick="resetFilters()">Reset All</button>
            </div>

            <div class="rail-content">
              <!-- Search Box -->
              <div class="filter-group">
                <span class="filter-group-title">Search Workshops</span>
                <div class="search-box">
                  <input type="text" id="filter-search" class="search-input" placeholder="Name, ID (SW-...) or work type..." oninput="handleSearchInput(this.value)">
                  <button type="button" id="search-clear-btn" class="search-clear" onclick="clearSearch()">✕</button>
                </div>
              </div>

              <!-- Risk Level Tiers -->
              <div class="filter-group">
                <span class="filter-group-title">Risk Level</span>
                <div class="tier-checkboxes">
                  <label class="tier-check-item">
                    <div class="tier-check-left">
                      <input type="checkbox" id="check-severe" checked onchange="handleFilterChange()">
                      <span class="tier-color-dot" style="background:var(--risk-severe);"></span>
                      <span>Severe Risk</span>
                    </div>
                    <span id="tier-count-severe" class="tier-count-chip num-tnum">114</span>
                  </label>

                  <label class="tier-check-item">
                    <div class="tier-check-left">
                      <input type="checkbox" id="check-high" checked onchange="handleFilterChange()">
                      <span class="tier-color-dot" style="background:var(--risk-high);"></span>
                      <span>High Risk</span>
                    </div>
                    <span id="tier-count-high" class="tier-count-chip num-tnum">34</span>
                  </label>

                  <label class="tier-check-item">
                    <div class="tier-check-left">
                      <input type="checkbox" id="check-moderate" checked onchange="handleFilterChange()">
                      <span class="tier-color-dot" style="background:var(--risk-moderate);"></span>
                      <span>Moderate Risk</span>
                    </div>
                    <span id="tier-count-moderate" class="tier-count-chip num-tnum">6</span>
                  </label>

                  <label class="tier-check-item">
                    <div class="tier-check-left">
                      <input type="checkbox" id="check-low" checked onchange="handleFilterChange()">
                      <span class="tier-color-dot" style="background:var(--risk-low);"></span>
                      <span>Low Risk</span>
                    </div>
                    <span id="tier-count-low" class="tier-count-chip num-tnum">4</span>
                  </label>
                </div>
              </div>

              <!-- Locality Filter -->
              <div class="filter-group">
                <span class="filter-group-title">Survey Locality</span>
                <select id="filter-locality" class="locality-select" onchange="handleLocalityChange(this.value)">
                  <option value="ALL">All Localities (158 workshops)</option>
                  <option value="Shanti Mohalla">Shanti Mohalla (38 • Avg 0.82)</option>
                  <option value="Seelampur">Seelampur (48 • Avg 0.78)</option>
                  <option value="Gandhi Nagar">Gandhi Nagar (42 • Avg 0.76)</option>
                  <option value="Subhash Nagar">Subhash Nagar (30 • Avg 0.54)</option>
                </select>
              </div>

              <!-- Base Map Selector -->
              <div class="filter-group">
                <span class="filter-group-title">Base Map Style</span>
                <div class="segmented-control">
                  <button type="button" id="tile-osm" class="segment-btn active" onclick="setBaseTile('osm')">Street</button>
                  <button type="button" id="tile-satellite" class="segment-btn" onclick="setBaseTile('satellite')">Satellite</button>
                  <button type="button" id="tile-light" class="segment-btn" onclick="setBaseTile('light')">Light</button>
                </div>
              </div>

              <!-- Layer Toggles -->
              <div class="filter-group">
                <span class="filter-group-title">Map Layers</span>
                <div class="layer-switches">
                  <div class="layer-switch-row">
                    <span>🔥 Risk Heat Map</span>
                    <label class="toggle-switch">
                      <input type="checkbox" id="toggle-heat" checked onchange="toggleHeatLayer(this.checked)">
                      <span class="slider"></span>
                    </label>
                  </div>

                  <div class="layer-switch-row">
                    <span>🚒 Fire Stations</span>
                    <label class="toggle-switch">
                      <input type="checkbox" id="toggle-firestations" checked onchange="toggleFireStations(this.checked)">
                      <span class="slider"></span>
                    </label>
                  </div>

                  <div class="layer-switch-row">
                    <span>🏥 Hospitals</span>
                    <label class="toggle-switch">
                      <input type="checkbox" id="toggle-hospitals" checked onchange="toggleHospitals(this.checked)">
                      <span class="slider"></span>
                    </label>
                  </div>

                  <div class="layer-switch-row">
                    <span>⚠️ Past-Fire Markers</span>
                    <label class="toggle-switch">
                      <input type="checkbox" id="toggle-pastfire" onchange="togglePastFireMarkers(this.checked)">
                      <span class="slider"></span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Location Button -->
              <button type="button" class="btn-locate" onclick="getUserLocation()">
                <span>📍</span> Show Where I Am
              </button>
            </div>
          </aside>

          <!-- Center Map -->
          <div id="map-container">
            <!-- Map Legend (Bottom Left) -->
            <div class="map-legend">
              <div class="legend-title">
                <span>🔥 Fire Risk Scale</span>
              </div>
              <div class="legend-tiers">
                <div class="legend-item"><span class="legend-dot" style="background:var(--risk-severe);"></span> Severe (≥0.70)</div>
                <div class="legend-item"><span class="legend-dot" style="background:var(--risk-high);"></span> High (0.50–0.69)</div>
                <div class="legend-item"><span class="legend-dot" style="background:var(--risk-moderate);"></span> Moderate (0.30–0.49)</div>
                <div class="legend-item"><span class="legend-dot" style="background:var(--risk-low);"></span> Low (&lt;0.30)</div>
              </div>
              <div class="legend-disclaimer">
                ⚠️ Workshop positions are approximate within each locality — the survey has no GPS points yet.
              </div>
            </div>

            <!-- Floating Route Navigation Card -->
            <div id="route-card" class="route-card">
              <div class="route-header">
                <div class="route-header-left">
                  <span id="route-type-icon">🚒</span>
                  <span id="route-title" class="route-title">Emergency Fire Route</span>
                </div>
                <button type="button" class="route-close-btn" onclick="clearNavigationRoute()" title="Close route">✕</button>
              </div>

              <div class="route-summary">
                <div class="route-metrics">
                  <div class="route-metric">
                    <span id="route-time" class="route-metric-val num-tnum">-- min</span>
                    <span class="route-metric-lbl">Drive Time</span>
                  </div>
                  <div class="route-metric">
                    <span id="route-dist" class="route-metric-val num-tnum">-- km</span>
                    <span class="route-metric-lbl">Distance</span>
                  </div>
                </div>
                <div id="route-waypoints" class="route-waypoints">
                  From: Station<br>To: Workshop
                </div>
              </div>

              <div id="route-fallback-notice" class="route-notice">
                ⚠️ Live road routing service unreachable — estimated straight-line trajectory shown.
              </div>

              <div id="route-steps" class="route-steps">
                <!-- Turn by turn steps injected here -->
              </div>
            </div>

            <!-- Sliding Detail Panel -->
            <aside id="detail-panel" class="detail-panel">
              <div class="panel-header">
                <button type="button" class="panel-close-btn" onclick="closeDetailPanel()" title="Close details">✕</button>
                <div class="panel-header-top">
                  <span id="panel-eyebrow" class="eyebrow">USAP AUDITED WORKSHOP</span>
                  <span id="panel-incident-badge" class="incident-flag" style="display:none;">🔥 Past Fire</span>
                </div>
                <h3 id="panel-name" class="panel-title">Al-Madina Denim Washing Unit</h3>
                <div id="panel-meta" class="panel-meta">Seelampur • Block C Gali 3 • ID: SW-001</div>

                <!-- Big Score Card -->
                <div class="panel-score-card">
                  <div class="score-left">
                    <div id="panel-score-circle" class="score-circle num-tnum">0.84</div>
                    <div class="score-title-wrap">
                      <span class="score-title">Fire Risk Index (FRI)</span>
                      <span id="panel-tier-badge" class="score-tier-badge">Severe Risk</span>
                    </div>
                  </div>
                  <div id="panel-work-type" class="badge-tier High" style="background:#475569;">Denim Processing</div>
                </div>
              </div>

              <!-- Plain Language Dynamic Summary -->
              <div id="panel-summary" class="panel-summary-box">
                This workshop is at severe fire risk. The biggest problems are only one way out, an obstructed escape path, and road inaccessible for fire trucks.
              </div>

              <!-- Action Buttons -->
              <div class="panel-actions">
                <button type="button" class="action-btn" onclick="routeFromNearestFireStation()">
                  <span class="icon">🚒</span>
                  <span>Fire Route</span>
                </button>
                <button type="button" class="action-btn" onclick="routeFromUserLocation()">
                  <span class="icon">📍</span>
                  <span>From Me</span>
                </button>
                <button type="button" class="action-btn" onclick="routeToNearestHospital()">
                  <span class="icon">🏥</span>
                  <span>To Hospital</span>
                </button>
                <button type="button" class="action-btn" onclick="zoomToSelectedWorkshop()">
                  <span class="icon">🔍</span>
                  <span>Zoom In</span>
                </button>
              </div>

              <!-- Scrollable Factors Section -->
              <div class="panel-scroll">
                <!-- Inside Building -->
                <div class="factor-section">
                  <div class="factor-section-header">
                    <span class="factor-section-title">🏢 Inside the Building (Egress Factors)</span>
                    <span class="eyebrow">Worst First</span>
                  </div>
                  <div id="panel-inside-factors" class="factor-list">
                    <!-- Injected via JS -->
                  </div>
                </div>

                <!-- Outside & Around -->
                <div class="factor-section">
                  <div class="factor-section-header">
                    <span class="factor-section-title">🧱 Outside &amp; Around (Hazard &amp; Access)</span>
                    <span class="eyebrow">Worst First</span>
                  </div>
                  <div id="panel-outside-factors" class="factor-list">
                    <!-- Injected via JS -->
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>

      <!-- =======================================================
           VIEW B: DASHBOARD VIEW
           ======================================================= -->
      <div id="tab-view-dashboard">
        <div class="dash-container">
          <div class="dash-header">
            <div>
              <span class="eyebrow">Aggregate Disaster Risk Assessment</span>
              <h2 class="dash-heading">Seelampur Vulnerability Dashboard</h2>
              <p class="dash-subheading">Analytical cross-section of all 158 surveyed informal production enterprises.</p>
            </div>
            <button type="button" class="btn-locate" onclick="switchTab('map')">
              <span>🗺️</span> Return to Map View
            </button>
          </div>

          <!-- Charts Grid -->
          <div class="dash-charts-grid">
            <!-- Chart 1: Segmented Risk Bar -->
            <div class="dash-card">
              <h3 class="dash-card-title"><span>📊</span> Workshop Risk Tier Distribution</h3>
              <p class="dash-card-desc">Proportion of surveyed units classified by composite Fire Risk Index (FRI).</p>

              <div class="segmented-bar-widget">
                <div class="seg-bar">
                  <div id="seg-severe" class="seg-part" style="width: 72.2%; background: var(--risk-severe);" title="Severe: 72.2%"></div>
                  <div id="seg-high" class="seg-part" style="width: 21.5%; background: var(--risk-high);" title="High: 21.5%"></div>
                  <div id="seg-mod" class="seg-part" style="width: 3.8%; background: var(--risk-moderate);" title="Moderate: 3.8%"></div>
                  <div id="seg-low" class="seg-part" style="width: 2.5%; background: var(--risk-low);" title="Low: 2.5%"></div>
                </div>

                <div class="seg-legend">
                  <div class="seg-legend-item">
                    <div class="seg-legend-top" style="color:var(--risk-severe);">
                      <span class="tier-color-dot" style="background:var(--risk-severe);"></span> Severe
                    </div>
                    <div id="dash-count-severe" class="seg-legend-val num-tnum">114</div>
                    <div id="dash-pct-severe" class="seg-legend-pct num-tnum">72.2%</div>
                  </div>

                  <div class="seg-legend-item">
                    <div class="seg-legend-top" style="color:var(--risk-high);">
                      <span class="tier-color-dot" style="background:var(--risk-high);"></span> High
                    </div>
                    <div id="dash-count-high" class="seg-legend-val num-tnum">34</div>
                    <div id="dash-pct-high" class="seg-legend-pct num-tnum">21.5%</div>
                  </div>

                  <div class="seg-legend-item">
                    <div class="seg-legend-top" style="color:var(--risk-moderate);">
                      <span class="tier-color-dot" style="background:var(--risk-moderate);"></span> Moderate
                    </div>
                    <div id="dash-count-mod" class="seg-legend-val num-tnum">6</div>
                    <div id="dash-pct-mod" class="seg-legend-pct num-tnum">3.8%</div>
                  </div>

                  <div class="seg-legend-item">
                    <div class="seg-legend-top" style="color:var(--risk-low);">
                      <span class="tier-color-dot" style="background:var(--risk-low);"></span> Low
                    </div>
                    <div id="dash-count-low" class="seg-legend-val num-tnum">4</div>
                    <div id="dash-pct-low" class="seg-legend-pct num-tnum">2.5%</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Chart 2: Average Risk by Locality -->
            <div class="dash-card">
              <h3 class="dash-card-title"><span>🏘️</span> Average Risk by Locality</h3>
              <p class="dash-card-desc">Ranked comparison of composite risk scores across the 4 surveyed zones.</p>

              <div id="dash-loc-bars" class="loc-bars-list">
                <!-- Injected via JS -->
              </div>
            </div>
          </div>

          <!-- Chart 3: Top 8 Area-Wide Problems -->
          <div class="dash-card">
            <h3 class="dash-card-title"><span>🚨</span> Biggest Problems Across Seelampur</h3>
            <p class="dash-card-desc">Settlement-wide critical failure points affecting the greatest percentage of workshops.</p>

            <div id="top-problems-grid" class="top-problems-grid">
              <!-- Injected via JS -->
            </div>
          </div>

          <!-- Master Sortable Table -->
          <div class="dash-table-card">
            <div class="table-controls">
              <div class="table-controls-left">
                <input type="text" id="dash-table-search" class="search-input" placeholder="Filter table by workshop, trade, or ID..." oninput="handleDashTableFilter()">
                <select id="dash-table-loc" class="locality-select" onchange="handleDashTableFilter()" style="max-width:180px;">
                  <option value="ALL">All Localities</option>
                  <option value="Shanti Mohalla">Shanti Mohalla</option>
                  <option value="Seelampur">Seelampur</option>
                  <option value="Gandhi Nagar">Gandhi Nagar</option>
                  <option value="Subhash Nagar">Subhash Nagar</option>
                </select>
              </div>
              <div style="font-size:12px; color:var(--text-muted); font-weight:600;">
                Click any row to inspect &amp; navigate on the map
              </div>
            </div>

            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th onclick="sortTable('id')">ID ↕</th>
                    <th onclick="sortTable('ent')">Workshop Name ↕</th>
                    <th onclick="sortTable('loc')">Locality ↕</th>
                    <th onclick="sortTable('work')">Work Type ↕</th>
                    <th onclick="sortTable('incident')">Past Fire ↕</th>
                    <th onclick="sortTable('fri')">Risk Score ↕</th>
                    <th onclick="sortTable('tier')">Risk Tier ↕</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody id="dash-table-body">
                  <!-- Injected via JS -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Leaflet JS & Leaflet Heat -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>

  <!-- Embedded Application Logic -->
  <script>
    // Embedded Data Constants
    const WORKSHOPS_DATA = {workshops_json};
    const SCORING_MAP = {scoring_map_json};

    // Emergency Facilities
    const FIRE_STATIONS = [
      {{ id: 'FS1', name: 'Shastri Park Fire Station', desc: 'Delhi Fire Service (HQ Division)', lat: 28.6655, lng: 77.2562 }},
      {{ id: 'FS2', name: 'Geeta Colony Fire Station', desc: 'East Delhi Fast Response Unit', lat: 28.6480, lng: 77.2680 }},
      {{ id: 'FS3', name: 'Shahdara Fire Station', desc: 'North East Sub-Station', lat: 28.6738, lng: 77.2910 }}
    ];

    const HOSPITALS = [
      {{ id: 'H1', name: 'Jag Pravesh Chandra Hospital', desc: 'Govt. Multi-Speciality (Shastri Park)', lat: 28.6672, lng: 77.2588 }},
      {{ id: 'H2', name: 'Swami Dayanand Hospital (SDN)', desc: 'Municipal General Hospital (Shahdara)', lat: 28.6750, lng: 77.2950 }},
      {{ id: 'H3', name: 'GTB Hospital & UCMS', desc: 'Tertiary Trauma & Burns Center', lat: 28.6835, lng: 77.3110 }}
    ];

    // Locality Centers for bounding fits
    const LOCALITY_CENTERS = {{
      'Seelampur': [28.6705, 77.2700],
      'Gandhi Nagar': [28.6590, 77.2665],
      'Shanti Mohalla': [28.6648, 77.2768],
      'Subhash Nagar': [28.6762, 77.2780]
    }};

    // Demo Users
    const DEMO_USERS = {{
      'admin@usap.edu': {{ name: 'Prof. Amit Sharma', role: 'Lead Planning Admin', initials: 'AS', color: '#0e3a5f' }},
      'planner@usap.edu': {{ name: 'Neha Gupta', role: 'Urban Risk Planner', initials: 'NG', color: '#0e7490' }},
      'fire@usap.edu': {{ name: 'Insp. R. K. Singh', role: 'Delhi Fire Service (DFS)', initials: 'RS', color: '#cf3a3a' }},
      'surveyor@usap.edu': {{ name: 'Tariq Anjum', role: 'Field Surveyor', initials: 'TA', color: '#2f9e44' }}
    }};

    // Factor Layman Explanations & Emojis
    const FACTOR_INFO = {{
      'exits': {{
        name: 'Exit Routes',
        emoji: '🚪',
        scope: 'inside',
        desc: {{
          '1 exit': 'Only one way out. If that exit is blocked by fire or smoke, people inside are trapped.',
          '2 exits': 'Two exits exist, but both lead into the same corridor.',
          '3+ exits': 'Multiple independent exit routes provide safe escape alternatives.'
        }}
      }},
      'obstruction': {{
        name: 'Obstruction-Free Evacuation',
        emoji: '📦',
        scope: 'inside',
        desc: {{
          'obstructed': 'Corridors and doorways are clogged with fabric bales and raw materials.',
          'partially_clear': 'Passageways have loose boxes and equipment slowing rapid movement.',
          'clear': 'Clear, completely unobstructed escape paths to the street.'
        }}
      }},
      'emergency_exits': {{
        name: 'Functional Emergency Exits',
        emoji: '🚨',
        scope: 'inside',
        desc: {{
          'none': 'No working emergency exit or secondary escape stairs exist.',
          'locked_or_blocked': 'An emergency door exists but is padlocked or buried behind inventory.',
          'functional': 'Clearly marked, unlocked emergency exit leads to safety.'
        }}
      }},
      'staircase_width': {{
        name: 'Staircase Width',
        emoji: '🪜',
        scope: 'inside',
        desc: {{
          'under_0_8m': 'Staircase is dangerously narrow (under 0.8m) — workers can only descend single file.',
          '0_8_to_1_2m': 'Moderate stair width (0.8–1.2m) prone to crushing bottlenecks in panic.',
          'over_1_2m': 'Wide staircase (over 1.2m) allows fast two-abreast evacuation.'
        }}
      }},
      'workspace': {{
        name: 'Workspace Size & Density',
        emoji: '📐',
        scope: 'inside',
        desc: {{
          'under_200sqft': 'Extremely cramped floor (under 200 sq ft) crammed with sewing machines and workers.',
          '200_to_500sqft': 'Compact floor area (200–500 sq ft) with restricted movement between rows.',
          'over_500sqft': 'Spacious layout (over 500 sq ft) with ample space between machines.'
        }}
      }},
      'floors': {{
        name: 'Vertical Floor Delay',
        emoji: '🏢',
        scope: 'inside',
        desc: {{
          'g_plus_3_or_more': 'High-rise informal unit (G+3 or more) — upper floors face lethal smoke rise delays.',
          'g_plus_2': 'Three-level building (G+2) with delayed descent time during a blaze.',
          'g_plus_1': 'Two levels (G+1) with relatively rapid access to ground level.',
          'ground_only': 'Ground floor only — direct step-out access to the lane.'
        }}
      }},
      'light': {{
        name: 'Natural Light & Smoke Venting',
        emoji: '💡',
        scope: 'inside',
        desc: {{
          'dark_no_vent': 'No natural ventilation or skylights — toxic combustion gases and smoke stay trapped.',
          'dim_partial': 'Small high vents provide only slight dissipation of hot smoke.',
          'well_lit': 'Good natural cross-ventilation shafts allow toxic fumes to vent.'
        }}
      }},
      'windows': {{
        name: 'Windows & Rescue Access',
        emoji: '🪟',
        scope: 'inside',
        desc: {{
          'no_windows_or_barred': 'Windows are absent or heavily welded with iron bars, preventing firefighter ladder rescue.',
          'few_restricted': 'Few small window openings restrict hose streams and ventilation.',
          'operable_clear': 'Openable windows facing the lane provide direct rescue access.'
        }}
      }},
      'corridor': {{
        name: 'Internal Corridor Width',
        emoji: '🚶',
        scope: 'inside',
        desc: {{
          'under_1m_cluttered': 'Internal hallway is under 1m wide and lined with scrap, making crawling in smoke perilous.',
          '1_to_1_5m': 'Corridor width is 1.0–1.5m, adequate for walking but tight under panic.',
          'wide_clear': 'Wide corridor exceeding 1.5m allows unhindered emergency passage.'
        }}
      }},
      'dust': {{
        name: 'Combustible Dust & Lint',
        emoji: '💨',
        scope: 'inside',
        desc: {{
          'heavy_flammable_lint': 'Air is thick with combustible textile lint and fluff that can flash-ignite into a fireball.',
          'moderate_dust': 'Noticeable fiber dust settling on machinery and electrical fittings.',
          'low_dust': 'Clean atmosphere with wet processing and minimal airborne fibers.'
        }}
      }},
      'building_gap': {{
        name: 'Gap to Neighbouring Buildings',
        emoji: '🧱',
        scope: 'outside',
        desc: {{
          'shared_wall_0m': 'Building touches its neighbours — a fire will conduct and burn right through adjoining structures.',
          'narrow_gap_under_1m': 'Less than 1m separation — radiant heat can easily ignite adjoining roofs.',
          'gap_over_1m': 'Clear thermal gap exceeding 1m prevents rapid flame transmission.'
        }}
      }},
      'waste_burning': {{
        name: 'Waste Burning Nearby',
        emoji: '🔥',
        scope: 'outside',
        desc: {{
          'daily_open_burning': 'Frequent burning of scrap fabric and plastic in the street throws live embers toward the workshop.',
          'occasional_burning': 'Sporadic trash fires in the lane pose occasional ember hazards.',
          'none': 'No open trash or scrap burning observed in the immediate street.'
        }}
      }},
      'station_dist': {{
        name: 'Distance to Fire Station',
        emoji: '🚒',
        scope: 'outside',
        desc: {{
          'over_3km': 'Over 3 km from the nearest fire station — heavy congestion on GT Road multiplies response delay.',
          '1_5_to_3km': '1.5–3.0 km from the fire brigade, requiring 15–20 minutes through crowded market streets.',
          'under_1_5km': 'Under 1.5 km from a fire station for quick initial turnout.'
        }}
      }},
      'response_time': {{
        name: 'Estimated Brigade Response Time',
        emoji: '⏱️',
        scope: 'outside',
        desc: {{
          'over_25min': 'Response time exceeds 25 minutes — flashover occurs before water tenders arrive.',
          '15_to_25min': 'Response delay is 15–25 minutes, meaning flames have spread to adjacent floors.',
          'under_15min': 'Response time is under 15 minutes, allowing early interior attack.'
        }}
      }},
      'approach_road': {{
        name: 'Road Access for Fire Truck',
        emoji: '🛣️',
        scope: 'outside',
        desc: {{
          'narrow_under_2_5m': 'No direct road — a fire truck cannot reach the door, crews must run hoses through narrow lanes.',
          'medium_2_5_to_4m': 'Tight 2.5–4m lane allows only small quick-response motorcycles or mini-tenders.',
          'wide_over_4m': 'Wide thoroughfare over 4m allows full hydraulic tenders direct frontage.'
        }}
      }}
    }};

    // State
    let currentUser = null;
    let activeTab = 'map';
    let map = null;
    let baseLayers = {{}};
    let currentTile = 'osm';
    let workshopMarkers = [];
    let heatLayer = null;
    let fireStationLayer = null;
    let hospitalLayer = null;
    let pastFireLayer = null;
    let userLocationMarker = null;
    let currentRouteLayers = [];
    let selectedWorkshop = null;
    let tableSortCol = 'fri';
    let tableSortAsc = false;

    // Session helpers
    function getStoredSession() {{
      try {{
        const raw = sessionStorage.getItem('seelampur_user');
        return raw ? JSON.parse(raw) : null;
      }} catch (e) {{
        return null;
      }}
    }}

    function storeSession(user) {{
      try {{
        if (user) sessionStorage.setItem('seelampur_user', JSON.stringify(user));
        else sessionStorage.removeItem('seelampur_user');
      }} catch (e) {{}}
    }}

    // App Initialization
    window.addEventListener('DOMContentLoaded', () => {{
      const session = getStoredSession();
      if (session) {{
        currentUser = session;
        showApp();
      }} else {{
        showLogin();
      }}
    }});

    function showLogin() {{
      document.getElementById('login-screen').classList.add('active');
      document.getElementById('app-screen').classList.remove('active');
    }}

    function showApp() {{
      document.getElementById('login-screen').classList.remove('active');
      document.getElementById('app-screen').classList.add('active');
      
      // Update User in Topbar
      if (currentUser) {{
        document.getElementById('top-user-name').textContent = currentUser.name;
        document.getElementById('top-user-role').textContent = currentUser.role;
        document.getElementById('top-user-avatar').textContent = currentUser.initials;
        document.getElementById('top-user-avatar').style.backgroundColor = currentUser.color;
      }}

      // Init Map on next tick
      setTimeout(() => {{
        if (!map) initMap();
        applyFilters();
        renderDashboard();
      }}, 50);
    }}

    function quickLogin(email) {{
      const user = DEMO_USERS[email];
      if (user) {{
        currentUser = user;
        storeSession(user);
        showApp();
      }}
    }}

    function handleFormLogin(e) {{
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const pwd = document.getElementById('login-password').value;
      const err = document.getElementById('login-error');

      if (pwd === 'fire2026') {{
        err.style.display = 'none';
        const user = DEMO_USERS[email] || {{
          name: email.split('@')[0],
          role: 'Field Analyst',
          initials: email.substring(0, 2).toUpperCase(),
          color: '#0e7490'
        }};
        currentUser = user;
        storeSession(user);
        showApp();
      }} else {{
        err.style.display = 'block';
      }}
    }}

    function handleLogout() {{
      storeSession(null);
      currentUser = null;
      if (map) {{
        clearNavigationRoute();
        closeDetailPanel();
      }}
      showLogin();
    }}

    // Tab Navigation
    function switchTab(tab) {{
      activeTab = tab;
      const mapBtn = document.getElementById('tab-btn-map');
      const dashBtn = document.getElementById('tab-btn-dashboard');
      const mapView = document.getElementById('tab-view-map');
      const dashView = document.getElementById('tab-view-dashboard');

      if (tab === 'map') {{
        mapBtn.classList.add('active');
        dashBtn.classList.remove('active');
        mapView.style.display = 'flex';
        dashView.style.display = 'none';
        if (map) {{
          setTimeout(() => map.invalidateSize(), 100);
        }}
      }} else {{
        mapBtn.classList.remove('active');
        dashBtn.classList.add('active');
        mapView.style.display = 'none';
        dashView.style.display = 'flex';
        renderDashboard();
      }}
    }}

    // =========================================================
    // MAP LOGIC
    // =========================================================
    function initMap() {{
      map = L.map('map-container', {{
        center: [28.6675, 77.2715],
        zoom: 15,
        zoomControl: true,
        attributionControl: true
      }});

      // Move zoom controls to top-right
      map.zoomControl.setPosition('topright');

      // Tile layers
      baseLayers.osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
      }});

      baseLayers.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        attribution: 'Tiles &copy; Esri, Earthstar Geographics',
        maxZoom: 19
      }});

      baseLayers.light = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; CARTO &copy; OpenStreetMap',
        maxZoom: 19
      }});

      baseLayers.osm.addTo(map);

      // Emergency Services Layer
      buildEmergencyFacilityLayers();

      // Keyboard escape to close panel
      document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') {{
          closeDetailPanel();
          clearNavigationRoute();
        }}
      }});
    }}

    function setBaseTile(type) {{
      currentTile = type;
      ['osm', 'satellite', 'light'].forEach(t => {{
        document.getElementById('tile-' + t).classList.toggle('active', t === type);
        if (map.hasLayer(baseLayers[t])) map.removeLayer(baseLayers[t]);
      }});
      baseLayers[type].addTo(map);
    }}

    function getTierColor(tier) {{
      switch (tier) {{
        case 'Severe': return '#cf3a3a';
        case 'High': return '#e2683c';
        case 'Moderate': return '#d9932a';
        case 'Low': return '#2f9e44';
        default: return '#64748b';
      }}
    }}

    function buildEmergencyFacilityLayers() {{
      // Fire Stations Layer
      const fsMarkers = FIRE_STATIONS.map(fs => {{
        const icon = L.divIcon({{
          className: 'emergency-icon-fs',
          html: `<div style="background:#b91c1c; color:#fff; border:2px solid #fff; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-size:16px; box-shadow:0 3px 8px rgba(0,0,0,0.3);">🚒</div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        }});
        const m = L.marker([fs.lat, fs.lng], {{ icon }});
        m.bindPopup(`
          <div style="padding:10px 14px; min-width:200px;">
            <div style="font-size:11px; font-weight:700; color:#b91c1c; text-transform:uppercase;">DELHI FIRE SERVICE</div>
            <div style="font-size:14px; font-weight:800; margin:2px 0 4px; color:#0f172a;">${{fs.name}}</div>
            <div style="font-size:12px; color:#64748b;">${{fs.desc}}</div>
          </div>
        `);
        return m;
      }});
      fireStationLayer = L.layerGroup(fsMarkers).addTo(map);

      // Hospitals Layer
      const hMarkers = HOSPITALS.map(h => {{
        const icon = L.divIcon({{
          className: 'emergency-icon-h',
          html: `<div style="background:#0284c7; color:#fff; border:2px solid #fff; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-size:16px; box-shadow:0 3px 8px rgba(0,0,0,0.3);">🏥</div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        }});
        const m = L.marker([h.lat, h.lng], {{ icon }});
        m.bindPopup(`
          <div style="padding:10px 14px; min-width:200px;">
            <div style="font-size:11px; font-weight:700; color:#0284c7; text-transform:uppercase;">EMERGENCY HEALTHCARE</div>
            <div style="font-size:14px; font-weight:800; margin:2px 0 4px; color:#0f172a;">${{h.name}}</div>
            <div style="font-size:12px; color:#64748b;">${{h.desc}}</div>
          </div>
        `);
        return m;
      }});
      hospitalLayer = L.layerGroup(hMarkers).addTo(map);
    }}

    // Filter Processing & Rendering
    function applyFilters() {{
      const query = (document.getElementById('filter-search').value || '').trim().toLowerCase();
      const loc = document.getElementById('filter-locality').value;
      const showSevere = document.getElementById('check-severe').checked;
      const showHigh = document.getElementById('check-high').checked;
      const showMod = document.getElementById('check-moderate').checked;
      const showLow = document.getElementById('check-low').checked;

      const filtered = WORKSHOPS_DATA.filter(w => {{
        // Locality
        if (loc !== 'ALL' && w.loc !== loc) return false;
        // Tier
        if (w.tier === 'Severe' && !showSevere) return false;
        if (w.tier === 'High' && !showHigh) return false;
        if (w.tier === 'Moderate' && !showMod) return false;
        if (w.tier === 'Low' && !showLow) return false;
        // Text Query
        if (query) {{
          const match = w.ent.toLowerCase().includes(query) ||
                        w.id.toLowerCase().includes(query) ||
                        w.work.toLowerCase().includes(query) ||
                        w.area.toLowerCase().includes(query);
          if (!match) return false;
        }}
        return true;
      }});

      renderMapMarkers(filtered);
      updateKPIStrip(filtered);
      updateHeatLayer(filtered);
      updatePastFireMarkers(filtered);
    }}

    function renderMapMarkers(workshops) {{
      // Remove existing workshop markers
      workshopMarkers.forEach(m => map.removeLayer(m));
      workshopMarkers = [];

      workshops.forEach(w => {{
        const color = getTierColor(w.tier);
        const marker = L.circleMarker([w.lat, w.lng], {{
          radius: 8,
          fillColor: color,
          color: '#ffffff',
          weight: 2,
          opacity: 0.95,
          fillOpacity: 0.9
        }});

        // Tooltip on Hover
        marker.bindTooltip(`
          <div style="line-height:1.35; padding:2px;">
            <div style="font-weight:800; font-size:12px;">${{w.ent}}</div>
            <div style="font-size:11px; color:#cbd5e1;">${{w.loc}} • ${{w.work}}</div>
            <div style="margin-top:4px; display:flex; align-items:center; gap:6px;">
              <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${{color}};"></span>
              <strong style="font-size:11px; color:#fff;">${{w.tier}} (${{w.fri.toFixed(2)}})</strong>
              ${{w.incident ? '<span style="font-size:10px; color:#fca5a5;">🔥 Past Fire</span>' : ''}}
            </div>
          </div>
        `, {{
          className: 'custom-tooltip',
          direction: 'top',
          offset: [0, -6]
        }});

        marker.on('click', () => {{
          openDetailPanel(w);
        }});

        marker.addTo(map);
        workshopMarkers.push(marker);
      }});
    }}

    function updateKPIStrip(filtered) {{
      const total = WORKSHOPS_DATA.length;
      const count = filtered.length;
      document.getElementById('kpi-count').textContent = `${{count}} / ${{total}}`;

      if (count === 0) {{
        document.getElementById('kpi-mean-fri').textContent = '0.00';
        document.getElementById('kpi-severe').textContent = '0 (0.0%)';
        document.getElementById('kpi-worst-area').textContent = 'None';
        document.getElementById('kpi-incidents').textContent = '0';
        return;
      }}

      // Mean FRI
      const sumFri = filtered.reduce((acc, w) => acc + w.fri, 0);
      const meanFri = (sumFri / count).toFixed(2);
      document.getElementById('kpi-mean-fri').textContent = meanFri;

      // Severe Count & %
      const severeCount = filtered.filter(w => w.tier === 'Severe').length;
      const severePct = ((severeCount / count) * 100).toFixed(1);
      document.getElementById('kpi-severe').textContent = `${{severeCount}} (${{severePct}}%)`;

      // Riskiest Area
      const locGroups = {{}};
      filtered.forEach(w => {{
        if (!locGroups[w.loc]) locGroups[w.loc] = [];
        locGroups[w.loc].push(w.fri);
      }});

      let worstLoc = 'None';
      let worstAvg = -1;
      for (const [loc, arr] of Object.entries(locGroups)) {{
        const avg = arr.reduce((a, b) => a + b, 0) / arr.length;
        if (avg > worstAvg) {{
          worstAvg = avg;
          worstLoc = loc;
        }}
      }}
      document.getElementById('kpi-worst-area').textContent = `${{worstLoc}} (${{worstAvg.toFixed(2)}})`;

      // Incidents
      const incCount = filtered.filter(w => w.incident).length;
      document.getElementById('kpi-incidents').textContent = incCount;

      // Update Filter Rail Counts
      document.getElementById('tier-count-severe').textContent = filtered.filter(w => w.tier === 'Severe').length;
      document.getElementById('tier-count-high').textContent = filtered.filter(w => w.tier === 'High').length;
      document.getElementById('tier-count-moderate').textContent = filtered.filter(w => w.tier === 'Moderate').length;
      document.getElementById('tier-count-low').textContent = filtered.filter(w => w.tier === 'Low').length;
    }}

    function updateHeatLayer(filtered) {{
      if (heatLayer && map.hasLayer(heatLayer)) {{
        map.removeLayer(heatLayer);
      }}

      const heatPoints = filtered.map(w => [w.lat, w.lng, w.fri]);
      heatLayer = L.heatLayer(heatPoints, {{
        radius: 28,
        blur: 20,
        maxZoom: 17,
        gradient: {{
          0.2: '#2f9e44',
          0.5: '#d9932a',
          0.7: '#e2683c',
          1.0: '#cf3a3a'
        }}
      }});

      if (document.getElementById('toggle-heat').checked) {{
        heatLayer.addTo(map);
      }}
    }}

    function updatePastFireMarkers(filtered) {{
      if (pastFireLayer && map.hasLayer(pastFireLayer)) {{
        map.removeLayer(pastFireLayer);
      }}

      const pastFires = filtered.filter(w => w.incident);
      const markers = pastFires.map(w => {{
        const icon = L.divIcon({{
          className: 'past-fire-icon',
          html: `<div style="background:#fee2e2; border:2px solid #ef4444; border-radius:50%; width:20px; height:20px; display:flex; align-items:center; justify-content:center; font-size:11px;">🔥</div>`,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        }});
        return L.marker([w.lat, w.lng], {{ icon }}).on('click', () => openDetailPanel(w));
      }});

      pastFireLayer = L.layerGroup(markers);
      if (document.getElementById('toggle-pastfire').checked) {{
        pastFireLayer.addTo(map);
      }}
    }}

    // Layer Toggle Handlers
    function toggleHeatLayer(checked) {{
      if (checked) {{
        if (heatLayer) heatLayer.addTo(map);
      }} else {{
        if (heatLayer && map.hasLayer(heatLayer)) map.removeLayer(heatLayer);
      }}
    }}

    function toggleFireStations(checked) {{
      if (checked) {{
        if (fireStationLayer) fireStationLayer.addTo(map);
      }} else {{
        if (fireStationLayer && map.hasLayer(fireStationLayer)) map.removeLayer(fireStationLayer);
      }}
    }}

    function toggleHospitals(checked) {{
      if (checked) {{
        if (hospitalLayer) hospitalLayer.addTo(map);
      }} else {{
        if (hospitalLayer && map.hasLayer(hospitalLayer)) map.removeLayer(hospitalLayer);
      }}
    }}

    function togglePastFireMarkers(checked) {{
      if (checked) {{
        if (pastFireLayer) pastFireLayer.addTo(map);
      }} else {{
        if (pastFireLayer && map.hasLayer(pastFireLayer)) map.removeLayer(pastFireLayer);
      }}
    }}

    // Filter controls
    function handleSearchInput(val) {{
      document.getElementById('search-clear-btn').style.display = val ? 'block' : 'none';
      applyFilters();
    }}

    function clearSearch() {{
      document.getElementById('filter-search').value = '';
      document.getElementById('search-clear-btn').style.display = 'none';
      applyFilters();
    }}

    function handleFilterChange() {{
      applyFilters();
    }}

    function handleLocalityChange(loc) {{
      applyFilters();
      if (loc !== 'ALL' && LOCALITY_CENTERS[loc]) {{
        const center = LOCALITY_CENTERS[loc];
        map.flyTo(center, 16, {{ duration: 1.0 }});
      }} else {{
        map.flyTo([28.6675, 77.2715], 15, {{ duration: 1.0 }});
      }}
    }}

    function resetFilters() {{
      document.getElementById('filter-search').value = '';
      document.getElementById('search-clear-btn').style.display = 'none';
      document.getElementById('check-severe').checked = true;
      document.getElementById('check-high').checked = true;
      document.getElementById('check-moderate').checked = true;
      document.getElementById('check-low').checked = true;
      document.getElementById('filter-locality').value = 'ALL';
      applyFilters();
      map.flyTo([28.6675, 77.2715], 15);
    }}

    function toggleFilterRail() {{
      const rail = document.getElementById('filter-rail');
      rail.classList.toggle('open');
    }}

    // User Geolocation
    function getUserLocation() {{
      if (!navigator.geolocation) {{
        alert('Geolocation is not supported by your browser.');
        return;
      }}

      navigator.geolocation.getCurrentPosition(
        pos => {{
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          showUserMarker(lat, lng);
        }},
        err => {{
          // Default demo position near Seelampur Metro Station / GT Road
          alert('GPS location not permitted. Using demo position at Seelampur GT Road.');
          showUserMarker(28.6698, 77.2660);
        }}
      );
    }}

    function showUserMarker(lat, lng) {{
      if (userLocationMarker && map.hasLayer(userLocationMarker)) {{
        map.removeLayer(userLocationMarker);
      }}

      const icon = L.divIcon({{
        className: 'user-gps-marker',
        html: `<div style="background:#0284c7; width:16px; height:16px; border:3px solid #fff; border-radius:50%; box-shadow:0 0 0 5px rgba(2,132,199,0.3); animation:pulse 2s infinite;"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
      }});

      userLocationMarker = L.marker([lat, lng], {{ icon }}).addTo(map);
      userLocationMarker.bindPopup(`<strong>Your Location</strong><br>Lat: ${{lat.toFixed(4)}}, Lng: ${{lng.toFixed(4)}}`).openPopup();
      map.flyTo([lat, lng], 16);
    }}

    // =========================================================
    // 3. DETAIL PANEL
    // =========================================================
    function openDetailPanel(w) {{
      selectedWorkshop = w;
      const panel = document.getElementById('detail-panel');

      // Populate Header
      document.getElementById('panel-eyebrow').textContent = `USAP AUDITED WORKSHOP • ${{w.loc.toUpperCase()}} • ${{w.id}}`;
      document.getElementById('panel-name').textContent = w.ent;
      document.getElementById('panel-meta').textContent = `${{w.loc}} • ${{w.area}} • ID: ${{w.id}}`;
      
      const tierColor = getTierColor(w.tier);
      const circle = document.getElementById('panel-score-circle');
      circle.textContent = w.fri.toFixed(2);
      circle.style.backgroundColor = tierColor;

      const tierBadge = document.getElementById('panel-tier-badge');
      tierBadge.textContent = `${{w.tier}} Fire Risk`;
      tierBadge.style.color = tierColor;

      document.getElementById('panel-work-type').textContent = w.work;
      document.getElementById('panel-incident-badge').style.display = w.incident ? 'flex' : 'none';

      // Plain language synthesis
      generatePlainSummary(w);

      // Render Factors
      renderPanelFactors(w);

      panel.classList.add('open');
      map.panTo([w.lat, w.lng]);
    }}

    function closeDetailPanel() {{
      selectedWorkshop = null;
      document.getElementById('detail-panel').classList.remove('open');
    }}

    function generatePlainSummary(w) {{
      // Find top 3 worst factors
      const factorEntries = Object.entries(w.cats).map(([factor, val]) => {{
        const score = SCORING_MAP[factor] ? SCORING_MAP[factor][val] : 0;
        return {{ factor, val, score }};
      }}).sort((a, b) => b.score - a.score);

      const top = factorEntries.slice(0, 3);
      const problemPhrases = top.map(item => {{
        switch (item.factor) {{
          case 'exits': return item.val === '1 exit' ? 'only one way out' : 'restricted exit routes';
          case 'obstruction': return 'a blocked escape path';
          case 'emergency_exits': return 'no working emergency exit';
          case 'stair_width': return 'dangerously narrow stairs';
          case 'workspace': return 'a tightly cramped workspace';
          case 'floors': return 'extreme vertical height without fire stairs';
          case 'light': return 'trapped smoke with no vents';
          case 'windows': return 'barred windows blocking rescue';
          case 'corridor': return 'narrow cluttered corridors';
          case 'dust': return 'heavy combustible dust';
          case 'building_gap': return 'zero gap to neighbouring buildings';
          case 'waste_burning': return 'open scrap burning nearby';
          case 'station_dist': return 'excessive distance to the fire station';
          case 'response_time': return 'severe fire brigade response delays';
          case 'approach_road': return 'no road access for fire trucks';
          default: return 'limited emergency preparedness';
        }}
      }});

      let summary = '';
      if (w.tier === 'Severe') {{
        summary = `This workshop is at severe fire risk. The biggest problems are ${{problemPhrases[0]}}, ${{problemPhrases[1]}} and ${{problemPhrases[2]}}.`;
      }} else if (w.tier === 'High') {{
        summary = `This workshop is at high fire risk. Critical concerns include ${{problemPhrases[0]}}, combined with ${{problemPhrases[1]}}.`;
      }} else if (w.tier === 'Moderate') {{
        summary = `This workshop has moderate fire risk. Key improvements needed are resolving ${{problemPhrases[0]}} and ${{problemPhrases[1]}}.`;
      }} else {{
        summary = `This workshop maintains relatively low fire risk with clear escape paths, operable windows, and wider access lanes.`;
      }}

      document.getElementById('panel-summary').textContent = summary;
    }}

    function renderPanelFactors(w) {{
      const insideEl = document.getElementById('panel-inside-factors');
      const outsideEl = document.getElementById('panel-outside-factors');
      insideEl.innerHTML = '';
      outsideEl.innerHTML = '';

      const items = Object.entries(w.cats).map(([factor, val]) => {{
        const info = FACTOR_INFO[factor] || {{ name: factor, emoji: '📌', scope: 'inside', desc: {{}} }};
        const score = SCORING_MAP[factor] ? SCORING_MAP[factor][val] : 0;
        const plainSentence = info.desc[val] || `${{val}} (${{score.toFixed(1)}})`;
        return {{ factor, val, score, info, plainSentence }};
      }}).sort((a, b) => b.score - a.score);

      items.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'factor-card';
        const color = item.score >= 0.7 ? '#cf3a3a' : (item.score >= 0.4 ? '#d9932a' : '#2f9e44');
        const pct = Math.round(item.score * 100);

        card.innerHTML = `
          <div class="factor-top">
            <div class="factor-title-wrap">
              <span>${{item.info.emoji}}</span>
              <span>${{item.info.name}}</span>
            </div>
            <span class="factor-score-pill num-tnum" style="background:${{color}};">${{item.score.toFixed(2)}}</span>
          </div>
          <div class="factor-desc">${{item.plainSentence}}</div>
          <div class="factor-bar-bg">
            <div class="factor-bar-fill" style="width:${{pct}}%; background:${{color}};"></div>
          </div>
        `;

        if (item.info.scope === 'inside') {{
          insideEl.appendChild(card);
        }} else {{
          outsideEl.appendChild(card);
        }}
      }});
    }}

    function zoomToSelectedWorkshop() {{
      if (!selectedWorkshop) return;
      map.flyTo([selectedWorkshop.lat, selectedWorkshop.lng], 18, {{ duration: 1.0 }});
    }}

    // =========================================================
    // 4. ROUTING & NAVIGATION (OSRM API)
    // =========================================================
    function getDistanceKm(lat1, lon1, lat2, lon2) {{
      const R = 6371;
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLon = (lon2 - lon1) * Math.PI / 180;
      const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      return R * c;
    }}

    function findNearestFireStation(lat, lng) {{
      let nearest = FIRE_STATIONS[0];
      let minD = Infinity;
      FIRE_STATIONS.forEach(fs => {{
        const d = getDistanceKm(lat, lng, fs.lat, fs.lng);
        if (d < minD) {{
          minD = d;
          nearest = fs;
        }}
      }});
      return nearest;
    }}

    function findNearestHospital(lat, lng) {{
      let nearest = HOSPITALS[0];
      let minD = Infinity;
      HOSPITALS.forEach(h => {{
        const d = getDistanceKm(lat, lng, h.lat, h.lng);
        if (d < minD) {{
          minD = d;
          nearest = h;
        }}
      }});
      return nearest;
    }}

    function routeFromNearestFireStation() {{
      if (!selectedWorkshop) return;
      const fs = findNearestFireStation(selectedWorkshop.lat, selectedWorkshop.lng);
      requestRoute(
        fs.lat, fs.lng,
        selectedWorkshop.lat, selectedWorkshop.lng,
        'fire',
        fs.name,
        selectedWorkshop.ent
      );
    }}

    function routeFromUserLocation() {{
      if (!selectedWorkshop) return;
      if (!userLocationMarker) {{
        // Prompt for user location first
        if (!navigator.geolocation) {{
          alert('Geolocation not supported. Showing route from GT Road link.');
          requestRoute(28.6698, 77.2660, selectedWorkshop.lat, selectedWorkshop.lng, 'user', 'Your Location (GT Road)', selectedWorkshop.ent);
          return;
        }}
        navigator.geolocation.getCurrentPosition(
          pos => {{
            showUserMarker(pos.coords.latitude, pos.coords.longitude);
            requestRoute(pos.coords.latitude, pos.coords.longitude, selectedWorkshop.lat, selectedWorkshop.lng, 'user', 'Your Current Location', selectedWorkshop.ent);
          }},
          err => {{
            alert('Location permission denied. Showing route from Seelampur Metro Station.');
            showUserMarker(28.6698, 77.2660);
            requestRoute(28.6698, 77.2660, selectedWorkshop.lat, selectedWorkshop.lng, 'user', 'Seelampur Metro Link', selectedWorkshop.ent);
          }}
        );
      }} else {{
        const pos = userLocationMarker.getLatLng();
        requestRoute(pos.lat, pos.lng, selectedWorkshop.lat, selectedWorkshop.lng, 'user', 'Your Location', selectedWorkshop.ent);
      }}
    }}

    function routeToNearestHospital() {{
      if (!selectedWorkshop) return;
      const h = findNearestHospital(selectedWorkshop.lat, selectedWorkshop.lng);
      requestRoute(
        selectedWorkshop.lat, selectedWorkshop.lng,
        h.lat, h.lng,
        'hospital',
        selectedWorkshop.ent,
        h.name
      );
    }}

    function requestRoute(fromLat, fromLng, toLat, toLng, type, fromLabel, toLabel) {{
      clearNavigationRoute();

      const routeCard = document.getElementById('route-card');
      const routeTitle = document.getElementById('route-title');
      const routeIcon = document.getElementById('route-type-icon');
      const waypoints = document.getElementById('route-waypoints');
      const fallbackNotice = document.getElementById('route-fallback-notice');

      if (type === 'fire') {{
        routeIcon.textContent = '🚒';
        routeTitle.textContent = 'Fire Brigade Turnout Route';
      }} else if (type === 'hospital') {{
        routeIcon.textContent = '🏥';
        routeTitle.textContent = 'Emergency Hospital Transfer Route';
      }} else {{
        routeIcon.textContent = '📍';
        routeTitle.textContent = 'Field Route From Your Location';
      }}

      waypoints.innerHTML = `From: <strong>${{fromLabel}}</strong><br>To: <strong>${{toLabel}}</strong>`;
      routeCard.classList.add('active');
      fallbackNotice.style.display = 'none';

      const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${{fromLng}},${{fromLat}};${{toLng}},${{toLat}}?overview=full&geometries=geojson&steps=true`;

      // Fetch with timeout fallback
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);

      fetch(osrmUrl, {{ signal: controller.signal }})
        .then(res => {{
          clearTimeout(timeoutId);
          if (!res.ok) throw new Error('OSRM API non-200');
          return res.json();
        }})
        .then(data => {{
          if (!data.routes || !data.routes.length) throw new Error('No route found');
          renderOSRMRoute(data.routes[0], [fromLat, fromLng], [toLat, toLng]);
        }})
        .catch(err => {{
          console.warn('OSRM router failed or timed out, falling back to estimated trajectory:', err);
          fallbackNotice.style.display = 'block';
          renderFallbackRoute([fromLat, fromLng], [toLat, toLng]);
        }});
    }}

    function renderOSRMRoute(route, startLatLng, endLatLng) {{
      const coords = route.geometry.coordinates.map(c => [c[1], c[0]]);
      const distKm = (route.distance / 1000).toFixed(1);
      const timeMin = Math.round(route.duration / 60);

      document.getElementById('route-dist').textContent = `${{distKm}} km`;
      document.getElementById('route-time').textContent = `${{timeMin}} min`;

      // Draw white casing & red line
      const casing = L.polyline(coords, {{ color: '#ffffff', weight: 10, opacity: 0.95 }}).addTo(map);
      const line = L.polyline(coords, {{ color: '#cf3a3a', weight: 6, opacity: 0.95 }}).addTo(map);
      currentRouteLayers.push(casing, line);

      // Start & Finish Markers
      const startMarker = L.marker(startLatLng, {{
        icon: L.divIcon({{
          className: 'route-start-icon',
          html: `<div style="background:#22c55e; color:#fff; border:2px solid #fff; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:12px; box-shadow:0 2px 5px rgba(0,0,0,0.3);">🟢</div>`,
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        }})
      }}).addTo(map);

      const endMarker = L.marker(endLatLng, {{
        icon: L.divIcon({{
          className: 'route-end-icon',
          html: `<div style="background:#0f172a; color:#fff; border:2px solid #fff; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:12px; box-shadow:0 2px 5px rgba(0,0,0,0.3);">🏁</div>`,
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        }})
      }}).addTo(map);

      currentRouteLayers.push(startMarker, endMarker);

      // Turn-by-turn guidance list
      const stepsContainer = document.getElementById('route-steps');
      stepsContainer.innerHTML = '';

      if (route.legs && route.legs[0] && route.legs[0].steps) {{
        route.legs[0].steps.forEach((step, idx) => {{
          const stepDiv = document.createElement('div');
          stepDiv.className = 'route-step-item';

          let icon = '⬆️';
          const type = step.maneuver.type;
          const mod = step.maneuver.modifier;
          if (mod && mod.includes('left')) icon = '↰';
          else if (mod && mod.includes('right')) icon = '↱';
          else if (mod && mod.includes('u-turn')) icon = '↩️';
          else if (type === 'roundabout') icon = '🔄';
          else if (type === 'arrive') icon = '🏁';

          const street = step.name ? `onto <strong>${{step.name}}</strong>` : '';
          const instruction = step.maneuver.instruction || `${{type}} ${{mod || ''}} ${{street}}`;
          const distM = Math.round(step.distance);

          stepDiv.innerHTML = `
            <span class="step-icon">${{icon}}</span>
            <div class="step-text">
              <div>${{instruction}}</div>
              <div class="step-dist">${{distM}} metres</div>
            </div>
          `;
          stepsContainer.appendChild(stepDiv);
        }});
      }}

      // Fit map with padding for side panels
      map.fitBounds(casing.getBounds(), {{
        paddingTopLeft: [60, 320],
        paddingBottomRight: [460, 60]
      }});
    }}

    function renderFallbackRoute(startLatLng, endLatLng) {{
      const dKm = getDistanceKm(startLatLng[0], startLatLng[1], endLatLng[0], endLatLng[1]);
      const estRoadDist = (dKm * 1.35).toFixed(1);
      // Avg 18 km/h speed through crowded Seelampur markets
      const estTimeMin = Math.round((parseFloat(estRoadDist) / 18.0) * 60);

      document.getElementById('route-dist').textContent = `~${{estRoadDist}} km`;
      document.getElementById('route-time').textContent = `~${{estTimeMin}} min`;

      const coords = [startLatLng, endLatLng];
      const casing = L.polyline(coords, {{ color: '#ffffff', weight: 8, opacity: 0.9 }}).addTo(map);
      const line = L.polyline(coords, {{ color: '#cf3a3a', weight: 4, dashArray: '8, 8', opacity: 0.9 }}).addTo(map);
      currentRouteLayers.push(casing, line);

      const startMarker = L.marker(startLatLng, {{
        icon: L.divIcon({{ html: '🟢', className: 'pt-icon', iconSize: [20, 20], iconAnchor: [10, 10] }})
      }}).addTo(map);

      const endMarker = L.marker(endLatLng, {{
        icon: L.divIcon({{ html: '🏁', className: 'pt-icon', iconSize: [20, 20], iconAnchor: [10, 10] }})
      }}).addTo(map);

      currentRouteLayers.push(startMarker, endMarker);

      const stepsContainer = document.getElementById('route-steps');
      stepsContainer.innerHTML = `
        <div class="route-step-item">
          <span class="step-icon">⬆️</span>
          <div class="step-text">
            <div>Proceed along primary arterial road toward target area.</div>
            <div class="step-dist">Direct distance: ${{dKm.toFixed(2)}} km</div>
          </div>
        </div>
        <div class="route-step-item">
          <span class="step-icon">🏁</span>
          <div class="step-text">
            <div>Arrive at workshop destination corridor.</div>
            <div class="step-dist">Deploy localized hose line relays if alley &lt; 2.5m.</div>
          </div>
        </div>
      `;

      map.fitBounds(casing.getBounds(), {{
        paddingTopLeft: [60, 320],
        paddingBottomRight: [460, 60]
      }});
    }}

    function clearNavigationRoute() {{
      currentRouteLayers.forEach(l => map.removeLayer(l));
      currentRouteLayers = [];
      document.getElementById('route-card').classList.remove('active');
    }}

    // =========================================================
    // 5. DASHBOARD VIEW
    // =========================================================
    function renderDashboard() {{
      // 1. Locality Ranked Bars
      const locStats = {{}};
      Object.keys(LOCALITY_CENTERS).forEach(loc => {{
        locStats[loc] = {{ sum: 0, count: 0, severe: 0 }};
      }});

      WORKSHOPS_DATA.forEach(w => {{
        if (locStats[w.loc]) {{
          locStats[w.loc].sum += w.fri;
          locStats[w.loc].count += 1;
          if (w.tier === 'Severe') locStats[w.loc].severe += 1;
        }}
      }});

      const locRanked = Object.entries(locStats).map(([loc, stat]) => {{
        const avg = stat.count > 0 ? (stat.sum / stat.count) : 0;
        return {{ loc, avg, count: stat.count, severe: stat.severe }};
      }}).sort((a, b) => b.avg - a.avg);

      const locBarsEl = document.getElementById('dash-loc-bars');
      locBarsEl.innerHTML = '';

      locRanked.forEach((item, idx) => {{
        const pct = Math.round(item.avg * 100);
        const color = item.avg >= 0.70 ? 'var(--risk-severe)' : (item.avg >= 0.50 ? 'var(--risk-high)' : 'var(--risk-moderate)');
        const sevPct = Math.round((item.severe / item.count) * 100);

        const row = document.createElement('div');
        row.className = 'loc-bar-row';
        row.innerHTML = `
          <div class="loc-bar-label">
            <span><strong>${{idx + 1}}. ${{item.loc}}</strong> (${{item.count}} workshops • ${{sevPct}}% Severe)</span>
            <span class="num-tnum" style="color:${{color}};">Avg FRI: ${{item.avg.toFixed(2)}}</span>
          </div>
          <div class="loc-bar-meter">
            <div class="loc-bar-meter-fill" style="width:${{pct}}%; background:${{color}};"></div>
          </div>
        `;
        locBarsEl.appendChild(row);
      }});

      // 2. Top 8 Critical Failure Problems Settlement-Wide
      const factorSeverities = {{}};
      Object.keys(FACTOR_INFO).forEach(f => {{
        factorSeverities[f] = 0;
      }});

      WORKSHOPS_DATA.forEach(w => {{
        Object.entries(w.cats).forEach(([factor, val]) => {{
          const score = SCORING_MAP[factor] ? SCORING_MAP[factor][val] : 0;
          if (score >= 0.65) {{
            factorSeverities[factor] = (factorSeverities[factor] || 0) + 1;
          }}
        }});
      }});

      const topProblems = Object.entries(factorSeverities).map(([f, count]) => {{
        const info = FACTOR_INFO[f] || {{ name: f, emoji: '📌', scope: 'inside' }};
        const pct = Math.round((count / WORKSHOPS_DATA.length) * 100);
        return {{ factor: f, count, pct, info }};
      }}).sort((a, b) => b.pct - a.pct).slice(0, 8);

      const problemsEl = document.getElementById('top-problems-grid');
      problemsEl.innerHTML = '';

      topProblems.forEach(p => {{
        const card = document.createElement('div');
        card.className = 'problem-card';
        card.innerHTML = `
          <div class="problem-top">
            <span style="font-size:18px;">${{p.info.emoji}}</span>
            <span class="scope-tag ${{p.info.scope}}">${{p.info.scope}}</span>
          </div>
          <div class="problem-name">${{p.info.name}}</div>
          <div class="problem-meter">
            <span class="problem-pct num-tnum">${{p.pct}}%</span>
            <span style="font-size:11px; color:var(--text-muted);">of workshops</span>
          </div>
        `;
        problemsEl.appendChild(card);
      }});

      // 3. Render Table
      renderMasterTable();
    }}

    function renderMasterTable() {{
      const query = (document.getElementById('dash-table-search').value || '').trim().toLowerCase();
      const loc = document.getElementById('dash-table-loc').value;

      let list = WORKSHOPS_DATA.filter(w => {{
        if (loc !== 'ALL' && w.loc !== loc) return false;
        if (query) {{
          return w.ent.toLowerCase().includes(query) ||
                 w.id.toLowerCase().includes(query) ||
                 w.work.toLowerCase().includes(query);
        }}
        return true;
      }});

      // Sort
      list.sort((a, b) => {{
        let vA = a[tableSortCol];
        let vB = b[tableSortCol];
        if (typeof vA === 'string') vA = vA.toLowerCase();
        if (typeof vB === 'string') vB = vB.toLowerCase();
        if (vA < vB) return tableSortAsc ? -1 : 1;
        if (vA > vB) return tableSortAsc ? 1 : -1;
        return 0;
      }});

      const tbody = document.getElementById('dash-table-body');
      tbody.innerHTML = '';

      list.forEach(w => {{
        const tr = document.createElement('tr');
        tr.onclick = (e) => {{
          if (e.target.tagName !== 'BUTTON') {{
            jumpToWorkshop(w.id);
          }}
        }};

        tr.innerHTML = `
          <td><strong>${{w.id}}</strong></td>
          <td style="font-weight:600;">${{w.ent}}</td>
          <td>${{w.loc}}</td>
          <td>${{w.work}}</td>
          <td>${{w.incident ? '🔥 Yes' : '—'}}</td>
          <td><strong class="num-tnum">${{w.fri.toFixed(2)}}</strong></td>
          <td><span class="badge-tier ${{w.tier}}">${{w.tier}}</span></td>
          <td>
            <button type="button" class="btn-view-map" onclick="jumpToWorkshop('${{w.id}}')">Inspect 🔍</button>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function sortTable(col) {{
      if (tableSortCol === col) {{
        tableSortAsc = !tableSortAsc;
      }} else {{
        tableSortCol = col;
        tableSortAsc = (col === 'id' || col === 'ent');
      }}
      renderMasterTable();
    }}

    function handleDashTableFilter() {{
      renderMasterTable();
    }}

    function jumpToWorkshop(wid) {{
      const w = WORKSHOPS_DATA.find(x => x.id === wid);
      if (!w) return;
      switchTab('map');
      setTimeout(() => {{
        openDetailPanel(w);
        map.flyTo([w.lat, w.lng], 17, {{ duration: 1.0 }});
      }}, 150);
    }}
  </script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Successfully generated index.html with {len(data['workshops'])} workshops!")
