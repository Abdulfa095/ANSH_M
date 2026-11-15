from app.engine.profit_optimizer import ProfitOptimizer
import json

def test_thiruchuli_routing():
    optimizer = ProfitOptimizer()
    
    # 1. Farmer Location: Thiruchuli, Virudhunagar district
    farmer_loc = (9.5398, 78.2046) 
    quantity = 10 # 10 Quintals = 1 Tonne
    
    # 2. Candidate Mandis
    # Let's test Tirumangalam (nearby), Madurai Central (mid), and Virudhunagar local market
    candidates = [
        {
            'name': 'Virudhunagar Market (Local)', 
            'price': 3100, # Lower price but very close
            'state': 'Tamil Nadu', 
            'lat': 9.5847, 
            'lon': 77.9620
        },
        {
            'name': 'Tirumangalam Sandhai', 
            'price': 3250, # Mid distance, mid price
            'state': 'Tamil Nadu', 
            'lat': 9.8252, 
            'lon': 77.9897
        },
        {
            'name': 'Madurai Central Mandi (Mattuthavani)', 
            'price': 3300, # Higher price, furthest away
            'state': 'Tamil Nadu', 
            'lat': 9.9391, 
            'lon': 78.1568
        }
    ]
    
    print("--- 🧅 Profit Optimization for Thiruchuli Farmer ---")
    print(f"Location: Thiruchuli, Virudhunagar")
    print(f"Produce: Onion, {quantity} Quintals (1 Tonne)")
    print(f"Searching {len(candidates)} nearby mandis...\n")
    
    # Run optimizer
    ranking = optimizer.recommend_mandi(farmer_loc[0], farmer_loc[1], quantity, candidates, diesel_price=93.0)
    
    print(json.dumps(ranking, indent=2))

if __name__ == "__main__":
    test_thiruchuli_routing()
