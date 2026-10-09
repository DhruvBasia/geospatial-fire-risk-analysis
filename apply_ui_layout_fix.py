# -*- coding: utf-8 -*-
import sys

def main():
    with open('generate_app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update CSS: Make map bigger on right (1fr), left rail 460px
    old_css_grid = '''.map-row-grid {{
      display: grid;
      grid-template-columns: 560px 1fr;
      gap: 24px;
      align-items: start;
    }}

    /* Square Map Card */
    .map-widget-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      transition: all 0.3s ease;
    }}'''

    new_css_grid = '''.map-row-grid {{
      display: grid;
      grid-template-columns: 460px 1fr;
      gap: 20px;
      align-items: start;
    }}

    .left-control-column {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    /* Big Spacious Map Card on the Right Side */
    .map-widget-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      height: 750px;
      min-height: 750px;
      position: sticky;
      top: 16px;
      transition: all 0.3s ease;
    }}'''

    if old_css_grid not in content:
        print("ERROR: old_css_grid not found!")
        sys.exit(1)
    content = content.replace(old_css_grid, new_css_grid, 1)

    # 2. Update map container height in CSS & Add rail card styles
    old_map_container_css = '''    /* Map Viewport in Square Mode */
    #map-container {{
      width: 100%;
      height: 490px;
      min-height: 490px;
      background: #e2e8f0;
      position: relative;
    }}'''

    new_map_container_css = '''    /* Big Map Viewport on Right Side */
    #map-container {{
      width: 100%;
      height: calc(750px - 49px - 41px);
      min-height: calc(750px - 49px - 41px);
      background: #e2e8f0;
      position: relative;
    }}

    /* Analytics Rail Card (Left Column) */
    .analytics-rail-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 16px;
      box-shadow: var(--shadow-sm);
    }}

    .rail-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }}

    .rail-card-title {{
      font-size: 14px;
      font-weight: 800;
      color: var(--navy-900);
      margin-top: 2px;
    }}

    .rail-total-badge {{
      font-size: 11px;
      font-weight: 800;
      background: #f1f5f9;
      color: var(--navy-900);
      padding: 3px 8px;
      border-radius: var(--radius-sm);
    }}

    .rail-stat-section {{
      margin-bottom: 12px;
    }}

    .rail-section-label {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 10px;
      font-weight: 700;
      color: var(--text-secondary);
      margin-bottom: 5px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    .rail-segmented-bar {{
      display: flex;
      height: 8px;
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 7px;
      background: #e2e8f0;
    }}

    .rail-tier-chips {{
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
    }}

    .rail-chip {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: #f8fafc;
      border: 1px solid var(--border);
      color: var(--navy-900);
    }}

    .chip-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }}

    .rail-locality-list {{
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}

    .rail-locality-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 3px 6px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: background 0.15s ease;
    }}

    .rail-locality-row:hover {{
      background: #f1f5f9;
    }}

    .rail-loc-name {{
      font-size: 11px;
      font-weight: 700;
      color: var(--navy-900);
      width: 95px;
      white-space: nowrap;
    }}

    .rail-loc-bar-wrap {{
      flex: 1;
      height: 6px;
      background: #f1f5f9;
      border-radius: 3px;
      overflow: hidden;
    }}

    .rail-loc-bar {{
      height: 100%;
      border-radius: 3px;
    }}

    .rail-loc-score {{
      font-size: 11px;
      font-weight: 800;
      width: 32px;
      text-align: right;
    }}

    .rail-driver-list {{
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}

    .rail-driver-item {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .rail-driver-head {{
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-primary);
    }}

    .rail-driver-bar-track {{
      height: 4px;
      background: #f1f5f9;
      border-radius: 2px;
      overflow: hidden;
    }}

    .rail-driver-bar-fill {{
      height: 100%;
      border-radius: 2px;
    }}

    .map-badge-count {{
      font-size: 11px;
      font-weight: 700;
      background: rgba(255, 255, 255, 0.12);
      padding: 3px 8px;
      border-radius: 4px;
      color: #7dd3fc;
    }}'''

    if old_map_container_css not in content:
        print("ERROR: old_map_container_css not found!")
        sys.exit(1)
    content = content.replace(old_map_container_css, new_map_container_css, 1)

    # 3. Locate the map-row-grid block and replace it
    start_str = '<div class="map-row-grid">'
    end_str = '<!-- =========================================================\n           LOWER SECTION: ANALYTICS DASHBOARD'
    
    start_pos = content.find(start_str)
    if start_pos == -1:
        print("ERROR: start_str not found!")
        sys.exit(1)
        
    end_pos = content.find(end_str, start_pos)
    if end_pos == -1:
        # try CRLF
        end_str_crlf = '<!-- =========================================================\r\n           LOWER SECTION: ANALYTICS DASHBOARD'
        end_pos = content.find(end_str_crlf, start_pos)
        if end_pos == -1:
            print("ERROR: end_pos not found!")
            sys.exit(1)

    new_html_grid = '''<div class="map-row-grid">
        <!-- Left Column: Rich Analytics, Unit Inspector & Spatial Filters -->
        <div class="left-control-column">
          
          <!-- Card 1: Area Risk Analytics & Drivers (Graphs) -->
          <div class="analytics-rail-card">
            <div class="rail-card-header">
              <div>
                <span class="eyebrow" style="color:var(--teal-600);">CLUSTER VULNERABILITY PROFILE</span>
                <div class="rail-card-title">Area Risk Analytics &amp; Drivers</div>
              </div>
              <span class="rail-total-badge" id="rail-total-count">158 Units</span>
            </div>

            <!-- Risk Tier Segmented Progress Bar -->
            <div class="rail-stat-section">
              <div class="rail-section-label">
                <span>Risk Tier Distribution</span>
                <span style="font-weight:800; color:var(--risk-severe);" id="rail-severe-pct">72.2% Severe</span>
              </div>
              <div class="rail-segmented-bar">
                <div style="width:72.2%; background:var(--risk-severe);" title="Severe: 114 units (72.2%)"></div>
                <div style="width:21.5%; background:var(--risk-high);" title="High: 34 units (21.5%)"></div>
                <div style="width:3.8%; background:var(--risk-moderate);" title="Moderate: 6 units (3.8%)"></div>
                <div style="width:2.5%; background:var(--risk-low);" title="Low: 4 units (2.5%)"></div>
              </div>
              <div class="rail-tier-chips">
                <span class="rail-chip"><span class="chip-dot" style="background:var(--risk-severe);"></span>Sev: <strong id="rail-cnt-severe">114</strong></span>
                <span class="rail-chip"><span class="chip-dot" style="background:var(--risk-high);"></span>High: <strong id="rail-cnt-high">34</strong></span>
                <span class="rail-chip"><span class="chip-dot" style="background:var(--risk-moderate);"></span>Mod: <strong id="rail-cnt-mod">6</strong></span>
                <span class="rail-chip"><span class="chip-dot" style="background:var(--risk-low);"></span>Low: <strong id="rail-cnt-low">4</strong></span>
              </div>
            </div>

            <!-- Locality Ranked Comparison Bars -->
            <div class="rail-stat-section">
              <div class="rail-section-label">
                <span>Locality Fire Risk Index (Ranked)</span>
                <span style="color:var(--text-muted); font-size:10px;">Click area to focus</span>
              </div>
              <div class="rail-locality-list">
                <div class="rail-locality-row" onclick="filterByLocalityFromRail('Shanti Mohalla')" title="Click to filter Shanti Mohalla">
                  <span class="rail-loc-name">Shanti Mohalla</span>
                  <div class="rail-loc-bar-wrap">
                    <div class="rail-loc-bar" style="width:82%; background:var(--risk-severe);"></div>
                  </div>
                  <span class="rail-loc-score num-tnum" style="color:var(--risk-severe);">0.82</span>
                </div>
                <div class="rail-locality-row" onclick="filterByLocalityFromRail('Seelampur')" title="Click to filter Seelampur">
                  <span class="rail-loc-name">Seelampur</span>
                  <div class="rail-loc-bar-wrap">
                    <div class="rail-loc-bar" style="width:75%; background:var(--risk-severe);"></div>
                  </div>
                  <span class="rail-loc-score num-tnum" style="color:var(--risk-severe);">0.75</span>
                </div>
                <div class="rail-locality-row" onclick="filterByLocalityFromRail('Gandhi Nagar')" title="Click to filter Gandhi Nagar">
                  <span class="rail-loc-name">Gandhi Nagar</span>
                  <div class="rail-loc-bar-wrap">
                    <div class="rail-loc-bar" style="width:71%; background:var(--risk-severe);"></div>
                  </div>
                  <span class="rail-loc-score num-tnum" style="color:var(--risk-severe);">0.71</span>
                </div>
                <div class="rail-locality-row" onclick="filterByLocalityFromRail('Subhash Nagar')" title="Click to filter Subhash Nagar">
                  <span class="rail-loc-name">Subhash Nagar</span>
                  <div class="rail-loc-bar-wrap">
                    <div class="rail-loc-bar" style="width:68%; background:var(--risk-high);"></div>
                  </div>
                  <span class="rail-loc-score num-tnum" style="color:var(--risk-high);">0.68</span>
                </div>
              </div>
            </div>

            <!-- Top Life-Safety Failure Drivers Across Area -->
            <div class="rail-stat-section" style="margin-bottom:0;">
              <div class="rail-section-label">
                <span>Top Vulnerability Drivers</span>
                <span style="color:var(--text-muted); font-size:10px;">% Non-Compliant</span>
              </div>
              <div class="rail-driver-list">
                <div class="rail-driver-item">
                  <div class="rail-driver-head">
                    <span>Narrow Stairs (&lt;0.75m)</span>
                    <span class="num-tnum">84%</span>
                  </div>
                  <div class="rail-driver-bar-track">
                    <div class="rail-driver-bar-fill" style="width:84%; background:#dc2626;"></div>
                  </div>
                </div>
                <div class="rail-driver-item">
                  <div class="rail-driver-head">
                    <span>Single Exit Route Only</span>
                    <span class="num-tnum">76%</span>
                  </div>
                  <div class="rail-driver-bar-track">
                    <div class="rail-driver-bar-fill" style="width:76%; background:#dc2626;"></div>
                  </div>
                </div>
                <div class="rail-driver-item">
                  <div class="rail-driver-head">
                    <span>Road Access &lt;3m (No Fire Engine)</span>
                    <span class="num-tnum">68%</span>
                  </div>
                  <div class="rail-driver-bar-track">
                    <div class="rail-driver-bar-fill" style="width:68%; background:#ea580c;"></div>
                  </div>
                </div>
                <div class="rail-driver-item">
                  <div class="rail-driver-head">
                    <span>Touching Adjacent Properties</span>
                    <span class="num-tnum">64%</span>
                  </div>
                  <div class="rail-driver-bar-track">
                    <div class="rail-driver-bar-fill" style="width:64%; background:#d97706;"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Card 2: Quick Workshop Inspector Card -->
          <div class="preview-card" id="preview-card">
            <div class="preview-header">
              <div>
                <span class="eyebrow" id="prev-eyebrow">SELECTED UNIT INSPECTOR</span>
                <div class="preview-title" id="prev-name">Navkar Fabric Wholesale Storage #2</div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;" id="prev-meta">
                  Gandhi Nagar • Ram Nagar Gali 4 • ID: SW-111
                </div>
              </div>
              <div class="preview-score-badge">
                <div>
                  <div class="preview-score-num num-tnum" id="prev-score-val" style="color:var(--risk-severe);">0.74</div>
                  <div style="font-size:9px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">FRI Score</div>
                </div>
                <span class="badge-tier Severe" id="prev-tier-badge">Severe</span>
              </div>
            </div>

            <div class="preview-deficiency-box" id="prev-deficiency-text">
              Primary difficulty: Only one exit door, blocked escape alley, and narrow lane under 3m preventing direct fire truck access.
            </div>

            <button type="button" class="btn-open-modal-large" onclick="openModalFromPreview()">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
              <span>View Full Inside &amp; Outside Facts</span>
            </button>

            <button type="button" class="btn-fire-emergency-hero" onclick="triggerShopFireIncident(selectedWorkshop)">
              <svg class="svg-icon" viewBox="0 0 24 24" style="color:#ffffff;"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
              <span>Simulate Fire Incident (Live Vehicle Tracking)</span>
            </button>

            <div class="preview-route-actions">
              <button type="button" class="btn-mini-action fire" onclick="triggerLiveDispatch('fire')">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color:#b91c1c;"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>
                <span>Dispatch Fire</span>
              </button>
              <button type="button" class="btn-mini-action hospital" onclick="triggerLiveDispatch('hospital')">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color:#0369a1;"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="6.5" y1="10" x2="10.5" y2="10"/><line x1="8.5" y1="8" x2="8.5" y2="12"/></svg>
                <span>Dispatch Hospital</span>
              </button>
              <button type="button" class="btn-mini-action" onclick="triggerRouteFromUser()">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color:#0284c7;"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/></svg>
                <span>My Route</span>
              </button>
            </div>
          </div>

          <!-- Card 3: Spatial Filter Controls & Layer Toggles Card -->
          <div class="filter-controls-card">
            <!-- Search -->
            <div class="filter-control-group">
              <span class="filter-label">Search Workshops</span>
              <div class="search-box">
                <span class="search-icon">
                  <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </span>
                <input type="text" id="filter-search" class="search-input" placeholder="ID, name, work type..." oninput="handleSearchInput(this.value)">
                <button type="button" id="search-clear-btn" class="search-clear" onclick="clearSearch()">✕</button>
              </div>
            </div>

            <!-- Locality Select -->
            <div class="filter-control-group">
              <span class="filter-label">Filter by Locality</span>
              <select id="filter-locality" class="locality-select" onchange="handleLocalityChange(this.value)">
                <option value="ALL">All Localities (Entire Survey Area)</option>
                <option value="Shanti Mohalla">Shanti Mohalla (38 units • Highest Risk)</option>
                <option value="Seelampur">Seelampur (48 units)</option>
                <option value="Gandhi Nagar">Gandhi Nagar (42 units)</option>
                <option value="Subhash Nagar">Subhash Nagar (30 units)</option>
              </select>
            </div>

            <!-- Risk Tiers Checkboxes -->
            <div class="filter-control-group">
              <span class="filter-label">Filter by Risk Tier</span>
              <div class="tier-pills-row">
                <label class="tier-check-pill">
                  <input type="checkbox" id="check-severe" checked onchange="handleFilterChange()">
                  <span style="color:var(--risk-severe);">Sev (<span id="tier-count-severe">114</span>)</span>
                </label>
                <label class="tier-check-pill">
                  <input type="checkbox" id="check-high" checked onchange="handleFilterChange()">
                  <span style="color:var(--risk-high);">High (<span id="tier-count-high">34</span>)</span>
                </label>
                <label class="tier-check-pill">
                  <input type="checkbox" id="check-moderate" checked onchange="handleFilterChange()">
                  <span style="color:var(--risk-moderate);">Mod (<span id="tier-count-moderate">6</span>)</span>
                </label>
                <label class="tier-check-pill">
                  <input type="checkbox" id="check-low" checked onchange="handleFilterChange()">
                  <span style="color:var(--risk-low);">Low (<span id="tier-count-low">4</span>)</span>
                </label>
              </div>
            </div>

            <!-- Layer Switches (Borders & Historical Fires UNCHECKED by default to remove clutter!) -->
            <div class="filter-control-group">
              <span class="filter-label">Emergency Overlays</span>
              <div class="layer-switches-row">
                <label class="mini-switch-label">
                  <input type="checkbox" id="toggle-heat" onchange="toggleHeatLayer(this.checked)">
                  <span>Heatmap</span>
                </label>
                <label class="mini-switch-label">
                  <input type="checkbox" id="toggle-fire-stations" checked onchange="toggleFireStations(this.checked)">
                  <span>Fire Stations</span>
                </label>
                <label class="mini-switch-label">
                  <input type="checkbox" id="toggle-hospitals" checked onchange="toggleHospitals(this.checked)">
                  <span>Hospitals</span>
                </label>
                <label class="mini-switch-label">
                  <input type="checkbox" id="toggle-boundaries" onchange="toggleBoundaries(this.checked)">
                  <span>Locality Borders</span>
                </label>
                <label class="mini-switch-label">
                  <input type="checkbox" id="toggle-pastfire" onchange="togglePastFireMarkers(this.checked)">
                  <span>Historical Fires</span>
                </label>
              </div>
            </div>

            <button type="button" class="btn-gps-locate" onclick="getUserLocation()">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>
              <span>Locate My Position (GPS)</span>
            </button>
          </div>
        </div>

        <!-- Right Column: Big Dominant Map Viewport -->
        <div id="map-widget-card" class="map-widget-card">
          <div class="map-widget-header">
            <div class="map-widget-title-wrap">
              <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
              <span class="map-widget-title">Geospatial Risk Map</span>
              <span id="map-units-badge" class="map-badge-count">158 Units Displayed</span>
            </div>
            <div class="map-widget-header-actions">
              <button type="button" id="tile-btn-google" class="style-btn-pill active" onclick="setBaseTile('google')">Google Street</button>
              <button type="button" id="tile-btn-satellite" class="style-btn-pill" onclick="setBaseTile('satellite')">Satellite</button>
              <button type="button" id="tile-btn-osm" class="style-btn-pill" onclick="setBaseTile('osm')">OSM</button>
              <button type="button" id="tile-btn-esri" class="style-btn-pill" onclick="setBaseTile('esri')">Esri</button>
              <button type="button" id="btn-fire-simulate-header" class="btn-fire-simulate-header" onclick="triggerShopFireIncident(selectedWorkshop || WORKSHOPS_DATA[0])" title="Simulate Fire Emergency at Selected Shop">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
                <span>Simulate Fire</span>
              </button>
              <button type="button" id="btn-toggle-expand" class="btn-expand-map" onclick="toggleMapExpansion()">
                <svg id="expand-icon" class="svg-icon" style="width:13px; height:13px;" viewBox="0 0 24 24"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
                <span id="expand-text">Expand Map</span>
              </button>
            </div>
          </div>

          <!-- Leaflet Map Container (Big Spacious Viewport) -->
          <div id="map-container"></div>

          <!-- Map Footer Legend -->
          <div class="map-widget-footer">
            <div class="map-footer-legend">
              <div class="legend-dot-item">
                <span class="legend-dot" style="background:var(--risk-severe);"></span>
                <span>Severe (≥0.70)</span>
              </div>
              <div class="legend-dot-item">
                <span class="legend-dot" style="background:var(--risk-high);"></span>
                <span>High (0.50–0.70)</span>
              </div>
              <div class="legend-dot-item">
                <span class="legend-dot" style="background:var(--risk-moderate);"></span>
                <span>Moderate (0.30–0.50)</span>
              </div>
              <div class="legend-dot-item">
                <span class="legend-dot" style="background:var(--risk-low);"></span>
                <span>Low (&lt;0.30)</span>
              </div>
            </div>
            <div style="font-weight:600; color:var(--text-muted); font-size:11px;">
              Click any dot to inspect facts &amp; dispatch
            </div>
          </div>
        </div>
      </div>

      '''

    content = content[:start_pos] + new_html_grid + content[end_pos:]

    # 4. In buildLocalityBoundaryLayers(), DO NOT add boundaryLayer to map by default!
    old_boundary_code = '''        polygons.push(poly);
      }});

      boundaryLayer = L.layerGroup(polygons).addTo(map);
    }}'''

    new_boundary_code = '''        polygons.push(poly);
      }});

      // Boundary layer created but NOT added by default to prevent visual clutter
      boundaryLayer = L.layerGroup(polygons);
    }}'''

    if old_boundary_code in content:
        content = content.replace(old_boundary_code, new_boundary_code, 1)

    # 5. In updatePastFireMarkers(), remove the '!' exclamation sign and do NOT add by default!
    old_past_fire_code = '''      const pastFires = filtered.filter(w => w.incident);
      const markers = pastFires.map(w => {{
        const icon = L.divIcon({{
          className: 'past-fire-icon',
          html: `<div style="background:#fef2f2; border:2px solid #ef4444; border-radius:50%; width:18px; height:18px; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:800; color:#dc2626;">!</div>`,
          iconSize: [18, 18],
          iconAnchor: [9, 9]
        }});
        return L.marker([w.lat, w.lng], {{ icon }}).on('click', () => {{
          updatePreviewCard(w);
          openWorkshopModal(w);
        }});
      }});

      pastFireLayer = L.layerGroup(markers);
      if (document.getElementById('toggle-pastfire').checked) {{
        pastFireLayer.addTo(map);
      }}'''

    new_past_fire_code = '''      const pastFires = filtered.filter(w => w.incident);
      const markers = pastFires.map(w => {{
        // Clean, subtle amber flame accent badge (Zero '!' exclamation clutter)
        const icon = L.divIcon({{
          className: 'past-fire-icon',
          html: `<div style="background:#fff7ed; border:2px solid #ea580c; border-radius:50%; width:20px; height:20px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 6px rgba(234,88,12,0.35);"><svg viewBox="0 0 24 24" width="12" height="12" fill="#ea580c"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg></div>`,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        }});
        return L.marker([w.lat, w.lng], {{ icon }}).on('click', () => {{
          updatePreviewCard(w);
          openWorkshopModal(w);
        }});
      }});

      pastFireLayer = L.layerGroup(markers);
      const pastCheck = document.getElementById('toggle-pastfire');
      if (pastCheck && pastCheck.checked) {{
        pastFireLayer.addTo(map);
      }}'''

    if old_past_fire_code in content:
        content = content.replace(old_past_fire_code, new_past_fire_code, 1)

    # 6. Add rail filter helper function and update KPI strip to also update rail stats
    old_update_kpi_func = '''    function updateKPIStrip(filtered) {{
      const total = WORKSHOPS_DATA.length;
      const count = filtered.length;
      document.getElementById('kpi-count').textContent = `${{count}} / ${{total}}`;'''

    new_update_kpi_func = '''    function filterByLocalityFromRail(loc) {{
      const select = document.getElementById('filter-locality');
      if (select) {{
        select.value = loc;
        handleLocalityChange(loc);
      }}
    }}
    window.filterByLocalityFromRail = filterByLocalityFromRail;

    function updateKPIStrip(filtered) {{
      const total = WORKSHOPS_DATA.length;
      const count = filtered.length;
      document.getElementById('kpi-count').textContent = `${{count}} / ${{total}}`;
      
      const badgeUnits = document.getElementById('map-units-badge');
      if (badgeUnits) {{
        badgeUnits.textContent = `${{count}} Units Displayed`;
      }}
      const railTotal = document.getElementById('rail-total-count');
      if (railTotal) {{
        railTotal.textContent = `${{count}} Units`;
      }}'''

    if old_update_kpi_func in content:
        content = content.replace(old_update_kpi_func, new_update_kpi_func, 1)

    with open('generate_app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: generate_app.py updated with new layout!")

if __name__ == '__main__':
    main()
