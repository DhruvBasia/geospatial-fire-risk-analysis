# -*- coding: utf-8 -*-
"""
add_hose_calculator.py
Adds Option 1: Fire Hose Relay & 'Narrow Gali' Reach Calculator to generate_app.py.
Features:
- Identifies optimal Fire Tender Staging Point on nearest wide arterial road.
- Calculates exact manual alley distance through narrow galiyan.
- Calculates required 30m standard Delhi Fire Service delivery hose lengths.
- Estimates manual hose deployment time with alley obstruction penalties.
- Performs hydraulic pressure analysis (branchpipe nozzle 3.5 bar + friction loss + elevation loss).
- Flags auxiliary portable booster pump requirement when distance > 150m.
- Compares deployment delay against flashover window.
- Visualizes the hose path on Leaflet with numbered coupling node markers every 30m.
- Zero emojis (100% clean vector SVGs and typography).
"""

import sys

def main():
    with open('generate_app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS for Hose Relay Modal & Map Layers
    old_css_anchor = '/* Crisp Tile Rendering */'
    new_css = '''/* =========================================================
       8. FIRE HOSE RELAY & ALLEY REACH ASSESSMENT STYLES
       ========================================================= */
    .hose-modal {{
      background: #ffffff;
      border-radius: var(--radius-md);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
      border: 1px solid var(--border);
      width: 820px;
      max-width: 95vw;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      font-family: var(--font);
    }}

    .hose-staging-banner {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: var(--radius-sm);
      margin: 16px 20px 0;
      padding: 12px 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }}

    .staging-banner-icon {{
      width: 36px;
      height: 36px;
      border-radius: var(--radius-sm);
      background: #16a34a;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .staging-banner-label {{
      font-size: 10px;
      font-weight: 800;
      color: #15803d;
      letter-spacing: 0.04em;
    }}

    .staging-banner-street {{
      font-size: 14px;
      font-weight: 800;
      color: var(--navy-900);
      margin: 2px 0;
    }}

    .staging-banner-desc {{
      font-size: 11px;
      color: #334155;
      line-height: 1.4;
    }}

    .hose-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      padding: 16px 20px 0;
    }}

    .hose-kpi-card {{
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
    }}

    .hose-kpi-val {{
      font-size: 20px;
      font-weight: 800;
      color: var(--navy-900);
    }}

    .hose-kpi-lbl {{
      font-size: 10px;
      font-weight: 700;
      color: var(--text-secondary);
      margin: 2px 0 4px;
      text-transform: uppercase;
    }}

    .hose-kpi-sub {{
      font-size: 10px;
      color: var(--text-muted);
      line-height: 1.3;
    }}

    .hose-analysis-section, .hose-sop-section {{
      padding: 16px 20px 0;
    }}

    .hose-section-title {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--navy-900);
      letter-spacing: 0.03em;
      margin-bottom: 8px;
    }}

    .hose-hazards-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}

    .hose-hazard-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 10px 12px;
    }}

    .hazard-card-head {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
      font-size: 11px;
      color: var(--navy-900);
    }}

    .hazard-card-badge {{
      font-size: 9px;
      font-weight: 800;
      padding: 2px 5px;
      border-radius: 3px;
      background: #e2e8f0;
      color: #334155;
      text-transform: uppercase;
    }}

    .hazard-card-badge.red {{
      background: #fef2f2;
      color: #b91c1c;
      border: 1px solid #fecaca;
    }}

    .hazard-card-badge.orange {{
      background: #fff7ed;
      color: #c2410c;
      border: 1px solid #fed7aa;
    }}

    .hazard-card-badge.green {{
      background: #f0fdf4;
      color: #15803d;
      border: 1px solid #bbf7d0;
    }}

    .hazard-card-body {{
      font-size: 11px;
      color: #475569;
      line-height: 1.35;
    }}

    .hose-sop-steps {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .sop-step-item {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      font-size: 11px;
      line-height: 1.35;
      background: #f8fafc;
      padding: 7px 10px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
    }}

    .sop-step-num {{
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--navy-900);
      color: #ffffff;
      font-size: 10px;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 1px;
    }}

    .sop-step-text {{
      flex: 1;
      color: #334155;
    }}

    .btn-hose-calc-rail {{
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 8px 12px;
      background: #f0fdf4;
      color: #15803d;
      border: 1px solid #bbf7d0;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      margin-top: 6px;
      transition: all 0.15s ease;
    }}

    .btn-hose-calc-rail:hover {{
      background: #dcfce7;
      border-color: #86efac;
    }}

    .staging-truck-marker {{
      background: #dc2626;
      color: #ffffff;
      border: 2px solid #ffffff;
      border-radius: 6px;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
      cursor: pointer;
    }}

    .hose-coupling-node {{
      background: #0284c7;
      color: #ffffff;
      border: 2px solid #ffffff;
      border-radius: 50%;
      width: 22px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 9px;
      font-weight: 800;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
      cursor: pointer;
    }}

    .branchpipe-nozzle-marker {{
      background: #ea580c;
      color: #ffffff;
      border: 2px solid #ffffff;
      border-radius: 50%;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
      cursor: pointer;
    }}

    /* Crisp Tile Rendering */'''

    if old_css_anchor not in content:
        print("ERROR: old_css_anchor not found!")
        sys.exit(1)
    content = content.replace(old_css_anchor, new_css, 1)

    # 2. Add Hose Calculator button in the Preview Card (left rail)
    old_preview_buttons = '''            <button type="button" class="btn-fire-emergency-hero" onclick="triggerShopFireIncident(selectedWorkshop)">
              <svg class="svg-icon" viewBox="0 0 24 24" style="color:#ffffff;"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
              <span>Simulate Fire Incident (Live Vehicle Tracking)</span>
            </button>'''

    new_preview_buttons = '''            <button type="button" class="btn-fire-emergency-hero" onclick="triggerShopFireIncident(selectedWorkshop)">
              <svg class="svg-icon" viewBox="0 0 24 24" style="color:#ffffff;"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
              <span>Simulate Fire Incident (Live Vehicle Tracking)</span>
            </button>

            <button type="button" class="btn-hose-calc-rail" onclick="openHoseRelayModal(selectedWorkshop)">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/><circle cx="12" cy="12" r="2"/></svg>
              <span>Calculate Fire Hose Reach &amp; Staging Point</span>
            </button>'''

    if old_preview_buttons not in content:
        print("ERROR: old_preview_buttons not found!")
        sys.exit(1)
    content = content.replace(old_preview_buttons, new_preview_buttons, 1)

    # 3. Add Hose Calculator button in Workshop Detail Modal footer
    old_modal_footer_btn = '''          <button type="button" class="btn-action hospital" onclick="closeWorkshopModal(); triggerLiveDispatch('hospital')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="6.5" y1="10" x2="10.5" y2="10"/><line x1="8.5" y1="8" x2="8.5" y2="12"/></svg>
            <span>Hospital Ambulance Route</span>
          </button>'''

    new_modal_footer_btn = '''          <button type="button" class="btn-action hospital" onclick="closeWorkshopModal(); triggerLiveDispatch('hospital')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="6.5" y1="10" x2="10.5" y2="10"/><line x1="8.5" y1="8" x2="8.5" y2="12"/></svg>
            <span>Hospital Ambulance Route</span>
          </button>
          <button type="button" class="btn-action hose-calc" onclick="closeWorkshopModal(); openHoseRelayModal(selectedWorkshop);" style="background:#0e7490; color:#ffffff; font-weight:700;">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/><circle cx="12" cy="12" r="2"/></svg>
            <span>Hose Reach &amp; Staging Analysis</span>
          </button>'''

    if old_modal_footer_btn not in content:
        print("ERROR: old_modal_footer_btn not found!")
        sys.exit(1)
    content = content.replace(old_modal_footer_btn, new_modal_footer_btn, 1)

    # 4. Insert the Hose Relay Modal HTML right after workshop-modal-overlay
    old_modal_overlay_end = '      <div class="modal-footer">\n        <div class="modal-actions-left">'
    # Let's find workshop-modal-overlay closing </div>
    target_close = '        <button type="button" class="btn-modal-dismiss" onclick="closeWorkshopModal()">Close</button>\n      </div>\n    </div>\n  </div>'
    target_close_crlf = '        <button type="button" class="btn-modal-dismiss" onclick="closeWorkshopModal()">Close</button>\r\n      </div>\r\n    </div>\r\n  </div>'

    hose_modal_html = '''

  <!-- =========================================================
       FIRE HOSE RELAY & ALLEY REACH ASSESSMENT MODAL
       ========================================================= -->
  <div id="hose-relay-modal-overlay" class="modal-overlay" onclick="handleHoseOverlayClick(event)">
    <div class="hose-modal" role="dialog" aria-modal="true" aria-labelledby="hose-title">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="modal-header-left">
          <div class="modal-eyebrow-row">
            <span class="eyebrow" style="color:var(--teal-600);">DELHI FIRE SERVICE TACTICAL ASSESSMENT</span>
            <span id="hose-workshop-id" class="modal-id-pill">ID</span>
            <span id="hose-road-badge" class="badge-tier Severe">Narrow Lane &lt;3m</span>
          </div>
          <h2 id="hose-title" class="modal-title">Fire Hose Reach &amp; Tender Staging Feasibility</h2>
          <div class="modal-meta-row">
            <span id="hose-workshop-name" style="font-weight:700; color:var(--navy-900);">Workshop Name</span>
            <span>•</span>
            <span id="hose-workshop-loc">Locality</span>
          </div>
        </div>
        <button type="button" class="modal-close-btn" onclick="closeHoseRelayModal()" title="Close dialog">✕</button>
      </div>

      <!-- Core Staging Banner -->
      <div class="hose-staging-banner">
        <div class="staging-banner-icon">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>
        </div>
        <div class="staging-banner-content">
          <div class="staging-banner-label">RECOMMENDED HEAVY TENDER STAGING LOCATION</div>
          <div class="staging-banner-street" id="hose-staging-street">Grand Trunk Road (GT Road Corridor) • Motorable Width ≥ 15m</div>
          <div class="staging-banner-desc" id="hose-staging-desc">Heavy water tender (2.5m wide) cannot enter internal gali. Must park at arterial staging point and run manual hose lines.</div>
        </div>
      </div>

      <!-- 4 Key Hydraulic & Operational KPIs -->
      <div class="hose-kpi-grid">
        <div class="hose-kpi-card">
          <span class="hose-kpi-val num-tnum" id="hose-kpi-dist">175 m</span>
          <span class="hose-kpi-lbl">Manual Alley Distance</span>
          <span class="hose-kpi-sub">Winding gali path to entry door</span>
        </div>
        <div class="hose-kpi-card">
          <span class="hose-kpi-val num-tnum" id="hose-kpi-hoses" style="color:#0284c7;">6 Lengths</span>
          <span class="hose-kpi-lbl">Hose Lines Required</span>
          <span class="hose-kpi-sub">Standard 30m DFS delivery hoses (180m total)</span>
        </div>
        <div class="hose-kpi-card">
          <span class="hose-kpi-val num-tnum" id="hose-kpi-time" style="color:#dc2626;">6m 30s</span>
          <span class="hose-kpi-lbl">Est. Deployment Time</span>
          <span class="hose-kpi-sub" id="hose-kpi-time-sub">2-crew coupling + obstruction penalty</span>
        </div>
        <div class="hose-kpi-card">
          <span class="hose-kpi-val num-tnum" id="hose-kpi-pressure" style="color:#ea580c;">6.65 bar</span>
          <span class="hose-kpi-lbl">Pump Discharge Pressure</span>
          <span class="hose-kpi-sub" id="hose-kpi-pressure-sub">3.5b nozzle + 2.1b friction + 1.0b elevation</span>
        </div>
      </div>

      <!-- Tactical Risk & Warning Analysis Cards -->
      <div class="hose-analysis-section">
        <div class="hose-section-title">Critical Tactical Hazards &amp; Hydraulic Checks</div>
        <div class="hose-hazards-grid">
          
          <div class="hose-hazard-card" id="hazard-card-access">
            <div class="hazard-card-head">
              <span class="hazard-card-badge red">CRITICAL ACCESS</span>
              <strong>Approach Road &lt;3m</strong>
            </div>
            <div class="hazard-card-body" id="hazard-body-access">
              Internal lane strictly under 3 metres. Heavy water tenders cannot enter. 100% of firefighting water must be relayed via manual delivery hose lines from the arterial staging point.
            </div>
          </div>

          <div class="hose-hazard-card" id="hazard-card-booster">
            <div class="hazard-card-head">
              <span class="hazard-card-badge" id="hazard-badge-booster">PRESSURE CHECK</span>
              <strong id="hazard-title-booster">Booster Pump Requirement</strong>
            </div>
            <div class="hazard-card-body" id="hazard-body-booster">
              Distance exceeds 150m threshold. Significant friction loss across multiple couplings. Auxiliary portable firefighting booster pump required at midpoint to maintain minimum 3.5 bar branchpipe stream.
            </div>
          </div>

          <div class="hose-hazard-card" id="hazard-card-obstruction">
            <div class="hazard-card-head">
              <span class="hazard-card-badge" id="hazard-badge-obst">ALLEY CLEARANCE</span>
              <strong id="hazard-title-obst">Evacuation &amp; Hose Route Obstruction</strong>
            </div>
            <div class="hazard-card-body" id="hazard-body-obst">
              Severe obstruction detected. Dense textile scrap bales and raw material inventory clog the gali corridor, creating hose kink hazards, acute puncture risks, and +90s coupling delay.
            </div>
          </div>

          <div class="hose-hazard-card" id="hazard-card-flashover">
            <div class="hazard-card-head">
              <span class="hazard-card-badge red">FLASHOVER WINDOW</span>
              <strong>Deployment vs Flashover Window</strong>
            </div>
            <div class="hazard-card-body" id="hazard-body-flashover">
              Textile &amp; solvent workshop flashover typically occurs within 5–7 minutes. Estimated hose laying time means water application may arrive near or post flashover. Early alarm is vital.
            </div>
          </div>

        </div>
      </div>

      <!-- Tactical Deployment SOP Checklist for Incident Commander -->
      <div class="hose-sop-section">
        <div class="hose-section-title">Delhi Fire Service SOP: Alley Hose Deployment Sequence</div>
        <div class="hose-sop-steps">
          <div class="sop-step-item">
            <span class="sop-step-num">1</span>
            <div class="sop-step-text">
              <strong>Tender Positioning:</strong> Stage DFS Water Tender at designated arterial road. Chock wheels, engage PTO pump, deploy warning markers.
            </div>
          </div>
          <div class="sop-step-item">
            <span class="sop-step-num">2</span>
            <div class="sop-step-text">
              <strong>Hose Relay Rollout:</strong> Run standard 63mm delivery hoses in dual-crew relay through alleyway. Ensure male instantaneous coupling faces toward fire.
            </div>
          </div>
          <div class="sop-step-item">
            <span class="sop-step-num">3</span>
            <div class="sop-step-text">
              <strong>Pressure Calibration:</strong> Set tender throttle to <span id="sop-pump-pressure" style="font-weight:800; color:var(--navy-900);">6.65 bar</span>. Bleed air at branchpipe before entry into workshop compartment.
            </div>
          </div>
          <div class="sop-step-item">
            <span class="sop-step-num">4</span>
            <div class="sop-step-text">
              <strong>Branchpipe Attack:</strong> Advance attack crew with fog nozzle set to 30° protective cone for thermal radiation shielding at workshop entrance.
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Buttons -->
      <div class="modal-footer">
        <div class="modal-actions-left">
          <button type="button" class="btn-action fire" onclick="closeHoseRelayModal(); triggerLiveDispatch('fire');">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>
            <span>Simulate Live Fire Tender Turnout</span>
          </button>
          <button type="button" class="btn-action" onclick="closeHoseRelayModal(); focusHoseRelayOnMap();">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
            <span>View Hose Path on Map</span>
          </button>
        </div>
        <button type="button" class="btn-modal-dismiss" onclick="closeHoseRelayModal()">Close</button>
      </div>
    </div>
  </div>'''

    if target_close in content:
        content = content.replace(target_close, target_close + hose_modal_html, 1)
    elif target_close_crlf in content:
        content = content.replace(target_close_crlf, target_close_crlf + hose_modal_html, 1)
    else:
        print("ERROR: target_close not found!")
        sys.exit(1)

    # 5. Insert JavaScript logic for Hose Relay Calculator
    js_anchor = '// =========================================================\n    // ANALYTICS DASHBOARD'
    js_anchor_crlf = '// =========================================================\r\n    // ANALYTICS DASHBOARD'

    hose_js_code = '''// =========================================================
    // FIRE HOSE RELAY & ALLEY REACH ENGINE (DELHI FIRE SERVICE)
    // =========================================================
    const ARTERIAL_STAGING_ROADS = [
      {{ name: 'Grand Trunk Road (GT Road Corridor)', widthM: 18.0, lat: 28.6688, lng: 77.2655, desc: '6-Lane Divided Arterial • Heavy Tender Staging & Water Relay Base' }},
      {{ name: 'Main 66-Feet Commercial Road', widthM: 12.0, lat: 28.6725, lng: 77.2725, desc: '4-Lane Commercial Corridor • Seelampur East Staging Hub' }},
      {{ name: 'Gandhi Nagar Main Market Road', widthM: 9.5, lat: 28.6580, lng: 77.2685, desc: '2-Lane Commercial Corridor • Textile Cluster Staging Base' }},
      {{ name: 'Swami Dayanand Marg (Shanti Mohalla Entry)', widthM: 10.0, lat: 28.6640, lng: 77.2785, desc: 'Primary Motorable Arterial for Textile Cluster' }},
      {{ name: 'Subhash Road / Kanti Nagar Link', widthM: 8.5, lat: 28.6775, lng: 77.2765, desc: 'Secondary Motorable Access for Northern Fabrication Units' }},
      {{ name: 'Brahmpuri Main Road', widthM: 9.0, lat: 28.6740, lng: 77.2680, desc: 'Arterial Road North of Seelampur Market' }},
      {{ name: 'Mahila Colony Pushta Road Link', widthM: 11.0, lat: 28.6550, lng: 77.2650, desc: 'Pushta Embankment Road • Direct Access to South Galis' }},
      {{ name: 'Dharampura Main Market Road', widthM: 8.5, lat: 28.6610, lng: 77.2635, desc: 'West Gandhi Nagar Motorable Entry' }},
      {{ name: 'Geeta Colony 7-Block Link Road', widthM: 9.0, lat: 28.6520, lng: 77.2705, desc: 'Southern Approach Arterial' }}
    ];

    let hoseRelayLayers = [];
    let currentHosePlan = null;

    function findClosestStagingRoad(lat, lng) {{
      let closest = ARTERIAL_STAGING_ROADS[0];
      let minD = Infinity;
      ARTERIAL_STAGING_ROADS.forEach(road => {{
        const d = getDistanceMeters(lat, lng, road.lat, road.lng);
        if (d < minD) {{
          minD = d;
          closest = road;
        }}
      }});
      return {{ road: closest, directDistanceM: minD }};
    }}

    function calculateHoseRelayData(w) {{
      const stagingInfo = findClosestStagingRoad(w.lat, w.lng);
      // Winding gali factor: ~1.35x Euclidean distance through Seelampur's narrow alley network
      const distM = Math.max(35, Math.round(stagingInfo.directDistanceM * 1.35));
      const hoseLen = 30; // 30m standard DFS delivery hose
      const numHoses = Math.ceil(distM / hoseLen);
      const totalCapacityM = numHoses * hoseLen;

      // Friction loss: ~0.35 bar per 30m hose at 500 L/min
      const frictionLoss = parseFloat((numHoses * 0.35).toFixed(2));

      // Elevation loss based on surveyed floors
      let floors = 1;
      const flCat = w.cats.floors || '';
      if (flCat.includes('4+')) floors = 4;
      else if (flCat.includes('2-3')) floors = 2.5;
      const elevationLoss = parseFloat(Math.max(0, (floors - 1) * 0.35).toFixed(2));

      const nozzlePressure = 3.5; // standard branchpipe pressure
      const pumpPressure = parseFloat((nozzlePressure + frictionLoss + elevationLoss).toFixed(2));

      // Deployment time calculation
      const baseTimePerHose = 45; // seconds per 30m length for 2 firefighters
      let obstPenalty = 0;
      const obstCat = w.cats.obstruction || '';
      if (obstCat === 'Blocked') obstPenalty = 90;
      else if (obstCat === 'Partially blocked') obstPenalty = 45;

      const appRoadCat = w.cats.approach_road || '';
      const widthPenalty = appRoadCat === '<3m' ? 30 : 0;

      const totalDeploySec = (numHoses * baseTimePerHose) + obstPenalty + widthPenalty;
      const deployMins = Math.floor(totalDeploySec / 60);
      const deploySecs = totalDeploySec % 60;

      const boosterRequired = distM > 150 || pumpPressure > 6.5;

      return {{
        workshop: w,
        stagingRoad: stagingInfo.road,
        distM,
        numHoses,
        totalCapacityM,
        frictionLoss,
        elevationLoss,
        pumpPressure,
        totalDeploySec,
        deployTimeString: `${{deployMins}}m ${{deploySecs < 10 ? '0' : ''}}${{deploySecs}}s`,
        boosterRequired,
        obstCat,
        appRoadCat,
        floors
      }};
    }}

    function openHoseRelayModal(w) {{
      const unit = w || selectedWorkshop || WORKSHOPS_DATA[0];
      selectedWorkshop = unit;
      const plan = calculateHoseRelayData(unit);
      currentHosePlan = plan;

      document.getElementById('hose-workshop-id').textContent = unit.id;
      document.getElementById('hose-workshop-name').textContent = unit.ent;
      document.getElementById('hose-workshop-loc').textContent = `${{unit.loc}} • ${{unit.area}}`;
      document.getElementById('hose-road-badge').textContent = `Lane: ${{unit.cats.approach_road || '<3m'}}`;

      document.getElementById('hose-staging-street').textContent = `${{plan.stagingRoad.name}} • Width ≥ ${{plan.stagingRoad.widthM}}m`;
      document.getElementById('hose-staging-desc').textContent = `${{plan.stagingRoad.desc}}. Heavy DFS water tender stages here; crew lays manual delivery lines into gali.`;

      document.getElementById('hose-kpi-dist').textContent = `${{plan.distM}} m`;
      document.getElementById('hose-kpi-hoses').textContent = `${{plan.numHoses}} Lengths`;
      document.getElementById('hose-kpi-time').textContent = plan.deployTimeString;
      document.getElementById('hose-kpi-pressure').textContent = `${{plan.pumpPressure}} bar`;

      document.getElementById('hose-kpi-time-sub').textContent = `${{plan.numHoses}} couplings (${{plan.numHoses * 45}}s) + ${{plan.obstCat === 'Blocked' ? '90s scrap blockage' : '30s width buffer'}}`;
      document.getElementById('hose-kpi-pressure-sub').textContent = `3.5b nozzle + ${{plan.frictionLoss}}b friction + ${{plan.elevationLoss}}b elev (${{plan.floors}} fl)`;
      document.getElementById('sop-pump-pressure').textContent = `${{plan.pumpPressure}} bar`;

      // Update Booster hazard card
      const boosterBadge = document.getElementById('hazard-badge-booster');
      const boosterBody = document.getElementById('hazard-body-booster');
      if (plan.boosterRequired) {{
        boosterBadge.className = 'hazard-card-badge red';
        boosterBadge.textContent = 'BOOSTER MANDATORY';
        boosterBody.textContent = `Relay distance (${{plan.distM}}m) exceeds 150m. Total pressure demand (${{plan.pumpPressure}} bar) causes extreme nozzle decay. Auxiliary portable booster pump required at ${{Math.round(plan.distM / 2)}}m midpoint.`;
      }} else {{
        boosterBadge.className = 'hazard-card-badge green';
        boosterBadge.textContent = 'DIRECT PUMP OK';
        boosterBody.textContent = `Distance (${{plan.distM}}m) is within 150m threshold. Direct pressure from tender pump (${{plan.pumpPressure}} bar) is sufficient to maintain standard 3.5 bar branchpipe fog jet.`;
      }}

      // Update Obstruction hazard card
      const obstBadge = document.getElementById('hazard-badge-obst');
      const obstBody = document.getElementById('hazard-body-obst');
      if (plan.obstCat === 'Blocked') {{
        obstBadge.className = 'hazard-card-badge red';
        obstBadge.textContent = 'HIGH BLOCKAGE';
        obstBody.textContent = 'Severe alley clutter detected. Dense fabric scrap bales and discarded machinery block the passage. Critical hose kink and puncture hazard (+90s delay).';
      }} else if (plan.obstCat === 'Partially blocked') {{
        obstBadge.className = 'hazard-card-badge orange';
        obstBadge.textContent = 'PARTIAL BLOCKAGE';
        obstBody.textContent = 'Partial inventory clutter in lane. Couplings must be dragged around obstacles, delaying line establishment by +45s.';
      }} else {{
        obstBadge.className = 'hazard-card-badge green';
        obstBadge.textContent = 'ALLEY CLEAR';
        obstBody.textContent = 'Lane is clear of heavy inventory piles. Rapid straight rollout feasible with standard 45s per hose coupling efficiency.';
      }}

      // Update Flashover comparison
      const flashoverBody = document.getElementById('hazard-body-flashover');
      if (plan.totalDeploySec > 330) {{
        flashoverBody.textContent = `ALERT: Est. hose deployment time (${{plan.deployTimeString}}) EXCEEDS flashover threshold (5m). Fire may transition to full flashover before water reaches branchpipe. Immediate life evacuation is paramount!`;
      }} else {{
        flashoverBody.textContent = `Estimated hose deployment time (${{plan.deployTimeString}}) is within early flashover window (5–7m). Rapid suppression possible if response turnout is under 6 minutes.`;
      }}

      // Render On-Map Hose Visuals in the background
      renderHoseRelayOnMap(plan);

      const overlay = document.getElementById('hose-relay-modal-overlay');
      if (overlay) overlay.classList.add('active');
    }}
    window.openHoseRelayModal = openHoseRelayModal;

    function closeHoseRelayModal() {{
      const overlay = document.getElementById('hose-relay-modal-overlay');
      if (overlay) overlay.classList.remove('active');
    }}
    window.closeHoseRelayModal = closeHoseRelayModal;

    function handleHoseOverlayClick(e) {{
      if (e.target && e.target.id === 'hose-relay-modal-overlay') {{
        closeHoseRelayModal();
      }}
    }}
    window.handleHoseOverlayClick = handleHoseOverlayClick;

    function renderHoseRelayOnMap(plan) {{
      // Clear previous hose layers
      hoseRelayLayers.forEach(l => {{ if (map && map.hasLayer(l)) map.removeLayer(l); }});
      hoseRelayLayers = [];

      const start = [plan.stagingRoad.lat, plan.stagingRoad.lng];
      const end = [plan.workshop.lat, plan.workshop.lng];

      // Generate intermediate points along winding gali
      const numSegments = plan.numHoses;
      const hoseCoords = [start];
      const couplingPoints = [];

      for (let i = 1; i < numSegments; i++) {{
        const r = i / numSegments;
        const lat = start[0] + (end[0] - start[0]) * r + (Math.sin(i * 1.8) * 0.00035);
        const lng = start[1] + (end[1] - start[1]) * r + (Math.cos(i * 1.8) * 0.00035);
        hoseCoords.push([lat, lng]);
        couplingPoints.push({{
          idx: i,
          lat,
          lng,
          distM: i * 30,
          pressure: parseFloat((plan.pumpPressure - (i * 0.35)).toFixed(2))
        }});
      }}
      hoseCoords.push(end);

      // Casing & Hose Line (Water Cyan/Blue Dashed)
      const casing = L.polyline(hoseCoords, {{ color: '#ffffff', weight: 8, opacity: 0.95 }}).addTo(map);
      const hoseLine = L.polyline(hoseCoords, {{ color: '#0284c7', weight: 5, dashArray: '8, 8', opacity: 0.95 }}).addTo(map);
      hoseRelayLayers.push(casing, hoseLine);

      // Staging Truck Marker (Arterial Road)
      const truckIcon = L.divIcon({{
        className: 'custom-staging-marker',
        html: `
          <div class="staging-truck-marker" title="Tender Staging Point">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#ffffff" stroke-width="2.2"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      }});
      const stagingMarker = L.marker(start, {{ icon: truckIcon, zIndexOffset: 2500 }})
        .bindPopup(`<strong>${{plan.stagingRoad.name}}</strong><br>DFS Water Tender Staging Point (Width ≥ ${{plan.stagingRoad.widthM}}m)<br>Pump Pressure: ${{plan.pumpPressure}} bar`)
        .addTo(map);
      hoseRelayLayers.push(stagingMarker);

      // Numbered Hose Coupling Nodes every 30m
      couplingPoints.forEach(cp => {{
        const nodeIcon = L.divIcon({{
          className: 'custom-coupling-marker',
          html: `<div class="hose-coupling-node" title="Hose Coupling #${{cp.idx}}">${{cp.idx}}</div>`,
          iconSize: [22, 22],
          iconAnchor: [11, 11]
        }});
        const cpMarker = L.marker([cp.lat, cp.lng], {{ icon: nodeIcon, zIndexOffset: 2600 }})
          .bindTooltip(`Coupling #${{cp.idx}} (${{cp.distM}}m)<br>Pressure: ${{cp.pressure}} bar`, {{ className: 'custom-map-tooltip' }})
          .addTo(map);
        hoseRelayLayers.push(cpMarker);
      }});

      // Target Nozzle Marker at Workshop Door
      const nozzleIcon = L.divIcon({{
        className: 'custom-nozzle-marker',
        html: `
          <div class="branchpipe-nozzle-marker" title="Branchpipe Nozzle at Entry">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="#ffffff"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      }});
      const nozzleMarker = L.marker(end, {{ icon: nozzleIcon, zIndexOffset: 2700 }})
        .bindPopup(`<strong>Target Entry: ${{plan.workshop.ent}}</strong><br>Nozzle Discharge: 3.5 bar<br>Relay Length: ${{plan.distM}}m (${{plan.numHoses}} hoses)`)
        .addTo(map);
      hoseRelayLayers.push(nozzleMarker);
    }}

    function focusHoseRelayOnMap() {{
      if (hoseRelayLayers.length && map) {{
        const group = L.featureGroup(hoseRelayLayers);
        map.fitBounds(group.getBounds(), {{
          paddingTopLeft: [60, 60],
          paddingBottomRight: [60, 60]
        }});
      }}
    }}
    window.focusHoseRelayOnMap = focusHoseRelayOnMap;

    '''

    if js_anchor in content:
        content = content.replace(js_anchor, hose_js_code + js_anchor, 1)
    elif js_anchor_crlf in content:
        content = content.replace(js_anchor_crlf, hose_js_code + js_anchor_crlf, 1)
    else:
        print("ERROR: js_anchor not found!")
        sys.exit(1)

    with open('generate_app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: generate_app.py updated with Fire Hose Relay & Reach Calculator!")

if __name__ == '__main__':
    main()
