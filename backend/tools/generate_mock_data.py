import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_synthetic_data(filename, start_year=2020, end_year=2026):
    print(f"Generating synthetic data: {filename}")
    
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()
    days = (end_date - start_date).days
    
    date_range = [start_date + timedelta(days=x) for x in range(days + 1)]
    
    data = {
        'date': date_range,
        'state': 'Tamil Nadu',
        'district': 'Dindigul',
        'market': 'Dindigul',
        'commodity': 'Onion',
        'variety': 'Red',
        'arrival_date': [d.strftime("%d/%m/%Y") for d in date_range],
        'min_price': [],
        'max_price': [],
        'modal_price': []
    }
    
    # Weather mock columns for training
    max_temps = []
    min_temps = []
    precips = []
    soil_moistures = []
    ndvis = []
    
    # Seasonality Logic for Onion Prices
    # High: Nov, Dec, Jan (Post Monsoon shortage)
    # Low: Mar, Apr, May (Rabi Harvest)
    
    base_price = 1500
    
    np.random.seed(42) # For reproducibility
    
    for d in date_range:
        month = d.month
        
        # Seasonal Multiplier
        if month in [10, 11, 12, 1]:
            season_factor = np.random.uniform(1.5, 2.5) # High season
            precip = np.random.choice([0, 0, 5, 10, 20]) # Some rain
        elif month in [3, 4, 5]:
            season_factor = np.random.uniform(0.6, 0.9) # Low season (Harvest)
            precip = 0
        else:
            season_factor = np.random.uniform(0.9, 1.2) # Normal
            precip = np.random.choice([0, 0, 0, 5])
            
        # Random daily fluctuation
        daily_noise = np.random.normal(0, 100)
        
        price = base_price * season_factor + daily_noise
        price = max(500, price) # Minimum price floor
        
        data['modal_price'].append(round(price, 2))
        data['min_price'].append(round(price * 0.9, 2))
        data['max_price'].append(round(price * 1.1, 2))
        
        # Simulated Weather
        max_temps.append(round(np.random.uniform(28, 35), 1))
        min_temps.append(round(np.random.uniform(20, 25), 1))
        precips.append(precip)
        soil_moistures.append(round(np.random.uniform(0.1, 0.4), 3))
        ndvis.append(round(np.random.uniform(0.2, 0.6), 2))
        
    df = pd.DataFrame(data)
    
    # Add weather columns directly since fusion.py expects them if cached
    df['max_temp'] = max_temps
    df['min_temp'] = min_temps
    df['precipitation'] = precips
    df['soil_moisture'] = soil_moistures
    df['ndvi'] = ndvis
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} records to {filename}")

if __name__ == "__main__":
    # Path to backend/data
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    
    # Generate for the 20k record requirement (train.py)
    generate_synthetic_data(os.path.join(data_dir, "Onion_Tamil Nadu_20000.csv"))
    
    # Generate for the 1k record requirement (test_model.py fallback)
    generate_synthetic_data(os.path.join(data_dir, "Onion_Tamil Nadu_1000.csv"))
