import json

ta_additions = {
"Madhuranthagam": "மதுராந்தகம்",
"RSPuram": "ஆர்.எஸ். புரம்",
"Singanallur": "சிங்காநல்லூர்",
"Vadavalli": "வடவள்ளி",
"Vadalur": "வடலூர்",
"Viruthachalam": "விருத்தாசலம்",
"AJattihalli": "எ.ஜட்டிஅள்ளி",
"Vedasanthur": "வேடசந்தூர்",
"Periyar_Nagar": "பெரியார் நகர்",
"Sathiyamagalam": "சத்தியமங்கலம்",
"Gandhigramam": "காந்திகிராமம்",
"Pallapatti": "பள்ளப்பட்டி",
"Velayuthampalayam": "வேலாயுதம்பாளையம்",
"Vengamedu": "வெங்கமேடு",
"Avallapalli": "அவல்லப்பள்ளி",
"Denkanikottai": "தேன்கனிக்கோட்டை",
"Anaiyur": "ஆனையூர்",
"Anna_nagar": "அண்ணா நகர்",
"Chokkikulam": "சொக்கிகுளம்",
"Palanganatham": "பழங்காநத்தம்",
"Myladi": "மயிலாடி",
"Vadaseri": "வடசேரி",
"Nagercoil": "நாகர்கோவில்",
"Mohanur": "மோகனூர்",
"Paramathivelur": "பரமத்திவேலூர்",
"Karambakkudi": "கறம்பக்குடி",
"Ranipettai": "இராணிப்பேட்டை",
"Ammapet": "அம்மாபேட்டை",
"Athur": "ஆத்தூர்",
"Elampillai": "இளம்பிள்ளை",
"Hasthampatti": "அஸ்தம்பட்டி",
"Jalagandapuram": "ஜலகண்டாபுரம்",
"Mecheri": "மேச்சேரி",
"Thammampatti": "தம்மம்பட்டி",
"Thathakapatti": "தாதகாபட்டி",
"Sankarankoil": "சங்கரன்கோவில்",
"Udhagamandalam": "உதகமண்டலம்",
"Andipatti": "ஆண்டிப்பட்டி",
"Chinnamanur": "சின்னமனூர்",
"Devaram": "தேவாரம்",
"Kambam": "கம்பம்",
"Thiruverumbur": "திருவெறும்பூர்",
"Kandiyaperi": "கண்டியபேரி",
"Melapalayam": "மேலப்பாளையம்",
"Thirupathur": "திருப்பத்தூர்",
"Kangayam": "காங்கேயம்",
"Tiruppur_South": "திருப்பூர் தெற்கு",
"Arani": "ஆரணி",
"Keelpennathur": "கீழ்பெண்ணாத்தூர்",
"Tamarainagar": "தாமரைநகர்",
"Tiruvannamalai": "திருவண்ணாமலை",
"Mannargudi_I": "மன்னார்குடி I",
"Tiruthuraipoondi": "திருத்துறைப்பூண்டி",
"Tuticorin": "தூத்துக்குடி",
"Kahithapattarai": "காகிதப்பட்டறை",
"Pallikonda": "பள்ளிகொண்டா",
"Perampet": "பேரம்பட்டு",
"Ulundurpettai": "உளுந்தூர்பேட்டை",
"Viruthunagar": "விருதுநகர்",
"Thalavaipuram": "தளவாய்புரம்"
}

en_additions = { k: k.replace('_', ' ') for k in ta_additions.keys() }

with open('frontend/messages/ta.json', 'r', encoding='utf-8') as f:
    ta = json.load(f)

if 'mandis' not in ta['MandiFinder']:
    ta['MandiFinder']['mandis'] = {}

for k, v in ta_additions.items():
    ta['MandiFinder']['mandis'][k] = v

with open('frontend/messages/ta.json', 'w', encoding='utf-8') as f:
    json.dump(ta, f, indent=2, ensure_ascii=False)


with open('frontend/messages/en.json', 'r', encoding='utf-8') as f:
    en = json.load(f)

if 'mandis' not in en['MandiFinder']:
    en['MandiFinder']['mandis'] = {}

for k, v in en_additions.items():
    en['MandiFinder']['mandis'][k] = v

with open('frontend/messages/en.json', 'w', encoding='utf-8') as f:
    json.dump(en, f, indent=2, ensure_ascii=False)

print("Updated translation JSON files successfully!")
