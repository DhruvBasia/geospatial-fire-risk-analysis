import random
import math
import json

random.seed(26)

SCORING_MAP = {
    'exits': {'1 exit': 1.0, '2 exits': 0.4, '3+ exits': 0.1},
    'obstruction': {'obstructed': 1.0, 'partially_clear': 0.6, 'clear': 0.0},
    'emergency_exits': {'none': 1.0, 'locked_or_blocked': 0.8, 'functional': 0.1},
    'stair_width': {'under_0_8m': 1.0, '0_8_to_1_2m': 0.6, 'over_1_2m': 0.1},
    'workspace': {'under_200sqft': 1.0, '200_to_500sqft': 0.6, 'over_500sqft': 0.2},
    'floors': {'g_plus_3_or_more': 1.0, 'g_plus_2': 0.7, 'g_plus_1': 0.4, 'ground_only': 0.1},
    'light': {'dark_no_vent': 1.0, 'dim_partial': 0.6, 'well_lit': 0.1},
    'windows': {'no_windows_or_barred': 1.0, 'few_restricted': 0.6, 'operable_clear': 0.1},
    'corridor': {'under_1m_cluttered': 1.0, '1_to_1_5m': 0.5, 'wide_clear': 0.1},
    'dust': {'heavy_flammable_lint': 1.0, 'moderate_dust': 0.5, 'low_dust': 0.1},
    'building_gap': {'shared_wall_0m': 1.0, 'narrow_gap_under_1m': 0.7, 'gap_over_1m': 0.1},
    'waste_burning': {'daily_open_burning': 1.0, 'occasional_burning': 0.6, 'none': 0.1},
    'station_dist': {'over_3km': 1.0, '1_5_to_3km': 0.6, 'under_1_5km': 0.2},
    'response_time': {'over_25min': 1.0, '15_to_25min': 0.6, 'under_15min': 0.2},
    'approach_road': {'narrow_under_2_5m': 1.0, 'medium_2_5_to_4m': 0.6, 'wide_over_4m': 0.1}
}

egress_factors = ['exits', 'obstruction', 'emergency_exits', 'stair_width', 'workspace', 'floors', 'light', 'windows', 'corridor']
hazard_factors = ['waste_burning', 'dust', 'building_gap']
access_factors = ['station_dist', 'response_time', 'approach_road']

def calc_fri(cats):
    egress = sum(SCORING_MAP[f][cats[f]] for f in egress_factors) / len(egress_factors)
    hazard = sum(SCORING_MAP[f][cats[f]] for f in hazard_factors) / len(hazard_factors)
    access = sum(SCORING_MAP[f][cats[f]] for f in access_factors) / len(access_factors)
    return (0.45 * egress + 0.25 * hazard + 0.30 * access), egress, hazard, access

def get_tier(score):
    if score < 0.30: return 'Low'
    if score < 0.50: return 'Moderate'
    if score < 0.70: return 'High'
    return 'Severe'

base_probs = {
    'exits': [('1 exit', 0.88), ('2 exits', 0.09), ('3+ exits', 0.03)],
    'obstruction': [('obstructed', 0.64), ('partially_clear', 0.24), ('clear', 0.12)],
    'emergency_exits': [('none', 0.76), ('locked_or_blocked', 0.16), ('functional', 0.08)],
    'stair_width': [('under_0_8m', 0.56), ('0_8_to_1_2m', 0.30), ('over_1_2m', 0.14)],
    'workspace': [('under_200sqft', 0.48), ('200_to_500sqft', 0.36), ('over_500sqft', 0.16)],
    'floors': [('g_plus_3_or_more', 0.40), ('g_plus_2', 0.36), ('g_plus_1', 0.16), ('ground_only', 0.08)],
    'light': [('dark_no_vent', 0.50), ('dim_partial', 0.32), ('well_lit', 0.18)],
    'windows': [('no_windows_or_barred', 0.58), ('few_restricted', 0.28), ('operable_clear', 0.14)],
    'corridor': [('under_1m_cluttered', 0.54), ('1_to_1_5m', 0.32), ('wide_clear', 0.14)],
    'dust': [('heavy_flammable_lint', 0.56), ('moderate_dust', 0.30), ('low_dust', 0.14)],
    'building_gap': [('shared_wall_0m', 0.80), ('narrow_gap_under_1m', 0.13), ('gap_over_1m', 0.07)],
    'waste_burning': [('daily_open_burning', 0.48), ('occasional_burning', 0.34), ('none', 0.18)],
    'station_dist': [('over_3km', 0.48), ('1_5_to_3km', 0.36), ('under_1_5km', 0.16)],
    'response_time': [('over_25min', 0.50), ('15_to_25min', 0.34), ('under_15min', 0.16)],
    'approach_road': [('narrow_under_2_5m', 0.66), ('medium_2_5_to_4m', 0.22), ('wide_over_4m', 0.12)]
}

localities_cfg = [
    ('Shanti Mohalla', 28.6648, 77.2768, 38, 0.35),
    ('Seelampur', 28.6705, 77.2700, 48, 0.10),
    ('Gandhi Nagar', 28.6590, 77.2665, 42, -0.05),
    ('Subhash Nagar', 28.6762, 77.2780, 30, -0.42)
]

def sample_factor(f, bias):
    opts = base_probs[f]
    weights = [max(0.01, p * (1.0 + (SCORING_MAP[f][o] - 0.5) * bias * 2.0)) for o, p in opts]
    return random.choices([o for o, _ in opts], weights=weights, k=1)[0]

names_pool = {
    'Seelampur': [
        ('Al-Madina Denim Washing Unit', 'Denim Stone-Washing & Dyeing', 'Block C Gali 3'),
        ('National E-Waste Dismantling Works', 'E-Waste PCB Recovery', 'Kabari Market Lane'),
        ('Farhan Plastic Granule Recyclers', 'Plastic Shredding & Melting', 'Gali No. 7 Shastri Park Rd'),
        ('Delhi Copper Stripping Workshop', 'Wire Stripping & Smelting', 'Near Chhota Seelampur Masjid'),
        ('Rehman Fabric Finishing', 'Denim Bleaching & Pressing', 'Block C Gali 4'),
        ('Hindustan Battery Scrap Traders', 'Lead Plate Dismantling', 'Old Seelampur Phirni'),
        ('Bismillah Carton & Corrugated Boxes', 'Cardboard Packaging', 'Gali No. 12 GT Road'),
        ('Shahid Screen Printing Works', 'Textile Pigment Printing', 'Gali No. 4 E-Waste Mandi'),
        ('Apex Brass Buffing & Polishing', 'Metal Polishing & Lacquer', 'Block D Gali 2'),
        ('Khan Upholstery & Cushion Works', 'Foam Cutting & Upholstery', 'Gali No. 18 Jafrabad Rd'),
        ('New Star Jeans Scrap Shredders', 'Fabric Waste Chindi Sorting', 'Block C Back Alley'),
        ('Zubair Circuit Board Salvage', 'Electronic Scrap Processing', 'Gali Kabari Mandi'),
        ('Modern Garment Washing Plant', 'Industrial Denim Laundering', 'Near DDA Park'),
        ('Barkat Cable Recycling Co.', 'Copper Wire Burning/Stripping', 'Block D Gali 5'),
        ('Star Auto Part Electroplating', 'Chemical Plating & Buffing', 'Gali No. 9 GT Road')
    ],
    'Gandhi Nagar': [
        ('Mahavir Garment Stitching Unit', 'RMG Sewing & Assembly', 'Mahavir Gali'),
        ('Kailash Cloth Cutting Hub', 'Bulk Fabric Shearing', 'Kailash Gali Cloth Market'),
        ('Shree Krishna Jeans Riveting', 'Hardware Punching & Rivets', 'Subhash Road Market'),
        ('Prem Sewing Machine Jobwork', 'Bulk Shirt Tailoring', 'Prem Gali Garment Hub'),
        ('Ashok Thread & Yarn Spooling', 'Synthetic Thread Winding', 'Ashok Gali Cloth Lane'),
        ('Paras Collar & Cuff Fusing', 'Heat-Press Collar Fusing', 'Gali Jain Mandir'),
        ('Vardhman Denim Finishing Works', 'Jeans Tagging & Ironing', 'Ram Nagar Main Road'),
        ('Goyal Readymade Packing Unit', 'Plastic Shrink Wrapping', 'Main Market Gali 2'),
        ('Tirupati Embroidery Works', 'Multi-Head Machine Embroidery', 'Gali No. 5 Garment Cluster'),
        ('Jain Button & Zipper Attachment', 'Garment Trims Assembly', 'Shanti Marg Wholesale Lane'),
        ('Navkar Fabric Wholesale Storage', 'Cloth Roll Godown', 'Ram Nagar Gali 4'),
        ('Balaji Hosiery Knitting Unit', 'Innerwear Cotton Knitting', 'Subhash Road Gali 7'),
        ('Gupta Jeans Overlock Workshop', 'Overlock & Hem Stitching', 'Mahavir Gali Lane 2'),
        ('Aggarwal Textile Job-Worker', 'Fabric Batch Printing', 'Kailash Gali Back Alley')
    ],
    'Shanti Mohalla': [
        ('Gupta Textile Waste Chindi Godown', 'Textile Scrap Sorting & Baling', 'Chindi Mandi Back-Alley'),
        ('Shree Ram Polyester Roll Storage', 'Synthetic Fabric Warehousing', 'Main Textile Market Lane'),
        ('Balaji Foam & Sponge Slitting', 'Foam Block Cutting & Quilting', 'Gali No. 6 Godown Lane'),
        ('Krishna Cut-Piece Fabric Bales', 'Scrap Fabric Sorting', 'Gali No. 2 Cut-Piece Market'),
        ('Radhey Shanti Chindi Hydraulic Press', 'Fabric Waste Hydraulic Baling', 'Chindi Mandi Gali 4'),
        ('Om Textile Roll Warehouse', 'Rayon & Silk Fabric Godown', 'Near Shanti Mohalla Chowk'),
        ('Aggarwal Curtain & Furnishing Godown', 'Heavy Upholstery Fabric Storage', 'Gali No. 10 Wholesale Lane'),
        ('Ganesh Denim Fabric Salvage', 'Cut-Piece Sorting & Bundling', 'Gali No. 4 Bale Godown'),
        ('Bhawani Non-Woven Interlining Godown', 'Synthetic Interlining Rolls', 'Krishna Gali Storage Cluster'),
        ('Khandelwal Scrap Fabric Bale Unit', 'Rags & Cotton Waste Baling', 'Chindi Mandi Lane 1'),
        ('Bansal Foam Mattress Quilting', 'Polyurethane Foam Assembly', 'Gali No. 8 Godown Lane'),
        ('Jai Durga Fabric Roll Sorting', 'Polyester Sheeting Warehouse', 'Shanti Mohalla Main Road')
    ],
    'Subhash Nagar': [
        ('Pooja Screen Printing & Drying', 'Screen Printing & Heat Curing', 'Pocket A Industrial Alley'),
        ('Shiv Shakti Small Motor Rewinding', 'Copper Coil Rewinding', 'Gali No. 3 Mixed Lane'),
        ('Shree Sai Packaging & Die Cutting', 'Corrugated Carton Creasing', 'Block B Work Center'),
        ('Vijay Auto Buffing & Gas Welding', 'Oxy-Acetylene Welding & Grinding', 'Main Road Gali 1'),
        ('Anand PVC Pipe & Fitting Assembly', 'Plastic Pipe Cutting & Gluing', 'Gali No. 5 Workshop Cluster'),
        ('Radha Madhav Mattress Stitching', 'Cotton Mattress Hand-Stuffing', 'Pocket C Commercial Lane'),
        ('Rathore Zipper & Elastic Hub', 'Haberdashery Assembly', 'GT Road Link Lane'),
        ('New Bright LED Assembly Workshop', 'Soldering & Driver Assembly', 'Gali No. 8 School Road'),
        ('Pawan Rubber Gasket Punching', 'Rubber Sheet Pressing', 'Block B Gali 4'),
        ('Dinesh Hardware & Wire Bending', 'Steel Wire Frame Welding', 'Gali No. 2 Workshop Lane')
    ]
}

workshops = []
workshop_counter = 1

for loc_name, center_lat, center_lng, count, bias in localities_cfg:
    pool = names_pool[loc_name]
    for i in range(count):
        wid = f"SW-{workshop_counter:03d}"
        template = pool[i % len(pool)]
        num_suffix = f" #{i // len(pool) + 1}" if i >= len(pool) else ""
        ent_name = template[0] + num_suffix
        work_type = template[1]
        area_name = template[2]
        
        # Jitter within ~450m of center
        r = random.uniform(35, 425)
        theta = random.uniform(0, 2 * math.pi)
        d_lat = (r * math.cos(theta)) / 111000.0
        d_lng = (r * math.sin(theta)) / (111000.0 * math.cos(math.radians(center_lat)))
        lat = round(center_lat + d_lat, 6)
        lng = round(center_lng + d_lng, 6)
        
        # Retrofitted low-risk model units in Subhash Nagar
        if loc_name == 'Subhash Nagar' and i in (3, 7, 14, 21):
            cats = {
                'exits': '2 exits' if i != 14 else '3+ exits',
                'obstruction': 'clear',
                'emergency_exits': 'functional',
                'stair_width': 'over_1_2m',
                'workspace': 'over_500sqft' if i in (3, 14) else '200_to_500sqft',
                'floors': 'ground_only',
                'light': 'well_lit',
                'windows': 'operable_clear',
                'corridor': 'wide_clear',
                'waste_burning': 'none',
                'dust': 'low_dust',
                'building_gap': 'gap_over_1m' if i == 14 else 'narrow_gap_under_1m',
                'station_dist': 'under_1_5km',
                'response_time': 'under_15min' if i == 14 else '15_to_25min',
                'approach_road': 'wide_over_4m'
            }
        # Moderate risk units in Subhash Nagar
        elif loc_name == 'Subhash Nagar' and i in (1, 5, 9, 13, 17, 23, 27, 29):
            cats = {
                'exits': '2 exits',
                'obstruction': 'partially_clear',
                'emergency_exits': 'locked_or_blocked' if i % 2 == 0 else 'functional',
                'stair_width': '0_8_to_1_2m',
                'workspace': '200_to_500sqft',
                'floors': 'ground_only' if i in (1, 9, 23) else 'g_plus_1',
                'light': 'dim_partial',
                'windows': 'few_restricted' if i % 2 == 0 else 'operable_clear',
                'corridor': '1_to_1_5m',
                'waste_burning': 'none' if i in (1, 9, 27) else 'occasional_burning',
                'dust': 'low_dust' if i in (5, 17) else 'moderate_dust',
                'building_gap': 'narrow_gap_under_1m',
                'station_dist': '1_5_to_3km',
                'response_time': '15_to_25min',
                'approach_road': 'medium_2_5_to_4m'
            }
        else:
            cats = {f: sample_factor(f, bias) for f in SCORING_MAP}
            
        fri, egress, hazard, access = calc_fri(cats)
        
        inc_p = 0.35 if fri >= 0.70 else (0.15 if fri >= 0.50 else 0.04)
        incident = (random.random() < inc_p)
        
        workshops.append({
            'id': wid,
            'loc': loc_name,
            'area': area_name,
            'ent': ent_name,
            'work': work_type,
            'incident': incident,
            'lat': lat,
            'lng': lng,
            'cats': cats,
            'fri': round(fri, 4),
            'egress': round(egress, 4),
            'hazard': round(hazard, 4),
            'access': round(access, 4),
            'tier': get_tier(fri)
        })
        workshop_counter += 1

all_fri = [w['fri'] for w in workshops]
mean_fri = sum(all_fri) / len(all_fri)
tier_counts = {t: sum(1 for w in workshops if w['tier'] == t) for t in ['Severe', 'High', 'Moderate', 'Low']}
severe_pct = tier_counts['Severe'] / len(workshops) * 100

print(f"Total workshops: {len(workshops)}")
print(f"Mean FRI: {mean_fri:.4f} (Target ~0.71)")
print(f"Severe Count: {tier_counts['Severe']} ({severe_pct:.1f}% - Target ~72%)")
print(f"Tiers: {tier_counts}")
print(f"Incidents: {sum(1 for w in workshops if w['incident'])}")

for loc in ['Shanti Mohalla', 'Seelampur', 'Gandhi Nagar', 'Subhash Nagar']:
    loc_w = [w for w in workshops if w['loc'] == loc]
    loc_mean = sum(w['fri'] for w in loc_w) / len(loc_w)
    loc_sev = sum(1 for w in loc_w if w['tier'] == 'Severe')
    print(f"{loc}: count={len(loc_w)}, mean FRI={loc_mean:.4f}, severe={loc_sev} ({loc_sev/len(loc_w)*100:.1f}%)")

with open('workshops_data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'scoring_map': SCORING_MAP,
        'workshops': workshops
    }, f, indent=2)

print("Saved to workshops_data.json")
