import urllib.request
import json
import time

taluks = [
    'Kallikudi', 'Madurai (East)', 'Madurai (North)', 'Madurai (South)',
    'Madurai (West)', 'Melur', 'Peraiyur', 'Thirumangalam',
    'Thiruparankundram', 'Usilampatti', 'Vadipatti'
]

result = []
for t in taluks:
    search_query = t.replace(' (Fast)', '').replace(' (North)', '').replace(' (South)', '').replace(' (West)', '').replace(' (East)', '')
    search_query = search_query.replace(' ', '+').replace('(', '').replace(')', '')
    url = f"https://nominatim.openstreetmap.org/search?q={search_query},+Madurai,+Tamil+Nadu,+India&format=json&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        if data:
            lat = round(float(data[0]['lat']), 4)
            lon = round(float(data[0]['lon']), 4)
            result.append(f'        "{t}": {{ lat: {lat}, lon: {lon} }},')
        else:
            result.append(f'        "{t}": {{ lat: 0, lon: 0 }},')
    except Exception as e:
        result.append(f'        "{t}": {{ lat: 0, lon: 0 }},')
    time.sleep(1)

with open('madurai_taluks.txt', 'w') as f:
    f.write('\n'.join(result))
