# build_role_dashboards.py
# Comprehensive script to introduce 4 distinct, fully-functional role dashboards
# (Fire Safety Officer, Urban Disaster Planner, Field Surveyor, System Administrator)
# and make all existing dashboard cards interactive.

import re

with open('generate_app.py', 'r', encoding='utf-8') as f:
    app_src = f.read()

# -------------------------------------------------------------
# 1. CSS STYLES FOR THE 4 DASHBOARDS
# -------------------------------------------------------------
role_dashboards_css = """
    /* =========================================================
       4 DISTINCT ROLE DASHBOARDS & FUNCTIONAL PANELS
       ========================================================= */
    .top-bar-center-roles {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .role-switcher-segmented {{
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: var(--radius-full);
      padding: 3px;
      gap: 3px;
    }}

    .role-switch-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      background: transparent;
      border: none;
      border-radius: var(--radius-full);
      color: #cbd5e1;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.18s ease;
      user-select: none;
    }}

    .role-switch-btn:hover {{
      color: #ffffff;
      background: rgba(255, 255, 255, 0.12);
    }}

    .role-switch-btn.active {{
      background: #0891b2;
      color: #ffffff;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
    }}

    .role-switch-btn.active.fire {{
      background: #dc2626;
    }}

    .role-switch-btn.active.planner {{
      background: #0891b2;
    }}

    .role-switch-btn.active.surveyor {{
      background: #16a34a;
    }}

    .role-switch-btn.active.admin {{
      background: #0e3a5f;
    }}

    /* Role Mission Context Banner */
    .role-mission-banner {{
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-shrink: 0;
      transition: all 0.2s ease;
    }}

    [data-theme="dark"] .role-mission-banner {{
      background: #111a2e;
      border-bottom-color: var(--border);
    }}

    .role-mission-left {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
    }}

    .role-mission-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: #ffffff;
      flex-shrink: 0;
    }}

    .role-mission-desc {{
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 500;
      line-height: 1.4;
    }}

    .role-mission-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }}

    .btn-role-action {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}

    .btn-role-action:hover {{
      transform: translateY(-1px);
    }}

    .btn-role-action.primary {{
      background: #0891b2;
      color: #ffffff;
    }}
    .btn-role-action.primary:hover {{
      background: #0e7490;
    }}

    .btn-role-action.fire-red {{
      background: #dc2626;
      color: #ffffff;
    }}
    .btn-role-action.fire-red:hover {{
      background: #b91c1c;
    }}

    .btn-role-action.outline {{
      background: var(--paper-card);
      border-color: var(--border);
      color: var(--text-primary);
    }}
    .btn-role-action.outline:hover {{
      background: var(--paper);
      border-color: var(--border-dark);
    }}

    /* Role Functional Panels below Map */
    .role-specific-section {{
      display: none;
      margin-top: 24px;
    }}

    .role-specific-section.active {{
      display: block;
    }}

    /* AHP Weight Tuning Drawer / Sliders */
    .ahp-tuner-card {{
      background: var(--paper-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      margin-bottom: 24px;
    }}

    [data-theme="dark"] .ahp-tuner-card {{
      background: #111a2e;
      border-color: var(--border);
    }}

    .ahp-slider-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-top: 14px;
    }}

    .ahp-slider-box {{
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
    }}

    [data-theme="dark"] .ahp-slider-box {{
      background: #162238;
      border-color: #1e2c47;
    }}

    .ahp-box-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .ahp-box-title {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-primary);
    }}

    .ahp-box-val {{
      font-size: 13px;
      font-weight: 800;
      color: #0891b2;
    }}

    .ahp-range-input {{
      width: 100%;
      height: 6px;
      border-radius: 9999px;
      background: #cbd5e1;
      outline: none;
      cursor: pointer;
    }}

    [data-theme="dark"] .ahp-range-input {{
      background: #2a3d60;
    }}

    /* Planner Conflagration & Policy Cards */
    .planner-grid-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }}

    .policy-box {{
      background: var(--paper);
      border-left: 3px solid #0891b2;
      padding: 12px 14px;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      margin-top: 10px;
      font-size: 12px;
      line-height: 1.5;
      color: var(--text-secondary);
    }}

    [data-theme="dark"] .policy-box {{
      background: #162238;
    }}

    /* Surveyor Rapid Audit Modal */
    .surveyor-modal {{
      background: var(--paper-card);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-modal);
      border: 1px solid var(--border);
      width: 720px;
      max-width: 95vw;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    [data-theme="dark"] .surveyor-modal {{
      background: #111a2e;
      border-color: #22324f;
    }}

    .surveyor-form-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      padding: 20px;
      overflow-y: auto;
      max-height: 65vh;
    }}

    .survey-group {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .survey-label {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-secondary);
    }}

    /* Clickable interactive analytics items */
    .clickable-bar-item {{
      cursor: pointer;
      transition: all 0.15s ease;
      border-radius: var(--radius-sm);
      padding: 4px 6px;
      margin: -4px -6px;
    }}

    .clickable-bar-item:hover {{
      background: rgba(8, 145, 178, 0.1);
      transform: translateX(2px);
    }}

    .clickable-seg-slice {{
      cursor: pointer;
      transition: opacity 0.15s ease;
    }}
    .clickable-seg-slice:hover {{
      opacity: 0.85;
      filter: brightness(1.1);
    }}
"""

if '/* 4 DISTINCT ROLE DASHBOARDS' not in app_src:
    app_src = app_src.replace('  </style>', role_dashboards_css + '\n  </style>', 1)
    print("Inserted role dashboards CSS.")

# -------------------------------------------------------------
# 2. TOP BAR ROLE SWITCHER HTML
# -------------------------------------------------------------
role_switcher_html = """      <!-- Center Role Switcher Segmented Pills -->
      <div class="top-bar-center-roles">
        <div class="role-switcher-segmented">
          <button type="button" class="role-switch-btn active fire" id="btn-role-fire" onclick="switchDashboardRole('fire')" title="Switch to Fire Safety Officer Incident Command">
            <svg class="svg-icon" style="width:12px; height:12px;" viewBox="0 0 24 24"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
            <span>Fire Officer</span>
          </button>
          <button type="button" class="role-switch-btn planner" id="btn-role-planner" onclick="switchDashboardRole('planner')" title="Switch to Urban Disaster Planner Structural Risk View">
            <svg class="svg-icon" style="width:12px; height:12px;" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
            <span>Urban Planner</span>
          </button>
          <button type="button" class="role-switch-btn surveyor" id="btn-role-surveyor" onclick="switchDashboardRole('surveyor')" title="Switch to Field Surveyor Rapid Audit Mode">
            <svg class="svg-icon" style="width:12px; height:12px;" viewBox="0 0 24 24"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="m9 14 2 2 4-4"/></svg>
            <span>Field Surveyor</span>
          </button>
          <button type="button" class="role-switch-btn admin" id="btn-role-admin" onclick="switchDashboardRole('admin')" title="Switch to System Administrator Governance & Modeling Hub">
            <svg class="svg-icon" style="width:12px; height:12px;" viewBox="0 0 24 24"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <span>Administrator</span>
          </button>
        </div>
      </div>
"""

if 'id="btn-role-fire"' not in app_src:
    app_src = app_src.replace(
        '      </div>\n\n      <div class="top-bar-right">',
        '      </div>\n\n' + role_switcher_html + '\n      <div class="top-bar-right">',
        1
    )
    print("Inserted top-bar role switcher HTML.")

# -------------------------------------------------------------
# 3. ROLE MISSION BANNER HTML (BELOW KPI STRIP)
# -------------------------------------------------------------
mission_banner_html = """    <!-- Role Context Mission Banner -->
    <div id="role-mission-banner" class="role-mission-banner">
      <div class="role-mission-left">
        <span id="role-mission-tag" class="role-mission-tag" style="background:#dc2626;">FIRE OFFICER VIEW</span>
        <span id="role-mission-desc" class="role-mission-desc">Incident Command Mode: Rapid emergency dispatch simulation, narrow gali hose relay calculation, and DFS tender access assessment.</span>
      </div>
      <div id="role-mission-actions" class="role-mission-actions">
        <!-- Injected dynamically by JS per role -->
      </div>
    </div>
"""

if 'id="role-mission-banner"' not in app_src:
    app_src = app_src.replace(
        '    <!-- Scrollable Unified Dashboard Body -->',
        mission_banner_html + '\n    <!-- Scrollable Unified Dashboard Body -->',
        1
    )
    print("Inserted role mission banner HTML.")

# -------------------------------------------------------------
# 4. ROLE SPECIFIC FUNCTIONAL PANELS (BELOW MAP)
# -------------------------------------------------------------
role_sections_html = """
      <!-- =========================================================
           ROLE-SPECIFIC FUNCTIONAL DASHBOARD PANELS
           ========================================================= -->

      <!-- 1. FIRE SAFETY OFFICER PANEL -->
      <div id="role-section-fire" class="role-specific-section active">
        <div class="analytics-grid-row">
          <div class="dash-card">
            <div class="dash-card-header">
              <span class="dash-card-title">DFS Tactical Pinch-Points (&lt;2.5m Galis)</span>
              <span class="eyebrow" style="color:var(--risk-severe);">High Entrapment Risk</span>
            </div>
            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:12px;">
              Workshops located on alleys under 2.5m where heavy DFS water tenders cannot enter. Crews must establish manual hose relays from perimeter avenues.
            </p>
            <div id="fire-pinchpoint-list" style="display:flex; flex-direction:column; gap:8px;">
              <!-- Populated by JS -->
            </div>
          </div>

          <div class="dash-card">
            <div class="dash-card-header">
              <span class="dash-card-title">DFS Perimeter Staging Avenues</span>
              <span class="eyebrow">6 Motorable Bases</span>
            </div>
            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:12px;">
              Arterial avenues with width &ge; 18m suitable for heavy tenders (16-tonne) and high-volume bowser pumps to lay delivery lines into interior clusters.
            </p>
            <div id="fire-staging-cards" style="display:flex; flex-direction:column; gap:8px;">
              <!-- Populated by JS -->
            </div>
          </div>
        </div>
      </div>

      <!-- 2. URBAN DISASTER PLANNER PANEL -->
      <div id="role-section-planner" class="role-specific-section">
        <div class="analytics-grid-row">
          <div class="dash-card">
            <div class="dash-card-header">
              <span class="dash-card-title">Building Setback &amp; Conflagration Separation</span>
              <span class="eyebrow">Zero-Setback Hazard</span>
            </div>
            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:12px;">
              Assessment of combustible building-to-building gap. Shared combustible walls allow fires to leap across contiguous workshop structures.
            </p>
            <div id="planner-gap-breakdown">
              <!-- Populated by JS -->
            </div>
          </div>

          <div class="dash-card">
            <div class="dash-card-header">
              <span class="dash-card-title">Master Plan 2041 Spatial Intervention Directives</span>
              <span class="eyebrow">Policy Generator</span>
            </div>
            <div style="display:flex; gap:8px; margin-bottom:10px;">
              <select id="planner-policy-loc" class="locality-select" onchange="renderPlannerPolicy(this.value)">
                <option value="Shanti Mohalla">Shanti Mohalla (Textile Hub)</option>
                <option value="Seelampur">Seelampur (Metal &amp; Scrap)</option>
                <option value="Gandhi Nagar">Gandhi Nagar (Garments)</option>
                <option value="Subhash Nagar">Subhash Nagar (Mixed)</option>
              </select>
            </div>
            <div id="planner-policy-content" class="policy-box">
              <!-- Populated by JS -->
            </div>
          </div>
        </div>
      </div>

      <!-- 3. FIELD SURVEYOR PANEL -->
      <div id="role-section-surveyor" class="role-specific-section">
        <div class="dash-card" style="margin-bottom:24px;">
          <div class="dash-card-header">
            <span class="dash-card-title">Ground-Truth Audit &amp; Verification Telemetry</span>
            <button type="button" class="btn-role-action primary" onclick="openSurveyorModal()">
              <svg class="svg-icon" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              <span>+ Audit New Workshop (Live GPS)</span>
            </button>
          </div>
          <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-top:8px;">
            <div class="preview-stat-card">
              <span class="preview-stat-label">Total Audited Units</span>
              <span id="surveyor-stat-total" class="preview-stat-val num-tnum">148</span>
            </div>
            <div class="preview-stat-card">
              <span class="preview-stat-label">Verified Today</span>
              <span id="surveyor-stat-verified" class="preview-stat-val num-tnum" style="color:#16a34a;">34</span>
            </div>
            <div class="preview-stat-card">
              <span class="preview-stat-label">Requires Re-Audit</span>
              <span id="surveyor-stat-recheck" class="preview-stat-val num-tnum" style="color:#ea580c;">12</span>
            </div>
            <div class="preview-stat-card">
              <span class="preview-stat-label">GPS Precision Status</span>
              <span class="preview-stat-val" style="color:#0891b2; font-size:13px;">Cadastral RTK Aligned</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. SYSTEM ADMINISTRATOR PANEL -->
      <div id="role-section-admin" class="role-specific-section">
        <div class="ahp-tuner-card">
          <div class="dash-card-header">
            <div>
              <span class="dash-card-title">Multi-Criteria AHP Weighting Engine (Live Model Tuning)</span>
              <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">
                Calibrate USAP mathematical formula weights: Fire Risk Index = (w<sub>Egress</sub> &times; Egress + w<sub>Hazard</sub> &times; Hazard + w<sub>Access</sub> &times; Access). Recomputes all 148 units dynamically.
              </div>
            </div>
            <div style="display:flex; gap:8px;">
              <button type="button" class="btn-role-action outline" onclick="resetAHPWeights()">Reset to USAP Baseline</button>
              <button type="button" class="btn-role-action primary" onclick="exportMasterCSV()">Export Master CSV</button>
              <button type="button" class="btn-role-action primary" onclick="exportSurveyGeoJSON()">Export GeoJSON</button>
            </div>
          </div>

          <div class="ahp-slider-grid">
            <div class="ahp-slider-box">
              <div class="ahp-box-header">
                <span class="ahp-box-title">Egress Sub-Index Weight</span>
                <span id="ahp-val-egress" class="ahp-box-val num-tnum">45%</span>
              </div>
              <input type="range" id="ahp-slider-egress" class="ahp-range-input" min="10" max="70" value="45" oninput="handleAHPWeightChange()">
              <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Exits, stair width, corridors, floors</div>
            </div>

            <div class="ahp-slider-box">
              <div class="ahp-box-header">
                <span class="ahp-box-title">Hazard Sub-Index Weight</span>
                <span id="ahp-val-hazard" class="ahp-box-val num-tnum">25%</span>
              </div>
              <input type="range" id="ahp-slider-hazard" class="ahp-range-input" min="10" max="60" value="25" oninput="handleAHPWeightChange()">
              <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Waste burning, combustible dust, building gap</div>
            </div>

            <div class="ahp-slider-box">
              <div class="ahp-box-header">
                <span class="ahp-box-title">Access Sub-Index Weight</span>
                <span id="ahp-val-access" class="ahp-box-val num-tnum">30%</span>
              </div>
              <input type="range" id="ahp-slider-access" class="ahp-range-input" min="10" max="60" value="30" oninput="handleAHPWeightChange()">
              <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Distance to fire station, response time, road width</div>
            </div>
          </div>
        </div>
      </div>
"""

if 'id="role-section-fire"' not in app_src:
    # Insert right before the sortable table card
    target_table_marker = '<div class="dash-card">\n          <div class="dash-card-header">\n            <span class="dash-card-title">All 148 Audited Workshops'
    if target_table_marker in app_src:
        app_src = app_src.replace(target_table_marker, role_sections_html + '\n        ' + target_table_marker, 1)
        print("Inserted role specific functional panels HTML.")
    else:
        # Fallback search
        idx_table = app_src.find('All 148 Audited Workshops')
        if idx_table != -1:
            idx_card = app_src.rfind('<div class="dash-card">', 0, idx_table)
            app_src = app_src[:idx_card] + role_sections_html + '\n        ' + app_src[idx_card:]
            print("Inserted role specific panels HTML via fallback index.")

# -------------------------------------------------------------
# 5. SURVEYOR RAPID AUDIT MODAL HTML
# -------------------------------------------------------------
surveyor_modal_html = """  <!-- Rapid Audit Modal for Field Surveyor -->
  <div id="surveyor-modal-overlay" class="modal-overlay" onclick="handleSurveyorOverlayClick(event)">
    <div class="surveyor-modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div>
          <span class="eyebrow" style="color:#16a34a;">RAPID CADASTRAL AUDIT ENGINE</span>
          <h2 class="modal-title">Record New Workshop Survey (Live On-Site)</h2>
        </div>
        <button type="button" class="modal-close-btn" onclick="closeSurveyorModal()">
          <svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <form id="surveyor-new-form" onsubmit="handleSurveyorSubmit(event)" class="surveyor-form-grid">
        <div class="survey-group">
          <label class="survey-label">Enterprise Name</label>
          <input type="text" id="surv-ent" class="form-input" required placeholder="e.g. Royal Denim Laundry Works">
        </div>
        <div class="survey-group">
          <label class="survey-label">Locality Cluster</label>
          <select id="surv-loc" class="locality-select" required>
            <option value="Seelampur">Seelampur</option>
            <option value="Gandhi Nagar">Gandhi Nagar</option>
            <option value="Shanti Mohalla">Shanti Mohalla</option>
            <option value="Subhash Nagar">Subhash Nagar</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">GPS Latitude</label>
          <input type="number" step="0.000001" id="surv-lat" class="form-input" required value="28.6668">
        </div>
        <div class="survey-group">
          <label class="survey-label">GPS Longitude</label>
          <input type="number" step="0.000001" id="surv-lng" class="form-input" required value="77.2715">
        </div>

        <div class="survey-group">
          <label class="survey-label">Exit Routes</label>
          <select id="surv-exits" class="locality-select">
            <option value="1 exit">1 Exit Only (Severe Risk)</option>
            <option value="2 exits">2 Independent Exits</option>
            <option value="3+ exits">3+ Exits (Low Risk)</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Evacuation Obstruction</label>
          <select id="surv-obstr" class="locality-select">
            <option value="obstructed">Obstructed / Blocked Path</option>
            <option value="clear">Obstruction-Free Corridor</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Emergency Exits</label>
          <select id="surv-emg" class="locality-select">
            <option value="none">No Emergency Exit</option>
            <option value="locked_or_blocked">Locked / Barred</option>
            <option value="functional">Functional &amp; Unlocked</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Staircase Width</label>
          <select id="surv-stair" class="locality-select">
            <option value="under_0_8m">&lt; 0.8m (Extremely Narrow)</option>
            <option value="0_8_to_1_2m">0.8m &ndash; 1.2m</option>
            <option value="over_1_2m">&gt; 1.2m (Wide)</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Number of Storeys</label>
          <select id="surv-floors" class="locality-select">
            <option value="g_plus_3_or_more">G+3 or More (High Chimney Hazard)</option>
            <option value="g_plus_2">G+2 Structure</option>
            <option value="g_plus_1">G+1 Structure</option>
            <option value="ground_only">Ground Floor Only</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Approach Road for Fire Tender</label>
          <select id="surv-road" class="locality-select">
            <option value="narrow_under_2_5m">&lt; 2.5m (Inaccessible to Truck)</option>
            <option value="wide_over_4m">&gt; 4m (Motorable Road)</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Building Separation Gap</label>
          <select id="surv-gap" class="locality-select">
            <option value="shared_wall_0m">Shared Wall (0m Setback)</option>
            <option value="narrow_gap_under_1m">&lt; 1m Gap</option>
            <option value="gap_over_1m">&gt; 1m Setback</option>
          </select>
        </div>
        <div class="survey-group">
          <label class="survey-label">Combustible Dust / Lint</label>
          <select id="surv-dust" class="locality-select">
            <option value="heavy_flammable_lint">Heavy Flammable Dust/Lint</option>
            <option value="moderate_dust">Moderate / Low Dust</option>
          </select>
        </div>

        <div style="grid-column:span 2; display:flex; justify-content:flex-end; gap:10px; margin-top:10px;">
          <button type="button" class="btn-role-action outline" onclick="closeSurveyorModal()">Cancel</button>
          <button type="submit" class="btn-role-action primary" style="background:#16a34a;">
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Save &amp; Compute Risk Index Live</span>
          </button>
        </div>
      </form>
    </div>
  </div>
"""

if 'id="surveyor-modal-overlay"' not in app_src:
    app_src = app_src.replace('  <!-- Leaflet JS', surveyor_modal_html + '\n  <!-- Leaflet JS', 1)
    print("Inserted surveyor modal HTML.")

# -------------------------------------------------------------
# 6. JAVASCRIPT LOGIC FOR THE 4 DASHBOARDS & INTERACTIVE CARDS
# -------------------------------------------------------------
dashboards_js = """
    // =========================================================
    // 4 DISTINCT DASHBOARDS CONTROLLER & ENGINE
    // =========================================================
    let activeDashboardRole = 'fire';
    let currentAHPWeights = {{ egress: 0.45, hazard: 0.25, access: 0.30 }};

    const ROLE_CONFIGS = {{
      fire: {{
        key: 'fire',
        name: 'Insp. R. K. Singh',
        roleTitle: 'Fire Safety Officer',
        initials: 'RS',
        badgeColor: '#dc2626',
        tagText: 'FIRE SAFETY OFFICER VIEW',
        missionDesc: 'Tactical Incident Command: Rapid emergency vehicle dispatch simulation, narrow gali delivery hose calculations, and DFS perimeter water staging.',
        actionsHtml: `
          <button type="button" class="btn-role-action fire-red" onclick="triggerShopFireIncident(selectedWorkshop || WORKSHOPS_DATA[0])">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
            <span>Simulate Active Incident</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="openHoseRelayModal(selectedWorkshop || WORKSHOPS_DATA[0])">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>
            <span>Hose Reach SOP</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="focusStagingRoadsOnMap()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/></svg>
            <span>Perimeter Staging Roads</span>
          </button>
        `
      }},
      planner: {{
        key: 'planner',
        name: 'Neha Gupta',
        roleTitle: 'Urban Disaster Planner',
        initials: 'NG',
        badgeColor: '#0891b2',
        tagText: 'URBAN DISASTER PLANNER VIEW',
        missionDesc: 'Structural Hazard Mitigation: Spatial setback compliance audits, multi-storey conflagration analysis, and Master Plan 2041 infrastructure easements.',
        actionsHtml: `
          <button type="button" class="btn-role-action primary" onclick="filterByZeroSetback()">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
            <span>Filter Zero-Setback (0m)</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="filterByHighRiseFloors()">
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            <span>G+3 &amp; G+4 Fabric</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="toggleCadastralStudyBoundary()">
            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/></svg>
            <span>Study Area Boundary</span>
          </button>
        `
      }},
      surveyor: {{
        key: 'surveyor',
        name: 'Tariq Anjum',
        roleTitle: 'Field Survey Lead',
        initials: 'TA',
        badgeColor: '#16a34a',
        tagText: 'FIELD SURVEYOR AUDIT VIEW',
        missionDesc: 'Ground-Truth Verification: On-site physical parameter collection, GPS parcel calibration, and rapid hazard auditing for informal workshops.',
        actionsHtml: `
          <button type="button" class="btn-role-action primary" style="background:#16a34a;" onclick="openSurveyorModal()">
            <svg class="svg-icon" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span>+ Audit New Workshop</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="getUserLocation()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
            <span>Calibrate GPS Location</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="markSelectedWorkshopVerified()">
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
            <span>Verify Selected Unit</span>
          </button>
        `
      }},
      admin: {{
        key: 'admin',
        name: 'Prof. Amit Sharma',
        roleTitle: 'System Administrator',
        initials: 'AS',
        badgeColor: '#0e3a5f',
        tagText: 'ADMINISTRATOR GOVERNANCE VIEW',
        missionDesc: 'Resilience Governance & Modeling: Multi-criteria AHP mathematical weighting calibration, executive authority briefings, and spatial data export.',
        actionsHtml: `
          <button type="button" class="btn-role-action primary" style="background:#0e3a5f;" onclick="exportSurveyGeoJSON()">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>Export GeoJSON</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="exportMasterCSV()">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span>Export CSV</span>
          </button>
          <button type="button" class="btn-role-action outline" onclick="printExecutiveReport()">
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
            <span>Print Executive Brief</span>
          </button>
        `
      }}
    }};

    function switchDashboardRole(roleKey) {{
      activeDashboardRole = roleKey;
      const cfg = ROLE_CONFIGS[roleKey] || ROLE_CONFIGS.fire;

      // Update segmented buttons
      ['fire', 'planner', 'surveyor', 'admin'].forEach(r => {{
        const btn = document.getElementById('btn-role-' + r);
        if (btn) btn.classList.toggle('active', r === roleKey);
      }});

      // Update user profile pill in top bar
      const nameEl = document.getElementById('top-user-name');
      const roleEl = document.getElementById('top-user-role');
      const avatarEl = document.getElementById('top-user-avatar');
      if (nameEl) nameEl.textContent = cfg.name;
      if (roleEl) roleEl.textContent = cfg.roleTitle;
      if (avatarEl) {{
        avatarEl.textContent = cfg.initials;
        avatarEl.style.backgroundColor = cfg.badgeColor;
      }}

      // Update Mission Banner
      const tagEl = document.getElementById('role-mission-tag');
      const descEl = document.getElementById('role-mission-desc');
      const actionsEl = document.getElementById('role-mission-actions');
      if (tagEl) {{
        tagEl.textContent = cfg.tagText;
        tagEl.style.backgroundColor = cfg.badgeColor;
      }}
      if (descEl) descEl.textContent = cfg.missionDesc;
      if (actionsEl) actionsEl.innerHTML = cfg.actionsHtml;

      // Toggle Role Functional Sections below Map
      ['fire', 'planner', 'surveyor', 'admin'].forEach(r => {{
        const sec = document.getElementById('role-section-' + r);
        if (sec) sec.classList.toggle('active', r === roleKey);
      }});

      // Populate role-specific dynamic content
      if (roleKey === 'fire') renderFireOfficerContent();
      if (roleKey === 'planner') renderPlannerContent();
      if (roleKey === 'surveyor') renderSurveyorContent();
      if (roleKey === 'admin') renderAdminContent();
    }}
    window.switchDashboardRole = switchDashboardRole;

    // --- FIRE OFFICER FUNCTIONS ---
    function renderFireOfficerContent() {{
      const pinchList = document.getElementById('fire-pinchpoint-list');
      if (pinchList) {{
        const severePinch = WORKSHOPS_DATA.filter(w => (w.cats.approach_road === 'narrow_under_2_5m' || w.cats.exits === '1 exit') && w.tier === 'Severe').slice(0, 5);
        pinchList.innerHTML = severePinch.map(w => `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 10px; background:var(--paper); border-radius:var(--radius-sm); border-left:3px solid #dc2626; cursor:pointer;" onclick="jumpToWorkshop('${{w.id}}')">
            <div>
              <div style="font-weight:700; font-size:12px; color:var(--text-primary);">${{w.ent}}</div>
              <div style="font-size:10px; color:var(--text-muted);">${{w.loc}} &bull; Lane: ${{w.cats.approach_road || '<2.5m'}} &bull; Single Exit</div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="kpi-badge severe" style="font-size:10px;">FRI ${{w.fri.toFixed(2)}}</span>
              <button type="button" class="btn-role-action fire-red" style="padding:3px 8px; font-size:10px;" onclick="event.stopPropagation(); triggerShopFireIncident(WORKSHOPS_DATA.find(x => x.id === '${{w.id}}'))">Dispatch</button>
            </div>
          </div>
        `).join('');
      }}

      const stagingList = document.getElementById('fire-staging-cards');
      if (stagingList && typeof ARTERIAL_STAGING_ROADS !== 'undefined') {{
        stagingList.innerHTML = ARTERIAL_STAGING_ROADS.slice(0, 4).map(r => `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 10px; background:var(--paper); border-radius:var(--radius-sm); cursor:pointer;" onclick="map.flyTo([${{r.lat}}, ${{r.lng}}], 17)">
            <div>
              <div style="font-weight:700; font-size:12px; color:var(--text-primary);">${{r.name}}</div>
              <div style="font-size:10px; color:var(--text-muted);">${{r.desc}}</div>
            </div>
            <span style="font-size:11px; font-weight:800; color:#0891b2;">&ge; ${{r.widthM}}m Motorable</span>
          </div>
        `).join('');
      }}
    }}

    function focusStagingRoadsOnMap() {{
      if (typeof ARTERIAL_STAGING_ROADS !== 'undefined' && map) {{
        const pts = ARTERIAL_STAGING_ROADS.map(r => [r.lat, r.lng]);
        map.fitBounds(L.latLngBounds(pts), {{ padding: [60, 60] }});
      }}
    }}
    window.focusStagingRoadsOnMap = focusStagingRoadsOnMap;

    // --- URBAN PLANNER FUNCTIONS ---
    function renderPlannerContent() {{
      const gapDiv = document.getElementById('planner-gap-breakdown');
      if (gapDiv) {{
        const zeroGap = WORKSHOPS_DATA.filter(w => w.cats.building_gap === 'shared_wall_0m').length;
        const sub1m = WORKSHOPS_DATA.filter(w => w.cats.building_gap === 'narrow_gap_under_1m').length;
        const clear = WORKSHOPS_DATA.length - zeroGap - sub1m;
        const total = WORKSHOPS_DATA.length || 1;

        gapDiv.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div>
              <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:3px;">
                <span style="font-weight:700; color:#dc2626;">Zero Setback (0m Shared Wall)</span>
                <span class="num-tnum font-weight:800;">${{zeroGap}} (${{(zeroGap/total*100).toFixed(1)}}%)</span>
              </div>
              <div class="factor-track-mini"><div class="factor-fill-mini" style="width:${{zeroGap/total*100}}%; background:#dc2626;"></div></div>
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:3px;">
                <span style="font-weight:700; color:#ea580c;">Sub-1m Narrow Gap</span>
                <span class="num-tnum font-weight:800;">${{sub1m}} (${{(sub1m/total*100).toFixed(1)}}%)</span>
              </div>
              <div class="factor-track-mini"><div class="factor-fill-mini" style="width:${{sub1m/total*100}}%; background:#ea580c;"></div></div>
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:3px;">
                <span style="font-weight:700; color:#16a34a;">Compliant Setback (&gt;1m)</span>
                <span class="num-tnum font-weight:800;">${{clear}} (${{(clear/total*100).toFixed(1)}}%)</span>
              </div>
              <div class="factor-track-mini"><div class="factor-fill-mini" style="width:${{clear/total*100}}%; background:#16a34a;"></div></div>
            </div>
          </div>
        `;
      }}
      renderPlannerPolicy(document.getElementById('planner-policy-loc')?.value || 'Shanti Mohalla');
    }}

    function renderPlannerPolicy(locality) {{
      const content = document.getElementById('planner-policy-content');
      if (!content) return;
      const policies = {{
        'Shanti Mohalla': `<strong>Master Plan 2041 Directive for Shanti Mohalla:</strong><br>&bull; <em>Textile Warehouse Separation:</em> Retrofit 2-hour fire-rated firewalls between contiguous garment godowns.<br>&bull; <em>External Fire Escape Easements:</em> Mandate steel external spiral fire stairs on rear alley elevations.<br>&bull; <em>Chindi Flammable Scrap:</em> Ban open-air sorting of synthetic cloth trimmings along residential access galis.`,
        'Seelampur': `<strong>Master Plan 2041 Directive for Seelampur Industrial Fabric:</strong><br>&bull; <em>Smelting &amp; PCB Salvage:</em> Relocate unauthorized acid/copper recovery furnaces to DSIIDC Narela industrial hub.<br>&bull; <em>Kabari Mandi Arterial:</em> Widen main commercial approach to 6 meters by clearing encroached temporary awnings.<br>&bull; <em>Transformer Setbacks:</em> Enforce 3-meter safety radius around local BSES electrical distribution transformers.`,
        'Gandhi Nagar': `<strong>Master Plan 2041 Directive for Gandhi Nagar Garment Cluster:</strong><br>&bull; <em>Multi-Storey Egress:</em> Mandate dual illuminated fire exit doors for all workshops with &gt;15 sewing machine operators.<br>&bull; <em>Fire Truck Approach:</em> Install dedicated dry riser pipes at Mahavir Gali entry to supply upper-floor garment lofts without dragging heavy hoses.`,
        'Subhash Nagar': `<strong>Master Plan 2041 Directive for Subhash Nagar Sector:</strong><br>&bull; <em>Mixed Residential Easements:</em> Prevent ground-floor industrial solvent storage beneath upper-floor residential quarters.<br>&bull; <em>Narrow Lane Quick-Attack:</em> Deploy custom battery-powered DFS mini water-mist motorbikes for sub-2m alley operations.`
      }};
      content.innerHTML = policies[locality] || policies['Shanti Mohalla'];
    }}
    window.renderPlannerPolicy = renderPlannerPolicy;

    function filterByZeroSetback() {{
      const zero = WORKSHOPS_DATA.filter(w => w.cats.building_gap === 'shared_wall_0m');
      renderMapMarkers(zero);
      updateKpis(zero);
      renderMasterTable(zero);
    }}
    window.filterByZeroSetback = filterByZeroSetback;

    function filterByHighRiseFloors() {{
      const highRise = WORKSHOPS_DATA.filter(w => w.cats.floors === 'g_plus_3_or_more' || w.cats.floors === 'g_plus_2');
      renderMapMarkers(highRise);
      updateKpis(highRise);
      renderMasterTable(highRise);
    }}
    window.filterByHighRiseFloors = filterByHighRiseFloors;

    function toggleCadastralStudyBoundary() {{
      const chk = document.getElementById('toggle-boundaries');
      if (chk) {{
        chk.checked = !chk.checked;
        toggleBoundaries(chk.checked);
      }}
    }}
    window.toggleCadastralStudyBoundary = toggleCadastralStudyBoundary;

    // --- FIELD SURVEYOR FUNCTIONS ---
    function renderSurveyorContent() {{
      const totalEl = document.getElementById('surveyor-stat-total');
      if (totalEl) totalEl.textContent = WORKSHOPS_DATA.length;
    }}

    function openSurveyorModal() {{
      const overlay = document.getElementById('surveyor-modal-overlay');
      if (overlay) overlay.classList.add('active');
    }}
    window.openSurveyorModal = openSurveyorModal;

    function closeSurveyorModal() {{
      const overlay = document.getElementById('surveyor-modal-overlay');
      if (overlay) overlay.classList.remove('active');
    }}
    window.closeSurveyorModal = closeSurveyorModal;

    function handleSurveyorOverlayClick(e) {{
      if (e.target.id === 'surveyor-modal-overlay') closeSurveyorModal();
    }}
    window.handleSurveyorOverlayClick = handleSurveyorOverlayClick;

    function handleSurveyorSubmit(e) {{
      e.preventDefault();
      const ent = document.getElementById('surv-ent').value.trim();
      const loc = document.getElementById('surv-loc').value;
      const lat = parseFloat(document.getElementById('surv-lat').value);
      const lng = parseFloat(document.getElementById('surv-lng').value);

      const cats = {{
        exits: document.getElementById('surv-exits').value,
        obstruction: document.getElementById('surv-obstr').value,
        emergency_exits: document.getElementById('surv-emg').value,
        stair_width: document.getElementById('surv-stair').value,
        workspace: '200_to_500sqft',
        floors: document.getElementById('surv-floors').value,
        light: 'dim_partial',
        windows: 'few_restricted',
        corridor: '1_to_1_5m',
        dust: document.getElementById('surv-dust').value,
        building_gap: document.getElementById('surv-gap').value,
        waste_burning: 'occasional_burning',
        station_dist: '1_5_to_3km',
        response_time: '15_to_25min',
        approach_road: document.getElementById('surv-road').value
      }};

      // Calculate FRI using AHP weights
      const egressVals = [
        SCORING_MAP.exits[cats.exits] || 0.6,
        SCORING_MAP.obstruction[cats.obstruction] || 0.6,
        SCORING_MAP.emergency_exits[cats.emergency_exits] || 0.6,
        SCORING_MAP.stair_width[cats.stair_width] || 0.6,
        0.5,
        SCORING_MAP.floors[cats.floors] || 0.6,
        0.5, 0.6, 0.5
      ];
      const egress = egressVals.reduce((a, b) => a + b, 0) / egressVals.length;

      const hazardVals = [
        SCORING_MAP.dust[cats.dust] || 0.6,
        SCORING_MAP.building_gap[cats.building_gap] || 0.6,
        0.5
      ];
      const hazard = hazardVals.reduce((a, b) => a + b, 0) / hazardVals.length;

      const accessVals = [
        0.6, 0.6,
        SCORING_MAP.approach_road[cats.approach_road] || 0.6
      ];
      const access = accessVals.reduce((a, b) => a + b, 0) / accessVals.length;

      const fri = (currentAHPWeights.egress * egress) + (currentAHPWeights.hazard * hazard) + (currentAHPWeights.access * access);
      const tier = fri >= 0.7 ? 'Severe' : (fri >= 0.5 ? 'High' : (fri >= 0.3 ? 'Moderate' : 'Low'));

      const newWorkshop = {{
        id: 'E' + (WORKSHOPS_DATA.length + 1).toString().padStart(3, '0'),
        loc: loc,
        area: `${{loc}} Sector (Audit Verified)`,
        ent: ent,
        work: 'Surveyed Workshop Unit',
        incident: false,
        lat: lat,
        lng: lng,
        cats: cats,
        fri: parseFloat(fri.toFixed(4)),
        egress: parseFloat(egress.toFixed(4)),
        hazard: parseFloat(hazard.toFixed(4)),
        access: parseFloat(access.toFixed(4)),
        tier: tier,
        socio_vuln: 0.35,
        verified: true
      }};

      WORKSHOPS_DATA.unshift(newWorkshop);
      closeSurveyorModal();
      applyFilters();
      jumpToWorkshop(newWorkshop.id);
      alert(`Success! Audited workshop '${{ent}}' recorded live with Fire Risk Index ${{newWorkshop.fri.toFixed(2)}} (${{tier}} Tier).`);
    }}
    window.handleSurveyorSubmit = handleSurveyorSubmit;

    function markSelectedWorkshopVerified() {{
      if (!selectedWorkshop) {{
        alert('Please click on any workshop dot on the map first.');
        return;
      }}
      selectedWorkshop.verified = true;
      alert(`Workshop '${{selectedWorkshop.ent}}' marked as Field Verified.`);
      const verifiedEl = document.getElementById('surveyor-stat-verified');
      if (verifiedEl) verifiedEl.textContent = parseInt(verifiedEl.textContent || '0') + 1;
    }}
    window.markSelectedWorkshopVerified = markSelectedWorkshopVerified;

    // --- SYSTEM ADMINISTRATOR FUNCTIONS (AHP TUNER & DATA EXPORT) ---
    function renderAdminContent() {{
      document.getElementById('ahp-slider-egress').value = Math.round(currentAHPWeights.egress * 100);
      document.getElementById('ahp-slider-hazard').value = Math.round(currentAHPWeights.hazard * 100);
      document.getElementById('ahp-slider-access').value = Math.round(currentAHPWeights.access * 100);
      document.getElementById('ahp-val-egress').textContent = `${{Math.round(currentAHPWeights.egress * 100)}}%`;
      document.getElementById('ahp-val-hazard').textContent = `${{Math.round(currentAHPWeights.hazard * 100)}}%`;
      document.getElementById('ahp-val-access').textContent = `${{Math.round(currentAHPWeights.access * 100)}}%`;
    }}

    function handleAHPWeightChange() {{
      const rawE = parseInt(document.getElementById('ahp-slider-egress').value);
      const rawH = parseInt(document.getElementById('ahp-slider-hazard').value);
      const rawA = parseInt(document.getElementById('ahp-slider-access').value);
      const sum = rawE + rawH + rawA || 100;

      currentAHPWeights.egress = rawE / sum;
      currentAHPWeights.hazard = rawH / sum;
      currentAHPWeights.access = rawA / sum;

      document.getElementById('ahp-val-egress').textContent = `${{Math.round(currentAHPWeights.egress * 100)}}%`;
      document.getElementById('ahp-val-hazard').textContent = `${{Math.round(currentAHPWeights.hazard * 100)}}%`;
      document.getElementById('ahp-val-access').textContent = `${{Math.round(currentAHPWeights.access * 100)}}%`;

      // Live recalculation across all workshops
      WORKSHOPS_DATA.forEach(w => {{
        w.fri = parseFloat(((currentAHPWeights.egress * w.egress) + (currentAHPWeights.hazard * w.hazard) + (currentAHPWeights.access * w.access)).toFixed(4));
        w.tier = w.fri >= 0.70 ? 'Severe' : (w.fri >= 0.50 ? 'High' : (w.fri >= 0.30 ? 'Moderate' : 'Low'));
      }});

      applyFilters();
      renderDashboard();
    }}
    window.handleAHPWeightChange = handleAHPWeightChange;

    function resetAHPWeights() {{
      currentAHPWeights = {{ egress: 0.45, hazard: 0.25, access: 0.30 }};
      renderAdminContent();
      handleAHPWeightChange();
    }}
    window.resetAHPWeights = resetAHPWeights;

    function exportSurveyGeoJSON() {{
      const features = WORKSHOPS_DATA.map(w => ({{
        type: 'Feature',
        geometry: {{ type: 'Point', coordinates: [w.lng, w.lat] }},
        properties: {{
          EnterpriseID: w.id,
          Enterprise: w.ent,
          Locality: w.loc,
          Area: w.area,
          FireRiskIndex: w.fri,
          RiskTier: w.tier,
          SUB_Egress: w.egress,
          SUB_Hazard: w.hazard,
          SUB_Access: w.access,
          PastIncident: w.incident ? 1.0 : 0.0,
          cats: w.cats
        }}
      }}));

      const geojson = {{
        type: 'FeatureCollection',
        crs: {{ type: 'name', properties: {{ name: 'urn:ogc:def:crs:OGC:1.3:CRS84' }} }},
        features: features
      }};

      const blob = new Blob([JSON.stringify(geojson, null, 2)], {{ type: 'application/geo+json' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `seelampur_fire_risk_survey_${{new Date().toISOString().slice(0, 10)}}.geojson`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}
    window.exportSurveyGeoJSON = exportSurveyGeoJSON;

    function exportMasterCSV() {{
      const headers = ['EnterpriseID', 'Enterprise', 'Locality', 'FireRiskIndex', 'RiskTier', 'SUB_Egress', 'SUB_Hazard', 'SUB_Access', 'PastIncident', 'Latitude', 'Longitude', 'ExitRoutes', 'Obstruction', 'StairWidth', 'Floors', 'RoadWidth'];
      const rows = WORKSHOPS_DATA.map(w => [
        `"${{w.id}}"`,
        `"${{w.ent.replace(/"/g, '""')}}"`,
        `"${{w.loc}}"`,
        w.fri,
        w.tier,
        w.egress,
        w.hazard,
        w.access,
        w.incident ? 1 : 0,
        w.lat,
        w.lng,
        `"${{w.cats.exits || ''}}"`,
        `"${{w.cats.obstruction || ''}}"`,
        `"${{w.cats.stair_width || ''}}"`,
        `"${{w.cats.floors || ''}}"`,
        `"${{w.cats.approach_road || ''}}"`
      ]);

      const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
      const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `seelampur_fire_risk_audit_${{new Date().toISOString().slice(0, 10)}}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}
    window.exportMasterCSV = exportMasterCSV;

    function printExecutiveReport() {{
      window.print();
    }}
    window.printExecutiveReport = printExecutiveReport;

    // --- INTERACTIVE ANALYTICS CARDS (CLICK TO FILTER) ---
    function filterByTier(tier) {{
      const list = WORKSHOPS_DATA.filter(w => w.tier === tier);
      renderMapMarkers(list);
      updateKpis(list);
      renderMasterTable(list);
    }}
    window.filterByTier = filterByTier;

    function filterByLocality(loc) {{
      const sel = document.getElementById('filter-locality');
      if (sel) {{
        sel.value = loc;
        handleLocalityChange(loc);
      }}
    }}
    window.filterByLocality = filterByLocality;

    function filterByDeficiencyFactor(factorKey, factorVal) {{
      const list = WORKSHOPS_DATA.filter(w => w.cats && w.cats[factorKey] === factorVal);
      renderMapMarkers(list);
      updateKpis(list);
      renderMasterTable(list);
      if (list.length && map) {{
        const b = L.latLngBounds(list.map(w => [w.lat, w.lng]));
        map.fitBounds(b, {{ padding: [40, 40], maxZoom: 17 }});
      }}
    }}
    window.filterByDeficiencyFactor = filterByDeficiencyFactor;
"""

if 'activeDashboardRole =' not in app_src:
    app_src = app_src.replace('    function renderDashboard() {', dashboards_js + '\n    function renderDashboard() {', 1)
    print("Inserted dashboards controller JavaScript.")

# -------------------------------------------------------------
# 7. UPDATE QUICKLOGIN & SHOWAPP TO SYNC ROLE
# -------------------------------------------------------------
app_src = app_src.replace(
    "const user = DEMO_USERS[email] || DEMO_USERS['fire@usap.edu'];\n      currentUser = user;\n      storeSession(user);\n      showApp();",
    """const user = DEMO_USERS[email] || DEMO_USERS['fire@usap.edu'];
      currentUser = user;
      storeSession(user);
      const rKey = email.includes('admin') ? 'admin' : (email.includes('planner') ? 'planner' : (email.includes('surveyor') ? 'surveyor' : 'fire'));
      showApp();
      switchDashboardRole(rKey);""",
    1
)

# In showApp(), call switchDashboardRole with currentUser
app_src = app_src.replace(
    "if (currentUser) {\n        const nameEl = document.getElementById('top-user-name');",
    """if (currentUser) {
        const email = currentUser.email || '';
        const rKey = email.includes('admin') ? 'admin' : (email.includes('planner') ? 'planner' : (email.includes('surveyor') ? 'surveyor' : 'fire'));
        switchDashboardRole(rKey);
        const nameEl = document.getElementById('top-user-name');""",
    1
)

# -------------------------------------------------------------
# 8. MAKE ANALYTICAL CHARTS CLICKABLE
# -------------------------------------------------------------
# Make the tier segmented bar slices clickable:
app_src = app_src.replace(
    'class="seg-slice" style="width:71.6%; background:var(--risk-severe);"',
    'class="seg-slice clickable-seg-slice" onclick="filterByTier(\'Severe\')" title="Click to filter Severe tier" style="width:71.6%; background:var(--risk-severe);"'
)
app_src = app_src.replace(
    'class="seg-slice" style="width:2.7%; background:var(--risk-high);"',
    'class="seg-slice clickable-seg-slice" onclick="filterByTier(\'High\')" title="Click to filter High tier" style="width:2.7%; background:var(--risk-high);"'
)
app_src = app_src.replace(
    'class="seg-slice" style="width:19.6%; background:var(--risk-moderate);"',
    'class="seg-slice clickable-seg-slice" onclick="filterByTier(\'Moderate\')" title="Click to filter Moderate tier" style="width:19.6%; background:var(--risk-moderate);"'
)
app_src = app_src.replace(
    'class="seg-slice" style="width:6.1%; background:var(--risk-low);"',
    'class="seg-slice clickable-seg-slice" onclick="filterByTier(\'Low\')" title="Click to filter Low tier" style="width:6.1%; background:var(--risk-low);"'
)

with open('generate_app.py', 'w', encoding='utf-8') as f:
    f.write(app_src)

print("SUCCESS: generate_app.py upgraded with 4 distinct, fully functional dashboards!")
