
import sys
import os
from datetime import datetime, timedelta
import torch
import pandas as pd
import numpy as np

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ingestion.fusion import DataFusionPipeline
from app.models.tft import TFT
from app.models.deep_extrema import DeepExtrema
from app.models.train import train_tft, train_deep_extrema, prepare_tft_data, get_state
from app.utils.mandi_coords import MANDI_COORDS

def train_all_mandis(commodity="Onion"):
    print(f"--- Starting Comprehensive Training for {commodity} (All Mandis) ---")
    
    # 1. Prepare Mandi Config from MANDI_COORDS
    mandi_config = []
    print(f"Loading configuration for {len(MANDI_COORDS)} mandis...")
    
    # Debug: Print first few to verify
    count = 0
    for name, coords in MANDI_COORDS.items():
        state = get_state(name)
        if state == "Unknown":
            print(f"Warning: Could not determine state for {name}. Skipping.")
            continue
            
        mandi_config.append({
            'name': name,
            'lat': coords[0],
            'lon': coords[1],
            'state': state
        })
        count += 1
        
    print(f"Prepared configuration for {len(mandi_config)} mandis.")
    
    # 2. Fetch Data
    pipeline = DataFusionPipeline()
    
    # Use 2 years of data for better seasonality learning
    start_date = (datetime.now() - timedelta(days=365*2)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Fetching GLOBAL data from Agmarknet ({start_date} to {end_date})...")
    print("This may take a significant amount of time due to API rate limits.")
    
    try:
        # Increase max_records to accommodate all mandis (approx 200 mandis * 700 days = 140k rows potential)
        # We'll set a high limit. Pagination in fusion.py handles the rest.
        df = pipeline.create_training_dataset(mandi_config, commodity, start_date, end_date, max_records=50000)
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return

    if df.empty:
        print("CRITICAL: No data fetched. API might be down or key invalid.")
        return

    print(f"Successfully fetched {len(df)} records from all sources.")
    
    # 3. Preprocess & Train
    print("Preprocessing...")
    SEQ_LEN = 30
    PREDICT_LEN = 7
    
    # Generate sequences
    X, Y = prepare_tft_data(df, SEQ_LEN, PREDICT_LEN, commodity_name=commodity)
    
    if X is None:
        print("Insufficient data for sequence generation.")
        return

    print(f"Training on {len(X)} sequences...")
    
    input_dim = X.shape[2]
    HIDDEN_DIM = 64
    
    # Initialize models
    tft_model = TFT(input_dim=input_dim, hidden_dim=HIDDEN_DIM, output_dim=1)
    de_model = DeepExtrema(input_dim=input_dim, hidden_dim=HIDDEN_DIM)
    
    # Train
    print("Training TFT (Temporal Fusion Transformer)...")
    tft_model = train_tft(tft_model, X, Y, epochs=10) # 10 epochs for full training
    
    print("Training DeepExtrema...")
    de_model = train_deep_extrema(de_model, X, Y, epochs=10)
    
    # Save
    save_dir = os.path.join(os.path.dirname(__file__), "app/models/saved")
    os.makedirs(save_dir, exist_ok=True)
    
    # Use specific names for "all mandis" models
    tft_path = os.path.join(save_dir, f"tft_{commodity.lower()}_all.pth")
    de_path = os.path.join(save_dir, f"deep_extrema_{commodity.lower()}_all.pth")
    
    torch.save(tft_model.state_dict(), tft_path)
    torch.save(de_model.state_dict(), de_path)
    
    print(f"✅ Models trained on ALL MANDIS and saved to:")
    print(f"   - {tft_path}")
    print(f"   - {de_path}")

if __name__ == "__main__":
    train_all_mandis("Onion")
