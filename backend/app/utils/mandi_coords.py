"""
mandi_coords.py
===============
Maps mandi/market names to (latitude, longitude).

Tamil Nadu section uses the real Agmarknet API market names
(Uzhavar Sandhai APMC format), organised district-wise.

Border mandis from Kerala, Karnataka, and Andhra Pradesh are
included because trade in onion, tomato, and potato regularly
crosses state lines at these points.
"""

MANDI_COORDS = {
    # ─────────────────────────────────────────────────────────────
    # MAHARASHTRA
    # ─────────────────────────────────────────────────────────────
    "Lasalgaon":          (20.1477, 74.2255),
    "Pinoalgaon Baswant": (20.1500, 74.0000),
    "Nashik":             (19.9975, 73.7898),
    "Pune":               (18.5204, 73.8567),
    "Mumbai":             (19.0760, 72.8777),
    "Vashi":              (19.0760, 72.8777),
    "Nagpur":             (21.1458, 79.0882),
    "Solapur":            (17.6599, 75.9064),
    "Kolhapur":           (16.7050, 74.2433),
    "Aurangabad":         (19.8762, 75.3433),
    "Ahmednagar":         (19.0952, 74.7496),
    "Rahata":             (19.6600, 74.4800),
    "Sangli":             (16.8524, 74.5815),
    "Satara":             (17.6805, 74.0183),
    "Amravati":           (20.9320, 77.7523),
    "Yeola":              (20.0440, 74.4870),
    "Manmad":             (20.2520, 74.4420),
    "Chandwad":           (20.3280, 74.2450),
    "Kalvan":             (20.4800, 73.8200),
    "Satana":             (20.5900, 74.2000),
    "Malegaon":           (20.5579, 74.5089),

    # ─────────────────────────────────────────────────────────────
    # PUNJAB
    # ─────────────────────────────────────────────────────────────
    "Ludhiana":   (30.9010, 75.8573),
    "Amritsar":   (31.6340, 74.8723),
    "Jalandhar":  (31.3260, 75.5762),
    "Patiala":    (30.3398, 76.3869),
    "Bathinda":   (30.2110, 74.9455),
    "Khanna":     (30.7070, 76.2160),
    "Moga":       (30.8230, 75.1735),
    "Firozpur":   (30.9000, 74.6000),
    "Hoshiarpur": (31.5100, 75.9100),
    "Pathankot":  (32.2600, 75.6400),
    "Sahnewal":   (30.8500, 75.9800),

    # ─────────────────────────────────────────────────────────────
    # HARYANA
    # ─────────────────────────────────────────────────────────────
    "Karnal":    (29.6857, 76.9905),
    "Panipat":   (29.3909, 76.9635),
    "Ambala":    (30.3782, 76.7767),
    "Hisar":     (29.1492, 75.7217),
    "Rohtak":    (28.8955, 76.6066),
    "Sonipat":   (28.9900, 77.0200),
    "Gurgaon":   (28.4595, 77.0266),
    "Faridabad": (28.4089, 77.3178),
    "Sirsa":     (29.5300, 75.0200),
    "Fatehabad": (29.5000, 75.4500),

    # ─────────────────────────────────────────────────────────────
    # UTTAR PRADESH
    # ─────────────────────────────────────────────────────────────
    "Lucknow":    (26.8467, 80.9462),
    "Kanpur":     (26.4499, 80.3319),
    "Agra":       (27.1767, 78.0081),
    "Varanasi":   (25.3176, 82.9739),
    "Ghaziabad":  (28.6692, 77.4538),
    "Meerut":     (28.9845, 77.7064),
    "Aligarh":    (27.8974, 78.0880),
    "Bareilly":   (28.3670, 79.4304),
    "Moradabad":  (28.8386, 78.7733),
    "Gorakhpur":  (26.7606, 83.3732),
    "Allahabad":  (25.4358, 81.8463),

    # ─────────────────────────────────────────────────────────────
    # MADHYA PRADESH
    # ─────────────────────────────────────────────────────────────
    "Indore":   (22.7196, 75.8577),
    "Bhopal":   (23.2599, 77.4126),
    "Jabalpur": (23.1815, 79.9864),
    "Gwalior":  (26.2183, 78.1828),
    "Ujjain":   (23.1765, 75.7819),
    "Sagar":    (23.8388, 78.7378),
    "Dewas":    (22.9676, 76.0534),
    "Satna":    (24.6005, 80.8322),
    "Ratlam":   (23.3315, 75.0367),

    # ─────────────────────────────────────────────────────────────
    # RAJASTHAN
    # ─────────────────────────────────────────────────────────────
    "Jaipur":   (26.9124, 75.7873),
    "Jodhpur":  (26.2389, 73.0243),
    "Kota":     (25.2138, 75.8648),
    "Bikaner":  (28.0229, 73.3119),
    "Ajmer":    (26.4499, 74.6399),
    "Udaipur":  (24.5854, 73.7125),
    "Bhilwara": (25.3407, 74.6313),
    "Alwar":    (27.5530, 76.6346),

    # ─────────────────────────────────────────────────────────────
    # GUJARAT
    # ─────────────────────────────────────────────────────────────
    "Ahmedabad":  (23.0225, 72.5714),
    "Surat":      (21.1702, 72.8311),
    "Vadodara":   (22.3072, 73.1812),
    "Rajkot":     (22.3039, 70.8022),
    "Bhavnagar":  (21.7645, 72.1519),
    "Jamnagar":   (22.4707, 70.0577),
    "Junagadh":   (21.5222, 70.4579),
    "Gandhinagar":(23.2156, 72.6369),

    # ─────────────────────────────────────────────────────────────
    # KARNATAKA
    # ─────────────────────────────────────────────────────────────
    "Bangalore":  (12.9716, 77.5946),
    "Mysore":     (12.2958, 76.6394),
    "Hubli":      (15.3647, 75.1240),
    "Mangalore":  (12.9141, 74.8560),
    "Belgaum":    (15.8497, 74.4977),
    "Gulbarga":   (17.3297, 76.8343),
    "Davangere":  (14.4644, 75.9218),
    "Bellary":    (15.1394, 76.9214),

    # ─────────────────────────────────────────────────────────────
    # ANDHRA PRADESH
    # ─────────────────────────────────────────────────────────────
    "Visakhapatnam": (17.6868, 83.2185),
    "Vijayawada":    (16.5062, 80.6480),
    "Guntur":        (16.3067, 80.4365),
    "Nellore":       (14.4426, 79.9865),
    "Kurnool":       (15.8281, 78.0373),
    "Rajahmundry":   (17.0005, 81.8040),
    "Kakinada":      (16.9891, 82.2475),
    "Tirupati":      (13.6288, 79.4192),

    # ─────────────────────────────────────────────────────────────
    # TELANGANA
    # ─────────────────────────────────────────────────────────────
    "Hyderabad":   (17.3850, 78.4867),
    "Warangal":    (17.9689, 79.5941),
    "Nizamabad":   (18.6725, 78.0941),
    "Karimnagar":  (18.4386, 79.1288),
    "Khammam":     (17.2473, 80.1514),
    "Ramagundam":  (18.7617, 79.4753),
    "Mahbubnagar": (16.7488, 78.0035),
    "Nalgonda":    (17.0577, 79.2684),

    # ─────────────────────────────────────────────────────────────
    # WEST BENGAL
    # ─────────────────────────────────────────────────────────────
    "Kolkata":   (22.5726, 88.3639),
    "Howrah":    (22.5958, 88.2636),
    "Durgapur":  (23.5204, 87.3119),
    "Asansol":   (23.6739, 86.9524),
    "Siliguri":  (26.7271, 88.3953),
    "Bardhaman": (23.2324, 87.8615),
    "Malda":     (25.0475, 88.1352),
    "Kharagpur": (22.3460, 87.2320),

    # ═════════════════════════════════════════════════════════════
    # TAMIL NADU — District-wise (Real Agmarknet API names)
    # ═════════════════════════════════════════════════════════════

    # ── Ariyalur ─────────────────────────────────────────────────
    "Ariyalur(Uzhavar Sandhai) APMC":                 (11.1400, 79.0800),

    # ── Chengalpet ───────────────────────────────────────────────
    "Madhuranthagam(Uzhavar Sandhai ) APMC":          (12.4900, 79.8700),

    # ── Coimbatore ───────────────────────────────────────────────
    "RSPuram(Uzhavar Sandhai ) APMC":                 (11.0040, 76.9553),
    "Singanallur(Uzhavar Sandhai ) APMC":             (10.9958, 77.0227),
    "Sulur(Uzhavar Sandhai ) APMC":                   (10.9976, 77.1245),
    "Vadavalli(Uzhavar Sandhai ) APMC":               (11.0383, 76.9228),
    "Mettupalayam(Uzhavar Sandhai ) APMC":            (11.2978, 76.9378),

    # ── Cuddalore ────────────────────────────────────────────────
    "Cuddalore(Uzhavar Sandhai ) APMC":               (11.7447, 79.7689),
    "Chidambaram(Uzhavar Sandhai ) APMC":             (11.3993, 79.6929),
    "Vadalur(Uzhavar Sandhai ) APMC":                 (11.5400, 79.4900),
    "Viruthachalam(Uzhavar Sandhai ) APMC":           (11.5202, 79.3144),

    # ── Dharmapuri ───────────────────────────────────────────────
    "AJattihalli(Uzhavar Sandhai ) APMC":             (12.4500, 77.9800),
    "Dharmapuri(Uzhavar Sandhai ) APMC":              (12.1277, 78.1580),
    "Harur(Uzhavar Sandhai ) APMC":                   (12.0508, 78.4770),
    "Karimangalam(Uzhavar Sandhai)":                  (12.2900, 78.3900),
    "Palacode(Uzhavar Sandhai ) APMC":                (12.2100, 78.0300),
    "Pennagaram(Uzhavar Sandhai ) APMC":              (11.9800, 77.9700),

    # ── Dindigul ─────────────────────────────────────────────────
    "Dindigul":                                       (10.3673, 77.9803),
    "Dindigul APMC":                                  (10.3673, 77.9803),
    "Palani(Uzhavar Sandhai ) APMC":                  (10.4500, 77.5200),
    "Vedasanthur(Uzhavar Sandhai ) APMC":             (10.5300, 77.9500),
    "Oddanchatram(Uzhavar Sandhai ) APMC":            (10.3400, 77.8700),

    # ── Erode ────────────────────────────────────────────────────
    "Gobichettipalayam(Uzhavar Sandhai ) APMC":       (11.4549, 77.4408),
    "Perundurai(Uzhavar Sandhai ) APMC":              (11.2725, 77.5831),
    "Periyar Nagar(Uzhavar Sandhai ) APMC":           (11.3500, 77.7800),
    "Sathiyamagalam(Uzhavar Sandhai ) APMC":          (11.5066, 77.2330),
    "Thalavadi(Uzhavar Sandhai ) APMC":               (11.6817, 77.0038),

    # ── Kallakuruchi ─────────────────────────────────────────────
    "Kallakurichi(Uzhavar Sandhai ) APMC":            (11.7380, 78.9600),
    "Sankarapuram(Uzhavar Sandhai ) APMC":            (11.8900, 79.0000),

    # ── Kancheepuram ─────────────────────────────────────────────
    "Kundrathur(Uzhavar Sandhai ) APMC":              (12.9800, 80.0900),

    # ── Karur ────────────────────────────────────────────────────
    "Gandhigramam(Uzhavar Sandhai)":                  (10.8000, 78.1000),
    "Karur(Uzhavar Sandhai ) APMC":                   (10.9601, 78.0766),
    "Kulithalai(Uzhavar Sandhai ) APMC":              (10.9200, 78.4200),
    "Pallapatti (Uzhavar Sandhai ) APMC":             (10.9900, 78.2400),
    "Velayuthampalayam(Uzhavar Sandhai ) APMC":       (11.0200, 77.8500),
    "Vengamedu(Uzhavar Sandhai ) APMC":               (10.9700, 78.0400),

    # ── Krishnagiri ──────────────────────────────────────────────
    "Avallapalli(Uzhavar Sandhai ) APMC":             (12.5900, 78.2200),
    "Denkanikottai(Uzhavar Sandhai ) APMC":           (12.4644, 77.9914),
    "Hosur(Uzhavar Sandhai ) APMC":                   (12.7409, 77.8253),
    "Krishnagiri(Uzhavar Sandhai ) APMC":             (12.5186, 78.2137),

    # ── Madurai ──────────────────────────────────────────────────
    "Madurai":                                        (9.9252,  78.1198),
    "Madurai APMC":                                   (9.9252,  78.1198),
    "Anaiyur(Uzhavar Sandhai ) APMC":                 (9.8900,  78.0700),
    "Anna nagar(Uzhavar Sandhai ) APMC":              (9.9600,  78.1400),
    "Chokkikulam(Uzhavar Sandhai ) APMC":             (9.9200,  78.1400),
    "Melur(Uzhavar Sandhai ) APMC":                   (10.0493, 78.3420),
    "Palanganatham(Uzhavar Sandhai ) APMC":           (9.8900,  78.1400),
    "Thirumangalam(Uzhavar Sandhai ) APMC":           (9.8189,  77.9874),
    "Usilampatti(Uzhavar Sandhai ) APMC":             (9.9699,  77.7958),

    # ── Nagapattinam ─────────────────────────────────────────────
    "Mayiladuthurai(Uzhavar Sandhai ) APMC":          (11.1000, 79.6500),
    "Nagapattinam(Uzhavar Sandhai ) APMC":            (10.7672, 79.8449),
    "Sirkali(Uzhavar Sandhai ) APMC":                 (11.2196, 79.7449),
    "Vedaranyam(Uzhavar Sandhai)":                    (10.3756, 79.8512),

    # ── Kanyakumari ──────────────────────────────────────────────
    "Myladi(Uzhavar Sandhai ) APMC":                  (8.2700,  77.3700),
    "Vadaseri APMC":                                  (8.1955,  77.4300),
    "Nagercoil":                                      (8.1830,  77.4119),

    # ── Namakkal ─────────────────────────────────────────────────
    "Kumarapalayam(Uzhavar Sandhai ) APMC":           (11.4450, 77.6900),
    "Mohanur(Uzhavar Sandhai ) APMC":                 (11.0500, 78.1400),
    "Paramathivelur(Uzhavar Sandhai ) APMC":          (11.0900, 78.1900),
    "Rasipuram(Uzhavar Sandhai ) APMC":               (11.4700, 78.1800),
    "Tiruchengode APMC":                              (11.3800, 77.8900),

    # ── Perambalur ───────────────────────────────────────────────
    "Perambalur(Uzhavar Sandhai ) APMC":              (11.2342, 78.8802),

    # ── Pudukkottai ──────────────────────────────────────────────
    "Alangudi(Uzhavar Sandhai ) APMC":                (10.3700, 78.9400),
    "Aranthangi(Uzhavar Sandhai ) APMC":              (10.1700, 79.0800),
    "Gandarvakottai(Uzhavar Sandhai ) APMC":          (10.5000, 78.8500),
    "Karambakkudi(Uzhavar Sandhai ) APMC":            (10.4500, 78.7700),
    "Pudukottai(Uzhavar Sandhai ) APMC":              (10.3797, 78.8203),

    # ── Ramanathapuram ───────────────────────────────────────────
    "Paramakudi(Uzhavar Sandhai ) APMC":              (9.5300,  78.5900),
    "Ramanathapuram(Uzhavar Sandhai ) APMC":          (9.3762,  78.8318),

    # ── Ranipet ──────────────────────────────────────────────────
    "Arcot(Uzhavar Sandhai ) APMC":                   (12.9000, 79.3200),
    "Ranipettai(Uzhavar Sandhai ) APMC":              (12.9278, 79.3320),

    # ── Salem ────────────────────────────────────────────────────
    "Ammapet(Uzhavar Sandhai ) APMC":                 (11.6800, 78.1600),
    "Athur(Uzhavar Sandhai ) APMC":                   (11.5800, 78.5900),
    "Edapadi (Uzhavar Sandhai ) APMC":                (11.5900, 77.8100),
    "Elampillai(Uzhavar Sandhai ) APMC":              (11.5900, 78.0300),
    "Hasthampatti(Uzhavar Sandhai ) APMC":            (11.7100, 78.1400),
    "Jalagandapuram(Uzhavar Sandhai ) APMC":          (11.5500, 77.8900),
    "Mecheri(Uzhavar Sandhai)":                       (11.7700, 78.0100),
    "Mettur(Uzhavar Sandhai ) APMC":                  (11.7890, 77.8010),
    "Thammampatti (Uzhavar Sandhai ) APMC":           (11.7700, 78.3500),
    "Thathakapatti(Uzhavar Sandhai ) APMC":           (11.8100, 78.1300),
    "Vazhapadi(Uzhavar Sandhai)":                     (11.8800, 78.5400),

    # ── Sivagangai ───────────────────────────────────────────────
    "Devakottai (Uzhavar Sandhai ) APMC":             (9.9400,  78.8200),
    "Karaikudi(Uzhavar Sandhai ) APMC":               (10.0768, 78.7814),
    "Singampunari(Uzhavar Sandhai ) APMC":            (10.2400, 78.4200),
    "Sivagangai (Uzhavar Sandhai ) APMC":             (9.8440,  78.4806),

    # ── Tenkasi ──────────────────────────────────────────────────
    "Sankarankoil(Uzhavar Sandhai ) APMC":            (9.1700,  77.5500),

    # ── Thanjavur ────────────────────────────────────────────────
    "Pattukottai(Uzhavar Sandhai ) APMC":             (10.4300, 79.3200),
    "Thanjavur(Uzhavar Sandhai ) APMC":               (10.7870, 79.1378),

    # ── The Nilgiris ─────────────────────────────────────────────
    "Gudalur(Uzhavar Sandhai ) APMC":                 (11.4990, 76.4940),
    "Udhagamandalam(Uzhavar Sandhai ) APMC":          (11.4102, 76.6950),

    # ── Theni ────────────────────────────────────────────────────
    "Andipatti(Uzhavar Sandhai ) APMC":               (10.0000, 77.6200),
    "Chinnamanur(Uzhavar Sandhai ) APMC":             (9.8600,  77.4400),
    "Devaram(Uzhavar Sandhai ) APMC":                 (9.9100,  77.5500),
    "Kambam(Uzhavar Sandhai ) APMC":                  (9.7400,  77.2800),
    "Periyakulam(Uzhavar Sandhai ) APMC":             (10.1175, 77.5440),
    "Theni(Uzhavar Sandhai ) APMC":                   (10.0102, 77.4767),

    # ── Thiruchirappalli ─────────────────────────────────────────
    "Manachanallur(Uzhavar Sandhai ) APMC":           (10.8750, 78.8620),
    "Musiri(Uzhavar Sandhai ) APMC":                  (10.9430, 78.4500),
    "Thiruverumbur(Uzhavar Sandhai ) APMC":           (10.8300, 78.7600),

    # ── Tirunelveli (Thirunelveli) ───────────────────────────────
    "Tirunelveli":                                    (8.7139,  77.7567),
    "Tirunelveli APMC":                               (8.7139,  77.7567),
    "Kandiyaperi(Uzhavar Sandhai ) APMC":             (8.6500,  77.7100),
    "Melapalayam(Uzhavar Sandhai ) APMC":             (8.7200,  77.6800),
    "Palayamkottai(Uzhavar Sandhai ) APMC":           (8.7310,  77.7352),

    # ── Thirupathur ──────────────────────────────────────────────
    "Natrampalli(Uzhavar Sandhai ) APMC":             (12.6400, 78.5900),
    "Thirupathur APMC":                               (12.4960, 78.5700),

    # ── Tiruppur ─────────────────────────────────────────────────
    "Dharapuram(Uzhavar Sandhai ) APMC":              (10.7316, 77.5104),
    "Kangayam(Uzhavar Sandhai ) APMC":                (10.9600, 77.5600),
    "Palladam(Uzhavar Sandhai ) APMC":                (10.9893, 77.2810),
    "Tiruppur (South) (Uzhavar Sandhai ) APMC":       (11.0891, 77.3476),

    # ── Thiruvannamalai ──────────────────────────────────────────
    "Arani(Uzhavar Sandhai ) APMC":                   (12.6700, 79.2800),
    "Chengam(Uzhavar Sandhai ) APMC":                 (12.3200, 78.7700),
    "Cheyyar(Uzhavar Sandhai ) APMC":                 (12.6700, 79.5400),
    "Keelpennathur(Uzhavar Sandhai ) APMC":           (12.5200, 79.1200),
    "Polur(Uzhavar Sandhai ) APMC":                   (12.5200, 79.1300),
    "Tamarainagar(Uzhavar Sandhai ) APMC":            (12.2900, 79.0900),
    "Tiruvannamalai(Uzhavar Sandhai ) APMC":          (12.2253, 79.0747),
    "Vandavasi(Uzhavar Sandhai ) APMC":               (12.5100, 79.6200),

    # ── Thiruvarur ───────────────────────────────────────────────
    "Mannargudi I(Uzhavar Sandhai ) APMC":            (10.6671, 79.4507),
    "Needamangalam(Uzhavar Sandhai ) APMC":           (10.7900, 79.4600),
    "Tiruthuraipoondi(Uzhavar Sandhai ) APMC":        (10.5300, 79.6300),

    # ── Tuticorin / Thoothukudi ───────────────────────────────────
    "Kovilpatti(Uzhavar Sandhai ) APMC":              (9.1735,  77.8631),
    "Tuticorin(Uzhavar Sandhai ) APMC":               (8.7642,  78.1348),

    # ── Vellore ──────────────────────────────────────────────────
    "Gudiyatham(Uzhavar Sandhai ) APMC":              (12.9380, 78.8745),
    "Kahithapattarai(Uzhavar Sandhai ) APMC":         (12.5800, 79.0600),
    "Pallikonda(Uzhavar Sandhai)":                    (12.9200, 78.9400),
    "Perampet(Uzhavar Sandhai)":                      (12.9700, 79.1800),

    # ── Villupuram ───────────────────────────────────────────────
    "Gingee(Uzhavar Sandhai ) APMC":                  (12.2530, 79.4170),
    "Tindivanam APMC":                                (12.2400, 79.6500),
    "Ulundurpettai APMC":                             (11.6800, 79.3100),
    "Villupuram(Uzhavar Sandhai ) APMC":              (11.9400, 79.4900),

    # ── Virudhunagar ─────────────────────────────────────────────
    "Virudhunagar":                                   (9.5872,  77.9546),
    "Virudhunagar APMC":                              (9.5872,  77.9546),
    "Viruthunagar":                                   (9.5872,  77.9546),
    "Aruppukottai(Uzhavar Sandhai ) APMC":            (9.5100,  78.0900),
    "Kariyapatti(Uzhavar Sandhai ) APMC":             (9.6500,  77.9700),
    "Rajapalayam(Uzhavar Sandhai ) APMC":             (9.4524,  77.5523),
    "Sathur(Uzhavar Sandhai ) APMC":                  (9.3500,  77.9000),
    "Sivakasi(Uzhavar Sandhai ) APMC":                (9.4532,  77.7985),
    "Srivilliputhur(Uzhavar Sandhai ) APMC":          (9.5100,  77.6300),
    "Thalavaipuram(Uzhavar Sandhai ) APMC":           (9.2800,  77.7700),

    # ═════════════════════════════════════════════════════════════
    # BORDER MANDIS — Kerala (TN ↔ KL trade routes)
    # ═════════════════════════════════════════════════════════════
    # Palakkad Gap corridor (biggest TN↔KL onion/veg route)
    "Pollachi":             (10.6545, 77.0073),  # TN — gateway to Palakkad
    "Palakkad":             (10.7867, 76.6548),  # KL — Palakkad town market
    "Ottapalam":            (10.7668, 76.3775),  # KL side, receives from Palakkad
    "Thrissur":             (10.5276, 76.2144),  # KL wholesale hub
    "Ernakulam":            (9.9312,  76.2673),  # Kochi — major KL distribution
    # Gudalur / Nilgiris corridor
    "Mananthavady":         (11.8020, 76.0050),  # KL border, Wayanad
    "Sultan Bathery":       (11.6600, 76.2500),  # Wayanad — receives from Nilgiris
    # Southern TN→KL
    "Thiruvananthapuram":   (8.5241,  77.9382),  # TVM — receives from Virudhunagar
    "Kollam":               (8.8932,  76.6141),  # KL — Tirunelveli belt
    "Kottayam":             (9.5916,  76.5222),  # KL interior
    # Coimbatore corridor
    "Palakkad Jn":          (10.7770, 76.6500),  # Major rail/road crossover

    # ═════════════════════════════════════════════════════════════
    # BORDER MANDIS — Karnataka (TN ↔ KA trade routes)
    # ═════════════════════════════════════════════════════════════
    # Salem / Dharmapuri → KA
    "Chamarajnagar":        (11.9200, 76.9400),  # KA, near Dharmapuri/Erode border
    "Kollegal":             (12.1514, 77.1118),  # KA, borders Erode/Dharmapuri
    "Yelandur":             (12.0500, 77.0400),  # KA, Chamarajnagar belt
    # Nilgiris / Gudalur → KA
    "Gundlupet":            (11.8073, 76.6882),  # KA, borders Nilgiris
    "Bandipur":             (11.6640, 76.6340),  # KA, wildlife corridor trade town
    # Krishnagiri / Hosur → Bangalore
    "Anekal":               (12.7100, 77.6900),  # KA, Bangalore border
    "Electronic City":      (12.8392, 77.6762),  # KA, Bangalore south

    # ═════════════════════════════════════════════════════════════
    # BORDER MANDIS — Andhra Pradesh (TN ↔ AP trade routes)
    # ═════════════════════════════════════════════════════════════
    # Vellore / Tirupattur → AP
    "Chittoor":             (13.2172, 79.1003),  # AP, borders Vellore
    "Puttur":               (13.4400, 79.5500),  # AP, borders Tirupattur
    "Gudupalli":            (13.9800, 79.6100),  # AP, Chittoor belt
    # Coastal / Nellore belt
    "Kavali":               (14.9100, 79.9900),  # AP coast, near Nellore
}
