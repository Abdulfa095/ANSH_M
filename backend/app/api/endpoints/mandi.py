from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import math
import pandas as pd
from datetime import datetime
from ...engine.profit_optimizer import ProfitOptimizer
from ...ingestion.agmarknet import AgmarknetClient
from ...ingestion.retail import RetailPriceClient
from ...utils.mandi_coords import MANDI_COORDS

router = APIRouter()

# Helper: Fast geospatial distance for pre-filtering (avoid hitting OSRM 1000s of times)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Helper: Cross-border search states
NEIGHBORING_STATES = {
    "Tamil Nadu": ["Kerala", "Karnataka", "Andhra Pradesh", "Puducherry"],
    "Kerala": ["Tamil Nadu", "Karnataka"],
    "Karnataka": ["Maharashtra", "Goa", "Kerala", "Tamil Nadu", "Andhra Pradesh", "Telangana"],
    "Andhra Pradesh": ["Tamil Nadu", "Karnataka", "Telangana", "Odisha", "Chhattisgarh"],
    "Telangana": ["Andhra Pradesh", "Karnataka", "Maharashtra", "Chhattisgarh"],
    "Maharashtra": ["Gujarat", "Madhya Pradesh", "Chhattisgarh", "Telangana", "Karnataka", "Goa"],
    "Gujarat": ["Rajasthan", "Madhya Pradesh", "Maharashtra"],
    "Rajasthan": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Gujarat"],
    "Punjab": ["Jammu and Kashmir", "Himachal Pradesh", "Haryana", "Rajasthan", "Chandigarh"],
    "Haryana": ["Punjab", "Himachal Pradesh", "Uttarakhand", "Uttar Pradesh", "Rajasthan", "Delhi"],
    "Uttar Pradesh": ["Uttarakhand", "Himachal Pradesh", "Haryana", "Delhi", "Rajasthan", "Madhya Pradesh", "Chhattisgarh", "Jharkhand", "Bihar"],
    "Madhya Pradesh": ["Uttar Pradesh", "Chhattisgarh", "Maharashtra", "Gujarat", "Rajasthan"],
    "Bihar": ["Uttar Pradesh", "Jharkhand", "West Bengal"],
    "West Bengal": ["Odisha", "Jharkhand", "Bihar", "Sikkim", "Assam"],
    "Odisha": ["West Bengal", "Jharkhand", "Chhattisgarh", "Andhra Pradesh"]
}
optimizer = ProfitOptimizer()
agmarknet = AgmarknetClient()
retail_client = RetailPriceClient()

class MandiRecommendationRequest(BaseModel):
    farmer_lat: float
    farmer_lon: float
    commodity: str
    variety: Optional[str] = None
    date: Optional[str] = None
    quantity_quintals: float
    state: str

class MandiRecommendationResponse(BaseModel):
    mandi: str
    net_profit: float
    gross_value: float
    distance_km: float
    transport_cost: float
    tax_amount: float
    labor_cost: float
    vehicle: str
    price_per_qtl: float
    retail_price: float = 0.0
    trader_margin: float = 0.0
    lat: float
    lon: float
    is_predicted: bool = False
    last_updated: str = ""

@router.post("/suggest", response_model=List[MandiRecommendationResponse])
def suggest_mandi(request: MandiRecommendationRequest):
    """
    Suggest best mandis based on Realized Net Profit using LIVE Agmarknet Data.
    """
    # 1. Fetch live prices for candidate mandis in the state & neighbors
    search_states = [request.state]
    if request.state in NEIGHBORING_STATES:
        search_states.extend(NEIGHBORING_STATES[request.state])
        
    print(f"Fetching live data for {request.commodity} in regions: {search_states}...")
    
    api_is_down = False
    all_dfs = []
    for state in search_states:
        if api_is_down:
            print(f"Skipping Agmarknet fetch for {state} as API seems to be down.")
            continue
            
        try:
            filters = {
                'state': state,
                'commodity': request.commodity
            }
            if request.variety:
                filters['variety'] = request.variety
                
            # Use shorter timeout for fallback states
            fetch_timeout = 30 if state == request.state else 10
            df = agmarknet.fetch_data(filters=filters, limit=500, timeout=fetch_timeout) 
            
            if df is not None and not df.empty and request.date:
                try:
                    target_date = datetime.strptime(request.date, "%Y-%m-%d")
                    if 'arrival_date' in df.columns:
                        temp_parsed = pd.to_datetime(df['arrival_date'], format='%d/%m/%Y', errors='coerce')
                        df = df[temp_parsed <= target_date]
                except ValueError:
                    pass
                    
            if df is not None and not df.empty:
                df['source_state'] = state # Tag for cross-border taxes
                all_dfs.append(df)
        except Exception as e:
            print(f"Agmarknet API failed for {state}: {e}")
            api_is_down = True
            # If primary state fails, don't wait for neighbors to timeout too
            if state == request.state:
                break
            
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
    else:
        combined_df = None

    candidates = []
    
    # Pre-calculate live dictionary for quick lookup
    live_dict = {}
    if combined_df is not None and not combined_df.empty and 'market' in combined_df.columns and 'modal_price' in combined_df.columns:
        if 'arrival_date' in combined_df.columns:
            combined_df['parsed_date'] = pd.to_datetime(combined_df['arrival_date'], format='%d/%m/%Y', errors='coerce')
            combined_df = combined_df.sort_values(by='parsed_date', ascending=False)
            combined_df = combined_df.drop_duplicates(subset=['market', 'source_state'], keep='first')
        for _, row in combined_df.iterrows():
            m_name = row['market'].title()
            live_dict[m_name] = row
            live_dict[row['market']] = row

    seen_markets = set()
    import os
    today = datetime.now()

    for raw_mandi, coords in MANDI_COORDS.items():
        lat, lon = coords
        
        dist_approx = haversine_distance(request.farmer_lat, request.farmer_lon, lat, lon)
        if dist_approx > 350.0:
            continue
            
        row = None
        market_name = raw_mandi
        
        if raw_mandi.title() in live_dict:
            row = live_dict[raw_mandi.title()]
            market_name = row['market']
        elif raw_mandi in live_dict:
            row = live_dict[raw_mandi]
            market_name = row['market']
        else:
            for lv_key in live_dict.keys():
                if raw_mandi.lower() in lv_key.lower():
                    row = live_dict[lv_key]
                    market_name = row['market']
                    break
        
        base_price = None
        last_updated = ""
        days_gap = 0
        market_state = request.state
        
        # We need target_date_for_gap earlier to use in the fallback heuristic
        target_date_for_gap = today
        if request.date:
            try:
                target_date_for_gap = datetime.strptime(request.date, "%Y-%m-%d")
            except ValueError:
                pass
                
        if row is not None:
            base_price = float(row['modal_price'])
            last_updated = row.get('arrival_date', "")
            market_state = row.get('source_state', request.state)
            if 'parsed_date' in row and pd.notnull(row['parsed_date']):
                days_gap = (today - row['parsed_date']).days
        else:
            # FALLBACK to local history CSV
            safe_name = raw_mandi.replace('(','').replace(')','').replace(' ','_')
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            full_path = os.path.join(base_dir, "data", "real", request.commodity.lower(), f"{safe_name}.csv")
            
            if os.path.exists(full_path):
                try:
                    df_hist = pd.read_csv(full_path)
                    if 'arrival_date' in df_hist.columns:
                        df_hist['parsed_date'] = pd.to_datetime(df_hist['arrival_date'], format='%d/%m/%Y', errors='coerce')
                        df_hist = df_hist.sort_values(by='parsed_date', ascending=False)
                        if not df_hist.empty:
                            last_row = df_hist.iloc[0]
                            base_price = float(last_row['modal_price'])
                            last_updated = str(last_row.get('arrival_date', ""))
                            market_state = str(last_row.get('state', request.state))
                            days_gap = (today - last_row['parsed_date']).days
                except Exception as e:
                    print(f"Error loading {full_path}: {e}")
                    
        if base_price is not None and market_name not in seen_markets:
            is_predicted = False
            price = base_price
            
            effective_days_gap = 0
            if row is not None and 'parsed_date' in row and pd.notnull(row['parsed_date']):
                effective_days_gap = max(0, (target_date_for_gap - row['parsed_date']).days)
            elif days_gap > 0:
                effective_days_gap = days_gap
                
            if effective_days_gap > 0:
                is_predicted = True
                
                from .predict import get_inference_engine
                import torch
                import numpy as np
                
                try:
                    engine = get_inference_engine(request.commodity)
                    if engine.models_loaded:
                        target_min = engine.scaler['modal_price']['min']
                        target_max = engine.scaler['modal_price']['max']
                        scale = target_max - target_min
                        
                        base_norm = (base_price - target_min) / scale if scale > 0 else 0
                        data = np.zeros((1, 30, len(engine.features)), dtype=np.float32)
                        data[:, :, 0] = base_norm
                        data[:, :, 1:] = 0.5
                        
                        tensor = torch.FloatTensor(data).to(engine.device)
                        with torch.no_grad():
                            mu, sigma, xi = engine.de(tensor)
                            quantiles = engine.tft(tensor)
                            p50_norm = quantiles[0, -1, 1].item()
                            
                        base_pred = p50_norm * scale + target_min
                        dynamic_std_dev = (sigma.item() * scale) * effective_days_gap
                        
                        np.random.seed(int(base_price) + effective_days_gap)
                        predicted_price = base_pred + np.random.normal(0, dynamic_std_dev)
                        
                        if xi.item() > 0.1 and np.random.random() > 0.7:
                            predicted_price += (base_price * 0.1) * np.sign(mu.item())
                            
                        price = max(100.0, float(predicted_price))
                        price = round(price, 2)
                    else:
                        raise ValueError("Model not loaded")
                except Exception as e:
                    import hashlib
                    mandi_hash = int(hashlib.md5(market_name.encode()).hexdigest(), 16)
                    np.random.seed(mandi_hash % 10000 + effective_days_gap)
                    std_dev = base_price * 0.02 * effective_days_gap
                    slope = base_price * np.random.uniform(-0.005, 0.005) * effective_days_gap
                    predicted_price = float(base_price + slope + np.random.normal(0, std_dev))
                    price = max(100.0, predicted_price)
                    price = round(price, 2)
                
            candidates.append({
                'name': market_name, 
                'price': price,
                'state': market_state,
                'lat': lat,
                'lon': lon,
                'is_predicted': is_predicted,
                'last_updated': last_updated
            })
            seen_markets.add(market_name)
                    
    # Return empty if no live data matches
    if not candidates:
        print("Warning: No matching live mandis found within 350km. Returning empty list.")
        return []
    # 1.5 Fetch Retail Prices for Margin Calculation
    try:
        retail_df = retail_client.fetch_retail_prices(request.commodity, request.state)
        # Average retail price for the state
        if not retail_df.empty and 'retail_price' in retail_df.columns:
            avg_retail_price_kg = retail_df['retail_price'].mean()
            avg_retail_price_qtl = avg_retail_price_kg * 100
        else:
            avg_retail_price_qtl = 0.0
    except Exception as e:
        print(f"Retail API failed: {e}")
        avg_retail_price_qtl = 0.0

    # Add retail info to candidates
    for c in candidates:
        c['retail_price'] = avg_retail_price_qtl
        # Calculate margin: Retail - Wholesale (Mandi Price)
        if avg_retail_price_qtl > 0:
            c['trader_margin'] = avg_retail_price_qtl - c['price']
        else:
            c['trader_margin'] = 0.0

    # 2. Run Optimization
    print(f"Running optimization for {len(candidates)} candidates.")
    ranked_results = optimizer.recommend_mandi(
        request.farmer_lat,
        request.farmer_lon,
        request.quantity_quintals,
        candidates
    )
    
    # 3. Format response
    response = []
    for item in ranked_results:
        response.append({
            "mandi": item['mandi'],
            "net_profit": item['net_profit'],
            "gross_value": item.get('gross_value', 0.0),
            "distance_km": item['distance_km'],
            "transport_cost": item['transport_cost'],
            "tax_amount": item.get('tax_amount', 0.0),
            "labor_cost": item.get('labor_cost', 0.0),
            "vehicle": item.get('vehicle', "Unknown"),
            "price_per_qtl": item['price_per_qtl'],
            "retail_price": item.get('retail_price', 0.0),
            "trader_margin": item.get('trader_margin', 0.0),
            "lat": item['lat'], 
            "lon": item['lon'],
            "is_predicted": item.get('is_predicted', False),
            "last_updated": item.get('last_updated', "")
        })
        
    return response
