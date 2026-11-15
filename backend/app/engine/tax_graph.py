class TaxKnowledgeGraph:
    """
    Tax Labyrinth Knowledge Graph.
    Stores state-wise APMC tax structures.
    """
    
    # Tax Rules (Percentage of Gross Value)
    TAX_RULES = {
        # NORTH INDIA
        "Punjab": {
            "market_fee": 0.02, # 2%
            "development_cess": 0.02, # Reduced from 3% in some recent updates
            "commission": 0.025 # 2.5% (Arhatia)
        },
        "Haryana": {
            "market_fee": 0.02,
            "development_cess": 0.01,
            "commission": 0.025
        },
        "Uttar Pradesh": {
            "market_fee": 0.015, # 1.5%
            "development_cess": 0.005, # 0.5%
            "commission": 0.015
        },
        "Uttarakhand": {
            "market_fee": 0.015,
            "development_cess": 0.005,
            "commission": 0.015
        },
        "Himachal Pradesh": {
            "market_fee": 0.01,
            "commission": 0.02
        },
        "Jammu and Kashmir": {
            "market_fee": 0.00, # Often exempted for fruit/veg or specific rates
            "commission": 0.02
        },
        "Delhi": {
            "market_fee": 0.01,
            "commission": 0.06 # Fruit/Veg often higher commission in Azadpur
        },
        "Rajasthan": {
            "market_fee": 0.016, 
            "development_cess": 0.00, # Varies
            "commission": 0.02
        },

        # WEST INDIA
        "Maharashtra": {
            "market_fee": 0.0105, # 1.05%
            "commission": 0.04 # Can go up to 6% for fruits
        },
        "Gujarat": {
            "market_fee": 0.005, # 0.5% to 1%
            "commission": 0.015
        },
        "Goa": {
            "market_fee": 0.01,
            "commission": 0.02
        },

        # CENTRAL INDIA
        "Madhya Pradesh": {
            "market_fee": 0.015, # 1.5%
            "development_cess": 0.002, # 0.2%
            "commission": 0.02
        },
        "Chhattisgarh": {
            "market_fee": 0.02,
            "commission": 0.025
        },

        # SOUTH INDIA
        "Karnataka": {
             "market_fee": 0.015,
             "commission": 0.02
        },
        "Tamil Nadu": {
            "market_fee": 0.01, # 1% (Paid by traders)
            "commission": 0.00 # No commission agent system in many TN markets
        },
        "Andhra Pradesh": {
            "market_fee": 0.01,
            "commission": 0.02
        },
        "Telangana": {
            "market_fee": 0.01,
            "commission": 0.02
        },
        "Kerala": {
            "market_fee": 0.00, # No APMC Act
            "commission": 0.07 # High trade margins/unregulated commission
        },

        # EAST INDIA
        "West Bengal": {
            "market_fee": 0.01, # Levied on purchase
            "commission": 0.00
        },
        "Odisha": {
            "market_fee": 0.02,
            "commission": 0.02
        },
        "Bihar": {
            "market_fee": 0.01, # APMC Repealed, but 1% market fee reintroduced in 2024 via distinct rule
            "commission": 0.02
        },
        "Jharkhand": {
            "market_fee": 0.02,
            "commission": 0.02
        },

        # NORTH EAST INDIA
        "Assam": { "market_fee": 0.01, "commission": 0.02 },
        "Arunachal Pradesh": { "market_fee": 0.01, "commission": 0.00 },
        "Manipur": { "market_fee": 0.01, "commission": 0.00 },
        "Meghalaya": { "market_fee": 0.00, "commission": 0.00 }, # Exempt
        "Mizoram": { "market_fee": 0.01, "commission": 0.00 },
        "Nagaland": { "market_fee": 0.01, "commission": 0.00 },
        "Sikkim": { "market_fee": 0.01, "commission": 0.00 },
        "Tripura": { "market_fee": 0.01, "commission": 0.00 },
        
        # UTs
        "Chandigarh": { "market_fee": 0.02, "commission": 0.025 },
        "Puducherry": { "market_fee": 0.01, "commission": 0.00 }
    }
    
    def calculate_taxes(self, state, gross_value, direct_marketing=False):
        """
        Calculate total tax deductions.
        
        Args:
            state (str): State name.
            gross_value (float): Total value of produce (Price * Qty).
            direct_marketing (bool): If true, some taxes might be waived (State dependent).
        
        Returns:
            dict: Breakdown of taxes and Total Tax Amount.
        """
        rules = self.TAX_RULES.get(state, {})
        if not rules:
            # Default fallback if state not found
            return {"total_tax": 0.0, "breakdown": {}}
            
        total_tax = 0.0
        breakdown = {}
        
        # Logic for Direct Marketing exemptions (Simplified)
        if direct_marketing and state in ["Maharashtra", "Uttar Pradesh"]:
             return {"total_tax": 0.0, "breakdown": {"exemption": "Direct Marketing applied"}}

        for tax_head, rate in rules.items():
            amount = gross_value * rate
            breakdown[tax_head] = amount
            total_tax += amount
            
        return {
            "total_tax": total_tax,
            "breakdown": breakdown
        }

if __name__ == "__main__":
    tkg = TaxKnowledgeGraph()
    test_states = ["Punjab", "Tamil Nadu", "Maharashtra", "West Bengal", "Bihar"]
    gross_val = 100000 # 1 Lakh
    
    print(f"--- Tax Calculation for Gross Value: ₹{gross_val} ---")
    for state in test_states:
        taxes = tkg.calculate_taxes(state, gross_val)
        print(f"\nState: {state}")
        print(f"Total Tax: ₹{taxes['total_tax']:.2f}")
        print(f"Breakdown: {taxes['breakdown']}")
