# update_staging_roads.py
with open('generate_app.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('const ARTERIAL_STAGING_ROADS = [')
end_idx = c.find('];', idx) + 2

new_staging_block = """const ARTERIAL_STAGING_ROADS = [
      {{ name: 'Grand Trunk Road (GT Road Arterial)', widthM: 30.0, lat: 28.6685, lng: 77.2665, desc: '6-Lane Divided Arterial Corridor — Major Heavy Tender Staging Base' }},
      {{ name: 'Marginal Bund Road (Pusta Road)', widthM: 24.0, lat: 28.6635, lng: 77.2685, desc: 'Arterial Embankment Highway — South-West Heavy Vehicle Staging Area' }},
      {{ name: 'Dharampura / Seelampur 100ft Road', widthM: 22.0, lat: 28.6630, lng: 77.2715, desc: '4-Lane Primary Collector — Direct Water Relay Connection' }},
      {{ name: 'Jafrabad Main Road', widthM: 18.0, lat: 28.6698, lng: 77.2710, desc: 'North Sector Commercial Arterial — Motorable Access Point' }},
      {{ name: 'Welcome Flyover Service Road', widthM: 20.0, lat: 28.6705, lng: 77.2735, desc: 'Elevated Corridor Service Bay — Heavy Water Bowser Staging Hub' }},
      {{ name: 'Swami Dayanand Marg (Shanti Mohalla Access)', widthM: 28.0, lat: 28.6655, lng: 77.2768, desc: 'East Perimeter Arterial — Primary High-Capacity Relay Point' }}
    ];"""

c = c[:idx] + new_staging_block + c[end_idx:]
with open('generate_app.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("SUCCESS: ARTERIAL_STAGING_ROADS updated with real perimeter coordinates!")
