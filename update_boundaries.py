# update_boundaries.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = """    function buildLocalityBoundaryLayers() {{
      const polygons = [];
      const colors = {{
        'Seelampur': '#0891b2',
        'Gandhi Nagar': '#2563eb',
        'Shanti Mohalla': '#dc2626',
        'Subhash Nagar': '#059669'
      }};

      Object.entries(LOCALITY_POLYGONS).forEach(([loc, coords]) => {{
        const color = colors[loc] || '#0891b2';
        const poly = L.polygon(coords, {{
          color: color,
          weight: 2,
          dashArray: '6, 6',
          fillColor: color,
          fillOpacity: 0.05
        }});

        poly.bindTooltip(`
          <div style="font-weight:700; font-size:11px; text-transform:uppercase; color:${{color}};">
            ${{loc}} Settlement Area
          </div>
        `, {{ sticky: true, className: 'custom-map-tooltip' }});

        polygons.push(poly);
      }});

      // Boundary layer created but NOT added by default to prevent visual clutter
      boundaryLayer = L.layerGroup(polygons);
    }}"""

replacement = """    function buildLocalityBoundaryLayers() {{
      const polygons = [];

      // Official Cadastral Survey Boundary Polygon (USAP Field Study Area)
      if (typeof STUDY_AREA_POLYGON !== 'undefined' && STUDY_AREA_POLYGON.length) {{
        const studyPoly = L.polygon(STUDY_AREA_POLYGON, {{
          color: '#0891b2',
          weight: 2.5,
          dashArray: '6, 6',
          fillColor: '#0891b2',
          fillOpacity: 0.06
        }});

        studyPoly.bindTooltip(`
          <div style="font-weight:700; font-size:11px; text-transform:uppercase; color:#0891b2;">
            USAP Seelampur Cadastral Study Area Boundary
          </div>
        `, {{ sticky: true, className: 'custom-map-tooltip' }});

        polygons.push(studyPoly);
      }}

      // Boundary layer created but NOT added by default to prevent visual clutter
      boundaryLayer = L.layerGroup(polygons);
    }}"""

if target in c:
    c = c.replace(target, replacement, 1)
    with open('generate_app.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("SUCCESS: buildLocalityBoundaryLayers updated with authentic study area polygon!")
else:
    print("Target not found, checking...")
