import urllib.request
import json
import time

districts = [
    'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri',
    'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram', 'Kanyakumari', 'Karur',
    'Krishnagiri', 'Madura', 'Mayiladuthurai', 'Nagapattinam', 'Namakkal',
    'Nilgiris', 'Perambalur', 'Pudukkottai', 'Ramanathapuram', 'Ranipet', 'Salem',
    'Sivaganga', 'Tenkasi', 'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli',
    'Tirunelveli', 'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai',
    'Tiruvarur', 'Vellore', 'Viluppuram', 'Virudhunagar'
]

result = []
for d in districts:
    search_query = 'Madurai' if d == 'Madura' else d # fix typo
    url = f"https://nominatim.openstreetmap.org/search?q={search_query},+Tamil+Nadu,+India&format=json&limit=1"
    url = url.replace(' ', '+')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        if data:
            lat = round(float(data[0]['lat']), 4)
            lon = round(float(data[0]['lon']), 4)
            result.append(f'        "{search_query}": {{ lat: {lat}, lon: {lon} }},')
        else:
            result.append(f'        "{search_query}": {{ lat: 0, lon: 0 }},')
    except Exception as e:
        result.append(f'        "{search_query}": {{ lat: 0, lon: 0 }},')
    time.sleep(1) # rate limit

with open("tn_coords.txt", "w") as f:
    f.write("\n".join(result))
print("Done!")
