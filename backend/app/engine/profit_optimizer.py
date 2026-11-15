from .osrm_client import OSRMClient
from .tax_graph import TaxKnowledgeGraph

class ProfitOptimizer:
    """
    Mandi-Connect Recommendation Engine.
    Calculates Realized Net Profit (RNP).
    """
    def __init__(self):
        self.osrm = OSRMClient()
        self.tax_engine = TaxKnowledgeGraph()
        
    def calculate_transport_cost(self, distance_km, load_tonnes, diesel_price=90.0):
        """
        Calculate transport cost based on vehicle type and distance.
        Formula: (2 * distance * Rate) + Tolls (ignored for now)
        Round trip assumed.
        """
        # Vehicle selection logic
        if load_tonnes < 1.5:
            vehicle = "Small (Tata Ace)"
            rate_per_km = 20 # Avg
        elif load_tonnes < 7:
            vehicle = "Medium (Eicher)"
            rate_per_km = 35
        else:
            vehicle = "Heavy Truck"
            rate_per_km = 50
            
        # Adjust rate by Diesel Price factor (simplified)
        # Base rate assumed at roughly 90 Rs/L. 
        # rate_per_km = base_rate * (diesel_price / 90)
        adjusted_rate = rate_per_km * (diesel_price / 90.0)
        
        total_cost = 2 * distance_km * adjusted_rate
        return total_cost, vehicle

    def recommend_mandi(self, farmer_lat, farmer_lon, quantity_quintals, candidate_mandis, diesel_price=90.0):
        """
        Rank mandis by Net Profit.
        
        Args:
            farmer_lat, farmer_lon: Farmer's location.
            quantity_quintals: Produce quantity.
            candidate_mandis: List of dicts [{'name': 'Mandi A', 'price': 2000, 'state': 'Punjab', 'lat': ..., 'lon': ...}]
            diesel_price (float): Current diesel price per liter.
            
        Returns:
            list: Ranked mandis with detailed cost breakdown.
        """
        load_tonnes = quantity_quintals / 10.0 # 10 Quintal = 1 Tonne
        ranked_mandis = []
        
        import time
        for mandi in candidate_mandis:
            # 1. Get Distance
            route = self.osrm.get_route(farmer_lat, farmer_lon, mandi['lat'], mandi['lon'])
            if not route:
                continue
                
            dist = route['distance_km']
            time.sleep(0.1)  # Respect public OSRM API rate limit
            
            # 2. Calculate Gross Value
            gross_value = mandi['price'] * quantity_quintals
            
            # 3. Calculate Transport Cost
            transport_cost, vehicle = self.calculate_transport_cost(dist, load_tonnes, diesel_price)
            
            # 4. Calculate Taxes
            taxes = self.tax_engine.calculate_taxes(mandi['state'], gross_value)
            tax_amount = taxes['total_tax']
            
            # 5. Labor Cost (Approx 20 Rs/qtl)
            labor_cost = 20 * quantity_quintals
            
            # 6. Net Profit
            net_profit = gross_value - transport_cost - tax_amount - labor_cost
            
            ranked_mandis.append({
                "mandi": mandi['name'],
                "net_profit": round(net_profit, 2),
                "gross_value": gross_value,
                "distance_km": dist,
                "transport_cost": round(transport_cost, 2),
                "tax_amount": round(tax_amount, 2),
                "labor_cost": labor_cost,
                "price_per_qtl": mandi['price'],
                "lat": mandi['lat'],
                "lon": mandi['lon'],
                "vehicle": vehicle,
                "retail_price": mandi.get('retail_price', 0.0),
                "trader_margin": mandi.get('trader_margin', 0.0),
                "is_predicted": mandi.get('is_predicted', False),
                "last_updated": mandi.get('last_updated', "")
            })
            
        # Sort by Net Profit descending
        ranked_mandis.sort(key=lambda x: x['net_profit'], reverse=True)
        return ranked_mandis

if __name__ == "__main__":
    optimizer = ProfitOptimizer()
    
    # Example scenario
    farmer_loc = (30.900, 75.857) # Ludhiana
    candidates = [
        {'name': 'Mandi A (Punjab)', 'price': 2500, 'state': 'Punjab', 'lat': 30.95, 'lon': 75.90},
        {'name': 'Mandi B (Haryana)', 'price': 2600, 'state': 'Haryana', 'lat': 29.95, 'lon': 76.80} # Further away
    ]
    
    print("--- Scenario 1: Diesel @ 90 Rs/L ---")
    ranking_90 = optimizer.recommend_mandi(farmer_loc[0], farmer_loc[1], 50, candidates, diesel_price=90.0)
    import json
    print(json.dumps(ranking_90, indent=2))
    
    print("\n--- Scenario 2: Diesel @ 100 Rs/L (High Fuel Cost) ---")
    ranking_100 = optimizer.recommend_mandi(farmer_loc[0], farmer_loc[1], 50, candidates, diesel_price=100.0)
    print(json.dumps(ranking_100, indent=2))

    # Clarification for user
    cost_diff = ranking_100[0]['transport_cost'] - ranking_90[0]['transport_cost']
    print(f"\nImpact of 10 Rs Diesel Hike: Transport Cost increased by Rs {cost_diff:.2f}")
