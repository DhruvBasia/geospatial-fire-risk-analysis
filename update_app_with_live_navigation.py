# -*- coding: utf-8 -*-
"""
update_app_with_live_navigation.py
Upgrades generate_app.py to add:
1. Ultra-clear and precise basemaps: Google Streets (default, maxZoom 20), Google Satellite Hybrid, OSM, Esri with crisp rendering.
2. Fire Emergency Incident Simulation on any workshop (Shop A or audited units) with on-map pulsating fire hazard beacon.
3. Live GPS Vehicle Tracking (Blinkit & Zepto Rider style):
   - Animated moving vehicle marker with real heading angle rotation following road curves
   - Dual flashing LED strobe lights & expanding sonar radar ripples
   - Delhi Fire Service (DFS Tender #04) vs Medical Ambulance (CATS ICU #02)
   - Real-time ETA countdown, distance remaining, speedometer
   - Live delivery/turnout progress timeline bar
   - Play/pause, 1x/2x/4x speed toggle, and Follow Vehicle camera tracking
4. Proper Direction Guidance (Turn-by-turn with clear Right and Left indicators):
   - Large next-turn maneuver card with turn arrow SVG, distance countdown in meters, and street name
   - Synchronized turn-by-turn cue sheet with active step auto-scroll and highlight
5. Zero emojis (100% vector SVGs and typography).
"""

import re
import sys

def main():
    with open('generate_app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Map Header Buttons & Add "Simulate Fire" Header Button
    old_map_header_actions = '''            <div class="map-widget-header-actions">
              <button type="button" id="tile-btn-osm" class="style-btn-pill active" onclick="setBaseTile('osm')">Street</button>
              <button type="button" id="tile-btn-esri" class="style-btn-pill" onclick="setBaseTile('esri')">Esri</button>
              <button type="button" id="tile-btn-satellite" class="style-btn-pill" onclick="setBaseTile('satellite')">Satellite</button>
              <button type="button" id="tile-btn-topo" class="style-btn-pill" onclick="setBaseTile('topo')">Topographic</button>
              <button type="button" id="btn-toggle-expand" class="btn-expand-map" onclick="toggleMapExpansion()">
                <svg id="expand-icon" class="svg-icon" style="width:13px; height:13px;" viewBox="0 0 24 24"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
                <span id="expand-text">Expand Map</span>
              </button>
            </div>'''

    new_map_header_actions = '''            <div class="map-widget-header-actions">
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
            </div>'''

    if old_map_header_actions not in content:
        print("ERROR: old_map_header_actions not found!")
        sys.exit(1)
    content = content.replace(old_map_header_actions, new_map_header_actions, 1)

    # 2. Update Preview Card with "Simulate Fire Incident" hero button and quick dispatch buttons
    old_preview_buttons = '''            <button type="button" class="btn-open-modal-large" onclick="openModalFromPreview()">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
              <span>View Full Inside &amp; Outside Facts</span>
            </button>

            <div class="preview-route-actions">
              <button type="button" class="btn-mini-action" onclick="triggerRouteFromFireStation()">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color:#b91c1c;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>
                <span>Fire Route</span>
              </button>
              <button type="button" class="btn-mini-action" onclick="triggerRouteFromUser()">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color:#0284c7;"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/></svg>
                <span>Route Me</span>
              </button>
              <button type="button" class="btn-mini-action" onclick="triggerRouteToHospital()">
                <svg class="svg-icon" viewBox="0 0 24 24" style="color:#0369a1;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                <span>Hospital</span>
              </button>
            </div>'''

    new_preview_buttons = '''            <button type="button" class="btn-open-modal-large" onclick="openModalFromPreview()">
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
            </div>'''

    if old_preview_buttons not in content:
        print("ERROR: old_preview_buttons not found!")
        sys.exit(1)
    content = content.replace(old_preview_buttons, new_preview_buttons, 1)

    # 3. Update Modal Actions
    old_modal_actions = '''        <div class="modal-actions-left">
          <button type="button" class="btn-action fire" onclick="triggerRouteFromFireStation()">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span>Fire Brigade Route</span>
          </button>
          <button type="button" class="btn-action" onclick="triggerRouteFromUser()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>
            <span>Route from My Location</span>
          </button>
          <button type="button" class="btn-action hospital" onclick="triggerRouteToHospital()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
            <span>Hospital Transfer Route</span>
          </button>
          <button type="button" class="btn-action" onclick="zoomToModalWorkshop()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
            <span>Focus on Map</span>
          </button>
        </div>'''

    new_modal_actions = '''        <div class="modal-actions-left">
          <button type="button" class="btn-action fire-emergency-highlight" onclick="closeWorkshopModal(); triggerShopFireIncident(selectedWorkshop);" style="background:#dc2626; color:#ffffff; font-weight:800;">
            <svg class="svg-icon" viewBox="0 0 24 24" style="color:#ffffff;"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
            <span>Report Active Fire &amp; Track Live Vehicle</span>
          </button>
          <button type="button" class="btn-action fire" onclick="closeWorkshopModal(); triggerLiveDispatch('fire')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>
            <span>Fire Brigade Route</span>
          </button>
          <button type="button" class="btn-action hospital" onclick="closeWorkshopModal(); triggerLiveDispatch('hospital')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="6.5" y1="10" x2="10.5" y2="10"/><line x1="8.5" y1="8" x2="8.5" y2="12"/></svg>
            <span>Hospital Ambulance Route</span>
          </button>
          <button type="button" class="btn-action" onclick="zoomToModalWorkshop()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
            <span>Focus on Map</span>
          </button>
        </div>'''

    if old_modal_actions not in content:
        print("ERROR: old_modal_actions not found!")
        sys.exit(1)
    content = content.replace(old_modal_actions, new_modal_actions, 1)

    # 4. Replace #route-card HTML with the State-of-the-Art Live Emergency Dispatch & Navigation Center
    old_route_card_html = '''    <!-- Navigation Turn-by-Turn Card (Overlay) -->
    <div id="route-card">
      <div class="route-card-header">
        <div class="route-header-title">
          <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
          <span id="route-title">Emergency Turnout Navigation</span>
        </div>
        <button type="button" class="btn-close-route" onclick="clearNavigationRoute()">✕</button>
      </div>

      <div class="route-summary-strip">
        <div class="route-stat">
          <span id="route-dist" class="route-stat-val num-tnum">0.0 km</span>
          <span class="route-stat-lbl">Road Distance</span>
        </div>
        <div class="route-stat">
          <span id="route-time" class="route-stat-val num-tnum">0 min</span>
          <span class="route-stat-lbl">Estimated Drive Time</span>
        </div>
      </div>

      <div id="route-waypoints" class="route-waypoints">
        From: <strong>Origin</strong><br>
        To: <strong>Destination</strong>
      </div>

      <div id="route-fallback-notice" class="route-fallback-notice">
        OSRM router offline or rate-limited. Showing direct trajectory with estimated road travel time.
      </div>

      <div id="route-steps" class="route-steps-container"></div>
    </div>'''

    new_route_card_html = '''    <!-- Live Emergency Dispatch & Turnout Navigation Center (Blinkit/Zepto Live Tracking + Left/Right Direction Guidance) -->
    <div id="route-card" class="emergency-nav-panel">
      <!-- Card Header -->
      <div class="route-card-header">
        <div class="route-header-title">
          <span class="live-pulse-dot"></span>
          <span id="route-title">Live Emergency Dispatch Telemetry</span>
        </div>
        <button type="button" class="btn-close-route" onclick="clearNavigationRoute()" title="Close Navigation">✕</button>
      </div>

      <!-- Incident Banner Strip -->
      <div class="route-incident-strip" id="route-incident-strip">
        <div class="route-incident-tag">
          <svg class="svg-icon" viewBox="0 0 24 24"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
          <span id="nav-incident-status">FIRE INCIDENT REPORTED</span>
        </div>
        <div class="route-target-name" id="nav-target-name">Target: Shop A (W-001)</div>
      </div>

      <!-- Vehicle Dispatch Selector Tabs (Fire Brigade vs Hospital Ambulance) -->
      <div class="nav-vehicle-tabs">
        <button type="button" id="tab-dispatch-fire" class="nav-tab-btn active" onclick="switchDispatchVehicle('fire')">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>
          <span>DFS Fire Tender</span>
        </button>
        <button type="button" id="tab-dispatch-hospital" class="nav-tab-btn" onclick="switchDispatchVehicle('hospital')">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="6.5" y1="10" x2="10.5" y2="10"/><line x1="8.5" y1="8" x2="8.5" y2="12"/></svg>
          <span>Ambulance &amp; Doctors</span>
        </button>
      </div>

      <!-- PROPER DIRECTION GUIDANCE: Prominent Next-Turn Maneuver Box -->
      <div class="next-turn-banner" id="next-turn-banner">
        <div class="next-turn-icon-wrap" id="next-turn-icon">
          <svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg>
        </div>
        <div class="next-turn-details">
          <div class="next-turn-instruction-row">
            <span class="next-turn-badge" id="next-turn-badge">TURN LEFT</span>
            <span class="next-turn-distance" id="next-turn-distance">In 120m</span>
          </div>
          <div class="next-turn-street" id="next-turn-street">onto Grand Trunk Road (GT Road)</div>
        </div>
      </div>

      <!-- Blinkit / Zepto Style Live Telemetry Strip -->
      <div class="telemetry-kpi-strip">
        <div class="telemetry-kpi">
          <span class="telemetry-val" id="telemetry-eta">3m 42s</span>
          <span class="telemetry-lbl">ETA to Scene</span>
        </div>
        <div class="telemetry-kpi">
          <span class="telemetry-val" id="telemetry-distance">1.4 km</span>
          <span class="telemetry-lbl">Distance Remaining</span>
        </div>
        <div class="telemetry-kpi">
          <span class="telemetry-val" id="telemetry-speed">42 km/h</span>
          <span class="telemetry-lbl">Vehicle Speed</span>
        </div>
      </div>

      <!-- Blinkit / Zepto Rider Progress Bar -->
      <div class="rider-progress-wrap">
        <div class="rider-progress-labels">
          <span id="progress-origin-label">Shastri Park Station</span>
          <span id="progress-percent-label">42% En Route</span>
          <span id="progress-dest-label">Shop A</span>
        </div>
        <div class="rider-progress-track">
          <div class="rider-progress-fill" id="rider-progress-fill" style="width: 42%;"></div>
        </div>
      </div>

      <!-- Simulation Playback & Tracking Controls -->
      <div class="sim-control-bar">
        <button type="button" class="btn-sim-action" id="btn-sim-playpause" onclick="toggleSimPause()">
          <svg class="svg-icon" id="sim-play-icon" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
          <span id="sim-play-text">Pause</span>
        </button>
        <div class="sim-speed-selector">
          <button type="button" class="btn-sim-speed" id="sim-speed-1" onclick="setSimSpeed(1)">1x</button>
          <button type="button" class="btn-sim-speed active" id="sim-speed-2" onclick="setSimSpeed(2)">2x</button>
          <button type="button" class="btn-sim-speed" id="sim-speed-4" onclick="setSimSpeed(4)">4x</button>
        </div>
        <button type="button" class="btn-sim-action" id="btn-follow-toggle" onclick="toggleFollowVehicle()">
          <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
          <span id="follow-toggle-text">Follow: ON</span>
        </button>
        <button type="button" class="btn-sim-action" onclick="fitRouteBounds()" title="Fit Route on Map">
          <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
        </button>
      </div>

      <div id="route-fallback-notice" class="route-fallback-notice">
        OSRM router offline. Using calculated direct corridor navigation with estimated live dispatch telemetry.
      </div>

      <!-- Turn-by-Turn Step Cue Sheet (Proper Direction Left & Right) -->
      <div class="route-steps-header">
        <span>Turn-by-Turn Navigation Steps</span>
        <span class="route-steps-count" id="route-steps-count">0 steps</span>
      </div>
      <div id="route-steps" class="route-steps-container"></div>
    </div>'''

    if old_route_card_html not in content:
        print("ERROR: old_route_card_html not found!")
        sys.exit(1)
    content = content.replace(old_route_card_html, new_route_card_html, 1)

    # 5. Replace Navigation CSS (lines 1725 to 1853)
    old_nav_css_regex = r'/\* =========================================================\s+7\. NAVIGATION CARD\s+========================================================= \*/[\s\S]*?(?=/\* Custom Leaflet Tooltip \*/)'
    
    new_nav_css = '''/* =========================================================
       7. LIVE EMERGENCY DISPATCH & NAVIGATION CARD (BLINKIT/ZEPTO STYLE)
       ========================================================= */
    #route-card {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 410px;
      max-height: 590px;
      background: #ffffff;
      border-radius: var(--radius-md);
      box-shadow: 0 20px 45px rgba(0, 0, 0, 0.35);
      border: 1px solid var(--border);
      z-index: 2600;
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: var(--font);
      animation: navSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @keyframes navSlideUp {{
      from {{ transform: translateY(30px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}

    #route-card.active {{
      display: flex;
    }}

    .route-card-header {{
      padding: 12px 16px;
      background: var(--navy-900);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .route-header-title {{
      font-size: 13px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .btn-close-route {{
      background: none;
      border: none;
      color: #cbd5e1;
      font-size: 16px;
      cursor: pointer;
      line-height: 1;
      padding: 2px 4px;
    }}

    .btn-close-route:hover {{
      color: #ffffff;
    }}

    .live-pulse-dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 8px #22c55e;
      display: inline-block;
      animation: livePulseRadar 1.4s infinite;
    }}

    @keyframes livePulseRadar {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.3); opacity: 0.6; }}
    }}

    .route-incident-strip {{
      padding: 8px 14px;
      background: #fef2f2;
      border-bottom: 1px solid #fee2e2;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }}

    .route-incident-tag {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      color: #b91c1c;
      letter-spacing: 0.03em;
    }}

    .route-target-name {{
      font-size: 11px;
      font-weight: 700;
      color: var(--navy-900);
      text-overflow: ellipsis;
      overflow: hidden;
      white-space: nowrap;
    }}

    /* Vehicle Dispatch Selector Tabs */
    .nav-vehicle-tabs {{
      display: flex;
      background: #f1f5f9;
      padding: 4px;
      gap: 4px;
      border-bottom: 1px solid var(--border);
    }}

    .nav-tab-btn {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 7px 10px;
      border-radius: var(--radius-sm);
      border: none;
      background: transparent;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .nav-tab-btn:hover {{
      background: rgba(255, 255, 255, 0.6);
      color: var(--text-primary);
    }}

    .nav-tab-btn.active {{
      background: #ffffff;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }}

    #tab-dispatch-fire.active {{
      color: #b91c1c;
      border-bottom: 2px solid #dc2626;
    }}

    #tab-dispatch-hospital.active {{
      color: #0284c7;
      border-bottom: 2px solid #0284c7;
    }}

    /* PROPER DIRECTION GUIDANCE: Next-Turn Banner */
    .next-turn-banner {{
      padding: 10px 14px;
      background: var(--navy-900);
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .next-turn-icon-wrap {{
      width: 42px;
      height: 42px;
      border-radius: var(--radius-md);
      background: rgba(255, 255, 255, 0.12);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .svg-maneuver {{
      width: 24px;
      height: 24px;
      stroke: #22c55e;
      stroke-width: 2.5;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}

    .next-turn-details {{
      flex: 1;
      min-width: 0;
    }}

    .next-turn-instruction-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 2px;
    }}

    .next-turn-badge {{
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 2px 6px;
      border-radius: 4px;
      background: #22c55e;
      color: #064e3b;
      letter-spacing: 0.04em;
    }}

    .next-turn-distance {{
      font-size: 14px;
      font-weight: 800;
      color: #ffffff;
    }}

    .next-turn-street {{
      font-size: 11px;
      font-weight: 600;
      color: #cbd5e1;
      text-overflow: ellipsis;
      overflow: hidden;
      white-space: nowrap;
    }}

    /* Telemetry KPI Strip */
    .telemetry-kpi-strip {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      padding: 8px 14px;
      background: #f8fafc;
      border-bottom: 1px solid var(--border);
      text-align: center;
    }}

    .telemetry-kpi {{
      display: flex;
      flex-direction: column;
    }}

    .telemetry-val {{
      font-size: 15px;
      font-weight: 800;
      color: var(--navy-900);
      font-variant-numeric: tabular-nums;
    }}

    .telemetry-lbl {{
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-top: 1px;
    }}

    /* Rider Progress Bar (Blinkit / Zepto) */
    .rider-progress-wrap {{
      padding: 7px 14px 8px;
      background: #ffffff;
      border-bottom: 1px solid var(--border);
    }}

    .rider-progress-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      font-weight: 700;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }}

    .rider-progress-track {{
      width: 100%;
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
      position: relative;
    }}

    .rider-progress-fill {{
      height: 100%;
      background: linear-gradient(90deg, #0e7490, #22c55e);
      border-radius: 3px;
      transition: width 0.15s linear;
    }}

    /* Simulation Control Bar */
    .sim-control-bar {{
      padding: 6px 14px;
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
    }}

    .btn-sim-action {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      background: #f1f5f9;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 700;
      color: var(--navy-900);
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .btn-sim-action:hover {{
      background: #e2e8f0;
    }}

    .btn-sim-action.active {{
      background: #e0f2fe;
      border-color: #0284c7;
      color: #0284c7;
    }}

    .sim-speed-selector {{
      display: inline-flex;
      background: #f1f5f9;
      border-radius: var(--radius-sm);
      padding: 2px;
      border: 1px solid var(--border);
    }}

    .btn-sim-speed {{
      background: transparent;
      border: none;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 3px;
      cursor: pointer;
      color: var(--text-secondary);
    }}

    .btn-sim-speed.active {{
      background: var(--navy-900);
      color: #ffffff;
    }}

    .route-fallback-notice {{
      padding: 6px 14px;
      background: #fffbeb;
      color: #92400e;
      font-size: 11px;
      display: none;
      border-bottom: 1px solid #fef3c7;
    }}

    .route-steps-header {{
      padding: 6px 14px;
      background: #f8fafc;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--text-secondary);
    }}

    .route-steps-container {{
      flex: 1;
      overflow-y: auto;
      max-height: 180px;
      padding: 6px 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .route-step-item {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      font-size: 11px;
      line-height: 1.35;
      padding: 6px 8px;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .route-step-item:hover {{
      background: #f8fafc;
    }}

    .route-step-item.active-turn {{
      background: #eff6ff;
      border-color: #3b82f6;
      box-shadow: 0 0 0 1px #3b82f6;
    }}

    .route-step-item.completed-turn {{
      opacity: 0.55;
    }}

    .step-icon {{
      display: flex;
      align-items: center;
      margin-top: 1px;
      flex-shrink: 0;
    }}

    .step-text {{
      flex: 1;
    }}

    .step-dist {{
      font-size: 10px;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .step-direction-pill {{
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 1px 4px;
      border-radius: 3px;
      background: #e2e8f0;
      color: var(--navy-900);
      margin-right: 4px;
    }}

    /* Emergency Header & Hero Buttons */
    .btn-fire-simulate-header {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 5px 9px;
      background: #dc2626;
      color: #ffffff;
      border: none;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      transition: background 0.2s;
    }}

    .btn-fire-simulate-header:hover {{
      background: #b91c1c;
    }}

    .btn-fire-emergency-hero {{
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 14px;
      background: #dc2626;
      color: #ffffff;
      border: none;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      margin-top: 8px;
      box-shadow: 0 3px 10px rgba(220, 38, 38, 0.35);
      transition: background 0.2s, transform 0.1s;
    }}

    .btn-fire-emergency-hero:hover {{
      background: #b91c1c;
      transform: translateY(-1px);
    }}

    /* Crisp Tile Rendering */
    .leaflet-tile {{
      image-rendering: -webkit-optimize-contrast;
      image-rendering: crisp-edges;
    }}

    /* Live Vehicle Marker & Sonar Radar (Blinkit/Zepto) */
    .live-vehicle-marker {{
      position: relative;
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      pointer-events: auto;
    }}

    .vehicle-disc {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      position: relative;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
      transition: transform 0.1s ease-out;
      border: 2.5px solid #ffffff;
      z-index: 2;
    }}

    .vehicle-disc.fire {{
      background: radial-gradient(circle, #ef4444 0%, #b91c1c 100%);
    }}

    .vehicle-disc.hospital {{
      background: radial-gradient(circle, #0284c7 0%, #0369a1 100%);
    }}

    .vehicle-radar-wave {{
      position: absolute;
      top: 50%;
      left: 50%;
      width: 38px;
      height: 38px;
      border-radius: 50%;
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: 1;
      animation: vehicleRadarPulse 1.8s infinite cubic-bezier(0.2, 0.8, 0.2, 1);
    }}

    .vehicle-disc.fire ~ .vehicle-radar-wave {{
      background: rgba(239, 68, 68, 0.45);
      box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
    }}

    .vehicle-disc.hospital ~ .vehicle-radar-wave {{
      background: rgba(2, 132, 199, 0.45);
      box-shadow: 0 0 15px rgba(2, 132, 199, 0.6);
    }}

    @keyframes vehicleRadarPulse {{
      0% {{ transform: translate(-50%, -50%) scale(0.9); opacity: 0.85; }}
      100% {{ transform: translate(-50%, -50%) scale(2.6); opacity: 0; }}
    }}

    .vehicle-nameplate {{
      position: absolute;
      bottom: -22px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.94);
      color: #ffffff;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      white-space: nowrap;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      pointer-events: none;
      border: 1px solid rgba(255, 255, 255, 0.2);
      z-index: 3;
    }}

    /* Active Incident Fire Beacon on Workshop */
    .fire-beacon-marker {{
      position: relative;
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .fire-beacon-disc {{
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: #dc2626;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2.5px solid #ffffff;
      box-shadow: 0 0 20px #ef4444;
      z-index: 2;
      animation: fireBeaconThrob 1.2s infinite ease-in-out;
    }}

    @keyframes fireBeaconThrob {{
      0%, 100% {{ transform: scale(1); box-shadow: 0 0 12px #ef4444; }}
      50% {{ transform: scale(1.15); box-shadow: 0 0 26px #f87171; }}
    }}

    .fire-beacon-radar {{
      position: absolute;
      top: 50%;
      left: 50%;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      border: 2px solid #ef4444;
      transform: translate(-50%, -50%);
      animation: fireRadarExpand 1.6s infinite cubic-bezier(0.1, 0.7, 0.3, 1);
      pointer-events: none;
    }}

    @keyframes fireRadarExpand {{
      0% {{ transform: translate(-50%, -50%) scale(1); opacity: 0.9; }}
      100% {{ transform: translate(-50%, -50%) scale(3.2); opacity: 0; }}
    }}

    .fire-beacon-label {{
      position: absolute;
      top: -24px;
      left: 50%;
      transform: translateX(-50%);
      background: #b91c1c;
      color: #ffffff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 4px;
      white-space: nowrap;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.4);
      letter-spacing: 0.03em;
    }}
    
    '''

    match = re.search(old_nav_css_regex, content)
    if not match:
        print("ERROR: old_nav_css_regex failed to match!")
        sys.exit(1)
    content = content[:match.start()] + new_nav_css + content[match.end():]

    # 6. Update State Variables
    old_state_vars = '''    let currentUser = null;
    let map = null;
    let baseLayers = {{}};
    let currentTile = 'osm';
    let workshopMarkers = [];
    let heatLayer = null;
    let fireStationLayer = null;
    let hospitalLayer = null;
    let pastFireLayer = null;
    let boundaryLayer = null;
    let userLocationMarker = null;
    let selectedMarkerHalo = null;
    let currentRouteLayers = [];
    let selectedWorkshop = null;
    let isMapExpanded = false;
    let tableSortCol = 'fri';
    let tableSortAsc = false;'''

    new_state_vars = '''    let currentUser = null;
    let map = null;
    let baseLayers = {{}};
    let currentTile = 'google';
    let workshopMarkers = [];
    let heatLayer = null;
    let fireStationLayer = null;
    let hospitalLayer = null;
    let pastFireLayer = null;
    let boundaryLayer = null;
    let userLocationMarker = null;
    let selectedMarkerHalo = null;
    let currentRouteLayers = [];
    let selectedWorkshop = null;
    let isMapExpanded = false;
    let tableSortCol = 'fri';
    let tableSortAsc = false;

    // Emergency Incident & Live Rider Telemetry State
    let activeIncidentWorkshop = null;
    let incidentBeaconMarker = null;
    let liveVehicleMarker = null;
    let simTraveledLine = null;
    let simRemainingLine = null;
    let simAnimationId = null;
    let simState = {{
      running: false,
      paused: false,
      type: 'fire',
      speedMultiplier: 2,
      followVehicle: true,
      route: null,
      routeBounds: null,
      coords: [],
      distances: [],
      totalDist: 0,
      totalDuration: 0,
      elapsed: 0,
      lastTimestamp: 0,
      targetWorkshop: null,
      originFacility: null,
      currentStepIndex: 0
    }};'''

    if old_state_vars not in content:
        print("ERROR: old_state_vars not found!")
        sys.exit(1)
    content = content.replace(old_state_vars, new_state_vars, 1)

    # 7. Update initMap and setBaseTile to use Google Streets default & maxZoom 20
    old_init_map = '''    function initMap() {{
      if (map) return;
      map = L.map('map-container', {{
        center: [28.6675, 77.2715],
        zoom: 15,
        zoomControl: true,
        attributionControl: true
      }});

      map.zoomControl.setPosition('topright');

      baseLayers.osm = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
        maxZoom: 19
      }});

      baseLayers.esri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        attribution: 'Tiles &copy; Esri, DeLorme, NAVTEQ',
        maxZoom: 19
      }});

      baseLayers.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        attribution: 'Tiles &copy; Esri, Earthstar Geographics',
        maxZoom: 19
      }});

      baseLayers.topo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        attribution: 'Tiles &copy; Esri',
        maxZoom: 19
      }});

      baseLayers.osm.addTo(map);

      buildLocalityBoundaryLayers();
      buildEmergencyFacilityLayers();

      document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') {{
          closeWorkshopModal();
          clearNavigationRoute();
          if (isMapExpanded) toggleMapExpansion();
        }}
      }});
    }}

    function toggleMapExpansion() {{
      isMapExpanded = !isMapExpanded;
      const card = document.getElementById('map-widget-card');
      const text = document.getElementById('expand-text');
      card.classList.toggle('expanded', isMapExpanded);
      text.textContent = isMapExpanded ? 'Minimize Map' : 'Expand Map';
      
      setTimeout(() => {{
        if (map) map.invalidateSize();
      }}, 60);
    }}
    window.toggleMapExpansion = toggleMapExpansion;

    function setBaseTile(type) {{
      currentTile = type;
      ['osm', 'esri', 'satellite', 'topo'].forEach(t => {{
        const btn = document.getElementById('tile-btn-' + t);
        if (btn) btn.classList.toggle('active', t === type);
        if (baseLayers[t] && map.hasLayer(baseLayers[t])) map.removeLayer(baseLayers[t]);
      }});
      if (baseLayers[type]) baseLayers[type].addTo(map);
    }}
    window.setBaseTile = setBaseTile;'''

    new_init_map = '''    function initMap() {{
      if (map) return;
      map = L.map('map-container', {{
        center: [28.6675, 77.2715],
        zoom: 15,
        maxZoom: 20,
        zoomControl: true,
        attributionControl: true
      }});

      map.zoomControl.setPosition('topright');

      // Ultra-Crisp Google Maps Street Layer (No API Key Required)
      baseLayers.google = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}', {{
        attribution: '&copy; Google Maps',
        maxZoom: 20
      }});

      // High-Resolution Satellite Hybrid with Road & Locality Overlays
      baseLayers.satellite = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}', {{
        attribution: '&copy; Google Satellite Imagery',
        maxZoom: 20
      }});

      // OpenStreetMap Standard
      baseLayers.osm = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
        maxZoom: 19
      }});

      // Esri World Street Map
      baseLayers.esri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        attribution: 'Tiles &copy; Esri, DeLorme, NAVTEQ',
        maxZoom: 19
      }});

      // Set Google Street as default basemap
      baseLayers.google.addTo(map);

      buildLocalityBoundaryLayers();
      buildEmergencyFacilityLayers();

      document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') {{
          closeWorkshopModal();
          clearNavigationRoute();
          if (isMapExpanded) toggleMapExpansion();
        }}
      }});
    }}

    function toggleMapExpansion() {{
      isMapExpanded = !isMapExpanded;
      const card = document.getElementById('map-widget-card');
      const text = document.getElementById('expand-text');
      card.classList.toggle('expanded', isMapExpanded);
      text.textContent = isMapExpanded ? 'Minimize Map' : 'Expand Map';
      
      setTimeout(() => {{
        if (map) map.invalidateSize();
      }}, 60);
    }}
    window.toggleMapExpansion = toggleMapExpansion;

    function setBaseTile(type) {{
      currentTile = type;
      ['google', 'satellite', 'osm', 'esri'].forEach(t => {{
        const btn = document.getElementById('tile-btn-' + t);
        if (btn) btn.classList.toggle('active', t === type);
        if (baseLayers[t] && map.hasLayer(baseLayers[t])) map.removeLayer(baseLayers[t]);
      }});
      if (baseLayers[type]) baseLayers[type].addTo(map);
    }}
    window.setBaseTile = setBaseTile;'''

    if old_init_map not in content:
        print("ERROR: old_init_map not found!")
        sys.exit(1)
    content = content.replace(old_init_map, new_init_map, 1)

    # 8. Upgrade the Navigation & Live Vehicle Tracking JavaScript Engine
    old_nav_js_regex = r'// =========================================================\s+// OSRM NAVIGATION & GUIDANCE \(NO EMOJIS\)[\s\S]*?(?=// =========================================================\s+// ANALYTICS DASHBOARD)'

    new_nav_js = '''// =========================================================
    // LIVE EMERGENCY DISPATCH & NAVIGATION SYSTEM (BLINKIT/ZEPTO STYLE)
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

    function getDistanceMeters(lat1, lon1, lat2, lon2) {{
      return getDistanceKm(lat1, lon1, lat2, lon2) * 1000;
    }}

    function calculateBearing(lat1, lng1, lat2, lng2) {{
      const dLng = (lng2 - lng1) * Math.PI / 180;
      const phi1 = lat1 * Math.PI / 180;
      const phi2 = lat2 * Math.PI / 180;
      const y = Math.sin(dLng) * Math.cos(phi2);
      const x = Math.cos(phi1) * Math.sin(phi2) - Math.sin(phi1) * Math.cos(phi2) * Math.cos(dLng);
      return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
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

    // Turn Arrow SVGs (Strictly No Emojis)
    function getTurnSvg(action) {{
      switch(action) {{
        case 'left':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg>';
        case 'right':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="15 14 20 9 15 4"/><path d="M4 20v-7a4 4 0 0 1 4-4h12"/></svg>';
        case 'sharp-left':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="7 12 3 8 7 4"/><path d="M19 20v-8a4 4 0 0 0-4-4H3"/></svg>';
        case 'sharp-right':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="17 12 21 8 17 4"/><path d="M5 20v-8a4 4 0 0 1 4-4h12"/></svg>';
        case 'slight-left':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="6 10 6 4 12 4"/><line x1="6" y1="4" x2="18" y2="16"/><line x1="18" y1="16" x2="18" y2="20"/></svg>';
        case 'slight-right':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="18 10 18 4 12 4"/><line x1="18" y1="4" x2="6" y2="16"/><line x1="6" y1="16" x2="6" y2="20"/></svg>';
        case 'uturn':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><polyline points="9 10 4 15 9 20"/><path d="M20 4v7a5 5 0 0 1-10 0V4"/><line x1="4" y1="15" x2="10" y2="15"/></svg>';
        case 'arrive':
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>';
        default:
          return '<svg class="svg-maneuver" viewBox="0 0 24 24"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>';
      }}
    }}

    function getManeuverDetails(step) {{
      if (!step || !step.maneuver) {{
        return {{
          action: 'straight',
          badge: 'STRAIGHT',
          instruction: 'Proceed along arterial route',
          street: 'Main Road'
        }};
      }}
      const type = (step.maneuver.type || '').toLowerCase();
      const mod = (step.maneuver.modifier || '').toLowerCase();
      const streetName = step.name ? `onto ${{step.name}}` : 'along corridor';

      if (type === 'arrive') {{
        return {{
          action: 'arrive',
          badge: 'ARRIVE',
          instruction: 'Arrive at Target Incident Site',
          street: step.name || 'Workshop Entrance Alley'
        }};
      }}
      if (mod.includes('uturn')) {{
        return {{ action: 'uturn', badge: 'U-TURN', instruction: 'Make U-Turn', street: streetName }};
      }}
      if (mod.includes('sharp left')) {{
        return {{ action: 'sharp-left', badge: 'SHARP LEFT', instruction: 'Turn Sharp Left', street: streetName }};
      }}
      if (mod.includes('sharp right')) {{
        return {{ action: 'sharp-right', badge: 'SHARP RIGHT', instruction: 'Turn Sharp Right', street: streetName }};
      }}
      if (mod.includes('slight left')) {{
        return {{ action: 'slight-left', badge: 'SLIGHT LEFT', instruction: 'Bear Slight Left', street: streetName }};
      }}
      if (mod.includes('slight right')) {{
        return {{ action: 'slight-right', badge: 'SLIGHT RIGHT', instruction: 'Bear Slight Right', street: streetName }};
      }}
      if (mod.includes('left')) {{
        return {{ action: 'left', badge: 'TURN LEFT', instruction: 'Turn Left', street: streetName }};
      }}
      if (mod.includes('right')) {{
        return {{ action: 'right', badge: 'TURN RIGHT', instruction: 'Turn Right', street: streetName }};
      }}
      return {{ action: 'straight', badge: 'STRAIGHT', instruction: 'Continue Straight', street: streetName }};
    }}

    function createVehicleDivIcon(type, bearing, speedKmh) {{
      const isFire = (type === 'fire');
      const cls = isFire ? 'fire' : 'hospital';
      const label = isFire ? 'DFS Tender #04' : 'CATS Ambulance #02';
      const svgIcon = isFire
        ? '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="7" y1="3" x2="11" y2="3"/><line x1="9" y1="3" x2="9" y2="6"/></svg>'
        : '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="15" height="11" rx="2"/><path d="M16 8h4l3 3v6h-7V8z"/><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><line x1="6.5" y1="10" x2="10.5" y2="10"/><line x1="8.5" y1="8" x2="8.5" y2="12"/></svg>';

      return L.divIcon({{
        className: 'custom-vehicle-div-marker',
        html: `
          <div class="live-vehicle-marker" id="live-vehicle-marker-el">
            <div class="vehicle-radar-wave"></div>
            <div class="vehicle-disc ${{cls}}" id="vehicle-disc-rotator" style="transform: rotate(${{bearing || 0}}deg);">
              ${{svgIcon}}
            </div>
            <div class="vehicle-nameplate">
              <span>${{label}}</span> • <span class="vehicle-live-speed">${{speedKmh || 42}} km/h</span>
            </div>
          </div>
        `,
        iconSize: [44, 44],
        iconAnchor: [22, 22]
      }});
    }}

    function createIncidentBeaconIcon(workshop) {{
      return L.divIcon({{
        className: 'custom-fire-beacon-div-marker',
        html: `
          <div class="fire-beacon-marker">
            <div class="fire-beacon-radar"></div>
            <div class="fire-beacon-disc">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="#ffffff"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"/></svg>
            </div>
            <div class="fire-beacon-label">INCIDENT: ${{workshop.ent.toUpperCase()}}</div>
          </div>
        `,
        iconSize: [44, 44],
        iconAnchor: [22, 22]
      }});
    }}

    // Trigger Fire Emergency on any Workshop (e.g. Shop A or Selected)
    function triggerShopFireIncident(workshop, type) {{
      const w = workshop || selectedWorkshop || WORKSHOPS_DATA[0];
      activeIncidentWorkshop = w;
      selectedWorkshop = w;
      updatePreviewCard(w);
      closeWorkshopModal();

      if (incidentBeaconMarker && map) {{
        map.removeLayer(incidentBeaconMarker);
      }}
      incidentBeaconMarker = L.marker([w.lat, w.lng], {{
        icon: createIncidentBeaconIcon(w),
        zIndexOffset: 3000
      }}).addTo(map);

      triggerLiveDispatch(type || 'fire');
    }}
    window.triggerShopFireIncident = triggerShopFireIncident;

    // Dispatch Emergency Response (Fire Brigade or Hospital Ambulance)
    function triggerLiveDispatch(type) {{
      const w = activeIncidentWorkshop || selectedWorkshop || WORKSHOPS_DATA[0];
      activeIncidentWorkshop = w;
      const isFire = (type === 'fire');

      const tabFire = document.getElementById('tab-dispatch-fire');
      const tabHosp = document.getElementById('tab-dispatch-hospital');
      if (tabFire) tabFire.classList.toggle('active', isFire);
      if (tabHosp) tabHosp.classList.toggle('active', !isFire);

      const origin = isFire
        ? findNearestFireStation(w.lat, w.lng)
        : findNearestHospital(w.lat, w.lng);

      const navCard = document.getElementById('route-card');
      if (navCard) navCard.classList.add('active');

      const targetEl = document.getElementById('nav-target-name');
      const statusEl = document.getElementById('nav-incident-status');
      const origEl = document.getElementById('progress-origin-label');
      const destEl = document.getElementById('progress-dest-label');
      const fallbackEl = document.getElementById('route-fallback-notice');

      if (targetEl) targetEl.textContent = `Target: ${{w.ent}} (${{w.loc}})`;
      if (statusEl) statusEl.textContent = isFire ? 'DFS TENDER DISPATCHED • SIREN ACTIVE' : 'CATS AMBULANCE DISPATCHED • CODE BLUE';
      if (origEl) origEl.textContent = origin.name;
      if (destEl) destEl.textContent = w.ent;
      if (fallbackEl) fallbackEl.style.display = 'none';

      clearRouteLayersOnly();

      const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${{origin.lng}},${{origin.lat}};${{w.lng}},${{w.lat}}?overview=full&geometries=geojson&steps=true`;

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
          prepareRouteSimulation(data.routes[0], type, w, origin);
        }})
        .catch(err => {{
          console.warn('OSRM router failed or timed out, generating calculated corridor simulation:', err);
          if (fallbackEl) fallbackEl.style.display = 'block';
          const syntheticRoute = createSyntheticRoute([origin.lat, origin.lng], [w.lat, w.lng], origin.name, w.ent);
          prepareRouteSimulation(syntheticRoute, type, w, origin);
        }});
    }}
    window.triggerLiveDispatch = triggerLiveDispatch;

    function switchDispatchVehicle(type) {{
      document.getElementById('tab-dispatch-fire').classList.toggle('active', type === 'fire');
      document.getElementById('tab-dispatch-hospital').classList.toggle('active', type === 'hospital');
      if (activeIncidentWorkshop) {{
        triggerLiveDispatch(type);
      }}
    }}
    window.switchDispatchVehicle = switchDispatchVehicle;

    function triggerRouteFromFireStation() {{
      triggerLiveDispatch('fire');
    }}
    window.triggerRouteFromFireStation = triggerRouteFromFireStation;

    function triggerRouteToHospital() {{
      triggerLiveDispatch('hospital');
    }}
    window.triggerRouteToHospital = triggerRouteToHospital;

    function triggerRouteFromUser() {{
      if (!navigator.geolocation) {{
        alert('Geolocation not supported by browser.');
        return;
      }}
      navigator.geolocation.getCurrentPosition(
        (pos) => {{
          const userLat = pos.coords.latitude;
          const userLng = pos.coords.longitude;
          const w = selectedWorkshop || WORKSHOPS_DATA[0];
          
          if (userLocationMarker && map) map.removeLayer(userLocationMarker);
          userLocationMarker = L.circleMarker([userLat, userLng], {{
            radius: 8,
            fillColor: '#0284c7',
            color: '#ffffff',
            weight: 3,
            fillOpacity: 1
          }}).bindPopup('<strong>Your Location</strong>').addTo(map);

          activeIncidentWorkshop = w;
          const origin = {{ name: 'Your GPS Location', lat: userLat, lng: userLng }};
          
          const navCard = document.getElementById('route-card');
          if (navCard) navCard.classList.add('active');

          const targetEl = document.getElementById('nav-target-name');
          const statusEl = document.getElementById('nav-incident-status');
          const origEl = document.getElementById('progress-origin-label');
          const destEl = document.getElementById('progress-dest-label');
          if (targetEl) targetEl.textContent = `Target: ${{w.ent}} (${{w.loc}})`;
          if (statusEl) statusEl.textContent = 'FIELD SURVEYOR EN ROUTE';
          if (origEl) origEl.textContent = 'Your Position';
          if (destEl) destEl.textContent = w.ent;

          clearRouteLayersOnly();

          const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${{userLng}},${{userLat}};${{w.lng}},${{w.lat}}?overview=full&geometries=geojson&steps=true`;
          fetch(osrmUrl)
            .then(res => res.json())
            .then(data => {{
              if (!data.routes || !data.routes.length) throw new Error('No route');
              prepareRouteSimulation(data.routes[0], 'surveyor', w, origin);
            }})
            .catch(() => {{
              const synth = createSyntheticRoute([userLat, userLng], [w.lat, w.lng], 'Your Position', w.ent);
              prepareRouteSimulation(synth, 'surveyor', w, origin);
            }});
        }},
        () => {{
          alert('Could not acquire GPS position. Check browser permissions.');
        }},
        {{ timeout: 10000, enableHighAccuracy: true }}
      );
    }}
    window.triggerRouteFromUser = triggerRouteFromUser;

    function createSyntheticRoute(startLatLng, endLatLng, startName, endName) {{
      const dKm = getDistanceKm(startLatLng[0], startLatLng[1], endLatLng[0], endLatLng[1]);
      const estDistM = Math.round(dKm * 1.35 * 1000);
      const estDurationS = Math.round((estDistM / 1000 / 30.0) * 3600);

      const coords = [];
      const stepsCount = 12;
      for (let i = 0; i <= stepsCount; i++) {{
        const ratio = i / stepsCount;
        const jitterLat = (i > 0 && i < stepsCount) ? (Math.sin(i * 1.6) * 0.0011) : 0;
        const jitterLng = (i > 0 && i < stepsCount) ? (Math.cos(i * 1.6) * 0.0011) : 0;
        coords.push([
          startLatLng[1] + (endLatLng[1] - startLatLng[1]) * ratio + jitterLng,
          startLatLng[0] + (endLatLng[0] - startLatLng[0]) * ratio + jitterLat
        ]);
      }}

      return {{
        distance: estDistM,
        duration: estDurationS,
        geometry: {{ coordinates: coords }},
        legs: [{{
          steps: [
            {{ maneuver: {{ type: 'depart', modifier: null, location: [coords[0][0], coords[0][1]] }}, name: startName, distance: estDistM * 0.25 }},
            {{ maneuver: {{ type: 'turn', modifier: 'right', location: [coords[3][0], coords[3][1]] }}, name: 'Grand Trunk Road', distance: estDistM * 0.35 }},
            {{ maneuver: {{ type: 'turn', modifier: 'left', location: [coords[7][0], coords[7][1]] }}, name: 'Main Seelampur Commercial Road', distance: estDistM * 0.25 }},
            {{ maneuver: {{ type: 'turn', modifier: 'sharp right', location: [coords[10][0], coords[10][1]] }}, name: 'Internal Workshop Alley', distance: estDistM * 0.15 }},
            {{ maneuver: {{ type: 'arrive', modifier: null, location: [coords[coords.length-1][0], coords[coords.length-1][1]] }}, name: endName, distance: 0 }}
          ]
        }}]
      }};
    }}

    function prepareRouteSimulation(route, type, targetWorkshop, originFacility) {{
      stopSimulation();

      const coords = route.geometry.coordinates.map(c => [c[1], c[0]]);
      const distances = [0];
      let totalD = 0;
      for (let i = 1; i < coords.length; i++) {{
        const d = getDistanceMeters(coords[i-1][0], coords[i-1][1], coords[i][0], coords[i][1]);
        totalD += d;
        distances.push(totalD);
      }}

      simState.route = route;
      simState.type = type;
      simState.targetWorkshop = targetWorkshop;
      simState.originFacility = originFacility;
      simState.coords = coords;
      simState.distances = distances;
      simState.totalDist = totalD;
      simState.totalDuration = Math.max(16, route.duration || 120);
      simState.elapsed = 0;
      simState.currentStepIndex = 0;
      simState.running = true;
      simState.paused = false;

      const isFire = (type === 'fire');
      const routeColor = isFire ? '#dc2626' : (type === 'hospital' ? '#0284c7' : '#0e7490');

      // Draw Route Polylines
      const casing = L.polyline(coords, {{ color: '#ffffff', weight: 8, opacity: 0.95 }}).addTo(map);
      simRemainingLine = L.polyline(coords, {{ color: routeColor, weight: 5, opacity: 0.95 }}).addTo(map);
      simTraveledLine = L.polyline([coords[0]], {{ color: '#475569', weight: 5, opacity: 0.8 }}).addTo(map);

      currentRouteLayers.push(casing, simRemainingLine, simTraveledLine);

      // Station / Origin Marker
      const originMarker = L.marker([originFacility.lat, originFacility.lng], {{
        icon: L.divIcon({{
          className: 'route-start-icon',
          html: `<div style="background:#16a34a; color:#fff; border:2px solid #fff; border-radius:50%; width:22px; height:22px; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:800; box-shadow:0 2px 6px rgba(0,0,0,0.3);">START</div>`,
          iconSize: [22, 22],
          iconAnchor: [11, 11]
        }})
      }}).bindPopup(`<strong>${{originFacility.name}}</strong><br>Dispatch Hub`).addTo(map);

      currentRouteLayers.push(originMarker);

      // Destination Target Marker (if beacon not already present)
      if (!incidentBeaconMarker) {{
        incidentBeaconMarker = L.marker([targetWorkshop.lat, targetWorkshop.lng], {{
          icon: createIncidentBeaconIcon(targetWorkshop),
          zIndexOffset: 3000
        }}).addTo(map);
      }}

      // Create Moving Live Vehicle Marker
      const initialBearing = coords.length > 1 ? calculateBearing(coords[0][0], coords[0][1], coords[1][0], coords[1][1]) : 0;
      liveVehicleMarker = L.marker(coords[0], {{
        icon: createVehicleDivIcon(type, initialBearing, 42),
        zIndexOffset: 3500
      }}).addTo(map);
      currentRouteLayers.push(liveVehicleMarker);

      simState.vehicleMarker = liveVehicleMarker;
      simState.traveledPolyline = simTraveledLine;
      simState.remainingPolyline = simRemainingLine;

      simState.routeBounds = casing.getBounds();
      map.fitBounds(simState.routeBounds, {{
        paddingTopLeft: [50, 50],
        paddingBottomRight: [50, 50]
      }});

      // Populate Turn-by-Turn Cue Sheet
      const stepsContainer = document.getElementById('route-steps');
      stepsContainer.innerHTML = '';
      const countEl = document.getElementById('route-steps-count');
      const steps = route.legs && route.legs[0] && route.legs[0].steps ? route.legs[0].steps : [];
      if (countEl) countEl.textContent = `${{steps.length}} turns`;

      steps.forEach((step, idx) => {{
        const item = document.createElement('div');
        item.className = 'route-step-item' + (idx === 0 ? ' active-turn' : '');
        const info = getManeuverDetails(step);
        const distM = Math.round(step.distance || 0);

        item.innerHTML = `
          <div class="step-icon" style="color:${{info.action.includes('left') || info.action.includes('right') ? '#16a34a' : '#0e7490'}}">
            ${{getTurnSvg(info.action)}}
          </div>
          <div class="step-text">
            <div>
              <span class="step-direction-pill">${{info.badge}}</span>
              <strong>${{info.instruction}}</strong> ${{info.street}}
            </div>
            <div class="step-dist">${{distM > 0 ? distM + ' metres' : 'At incident point'}}</div>
          </div>
        `;

        item.onclick = () => {{
          if (step.maneuver && step.maneuver.location) {{
            const loc = step.maneuver.location;
            map.flyTo([loc[1], loc[0]], 18, {{ duration: 0.8 }});
          }}
        }};

        stepsContainer.appendChild(item);
      }});

      // Reset controls
      const playIcon = document.getElementById('sim-play-icon');
      const playText = document.getElementById('sim-play-text');
      if (playText) playText.textContent = 'Pause';
      if (playIcon) playIcon.innerHTML = `<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>`;

      // Start tick loop
      simState.lastTimestamp = performance.now();
      simState.animFrameId = requestAnimationFrame(simulationTick);
    }}

    function simulationTick(timestamp) {{
      if (!simState.running) return;

      if (simState.paused) {{
        simState.lastTimestamp = timestamp;
        simState.animFrameId = requestAnimationFrame(simulationTick);
        return;
      }}

      const dt = (timestamp - simState.lastTimestamp) / 1000;
      simState.lastTimestamp = timestamp;

      // Accelerated virtual time: complete route in ~32 seconds at 1x
      const virtualSpeed = (simState.totalDist / 32.0) * simState.speedMultiplier;
      simState.elapsed += dt * virtualSpeed;

      const progress = Math.min(1.0, simState.elapsed / simState.totalDist);
      const curDist = progress * simState.totalDist;

      // Find current segment along route geometry
      let segIdx = 0;
      while (segIdx < simState.distances.length - 1 && simState.distances[segIdx + 1] < curDist) {{
        segIdx++;
      }}

      let curLat, curLng, bearing = 0;
      if (segIdx >= simState.coords.length - 1) {{
        const last = simState.coords[simState.coords.length - 1];
        curLat = last[0];
        curLng = last[1];
      }} else {{
        const p1 = simState.coords[segIdx];
        const p2 = simState.coords[segIdx + 1];
        const d1 = simState.distances[segIdx];
        const d2 = simState.distances[segIdx + 1];
        const segRatio = (d2 > d1) ? (curDist - d1) / (d2 - d1) : 0;
        curLat = p1[0] + (p2[0] - p1[0]) * segRatio;
        curLng = p1[1] + (p2[1] - p1[1]) * segRatio;
        bearing = calculateBearing(p1[0], p1[1], p2[0], p2[1]);
      }}

      // Dynamic Speedometer with subtle realistic oscillation
      const liveSpeed = progress >= 1.0 ? 0 : Math.round(38 + Math.sin(simState.elapsed * 0.05) * 5);

      // Update vehicle marker position and rotation
      if (simState.vehicleMarker) {{
        simState.vehicleMarker.setLatLng([curLat, curLng]);
        const rotator = document.getElementById('vehicle-disc-rotator');
        if (rotator) rotator.style.transform = `rotate(${{bearing}}deg)`;
        const spdEl = document.querySelector('.vehicle-live-speed');
        if (spdEl) spdEl.textContent = `${{liveSpeed}} km/h`;
      }}

      // Update traveled vs remaining polylines
      const traveledPoints = simState.coords.slice(0, segIdx + 1);
      traveledPoints.push([curLat, curLng]);
      if (simState.traveledPolyline) simState.traveledPolyline.setLatLngs(traveledPoints);

      const remainingPoints = [[curLat, curLng], ...simState.coords.slice(segIdx + 1)];
      if (simState.remainingPolyline) simState.remainingPolyline.setLatLngs(remainingPoints);

      // Follow vehicle camera auto-pan
      if (simState.followVehicle && map && progress < 1.0) {{
        map.panTo([curLat, curLng], {{ animate: false }});
      }}

      // Telemetry metrics calculation
      const remainingMeters = Math.max(0, simState.totalDist - curDist);
      const remainingSeconds = Math.max(0, Math.round((1.0 - progress) * (simState.totalDuration / simState.speedMultiplier)));

      updateTelemetryHUD(progress, remainingMeters, remainingSeconds, liveSpeed);
      updateNavigationStepGuidance(curLat, curLng);

      if (progress < 1.0) {{
        simState.animFrameId = requestAnimationFrame(simulationTick);
      }} else {{
        onVehicleArrival();
      }}
    }}

    function updateNavigationStepGuidance(curLat, curLng) {{
      if (!simState.route || !simState.route.legs || !simState.route.legs[0]) return;
      const steps = simState.route.legs[0].steps;
      if (!steps || !steps.length) return;

      let idx = simState.currentStepIndex;
      while (idx < steps.length - 1) {{
        const nextLoc = steps[idx].maneuver.location;
        const d = getDistanceMeters(curLat, curLng, nextLoc[1], nextLoc[0]);
        if (d < 30 && idx < steps.length - 1) {{
          idx++;
        }} else {{
          break;
        }}
      }}
      simState.currentStepIndex = idx;

      const currentStep = steps[idx];
      const info = getManeuverDetails(currentStep);
      const nextLoc = currentStep.maneuver.location;
      const distToTurn = Math.round(getDistanceMeters(curLat, curLng, nextLoc[1], nextLoc[0]));

      const iconWrap = document.getElementById('next-turn-icon');
      const badgeEl = document.getElementById('next-turn-badge');
      const distEl = document.getElementById('next-turn-distance');
      const streetEl = document.getElementById('next-turn-street');

      if (iconWrap) iconWrap.innerHTML = getTurnSvg(info.action);
      if (badgeEl) {{
        badgeEl.textContent = info.badge;
        badgeEl.style.background = (info.action.includes('left') || info.action.includes('right')) ? '#22c55e' : (info.action === 'arrive' ? '#ef4444' : '#0e7490');
      }}
      if (distEl) distEl.textContent = (info.action === 'arrive' && distToTurn < 25) ? 'On Scene' : `In ${{distToTurn}}m`;
      if (streetEl) streetEl.textContent = `${{info.instruction}} ${{info.street}}`;

      const stepItems = document.querySelectorAll('.route-step-item');
      stepItems.forEach((el, i) => {{
        el.classList.toggle('active-turn', i === idx);
        el.classList.toggle('completed-turn', i < idx);
      }});
    }}

    function updateTelemetryHUD(progress, remainingMeters, remainingSeconds, speedKmh) {{
      const etaEl = document.getElementById('telemetry-eta');
      const distEl = document.getElementById('telemetry-distance');
      const speedEl = document.getElementById('telemetry-speed');
      const fillEl = document.getElementById('rider-progress-fill');
      const percentEl = document.getElementById('progress-percent-label');

      const mins = Math.floor(remainingSeconds / 60);
      const secs = Math.floor(remainingSeconds % 60);
      if (etaEl) etaEl.textContent = (remainingSeconds <= 1) ? '0m 00s (On Scene)' : `${{mins}}m ${{secs < 10 ? '0' : ''}}${{secs}}s`;
      if (distEl) distEl.textContent = remainingMeters > 1000 ? `${{(remainingMeters / 1000).toFixed(1)}} km` : `${{Math.round(remainingMeters)}} m`;
      if (speedEl) speedEl.textContent = `${{speedKmh}} km/h`;

      const pct = Math.min(100, Math.round(progress * 100));
      if (fillEl) fillEl.style.width = `${{pct}}%`;
      if (percentEl) percentEl.textContent = (pct >= 100) ? 'Arrived on Scene' : `${{pct}}% En Route`;
    }}

    function onVehicleArrival() {{
      simState.running = false;
      const playIcon = document.getElementById('sim-play-icon');
      const playText = document.getElementById('sim-play-text');
      if (playText) playText.textContent = 'Restart';
      if (playIcon) playIcon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"/>';

      const isFire = (simState.type === 'fire');
      const statusTag = document.getElementById('nav-incident-status');
      if (statusTag) {{
        statusTag.textContent = isFire
          ? 'DFS TENDER ON-SCENE • HOSES RELAYED'
          : 'CATS AMBULANCE ON-SCENE • TRIAGE DEPLOYED';
      }}

      updateTelemetryHUD(1.0, 0, 0, 0);
    }}

    function toggleSimPause() {{
      if (!simState.running && simState.route) {{
        prepareRouteSimulation(simState.route, simState.type, simState.targetWorkshop, simState.originFacility);
        return;
      }}
      simState.paused = !simState.paused;
      const playIcon = document.getElementById('sim-play-icon');
      const playText = document.getElementById('sim-play-text');
      if (simState.paused) {{
        if (playText) playText.textContent = 'Resume';
        if (playIcon) playIcon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"/>';
      }} else {{
        if (playText) playText.textContent = 'Pause';
        if (playIcon) playIcon.innerHTML = '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>';
      }}
    }}
    window.toggleSimPause = toggleSimPause;

    function setSimSpeed(speed) {{
      simState.speedMultiplier = speed;
      [1, 2, 4].forEach(s => {{
        const btn = document.getElementById('sim-speed-' + s);
        if (btn) btn.classList.toggle('active', s === speed);
      }});
    }}
    window.setSimSpeed = setSimSpeed;

    function toggleFollowVehicle() {{
      simState.followVehicle = !simState.followVehicle;
      const text = document.getElementById('follow-toggle-text');
      if (text) text.textContent = simState.followVehicle ? 'Follow: ON' : 'Follow: OFF';
      const btn = document.getElementById('btn-follow-toggle');
      if (btn) btn.classList.toggle('active', simState.followVehicle);
    }}
    window.toggleFollowVehicle = toggleFollowVehicle;

    function fitRouteBounds() {{
      if (simState.routeBounds && map) {{
        map.fitBounds(simState.routeBounds, {{ paddingTopLeft: [50, 50], paddingBottomRight: [50, 50] }});
      }}
    }}
    window.fitRouteBounds = fitRouteBounds;

    function clearNavigationRoute() {{
      stopSimulation();
      clearRouteLayersOnly();
      if (incidentBeaconMarker && map) {{
        map.removeLayer(incidentBeaconMarker);
        incidentBeaconMarker = null;
      }}
      activeIncidentWorkshop = null;
      const card = document.getElementById('route-card');
      if (card) card.classList.remove('active');
    }}
    window.clearNavigationRoute = clearNavigationRoute;

    function clearRouteLayersOnly() {{
      if (simState.vehicleMarker && map) map.removeLayer(simState.vehicleMarker);
      if (simState.traveledPolyline && map) map.removeLayer(simState.traveledPolyline);
      if (simState.remainingPolyline && map) map.removeLayer(simState.remainingPolyline);
      currentRouteLayers.forEach(l => {{ if (map && map.hasLayer(l)) map.removeLayer(l); }});
      currentRouteLayers = [];
    }}

    function stopSimulation() {{
      simState.running = false;
      if (simState.animFrameId) {{
        cancelAnimationFrame(simState.animFrameId);
        simState.animFrameId = null;
      }}
    }}

    '''

    match = re.search(old_nav_js_regex, content)
    if not match:
        print("ERROR: old_nav_js_regex failed to match!")
        sys.exit(1)
    content = content[:match.start()] + new_nav_js + content[match.end():]

    with open('generate_app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated generate_app.py with Live Navigation and Tracking engine!")

if __name__ == '__main__':
    main()
