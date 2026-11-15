import json
import re

with open('app/utils/mandi_coords.py', 'r', encoding='utf-8') as f:
    text = f.read()

with open('../frontend/messages/ta.json', 'r', encoding='utf-8') as f:
    ta = json.load(f)

taluks = ta['MandiFinder']['taluks']
districts = ta['MandiFinder']['districts']
mandis = ta['MandiFinder'].get('mandis', {})

lines = text.split('\n')
tn_start = False
tn_mandis = []

for line in lines:
    if 'TAMIL NADU' in line:
        tn_start = True
    if 'BORDER MANDIS' in line:
        tn_start = False
    
    if tn_start and ':' in line and '"' in line:
        m_name = line.split('"')[1]
        tn_mandis.append(m_name)

missing = []

for m in tn_mandis:
    prefix = m
    l_m = m.lower()
    if 'uzhavar' in l_m:
        prefix = re.split(r'\s*\(?uzhavar', m, flags=re.I)[0].strip()
    elif l_m.endswith('apmc'):
        prefix = re.sub(r'\s*apmc$', '', m, flags=re.I).strip()
    
    prefix = prefix.replace('(', '').replace(')', '').strip()
    k = prefix.replace(' ', '_').replace('.', '')
    
    if k not in taluks and k not in districts and k not in mandis:
        missing.append((m, prefix, k))

for m in missing:
    print(f'"{m[2]}": "{m[1]}",')
