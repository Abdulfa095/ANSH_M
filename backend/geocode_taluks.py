"""
Geocodes every taluk in TNTaluks.ts that has placeholder or fallback coordinates
using the Nominatim API, then rewrites the file with real coordinates.
Rate-limited to 1 req/s to respect OSM ToS.
"""
import re
import time
import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

TS_FILE = '../frontend/components/TNTaluks.ts'

ALIASES = {
    "Purasavakkam": "Purasaiwakkam",
    "Aanaimalai": "Anaimalai",
    "Madukarai": "Madukkarai",
    "Atthur": "Authoor",
    "Dindigul (East)": "Dindigul",
    "Dindigul (West)": "Dindigul",
    "Guziliyamparai": "Gujiliyamparai",
    "Modakurichi": "Modakkurichi",
    "Kundrathur": "Kundrathur",
    "Thiruvatar": "Thiruvattar",
    "Vilavankodu": "Vilavancode",
    "Kholli Hills": "Kolli Hills",
    "Mohanoor": "Mohanur",
    "Senthamangalam": "Sendamangalam",
    "Avudiyarkoil": "Avadaiyarkoil",
    "Kezhakarai": "Kilakarai",
    "Rajasingamangalam": "R.S. Mangalam",
    "Kadaiyampatti": "Kadayampatti",
    "Pethanayakanpalayam": "Pethanaickenpalayam",
    "Thirupuvanam": "Thiruppuvanam",
    "Tirupathur": "Thiruppathur",
    "Boothalur": "Budalur",
    "Aandipatti": "Andipatti",
    "Chetpet": "Chetpet",
    "Thandramet": "Thandarampattu",
    "Sattankulam": "Sathankulam",
    "Thottiam": "Thottiyam",
    "Tiruchirapalli (West)": "Tiruchirappalli",
    "Aanikattu": "Anaicut",
    "Marakanam": "Marakkanam",
    "Udaiyarpalayam": "Udayarpalayam",
    "Anjetty": "Anchetti",
    "Madathukkulam": "Madathukulam",
    "Oothukuli": "Uthukuli",
    "Chinnaselam": "Chinnasalem",
    "Kalvarayan Hills": "Kalvarayan Hills",
    "Sholingur": "Sholinghur"
}

def clean_name(taluk_name):
    # Condense multiple spaces to single
    cleaned = re.sub(r'\s+', ' ', taluk_name).strip()
    return ALIASES.get(cleaned, cleaned)

def geocode(query: str):
    url = f'https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1'
    req = urllib.request.Request(url, headers={'User-Agent': 'ANSH-M-FYP/1.1'})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=8)
        data = json.loads(resp.read())
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f'  ERROR: {e}')
    return None, None

with open(TS_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# 1. Build district fallbacks from the file
district_coords = {}
in_district_fallback = False
for line in lines:
    if 'TN_DISTRICT_COORDS' in line:
        in_district_fallback = True
    elif in_district_fallback and 'lat:' in line:
        m = re.search(r'"([^"]+)":\s*\{\s*lat:\s*([0-9\.]+),\s*lon:\s*([0-9\.]+)\s*\}', line)
        if m:
            district_coords[m.group(1)] = (m.group(2), m.group(3))

# 2. Find missing taluks and geocode
current_district = None
replacements = {}  # (taluk_name, district_name) -> (new_lat, new_lon)

for line in lines:
    dist_match = re.search(r'\s+"([^"]+)":\s*\{', line)
    if dist_match and 'lat:' not in line:
        current_district = dist_match.group(1)

    if current_district and 'lat:' in line:
        taluk_match = re.search(r'"([^"]+)":\s*\{\s*lat:\s*([0-9\.]+),\s*lon:\s*([0-9\.]+)\s*\}', line)
        if taluk_match:
            taluk = taluk_match.group(1)
            lat_str = taluk_match.group(2)
            lon_str = taluk_match.group(3)
            
            # Identify placeholders
            is_placeholder = (lat_str == '10.82' and lon_str == '78.68') or \
                             (lat_str == '0' and lon_str == '0')
            
            dist_c = district_coords.get(current_district)
            is_fallback = False
            if dist_c and lat_str == dist_c[0] and lon_str == dist_c[1]:
                is_fallback = True

            if is_placeholder or is_fallback:
                clean_taluk = clean_name(taluk)
                
                # Try geocoding with district
                query1 = f'{clean_taluk}, {current_district}, Tamil Nadu, India'
                print(f'Geocoding: {taluk} -> {query1}')
                lat, lon = geocode(query1)
                time.sleep(1.2)
                
                # Try without district if not found
                if not lat:
                    query2 = f'{clean_taluk}, Tamil Nadu, India'
                    print(f'  Retrying: {query2}')
                    lat, lon = geocode(query2)
                    time.sleep(1.2)
                
                if lat:
                    replacements[(taluk, current_district)] = (round(lat, 4), round(lon, 4))
                    print(f'  -> Found: ({lat:.4f}, {lon:.4f})')
                else:
                    print(f'  -> NOT FOUND, keeping fallback')

print(f'\nFetched {len(replacements)} new coordinates. Updating file...')

# 3. Update file
new_lines = []
current_district = None
for line in lines:
    dist_match = re.search(r'\s+"([^"]+)":\s*\{', line)
    if dist_match and 'lat:' not in line:
        current_district = dist_match.group(1)

    if current_district and 'lat:' in line:
        taluk_match = re.search(r'"([^"]+)":\s*\{\s*lat:\s*([0-9\.]+),\s*lon:\s*([0-9\.]+)\s*\}', line)
        if taluk_match:
            taluk = taluk_match.group(1)
            if (taluk, current_district) in replacements:
                lat, lon = replacements[(taluk, current_district)]
                line = re.sub(
                    r'lat:\s*[0-9\.]+,\s*lon:\s*[0-9\.]+',
                    f'lat: {lat}, lon: {lon}',
                    line
                )
    new_lines.append(line)

with open(TS_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print('Done! TNTaluks.ts has been updated with real coordinates.')
